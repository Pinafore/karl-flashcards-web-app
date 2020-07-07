<template>
  <v-container fluid>
    <connection-popup></connection-popup>
    <v-card class="ma-3 mb-0 pa-3">
      <v-row no-gutters>
        <v-col>
          <v-card-title primary-title>
            <div class="headline primary--text">Statistics</div>
          </v-card-title>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="pt-0">
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
              <v-row>
                <v-col
                  v-for="item in props.items"
                  :key="item.name"
                  cols="12"
                  lg="4"
                  md="6"
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
        </v-col>
      </v-row>
    </v-card>
    <v-card class="ma-3 mb-0 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Filter Statistics</div>
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
      <v-row v-if="filteredStat">
        <v-col>
          <v-card>
            <v-card-title class="subheading font-weight-medium justify-center">{{
              filteredStat.name
            }}</v-card-title>
            <v-divider></v-divider>
            <v-list dense>
              <v-list-item v-for="type in types" :key="type.value" class="pa-2">
                <v-row no-gutters align="end">
                  <v-col cols="9">
                    <v-list-item-content>{{ type.text }} </v-list-item-content>
                  </v-col>
                  <v-col cols="3">
                    <v-list-item-content>{{
                      filteredStat[type.value]
                    }}</v-list-item-content>
                  </v-col>
                </v-row>
              </v-list-item>
            </v-list>
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
  export default class Statistics extends Vue {
    loading = true;
    searchOptions: IComponents["StatSearch"] = {};
    startMenu = false;
    endMenu = false;

    async mounted() {
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
      await this.savedStatistics();
      await this.searchStatistic();
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }

    get today() {
      return mainStore.today;
    }

    get filteredStat() {
      return mainStore.filteredStat;
    }

    get stats() {
      return mainStore.savedStats;
    }

    get types() {
      return mainStore.types;
    }

    @Watch("searchOptions", { deep: true })
    onSearchOptionsChanged() {
      this.searchStatistic();
    }

    async searchStatistic() {
      this.loading = true;
      await mainStore.getStatistic(this.searchOptions);
      this.loading = false;
    }

    async savedStatistics() {
      this.loading = true;
      await mainStore.getSavedStatistics();
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
