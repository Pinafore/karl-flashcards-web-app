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
            <div class="headline primary--text justify-center">Stats</div>
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
              Leaderboard
            </div>
          </v-card-title>
          <v-data-iterator
            :items="leaderboards"
            hide-default-footer
            disable-sort
            disable-filtering
            disable-pagination
            :loading="loading"
            loading-text="Loading leaderboards..."
            class="pa-1"
          >
            <template v-slot:default="props">
              <v-row
                ><v-select
                  v-model="rankType"
                  :items="rankTypes"
                  item-text="text"
                  item-value="value"
                  label="Rank By"
                  dense
                  solo
                  class="px-2 pt-2 pb-3"
                  hide-details
                ></v-select
              ></v-row>
              <v-row class="justify-center">
                <v-col
                  v-for="item in props.items"
                  :key="item.name"
                  cols="12"
                  xl="6"
                  class="pa-2"
                >
                  <v-card>
                    <v-card-title
                      class="subheading font-weight-medium justify-center pb-0"
                      >{{ item.name }}</v-card-title
                    >
                    <div class="px-2 mb-0 pt-1 pb-2 text-center">
                      {{ item.details }}
                    </div>
                    <v-row class="justify-center pb-2">
                      <div v-if="item.user_place !== null">
                        Your Rank: {{ item.user_place + 1 }}
                      </div>
                      <div v-else class="text-center">
                        Your Rank: N/A
                      </div>
                    </v-row>
                    <v-divider></v-divider>
                    <v-data-table
                      disable-pagination
                      disable-filtering
                      disable-sort
                      hide-default-footer
                      class="mb-3 pa-1 pt-0 px-2"
                      :headers="item.headers"
                      item-key="id"
                      :loading="loading"
                      :items="item.leaderboard"
                    >
                    </v-data-table>
                  </v-card>
                </v-col>
              </v-row>
            </template>
          </v-data-iterator>
          <v-card-actions class="pa-0">
            <v-btn to="/main/leaderboards">More Leaderboards</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore } from "@/store";

  import "@/utils/date.extensions";

  @Component
  export default class Dashboard extends Vue {
    loading = true;
    rankType = "total_seen";

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

    get rankTypes() {
      return mainStore.rankTypes;
    }

    async mounted() {
      this.loading = true;
      await mainStore.getHomeStatistics();
      await this.getLeaderboards();
    }

    @Watch("rankType")
    onRankTypeChanged() {
      this.getLeaderboards();
    }

    async getLeaderboards() {
      this.loading = true;
      const date = new Date();
      date.setHours(0, 0, 0, 0);
      date.setDate(date.getDate());
      await mainStore.getHomeLeaderboards([
        {
          rank_type: this.rankType,
        },
        {
          rank_type: this.rankType,
          date_start: date.toIsoString(),
        },
      ]);
      this.loading = false;
    }
    get stats() {
      return mainStore.homeStats;
    }

    get leaderboards() {
      return mainStore.homeLeaderboards ?? [];
    }

    get connectionError() {
      return mainStore.connectionError;
    }
  }
</script>
