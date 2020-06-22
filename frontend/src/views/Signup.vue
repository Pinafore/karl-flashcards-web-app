<template>
  <v-content>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="elevation-24">
          <v-toolbar dark color="primary">
            <v-toolbar-title
              >Sign Up — {{ appName }} (IRB Form, Scroll Down To Sign Up!)
            </v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
            <validation-provider
              v-slot="{ errors }"
              name="Email"
              rules="required|email"
            >
              <v-text-field
                v-model="email"
                prepend-icon="mdi-account"
                :error-messages="errors[0]"
                label="Email"
                type="email"
                required
              ></v-text-field>
            </validation-provider>
            <validation-provider v-slot="{ errors }" name="Username" rules="required">
              <v-text-field
                v-model="username"
                prepend-icon="mdi-account"
                label="Username"
                :error-messages="errors[0]"
                autocomplete="off"
                required
              ></v-text-field>
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              :debounce="100"
              name="Password"
              vid="password1"
              rules="required"
            >
              <v-text-field
                v-model="password1"
                prepend-icon="mdi-lock"
                type="password"
                label="Password"
                :error-messages="errors"
                autocomplete="off"
              ></v-text-field>
            </validation-provider>
            <validation-provider
              v-slot="{ errors }"
              :debounce="100"
              name="Password confirmation"
              vid="password2"
              rules="required|confirmed:password1"
              autocomplete="off"
            >
              <v-text-field
                v-model="password2"
                prepend-icon="mdi-lock"
                type="password"
                label="Confirm Password"
                :error-messages="errors"
                autocomplete="off"
              ></v-text-field>
            </validation-provider>

            <div v-if="signUpError">
              <v-alert :value="signUpError" transition="fade-transition" type="error">
                A user with this email or username already exists
              </v-alert>
            </div>
            <v-col class="caption text-right"
              ><router-link to="/recover-password"
                >Forgot your password?</router-link
              ></v-col
            >
          </v-card-text>
          <v-card-actions>
            <v-btn @click="close">Close</v-btn>
            <v-btn @click="login">Go to Login</v-btn>
            <v-spacer></v-spacer>
            <v-btn type="reset">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid">Sign Up</v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-content>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { confirmed, email, required } from "vee-validate/dist/rules";
  import { extend, ValidationObserver, ValidationProvider } from "vee-validate";
  import { mainStore } from "@/utils/store-accessor";
  import { IComponents } from "@/interfaces";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("confirmed", { ...confirmed, message: "Passwords do not match" });
  extend("email", { ...email, message: "Invalid email address" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class SignUp extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };
    appName = appName;
    username = "";
    email = "";
    password1 = "";
    password2 = "";
    signUpError: boolean | null = null;

    async mounted() {
      this.onReset();
    }

    public login() {
      this.$router.push("/login");
    }

    public close() {
      this.$router.push("/landing");
    }

    onReset() {
      this.password1 = "";
      this.password2 = "";
      this.username = "";
      this.email = "";
      this.$refs.observer.reset();
    }

    async onSubmit() {
      this.signUpError = false;
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      const updatedProfile: IComponents["UserCreate"] = {
        email: this.email,
        username: this.username,
        password: this.password1,
      };
      if (await mainStore.createUserOpen(updatedProfile)) {
        await mainStore.logIn({ username: this.email, password: this.password1 });
      } else {
        this.signUpError = true;
      }
    }
  }
</script>
