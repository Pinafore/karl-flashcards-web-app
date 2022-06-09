<template class="pa-0 ma-0">
  <validation-observer ref="observer" v-slot="{ invalid }">
    <v-dialog v-model="recallPopup" max-width="1000px" persistent>
      <v-card>
        <v-card-title>
          <h2>Phase 2: Set Target Recall Percentage</h2>
        </v-card-title>
        <v-card-text style="padding-bottom: 0px;">
          <p>
            In KAR³L phase 2, we ask you to specify your desired rate of correctly
            recalling a flashcard (target recall percentage).
          </p>
          <p>
            Your answer may or may not affect the flashcards you see. This setting may
            be adjusted later in the User Profile screen.
          </p>
        </v-card-text>

        <v-card-actions class="pt-0">
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="set50"> 50% Recall </v-btn
          ><v-btn color="primary" text @click="set85">
            85% Recall
          </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </validation-observer>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";
  import { IComponents } from "@/interfaces";
  import { between, required } from "vee-validate/dist/rules";
  import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("between", { ...between, message: "{_field_} must be between 0 and 100" });
  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class RecallPopup extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };
    recallTarget = 0;

    async mounted() {
      this.setPopup();
      this.recallTarget = this.currentRecallTarget;
    }

    get userProfile() {
      return mainStore.userProfile;
    }

    get recallPopup() {
      return mainStore.recallPopup;
    }

    setPopup() {
      mainStore.setRecallPopup(
        this.isRequired || this.$router.currentRoute.name === "settings",
      );
    }

    get isRequired() {
      return this.currentRecallTarget == -1;
    }

    get currentRecallTarget() {
      return this.userProfile?.recall_target ?? -1;
    }

    set50() {
      this.recallTarget = 50;
      this.onSubmit();
    }

    set85() {
      this.recallTarget = 85;
      this.onSubmit();
    }

    async onSubmit() {
      const success = await this.$refs.observer.validate();
      if (!success) {
        return;
      }
      mainStore.setRecallPopup(false);

      const updatedProfile: IComponents["UserUpdate"] = {};

      if (this.isRequired) {
        updatedProfile.recall_target = this.recallTarget;
      }

      await mainStore.updateUserProfile(updatedProfile);
      await new Promise((resolve) => setTimeout(resolve, 100));
      studyStore.setShowActions();
    }
  }
</script>

<style></style>
