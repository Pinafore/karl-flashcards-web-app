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
        <v-col class="text-right" cols="12"><v-btn size="large" @click="retrievePredictedCards">See Predictions!</v-btn></v-col>
      </v-row>
      <v-row v-if="filteredLeaderboard">
        <v-col>
          <v-card class="pa-3">
            <v-card-title primary-title class="pb-2 justify-center">
              <div class="headline primary--text justify-center">
                {{ filteredLeaderboard.name }}
              </div>
            </v-card-title>
            <div class="px-2 text-center">{{ filteredLeaderboard.details }}</div>
            <v-row justify="center">
              <v-btn v-if="showGoToUser()" class="px-2 mt-2 justify-center" @click="goToUser()">Your Rank: {{ userRank()
              }} - See Page</v-btn>
              <div v-else-if="showRank()" class="px-2 text-center">
                Your Rank: {{ userRank() }}
              </div>
              <div v-else class="px-2 text-center">
                Your Rank: N/A
              </div>
            </v-row>

            <v-data-table disable-filtering disable-sort class="mb-3 pa-1" :headers="filteredLeaderboard.headers"
              item-key="id" :loading="loading" :items="filteredLeaderboard.leaderboard" :options.sync="options"
              :server-items-length="filteredLeaderboard.total" :footer-props="{
                itemsPerPageOptions: [10, 25, 50, 100],
                showFirstLastPage: true,
              }">
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-else>
        <v-col>
          <v-card class="pa-3">
            <v-card-title primary-title class="pb-2 justify-center">
              <div class="headline primary--text justify-center">
                Loading
              </div>
            </v-card-title>
          </v-card>
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

@Component({
  components: { ConnectionPopup, RecallPopup },
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
    this.updateSelectedNum(this.$router.currentRoute.query.num);
    await this.determine_decks(this.$router.currentRoute.query.deck);
    // window.addEventListener("keydown", this.handleKeyDown);
    // window.addEventListener("keyup", this.resetKeyListener);
  }

  public beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.editDialog = to.name == "learn-edit" || to.name == "learn-report";
    });
  }

  public async beforeRouteUpdate(to, from, next) {
    if (!to.name.startsWith("learn-") && !from.name.startsWith("learn-")) {
      await this.determine_decks(to.query.deck);
    }
    this.editDialog = to.name == "learn-edit" || to.name == "learn-report";
    if (to.name == "learn") {
      studyStore.startTimer();
    }
    next();
  }

  public async determine_decks(deckIds: string | (string | null)[]) {
    if (deckIds) {
      if (typeof deckIds === "string") {
        studyStore.setDeckIds([Number(deckIds)]);
      } else {
        studyStore.setDeckIds(deckIds.map(Number));
      }
    } else {
      studyStore.setDeckIds([]);
    }
  }

  public updateSelectedNum(payload: string | (string | null)[]) {
    if (payload && payload !== undefined) {
      studyStore.updateSelectedNum(payload);
    }
  }

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

  async searchLeaderboards() {
    this.loading = true;
    await mainStore.getLeaderboard(this.searchOptions);
    this.loading = false;
  }

  showRank() {
    const place = this.filteredLeaderboard?.user_place ?? null;
    return place !== null;
  }

  showGoToUser() {
    const place = this.filteredLeaderboard?.user_place ?? null;
    if (place) {
      return (
        (this.options.page - 1) * this.options.itemsPerPage >= place ||
        place >
        (this.options.page - 1) * this.options.itemsPerPage +
        this.options.itemsPerPage
      );
    } else {
      return false;
    }
  }
  goToUser() {
    const place = this.filteredLeaderboard?.user_place ?? null;
    if (place) {
      this.options.page = Math.ceil(place / this.options.itemsPerPage);
      this.searchOptions.skip =
        Math.floor(place / this.options.itemsPerPage) * this.options.itemsPerPage;
      this.searchOptions.limit = this.options.itemsPerPage;
      this.searchLeaderboards();
    }
  }

  async retrievePredictedCards() {
    studyStore.setTargetRecall(this.searchOptions.student_recall)
    await studyStore.getStudyFacts();
    studyStore.setTargetRecall(null)
  }
}
</script>
  