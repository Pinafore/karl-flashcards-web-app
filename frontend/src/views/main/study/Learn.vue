<template>
  <v-container fluid style="max-width:1250px">
    <onboard></onboard>
    <mnemonic-onboard :should-show="shouldShowMnemonicTips"></mnemonic-onboard>
    <connection-popup></connection-popup>
    <test-popup :should-show="shouldShowTestPopup"></test-popup>
    <!-- <RecallPopup></RecallPopup> -->
    <study-set></study-set>
    <v-card class="mx-3 my-1 py-1 px-0 px-sm-3">
      <v-card-title primary-title class="mx-3 my-0 pa-0">
        <div v-if="inTestMode" class="headline primary--text">Test Mode</div>
        <div
          v-else-if="$vuetify.breakpoint.xsOnly || studyset === null"
          class="headline primary--text"
        >
          Learn
        </div>
        <div v-else class="headline primary--text">
          {{ studyset.short_description }}
        </div>
        <div
          v-show="show.text !== 'Loading...'"
          class="headline primary--text"
          style="margin-left: .5em"
        >
          ({{ current_study_num }} of {{ num_facts }})
        </div>
        <v-spacer></v-spacer>
        <span v-show="False">
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
                <v-btn
                  v-else
                  class="ma-1 pa-2"
                  v-bind="attrs"
                  @click="edit()"
                  v-on="on"
                >
                  <v-icon left>mdi-pencil</v-icon>Edit: Alt-E
                </v-btn>
              </template>
              <span>Edit (Alt-E)</span>
            </v-tooltip>
          </span>
        </span>
      </v-card-title>
    </v-card>
    <v-card v-show="!mnemonicData.isStudyingMnemonic" class="my-2 mx-3 px-3 py-4 pb-5">
      <v-card-title class="py-0">
        <v-row no-gutters>
          <v-col cols="12" sm="auto">
            <div
              v-if="
                show.enable_show_back &&
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
              v-show="show.enable_show_back && show.fact && show.fact.identifier"
              class="title"
            >
              <span class="hidden-xs-only">—</span>

              <span v-if="!mnemonicData.cardHasMnemonic" class="hidden-xs-only"
                >Identify {{ show.fact && show.fact.identifier }}</span
              >
              <span v-else class="hidden-xs-only">What's the definition?</span>
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
      <v-card-text v-show="show.enable_show_back" class="py-2">
        <v-text-field
          id="answer"
          ref="answerfield"
          v-model="typed"
          solo
          autofocus
          hide-details="auto"
          @keydown="keyHandler"
          ><template v-slot:label>
            <span v-if="inTestMode">Required (Test Mode) - </span>
            <span v-else>Recommended - </span>
            Type Answer (Press any letter to focus)
          </template>
        </v-text-field>
      </v-card-text>
      <v-card-actions
        v-show="show.enable_show_back && !showBack"
        class="px-5 pt-3 pb-2"
      >
        <v-row class="shrink" justify="start">
          <v-col cols="12" md="5" class="ma-1 pa-1 py-0 pr-10">
            <v-btn @click="showAnswer">Show Answer (Enter)</v-btn>
          </v-col>
          <v-col cols="12" md="5" class="ma-1 pa-1 py-0">
            <v-btn @click="dontKnow">Don't Know (Shift-Enter)</v-btn>
          </v-col>
        </v-row>
      </v-card-actions>
    </v-card>

    <v-dialog v-model="mnemonicData.mnemonicDialogue" scrollable>
      <v-card>
        <v-card-title>
          <h2 class="headline">What makes a mnemonic good?</h2>
        </v-card-title>
        <v-card-text class="title">
          Determining what makes a mnemonic good is a highly subjective process. Below,
          we define some criteria and examples that can be considered to help you rate
          the quality of mnemonics:
          <ol>
            <li>
              <b>Correctness:</b> A good mnemonic should accurately capture the
              definition of the vocabulary term
            </li>
            <li>
              <b>Clarity:</b> A good mnemonic should be easy to understand and free of
              mistakes in grammar, spelling, etc.
            </li>
            <li>
              <b>Memorability:</b> A good mnemonic should be easy to remember and link
              to familiar concepts
            </li>
            <li>
              <b>Keyword Quality:</b> A good mnemonic should link to keywords that sound
              like the original term, and ideally should not be circular (e.g. the
              keyword "memory" for "memorable" is circular)
            </li>
            <li>
              <b>Keyword Explanation:</b> A good mnemonic should have a reasonable
              explanation for how the keyword and original vocab term are related
            </li>
            <li>
              <b>Offensiveness:</b> A good mnemonic should not discuss inappropriate
              themes, biases, etc.
            </li>
          </ol>
          <br />
          <v-img
            width="100%"
            :src="require('@/assets/mnemonic-examples-wide.svg')"
          ></v-img>
        </v-card-text>
        <v-card-actions>
          <v-btn @click="mnemonicData.mnemonicDialogue = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <div
      v-show="mnemonicData.isStudyingMnemonic && mnemonicData.cardHasMnemonic"
      class="my-2 mx-3 px-3 py-4"
    >
      <v-expansion-panels
        v-model="mnemonicData.panelOpen"
        :readonly="mnemonicData.response"
        :disabled="false"
        :flat="true"
        :tile="true"
      >
        <v-expansion-panel @click="updateMnemonicClick()">
          <v-expansion-panel-header
            color="#e0f0ff"
            class="d-flex align-center justify-start py-1"
          >
            <div class="d-flex align-center justify-start title">
              <b
                v-if="mnemonicData.response && !mnemonicData.isInteractiveMnemonic"
                class="mr-2"
                >KAR³L-generated Mnemonic Devices</b
              >
              <b v-else-if="mnemonicData.isInteractiveMnemonic" class="mr-2"
                >Mnemonic Device</b
              >
              <b v-else class="mr-2">KAR³L-generated Mnemonic Device</b>
              <v-tooltip right>
                <template v-slot:activator="{ on, attrs }">
                  <v-icon
                    icon
                    v-bind="attrs"
                    @click.stop="mnemonicData.mnemonicDialogue = true"
                    v-on="on"
                    >mdi-help-circle</v-icon
                  >
                </template>
                <span>What makes a mnemonic good?</span>
              </v-tooltip>
            </div>
            <div ref="mnemonicPaneTop"></div>
          </v-expansion-panel-header>

          <v-expansion-panel-content v-if="mnemonicData.response" color="#e0f0ff">
            <v-container>
              <p class="title">
                Which mnemonic do you think would help you learn better?
              </p>
              <v-row>
                <v-col cols="6" class="d-flex">
                  <v-card
                    class="flex"
                    :style="
                      mnemonicData.hoverA
                        ? { backgroundColor: '#e0e0e0', cursor: 'pointer' }
                        : {}
                    "
                    @mouseover="mnemonicData.hoverA = true"
                    @mouseleave="mnemonicData.hoverA = false"
                    @click="submitComparisonFeedback('a_better')"
                  >
                    <v-card-title class="title">
                      Mnemonic A ([)
                    </v-card-title>
                    <v-card-text class="body-1" style="color: black">
                      {{
                        show.fact &&
                          show.fact.extra &&
                          show.fact.extra[
                            "mnemonic_" + mnemonicData.mnemonicComparisons[0]
                          ]
                      }}
                    </v-card-text>
                  </v-card>
                </v-col>

                <v-col cols="6" class="d-flex">
                  <v-card
                    class="flex"
                    :style="
                      mnemonicData.hoverB
                        ? { backgroundColor: '#e0e0e0', cursor: 'pointer' }
                        : {}
                    "
                    @mouseover="mnemonicData.hoverB = true"
                    @mouseleave="mnemonicData.hoverB = false"
                    @click="submitComparisonFeedback('b_better')"
                  >
                    <v-card-title class="title">
                      Mnemonic B (])
                    </v-card-title>
                    <v-card-text class="body-1" style="color: black">
                      {{
                        show.fact &&
                          show.fact.extra &&
                          show.fact.extra[
                            "mnemonic_" + mnemonicData.mnemonicComparisons[1]
                          ]
                      }}
                    </v-card-text>
                  </v-card>
                </v-col>

                <v-col class="rows">
                  <v-card-actions class="px-0 pt-3 pb-2 mx-0">
                    <v-row class="shrink" justify="center">
                      <v-col cols="12" md="5" class="ma-1 pa-1 pl-2 py-0">
                        <v-btn medium @click="submitComparisonFeedback('equal')"
                          >Equal (Shift-Enter)</v-btn
                        ></v-col
                      >
                    </v-row>
                  </v-card-actions>
                </v-col>
              </v-row>
            </v-container>
          </v-expansion-panel-content>

          <v-expansion-panel-content v-else color="#e0f0ff">
            <div style="min-height: 120px;">
              <p class="title pb-0">
                <span
                  v-if="
                    mnemonicData.isGeneratingMnemonic &&
                      mnemonicData.isInteractiveMnemonic
                  "
                >
                  {{ mnemonicData.mnemonicDisplayText }}
                </span>
                <span
                  v-else-if="
                    mnemonicData.isInteractiveMnemonic && !mnemonicData.isBuildingMnemonic
                  "
                >
                  {{ mnemonicData.mnemonicDisplayText }}
                </span>
                <span
                  v-else-if="
                    mnemonicData.isInteractiveMnemonic && mnemonicData.isBuildingMnemonic
                  "
                >
                  {{ mnemonicData.mnemonicDisplayText }}
                </span>
                <span v-else>
                  {{
                    show.fact &&
                      show.fact.extra &&
                      show.fact.extra[
                        show.fact.deck.deck_type == "sanity_check"
                          ? "mnemonic_1"
                          : mnemonicData.mnemonicGroup
                      ]
                  }}
                </span>
              </p>
            </div>

            <!-- Selection Interfaces Container -->
            <div style="min-height: 400px;">
              <!-- Keyword Selection Interface -->
              <v-container
                v-if="
                  mnemonicData.showKeywordSelection && mnemonicData.currentMnemonicData
                "
                class="pl-0 pb-0"
              >
                <v-subheader class="title pl-0 ml-0">Choose a keyword:</v-subheader>
                <v-row>
                  <v-col
                    v-for="(keyword, index) in mnemonicData.currentMnemonicData.keywords"
                    :key="index"
                    cols="12"
                    class="pa-1"
                  >
                    <v-btn
                      block
                      outlined
                      :style="{
                        backgroundColor:
                          mnemonicData.selectedKeywordIndex === index ? '#e3f2fd' : '',
                        borderColor:
                          mnemonicData.selectedKeywordIndex === index ? '#1976d2' : '',
                      }"
                      @click="selectKeyword(index)"
                    >
                      {{ keyword }}
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>

              <!-- Explanation Selection Interface -->
              <v-container
                v-if="
                  mnemonicData.showExplanationSelection &&
                    mnemonicData.currentMnemonicData
                "
                class="pl-0 pb-0"
              >
                <v-subheader class="title pl-0 ml-0">Choose an explanation:</v-subheader>
                <v-row>
                  <v-col
                    v-for="(explanation, index) in mnemonicData.currentMnemonicData
                      .explanations[mnemonicData.selectedKeywordIndex]"
                    :key="index"
                    cols="12"
                    class="pa-1"
                  >
                    <v-btn
                      block
                      outlined
                      :style="{
                        backgroundColor:
                          mnemonicData.selectedExplanationIndex === index
                            ? '#e3f2fd'
                            : '',
                        borderColor:
                          mnemonicData.selectedExplanationIndex === index
                            ? '#1976d2'
                            : '',
                      }"
                      @click="selectExplanation(index)"
                    >
                      {{ explanation }}
                    </v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </div>
            <v-container v-if="show.fact && !hasSubmittedFeedback()" class="pl-0 pb-0">
              <v-subheader class="title pl-0 ml-0">
                {{
                  mnemonicData.isInteractiveMnemonic
                    ? "Rate this mnemonic"
                    : "Give Feedback (Optional)"
                }}
                <v-tooltip v-if="!mnemonicData.isInteractiveMnemonic" right>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                      >mdi-information</v-icon
                    >
                  </template>
                  <span>Type 1-5 to rate the mnemonic</span>
                </v-tooltip>
                <v-tooltip v-else right>
                  <template v-slot:activator="{ on, attrs }">
                    <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                      >mdi-information</v-icon
                    >
                  </template>
                  <span>Required: Rate from 1 (poor) to 5 (excellent)</span>
                </v-tooltip>
              </v-subheader>

              <v-rating
                v-model="mnemonicData.mnemonicRating"
                hover
                :length="5"
                :size="30"
                :model-value="5"
                active-color="black"
                class="pb-5"
                @click.native="handleMnemonicRatingClick"
              />
              <v-subheader
                v-show="
                  (mnemonicData.mnemonicRating === 1 ||
                    mnemonicData.mnemonicRating === 2) &&
                    !mnemonicData.isInteractiveMnemonic
                "
                class="pl-0 pt-0 title"
                >Why is this mnemonic bad? (Optional)</v-subheader
              >
              <v-container
                v-show="
                  (mnemonicData.mnemonicRating === 1 ||
                    mnemonicData.mnemonicRating === 2) &&
                    !mnemonicData.isInteractiveMnemonic
                "
                fluid
                class="pa-0"
              >
                <v-row>
                  <v-col>
                    <v-checkbox
                      v-model="mnemonicData.isIncorrectDefinition"
                      class="shrink mb-2 mt-2"
                      density="compact"
                      hide-details
                    >
                      <template v-slot:label>
                        <span>Incorrect Definition</span>
                        <v-tooltip right>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                              >mdi-information</v-icon
                            >
                          </template>
                          <span
                            >The definition in the mnemonic is not the definition of the
                            vocab term</span
                          >
                        </v-tooltip>
                      </template>
                    </v-checkbox>
                    <v-checkbox
                      v-model="mnemonicData.isDifficultToUnderstand"
                      class="shrink my-2"
                      density="compact"
                      hide-details
                    >
                      <template v-slot:label>
                        <span>Difficult to Understand</span>
                        <v-tooltip right>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                              >mdi-information</v-icon
                            >
                          </template>
                          <span
                            >The mnemonic is difficult to understand through grammar,
                            word choice, etc.</span
                          >
                        </v-tooltip>
                      </template>
                    </v-checkbox>
                    <v-checkbox
                      v-model="mnemonicData.isNotMemorable"
                      class="shrink mb-2 mt-2"
                      density="compact"
                      hide-details
                    >
                      <template v-slot:label>
                        <span>Not Memorable</span>
                        <v-tooltip right>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                              >mdi-information</v-icon
                            >
                          </template>
                          <span
                            >The mnemonic is hard to remember, links to unfamiliar
                            concepts, etc.</span
                          >
                        </v-tooltip>
                      </template>
                    </v-checkbox>
                    <v-checkbox
                      v-model="mnemonicData.isBadPhoneticKeyword"
                      class="shrink my-2"
                      density="compact"
                      hide-details
                    >
                      <template v-slot:label>
                        <span>Bad Phonetic Keyword</span>
                        <v-tooltip right>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                              >mdi-information</v-icon
                            >
                          </template>
                          <span
                            >The generated keyword does not sound like the original
                            vocab term</span
                          >
                        </v-tooltip>
                      </template>
                    </v-checkbox>
                    <v-checkbox
                      v-model="mnemonicData.isBadCircularKeyword"
                      class="shrink my-2"
                      density="compact"
                      hide-details
                    >
                      <template v-slot:label>
                        <span>Bad Circular Keyword</span>
                        <v-tooltip right>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                              >mdi-information</v-icon
                            >
                          </template>
                          <span
                            >The generated keyword is the same as or too similar to the
                            original vocab term</span
                          >
                        </v-tooltip>
                      </template>
                    </v-checkbox>
                    <v-checkbox
                      v-model="mnemonicData.isBadKeywordExplanation"
                      class="shrink my-2"
                      density="compact"
                      hide-details
                    >
                      <template v-slot:label>
                        <span>Bad Keyword Explanation</span>
                        <v-tooltip right>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                              >mdi-information</v-icon
                            >
                          </template>
                          <span
                            >The explanation linking the keyword and vocab term is
                            poor</span
                          >
                        </v-tooltip>
                      </template>
                    </v-checkbox>
                    <v-checkbox
                      v-model="mnemonicData.isOffensive"
                      class="shrink my-2"
                      density="compact"
                      hide-details
                    >
                      <template v-slot:label>
                        <span>Offensive</span>
                        <v-tooltip right>
                          <template v-slot:activator="{ on, attrs }">
                            <v-icon small class="ml-2" v-bind="attrs" v-on="on"
                              >mdi-information</v-icon
                            >
                          </template>
                          <span>The mnemonic device is offensive or harmful</span>
                        </v-tooltip>
                      </template>
                    </v-checkbox>

                    <v-text-field
                      v-model="mnemonicData.otherReason"
                      label="Other Feedback"
                    ></v-text-field>
                    <v-btn medium @click="submitFeedbackIndividualFeedback()">{{
                      mnemonicData.isInteractiveMnemonic
                        ? "Submit Rating (Required)"
                        : "Submit (])"
                    }}</v-btn>
                  </v-col>
                </v-row>
              </v-container>
            </v-container>
            <v-container v-else class="pl-0 pt-2">
              <p class="primary--text">
                <i v-if="!mnemonicData.isInteractiveMnemonic">
                  Thank you for submitting feedback! Edit feedback
                  <a @click="removeSubmittedFeedback"><u>here</u></a
                  >.
                </i>
                <i v-else>
                  Thank you for rating this mnemonic! Edit rating
                  <a @click="removeSubmittedFeedback"><u>here</u></a
                  >.
                </i>
              </p>
            </v-container>
          </v-expansion-panel-content>
        </v-expansion-panel>
      </v-expansion-panels>
    </div>

    <v-card
      v-show="
        showBack &&
          show.enable_show_back &&
          !(mnemonicData.isStudyingMnemonic && mnemonicData.response)
      "
      class="my-2 mx-3 px-3 py-4"
    >
      <v-card-title v-if="mnemonicData.cardHasMnemonic" class="py-0">
        <span>Answer for
            <b>{{ show.text }}</b>
          </span
        >
      </v-card-title>
      <v-card-title v-else class="py-0">Answer</v-card-title>
      <v-card-text class="pb-0 pt-1">
        <div v-if="!mnemonicData.cardHasMnemonic" class="title primary--text">
          {{ show.fact && show.fact.answer }}
        </div>
        <div v-else class="title primary--text" style="white-space: pre-line;">
          {{ show.fact && show.fact.answer }}
        </div>
        <div v-show="mnemonicData.cardHasMnemonic && !mnemonicData.isStudyingMnemonic">
          <br />
        </div>
        <span v-show="showResponseBtns && !mnemonicData.isStudyingMnemonic">
          <div class="title">You typed: '{{ typed }}'</div>
          <div
            v-if="recommendation"
            class="title primary--text py-2"
            :style="{ color: 'green !important' }"
          >
            KAR³L Believes Your Response Was Correct
            <span class="hidden-xs-only">(Enter to Accept, Or Override Below)</span>
          </div>
          <div
            v-else-if="!mnemonicData.cardHasMnemonic"
            class="title primary--text"
            :style="{ color: 'red !important' }"
          >
            KAR³L Believes Your Response Was Wrong
            <span class="hidden-xs-only">(Enter to Accept, Or Override Below)</span>
          </div>
        </span>
      </v-card-text>
      <v-card-text v-show="show.enable_show_back" class="py-2">
        <v-text-field
          v-if="!mnemonicData.cardHasMnemonic"
          id="retype_answer"
          ref="retype"
          v-model="retyped"
          solo
          label="Optional - Retype Answer (Press any letter to focus)"
          autofocus
          hide-details="auto"
        ></v-text-field>
        <v-text-field
          v-if="mnemonicData.cardHasMnemonic && mnemonicData.isStudyingMnemonic"
          id="retype_answer"
          ref="retype_mnemonic"
          v-model="mnemonicData.retypedMnemonic"
          solo
          label="Optional - Retype Answer"
          hide-details="auto"
        ></v-text-field>
      </v-card-text>
      <v-card-actions class="pt-3 pb-1 px-5">
        <v-row class="shrink" justify="start">
          <v-col
            v-show="showResponseBtns && !mnemonicData.isStudyingMnemonic"
            cols="5"
            sm="auto"
            class="ma-1 pa-1 py-0 shrink"
          >
            <v-btn
              ref="wrong"
              :color="!recommendation && !mnemonicData.cardHasMnemonic ? 'red' : ''"
              class="px-2"
              @click="
                mnemonicData.cardHasMnemonic ? mnemonicResponse(false) : response(false)
              "
              >wrong ([)</v-btn
            >
          </v-col>
          <v-col
            v-show="showResponseBtns && !mnemonicData.isStudyingMnemonic"
            id="response"
            cols="5"
            sm="auto"
            class="ma-1 pa-1 py-0 shrink"
          >
            <v-btn
              ref="right"
              :color="recommendation ? 'green' : ''"
              class="px-2"
              @click="
                mnemonicData.cardHasMnemonic ? mnemonicResponse(true) : response(true)
              "
              >right (])</v-btn
            >
          </v-col>
          <v-col
            v-show="!showResponseBtns || mnemonicData.isStudyingMnemonic"
            cols="5"
            sm="auto"
            class="ma-1 pa-1 py-0 shrink"
          >
            <v-btn
              ref="continue"
              class="px-2"
              :disabled="
                mnemonicData.cardHasMnemonic &&
                  mnemonicData.isStudyingMnemonic &&
                  !hasSubmittedFeedback()
              "
              @click="response(mnemonicData.response)"
              >continue (Enter)</v-btn
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
  import { Component, Vue } from "vue-property-decorator";
  import { studyStore, mainStore } from "@/utils/store-accessor";
  import Onboard from "@/views/Onboard.vue";
  import MnemonicOnboard from "@/views/MnemonicOnboard.vue";
  import ConnectionPopup from "@/views/ConnectionPopup.vue";
  import RecallPopup from "@/views/main/RecallPopup.vue";
  import TestPopup from "@/views/main/TestPopup.vue";
  import StudySet from "@/views/main/StudySet.vue";

  @Component({
    components: {
      TestPopup,
      ConnectionPopup,
      Onboard,
      MnemonicOnboard,
      RecallPopup,
      StudySet,
    },
  })
  export default class Learn extends Vue {
    $refs!: {
      answerfield: HTMLInputElement;
      retype: HTMLInputElement;
      retype_mnemonic: HTMLInputElement;
      right: HTMLButtonElement;
      wrong: HTMLButtonElement;
      mnemonicPaneTop: HTMLInputElement;
    };
    showBack = false;
    typed = "";
    retyped = "";
    dialog = false;
    editDialog = false;
    pressed = false;
    showResponseBtns = true;
    mnemonicData = {
      mnemonicDialogue: false,
      mnemonicGroup: "",
      retypedMnemonic: "",
      mnemonicClick: false,
      cardHasMnemonic: false,
      isInteractiveMnemonic: false,
      isStudyingMnemonic: false,
      isIncorrectDefinition: false,
      isNotMemorable: false,
      isDifficultToUnderstand: false,
      isBadKeywordLink: false,
      isBadPhoneticKeyword: false,
      isBadCircularKeyword: false,
      isBadKeywordExplanation: false,
      isOffensive: false,
      isOther: false,
      otherReason: "",
      mnemonicRating: 0,
      response: null,
      panelOpen: -1,
      comparisonChoice: "",
      feedbackFactIdsLearning: new Set(),
      feedbackFactIdsComparison: new Set(),
      mnemonicComparisons: ["", ""],
      hoverA: false,
      hoverB: false,
      mnemonicDisplayText: "",
      mnemonicFullText: "",
      isGeneratingMnemonic: false,
      generationSpeed: 25, // milliseconds per character for streaming effect
      // Interactive mnemonic builder properties
      isBuildingMnemonic: false,
      currentMnemonicData: null,
      buildStep: "pre_keyword", // pre_keyword, keyword_selection, pre_explanation, explanation_selection, definition
      selectedKeywordIndex: -1,
      selectedExplanationIndex: -1,
      showKeywordSelection: false,
      showExplanationSelection: false,
    };

    fromQuickStudy = true;

    get studyset() {
      return studyStore.studyset;
    }

    get deckIds() {
      return studyStore.deckIds;
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

    get is_resume() {
      if (window) {
        const currentUrl = window.location.href;
        const url = new URL(currentUrl);
        const urlParams = new URLSearchParams(url.search);
        return urlParams.get("resume") === "true";
      }
      return false;
    }

    get shouldShowTestPopup() {
      if (process.env.VUE_APP_TEST_MODE_ENABLED == "0") {
        return false;
      }
      if (studyStore.isContinuedSet) {
        return true;
      }
      if (window) {
        const currentUrl = window.location.href;
        const url = new URL(currentUrl);
        const urlParams = new URLSearchParams(url.search);
        return (
          urlParams.get("show_test_mode") === "true" ||
          urlParams.get("resume") === "true"
        );
      }
      return false;
    }

    get shouldShowMnemonicTips() {
      if (window) {
        return this.mnemonicData.cardHasMnemonic;
      }
      return false;
    }

    public checkIfMnemonicDeck(facts) {
      return facts.some(
        (fact) =>
          fact !== undefined &&
          (fact.deck.deck_type == "public_mnemonic" ||
            fact.deck.deck_type == "interactive_mnemonic"),
      );
    }

    public isCurrentFactInteractiveMnemonic(): boolean {
      return !!(
        this.show.fact && this.show.fact.deck.deck_type == "interactive_mnemonic"
      );
    }

    public async generateMnemonicCharacterByCharacter() {
      if (this.mnemonicData.isGeneratingMnemonic) {
        return; // Already generating
      }

      this.mnemonicData.isGeneratingMnemonic = true;
      this.mnemonicData.mnemonicDisplayText = "";

      const text = this.mnemonicData.mnemonicFullText;

      for (let i = 0; i < text.length; i++) {
        this.mnemonicData.mnemonicDisplayText += text[i];

        // Add a small delay between characters for streaming effect
        await new Promise((resolve) =>
          setTimeout(resolve, this.mnemonicData.generationSpeed),
        );
      }

      this.mnemonicData.isGeneratingMnemonic = false;
    }

    public async startInteractiveMnemonicBuilding() {
      if (
        !this.show.fact ||
        !this.show.fact.extra ||
        !this.show.fact.extra["interactive_mnemonic_data"]
      ) {
        return;
      }

      this.mnemonicData.isBuildingMnemonic = true;
      this.mnemonicData.currentMnemonicData = this.show.fact.extra[
        "interactive_mnemonic_data"
      ];
      this.mnemonicData.buildStep = "pre_keyword";
      this.mnemonicData.mnemonicDisplayText = "";
      this.mnemonicData.showKeywordSelection = false;
      this.mnemonicData.showExplanationSelection = false;
      this.mnemonicData.selectedKeywordIndex = -1;
      this.mnemonicData.selectedExplanationIndex = -1;

      // Start with pre_keyword generation
      await this.generatePreKeyword();
    }

    public async generatePreKeyword() {
      if (!this.mnemonicData.currentMnemonicData) return;

      this.mnemonicData.isGeneratingMnemonic = true;
      this.mnemonicData.mnemonicDisplayText = "";
      const preKeyword = this.mnemonicData.currentMnemonicData!["pre_keyword"] as string;

      if (!preKeyword) return;

      for (let i = 0; i < preKeyword.length; i++) {
        this.mnemonicData.mnemonicDisplayText += preKeyword[i];
        await new Promise((resolve) =>
          setTimeout(resolve, this.mnemonicData.generationSpeed),
        );
      }

      this.mnemonicData.isGeneratingMnemonic = false;
      this.mnemonicData.showKeywordSelection = true;
    }

    public async selectKeyword(keywordIndex: number) {
      this.mnemonicData.selectedKeywordIndex = keywordIndex;
      this.mnemonicData.showKeywordSelection = false;

      // Continue building the mnemonic with the selected keyword
      await this.generateWithSelectedKeyword();
    }

    public async generateWithSelectedKeyword() {
      if (
        !this.mnemonicData.currentMnemonicData ||
        this.mnemonicData.selectedKeywordIndex === -1
      )
        return;

      this.mnemonicData.isGeneratingMnemonic = true;
      const keywords = this.mnemonicData.currentMnemonicData!["keywords"] as string[];
      const preExplanation = this.mnemonicData.currentMnemonicData!["pre_explanation"] as string;
      
      if (!keywords || !preExplanation) return;
      
      const selectedKeyword = keywords[this.mnemonicData.selectedKeywordIndex];
      
      if (!selectedKeyword) return;

      // Add the selected keyword to the display with streaming effect
      for (let i = 0; i < selectedKeyword.length; i++) {
        this.mnemonicData.mnemonicDisplayText += selectedKeyword[i];
        await new Promise((resolve) =>
          setTimeout(resolve, this.mnemonicData.generationSpeed),
        );
      }
      this.mnemonicData.mnemonicDisplayText += " ";

      // Generate pre_explanation
      for (let i = 0; i < preExplanation.length; i++) {
        this.mnemonicData.mnemonicDisplayText += preExplanation[i];
        await new Promise((resolve) =>
          setTimeout(resolve, this.mnemonicData.generationSpeed),
        );
      }

      this.mnemonicData.isGeneratingMnemonic = false;
      this.mnemonicData.showExplanationSelection = true;
    }

    public async selectExplanation(explanationIndex: number) {
      this.mnemonicData.selectedExplanationIndex = explanationIndex;
      this.mnemonicData.showExplanationSelection = false;

      // Show the final definition
      await this.generateFinalDefinition();
    }

    public async generateFinalDefinition() {
      if (
        !this.mnemonicData.currentMnemonicData ||
        this.mnemonicData.selectedKeywordIndex === -1 ||
        this.mnemonicData.selectedExplanationIndex === -1
      )
        return;

      this.mnemonicData.isGeneratingMnemonic = true;

      // Get the selected explanation and definition
      const explanations = this.mnemonicData.currentMnemonicData!["explanations"] as string[][];
      const definitions = this.mnemonicData.currentMnemonicData!["definitions"] as string[][];
      
      if (!explanations || !definitions) return;
      
      const selectedExplanation = explanations[
        this.mnemonicData.selectedKeywordIndex
      ]?.[this.mnemonicData.selectedExplanationIndex];
      const selectedDefinition = definitions[
        this.mnemonicData.selectedKeywordIndex
      ]?.[this.mnemonicData.selectedExplanationIndex];

      if (!selectedExplanation || !selectedDefinition) return;

      // Add explanation with streaming effect
      for (let i = 0; i < selectedExplanation.length; i++) {
        this.mnemonicData.mnemonicDisplayText += selectedExplanation[i];
        await new Promise((resolve) =>
          setTimeout(resolve, this.mnemonicData.generationSpeed),
        );
      }
      this.mnemonicData.mnemonicDisplayText += ". ";

      // Build the final mnemonic from user's selections instead of using static definition
      // The final mnemonic should end with the answer/fact being memorized
      const factAnswer = this.show.fact?.answer || "";
      const finalMnemonicText = `Thus, ${factAnswer}`;
      
      // Add the final conclusion character by character for streaming effect
      for (let i = 0; i < finalMnemonicText.length; i++) {
        this.mnemonicData.mnemonicDisplayText += finalMnemonicText[i];
        await new Promise((resolve) =>
          setTimeout(resolve, this.mnemonicData.generationSpeed),
        );
      }

      this.mnemonicData.isGeneratingMnemonic = false;
      this.mnemonicData.isBuildingMnemonic = false;
    }

    public async mounted() {
      studyStore.setStudySet(null);
      await mainStore.getUserProfile();
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
      this.updateSelectedNum(this.$router.currentRoute.query.num);
      await this.determine_decks(this.$router.currentRoute.query.deck);
      window.addEventListener("keydown", this.handleKeyDown);
      window.addEventListener("keyup", this.resetKeyListener);
      studyStore.setResume(this.is_resume);
      await studyStore.getStudyFacts();
      this.mnemonicData.cardHasMnemonic = this.checkIfMnemonicDeck(this.facts);
      this.mnemonicData.isInteractiveMnemonic = this.isCurrentFactInteractiveMnemonic();
      if (this.mnemonicData.cardHasMnemonic) {
        await this.setupMnemonicData();
        // Auto-open panel for interactive mnemonic mode
        if (this.mnemonicData.isInteractiveMnemonic) {
          this.mnemonicData.panelOpen = 0;
          // Start interactive mnemonic building if interactive data is available
          if (
            this.show.fact &&
            this.show.fact.extra &&
            this.show.fact.extra["interactive_mnemonic_data"]
          ) {
            this.startInteractiveMnemonicBuilding();
          } else if (
            this.show.fact &&
            this.show.fact.extra &&
            this.show.fact.extra["mnemonic"]
          ) {
            // Fallback to simple streaming if no interactive data
            this.mnemonicData.mnemonicFullText = this.show.fact.extra["mnemonic"];
            this.generateMnemonicCharacterByCharacter();
          }
        }
      }
      studyStore.setResume(false);
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
        const user_decks = mainStore.userProfile?.decks;
        if (user_decks) {
          let decks = user_decks
            .filter((deck) => deck.deck_type != "public_mnemonic" && deck.id != 1)
            .map((deck) => deck.id);
          if (decks.length == 0) {
            decks = user_decks.filter((deck) => deck.id != 1).map((deck) => deck.id);
          }
          studyStore.setDeckIds(decks);
        }
      }
    }

    public updateSelectedNum(payload: string | (string | null)[]) {
      if (payload && payload !== undefined) {
        studyStore.updateSelectedNum(payload);
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
        } else if (e.shiftKey && key == "enter" && this.show.enable_show_back) {
          this.dontKnow();
        } else if (key == "enter" && this.show.enable_show_back) {
          this.showAnswer();
        } else if (
          /^[a-z0-9]$/i.test(key) &&
          !e.altKey &&
          !e.metaKey &&
          !e.shiftKey &&
          !e.ctrlKey
        ) {
          this.$nextTick(() => {
            if (this.$refs.answerfield) {
              this.$refs.answerfield.focus();
            } else {
              console.error("answerfield is not rendered yet");
            }
          });
        }
      }
    }

    public resetKeyListener(_: KeyboardEvent) {
      this.pressed = false;
    }

    public determineResponse(e: KeyboardEvent, key: string) {
      if (key == "enter" && !e.shiftKey) {
        // this.showResponseBtns ensures that response is never true when user doesn't know
        // !this.mnemonicData.isStudyingMnemonic ensures that response is never true when the user is studying the mnemonic (only studies the mnemonic when wrong)
        if (
          this.mnemonicData.cardHasMnemonic &&
          !this.mnemonicData.isStudyingMnemonic
        ) {
          this.mnemonicResponse(this.recommendation && this.showResponseBtns);
        } else if (
          this.mnemonicData.cardHasMnemonic &&
          this.mnemonicData.isStudyingMnemonic
        ) {
          if (this.mnemonicData.response) {
            // No skip option - user must choose between mnemonic A or B
            mainStore.addNotification({
              content: "Please choose between Mnemonic A ([) or Mnemonic B (])",
              color: "error",
            });
          } else {
            // Check if user needs to complete rating before continuing
            if (
              this.mnemonicData.isInteractiveMnemonic &&
              !this.hasSubmittedFeedback()
            ) {
              mainStore.addNotification({
                content: "You must rate the mnemonic before continuing!",
                color: "error",
              });
            } else {
              this.response(this.mnemonicData.response && this.showResponseBtns);
            }
          }
        } else {
          this.response(
            this.recommendation &&
              this.showResponseBtns &&
              !this.mnemonicData.isStudyingMnemonic,
          );
        }
      } else if (key == "[") {
        // when the card has a mnemonic and the user has just entered their answer => show the mnemonic
        if (
          this.mnemonicData.cardHasMnemonic &&
          !this.mnemonicData.isStudyingMnemonic
        ) {
          this.mnemonicResponse(false);
        }
        // when the card has a mnemonic and the user already sees the mnemonic => log the response as normal
        else if (
          this.mnemonicData.cardHasMnemonic &&
          this.mnemonicData.isStudyingMnemonic
        ) {
          if (this.mnemonicData.response) {
            this.submitComparisonFeedback("a_better");
          }
        }
        // previous response logging logic
        else if (!this.mnemonicData.cardHasMnemonic && this.showResponseBtns) {
          this.response(false);
        }
      } else if (key == "]") {
        // when the card has a mnemonic and the user has just entered their answer => show the mnemonic
        if (
          this.mnemonicData.cardHasMnemonic &&
          !this.mnemonicData.isStudyingMnemonic
        ) {
          this.mnemonicResponse(true);
        }
        // when the card has a mnemonic and the user already sees the mnemonic => log the response as normal
        else if (
          this.mnemonicData.cardHasMnemonic &&
          this.mnemonicData.isStudyingMnemonic
        ) {
          if (this.mnemonicData.response) {
            this.submitComparisonFeedback("b_better");
          } else if ([1, 2].includes(this.mnemonicData.mnemonicRating)) {
            this.submitFeedbackIndividualFeedback();
          }
        }
        // previous response logging logic
        else if (!this.mnemonicData.cardHasMnemonic && this.showResponseBtns) {
          this.response(true);
        }
      }
      // toggle the mnemonic pane if possible
      else if (key == "escape" && this.mnemonicData.cardHasMnemonic) {
        this.toggleMnemonic();
      } else if (
        this.mnemonicData.cardHasMnemonic &&
        this.mnemonicData.isStudyingMnemonic &&
        !this.hasSubmittedFeedback() &&
        !this.mnemonicData.response &&
        ["1", "2", "3", "4", "5"].includes(key)
      ) {
        this.mnemonicData.mnemonicRating = Number(key);
        if (["3", "4", "5"].includes(key)) {
          this.submitFeedbackIndividualFeedback();
        }
      } else if (
        /^[a-z0-9]$/i.test(key) &&
        !e.altKey &&
        !e.metaKey &&
        !e.shiftKey &&
        !e.ctrlKey
      ) {
        this.$nextTick(() => {
          if (!this.mnemonicData.cardHasMnemonic && this.$refs.retype) {
            this.$refs.retype.focus();
          } else if (
            this.mnemonicData.cardHasMnemonic &&
            this.$refs.retype_mnemonic &&
            (this.mnemonicData.mnemonicRating > 2 || this.hasSubmittedFeedback())
          ) {
            this.$refs.retype_mnemonic.focus();
          } else {
            console.error("retype is not rendered yet");
          }
        });
      } else if (
        e.shiftKey &&
        key == "enter" &&
        this.mnemonicData.cardHasMnemonic &&
        this.mnemonicData.isStudyingMnemonic &&
        this.mnemonicData.response
      ) {
        this.submitComparisonFeedback("equal");
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

    public coinflip() {
      const random_n = Math.random();
      return random_n > 0.5;
    }

    public async setupMnemonicData() {
      const user_id = mainStore.userProfile?.id;
      if (user_id) {
        this.mnemonicData.mnemonicGroup = "mnemonic_" + ((user_id % 2) + 1).toString();
        if (this.studyset?.all_facts) {
          const res = await mainStore.getMnemonic({
            data: {
              user_id: user_id,
              fact_ids: this.studyset.all_facts.map((fact) => {
                return fact.fact_id;
              }),
            },
          });
          this.mnemonicData.feedbackFactIdsLearning = new Set(res.fact_ids_learning);
          this.mnemonicData.feedbackFactIdsComparison = new Set(
            res.fact_ids_comparison,
          );
        }
      }
      const rand_coinflip = this.coinflip();
      this.mnemonicData.mnemonicComparisons[0] = rand_coinflip ? "1" : "2";
      this.mnemonicData.mnemonicComparisons[1] = rand_coinflip ? "2" : "1";
    }

    public async updateMnemonicClick() {
      this.mnemonicData.mnemonicClick = !this.mnemonicData.mnemonicClick;
    }

    public async toggleMnemonic() {
      this.$refs.mnemonicPaneTop.click();
    }

    public hasSubmittedFeedback() {
      const feedbackSet = this.mnemonicData.response
        ? this.mnemonicData.feedbackFactIdsComparison
        : this.mnemonicData.feedbackFactIdsLearning;
      return this.show.fact && feedbackSet.has(this.show.fact.fact_id);
    }

    public async handleMnemonicRatingClick() {
      if ([3, 4, 5].includes(this.mnemonicData.mnemonicRating)) {
        this.submitFeedbackIndividualFeedback();
      }
    }

    public async removeSubmittedFeedback() {
      // sometimes mark the current feedback as completed to measure intra-annotator agreement
      const rand_coinflip = this.coinflip();
      if (this.show.fact && rand_coinflip) {
        this.mnemonicData.feedbackFactIdsLearning.delete(this.show.fact.fact_id);
        this.mnemonicData.feedbackFactIdsLearning = new Set([
          ...this.mnemonicData.feedbackFactIdsLearning,
        ]);
      }
    }

    public async submitFeedbackIndividualFeedback() {
      const rand_coinflip = this.coinflip();
      if (this.mnemonicData.mnemonicRating == 0) {
        mainStore.addNotification({
          content: this.mnemonicData.isInteractiveMnemonic
            ? "You must select a rating to continue!"
            : "You must make a selection to submit feedback!",
          color: "error",
        });
      } else if (this.show.fact && rand_coinflip) {
        // sometimes mark the current feedback as completed to measure intra-annotator agreement
        this.mnemonicData.feedbackFactIdsLearning.add(this.show.fact.fact_id);
        this.mnemonicData.feedbackFactIdsLearning = new Set([
          ...this.mnemonicData.feedbackFactIdsLearning,
        ]);
      }
    }

    public async submitComparisonFeedback(selection: string) {
      if (this.show.fact && selection != "") {
        this.mnemonicData.feedbackFactIdsComparison.add(this.show.fact.fact_id);
        this.mnemonicData.feedbackFactIdsComparison = new Set([
          ...this.mnemonicData.feedbackFactIdsComparison,
        ]);
        this.mnemonicData.comparisonChoice = selection;
      }
      this.response(true);
    }

    public passedSanityCheck(selection: string) {
      if (selection == "") {
        return true;
      }
      if (selection == "equal") {
        return false;
      }
      return (
        (selection == "a_better" && this.mnemonicData.mnemonicComparisons[0] == "1") ||
        (selection == "b_better" && this.mnemonicData.mnemonicComparisons[1] == "1")
      );
    }

    public async resetMnemonicData() {
      if (this.mnemonicData.mnemonicClick) {
        await this.toggleMnemonic();
      }
      const defaultValues = {
        retypedMnemonic: "",
        isStudyingMnemonic: false,
        isIncorrectDefinition: false,
        isNotMemorable: false,
        isDifficultToUnderstand: false,
        isBadKeywordLink: false,
        isOffensive: false,
        isBadPhoneticKeyword: false,
        isBadCircularKeyword: false,
        isBadKeywordExplanation: false,
        isOther: false,
        otherReason: "",
        mnemonicRating: 0,
        response: null,
        panelOpen: -1,
        comparisonChoice: "",
        mnemonicDisplayText: "",
        mnemonicFullText: "",
        isGeneratingMnemonic: false,
        isBuildingMnemonic: false,
        currentMnemonicData: null,
        buildStep: "pre_keyword",
        selectedKeywordIndex: -1,
        selectedExplanationIndex: -1,
        showKeywordSelection: false,
        showExplanationSelection: false,
      };
      // Update interactive mnemonic flag for current fact
      this.mnemonicData.isInteractiveMnemonic = this.isCurrentFactInteractiveMnemonic();
      this.mnemonicData = Object.assign({}, this.mnemonicData, defaultValues);

      // Auto-open panel for interactive mnemonic mode
      if (this.mnemonicData.isInteractiveMnemonic) {
        this.mnemonicData.panelOpen = 0;
        // Start interactive mnemonic building if interactive data is available
        if (
          this.show.fact &&
          this.show.fact.extra &&
          this.show.fact.extra["interactive_mnemonic_data"]
        ) {
          this.startInteractiveMnemonicBuilding();
        } else if (
          this.show.fact &&
          this.show.fact.extra &&
          this.show.fact.extra["mnemonic"]
        ) {
          // Fallback to simple streaming if no interactive data
          this.mnemonicData.mnemonicFullText = this.show.fact.extra["mnemonic"];
          this.generateMnemonicCharacterByCharacter();
        }
      }
    }

    public async dontKnow() {
      if (this.mnemonicData.cardHasMnemonic && !this.mnemonicData.isStudyingMnemonic) {
        this.mnemonicResponse(false);
      }
      this.showResponseBtns = false;
      this.showBack = true;
      this.scrollToResponseButtons();
    }

    public async showAnswer() {
      if (this.inTestMode && this.typed.trimStart() == "") {
        this.requireAnswerError();
      } else {
        await studyStore.evaluateAnswer(this.typed);
        this.showBack = true;
        this.scrollToResponseButtons();
      }
    }

    public resetCard() {
      this.showBack = false;
      this.showResponseBtns = true;
      this.typed = "";
      this.retyped = "";
      this.resetMnemonicData();
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

    public requireAnswerError() {
      mainStore.addNotification({
        content: "In Test Mode, you must type your answer or press don't know!",
        color: "error",
      });
    }

    public async mnemonicResponse(response) {
      this.mnemonicData.response = response;
      if (response && this.hasSubmittedFeedback()) {
        this.response(response);
      } else {
        this.sendResponseNotification(response);
        // Always open panel for interactive mnemonic mode, or when response is true
        if (this.mnemonicData.isInteractiveMnemonic) {
          this.mnemonicData.panelOpen = 0;
        } else {
          this.mnemonicData.panelOpen = response ? 0 : -1;
        }
        this.mnemonicData.isStudyingMnemonic = true;

        // Start interactive mnemonic building for interactive mnemonic mode
        if (
          this.mnemonicData.isInteractiveMnemonic &&
          this.show.fact &&
          this.show.fact.extra &&
          this.show.fact.extra["interactive_mnemonic_data"]
        ) {
          this.startInteractiveMnemonicBuilding();
        } else if (
          this.mnemonicData.isInteractiveMnemonic &&
          this.show.fact &&
          this.show.fact.extra &&
          this.show.fact.extra["mnemonic"]
        ) {
          // Fallback to simple streaming if no interactive data
          this.mnemonicData.mnemonicFullText = this.show.fact.extra["mnemonic"];
          this.generateMnemonicCharacterByCharacter();
        }

        // Only toggle for public mnemonic mode when response is false
        if (!this.mnemonicData.isInteractiveMnemonic && !response) {
          this.toggleMnemonic();
        }
      }
    }

    public async sendResponseNotification(response) {
      if (response) {
        mainStore.addNotification({
          content: "Your evaluation: Right",
          color: "success",
        });
      } else {
        studyStore.setRestudy();
        mainStore.addNotification({
          content: "Your evaluation: Wrong",
          color: "error",
        });
      }
    }

    public async response(response) {
      // Check if user needs to complete mandatory rating before continuing
      if (
        this.mnemonicData.cardHasMnemonic &&
        this.mnemonicData.isStudyingMnemonic &&
        !this.mnemonicData.isInteractiveMnemonic &&
        this.mnemonicData.response &&
        !this.hasSubmittedFeedback()
      ) {
        // For public_mnemonic mode, user must submit feedback before continuing
        mainStore.addNotification({
          content: "You must complete the mnemonic feedback before continuing!",
          color: "error",
        });
        return;
      }

      if (
        this.mnemonicData.cardHasMnemonic &&
        this.mnemonicData.isInteractiveMnemonic &&
        !this.hasSubmittedFeedback()
      ) {
        // For interactive_mnemonic mode, user must submit rating before continuing
        mainStore.addNotification({
          content: "You must rate the mnemonic before continuing!",
          color: "error",
        });
        return;
      }

      if (!this.mnemonicData.isStudyingMnemonic) {
        this.sendResponseNotification(response);
      }

      if (
        this.show &&
        this.show.fact &&
        this.studyset &&
        this.mnemonicData.cardHasMnemonic
      ) {
        if (response) {
          await mainStore.createMnemonicFeedbackLog({
            data: {
              study_id: this.studyset.id,
              fact_id: this.show.fact.fact_id,
              user_id: this.studyset.user.id,
              mnemonic_a:
                this.show &&
                this.show.fact &&
                this.show.fact.extra &&
                this.show.fact.extra[
                  "mnemonic_" + this.mnemonicData.mnemonicComparisons[0]
                ],
              mnemonic_b:
                this.show &&
                this.show.fact &&
                this.show.fact.extra &&
                this.show.fact.extra[
                  "mnemonic_" + this.mnemonicData.mnemonicComparisons[1]
                ],
              comparison_rating:
                this.mnemonicData.comparisonChoice == ""
                  ? null
                  : this.mnemonicData.comparisonChoice,
              correct: response,
              passed_sanity_check:
                this.show.fact.deck.deck_type == "sanity_check"
                  ? this.passedSanityCheck(this.mnemonicData.comparisonChoice)
                  : null,
            },
          });
        } else {
          await mainStore.createMnemonicFeedbackLog({
            data: {
              study_id: this.studyset.id,
              fact_id: this.show.fact.fact_id,
              user_id: this.studyset.user.id,
              user_rating: this.mnemonicData.mnemonicRating,
              is_offensive: this.mnemonicData.isOffensive,
              is_incorrect_definition: this.mnemonicData.isIncorrectDefinition,
              is_not_memorable: this.mnemonicData.isNotMemorable,
              is_difficult_to_understand: this.mnemonicData.isDifficultToUnderstand,
              is_bad_for_other_reason: this.mnemonicData.otherReason != "",
              is_bad_phonetic_keyword: this.mnemonicData.isBadPhoneticKeyword,
              is_bad_circular_keyword: this.mnemonicData.isBadCircularKeyword,
              is_bad_keyword_explanation: this.mnemonicData.isBadKeywordExplanation,
              other_reason_text: this.mnemonicData.otherReason,
              correct: response,
              mnemonic_used_id: this.mnemonicData.mnemonicGroup,
              mnemonic_used_text:
                this.show.fact &&
                this.show.fact.extra &&
                this.show.fact.extra[this.mnemonicData.mnemonicGroup],
            },
          });
        }
      }

      if (this.show.fact) {
        studyStore.markBackTime();
        studyStore.addToSchedule({
          fact_id: this.show.fact.fact_id,
          typed: this.typed,
          response: response,
          elapsed_milliseconds_text: this.frontTime,
          elapsed_milliseconds_answer: this.backTime,
          test_mode: this.inTestMode,
          recommendation: this.recommendation,
        });
        this.resetCard();
        await studyStore.updateSchedule();
        this.resetCard();
      }

      if (this.mnemonicData.cardHasMnemonic) {
        await this.resetMnemonicData();
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
