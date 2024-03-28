<template class="pa-0 ma-0">
  <v-main class="pa-0 ma-0">
    <v-dialog v-model="mnemonic_study_tip" @click:outside="exit()">
      <v-card>
        <v-card-title>
          <v-col cols="12" md="7" lg="6" class="pl-0 ml-0">
            <h2>University of Maryland Research Study</h2>
          </v-col>
          <v-col cols="12" md="5" lg="6">
            <v-img
              :src="require('@/assets/umd-horizontal.png')"
              max-height="50"
              contain
            ></v-img>
          </v-col>
        </v-card-title>
        <div class="px-2">
          <v-card-text class="subtitle-1">
              We are a team of researchers at the University of Maryland who have
              recently developed KAR³L, the first flashcard scheduler powered by machine
              learning and natural language processing (NLP). Our hope is that with these
              advanced techniques, we can research and develop methods to help students learn more
              effectively. If you are interested in learning more about our mission, you
              can visit our <a target="_blank" href="https://nbalepur.github.io/assets/html/KARL">research project website</a>
              .
              At this point, we are conducting a funded user study to see if
              model-generated mnemonic devices can help students more effectively
              (described below). Come join us to help us build the next generation of
              NLP-powered adaptive learning tools!
          </v-card-text>

          <v-card-text class="subtitle-1">
            If you study our deck titled "GRE Vocab" in KAR³L, you will be participating in our
            research study with the University of Maryland, which spans from 02/26/2024
            to 05/26/2024. In this research study, we will be collecting your feedback
            to improve our mnemonic device generation. None of your personal information
            will be collected or released. Users participating in our study are eligible
            to receive
            <b>monetary rewards</b>, summarized below. Full instructions for our user
            study can be found
            <a
              target="_blank"
              href="https://docs.google.com/document/d/1Ecv2BbHN_AAsmv7Orf7IGCu8ENGbC5mRyRKcNKjc3fU/edit?usp=sharing"
              >here</a
            >.
          </v-card-text>
          <v-card-title>
            Monetary Reward Structure
          </v-card-title>
          <v-card-text class="subtitle-1">
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
            <br />
            You can check out the "statistics" page to see your progress on these
            rewards! (see "Vocab Facts Studied" and "Mnemonics Rated")
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
          <v-card-text class="subtitle-1">
            If you have any questions or concerns, please feel to reach out to me
            (Nishant Balepur), a co-investigator of the project (University of Maryland,
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
          <v-btn ref="begin" color="primary" text @click="exit">
            Got it!
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-main>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  @Component
  export default class MnemonicStudy extends Vue {
    mnemonic_study_tip = false;

    async mounted() {
      this.mnemonic_study_tip = this.$router.currentRoute.name === "mnemonic-study";
    }

    exit() {
      this.mnemonic_study_tip = false;
      if (this.$router.currentRoute.name === "mnemonic-study") {
        console.log('pushing');
        this.$router.push("/landing");
      }
    }
  }
</script>

<style></style>
