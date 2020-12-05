<template>
  <v-container fluid>
    <connection-popup></connection-popup>
    <v-card class="ma-3 mb-0 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Filter Leaderboards</div>
      </v-card-title>
      <v-row>
        <v-col>
          <v-select
            v-model="searchOptions.rank_type"
            :items="rankTypes"
            item-text="text"
            item-value="value"
            label="Rank By"
            hide-details
            dense
          ></v-select>
        </v-col>
        <v-col>
          <v-select
            v-model="searchOptions.deck_id"
            :items="decks"
            item-text="title"
            item-value="id"
            label="Decks"
            deletable-chips
            hide-details
            dense
          ></v-select>
        </v-col>
        <v-col cols="12" sm="6" md="4">
          <v-menu
            ref="startMenu"
            v-model="startMenu"
            :close-on-content-click="false"
            transition="scale-transition"
            offset-y
            min-width="290px"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="searchOptions.date_start"
                label="Start Date"
                prepend-icon="mdi-calendar"
                readonly
                dense
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="searchOptions.date_start"
              :max="today"
              no-title
              scrollable
            >
              <v-spacer></v-spacer>
              <v-btn text color="primary" @click="clearStartDate">Clear</v-btn>
              <v-btn
                text
                color="primary"
                @click="$refs.startMenu.save(searchOptions.date_start)"
                >OK</v-btn
              >
            </v-date-picker>
          </v-menu>
        </v-col>
        <v-col cols="12" sm="6" md="4">
          <v-menu
            ref="endMenu"
            v-model="endMenu"
            :close-on-content-click="false"
            transition="scale-transition"
            offset-y
            min-width="290px"
          >
            <template v-slot:activator="{ on, attrs }">
              <v-text-field
                v-model="searchOptions.date_end"
                label="End Date"
                prepend-icon="mdi-calendar"
                readonly
                dense
                v-bind="attrs"
                v-on="on"
              ></v-text-field>
            </template>
            <v-date-picker
              v-model="searchOptions.date_end"
              :min="searchOptions.date_start"
              :max="today"
              no-title
              scrollable
            >
              <v-spacer></v-spacer>
              <v-btn text color="primary" @click="clearEndDate">Clear</v-btn>
              <v-btn
                text
                color="primary"
                @click="$refs.endMenu.save(searchOptions.date_end)"
                >OK</v-btn
              >
            </v-date-picker>
          </v-menu>
        </v-col>
      </v-row>
      <v-row v-if="filteredLeaderboard">
        <v-col>
          <v-card class="pa-3">
            <v-card-title primary-title class="pb-2 justify-center">
              <div class="headline primary--text justify-center">
                {{ filteredLeaderboard.name }}
              </div>
            </v-card-title>
            <div class="px-2 text-center">{{ filteredLeaderboard.details }}</div>
            <v-row justify="center">
              <v-btn
                v-if="showGoToUser()"
                class="px-2 mt-2 justify-center"
                @click="goToUser()"
                >Your Rank: {{ userRank() }} - See Page</v-btn
              >
              <div v-else-if="showRank()" class="px-2 text-center">
                Your Rank: {{ userRank() }}
              </div>
              <div v-else class="px-2 text-center">
                Your Rank: N/A
              </div>
            </v-row>

            <v-data-table
              disable-filtering
              disable-sort
              class="mb-3 pa-1"
              :headers="filteredLeaderboard.headers"
              item-key="id"
              :loading="loading"
              :items="filteredLeaderboard.leaderboard"
              :options.sync="options"
              :server-items-length="filteredLeaderboard.total"
              :footer-props="{
                itemsPerPageOptions: [10, 25, 50, 100],
                showFirstLastPage: true,
              }"
            >
            </v-data-table>
          </v-card>
        </v-col>
      </v-row>
      <v-row v-else>
        <v-col>
          <v-card class="pa-3">
            <v-card-title primary-title class="pb-2 justify-center">
              <div class="headline primary--text justify-center">
                Loading
              </div>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore } from "@/store";
  import { IComponents } from "@/interfaces";
  import ConnectionPopup from "@/views/ErrorPopup.vue";
  import { DataOptions } from "vuetify";

  @Component({
    components: { ConnectionPopup },
  })
  export default class Leaderboard extends Vue {
    loading = true;
    searchOptions: IComponents["LeaderboardSearch"] = { rank_type: "total_seen" };
    startMenu = false;
    endMenu = false;
    options: DataOptions = {
      groupBy: [],
      groupDesc: [],
      itemsPerPage: 25,
      multiSort: false,
      mustSort: false,
      page: 1,
      sortBy: [],
      sortDesc: [],
    };

    async mounted() {
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
      await this.searchLeaderboards();
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks
        ? [{ title: "All", public: false, id: 0 }].concat(userProfile.decks)
        : [];
    }

    get today() {
      return mainStore.today;
    }

    get filteredLeaderboard() {
      return mainStore.filteredLeaderboard;
    }

    get rankTypes() {
      return mainStore.rankTypes;
    }

    @Watch("searchOptions", { deep: true })
    onSearchOptionsChanged() {
      if (this.searchOptions.deck_id == 0) {
        this.searchOptions.deck_id = undefined;
      }
      this.searchLeaderboards();
    }

    @Watch("options", { deep: true })
    onOptionsChanged(value: DataOptions) {
      this.searchOptions.skip = value.page * value.itemsPerPage - value.itemsPerPage;
      this.searchOptions.limit = value.itemsPerPage;
      this.searchLeaderboards();
    }

    async searchLeaderboards() {
      this.loading = true;
      await mainStore.getLeaderboard(this.searchOptions);
      this.loading = false;
    }

    showRank() {
      const place = this.filteredLeaderboard?.user_place ?? null;
      return place !== null;
    }

    showGoToUser() {
      const place = this.filteredLeaderboard?.user_place ?? null;
      if (place) {
        return (
          (this.options.page - 1) * this.options.itemsPerPage >= place ||
          place >
            (this.options.page - 1) * this.options.itemsPerPage +
              this.options.itemsPerPage
        );
      } else {
        return false;
      }
    }
    goToUser() {
      const place = this.filteredLeaderboard?.user_place ?? null;
      if (place) {
        this.options.page = Math.ceil(place / this.options.itemsPerPage);
        this.searchOptions.skip =
          Math.floor(place / this.options.itemsPerPage) * this.options.itemsPerPage;
        this.searchOptions.limit = this.options.itemsPerPage;
        this.searchLeaderboards();
      }
    }

    userRank() {
      const place =
        this.filteredLeaderboard?.user_place !== undefined
          ? this.filteredLeaderboard?.user_place + 1
          : null;
      if (place) {
        return place;
      } else {
        return "N/A";
      }
    }

    clearStartDate() {
      this.startMenu = false;
      this.searchOptions.date_start = undefined;
    }

    clearEndDate() {
      this.endMenu = false;
      this.searchOptions.date_end = undefined;
    }
  }
</script>
