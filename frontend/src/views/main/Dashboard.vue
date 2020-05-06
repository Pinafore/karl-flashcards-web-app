<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Dashboard</div>
      </v-card-title>
      <v-card-text>
        <div class="headline font-weight-light ma-5">Welcome {{ greetedUser }}!</div>
      </v-card-text>
      <v-card-actions>
        <v-btn to="/main/profile/view">Learn</v-btn>
        <v-btn to="/main/study/decks">Decks</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  @Component
  export default class Dashboard extends Vue {
    get greetedUser() {
      const userProfile = mainStore.userProfile;
      if (userProfile && userProfile.username) {
        if (userProfile.username) {
          return userProfile.username;
        } else {
          return userProfile.email;
        }
      } else {
        return "unknown user";
      }
    }
  }
</script>
