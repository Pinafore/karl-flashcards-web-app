<template>
  <div>
    <Onboard></Onboard>
    <RecallPopup></RecallPopup>
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
      @click:row="openDeck"
    >

    <template v-slot:header.data-table-select>
      <v-simple-checkbox
        :value="areAllSelectedExceptVocab()"
        @input="toggleAllExceptVocab"
      ></v-simple-checkbox>
    </template>
    
    <template v-slot:item.data-table-select="{item}">
      <v-simple-checkbox
        v-ripple
        :value="isSelected(item)"
        @input="updateSelection(item)"
      ></v-simple-checkbox>
    </template>


    </v-data-table>
  </div>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/utils/store-accessor";
  import { IComponents } from "@/interfaces";
  import Onboard from "@/views/Onboard.vue";
  import RecallPopup from "@/views/main/RecallPopup.vue";
import UserProfile from "../profile/UserProfile.vue";

  @Component({
    components: { RecallPopup, Onboard },
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
    vocabIdentifier = process.env.VUE_APP_VOCAB_DECK + " (Can only be studied on its own!)";

    async mounted() {
      studyStore.setInTestMode(false);
      await mainStore.getUserProfile();
    }

    get decks() {
      if (!mainStore.userProfile || !mainStore.userProfile.decks) {
        return []
      }
      return mainStore.userProfile.decks.map(i => (this.vocabIdentifier.includes(i.title) ? {'title': i.title + " (Can only be studied on its own!)", 'id': i.id, 'public': i.public} : i))
    }

    get resumeAvail() {
      return mainStore.userProfile && mainStore.userProfile.study_set_expiry_date;
    }

    public checkAllDecks() {
      return this.selected.length == 0 || this.selected.length == this.decks.length;
    }

    public areAllSelectedExceptVocab() {
      return this.decks.filter(i => i.title !== this.vocabIdentifier).every(i => this.selected.map(j => j.title).includes(i.title));
    }

    public toggleAllExceptVocab() {
      if (this.areAllSelectedExceptVocab()) {
        this.selected = [];
      } else {
        this.selected = this.decks.filter(i => i.title !== this.vocabIdentifier);
      }
    }

    public isSelected(id) {
      return this.selected.includes(id);
    };
    
    public updateSelection(id) {
      if (id.title === this.vocabIdentifier) {
        if (this.isSelected(id)) {
          this.selected = [];
        } else {
          this.selected = [id];
        }
      } else {
        const specialIndex = this.selected.map(i => i.title).indexOf(this.vocabIdentifier);
        if (specialIndex !== -1) {
          this.selected.splice(specialIndex, 1)
        }
        const index = this.selected.indexOf(id);
    if (index === -1) {
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
        path: "/main/study/learn",
        query: { deck: selectedIds, num: String(this.selectedNum) },
      });
    }

    public openDeck(deck) {
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn",
        query: { deck: String(deck.id), num: String(this.selectedNum) },
      });
    }

    public openAll() {
      studyStore.setForceNew(true);
      this.$router.push({
        path: "/main/study/learn",
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
