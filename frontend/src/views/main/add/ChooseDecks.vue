<template>
  <div>
    <v-toolbar style="position: sticky; top: 0; z-index: 10;">
      <v-toolbar-title>
        Public Decks
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn :disabled="selected !== []" @click="decksSelected()">Add Deck(s)</v-btn>
    </v-toolbar>
    <v-dialog v-model="onboard" scrollable width="500">
      <v-card>
        <v-card-title>
          <h2>Welcome!</h2>
        </v-card-title>
        <v-card-text>
          KAR³L has decks of pre-made facts. Choose the decks you're interested in and
          click "Add Decks" to continue
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="onboard = false">
            Got it!
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
    onboard = false;

    async mounted() {
      this.onboard = this.$router.currentRoute.query.onboard === "true";
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
