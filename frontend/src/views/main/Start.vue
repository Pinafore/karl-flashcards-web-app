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
  import { getVisited, saveVisited } from "@/utils";

  const startRouteGuard = async (to, _from, next) => {
    await mainStore.checkLoggedIn();
    if (mainStore.isLoggedIn) {
      mainStore.setisOnHomeScreenPopup(false);
      if (to.path === "/login" || to.path === "/" || to.path === "/landing") {
        mainStore.setisOnHomeScreenPopup(false);
        next("/main");
      } else if (to.path === "/privacy-irb" || to.path === "/pwa" || to.path === "/mnemonic-study") {
        mainStore.setisOnHomeScreenPopup(true);
        next();
      } else {
        mainStore.setisOnHomeScreenPopup(false);
        next();
      }
    } else if (mainStore.isLoggedIn === false) {
      const visited = getVisited();
      if (visited === null && to.path !== "/privacy-irb" && to.path !== "/pwa" && to.path !== "/mnemonic-study") {
        mainStore.setisOnHomeScreenPopup(true);
        // where to direct the user upon first visit
        next(process.env.VUE_APP_UNVISITED_PAGE_DIRECT);
      } else if (to.path === "/" || (to.path as string).startsWith("/main")) {
        next("/landing");
      } else if (
        to.path === "/login" ||
        to.path === "/sign-up" ||
        to.path === "/privacy-irb" ||
        to.path === "/pwa" ||
        to.path === "/mnemonic-study"
      ) {
        mainStore.setisOnHomeScreenPopup(true);
        next();
      } else {
        mainStore.setisOnHomeScreenPopup(false);
        next();
      }
    }
  };

  @Component
  export default class Start extends Vue {
    get dialog() {
      return mainStore.isOnHomeScreenPopup;
    }
    public beforeRouteEnter(to, from, next) {
      startRouteGuard(to, from, next);
    }

    public beforeRouteUpdate(to, from, next) {
      startRouteGuard(to, from, next);
    }
    public goHome() {
      saveVisited();
      this.$router.push("/landing");
    }
  }
</script>
