<template>
  <div>
    <v-data-table
      :headers="headers"
      :hide-default-footer="true"
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
      //await mainStore.getUserProfile();
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
      //await mainStore.getFacts(searchData);
      this.loading = false;
    }

    @Watch("options", { deep: true })
    onOptionsChanged(value: DataOptions) {
      const limit = value.itemsPerPage;
      const skip = value.page * value.itemsPerPage - value.itemsPerPage;
      const searchData: IComponents["FactSearch"] = { skip: skip, limit: limit };
      this.searchAPI(searchData);
    }

    @Watch("search", { deep: true })
    onSearchChanged() {
      this.options.page = 1;
      this.debounceSearch({ skip: 0, limit: this.options.itemsPerPage });
    }

    @Watch("selectedDecks", { deep: true })
    onSelectedDecksChanged() {
      this.options.page = 1;
      this.debounceDeck({ skip: 0, limit: this.options.itemsPerPage });
    }

    @Watch("selectedStatus", { deep: true })
    onSelectedStatusChanged() {
      this.options.page = 1;
      this.debounceSearch({ skip: 0, limit: this.options.itemsPerPage });
    }

    searchAPI(searchData: IComponents["FactSearch"]) {
      this.scrollToTop();
      if (this.search != "") {
        searchData.all = this.search;
      }

      if (this.selectedDecks.length != 0) {
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

    public scrollToTop() {
      window.scrollTo(0, 0);
    }

    returnBrowser() {
      if (this.$router.currentRoute.name == "browse-resolve") {
        this.$router.push({ name: "browse", query: { reported: "1" } });
      } else {
        this.$router.back();
      }
    }
  }
</script>
