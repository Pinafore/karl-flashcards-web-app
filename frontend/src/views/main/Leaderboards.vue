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
            v-model="searchOptions.deck_id"
            :items="decks"
            item-text="title"
            item-value="id"
            small-chips
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
          <v-card class="ml-0 mr-3 pa-3">
            <v-card-title primary-title class="pb-3 justify-center">
              <div class="headline primary--text justify-center">
                {{ filteredLeaderboard.name }}
              </div>
            </v-card-title>
            <v-data-table
              disable-pagination
              disable-filtering
              hide-default-footer
              class="mb-3 pa-1"
              :headers="filteredLeaderboard.headers"
              item-key="id"
              :loading="loading"
              :items="filteredLeaderboard.leaderboard"
            >
            </v-data-table>
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

  @Component({
    components: { ConnectionPopup },
  })
  export default class Leaderboard extends Vue {
    loading = true;
    searchOptions: IComponents["LeaderboardSearch"] = { rank_type: "total_seen" };
    startMenu = false;
    endMenu = false;

    async mounted() {
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
      await this.searchLeaderboards();
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }

    get today() {
      return mainStore.today;
    }

    get filteredLeaderboard() {
      return mainStore.filteredLeaderboard;
    }

    @Watch("searchOptions", { deep: true })
    onSearchOptionsChanged() {
      this.searchLeaderboards();
    }

    async searchLeaderboards() {
      this.loading = true;
      await mainStore.getLeaderboard(this.searchOptions);
      this.loading = false;
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
