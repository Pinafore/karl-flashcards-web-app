<template>
  <div>
    <Onboard></Onboard>
    <test-popup :should-show="true"></test-popup>
    <!-- <RecallPopup></RecallPopup> -->
    <v-toolbar style="position: sticky; top: 0; z-index: 10;">
      <v-toolbar-title>
        New Study Set
        <span v-show="resumeAvail" style="margin-left: .5em">
          (Overrides Current Study Set!!)
        </span>
      </v-toolbar-title>
      <v-spacer class="hidden-xs-only"></v-spacer>

      <v-card-actions class="px-0 px-sm-auto">
        <v-btn v-show="!checkAllDecks()" @click="deleteDecks">Delete</v-btn>
        <v-btn to="/main/add/deck">Add Deck</v-btn>
        <v-btn v-if="checkAllDecks()" @click="openAll()">Study All</v-btn>
        <v-btn v-else color="primary" @click="openDecks()"
          >Study<span class="hidden-xs-only"> Selected</span></v-btn
        >
      </v-card-actions>
    </v-toolbar>
    <v-card flat>
      <v-card-text style="padding-bottom: 0px">
        <p class="subheading">
          Max Facts (Create a new study set after completion if you wish to keep
          studying):
        </p>
        <v-radio-group v-model="selectedNum" row>
          <v-radio
            v-for="num in studyNumOptions"
            :key="num"
            :label="`${num} Facts`"
            :value="num"
          >
          </v-radio>
        </v-radio-group>
      </v-card-text>
    </v-card>
    <v-data-table
      v-model="selected"
      :headers="headers"
      item-key="id"
      :items="decks"
      :items-per-page="15"
      :style="{ cursor: 'pointer' }"
      show-select
    >
      <template v-slot:header.data-table-select>
        <v-simple-checkbox
          :value="areAllSelectedExceptMnemonic()"
          @input="toggleAllExceptMnemonic"
        ></v-simple-checkbox>
      </template>

      <template v-slot:item="{ item }">
        <tr @click="openDeck(item)">
          <td>
            <v-simple-checkbox
              v-ripple
              :value="isSelected(item)"
              @input="updateSelection(item)"
            ></v-simple-checkbox>
          </td>
          <td>
            {{ item.title }}
            <v-tooltip color="#302f2f" right v-if="item.deck_type == 'public_mnemonic'">
              <template v-slot:activator="{ on, attrs }">
                <v-icon medium class="ml-0 mb-1" v-bind="attrs" v-on="on" color="#e0b310"
                  >mdi-alert</v-icon
                >
              </template>
              <span>This deck contains automatically generated mnemonic devices from a large language model, and can only be studied on its own!</span>
            </v-tooltip>
          </td>
        </tr>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/utils/store-accessor";
  import { IComponents } from "@/interfaces";
  import Onboard from "@/views/Onboard.vue";
  import TestPopup from "@/views/main/TestPopup.vue";

  @Component({
    components: { TestPopup, Onboard },
  })
  export default class Decks extends Vue {
    public headers = [
      {
        text: "Deck",
        sortable: true,
        value: "title",
        align: "left",
      },
    ];
    selected: IComponents["Deck"][] = [];
    studyNumOptions: number[] = [5, 10, 20, 30, 50];
    selectedNum = 20;

    async mounted() {
      studyStore.setStudySet(null);
      await mainStore.getUserProfile();
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
      await studyStore.checkIfInTestMode();
    }

    get decks() {
      if (!mainStore.userProfile || !mainStore.userProfile.decks) {
        return [];
      }
      return mainStore.userProfile.decks.map((i) =>
        i.deck_type == "public_mnemonic"
          ? {
              title: i.title,
              id: i.id,
              public: i.public,
              deck_type: i.deck_type,
            }
          : i,
      );
    }

    get resumeAvail() {
      return mainStore.userProfile && mainStore.userProfile.study_set_expiry_date;
    }

    public checkAllDecks() {
      return this.selected.length == 0 || this.selected.length == this.decks.length;
    }

    public areAllSelectedExceptMnemonic() {
      return this.decks
        .filter((i) => i.deck_type !== "public_mnemonic")
        .every((i) => this.selected.map((j) => j.title).includes(i.title));
    }

    public toggleAllExceptMnemonic() {
      if (this.areAllSelectedExceptMnemonic()) {
        this.selected = [];
      } else {
        this.selected = this.decks.filter((i) => i.deck_type !== "public_mnemonic");
      }
    }

    public isMnemonicDeck(i) {
      return i.deck_type == "public_menmonic";
    }

    public isSelected(id) {
      return this.selected.includes(id);
    }

    public updateSelection(id) {
      if (id.deck_type == "public_mnemonic") {
        if (this.isSelected(id)) {
          this.selected = [];
        } else {
          this.selected = [id];
        }
      } else {
        const specialIndex = this.selected
          .map((i) => i.deck_type)
          .indexOf("public_mnemonic");
        if (specialIndex !== -1) {
          this.selected.splice(specialIndex, 1);
        }
        const index = this.selected.indexOf(id);
        if (index == -1) {
          this.selected.push(id);
        } else {
          this.selected.splice(index, 1);
        }
      }
    }

    public openDecks() {
      // Vue router takes in arrays only as strings
      const selectedIds = this.selected.map((a) => String(a.id));
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn?show_test_mode=true",
        query: { deck: selectedIds, num: String(this.selectedNum) },
      });
    }

    public openDeck(deck) {
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn?show_test_mode=true",
        query: { deck: String(deck.id), num: String(this.selectedNum) },
      });
    }

    public openAll() {
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn?show_test_mode=true",
      });
    }

    public async deleteDecks() {
      const selectedIds = this.selected.map((a) => a.id);
      if (selectedIds.length > 0) {
        await mainStore.deleteDecks({ ids: selectedIds });
        this.selected = [];
        await mainStore.getUserProfile();
      }
    }
  }
</script>
