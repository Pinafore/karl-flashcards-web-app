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
      mobile-breakpoint="600"
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
        <v-list-item to="/main/statistics">
          <v-list-item-action>
            <v-icon>{{ mdiBookInformationVariant }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Statistics</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/leaderboards">
          <v-list-item-action>
            <v-icon>{{ mdiFormatListNumbered }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Leaderboards</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
      <v-divider></v-divider>
      <v-list subheader>
        <v-list-item
          v-if="recallPopup && expiration != null"
          to="/main/study/learn?resume=true"
        >
          <v-list-item-action>
            <v-icon>mdi-lightbulb-on</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Resume Study</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item
          v-if="recallPopup && expiration == null"
          to="/main/study/learn?show_test_mode=true"
        >
          <v-list-item-action>
            <v-icon>mdi-lightbulb-on</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Quick Study (All)</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/study/decks">
          <v-list-item-action>
            <v-icon>{{ mdiBookMultiple }}</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>New Study Set</v-list-item-title>
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
        <v-list-item to="/main/browse?reported=1">
          <v-list-item-action>
            <v-icon>mdi-alert-octagon</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Reported Facts</v-list-item-title>
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
      <v-divider></v-divider>
      <v-list>
        <v-list-item to="/main/profile/view">
          <v-list-item-action>
            <v-icon>mdi-account</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Profile</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/main/contact">
          <v-list-item-action>
            <v-icon>mdi-contacts</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Contact</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item to="/privacy-irb">
          <v-list-item-action>
            <v-icon>mdi-information-outline</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>IRB</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item @click="logout">
          <v-list-item-action>
            <v-icon>mdi-close</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>Logout</v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>

      <template v-slot:append>
        <v-list>
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
      <v-btn class="mx-n3" text x-large @click.stop="goHome">{{ appName }}</v-btn>
      <v-list-item v-show="expiration != null">
        <v-list-item-content v-if="$vuetify.breakpoint.xsOnly" style="padding: 0px">
          Expires: {{ expiration }}
        </v-list-item-content>
        <v-list-item-content v-else>
          Current Study Set Expires at {{ expiration }}
        </v-list-item-content>
      </v-list-item>
      <v-list-item class="justify-end px-2">
        <v-icon>mdi-weather-sunny</v-icon>
        <v-list-item-action>
          <v-switch v-model="darkMode" inset></v-switch>
        </v-list-item-action>
        <v-icon class="pl-2">mdi-weather-night</v-icon>
      </v-list-item>
      <v-menu bottom left offset-y>
        <template v-slot:activator="{ on }">
          <v-btn icon v-on="on">
            <v-icon>mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item to="/ma in/profile">
            <v-list-item-action>
              <v-icon>mdi-account</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Profile</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item to="/main/contact">
            <v-list-item-action>
              <v-icon>mdi-contacts</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>Contact</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
          <v-list-item to="/privacy-irb">
            <v-list-item-action>
              <v-icon>mdi-information-outline</v-icon>
            </v-list-item-action>
            <v-list-item-content>
              <v-list-item-title>IRB</v-list-item-title>
            </v-list-item-content>
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
    <v-main>
      <router-view></router-view>
    </v-main>
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
    mdiFormatListNumbered,
    mdiBookInformationVariant,
  } from "@mdi/js";

  import { parseISO, format } from "date-fns";

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
    mdiBookInformationVariant = mdiBookInformationVariant;
    mdiFormatListNumbered = mdiFormatListNumbered;

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

    // get resumeAvail() {
    //   if (this.expiration() ) {
    //     return mainStore.userProfile.resume_studyset;
    //   } else {
    //     return false;
    //   }
    // }

    get darkMode() {
      this.$vuetify.theme.dark = mainStore.userProfile?.dark_mode ?? false;
      return mainStore.userProfile?.dark_mode;
    }

    set darkMode(set) {
      this.$vuetify.theme.dark = set ?? false;
      mainStore.updateUserProfile({ dark_mode: set });
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

    get recallPopup() {
      if (mainStore.userProfile) {
        return (mainStore.userProfile.recall_target ?? -1) != -1;
      } else {
        return false;
      }
    }

    get expiration() {
      if (mainStore.userProfile && mainStore.userProfile.study_set_expiry_date) {
        return format(parseISO(mainStore.userProfile.study_set_expiry_date), "h:mm a");
      } else {
        return null;
      }
    }
  }
</script>

<style>
  .v-navigation-drawer__content {
    overflow-y: scroll;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* Internet Explorer 10+ */
  }
  .v-navigation-drawer__content::-webkit-scrollbar {
    /* WebKit */
    width: 0;
    height: 0;
  }
  .v-data-table-header.v-data-table-header-mobile {
    display: none;
  }
</style>
