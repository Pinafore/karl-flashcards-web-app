<template>
  <v-container fluid>
    <v-card class="mx-3 my-1 py-1 px-3">
      <v-card-title primary-title class="mx-3 my-0 pa-0">
        <div class="headline primary--text">Learn</div>
        <v-spacer></v-spacer>
        <v-btn
          v-if="$vuetify.breakpoint.smAndDown"
          :disabled="!show.enable_actions"
          text
          icon
          @click="dialog = true"
        >
          <v-icon>mdi-information</v-icon>
        </v-btn>
        <v-btn
          v-else
          :disabled="!show.enable_actions"
          class="ma-1 pa-2"
          @click="dialog = true"
        >
          <v-icon>mdi-information</v-icon>Debug (Alt-/)
        </v-btn>
        <v-btn
          v-if="$vuetify.breakpoint.smAndDown"
          :disabled="!show.enable_actions"
          text
          icon
          @click="suspend()"
        >
          <v-icon>mdi-star</v-icon>
        </v-btn>
        <v-btn
          v-else
          :disabled="!show.enable_actions"
          class="ma-1 pa-2"
          @click="mark()"
        >
          <v-icon left>mdi-star</v-icon>Mark (Alt-M)
        </v-btn>
        <v-btn
          v-if="$vuetify.breakpoint.smAndDown"
          :disabled="!show.enable_actions"
          text
          icon
          @click="mark()"
        >
          <v-icon>mdi-star</v-icon>
        </v-btn>
        <v-btn
          v-else
          :disabled="!show.enable_actions"
          class="ma-1 pa-2"
          @click="suspend()"
        >
          <v-icon left>mdi-pause</v-icon>Suspend (Alt-S)
        </v-btn>
        <v-btn
          v-if="$vuetify.breakpoint.smAndDown"
          :disabled="!show.enable_report"
          text
          icon
          @click="report()"
        >
          <v-icon>mdi-alert-octagon</v-icon>
        </v-btn>
        <v-btn
          v-else
          class="ma-1 pa-2"
          :disabled="!show.enable_report"
          @click="report()"
        >
          <v-icon left>mdi-alert-octagon</v-icon>Report (Alt-R)
        </v-btn>
        <v-btn
          v-if="$vuetify.breakpoint.smAndDown"
          :disabled="!show.enable_actions"
          text
          icon
          @click="remove()"
        >
          <v-icon>mdi-delete</v-icon>
        </v-btn>
        <v-btn
          v-else
          class="ma-1 pa-2"
          :disabled="!show.enable_actions"
          @click="remove()"
        >
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
        <div v-show="show.marked" style="margin-left: auto;">&#11088;&nbsp;</div>
      </v-card-title>
      <v-card-text class="pb-2">
        <div class="title primary--text">
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
        <div class="title primary--text py-2">
          Answer: {{ show.fact && show.fact.answer }}
        </div>
        <div class="title pb-2">You typed: '{{ typed }}'</div>
        <div
          v-if="recommendation"
          class="title primary--text py-2"
          :style="{ color: 'green !important' }"
        >
          KAR³L Believes Your Answer Was Right (Enter to Accept)
        </div>
        <div
          v-else
          class="title primary--text py-2"
          :style="{ color: 'red !important' }"
        >
          KAR³L Believes Your Answer Was Wrong (Enter to Accept)
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
      const deckIds = this.$router.currentRoute.query.deck;
      if (deckIds) {
        if (typeof deckIds === "string") {
          studyStore.setDeckIds([Number(deckIds)]);
        } else {
          studyStore.setDeckIds(deckIds.map(Number));
        }
      }
      await studyStore.getNextShow();
      window.addEventListener("keydown", this.handleKeyPress);
    }

    public async destroyed() {
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

    public async mark() {
      await studyStore.markFact();
    }

    public async response(response) {
      if (this.show.fact) {
        await studyStore.addToSchedule({
          fact_id: this.show.fact.fact_id,
          typed: this.typed,
          response: response,
          elapsed_seconds_text: this.frontTime,
          elapsed_seconds_answer: this.backTime,
        });
        this.resetCard();
        await studyStore.updateSchedule();
      }
    }
  }
</script>
