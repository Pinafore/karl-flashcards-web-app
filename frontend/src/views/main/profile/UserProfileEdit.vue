<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Edit User Profile</div>
          </v-card-title>
          <v-card-text>
            <validation-provider v-slot="{ errors }" name="Username" rules="required">
              <v-text-field
                v-model="username"
                label="Username"
                :error-messages="errors[0]"
                required
                name="username"
                autocomplete="username"
              ></v-text-field>
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              rules="required|email"
              name="E-mail"
            >
              <v-text-field
                v-model="email"
                label="E-mail"
                type="email"
                :error-messages="errors[0]"
                required
                name="email"
                autocomplete="email"
              ></v-text-field>
            </validation-provider>
            <v-radio-group v-model="recallTarget" row>
              <v-radio
                v-for="num in recallTargetOptions"
                :key="num"
                :label="`${num}% Recall`"
                :value="num"
              >
              </v-radio>
            </v-radio-group>
            <v-checkbox v-model="showTips" label="Show Tips"></v-checkbox>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancel">Cancel</v-btn>
            <v-btn type="reset">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid">
              Save
            </v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { IComponents } from "@/interfaces";
  import { mainStore } from "@/store";
  import { required, email, between } from "vee-validate/dist/rules";
  import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("email", { ...email, message: "Invalid email address" });
  extend("between", { ...between, message: "{_field_} must be between 0 and 100" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class UserProfileEdit extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };

    valid = true;
    username = "";
    email = "";
    showTips = false;
    recallTarget = 0;
    recallTargetOptions: number[] = [50, 85];

    created() {
      const userProfile = mainStore.userProfile;
      if (userProfile) {
        this.username = userProfile.username;
        this.email = userProfile.email;
        this.showTips = userProfile.show_help;
        this.recallTarget = userProfile.recall_target;
      }
    }

    get userProfile() {
      return mainStore.userProfile;
    }

    onReset() {
      const userProfile = mainStore.userProfile;
      if (userProfile) {
        this.username = userProfile.username;
        this.email = userProfile.email;
        this.showTips = userProfile.show_help;
        this.recallTarget = userProfile.recall_target;
      }
      this.$refs.observer.reset();
    }

    cancel() {
      this.$router.back();
    }

    async onSubmit() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      const userProfile = mainStore.userProfile;
      const updatedProfile: IComponents["UserUpdate"] = {};
      if (userProfile && this.username != userProfile.username) {
        // eslint-disable-next-line @typescript-eslint/camelcase
        updatedProfile.username = this.username;
      }
      if (userProfile && this.email != userProfile.email) {
        updatedProfile.email = this.email;
      }

      if (userProfile && this.recallTarget != userProfile.recall_target) {
        updatedProfile.recall_target = this.recallTarget;
      }

      if (userProfile && this.showTips != userProfile.show_help) {
        updatedProfile.show_help = this.showTips;
      }

      await mainStore.updateUserProfile(updatedProfile);
      await this.$router.push("/main/profile");
    }
  }
</script>
