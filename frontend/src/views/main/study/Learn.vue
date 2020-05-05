<template>
  <v-container fluid>
    <v-card class="mx-3 my-1 py-1 px-3">
      <v-card-title v-show="show.enable_actions" primary-title class="mx-3 my-0 pa-0">
        <div class="headline primary--text ma-0 pa-0">Learn</div>
        <v-spacer></v-spacer>
        <v-btn v-if="$vuetify.breakpoint.smAndDown" text icon @click="dialog = true">
          <v-icon>mdi-information</v-icon>
        </v-btn>
        <v-btn v-else class="ma-1 pa-2" @click="dialog = true">
          <v-icon>mdi-information</v-icon>Debug (Alt-/)
        </v-btn>
        <v-btn v-if="$vuetify.breakpoint.smAndDown" text icon @click="suspend()">
          <v-icon>mdi-pause</v-icon>
        </v-btn>
        <v-btn v-else class="ma-1 pa-2" @click="suspend()">
          <v-icon left>mdi-pause</v-icon>Suspend (Alt-S)
        </v-btn>
        <div v-if="show.enable_report">
          <v-btn v-if="$vuetify.breakpoint.smAndDown" text icon @click="report()">
            <v-icon>mdi-alert-octagon</v-icon>
          </v-btn>
          <v-btn v-else class="ma-1 pa-2" @click="report()">
            <v-icon left>mdi-alert-octagon</v-icon>Report (Alt-R)
          </v-btn>
        </div>
        <v-btn v-if="$vuetify.breakpoint.smAndDown" text icon @click="remove()">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
        <v-btn v-else class="ma-1 pa-2" @click="remove()">
          <v-icon left>mdi-delete</v-icon>Delete (Alt-R)
        </v-btn>
      </v-card-title>
    </v-card>
    <v-card class="my-2 mx-3 px-3 py-3">
      <v-card-title class="py-2 pb-0">
        <div
          v-if="
            show.enable_actions &&
              show.fact &&
              show.fact.category &&
              show.fact.category.toString() !== 'None' &&
              show.fact.category.toString() !== 'Other'
          "
          class="title"
        >
          Category: {{ show.fact.category }}
        </div>
        <div v-else class="title">Front</div>
        <div
          v-if="show.enable_actions && show.fact && show.fact.identifier"
          class="title"
        >
          &nbsp; — Identify {{ show.fact.identifier }}
        </div>
      </v-card-title>
      <v-card-text class="pb-2">
        <div class="title primary--text text--darken-2">
          {{ show.text }}
        </div>
      </v-card-text>
      <v-card-text v-show="show.enable_actions" class="pt-3">
        <v-text-field
          id="answer"
          v-model="typed"
          solo
          label="Type Answer"
          autofocus
          class="hide-details"
        ></v-text-field>
      </v-card-text>
      <v-card-actions v-show="show.enable_actions">
        <v-btn @click="showAnswer">Show Answer</v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-show="showBack" class="my-2 mx-3 px-3 py-2">
      <v-card-title class="py-2 pb-0">
        <div class="title">Back</div>
      </v-card-title>
      <v-card-text class="pt-2 pb-0">
        <div class="title text--darken-2 pb-2">You typed: '{{ typed }}'</div>
        <div class="title primary--text text--darken-2 py-2">
          Answer: {{ show.fact && show.fact.answer }}
        </div>
        <div
          v-if="recommendation"
          class="title primary--text text--darken-2 py-2"
          :style="{ color: 'green !important' }"
        >
          KAR³L Suggests: Right (Enter to Accept)
        </div>
        <div
          v-else
          class="title primary--text text--darken-2 py-2"
          :style="{ color: 'red !important' }"
        >
          KAR³L Suggests: Wrong (Enter to Accept)
        </div>
        <v-text-field
          id="retype_answer"
          v-model="retyped"
          solo
          label="Retype Answer"
          autofocus
          class="hide-details pt-3"
        ></v-text-field>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-row class="shrink">
          <v-col class="ma-1 pa-1 shrink">
            <v-btn
              ref="again"
              :color="!recommendation ? 'red' : ''"
              @click="response(false)"
              >wrong (1)</v-btn
            >
          </v-col>
          <v-col class="ma-1 pa-1 shrink">
            <v-btn
              ref="good"
              :color="recommendation ? 'green' : ''"
              @click="response(true)"
              >right (2)</v-btn
            >
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
    <v-dialog v-model="dialog" scrollable>
      <v-card>
        <v-card-title>
          <h2>Debug</h2>
        </v-card-title>
        <v-card-text>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div v-html="show.fact && show.fact.rationale"></div>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="dialog = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { studyStore } from "@/utils/store-accessor";

  @Component
  export default class Learn extends Vue {
    showBack = false;
    typed = "";
    retyped = "";
    dialog = false;

    get facts() {
      return studyStore.facts;
    }

    get show() {
      return studyStore.show;
    }

    get frontTime() {
      return studyStore.frontTime;
    }

    get backTime() {
      return studyStore.backTime;
    }

    get recommendation() {
      return studyStore.recommendation;
    }

    public async mounted() {
      await studyStore.getNextShow();
      window.addEventListener("keydown", this.handleKeyPress);
    }

    public async destroyed() {
      // commitResetFacts(this.$store);
      studyStore.setShowLoading();
      studyStore.emptySchedule();
      window.removeEventListener("keydown", this.handleKeyPress);
    }

    public handleKeyPress(e) {
      const KeyBoardCode = String(e.code);

      if (e.altKey && KeyBoardCode == "KeyS") {
        this.suspend();
      } else if (e.altKey && KeyBoardCode == "Slash") {
        this.dialog = !this.dialog;
      } else if (e.altKey && KeyBoardCode == "KeyR") {
        this.report();
      } else if (this.showBack) {
        this.determineResponse(KeyBoardCode);
      } else if (KeyBoardCode == "Enter") {
        this.showAnswer();
      } else {
        //this.$ref.typed.$el.focus() doesn't work some reason
        document.getElementById("answer")!.focus(); // eslint-disable-line
      }
    }

    public determineResponse(KeyBoardCode) {
      switch (KeyBoardCode) {
        case "Enter":
          this.response(this.recommendation);
          break;
        case "Digit1":
          this.response(false);
          break;
        case "Digit2":
          this.response(true);
          break;
        default:
          // TODO: Don't use getElementById
          document.getElementById("retype_answer")!.focus(); //eslint-disable-line
          break;
      }
    }

    public async showAnswer() {
      console.log("SHOWING ANSWER");
      await studyStore.evaluateAnswer(this.typed);
      this.showBack = true;
    }

    public resetCard() {
      this.showBack = false;
      this.typed = "";
      this.retyped = "";
    }

    public async suspend() {
      await studyStore.suspendFact();
      this.resetCard();
    }

    public async report() {
      await studyStore.reportFact();
      this.resetCard();
    }

    public async remove() {
      await studyStore.deleteFact();
      this.resetCard();
    }

    public async response(response) {
      if (this.show.fact) {
        studyStore.markBackTime();
        studyStore.addToSchedule(
          this.show.fact.fact_id,
          this.typed,
          response,
          this.frontTime,
          this.backTime,
        );
        await studyStore.updateSchedule();
        this.resetCard();
      }
    }
  }
</script>
