<template class="pa-0 ma-0">
  <v-dialog v-model="popup" max-width="1000px" persistent>
    <v-card>
      <v-card-title>
        <h2 v-if="status == 'completed'">Study Set Finished</h2>
        <h2 v-else-if="status == 'expired'">Study Set Expired</h2>
      </v-card-title>
      <v-card-text v-if="status == 'completed'">
        <p v-if="inTestMode">
          Thanks for completing test mode! Click below to go back to the create study
          set screen.
        </p>
        <p v-else>
          You've finished this study set! Would you like to create another set with the
          same settings or go back to the the create study set screen to change options?
        </p>
      </v-card-text>
      <v-card-text v-else-if="status == 'expired'">
        <p v-if="inTestMode">
          This test mode study set has expired! Click below to go back to the create
          study set screen.
        </p>
        <p v-else>
          This study set has expired! Would you like to create another set with the same
          settings or go back to the the create study set screen to change options?
        </p>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn
          v-show="!inTestMode"
          ref="same"
          color="primary"
          text
          @click="continueStudy"
        >
          Create: Same Settings
        </v-btn>
        <v-btn color="primary" text @click="goToDeck">
          Back: Change Options
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";
  import { parseISO } from "date-fns";

  @Component
  export default class StudySet extends Vue {
    $refs!: {
      same: Vue;
    };
    popup = false;
    status = "studying";

    async mounted() {
      this.popup = this.isFinished != "studying";
    }

    get isFinished() {
      if (
        studyStore.studyset !== null &&
        studyStore.studyset.num_unstudied == 0 &&
        studyStore.studyset.needs_restudy != true
      ) {
        // this.status = "completed";
        return "completed";
      } else if (
        mainStore.userProfile &&
        mainStore.userProfile.study_set_expiry_date &&
        parseISO(mainStore.userProfile.study_set_expiry_date) < new Date()
      ) {
        // this.status = "expired";
        return "expired";
      } else {
        // this.status = "studying";
        return "studying";
      }
    }

    get isRetired() {
      // return mainStore.userProfile && parseISO(mainStore.userProfile.study_set_expiry_date) > ;
      if (mainStore.userProfile && mainStore.userProfile.study_set_expiry_date) {
        console.log(
          "is retired:",
          parseISO(mainStore.userProfile.study_set_expiry_date) < new Date(),
        );
        return parseISO(mainStore.userProfile.study_set_expiry_date) < new Date();
      } else {
        return false;
      }
    }

    get inTestMode() {
      return studyStore.inTestMode;
    }

    continueStudy() {
      studyStore.getStudyFacts();
      this.popup = false;
    }

    goToDeck() {
      studyStore.setInTestMode(false);
      this.popup = false;
      this.$router.push("/main/study/decks");
    }

    @Watch("isFinished")
    onIsFinishedChanged() {
      this.popup = this.isFinished != "studying";
      this.status = this.isFinished;
      setTimeout(() => {
        (this.$refs.same.$el as HTMLInputElement).focus();
      });
    }
  }
</script>
