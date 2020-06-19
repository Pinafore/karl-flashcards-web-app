<template>
  <div>
    <v-dialog v-model="dialog" max-width="1000px" @click:outside="goHome">
      <router-view name="dialog"></router-view>
    </v-dialog>
    <router-view></router-view>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  const startRouteGuard = async (to, _from, next) => {
    await mainStore.checkLoggedIn();
    if (mainStore.isLoggedIn) {
      mainStore.setIsOnLogin(false);
      if (to.path === "/login" || to.path === "/") {
        next("/main");
      } else {
        next();
      }
    } else if (mainStore.isLoggedIn === false) {
      if (to.path === "/" || (to.path as string).startsWith("/main")) {
        next("/landing");
      } else if (to.path === "/login" || to.path === "/sign-up") {
        mainStore.setIsOnLogin(true);
        next();
      } else {
        mainStore.setIsOnLogin(false);
        next();
      }
    }
  };

  @Component
  export default class Start extends Vue {
    get dialog() {
      return mainStore.isOnLogin;
    }
    public beforeRouteEnter(to, from, next) {
      startRouteGuard(to, from, next);
    }

    public beforeRouteUpdate(to, from, next) {
      startRouteGuard(to, from, next);
    }
    public goHome() {
      this.$router.push("/landing");
    }
  }
</script>
