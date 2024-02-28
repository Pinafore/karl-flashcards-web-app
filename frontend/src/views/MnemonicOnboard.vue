<template class="pa-0 ma-0">
  <v-main class="pa-0 ma-0">
    <v-dialog v-model="mnemonicOnboarding" width="1000">
      <v-card>
        <v-card-title>
          <h2>Mnemonic Research Study</h2>
        </v-card-title>
        <div class="px-2">
          <v-card-text>
            By studying this deck, you will be participating in our research study,
            which spans from 02/26/2024 to 05/26/2024. In this research study, we will
            be collecting your feedback to improve our mnemonic device generation. None
            of your personal information will be collected or released. Users
            participating in our study are eligible to receive <b>monetary rewards</b>,
            summarized below. Full instructions for our user study can be found
            <a
              target="_blank"
              href="https://docs.google.com/document/d/1Ecv2BbHN_AAsmv7Orf7IGCu8ENGbC5mRyRKcNKjc3fU/edit?usp=sharing"
              >here</a
            >.
          </v-card-text>
          <v-card-title>
            Monetary Reward Structure
          </v-card-title>
          <v-card-text>
            As a token of appreciation for helping us with our study, we will have two
            ways for users to win rewards (both rewards can be earned):
            <ol>
              <li>
                <b>Base Reward:</b> Users who study 20+ GRE flashcards a day over 5
                unique days will be entered into a raffle to
                <b>win one of 50 $25 gift cards</b>
              </li>
              <li>
                <b>Power user Reward:</b> Users who give feedback on 75 or more mnemonic
                devices will be entered into a raffle to
                <b>win one of 50 $25 gift cards</b>
              </li>
            </ol>
          </v-card-text>
          <!-- <v-card-title>
            Notice on Accurate Ratings
          </v-card-title>
          <v-card-text>
            We have also inserted sanity checks (e.g. examples where one mnemonic is
            clearly worse) to ensure that you give accurate feedback. If you are found
            to be abusing our system, you will be notified and disqualified from
            receiving rewards
          </v-card-text> -->

          <v-card-title>
            Contact
          </v-card-title>
          <v-card-text>
            If you have any questions, please contact me (Nishant Balepur), a
            co-investigator of the project (University of Maryland,
            <a target="_blank" href="mailto:nbalepur@umd.edu">nbalepur@umd.edu</a>). You
            can also join our
            <a target="_blank" href="https://discord.gg/PTfEmHd">Discord</a>. Thanks
            again for your help, and happy studying!
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
            Stop Showing Popup
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
  import { Component, Vue, Watch, Prop } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";

  @Component
  export default class MnemonicOnboard extends Vue {
    @Prop() readonly shouldShow!: boolean;
    $refs!: {
      begin: Vue;
    };
    mnemonicOnboard = false;

    async mounted() {
      await mainStore.getUserProfile();
      this.getUpdate();
    }

    get mnemonicOnboarding() {
      return mainStore.mnemonicOnboarding;
    }

    set mnemonicOnboarding(value) {
      mainStore.setMnemonicOnboarding(value);
    }

    get testModePopup() {
      return mainStore.testModePopup;
    }

    get currentRecallTarget() {
      return mainStore.userProfile?.recall_target ?? -1;
    }

    getUpdate() {
      if (this.shouldShow) {
        mainStore.setMnemonicOnboarding(this.show_mnemonic_help);
        if (this.mnemonicOnboarding) {
          setTimeout(() => {
            (this.$refs.begin.$el as HTMLInputElement).focus();
          });
        }
      }
    }

    @Watch("shouldShow")
    onShouldShowChange(newValue: boolean, oldValue: boolean) {
      this.getUpdate();
    }

    get show_mnemonic_help() {
      return mainStore.userProfile?.show_mnemonic_help ?? false;
    }

    @Watch("recallPopup")
    recallPopupChanged() {
      this.getUpdate();
    }

    async noMoreHelp() {
      mainStore.updateUserHelpMnemonic(false);
      await this.hideTip();
    }

    async hideTip() {
      mainStore.setMnemonicOnboarding(false);
      await new Promise((resolve) => setTimeout(resolve, 100));
      studyStore.setShowActions();
    }
  }
</script>

<style></style>
