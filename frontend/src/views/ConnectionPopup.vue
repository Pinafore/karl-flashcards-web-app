<template class="pa-0 ma-0">
  <v-dialog v-model="connectionPopup" max-width="1000px" @click:outside="goBack">
    <v-card>
      <span v-if="type === 'connection'">
        <v-card-title>
          <h2>Scheduler Connection Error</h2>
        </v-card-title>
        <v-card-text>
          Due to updates at the University of Maryland, College Park, the connection to
          KAR³L's scheduler is currently down. During this brief period of time, you
          will be unable to study facts or view statistics, but you may continue to
          access all other functionality (such as the fact browser). Please check back
          in a few hours and KAR³L will be ready again to schedule facts to review for
          you.
        </v-card-text>
      </span>
      <span v-else-if="type === 'scheduler'">
        <v-card-title>
          <h2>Scheduler Error</h2>
        </v-card-title>
        <v-card-text>
          There is a problem with the KAR³L scheduler and we are working on a solution.
          Please check back in a few hours and KAR³L will be ready again to schedule
          facts to review for you.
        </v-card-text>
      </span>
      <span v-else-if="type === 'inaccessibleDeckError'">
        <v-card-title>
          <h2>Jeopardy! Deck Unavailable</h2>
        </v-card-title>
        <v-card-text>
          The Jeopardy! deck is currently unavailable and may not be selected for study.
          All other public decks remain available to study and users may still create
          private decks or import them from or other flashcard apps like Anki. Apologies
          for the inconvenience caused.
        </v-card-text>
      </span>
      <span v-else>
        <v-card-title>
          <h2>An Error Occurred</h2>
        </v-card-title>
      </span>
      <v-card-actions>
        <v-btn v-if="type === 'inaccessibleDeckError'" @click="goBack">Return</v-btn>
        <v-btn v-else @click="goBack">Return to Home Screen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";

  @Component
  export default class ConnectionPopup extends Vue {
    type = "";

    mounted() {
      this.checkPopup();
    }

    destroyed() {
      mainStore.setInaccessibleDeckError(false);
    }

    get connectionPopup() {
      return mainStore.connectionPopup;
    }

    get connectionError() {
      return mainStore.connectionError;
    }

    get schedulerError() {
      return mainStore.schedulerError;
    }

    get inaccessibleDeckError() {
      return mainStore.inaccessibleDeckError;
    }

    @Watch("connectionError")
    onConnectionErrorChanged() {
      this.checkPopup();
    }

    @Watch("schedulerError")
    onSchedulerErrorChanged() {
      this.checkPopup();
    }

    @Watch("inaccessibleDeckError")
    onInaccessibleDeckErrorChanged() {
      this.checkPopup();
    }

    checkPopup() {
      const popup =
        mainStore.connectionError && studyStore.inTestMode !== true ||
        mainStore.schedulerError ||
        mainStore.inaccessibleDeckError;
      mainStore.setConnectionPopup(popup);
      if (mainStore.connectionError) {
        this.type = "connection";
      } else if (mainStore.schedulerError) {
        this.type = "scheduler";
      } else if (mainStore.inaccessibleDeckError) {
        this.type = "inaccessibleDeckError";
      }
    }

    goBack() {
      mainStore.setConnectionPopup(false);
      if (this.type === "inaccessibleDeckError") {
        mainStore.setInaccessibleDeckError(false);
        this.$router.back();
      } else {
        this.$router.push("/main/dashboard");
      }
    }
  }
</script>

<style></style>
