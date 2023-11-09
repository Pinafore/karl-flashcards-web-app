<template class="pa-0 ma-0">
  <v-dialog
    v-model="testModePopup"
    max-width="1000px"
    persistent
    @click:outside="startTesting"
    @keydown.enter="startTesting"
  >
    <v-card>
      <v-card-title>
        <h2>Phase 2: Test Mode</h2>
      </v-card-title>
      <v-card-text>
        <p>
          In KAR³L phase 2, we are running a study to perform a more rigorous evaluation
          of flashcard scheduling systems. We therefore require you to first complete
          studying our 10 test mode flashcards during this ~3 week period. Please
          complete this test mode studyset before it expires two hours after creation.
          You may resume your regular study after completing these cards.
        </p>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn ref="begin" color="primary" text @click="startTesting">
          Begin
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
  import { Component, Vue, Watch, Prop } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";

  @Component
  export default class TestPopup extends Vue {

    @Prop() readonly shouldShow!: boolean;

    $refs!: {
      begin: Vue;
    };
    popup = false;
    // May be good to have a popup when test mode is done

    async mounted() {
      mainStore.setTestModePopup(this.inTestMode && this.shouldShow);
    }

    get inTestMode() {
      return studyStore.inTestMode;
    }

    get onboarding() {
      return mainStore.onboarding;
    }

    get recallPopup() {
      return mainStore.recallPopup;
    }

    get testModePopup() {
      return mainStore.testModePopup;
    }

    @Watch("inTestMode")
    onIsTestModeChanged() {
      if (this.shouldShow) {
      mainStore.setTestModePopup(this.inTestMode);
        setTimeout(() => {
        (this.$refs.begin.$el as HTMLInputElement).focus();
      });
      }
    }

    @Watch("onboarding")
    onOnboardingChanged() {
      mainStore.setTestModePopup(false);
    }

    async startTesting() {
      this.$router.push({
        path: "/main/study/learn?quick=false",
        query: { test: String(1) },
      });
      mainStore.setTestModePopup(false);
      await new Promise((resolve) => setTimeout(resolve, 100));
      studyStore.setShowActions();
    }
  }
</script>

<style></style>
