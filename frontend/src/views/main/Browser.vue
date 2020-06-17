<template>
  <div>
    <v-data-table
      :headers="headers"
      :items="facts"
      :options.sync="options"
      :server-items-length="totalFacts"
      :loading="loading"
      class="elevation-1"
      dense
      no-results-text="No results found"
      disable-sort
      :footer-props="{
        showFirstLastPage: true,
        itemsPerPageOptions: [10, 50, 100, 1000],
      }"
    >
      <template v-slot:top>
        <v-container class="ma-0 py-0" fluid>
          <v-row>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                dense
                hide-details
              ></v-text-field>
            </v-col>
            <v-col cols="12" sm="4">
              <v-select
                v-model="selectedDecks"
                :items="decks"
                item-text="title"
                item-value="id"
                small-chips
                single-line
                label="Decks"
                multiple
                deletable-chips
                hide-details
                dense
              ></v-select>
            </v-col>
            <v-col cols="12" sm="4">
              <v-select
                v-model="selectedStatus"
                :items="status"
                item-text="name"
                item-value="params"
                single-line
                label="Status Filters"
                hide-details
                dense
              ></v-select>
            </v-col>
          </v-row>
        </v-container>
        <v-dialog v-model="dialog" max-width="500px">
          <v-card>
            <v-card-title>
              <span class="headline">{{ formTitle }}</span>
            </v-card-title>

            <v-card-text>
              <!-- front -->
              <validation-provider
                v-slot="{ errors }"
                name="Front"
                :rules="{
                  required: true,
                }"
              >
                <v-text-field
                  v-model="editedFact.text"
                  label="Front"
                  :error-messages="errors[0]"
                  required
                ></v-text-field>
              </validation-provider>

              <!-- back -->
              <validation-provider v-slot="{ errors }" rules="required" name="Back">
                <v-text-field
                  v-model="editedFact.answer"
                  label="Back"
                  type="back"
                  :error-messages="errors[0]"
                  required
                ></v-text-field>
              </validation-provider>

              <v-select
                v-model="editedFact.deck_id"
                :items="decks"
                item-text="title"
                item-value="id"
                label="Choose Deck"
              >
              </v-select>

              <!-- category -->
              <validation-provider v-slot="{ errors }" name="Category">
                <v-text-field
                  v-model="editedFact.category"
                  label="Category"
                  type="category"
                  :error-messages="errors[0]"
                ></v-text-field>
              </validation-provider>

              <!-- identifier -->
              <validation-provider v-slot="{ errors }" name="Identifier">
                <v-text-field
                  v-model="editedFact.identifier"
                  label="Identifier"
                  type="identifier"
                  :error-messages="errors[0]"
                ></v-text-field>
              </validation-provider>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn color="blue darken-1" text @click="close">Cancel</v-btn>
              <v-btn color="blue darken-1" text @click="save">Save</v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </template>
      <template v-slot:item.marked="{ item }">
        <v-simple-checkbox
          v-model="item.marked"
          v-ripple
          @input="markFact(item, item.marked)"
        ></v-simple-checkbox>
      </template>
      <template v-slot:item.suspended="{ item }">
        <v-simple-checkbox
          v-model="item.suspended"
          v-ripple
          @input="suspendFact(item, item.suspended)"
        ></v-simple-checkbox>
      </template>
      <template v-slot:item.reported="{ item }">
        <v-simple-checkbox
          v-if="item.permission === 'viewer'"
          v-model="item.reported"
          v-ripple
          @input="reportFact(item, item.reported)"
        ></v-simple-checkbox>
        <div v-else>
          owner
        </div>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon v-if="item.permission === 'owner'" @click="editFact(item)">
          mdi-pencil
        </v-icon>
        <v-icon @click="deleteFact(item, true)">
          mdi-delete
        </v-icon>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/utils/store-accessor";
  import { DataOptions } from "vuetify";
  import { IComponents, IStatus, Permission } from "@/interfaces";
  import { extend, ValidationObserver, ValidationProvider } from "vee-validate";
  import { excluded, required } from "vee-validate/dist/rules";
  import debounce from "lodash.debounce";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("excluded", {
    ...excluded,
    message: "You already have a fact with this front text.",
  });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class Facts extends Vue {
    loading = true;
    totalFacts = 0;
    formTitle = "Edit Fact";
    search = "";
    options: DataOptions = {
      groupBy: [],
      groupDesc: [],
      itemsPerPage: 100,
      multiSort: false,
      mustSort: false,
      page: 1,
      sortBy: [],
      sortDesc: [],
    };
    dialog = false;
    selectedDecks = [];
    selectedStatus: IStatus = {};
    editedFact = {
      text: "",
      answer: "",
      deck_id: this.defaultDeck.id,
      category: "",
      identifier: "",
    };
    defaultFact = {
      text: "",
      answer: "",
      deck_id: this.defaultDeck.id,
      category: "",
      identifier: "",
    };
    editedIndex = -1;
    facts: IComponents["Fact"][] = [];
    debounceSearch = debounce(this.searchAPI, 1000);
    debounceDeck = debounce(this.searchAPI, 2000);
    headers = [
      {
        text: "Text",
        sortable: true,
        value: "text",
        align: "left",
      },
      {
        text: "Answer",
        sortable: true,
        value: "answer",
        align: "left",
      },
      {
        text: "Deck",
        sortable: true,
        value: "deck.title",
        align: "left",
      },
      {
        text: "Category",
        sortable: true,
        value: "category",
        align: "left",
      },
      {
        text: "Identifier",
        sortable: true,
        value: "identifier",
        align: "left",
      },
      {
        text: "Favorite",
        sortable: true,
        value: "marked",
        align: "left",
      },
      {
        text: "reported",
        sortable: true,
        value: "reported",
        align: "left",
      },
      {
        text: "suspended",
        sortable: true,
        value: "suspended",
        align: "left",
      },
      { text: "Actions", value: "actions", sortable: false },
    ];
    status = [
      { name: "No Status Filters", params: {} },
      { name: "Marked", params: { marked: true } },
      { name: "All Suspended (not reported)", params: { suspended: true } },
      { name: "All Reported", params: { reported: true } },
      { name: "Marked + Reported", params: { marked: true, reported: true } },
      { name: "Marked + Suspended", params: { marked: true, suspended: true } },
      { name: "Unmarked + Reported", params: { marked: false, reported: true } },
      { name: "Unmarked + Suspended", params: { marked: false, suspended: true } },
    ];

    async mounted() {
      await mainStore.getUserProfile();
    }

    get defaultDeck() {
      const userProfile = mainStore.userProfile;
      const default_deck: IComponents["Deck"] = {
        title: "Default",
        public: true,
        id: 1,
      };
      return userProfile && userProfile.default_deck
        ? userProfile.default_deck
        : default_deck;
    }
    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }
    async getDataFromApi(searchData: IComponents["FactSearch"]) {
      this.loading = true;
      await mainStore.getFacts(searchData);
      // eslint-disable-next-line
      this.facts = mainStore.facts;
      this.totalFacts = mainStore.totalFacts;
      this.loading = false;
    }

    @Watch("options", { deep: true })
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onOptionsChanged(value: DataOptions) {
      const limit = value.itemsPerPage;
      const skip = value.page * value.itemsPerPage - value.itemsPerPage;
      const searchData: IComponents["FactSearch"] = { skip: skip, limit: limit };
      this.getDataFromApi(searchData);
    }

    @Watch("search", { deep: true })
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onSearchChanged() {
      this.debounceSearch();
    }

    @Watch("selectedDecks", { deep: true })
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onSelectedDecksChanged() {
      this.debounceDeck();
    }

    @Watch("selectedStatus", { deep: true })
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onSelectedStatusChanged() {
      this.debounceSearch();
    }

    searchAPI() {
      const searchData: IComponents["FactSearch"] = {
        limit: this.options.itemsPerPage,
        skip: this.options.page * this.options.itemsPerPage - this.options.itemsPerPage,
      };
      if (this.search != "") {
        searchData.all = this.search;
      }

      if (this.selectedDecks != []) {
        searchData.deck_ids = this.selectedDecks;
      }

      if (this.selectedStatus.marked) {
        searchData.marked = this.selectedStatus.marked;
      }

      if (this.selectedStatus.reported) {
        searchData.reported = this.selectedStatus.reported;
      }

      if (this.selectedStatus.suspended) {
        searchData.suspended = this.selectedStatus.suspended;
      }
      this.getDataFromApi(searchData);
    }
    editFact(item) {
      this.editedIndex = this.facts.indexOf(item);
      this.editedFact = Object.assign({}, item);
      this.dialog = true;
    }

    async markFact(item, todo) {
      await mainStore.markFact({ id: item.fact_id, todo: todo });
    }

    async reportFact(item, todo) {
      await mainStore.reportFact({ id: item.fact_id, todo: todo });
      item.suspended = todo;
    }

    async suspendFact(item, todo) {
      await mainStore.suspendFact({ id: item.fact_id, todo: todo });
      if (!todo && item.reported) {
        item.reported = false;
      }
    }

    async deleteFact(item, todo) {
      const index = this.facts.indexOf(item);

      this.facts.splice(index, 1);
      await mainStore.deleteFact({ id: item.fact_id, todo: todo });
    }

    close() {
      this.dialog = false;
      this.$nextTick(() => {
        this.editedFact = Object.assign({}, this.defaultFact);
        this.editedIndex = -1;
      });
    }

    async save() {
      if (this.editedIndex > -1) {
        const fact: IComponents["FactUpdate"] = {
          text: this.editedFact.text,
          deck_id: this.editedFact.deck_id,
          answer: this.editedFact.answer,
          category: this.editedFact.category,
          identifier: this.editedFact.identifier,
        };
        Object.assign(this.facts[this.editedIndex], this.editedFact);
        this.close();
        await mainStore.updateFact({
          id: this.facts[this.editedIndex].fact_id,
          data: fact,
        });
      } else {
        this.close();
      }
    }
  }
</script>
