<template>
  <div>
    <v-toolbar light>
      <v-toolbar-title>
        Decks
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" to="/main/add/deck">Add New Deck</v-btn>
      <v-btn v-if="checkAllDecks()" color="primary" to="/main/study/learn"
        >Study All</v-btn
      >
      <v-btn v-else color="primary" @click="openDecks()">Study Selected</v-btn>
    </v-toolbar>
    <v-data-table
      v-model="selected"
      :headers="headers"
      item-key="id"
      :items="decks"
      show-select
      hide-default-footer
      :style="{ cursor: 'pointer' }"
      @click:row="openDeck"
    >
      <!--      <template slot="items" slot-scope="props">-->
      <!--        <td width="30px">-->
      <!--          <v-checkbox v-model="props.selected" primary hide-details></v-checkbox>-->
      <!--        </td>-->
      <!--        &lt;!&ndash;        <template v-slot:item.title="{ item }">&ndash;&gt;-->
      <!--        &lt;!&ndash;          <v-icon v-if="item.title">mdi-check</v-icon>&ndash;&gt;-->
      <!--        &lt;!&ndash;        </template>&ndash;&gt;-->
      <!--        &lt;!&ndash;        <td :style="{ cursor: 'pointer' }" @click="openDeck(props.item.id)">&ndash;&gt;-->
      <!--        &lt;!&ndash;          {{ props.item.title }}&ndash;&gt;-->
      <!--        &lt;!&ndash;        </td>&ndash;&gt;-->
      <!--      </template>-->
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
        sortable: false,
        value: "title",
        align: "left",
      },
    ];
    selected: IComponents["Deck"][] = [];

    get decks() {
      const userProfile = mainStore.userProfile;
      console.log("DECKS");
      console.log(userProfile && userProfile.decks ? userProfile.decks : []);
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }

    public checkAllDecks() {
      return this.selected.length == 0 || this.selected.length == this.decks.length;
    }

    public openDecks() {
      console.log(this.selected);
      // Vue router takes in arrays only as strings
      const selectedIds = this.selected.map((a) => String(a.id));
      this.$router.push({
        path: "/main/study/learn",
        query: { deck: selectedIds },
      });
    }

    public openDeck(deck) {
      this.$router.push({ path: "/main/study/learn", query: { deck: deck.id } });
      // this.$router.push({ name: 'main-study-users-decks-learn', params: { deck: id } })
      // this.$router.push(pathname:'main-study-users-decks-learn', params: {deck: id});
    }
  }
</script>
