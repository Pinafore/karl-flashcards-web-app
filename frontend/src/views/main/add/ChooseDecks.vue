<template>
  <div>
    <v-toolbar style="position: sticky; top: 0; z-index: 10;">
      <v-toolbar-title>
        Public Decks
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="decksSelected()">Add Selected Deck(s)</v-btn>
    </v-toolbar>
    <v-data-table
      v-model="selected"
      :headers="headers"
      item-key="id"
      :items="decks"
      :items-per-page="15"
      show-select
      :style="{ cursor: 'pointer' }"
    >
    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/utils/store-accessor";
  import { IComponents } from "@/interfaces";

  @Component
  export default class Decks extends Vue {
    public headers = [
      {
        text: "Deck",
        sortable: true,
        value: "title",
        align: "left",
      },
    ];
    selected: IComponents["Deck"][] = [];

    async mounted() {
      await mainStore.getPublicDecks();
    }

    get decks() {
      return mainStore.publicDecks;
    }

    public async decksSelected() {
      const selectedIds = this.selected.map((a) => Number(a.id));
      const router = this.$router;
      await mainStore.assignDecks(selectedIds).finally(function() {
        router.push({ path: "/main/study/decks" });
      });
    }
  }
</script>
