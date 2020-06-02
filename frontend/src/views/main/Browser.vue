<template>
  <div>
    <v-data-table
      v-model="selected"
      :headers="headers"
      item-key="id"
      :items="facts"
      :items-per-page="15"
      show-select
      :style="{ cursor: 'pointer' }"
      @click:row="openFact"
    >
    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/utils/store-accessor";

  @Component
  export default class Facts extends Vue {
    public headers = [
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
        value: "deck",
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
      {
        text: "Marked",
        sortable: true,
        value: "marked",
        align: "left",
      },
      {
        text: "Reported",
        sortable: true,
        value: "reported",
        align: "left",
      },
      {
        text: "Suspended",
        sortable: true,
        value: "reported",
        align: "left",
      },
    ];

    async mounted() {
      await mainStore.getUserProfile();
    }

    get facts() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.facts ? userProfile.facts : [];
    }
  }
</script>
