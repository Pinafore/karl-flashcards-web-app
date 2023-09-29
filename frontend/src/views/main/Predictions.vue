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
      <v-row v-if="loading" cols="12">
        <v-col>
          <v-card class="pa-3">
            <v-card-title primary-title class="pb-2 justify-center">
              <div class="headline primary--text justify-center">
                Loading...
              </div>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-else cols="12">
        <v-col>
          <Facts />
        </v-col>
      </v-row>
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
  originalRecall = 0.0;
  originalFacts = [];

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

      const recall = mainStore.userProfile?.recall_target
      if (recall !== undefined) {
        this.originalRecall = recall
      }
    
      await this.retrievePredictedCards()
  }

  public async destroyed() {
    studyStore.clearTimer();
    studyStore.setShowLoading();
    studyStore.emptySchedule();
  }


  get today() {
    return mainStore.today;
  }

  @Watch("searchOptions", { deep: true })
  onSearchOptionsChanged() {
    // console.log(this.searchOptions)
    // this.searchLeaderboards();
  }

  async retrievePredictedCards() {
    this.loading = true;
    const currProfile = mainStore.userProfile
    if (!currProfile) {
      return
    }
    const oldRecall = currProfile?.recall_target
    console.log(oldRecall)

    studyStore.setTargetRecall(this.searchOptions.student_recall > 0 ? this.searchOptions.student_recall : 1)
    await studyStore.getStudyFacts();
    const facts = studyStore.studyset?.all_facts
    console.log(facts)
    if (facts != null) {
      mainStore.setFacts(facts)
      mainStore.setTotalFacts(facts.length)
    } else {
      mainStore.setFacts([])
      mainStore.setTotalFacts(0)
    }
    studyStore.setTargetRecall(oldRecall)
    currProfile.recall_target = oldRecall
    mainStore.setUserProfile(currProfile)
    this.loading = false;
  }
}
</script>
  