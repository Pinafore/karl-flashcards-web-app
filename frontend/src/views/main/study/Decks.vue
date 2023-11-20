<template>
  <div>
    <Onboard></Onboard>
    <test-popup :shouldShow="true"></test-popup>
    <!-- <RecallPopup></RecallPopup> -->
    <v-toolbar style="position: sticky; top: 0; z-index: 10;">
      <v-toolbar-title>
        New Study Set
        <span v-show="resumeAvail" style="margin-left: .5em">
          (Overrides Current Study Set!!)
        </span>
      </v-toolbar-title>
      <v-spacer class="hidden-xs-only"></v-spacer>

      <v-card-actions class="px-0 px-sm-auto">
        <v-btn v-show="!checkAllDecks()" @click="deleteDecks">Delete</v-btn>
        <v-btn to="/main/add/deck">Add Deck</v-btn>
        <v-btn v-if="checkAllDecks()" @click="openAll()">Study All</v-btn>
        <v-btn v-else color="primary" @click="openDecks()"
          >Study<span class="hidden-xs-only"> Selected</span></v-btn
        >
      </v-card-actions>
    </v-toolbar>
    <v-card flat>
      <v-card-text style="padding-bottom: 0px">
        <p class="subheading">
          Max Facts (Create a new study set after completion if you wish to keep
          studying):
        </p>
        <v-radio-group v-model="selectedNum" row>
          <v-radio
            v-for="num in studyNumOptions"
            :key="num"
            :label="`${num} Facts`"
            :value="num"
          >
          </v-radio>
        </v-radio-group>
      </v-card-text>
    </v-card>
    <v-data-table
      v-model="selected"
      :headers="headers"
      item-key="id"
      :items="decks"
      :items-per-page="15"
      show-select
      :style="{ cursor: 'pointer' }"
      @click:row="openDeck"
    >
    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/utils/store-accessor";
  import { IComponents } from "@/interfaces";
  import Onboard from "@/views/Onboard.vue";
  import TestPopup from "@/views/main/TestPopup.vue";
  // import RecallPopup from "@/views/main/RecallPopup.vue";

  @Component({
    components: { TestPopup, Onboard },
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
    studyNumOptions: number[] = [5, 10, 20, 30, 50];
    selectedNum = 20;

    async mounted() {
      studyStore.setStudySet(null);
      await mainStore.getUserProfile();
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
      await studyStore.checkIfInTestMode();
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }

    get resumeAvail() {
      return mainStore.userProfile && mainStore.userProfile.study_set_expiry_date;
    }

    public checkAllDecks() {
      return this.selected.length == 0 || this.selected.length == this.decks.length;
    }

    public openDecks() {
      // Vue router takes in arrays only as strings
      const selectedIds = this.selected.map((a) => String(a.id));
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn?show_test_mode=true",
        query: { deck: selectedIds, num: String(this.selectedNum) },
      });
    }

    public openDeck(deck) {
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn?show_test_mode=true",
        query: { deck: String(deck.id), num: String(this.selectedNum) },
      });
    }

    public openAll() {
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn?show_test_mode=true",
      });
    }

    public async deleteDecks() {
      const selectedIds = this.selected.map((a) => a.id);
      if (selectedIds.length > 0) {
        await mainStore.deleteDecks({ ids: selectedIds });
        this.selected = [];
        await mainStore.getUserProfile();
      }
    }
  }
</script>
