<template>
  <v-container fluid style="max-width:1200px">
    <v-card class="mx-3 my-1 py-1 px-3">
      <v-card-title primary-title class="mx-3 my-0 pa-0">
        <div class="headline primary--text">Learn</div>
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
              <v-icon>mdi-information</v-icon>Debug (Alt-/)
            </v-btn>
          </template>
          <span>Debug (Alt-/)</span>
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
              <v-icon left>mdi-star</v-icon>Favorite (Alt-M)
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
              <v-icon left>mdi-pause</v-icon>Suspend (Alt-S)
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
              <v-icon left>mdi-delete</v-icon>Delete (Alt-D)
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
                <v-icon left>mdi-alert-octagon</v-icon>Report (Alt-R)
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
                <v-icon left>mdi-pencil</v-icon>Edit (Alt-E)
              </v-btn>
            </template>
            <span>Edit (Alt-E)</span>
          </v-tooltip>
        </span>
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
          label="Type Answer (Press any letter to focus)"
          autofocus
          class="hide-details"
        ></v-text-field>
      </v-card-text>
      <v-card-actions v-show="show.enable_actions">
        <v-btn @click="showAnswer">Show Answer (Enter)</v-btn>
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
          label="Retype Answer (Press any letter to focus)"
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
              >wrong ([)</v-btn
            >
          </v-col>
          <v-col class="ma-1 pa-1 shrink">
            <v-btn
              ref="good"
              :color="recommendation ? 'green' : ''"
              @click="response(true)"
              >right (])</v-btn
            >
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>
    <div id="response"></div>
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
  import { Component, Vue } from "vue-property-decorator";
  import { studyStore } from "@/utils/store-accessor";

  @Component
  export default class Learn extends Vue {
    showBack = false;
    typed = "";
    retyped = "";
    dialog = false;
    editDialog = false;

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

    public async mounted() {
      await this.determine_decks(this.$router.currentRoute.query.deck);
      window.addEventListener("keydown", this.handleKeyDown);
    }

    public beforeRouteEnter(to, from, next) {
      next((vm) => {
        vm.editDialog = to.name == "learn-edit";
      });
    }

    public async beforeRouteUpdate(to, from, next) {
      if (to.name != "learn-edit" && from.name != "learn-edit") {
        await this.determine_decks(to.query.deck);
      }
      this.editDialog = to.name == "learn-edit";
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

    public async destroyed() {
      studyStore.setShowLoading();
      studyStore.emptySchedule();
      window.removeEventListener("keydown", this.handleKeyDown);
    }

    public handleKeyDown(e: KeyboardEvent) {
      const key = e.key.toLowerCase();
      if (e.altKey && e.key == "s") {
        this.suspend();
      } else if (e.altKey && key == "d") {
        this.remove();
      } else if (e.altKey && key == "/") {
        this.dialog = !this.dialog;
      } else if (e.altKey && key == "r") {
        this.report();
      } else if (e.altKey && key == "m") {
        this.mark();
      } else if (e.altKey && key == "e") {
        this.edit();
      } else if (this.showBack) {
        this.determineResponse(e, key);
      } else if (key == "enter") {
        this.showAnswer();
      } else if (
        /^[a-z0-9]$/i.test(key) &&
        !e.altKey &&
        !e.metaKey &&
        !e.shiftKey &&
        !e.ctrlKey
      ) {
        //this.$ref.typed.$el.focus() doesn't work some reason
        document.getElementById("answer")!.focus(); // eslint-disable-line
      }
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
        document.getElementById("retype_answer")!.focus(); //eslint-disable-line
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
    }

    public async suspend() {
      await studyStore.suspendFact();
      this.resetCard();
    }

    public async edit() {
      await studyStore.editFactDialog();
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
        this.resetCard();
      }
    }

    public scrollToResponseButtons() {
      const container = this.$el.querySelector("#response");
      if (container) {
        container.scrollIntoView();
      }
    }

    returnLearn() {
      this.$router.back();
    }
  }
</script>
