<template>
  <v-container fluid style="max-width:1250px">
    <onboard></onboard>
    <connection-popup></connection-popup>
    <test-popup></test-popup>
    <RecallPopup></RecallPopup>
    <v-card class="mx-3 my-1 py-1 px-0 px-sm-3">
      <!--      <v-card-title  primary-title class="mx-3 my-0 pa-0">-->
      <!--        <div class="headline primary&#45;&#45;text">Test Mode</div>-->
      <!--      </v-card-title>-->
      <v-card-title primary-title class="mx-3 my-0 pa-0">
        <div v-if="inTestMode" class="headline primary--text">Test Mode</div>
        <div
          v-else-if="$vuetify.breakpoint.xsOnly || studyset === null"
          class="headline primary--text"
        >
          Study
        </div>
        <div v-else class="headline primary--text">
          {{ studyset.short_description }}
        </div>
        <div
          v-show="show.text !== `Loading`"
          class="headline primary--text"
          style="margin-left: .5em"
        >
          ({{ current_study_num }} of {{ num_facts }})
        </div>
        <v-spacer></v-spacer>

        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              v-if="$vuetify.breakpoint.mdAndDown"
              :disabled="!show.enable_actions"
              text
              icon
              v-bind="attrs"
              @click="dialog = true"
              v-on="on"
            >
              <v-icon>mdi-information</v-icon>
            </v-btn>
            <v-btn
              v-else
              :disabled="!show.enable_actions"
              class="ma-1 pa-2"
              v-bind="attrs"
              @click="dialog = true"
              v-on="on"
            >
              <v-icon>mdi-information</v-icon>Info: Alt-/
            </v-btn>
          </template>
          <span>Info (Alt-/)</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              v-if="$vuetify.breakpoint.mdAndDown"
              :disabled="!show.enable_actions"
              text
              icon
              v-bind="attrs"
              @click="mark()"
              v-on="on"
            >
              <v-icon>mdi-star</v-icon>
            </v-btn>
            <v-btn
              v-else
              :disabled="!show.enable_actions"
              class="ma-1 pa-2"
              v-bind="attrs"
              @click="mark()"
              v-on="on"
            >
              <v-icon left>mdi-star</v-icon>Mark: Alt-M
            </v-btn>
          </template>
          <span>Favorite (Alt-M)</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              v-if="$vuetify.breakpoint.mdAndDown"
              :disabled="!show.enable_actions"
              text
              icon
              v-bind="attrs"
              @click="suspend()"
              v-on="on"
            >
              <v-icon>mdi-pause</v-icon>
            </v-btn>
            <v-btn
              v-else
              :disabled="!show.enable_actions"
              class="ma-1 pa-2"
              v-bind="attrs"
              @click="suspend()"
              v-on="on"
            >
              <v-icon left>mdi-pause</v-icon>Suspend: Alt-S
            </v-btn>
          </template>
          <span>Suspend (Alt-S)</span>
        </v-tooltip>
        <v-tooltip bottom>
          <template v-slot:activator="{ on, attrs }">
            <v-btn
              v-if="$vuetify.breakpoint.mdAndDown"
              :disabled="!show.enable_actions"
              text
              icon
              v-bind="attrs"
              @click="remove()"
              v-on="on"
            >
              <v-icon>mdi-delete</v-icon>
            </v-btn>
            <v-btn
              v-else
              class="ma-1 pa-2"
              :disabled="!show.enable_actions"
              v-bind="attrs"
              @click="remove()"
              v-on="on"
            >
              <v-icon left>mdi-delete</v-icon>Delete: Alt-D
            </v-btn>
          </template>
          <span>Delete (Alt-D)</span>
        </v-tooltip>
        <span v-if="show.enable_report">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                v-if="$vuetify.breakpoint.mdAndDown"
                text
                icon
                v-bind="attrs"
                @click="report()"
                v-on="on"
              >
                <v-icon>mdi-alert-octagon</v-icon>
              </v-btn>
              <v-btn
                v-else
                class="ma-1 pa-2"
                v-bind="attrs"
                @click="report()"
                v-on="on"
              >
                <v-icon left>mdi-alert-octagon</v-icon>Report: Alt-R
              </v-btn>
            </template>
            <span>Report (Alt-R)</span>
          </v-tooltip>
        </span>
        <span v-else-if="show.enable_actions">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                v-if="$vuetify.breakpoint.mdAndDown"
                text
                icon
                v-bind="attrs"
                @click="edit()"
                v-on="on"
              >
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn v-else class="ma-1 pa-2" v-bind="attrs" @click="edit()" v-on="on">
                <v-icon left>mdi-pencil</v-icon>Edit: Alt-E
              </v-btn>
            </template>
            <span>Edit (Alt-E)</span>
          </v-tooltip>
        </span>
      </v-card-title>
    </v-card>
    <v-card class="my-2 mx-3 px-3 py-4 pb-5">
      <v-card-title class="py-0">
        <v-row no-gutters>
          <v-col cols="12" sm="auto">
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
          </v-col>
          <v-col cols="12" sm="auto">
            <div
              v-if="show.enable_actions && show.fact && show.fact.identifier"
              class="title"
            >
              <span class="hidden-xs-only">—</span>Identify {{ show.fact.identifier }}
            </div>
          </v-col>
        </v-row>

        <div v-show="show.marked" style="margin-left: auto;">&#11088;&nbsp;</div>
      </v-card-title>
      <v-card-text class="pb-0 pt-1">
        <div class="title primary--text">
          {{ show.text }}
        </div>
      </v-card-text>
      <v-card-text v-show="show.enable_actions" class="py-2">
        <v-text-field
          id="answer"
          ref="answerfield"
          v-model="typed"
          solo
          label="Recommended - Type Answer (Press any letter to focus)"
          autofocus
          hide-details="auto"
          @keydown="keyHandler"
        ></v-text-field>
      </v-card-text>
      <v-card-actions v-show="show.enable_actions && !showBack" class="px-4 pt-3 pb-2">
        <v-btn @click="showAnswer">Show Answer (Enter)</v-btn>
      </v-card-actions>
    </v-card>
    <v-card v-show="showBack && show.enable_actions" class="my-2 mx-3 px-3 py-4">
      <v-card-title class="py-0">
        <div class="title">Answer</div>
      </v-card-title>
      <v-card-text class="pb-0 pt-1">
        <div class="title primary--text">
          {{ show.fact && show.fact.answer }}
        </div>
        <div class="title">You typed: '{{ typed }}'</div>
        <div
          v-if="recommendation"
          class="title primary--text py-2"
          :style="{ color: 'green !important' }"
        >
          KAR³L Believes Your Response Was Correct
          <span class="hidden-xs-only">(Enter to Accept, Or Override Below)</span>
        </div>
        <div v-else class="title primary--text" :style="{ color: 'red !important' }">
          KAR³L Believes Your Response Was Wrong
          <span class="hidden-xs-only">(Enter to Accept, Or Override Below)</span>
        </div>
      </v-card-text>
      <v-card-text v-show="show.enable_actions" class="py-2">
        <v-text-field
          id="retype_answer"
          ref="retype"
          v-model="retyped"
          solo
          label="Optional - Retype Answer (Press any letter to focus)"
          autofocus
          hide-details="auto"
        ></v-text-field>
      </v-card-text>
      <v-card-actions class="pt-3 pb-1 px-5">
        <v-row class="shrink" justify="space-around">
          <v-col cols="5" sm="auto" class="ma-1 pa-1 py-0 shrink">
            <v-btn
              ref="wrong"
              :color="!recommendation ? 'red' : ''"
              class="px-2"
              @click="response(false)"
              >wrong ([)</v-btn
            >
          </v-col>
          <v-col id="response" cols="5" sm="auto" class="ma-1 pa-1 py-0 shrink">
            <v-btn
              ref="right"
              :color="recommendation ? 'green' : ''"
              class="px-2"
              @click="response(true)"
              >right (])</v-btn
            >
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
    <v-dialog v-model="dialog" scrollable>
      <v-card>
        <v-card-title>
          <h2>Information and Debugging</h2>
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
    <v-dialog
      v-model="editDialog"
      max-width="1000px"
      scrollable
      @click:outside="returnLearn"
    >
      <router-view name="edit"></router-view>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { studyStore, mainStore } from "@/utils/store-accessor";
  import Onboard from "@/views/Onboard.vue";
  import ConnectionPopup from "@/views/ConnectionPopup.vue";
  import RecallPopup from "@/views/main/RecallPopup.vue";
  import TestPopup from "@/views/main/TestPopup.vue";

  @Component({
    components: { TestPopup, ConnectionPopup, Onboard, RecallPopup },
  })
  export default class Learn extends Vue {
    $refs!: {
      answerfield: HTMLInputElement;
      retype: HTMLInputElement;
      right: HTMLButtonElement;
      wrong: HTMLButtonElement;
    };
    showBack = false;
    typed = "";
    retyped = "";
    dialog = false;
    editDialog = false;
    pressed = false;

    get studyset() {
      return studyStore.studyset;
    }

    get facts() {
      return studyStore.study;
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

    get inTestMode() {
      return studyStore.inTestMode;
    }

    get num_unstudied() {
      return studyStore.studyset?.unstudied_facts.length ?? 0;
    }

    get num_facts() {
      return studyStore.init_unstudied;
    }

    get current_study_num() {
      return this.num_facts - this.num_unstudied;
    }

    public async mounted() {
      await mainStore.getUserProfile();
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
      this.updateSelectedNum(this.$router.currentRoute.query.num);
      this.setResume(this.$router.currentRoute.query.resume);
      await this.determine_decks(this.$router.currentRoute.query.deck);
      window.addEventListener("keydown", this.handleKeyDown);
      window.addEventListener("keyup", this.resetKeyListener);
    }

    public beforeRouteEnter(to, from, next) {
      next((vm) => {
        vm.editDialog = to.name == "learn-edit" || to.name == "learn-report";
      });
    }

    public async beforeRouteUpdate(to, from, next) {
      if (!to.name.startsWith("learn-") && !from.name.startsWith("learn-")) {
        await this.determine_decks(to.query.deck);
      }
      this.editDialog = to.name == "learn-edit" || to.name == "learn-report";
      if (to.name == "learn") {
        studyStore.startTimer();
      }
      next();
    }

    public async determine_decks(deckIds: string | (string | null)[]) {
      if (deckIds) {
        if (typeof deckIds === "string") {
          studyStore.setDeckIds([Number(deckIds)]);
        } else {
          studyStore.setDeckIds(deckIds.map(Number));
        }
      } else {
        studyStore.setDeckIds([]);
      }
      await studyStore.getNextShow();
    }

    public updateSelectedNum(payload: string | (string | null)[]) {
      if (payload && payload !== undefined) {
        studyStore.updateSelectedNum(payload);
      }
    }

    public setResume(payload: string | (string | null)[]) {
      if (payload && payload !== undefined) {
        if (payload === "1") {
          studyStore.setForceNew(true);
        } else {
          studyStore.setForceNew(false);
        }
      }
    }

    public async destroyed() {
      studyStore.clearTimer();
      studyStore.setShowLoading();
      studyStore.emptySchedule();
      window.removeEventListener("keydown", this.handleKeyDown);
      window.removeEventListener("keyup", this.resetKeyListener);
    }

    public handleKeyDown(e: KeyboardEvent) {
      const key = e.key.toLowerCase();
      if (!this.editDialog && !this.pressed) {
        this.pressed = true;
        if (e.altKey && (e.key == "s" || key == "ß")) {
          this.suspend();
        } else if (e.altKey && (key == "d" || key == "∂")) {
          this.remove();
        } else if (e.altKey && (key == "/" || key == "÷")) {
          this.dialog = !this.dialog;
        } else if (e.altKey && (key == "r" || key == "®")) {
          this.report();
        } else if (e.altKey && (key == "m" || key == "µ")) {
          this.mark();
        } else if (e.altKey && (key == "e" || key == "dead")) {
          this.edit();
        } else if (this.showBack) {
          this.determineResponse(e, key);
        } else if (key == "enter" && this.show.enable_actions) {
          this.showAnswer();
        } else if (
          /^[a-z0-9]$/i.test(key) &&
          !e.altKey &&
          !e.metaKey &&
          !e.shiftKey &&
          !e.ctrlKey
        ) {
          this.$nextTick(() => {
            this.$refs.answerfield.focus();
          });
        }
      }
    }

    public resetKeyListener(_: KeyboardEvent) {
      this.pressed = false;
    }

    public determineResponse(e: KeyboardEvent, key: string) {
      if (key == "enter") {
        this.response(this.recommendation);
      } else if (key == "[") {
        this.response(false);
      } else if (key == "]") {
        this.response(true);
      } else if (
        /^[a-z0-9]$/i.test(key) &&
        !e.altKey &&
        !e.metaKey &&
        !e.shiftKey &&
        !e.ctrlKey
      ) {
        this.$nextTick(() => {
          this.$refs.retype.focus();
        });
      }
    }

    public keyHandler(e: KeyboardEvent) {
      const key = e.key.toLowerCase();
      if (
        (e.altKey &&
          (key == "m" ||
            key == "µ" ||
            key == "d" ||
            key == "∂" ||
            key == "/" ||
            key == "÷" ||
            key == "r" ||
            key == "®" ||
            key == "e" ||
            key == "dead")) ||
        (this.showBack && (key == "[" || key == "]"))
      ) {
        e.preventDefault();
      }
    }
    public async showAnswer() {
      await studyStore.evaluateAnswer(this.typed);
      this.showBack = true;
      this.scrollToResponseButtons();
    }

    public resetCard() {
      this.showBack = false;
      this.typed = "";
      this.retyped = "";
      this.scrollToFront();
    }

    public async suspend() {
      if (!this.inTestMode) {
        await studyStore.suspendFact();
        this.resetCard();
      }
    }

    public async edit() {
      if (!this.inTestMode) {
        await studyStore.editFactDialog();
      }
    }

    public async report() {
      if (!this.inTestMode) {
        await studyStore.reportFactDialog();
        this.resetCard();
      }
    }

    public async remove() {
      if (!this.inTestMode) {
        await studyStore.deleteFact();
        this.resetCard();
      }
    }

    public async mark() {
      if (!this.inTestMode) {
        await studyStore.markFact();
      }
    }

    public async response(response) {
      if (response) {
        mainStore.addNotification({
          content: "Your evaluation: Right",
          color: "success",
        });
      } else {
        mainStore.addNotification({
          content: "Your evaluation: Wrong",
          color: "error",
        });
      }

      if (this.show.fact) {
        studyStore.markBackTime();
        studyStore.addToSchedule({
          fact_id: this.show.fact.fact_id,
          debug_id: this.show.fact.debug_id ?? "unknown id",
          typed: this.typed,
          response: response,
          elapsed_milliseconds_text: this.frontTime,
          elapsed_milliseconds_answer: this.backTime,
          test_mode: this.inTestMode,
        });
        this.resetCard();
        await studyStore.updateSchedule();
        this.resetCard();
      }
    }

    public scrollToResponseButtons() {
      this.$nextTick(function() {
        const container = this.$el.querySelector("#response");
        if (container) {
          container.scrollIntoView();
        }
      });
    }

    public scrollToFront() {
      this.$nextTick(function() {
        window.scrollTo(0, 0);
      });
    }

    returnLearn() {
      this.$router.back();
    }
  }
</script>
