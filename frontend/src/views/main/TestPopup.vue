<template class="pa-0 ma-0">
  <v-dialog v-model="popup" max-width="1000px" persistent @click:outside="startTesting">
    <v-card>
      <v-card-title>
        <h2>Phase 2: Test Mode</h2>
      </v-card-title>
      <v-card-text>
        <p>
          In KAR³L phase 2, we ask users to periodically study a test set of general
          knowledge flashcards. This will allow us to perform a more rigorous evaluation
          of current and future scheduling systems. We expect each session of test mode
          to generally taken less than fifteen minutes.
        </p>
      </v-card-text>

      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="startTesting">
          Begin
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  @Component
  export default class TestPopup extends Vue {
    popup = false;

    async mounted() {
      await mainStore.getUserProfile();
      this.onboard = mainStore.userProfile?.test_mode ?? false;
    }

    startTesting() {
      this.popup = false;
    }
  }
</script>

<style></style>
