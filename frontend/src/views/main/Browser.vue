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
            <v-col cols="11" sm="3">
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
            <v-col align-self="center" cols="1" sm="1">
              <v-tooltip bottom>
                <template v-slot:activator="{ on, attrs }">
                  <v-btn icon v-bind="attrs" @click="searchAPI()" v-on="on">
                    <v-icon>
                      mdi-refresh
                    </v-icon>
                  </v-btn>
                </template>
                <span>Refresh</span>
              </v-tooltip>
            </v-col>
          </v-row>
        </v-container>
        <v-dialog v-model="dialog" max-width="1000px" @click:outside="returnBrowser">
          <router-view name="edit"></router-view>
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
      <template v-slot:item.reports="{ item }">
        <v-tooltip v-if="isViewer(item) && item.reports.length === 0" bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-bind="attrs" @click="viewReport(item)" v-on="on">
              <v-icon>mdi-alert-octagon</v-icon>
            </v-btn>
          </template>
          <span>Report</span>
        </v-tooltip>
        <v-tooltip v-else bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              icon
              v-bind="attrs"
              :disabled="item.reports.length === 0"
              @click="viewReport(item)"
              v-on="on"
            >
              <v-icon>mdi-eye</v-icon>
            </v-btn>
          </template>
          <span>View Report(s)</span>
        </v-tooltip>
      </template>
      <template v-slot:item.actions="{ item }">
        <v-icon v-if="isOwner(item)" @click="editFact(item)">
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
  import { mainStore } from "@/utils/store-accessor";
  import { DataOptions } from "vuetify";
  import { IComponents, IStatus, Permission } from "@/interfaces";
  import { extend, ValidationObserver, ValidationProvider } from "vee-validate";
  import { required } from "vee-validate/dist/rules";
  import debounce from "lodash.debounce";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class Facts extends Vue {
    loading = true;
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
        text: "Suspended",
        sortable: true,
        value: "suspended",
        align: "left",
      },
      {
        text: "Reported",
        sortable: true,
        value: "reports",
        align: "left",
      },
      { text: "Actions", value: "actions", sortable: false },
    ];
    status = [
      { name: "No Status Filters", params: {} },
      { name: "Favorite", params: { marked: true } },
      { name: "All Suspended", params: { suspended: true } },
      { name: "All Reported", params: { reported: true } },
      { name: "Favorite + Reported", params: { marked: true, reported: true } },
      { name: "Favorite + Suspended", params: { marked: true, suspended: true } },
      { name: "Not Favorite + Reported", params: { marked: false, reported: true } },
      { name: "Not Favorite + Suspended", params: { marked: false, suspended: true } },
    ];

    async mounted() {
      await mainStore.getUserProfile();
    }

    public beforeRouteEnter(to, from, next) {
      next((vm) => {
        vm.dialog =
          to.name == "browse-edit" ||
          to.name == "browse-report" ||
          to.name == "browse-resolve";
        vm.setSettings(to);
      });
    }

    public beforeRouteUpdate(to, from, next) {
      this.dialog =
        to.name == "browse-edit" ||
        to.name == "browse-report" ||
        to.name == "browse-resolve";
      this.setSettings(to);
      next();
    }

    setSettings(route) {
      if (route.query.reported === "1") {
        this.selectedStatus = { reported: true };
      }
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }

    isOwner(item) {
      return item.permission === Permission.owner;
    }

    isViewer(item) {
      return item.permission === Permission.viewer;
    }

    get facts() {
      return mainStore.facts;
    }

    get totalFacts() {
      return mainStore.totalFacts;
    }

    async getDataFromApi(searchData: IComponents["FactSearch"]) {
      this.loading = true;
      await mainStore.getFacts(searchData);
      this.loading = false;
    }

    @Watch("options", { deep: true })
    onOptionsChanged(value: DataOptions) {
      const limit = value.itemsPerPage;
      const skip = value.page * value.itemsPerPage - value.itemsPerPage;
      const searchData: IComponents["FactSearch"] = { skip: skip, limit: limit };
      this.getDataFromApi(searchData);
    }

    @Watch("search", { deep: true })
    onSearchChanged() {
      this.debounceSearch();
    }

    @Watch("selectedDecks", { deep: true })
    onSelectedDecksChanged() {
      this.debounceDeck();
    }

    @Watch("selectedStatus", { deep: true })
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
      const index = String(this.facts.indexOf(item));
      this.$router.push({
        name: "browse-edit",
        params: { id: index },
      });
    }

    viewReport(item) {
      const index = String(this.facts.indexOf(item));
      if (this.isViewer(item)) {
        this.$router.push({
          name: "browse-report",
          params: { id: index },
        });
      } else {
        this.$router.push({
          name: "browse-resolve",
          params: { id: index },
        });
      }
    }

    async markFact(item, todo) {
      await mainStore.markFact({ id: item.fact_id, todo: todo });
    }

    async suspendFact(item, todo) {
      await mainStore.suspendFact({ id: item.fact_id, todo: todo });
    }

    async deleteFact(item, todo) {
      const index = this.facts.indexOf(item);

      this.facts.splice(index, 1);
      await mainStore.deleteFact({ id: item.fact_id, todo: todo });
    }

    returnBrowser() {
      this.$router.back();
    }
  }
</script>
