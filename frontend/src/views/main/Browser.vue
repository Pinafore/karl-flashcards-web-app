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
    ></v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore } from "@/utils/store-accessor";
  import { DataOptions } from "vuetify";
  import { IBrowser, IComponents } from "@/interfaces";

  @Component
  export default class Facts extends Vue {
    loading = true;
    totalFacts = 0;
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
        value: "answer",
        align: "left",
      },
      {
        text: "Identifier",
        sortable: true,
        value: "identifier",
        align: "left",
      },
    ];

    async mounted() {
      this.getDataFromApi().then((data) => {
        this.facts = data.facts;
        this.totalFacts = data.totalFacts;
      });
    }

    async getDataFromApi() {
      this.loading = true;
      await mainStore.getFacts();
      // eslint-disable-next-line
      return new Promise<IBrowser>( (resolve, reject) => {
        const { sortBy, sortDesc, page, itemsPerPage } = this.options;
        let items: IComponents["Fact"][] = mainStore.facts;
        const total: number = items.length;

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

        if (itemsPerPage > 0) {
          items = items.slice((page - 1) * itemsPerPage, page * itemsPerPage);
        }

        setTimeout(() => {
          this.loading = false;
          resolve({
            facts: items,
            totalFacts: total,
          });
        }, 1000);
      });
    }

    @Watch("options", { deep: true })
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    onOptionsChanged(value: DataOptions, oldValue: DataOptions) {
      this.getDataFromApi().then((data) => {
        this.facts = data.facts;
        this.totalFacts = data.totalFacts;
      });
    }
  }
</script>
