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
          to generally take less than fifteen minutes. You may resume your regular study
          after completing this test mode.
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
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";

  @Component
  export default class TestPopup extends Vue {
    popup = false;
    // May be good to have a popup when test mode is done

    async mounted() {
      this.popup = this.inTestMode;
    }

    get inTestMode() {
      return studyStore.inTestMode;
    }

    @Watch("inTestMode")
    onIsTestModeChanged() {
      this.popup = true;
    }

    startTesting() {
      this.popup = false;
    }
  }
</script>

<style></style>
