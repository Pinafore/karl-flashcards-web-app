<template>
  <v-main>
    <v-card class="elevation-12">
      <v-toolbar dark color="primary">
        <v-toolbar-title>Login</v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>
      <v-card-text>
        <v-form @keyup.enter="submit">
          <v-text-field
            v-model="email"
            prepend-icon="mdi-account"
            name="login"
            label="Username/Email"
            type="text"
            @keyup.enter="submit"
          ></v-text-field>
          <v-text-field
            id="password"
            v-model="password"
            prepend-icon="mdi-lock"
            name="password"
            label="Password"
            type="password"
            @keyup.enter="submit"
          ></v-text-field>
        </v-form>
        <div v-if="loginError">
          <v-alert :value="loginError" transition="fade-transition" type="error">
            Incorrect email or password
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
        <v-btn @click="signup">Create Account</v-btn>
        <v-spacer></v-spacer>
        <v-btn @click.prevent="submit">Login</v-btn>
      </v-card-actions>
    </v-card>
  </v-main>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { mainStore } from "@/store";

  @Component
  export default class Login extends Vue {
    public email = "";
    public password = "";
    public appName = appName;

    public get loginError() {
      return mainStore.logInError;
    }

    public signup() {
      this.$router.push("/sign-up");
    }

    public close() {
      this.$router.push("/landing");
    }

    public async submit() {
      await mainStore.logIn({ username: this.email, password: this.password });
    }
  }
</script>

<style></style>
