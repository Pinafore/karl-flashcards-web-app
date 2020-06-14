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
        <v-toolbar flat>
          <v-toolbar-title>Facts</v-toolbar-title>
          <v-divider class="mx-4" inset vertical></v-divider>
          <v-spacer></v-spacer>
          <v-text-field
            v-model="search"
            append-icon="mdi-magnify"
            label="Search"
            single-line
            hide-details
          ></v-text-field>
          <v-spacer></v-spacer>
          <v-dialog v-model="dialog" max-width="500px">
            <template v-slot:activator="{ on }">
              <v-btn color="primary" dark class="mb-2" v-on="on">New Fact</v-btn>
            </template>
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
        </v-toolbar>
      </template>

      <template v-slot:item.actions="{ item }">
        <v-icon
          v-if="item.permission === 'owner'"
          small
          class="mr-2"
          @click="editFact(item)"
        >
          mdi-pencil
        </v-icon>
        <v-icon small @click="markFact(item)">
          mdi-star
        </v-icon>
        <v-icon v-if="item.permission === 'viewer'" @click="reportFact(item)">
          mdi-report
        </v-icon>
        <v-icon small @click="suspendFact(item)">
          mdi-pause
        </v-icon>
        <v-icon small @click="deleteFact(item)">
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
  import { IComponents, Permission } from "@/interfaces";
  import { extend, ValidationObserver, ValidationProvider } from "vee-validate";
  import { excluded, required } from "vee-validate/dist/rules";

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
      { text: "Actions", value: "actions", sortable: false },
    ];

    async mounted() {
      await mainStore.getUserProfile();
      // const limit = this.options.itemsPerPage;
      // const skip =
      //   this.options.page * this.options.itemsPerPage - this.options.itemsPerPage;
      // const searchData: IComponents["FactSearch"] = { skip: skip, limit: limit };
      // this.getDataFromApi(searchData).then((data) => {
      //   this.facts = data.facts;
      //   this.totalFacts = data.total;
      // });
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
      return new Promise<IComponents["FactBrowse"]>( (resolve, reject) => {
        const { sortBy, sortDesc, page, itemsPerPage } = this.options;
        let items: IComponents["Fact"][] = mainStore.facts;
        const total: number = mainStore.totalFacts;

        if (sortBy.length === 1 && sortDesc.length === 1) {
          items = items.sort((a, b) => {
            const sortA = a[sortBy[0]];
            const sortB = b[sortBy[0]];

            if (sortDesc[0]) {
              if (sortA < sortB) return 1;
              if (sortA > sortB) return -1;
              return 0;
            } else {
              if (sortA < sortB) return -1;
              if (sortA > sortB) return 1;
              return 0;
            }
          });
        }

        setTimeout(() => {
          this.loading = false;
          resolve({
            facts: items,
            total: total,
          });
        }, 1000);
      });
    }

    @Watch("options", { deep: true })
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onOptionsChanged(value: DataOptions, oldValue: DataOptions) {
      const limit = value.itemsPerPage;
      const skip = value.page * value.itemsPerPage - value.itemsPerPage;
      const searchData: IComponents["FactSearch"] = { skip: skip, limit: limit };
      this.getDataFromApi(searchData).then((data) => {
        this.facts = data.facts;
        this.totalFacts = data.total;
      });
    }

    editFact(item) {
      this.editedIndex = this.facts.indexOf(item);
      this.editedFact = Object.assign({}, item);
      this.dialog = true;
    }

    async markFact(item) {
      await mainStore.markFact(item.fact_id);
    }

    async reportFact(item) {
      await mainStore.reportFact(item.fact_id);
    }

    async suspendFact(item) {
      await mainStore.suspendFact(item.fact_id);
    }

    async deleteFact(item) {
      const index = this.facts.indexOf(item);

      this.facts.splice(index, 1);
      await mainStore.deleteFact(item.fact_id);
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
