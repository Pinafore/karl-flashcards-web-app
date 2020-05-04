<template>
  <v-container fluid>
    <v-card class="mx-3 my-1 py-1 px-3">
      <v-card-title primary-title class="mx-3 my-0 pa-0">
        <v-col class="headline primary--text ma-0 pa-0">Learn</v-col>
        <v-btn v-if="$vuetify.breakpoint.xsOnly" text icon @click="dialog = true">
          <v-icon>info</v-icon>
        </v-btn>
        <v-btn v-else class="ma-1 pa-2" @click="dialog = true">
          <v-icon>info</v-icon>Debug (Alt-/)
        </v-btn>
        <v-btn v-if="$vuetify.breakpoint.xsOnly" text icon @click="suspend()">
          <v-icon>pause</v-icon>
        </v-btn>
        <v-btn v-else class="ma-1 pa-2" @click="suspend()">
          <v-icon left>pause</v-icon>Suspend (Alt-S)
        </v-btn>
        <div v-if="fact && fact.public">
          <v-btn v-if="$vuetify.breakpoint.xsOnly" text icon @click="deleteOrReport()">
            <v-icon>report</v-icon>
          </v-btn>
          <v-btn v-else class="ma-1 pa-2" @click="deleteOrReport()">
            <v-icon left>report</v-icon>Report (Alt-R)
          </v-btn>
        </div>
        <div>
          <v-btn v-if="$vuetify.breakpoint.xsOnly" text icon @click="deleteOrReport()">
            <v-icon>delete</v-icon>
          </v-btn>
          <v-btn v-else class="ma-1 pa-2" @click="deleteOrReport()">
            <v-icon left>delete</v-icon>Delete (Alt-R)
          </v-btn>
        </div>
      </v-card-title>
    </v-card>
    <v-card class="my-2 mx-3 px-3 py-3">
      <v-card-title class="py-2 pb-0">
        <div
          v-if="
            !loading &&
              fact &&
              fact.category &&
              fact.category.toString() !== 'None' &&
              fact.category.toString() !== 'Other'
          "
          class="title"
        >
          Category: {{ fact.category }}
        </div>
        <div v-else class="title">Front</div>
        <div v-if="!loading && fact && fact.identifier" class="title">
          &nbsp;— Identify {{ fact.identifier }}
        </div>
      </v-card-title>
      <v-card-text class="pb-2">
        <div v-if="!loading && fact" class="title primary--text text--darken-2">
          {{ fact.front }}
        </div>
        <div v-else-if="loading" class="title primary--text text--darken-2">
          Loading next fact...
        </div>
        <div v-else class="title primary--text text--darken-2">
          You have finished your facts for now, check back in later!
        </div>
      </v-card-text>
      <v-card-text v-show="showAnsButtonAndField" class="pt-3">
        <v-text-field
          id="answer"
          v-model="answer"
          solo
          label="Type Answer"
          autofocus
          class="hide-details"
        ></v-text-field>
      </v-card-text>
      <v-card-actions v-show="showAnsButtonAndField">
        <v-btn @click="showAnswer">Show Answer</v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-show="showBack" class="my-2 mx-3 px-3 py-2">
      <v-card-title class="py-2 pb-0">
        <div class="title">Back</div>
      </v-card-title>
      <v-card-text class="pt-2 pb-0">
        <div v-if="fact" class="title text--darken-2 pb-2">
          You typed: '{{ answer }}'
        </div>
        <div v-if="fact" class="title primary--text text--darken-2 py-2">
          Answer: {{ fact.back }}
        </div>
        <div
          v-if="evalAnswer"
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
              :color="!evalAnswer ? 'red' : ''"
              @click="response('wrong')"
              >wrong (1)</v-btn
            >
          </v-col>
          <v-col class="ma-1 pa-1 shrink">
            <v-btn
              ref="good"
              :color="evalAnswer ? 'green' : ''"
              @click="response('right')"
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
          <div v-html="fact && fact.rationale"></div>
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
  // import { IComponents } from "@/interfaces";

  @Component
  export default class Learn extends Vue {
    showAnsButtonAndField = true;
    showBack = false;
    answer = "";
    retyped = "";
    loading = true;
    time = 0;
    frontTime = 0;
    backTime = 0;
    timer: number | undefined;
    dialog = false;

    get fact() {
      if (this.facts.length > 0) {
        return this.facts[0];
      } else {
        return null;
      }
      //   if (this.facts.length > 0) {
      //     return this.facts[0];
      //   } else {
      //   }
    }

    get facts() {
      return studyStore.facts;
    }

    get evalAnswer() {
      return false;
      //   return readEvalAnswer(this.$store);
    }

    public async mounted() {
      // const self = this;
      // this.showBack = false;
      // this.loading = true;
      // this.showAnsButtonAndField = false;
      // this.dialog = false;
      // this.resetTimer();
      // this.getFactSet().finally(function() {
      //   self.showAnsButtonAndField = self.fact !== undefined;
      //   self.loading = false;
      //   self.startTimer();
      // });
      // this.userProfile;
      // window.addEventListener("keydown", this.handleKeyPress);
    }

    public async destroyed() {
      // commitResetFacts(this.$store);
      window.removeEventListener("keydown", this.handleKeyPress);
    }

    public updateTimer() {
      this.time++;
    }

    public resetTimer() {
      clearInterval(this.timer);
      this.time = 0;
    }

    public startTimer() {
      this.timer = setInterval(() => this.updateTimer(), 1000);
    }

    public handleKeyPress(e) {
      const KeyBoardCode = String(e.code);

      if (e.altKey && KeyBoardCode == "KeyS") {
        this.suspend();
      } else if (e.altKey && KeyBoardCode == "Slash") {
        this.dialog = !this.dialog;
      } else if (e.altKey && KeyBoardCode == "KeyR") {
        this.deleteOrReport();
      } else if (this.showBack) {
        this.determineResponse(KeyBoardCode);
      } else if (KeyBoardCode == "Enter") {
        this.showAnswer();
      } else {
        //this.$ref.answer.$el.focus() doesn't work some reason
        document.getElementById("answer")!.focus(); // eslint-disable-line
      }
    }

    // public async getFactSet() {
    //   const queryDeckIdsStrings = this.$router.currentRoute.query.deck;
    //   if (this.userProfile && this.userProfile.id !== null && queryDeckIdsStrings) {
    //     let queryDeckIds;
    //     if (
    //       typeof queryDeckIdsStrings === "string" ||
    //       typeof queryDeckIdsStrings === "number"
    //     ) {
    //       queryDeckIds = [Number(queryDeckIdsStrings)];
    //     } else {
    //       queryDeckIds = queryDeckIdsStrings.map(Number);
    //     }
    //     await dispatchGetDeckFacts(this.$store, {
    //       userId: this.userProfile.id,
    //       deckIds: queryDeckIds,
    //     });
    //   } else if (this.userProfile && this.userProfile.id !== null) {
    //     await dispatchGetFacts(this.$store, { userId: this.userProfile.id });
    //   }
    // }

    public determineResponse(KeyBoardCode) {
      switch (KeyBoardCode) {
        case "Enter":
          // this.response(this.evalAnswer);
          break;
        case "Digit1":
          this.response("wrong");
          break;
        case "Digit2":
          this.response("right");
          break;
        default:
          document.getElementById("retype_answer")!.focus();
          break;
      }
    }

    public async showAnswer() {
      // if (
      //   this.showAnsButtonAndField &&
      //   this.userProfile &&
      //   this.userProfile.id !== null
      // ) {
      //   this.showAnsButtonAndField = false;
      //   await dispatchEvaluateAnswer(this.$store, {
      //     factId: this.fact.id,
      //     typed: this.answer,
      //   });
      //   this.showBack = true;
      //   this.frontTime = this.time;
      // }
    }

    public resetCard() {
      // this.showBack = false;
      // this.answer = "";
      // this.retyped = "";
      // this.resetTimer();
      //
      // commitRemoveFirstFact(this.$store);
      // this.showAnsButtonAndField = this.fact !== undefined;
    }

    public checkEmpty() {
      // if (this.facts.length === 0) {
      //   this.loading = true;
      //   const self = this;
      //   this.getFactSet().finally(function() {
      //     self.showAnsButtonAndField = self.fact !== undefined;
      //     self.loading = false;
      //
      //     self.resetTimer();
      //     self.startTimer();
      //   });
      // } else {
      //   this.resetTimer();
      //   this.startTimer();
      // }
    }

    public async suspend() {
      // await dispatchSuspendFact(this.$store, this.fact.id);

      this.resetCard();
      this.checkEmpty();
    }

    public async deleteOrReport() {
      // await dispatchDeleteFact(this.$store, this.fact.id);

      this.resetCard();
      this.checkEmpty();
    }

    public async response(responseButtonText) {
      //   const oldFact = this.fact;
      //   const typed = this.answer;
      //   this.backTime = this.time - this.frontTime;
      //
      //   if (await this.$validator.validateAll()) {
      //     if (this.userProfile && this.userProfile.id !== null) {
      //       const factUpdate: FactScheduleUpdate = {
      //         review_datetime: new Date().toISOString(),
      //         front: oldFact.front,
      //         back: oldFact.back,
      //         typed: typed,
      //         response: responseButtonText,
      //         deck_id: oldFact.deck_id,
      //         elapsed_seconds_front: this.frontTime < 30 ? this.frontTime : 30,
      //         elapsed_seconds_back: this.backTime < 30 ? this.backTime : 30,
      //         answer_lines: oldFact.answer_lines,
      //       };
      //       const fact_ids: number[] = [oldFact.id];
      //       await dispatchUpdateFactSchedule(this.$store, {
      //         factIds: fact_ids,
      //         update: [factUpdate],
      //       });
      //     }
      //   }
      //
      //   this.resetCard();
      //   this.checkEmpty();
    }
  }
</script>
