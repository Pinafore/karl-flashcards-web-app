<template class="pa-0 ma-0">
  <v-dialog v-model="popup" max-width="1000px" @click:outside="returnHome">
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
      <span v-else>
        <v-card-title>
          <h2>An Error Occurred</h2>
        </v-card-title>
      </span>
      <v-card-actions>
        <v-btn @click="returnHome">Return to Home Screen</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore } from "@/store";

  @Component
  export default class ConnectionPopup extends Vue {
    popup = false;
    type = "";

    mounted() {
      this.checkPopup();
    }

    get connectionError() {
      return mainStore.connectionError;
    }

    get schedulerError() {
      return mainStore.connectionError;
    }

    @Watch("connectionError")
    onConnectionErrorChanged() {
      this.checkPopup();
    }

    @Watch("schedulerError")
    onSchedulerErrorChanged() {
      this.checkPopup();
    }

    checkPopup() {
      this.popup = mainStore.connectionError || mainStore.schedulerError;
      if (mainStore.connectionError) {
        this.type = "connection";
      } else if (mainStore.schedulerError) {
        this.type = "scheduler";
      }
    }

    returnHome() {
      this.popup = false;
      this.$router.push("/main/dashboard");
    }
  }
</script>

<style></style>
