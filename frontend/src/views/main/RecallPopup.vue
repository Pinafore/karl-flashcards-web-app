<template class="pa-0 ma-0">
  <validation-observer ref="observer" v-slot="{ invalid }">
    <v-dialog v-model="recallPopup" max-width="1000px" persistent>
      <v-card>
        <v-card-title>
          <h2>Phase 2: Set Target Recall Percentage</h2>
        </v-card-title>
        <v-card-text>
          <p>
            In KAR³L phase 2, we have randomly assigned all users to one of two new
            scheduling systems. One scheduler allows you to adjust preferred level of
            difficulty by specifying the ideal likelihood for getting your flashcards
            correct should be (target recall percentage). This scheduler then shows
            flashcards with recall probabilities closest to this target.
          </p>
          <p>
            To maintain anonymity in scheduler assignments, we ask <b>all users</b> to
            specify their target recall percentage even though not all schedulers are
            affected by the setting. This setting may be adjusted later in the User
            Profile screen.
          </p>
          <validation-provider
            v-slot="{ errors }"
            rules="required|between:0,100"
            name="Target Recall Percentage"
          >
            <v-text-field
              v-model="recallTarget"
              label="Target Recall Percentage (Must be between 0 and 100)"
              :error-messages="errors[0]"
              required
              name="Target Recall Percentage"
            ></v-text-field>
          </validation-provider>
        </v-card-text>

        <v-card-actions class="pt-0">
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="onSubmit">
            Done
          </v-btn>
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
      mainStore.setRecallPopup(this.isRequired || this.$router.currentRoute.name === "settings");
    }


    get isRequired() {
      return this.currentRecallTarget == -1;
    }

    get currentRecallTarget() {
      return this.userProfile?.recall_target ?? -1;
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
      await new Promise(resolve => setTimeout(resolve, 100));
      studyStore.setShowActions();
    }
  }
</script>

<style></style>
