<template>
  <v-main>
    <v-img
      :min-height="'calc(100vh - ' + $vuetify.application.top + 'px)'"
      :src="require('@/assets/background-desktop.png')"
      ><v-theme-provider dark>
        <v-container fluid>
          <v-row justify="center" class="pt-2">
            <v-col align-self="center" class="text-md-h1 text-h2 font-weight-bold">
              <div class="white--text text-center">{{ appName }}</div>
            </v-col>
          </v-row>
          <v-row justify="center" class="pt-0 mt-0" no-gutters>
            <v-col
              align-self="center"
              class="pt-0 mt-0 text-md-h4 text-h5 font-weight-bold"
            >
              <div class="white--text text-center">
                A Fresh Approach to Flashcards
              </div>
            </v-col>
          </v-row>
          <v-row justify="center" class="mb-3 hidden-xs-only">
            <v-col align-self="center" class="text-h6 font-weight-bold font-italic">
              <div class="white--text text-center">
                Knowledge Application using Repetition & Representations for Retention &
                Learning
              </div>
            </v-col>
          </v-row>
          <v-row justify="center" align="center" class="pa-3">
            <v-col cols="auto">
              <v-btn
                large
                depressed
                color="white"
                class="primary--text text-h5 text-none"
                width="200px"
                @click="signup"
              >
                Sign Up
              </v-btn>
            </v-col>
            <v-col cols="auto">
              <v-btn
                large
                depressed
                color="white"
                class="primary--text text-h5 text-none"
                width="200px"
                @click="login"
              >
                Login
              </v-btn>
            </v-col>
          </v-row>
          <v-row justify="center" class="pa-3">
            <v-btn
              width="200px"
              large
              text
              class="white--text text-h5 text-none"
              @click="privacy"
            >
              IRB Privacy Form
            </v-btn>
          </v-row>
          <v-row justify="center" no-gutters>
            <v-col sm="5" cols="12">
              <v-card outlined color="transparent">
                <v-container class="text-h6 white--text font-weight-medium">
                  <v-row align="center">
                    <v-col cols="auto" order="1" order-sm="1">
                      <v-icon size="100" class="ml-n4">{{ mdiHeadCog }}</v-icon>
                    </v-col>
                    <v-col order="2" order-sm="2">
                      <div>
                        KAR³L
                        <span class="text-decoration-underline font-weight-bold"
                          >automatically reviews</span
                        >
                        typed answers and recommends an
                        <span class="text-decoration-underline font-weight-bold">
                          evaluation
                        </span>
                      </div>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card>
            </v-col>
            <v-col sm="5" cols="12">
              <v-card outlined color="transparent">
                <v-container class="text-h6 white--text font-weight-medium">
                  <v-row align="center">
                    <v-col cols="auto" order="2" order-sm="1">
                      <v-img
                        width="100"
                        :src="require('@/assets/neural-net.svg')"
                      ></v-img>
                    </v-col>
                    <v-col order="1" order-sm="2">
                      <div>
                        <span class="text-decoration-underline font-weight-bold">
                          Representation learning</span
                        >
                        leads to more
                        <span class="text-decoration-underline font-weight-bold"
                          >topical</span
                        >
                        flashcard suggestions
                      </div>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card>
            </v-col>
          </v-row>
          <v-row justify="center" align="center">
            <v-col sm="5" cols="12">
              <v-card outlined color="transparent">
                <v-container class="text-h6 white--text font-weight-medium">
                  <v-row align="center">
                    <v-col cols="auto" order="1" order-sm="2">
                      <v-icon size="90">{{ mdiFormatListNumbered }}</v-icon>
                    </v-col>
                    <v-col order="2" order-sm="1">
                      <div>
                        See personal
                        <span class="text-decoration-underline font-weight-bold"
                          >statistics</span
                        >
                        and compete with friends to earn a spot on
                        <span class="text-decoration-underline font-weight-bold">
                          leaderboards
                        </span>
                      </div>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card>
            </v-col>
            <v-col sm="5" cols="12">
              <v-card outlined color="transparent">
                <v-container class="text-h6 white--text font-weight-medium">
                  <v-row align="center">
                    <v-col cols="auto" order="2" order-sm="2">
                      <v-img
                        width="60"
                        :src="require('@/assets/spaced-repetition.svg')"
                      ></v-img>
                    </v-col>
                    <v-col order="1" order-sm="1">
                      <div>
                        Intelligent
                        <span class="text-decoration-underline font-weight-bold">
                          spaced repetition</span
                        >
                        makes studying more efficient and prioritizes
                        <span class="text-decoration-underline font-weight-bold">
                          long-term retention
                        </span>
                      </div>
                    </v-col>
                  </v-row>
                </v-container>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
        <v-dialog>
          <router-view name="dialog"></router-view>
        </v-dialog>
      </v-theme-provider>
    </v-img>
  </v-main>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { mdiHeadCog, mdiFormatListNumbered } from "@mdi/js";

  @Component
  export default class Index extends Vue {
    public appName = appName;
    mdiHeadCog = mdiHeadCog;
    mdiFormatListNumbered = mdiFormatListNumbered;
    public signup() {
      this.$router.push("/sign-up");
    }

    public login() {
      this.$router.push("/login");
    }

    public privacy() {
      this.$router.push("/privacy-irb");
    }
  }
</script>

<style></style>
