<template class="pa-0 ma-0">
  <v-dialog v-model="popup" max-width="1000px" persistent>
    <v-card>
      <v-card-title>
        <h2>Study Set Finished</h2>
      </v-card-title>
      <v-card-text>
        <p v-if="inTestMode">
          Thanks for completing test mode! Would you like to create a study set with
          your originally selected settings or go back to the create study set screen?
        </p>
        <p v-else>
          You've finished this study set! Would you like to create another set with the
          same settings or go back to the the create study screen to change options?
        </p>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn ref="same" color="primary" text @click="continueStudy">
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

  @Component
  export default class StudySet extends Vue {
    $refs!: {
      same: Vue;
    };
    popup = false;

    async mounted() {
      this.popup = this.isFinished;
    }

    get isFinished() {
      return (
        studyStore.studyset !== null &&
        studyStore.studyset.num_unstudied == 0 &&
        studyStore.studyset.needs_restudy != true
      );
    }

    get inTestMode() {
      return studyStore.inTestMode;
    }

    continueStudy() {
      studyStore.getStudyFacts();
      this.popup = false;
    }

    goToDeck() {
      this.$router.push("/main/study/decks");
    }

    @Watch("isFinished")
    onIsFinishedChanged() {
      this.popup = this.isFinished;
      setTimeout(() => {
        (this.$refs.same.$el as HTMLInputElement).focus();
      });
    }
  }
</script>
