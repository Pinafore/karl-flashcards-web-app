<template>
  <div>
    <v-navigation-drawer
      v-model="showDrawer"
      color="navigation"
      app
      dark
      :expand-on-hover="$vuetify.breakpoint.smAndUp"
      clipped
      elevation="20"
      mobile-break-point="600"
      bottom
      style="z-index: 11;"
    >
      <v-list>
        <v-list-item to="/main/dashboard">
          <v-list-item-action>
            <v-icon>mdi-web</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Dashboard</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/profile/view">
          <v-list-item-action>
            <v-icon>mdi-account</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-list subheader>
        <v-list-item to="/main/study/decks">
          <v-list-item-action>
            <v-icon>{{ mdiBookMultiple }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Decks</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/study/learn">
          <v-list-item-action>
            <v-icon>mdi-lightbulb-on</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Study All</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/browse">
          <v-list-item-action>
            <v-icon>{{ mdiTextBoxMultiple }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Browse Facts</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-list>
        <v-list-item to="/main/add/fact">
          <v-list-item-action>
            <v-icon>{{ mdiTextBoxPlus }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Add Fact</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/add/deck">
          <v-list-item-action>
            <v-icon>mdi-book-plus</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Add Deck</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/add/upload-facts">
          <v-list-item-action>
            <v-icon>{{ mdiUploadMultiple }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Upload Facts</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/add/public-decks">
          <v-list-item-action>
            <v-icon>{{ mdiEarthPlus }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Add Public Decks</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-list v-show="hasAdminAccess" subheader>
        <v-list-item to="/main/admin/users/all">
          <v-list-item-action>
            <v-icon>mdi-account-multiple</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Manage Users</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/admin/users/create">
          <v-list-item-action>
            <v-icon>mdi-account-plus</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Create User</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <v-list>
          <v-list-item @click="logout">
            <v-list-item-action>
              <v-icon>mdi-close</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item-content>
          </v-list-item>

          <v-divider></v-divider>

          <v-list-item @click="switchShowDrawer">
            <v-list-item-action>
              <v-icon>
                {{
                  $vuetify.breakpoint.smAndUp ? "mdi-chevron-left" : "mdi-chevron-down"
                }}
              </v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Collapse</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list>
      </template>
    </v-navigation-drawer>

    <v-app-bar
      :clipped-left="$vuetify.breakpoint.smAndUp"
      color="navigation"
      dark
      elevation="1"
      app
    >
      <v-app-bar-nav-icon @click.stop="switchShowDrawer"></v-app-bar-nav-icon>
      <v-btn text x-large @click.stop="goHome">{{ appName }}</v-btn>
      <v-spacer></v-spacer>
      <v-switch v-model="$vuetify.theme.dark" label="Dark Mode" hide-details></v-switch>
      <v-menu bottom left offset-y>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/main/profile">
            <v-list-item-content>
              <v-list-item-title>Profile</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>mdi-account</v-icon>
            </v-list-item-action>
          </v-list-item>
          <v-list-item @click="logout">
            <v-list-item-content>
              <v-list-item-title>Logout</v-list-item-title>
            </v-list-item-content>
            <v-list-item-action>
              <v-icon>mdi-close</v-icon>
            </v-list-item-action>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>
    <v-content>
      <router-view></router-view>
    </v-content>
    <v-footer class="pa-3" fixed app>
      <v-spacer></v-spacer>
      <span>&copy; {{ appName }}</span>
    </v-footer>
  </div>
</template>

<script lang="ts">
  import { Vue, Component } from "vue-property-decorator";
  import { appName } from "@/env";
  import { mainStore } from "@/store";
  import {
    mdiEarthPlus,
    mdiTextBoxPlus,
    mdiBookMultiple,
    mdiTextBoxMultiple,
    mdiUploadMultiple,
  } from "@mdi/js";

  const routeGuardMain = async (to, _from, next) => {
    if (to.path === "/main") {
      next("/main/dashboard");
    } else {
      next();
    }
  };

  @Component
  export default class Main extends Vue {
    public appName = appName;
    mdiEarthPlus = mdiEarthPlus;
    mdiTextBoxPlus = mdiTextBoxPlus;
    mdiBookMultiple = mdiBookMultiple;
    mdiTextBoxMultiple = mdiTextBoxMultiple;
    mdiUploadMultiple = mdiUploadMultiple;

    public beforeRouteEnter(to, from, next) {
      routeGuardMain(to, from, next);
    }

    public beforeRouteUpdate(to, from, next) {
      routeGuardMain(to, from, next);
    }

    get showDrawer() {
      return mainStore.dashboardShowDrawer;
    }

    set showDrawer(value) {
      mainStore.setDashboardShowDrawer(value);
    }

    public goHome() {
      this.$router.push("/main");
    }

    public switchShowDrawer() {
      mainStore.setDashboardShowDrawer(!mainStore.dashboardShowDrawer);
    }

    public get hasAdminAccess() {
      return mainStore.hasAdminAccess;
    }

    public async logout() {
      await mainStore.userLogOut();
    }
    // TODO: Don't show bottom for small screen on reload
  }
</script>
