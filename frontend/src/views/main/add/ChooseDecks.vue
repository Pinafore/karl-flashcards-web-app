<template>
  <div>
    <Onboard></Onboard>
    <v-toolbar style="position: sticky; top: 0; z-index: 10;">
      <v-toolbar-title>
        Public Decks
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn :disabled="selected.length === 0" @click="decksSelected()"
        >Add Deck(s)</v-btn
      >
    </v-toolbar>
    <v-data-table
      v-model="selected"
      :headers="headers"
      item-key="id"
      :items="decks"
      :items-per-page="15"
      show-select
      :style="{ cursor: 'pointer' }"
      no-data-text="You have added all available public decks!"
    >
    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/utils/store-accessor";
  import { IComponents } from "@/interfaces";
  import Onboard from "@/views/Onboard.vue";

  @Component({
    components: { Onboard },
  })
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
