<template class="pa-0 ma-0">
  <v-snackbar bottom right :value="updateExists" :timeout="-1" color="primary">
    Update available. KAR³L may not work properly until updated.
    <v-btn text @click="refreshApp">
      Update
    </v-btn>
  </v-snackbar>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";

  @Component
  export default class UpdateAvailable extends Vue {
    updateExists = false;
    refreshing = false;
    registration: CustomEvent["detail"] = undefined;

    created() {
      document.addEventListener(
        "swUpdated",
        ((event: CustomEvent) => {
          this.registration = event.detail;
          this.updateExists = true;
        }) as EventListener,
        { once: true },
      );
      navigator.serviceWorker.addEventListener("controllerchange", () => {
        if (this.refreshing) return;
        this.refreshing = true;
        window.location.reload();
      });
    }

    refreshApp() {
      this.updateExists = false;
      if (this.registration !== undefined) {
        if (!this.registration || !this.registration.waiting) return;
        this.registration.waiting.postMessage({ type: "SKIP_WAITING" });
      }
    }
  }
</script>

<style></style>
