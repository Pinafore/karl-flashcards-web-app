<template>
  <v-container fluid>
    <!-- <connection-popup></connection-popup> -->
    <RecallPopup></RecallPopup>
    <v-card class="ma-3 mb-0 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">See KAR³L Predictions</div>
      </v-card-title>
      <p>Adjust the "student recall" slider and click "See Predictions" to view the flashcards that KAR³L predicts you have a probability of answering correctly closest to the selected recall!</p>
      <br />
      <v-row>
        <v-col cols="12">
          <p>Your Predicted Recall: {{ searchOptions.student_recall }}%</p>
          <br />
          <v-slider v-model="searchOptions.student_recall" thumb-label step="10" min="0" max="100" show-ticks="always"
            tick-size="4"></v-slider>
        </v-col>
        <v-col class="text-right" cols="12"><v-btn @click="retrievePredictedCards">See Predictions!</v-btn></v-col>
      </v-row>
      <br />
      <br />
      <Facts />
    </v-card>
  </v-container>
</template>
  
<script lang="ts">
import { Component, Vue, Watch } from "vue-property-decorator";
import { mainStore, studyStore } from "@/store";
import { IComponents } from "@/interfaces";
import ConnectionPopup from "@/views/ConnectionPopup.vue";
import RecallPopup from "@/views/main/RecallPopup.vue";
import { DataOptions } from "vuetify";
import Facts from "@/views/main/PredictionBrowser.vue"

@Component({
  components: { ConnectionPopup, RecallPopup, Facts },
})
export default class Predictions extends Vue {
  loading = true;
  searchOptions: IComponents["ModelPredictionSearch"] = { student_recall: 0.0 };
  startMenu = false;
  endMenu = false;
  options: DataOptions = {
    groupBy: [],
    groupDesc: [],
    itemsPerPage: 25,
    multiSort: false,
    mustSort: false,
    page: 1,
    sortBy: [],
    sortDesc: [],
  };

  // async mounted() {
  //   mainStore.setConnectionError(false);
  //   mainStore.setSchedulerError(false);
  //   await this.searchLeaderboards();
  // }

  public async mounted() {
      studyStore.setStudySet(null);
      await mainStore.getUserProfile();
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
    
    await this.retrievePredictedCards()
  }

  public beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.editDialog = to.name == "learn-edit" || to.name == "learn-report";
    });
  }


  // public async determine_decks(deckIds: string | (string | null)[]) {
  //   if (deckIds) {
  //     if (typeof deckIds === "string") {
  //       studyStore.setDeckIds([Number(deckIds)]);
  //     } else {
  //       studyStore.setDeckIds(deckIds.map(Number));
  //     }
  //   } else {
  //     studyStore.setDeckIds([]);
  //   }
  // }

  // public updateSelectedNum(payload: string | (string | null)[]) {
  //   if (payload && payload !== undefined) {
  //     studyStore.updateSelectedNum(payload);
  //   }
  // }

  public async destroyed() {
    studyStore.clearTimer();
    studyStore.setShowLoading();
    studyStore.emptySchedule();
    // window.removeEventListener("keydown", this.handleKeyDown);
    // window.removeEventListener("keyup", this.resetKeyListener);
  }

  get decks() {
    const userProfile = mainStore.userProfile;
    return userProfile && userProfile.decks
      ? [{ title: "All", public: false, id: 0 }].concat(userProfile.decks)
      : [];
  }

  get today() {
    return mainStore.today;
  }

  get filteredLeaderboard() {
    return mainStore.filteredLeaderboard;
  }

  get rankTypes() {
    return mainStore.rankTypes;
  }

  @Watch("searchOptions", { deep: true })
  onSearchOptionsChanged() {
    // console.log(this.searchOptions)
    // this.searchLeaderboards();
  }

  // @Watch("options", { deep: true })
  // onOptionsChanged(value: DataOptions) {
  //   this.searchOptions.skip = value.page * value.itemsPerPage - value.itemsPerPage;
  //   this.searchOptions.limit = value.itemsPerPage;
  //   this.searchLeaderboards();
  // }
  showRank() {
    const place = this.filteredLeaderboard?.user_place ?? null;
    return place !== null;
  }

  async retrievePredictedCards() {
    studyStore.setTargetRecall(this.searchOptions.student_recall)
    await studyStore.getStudyFacts();
    const facts = studyStore.studyset?.all_facts
    console.log(facts)
    if (facts != null) {
      mainStore.setFacts(facts)
      mainStore.setTotalFacts(facts.length)
    }
    
    studyStore.setTargetRecall(null)
  }
}
</script>
  