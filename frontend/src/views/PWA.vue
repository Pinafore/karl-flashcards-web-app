<template class="pa-0 ma-0">
  <v-main class="pa-0 ma-0">
    <v-dialog v-model="pwa_tip" width="1000" @click:outside="exit()">
      <v-card>
        <v-card-title>
          <h2>
            <span class="hidden-xs-only">You Can </span>Download
            <span class="hidden-sm-and-up"><br /></span>KAR³L!
          </h2>
        </v-card-title>
        <v-card-text>
          KAR³L can be installed as both a native desktop and mobile app! See
          instructions below.
        </v-card-text>
        <v-expansion-panels v-model="panel" multiple>
          <v-expansion-panel>
            <v-expansion-panel-header>iOS</v-expansion-panel-header>
            <v-expansion-panel-content
              >The images below show steps for adding KAR³L to the homescreen.
              <v-row justify="space-around">
                <v-col cols="6" sm="4" class="justify-center">
                  <v-img
                    max-width="300"
                    :src="require('@/assets/ios_button.jpg')"
                  ></v-img>
                </v-col>
                <v-col cols="6" sm="4" class="justify-center">
                  <v-img
                    max-width="300"
                    :src="require('@/assets/ios_screen.jpg')"
                  ></v-img>
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>

          <v-expansion-panel>
            <v-expansion-panel-header>Android</v-expansion-panel-header>
            <v-expansion-panel-content>
              On your first visit to KAR³L in your web browser, an install banner should
              appear. If you choose not to install KAR³L then, you can do so any time by
              clicking on the browser menu and selecting
              <strong>Add to Home screen</strong>.
            </v-expansion-panel-content>
          </v-expansion-panel>

          <v-expansion-panel>
            <v-expansion-panel-header>Desktop</v-expansion-panel-header>
            <v-expansion-panel-content>
              Desktop KAR³L can currently be installed through either Chrome or
              Microsoft Edge. If you visit KAR³L in these browsers, you can install
              KAR³L by clicking on the + button on the right edge of the address bar.
              <v-row>
                <v-col cols="12">
                  <v-img :src="require('@/assets/karl_install.png')"></v-img>
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>

        <v-card-actions class="pt-3">
          <v-spacer class="hidden-xs-only"></v-spacer>
          <v-row no-gutters>
            <v-col>
              <v-btn color="primary" text @click="noMorePWA">
                Don't Show Again
              </v-btn>
            </v-col>
            <v-col>
              <v-btn color="primary" text @click="exit">
                Remind Me Later
              </v-btn>
            </v-col>
            <v-col>
              <v-btn color="primary" text @click="noMorePWA">
                I've Done It!
              </v-btn>
            </v-col>
          </v-row>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-main>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  @Component
  export default class PWA extends Vue {
    pwa_tip = false;
    panel = [0, 1, 2];

    async mounted() {
      await mainStore.getUserProfile();
      this.pwa_tip =
        (mainStore.userProfile?.pwa_tip ?? false) ||
        this.$router.currentRoute.name === "pwa";
      if (this.$vuetify.breakpoint.xsOnly) {
        this.panel = [0, 1];
      } else {
        this.panel = [2];
      }
    }

    noMorePWA() {
      if (this.$router.currentRoute.name === "pwa") {
        this.$router.push("/landing");
      }
      mainStore.updatePWA(false);
      this.pwa_tip = false;
    }

    exit() {
      this.pwa_tip = false;
      if (this.$router.currentRoute.name === "pwa") {
        this.$router.push("/landing");
      }
    }
  }
</script>

<style></style>
