<template class="pa-0 ma-0">
  <v-main class="pa-0 ma-0">
    <v-dialog v-model="onboarding" width="1000">
      <v-card>
        <v-card-title>
          <h2>Tips</h2>
        </v-card-title>
        <v-card-text v-if="this.$router.currentRoute.name === 'public-decks'">
          KAR³L has decks of pre-made facts. Choose the decks you're interested in and
          click "Add Decks" to continue!
        </v-card-text>
        <v-card-text v-if="this.$router.currentRoute.name === 'decks'">
          In the create study set screen, you can select a specific deck or multiple
          decks to study facts from. Click the checkboxes next to the deck names in
          order to select multiple decks.
        </v-card-text>
        <div v-if="this.$router.currentRoute.name === 'learn'" class="px-2">
          <v-card-subtitle>
            Learning Facts
          </v-card-subtitle>
          <v-card-text>
            KAR³L automatically suggests facts for you to learn and review. Text fields
            are provided for you to optional type and retype answers to questions. After
            seeing the answer, evaluate your performance with 'right' or 'wrong'.
          </v-card-text>
          <v-card-subtitle>
            Test Mode
          </v-card-subtitle>
          <v-card-text>
            During the daily test mode for phase 2 research, you must type a response to
            a question unless you do not know it. While you may override automatic
            evaluations to correct errors, good faith attempts are required for gift
            card eligibility. During test mode, the toolbar is unavailable.
          </v-card-text>
          <v-card-text>
            Outside of test mode, typing answers is still recommended so KAR³L can
            automatically suggest an answer evaluation. Press 'Enter' to follow KAR³L's
            suggestion. If you do not type or disagree with the evaluation, you may
            manually choose 'right' and 'wrong'.
          </v-card-text>
          <v-card-subtitle>
            Answer Evaluation
          </v-card-subtitle>
          <v-card-text>
            Typing answers is recommended so KAR³L can automatically suggest an answer
            evaluation. Press 'Enter' to follow KAR³L's suggestion. If you do not type
            or disagree with the evaluation, you may manually choose 'right' and
            'wrong'.
          </v-card-text>
          <v-card-subtitle>
            Toolbar Actions (Regular Study Only)
          </v-card-subtitle>
          <v-card-text>
            <ul>
              <li>
                Debug (Alt-/) - View stats that detail why KAR³L showed you this fact.
              </li>
              <li>
                Favorite (Alt-M) - Allows you to "bookmark" facts to easily find in the
                browser. Does not affect scheduling.
              </li>
              <li>
                Suspend (Alt-S) - Tells KAR³L to not show this fact again until you
                unsuspend it in the browser.
              </li>
              <li>
                Delete (Alt-D) - Never show this fact again during study or in the
                browser. In shared decks, only deletes for you personally.
              </li>
              <li>
                Report (Alt-R) - Only shown when you do not own the fact, report allows
                you to suggest changes to fix errors in an unowned fact. The fact is not
                shown again until the report is resolved.
              </li>
              <li>
                Edit (Alt-E) - Only shown when you own the fact, edit allows you to
                directly change a fact while reviewing it.
              </li>
            </ul>
          </v-card-text>
          <v-card-subtitle>
            Keyboard Shortcuts
          </v-card-subtitle>
          <v-card-text>
            On large screens, all keyboard shortcuts are listed next to their respective
            buttons. On smaller screens, hover over button icons to view name and
            keyboard shortcut.
          </v-card-text>
        </div>

        <!-- <v-card-text class="pb-0">
          <a @click="noMoreHelp"
            >Familiar with KAR³L? Click here to stop showing tips.</a
          >
        </v-card-text> -->
        <v-card-actions class="pt-0">
          <v-spacer></v-spacer>
          <v-btn ref="begin" color="primary" text @click="noMoreHelp">
            Stop Showing Tips
          </v-btn>
          <v-btn ref="begin" color="primary" text @click="hideTip">
            Got it!
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-main>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";

  @Component
  export default class Onboard extends Vue {
    $refs!: {
      begin: Vue;
    };
    onboard = false;

    async mounted() {
      await mainStore.getUserProfile();
      this.getUpdate();
    }

    get onboarding() {
      return mainStore.onboarding;
    }

    set onboarding(value) {
      mainStore.setOnboarding(value);
    }

    // Not mainStore.recallPopup as that can cause a race, it may not be set to true yet
    // get recallPopup() {
    //   return this.currentRecallTarget == -1;
    // }

    get testModePopup() {
      return mainStore.testModePopup;
    }

    get currentRecallTarget() {
      return mainStore.userProfile?.recall_target ?? -1;
    }

    getUpdate() {
      if (this.$router.currentRoute.name === "decks") {
        mainStore.setOnboarding(this.show_help && !this.testModePopup);
      } else {
        mainStore.setOnboarding(this.show_help);
      }
      if (this.onboarding) {
        setTimeout(() => {
          (this.$refs.begin.$el as HTMLInputElement).focus();
        });
      }
    }

    get show_help() {
      return mainStore.userProfile?.show_help ?? false;
    }

    @Watch("recallPopup")
    recallPopupChanged() {
      this.getUpdate();
    }

    async noMoreHelp() {
      mainStore.updateUserHelp(false);
      await this.hideTip();
    }

    async hideTip() {
      mainStore.setOnboarding(false);
      await new Promise((resolve) => setTimeout(resolve, 100));
      studyStore.setShowActions();
    }
  }
</script>

<style></style>
