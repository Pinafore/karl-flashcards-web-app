<template>
  <v-container fluid>
    <v-row>
      <v-col>
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Hi {{ greetedUser }}</div>
          </v-card-title>
          <v-card-actions class="pa-4">
            <v-btn to="/main/study/learn">Study All</v-btn>
            <v-btn to="/main/study/decks">Decks</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-if="connectionError">
      <v-col>
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Statistics Unavailable</div>
          </v-card-title>
          <v-card-text>
            Due to updates at the University of Maryland, College Park, the connection
            to KAR³L's scheduler is currently down. During this brief period of time,
            you will be unable to study facts or view statistics, but you may continue
            to access all other functionality (such as the fact browser). Please check
            back in a few hours and KAR³L will be ready again to schedule facts to
            review for you.
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12" md="8">
        <v-card class="mr-0 ml-3 pa-3">
          <v-card-title primary-title class="pb-0 justify-center">
            <div class="headline primary--text justify-center">Stats at a Glance</div>
          </v-card-title>
          <v-data-iterator
            :items="stats"
            hide-default-footer
            disable-sort
            disable-filtering
            disable-pagination
            :loading="loading"
            loading-text="Loading statistics..."
            class="pa-1"
          >
            <template v-slot:default="props">
              <v-row class="justify-center">
                <v-col
                  v-for="item in props.items"
                  :key="item.name"
                  cols="12"
                  :md="item.name === 'All Time' ? 12 : 6"
                  lg="4"
                  class="pa-2"
                >
                  <v-card>
                    <v-card-title
                      class="subheading font-weight-medium justify-center"
                      >{{ item.name }}</v-card-title
                    >
                    <v-divider></v-divider>
                    <v-list dense>
                      <v-list-item v-for="type in types" :key="type.value" class="pa-2">
                        <v-row no-gutters align="end">
                          <v-col cols="9">
                            <v-list-item-content>{{ type.text }} </v-list-item-content>
                          </v-col>
                          <v-col cols="3">
                            <v-list-item-content>{{
                              item[type.value]
                            }}</v-list-item-content>
                          </v-col>
                        </v-row>
                      </v-list-item>
                    </v-list>
                  </v-card>
                </v-col>
              </v-row>
            </template>
          </v-data-iterator>
          <v-card-actions class="pa-0">
            <v-btn to="/main/statistics">More Stats</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      <v-col>
        <v-card class="ml-0 mr-3 pa-3">
          <v-card-title primary-title class="pb-3 justify-center">
            <div class="headline primary--text justify-center">
              Today
            </div>
          </v-card-title>
          <v-data-table
            disable-pagination
            disable-filtering
            hide-default-footer
            class="elevation-1 mb-3 pa-1"
            :headers="leaderboard.headers"
            item-key="id"
            :loading="loading"
            :items="leaderboard.leaderboard"
          >
          </v-data-table>
          <v-card-actions class="pa-0">
            <v-btn to="/main/leaderboards">More Leaderboards</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore } from "@/store";

  import "@/utils/date.extensions";

  @Component
  export default class Dashboard extends Vue {
    loading = true;

    get greetedUser() {
      const userProfile = mainStore.userProfile;
      if (userProfile && userProfile.username) {
        if (userProfile.username) {
          return userProfile.username;
        } else {
          return userProfile.email;
        }
      } else {
        return "unknown user";
      }
    }

    get types() {
      return mainStore.types;
    }

    async mounted() {
      this.loading = true;
      await mainStore.getHomeStatistics();
      const date = new Date();
      date.setHours(0, 0, 0, 0);
      date.setDate(date.getDate());
      await mainStore.getHomeLeaderboard({
        rank_type: "total_seen",
        date_start: date.toIsoString(),
      });
      this.loading = false;
    }

    get stats() {
      return mainStore.homeStats;
    }

    get leaderboard() {
      return mainStore.homeLeaderboard ?? { leaderboard: [] };
    }

    get connectionError() {
      return mainStore.connectionError;
    }
  }
</script>
