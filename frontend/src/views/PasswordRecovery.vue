<template>
  <v-main>
    <v-container fluid class="fill-height">
      <v-row align="center" justify="center">
        <v-col cols="12" sm="8" md="4">
          <validation-observer ref="observer" v-slot="{ invalid }">
            <form @submit.prevent="onSubmit">
              <v-card class="elevation-12">
                <v-toolbar dark color="primary">
                  <v-toolbar-title>{{ appName }} - Password Recovery</v-toolbar-title>
                </v-toolbar>
                <v-card-text>
                  <p class="subheading">
                    A password recovery email will be sent to the registered account
                  </p>
                  <!-- email field -->
                  <validation-provider
                    v-slot="{ errors }"
                    rules="required"
                    name="email"
                  >
                    <v-text-field
                      v-model="email"
                      label="email"
                      type="text"
                      prepend-icon="mdi-account"
                      :error-messages="errors[0]"
                      required
                      name="email"
                      autocomplete="email"
                      @keyup.enter="onSubmit"
                    ></v-text-field>
                  </validation-provider>
                </v-card-text>
                <v-card-actions>
                  <v-spacer></v-spacer>
                  <v-btn @click="cancel">Cancel</v-btn>
                  <v-btn type="submit" :disabled="invalid">
                    Recover Password
                  </v-btn>
                </v-card-actions>
              </v-card>
            </form>
          </validation-observer>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { mainStore } from "@/store";

  import { required } from "vee-validate/dist/rules";
  import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class Login extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };

    public valid = true;
    public email = "";
    public appName = appName;

    public cancel() {
      this.$router.back();
    }

    public async onSubmit() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      mainStore.recoverPassword({ email: this.email });
    }
  }
</script>

<style></style>
