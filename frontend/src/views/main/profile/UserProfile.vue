<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">User Profile</div>
      </v-card-title>
      <v-card-text>
        <div class="my-4">
          <div class="subheading secondary--text">User ID</div>
          <div v-if="userProfile && userProfile.id" class="title primary--text">
            {{ userProfile.id }}
          </div>
          <div v-else class="title primary--text">-----</div>
        </div>
        <div class="my-4">
          <div class="subheading secondary--text">Username</div>
          <div v-if="userProfile && userProfile.username" class="title primary--text">
            {{ userProfile.username }}
          </div>
          <div v-else class="title primary--text">-----</div>
        </div>
        <div class="my-4">
          <div class="subheading secondary--text">Email</div>
          <div v-if="userProfile && userProfile.email" class="title primary--text">
            {{ userProfile.email }}
          </div>
          <div v-else class="title primary--text">-----</div>
        </div>
        <div class="my-3">
          <div class="subheading secondary--text">Tips</div>
          <div v-if="userProfile && userProfile.show_help" class="title primary--text">
            Shown
          </div>
          <div v-if="userProfile && !userProfile.show_help" class="title primary--text">
            Disabled
          </div>
          <!-- <div v-else class="title primary--text">
            -----
          </div> -->
        </div>
        <div class="my-3">
          <div class="subheading secondary--text">Mnemonic Tips</div>
          <div v-if="userProfile && userProfile.show_mnemonic_help" class="title primary--text">
            Shown
          </div>
          <div v-if="userProfile && !userProfile.show_mnemonic_help" class="title primary--text">
            Disabled
          </div>
          <!-- <div v-else class="title primary--text">
            -----
          </div> -->
        </div>
        <!-- <div class="my-3">
          <div class="subheading secondary--text">
            Target Recall Percentage (Only Affects Certain Randomly Assigned Users)
          </div>
          <div
            v-if="userProfile && userProfile.recall_target"
            class="title primary--text"
          >
            {{ userProfile.recall_target }}%
          </div>
          <div v-else class="title primary--text">
            -----
          </div>
        </div> -->
      </v-card-text>
      <v-card-actions>
        <v-btn to="/main/profile/edit">Edit</v-btn>
        <v-btn to="/main/profile/password">Change password</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  @Component
  export default class UserProfile extends Vue {
    get userProfile() {
      return mainStore.userProfile;
    }

    public goToEdit() {
      this.$router.push("/main/profile/edit");
    }

    public goToPassword() {
      this.$router.push("/main/profile/password");
    }
  }
</script>
