<template>
  <v-content>
    <v-row no-gutters>
      <v-img
        :min-height="'calc(100vh - ' + $vuetify.application.top + 'px)'"
        :src="require('@/assets/background-desktop.png')"
      >
        <v-theme-provider dark>
          <v-container class="fill-height">
            <v-row class="white--text mx-auto" justify="center">
              <v-col class="white--text text-center" cols="12">
                <div
                  :class="[$vuetify.breakpoint.smAndDown ? 'display-3' : 'display-4']"
                  class="font-weight-black"
                >
                  KAR³L
                </div>
                <div
                  :class="[
                    $vuetify.breakpoint.smAndDown
                      ? 'text-subtitle-2'
                      : 'text-subtitle-1',
                  ]"
                  class="font-weight-light"
                >
                  A fresh approach to flashcard learning
                </div>
                <div
                  :class="[
                    $vuetify.breakpoint.smAndDown
                      ? 'text-subtitle-2'
                      : 'text-subtitle-1',
                  ]"
                  class="font-weight-light"
                >
                  Knowledge Acquisition Through Representations and Repetition for
                  Retention and Learning
                </div>
              </v-col>
            </v-row>
            <v-row class="white--text mx-auto" justify="center">
              <v-btn @click="login">
                Log In
              </v-btn>
            </v-row>
            <v-row class="white--text mx-auto" justify="center">
              <v-btn @click="signup">
                Sign Up
              </v-btn>
            </v-row>
            <v-row class="white--text mx-auto" justify="center">
              <v-btn @click="$vuetify.goTo('#about-me')">
                <v-icon>mdi-chevron-double-down</v-icon>
              </v-btn>
            </v-row>
          </v-container>
        </v-theme-provider>
      </v-img>
    </v-row>
  </v-content>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { mainStore } from "@/store";

  @Component
  export default class Login extends Vue {
    public signup() {
      this.$router.push("/sign-up");
    }

    public login() {
      this.$router.push("/login");
    }
  }
</script>

<style></style>
