<template class="pa-0 ma-0">
  <div>
    <v-dialog v-model="offline" max-width="1000px" persistent>
      <v-card>
        <v-card-title>
          <h2>You Are Offline</h2>
        </v-card-title>
        <v-card-text>
          KAR³L requires an internet connection to use. We'll let you in when you're
          back online!
        </v-card-text>
      </v-card>
    </v-dialog>
    <v-snackbar bottom right :value="showBackOnline" :timeout="2000" color="primary">
      You're Back Online!
    </v-snackbar>
  </div>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";

  @Component
  export default class ConnectionError extends Vue {
    offline = !navigator.onLine;
    showBackOnline = false;

    mounted() {
      window.addEventListener("online", this.updateOnlineStatus);
      window.addEventListener("offline", this.updateOnlineStatus);
    }

    beforeDestroy() {
      window.removeEventListener("online", this.updateOnlineStatus);
      window.removeEventListener("offline", this.updateOnlineStatus);
    }

    updateOnlineStatus(e) {
      const { type } = e;
      this.offline = type !== "online";
    }

    @Watch("onLine")
    onLineChanged(v) {
      if (v) {
        this.showBackOnline = true;
        setTimeout(() => {
          this.showBackOnline = false;
        }, 1000);
      }
    }
  }
</script>

<style></style>
