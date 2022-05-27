<template class="pa-0 ma-0">
  <v-dialog v-model="popup" max-width="1000px" persistent @click:outside="startTesting">
    <v-card>
      <v-card-title>
        <h2>Old Study Set Found</h2>
      </v-card-title>
      <v-card-text>
        <p>
          It looks like you didn't finish your last study set. Would you like to study
          that one?
        </p>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn color="primary" text @click="startTesting">
          Begin
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { mainStore, studyStore } from "@/store";

  @Component
  export default class StudySet extends Vue {
    popup = false;

    async mounted() {
      this.popup = this.inTestMode;
    }

    get inTestMode() {
      return studyStore.inTestMode;
    }

    @Watch("inTestMode")
    onIsTestModeChanged() {
      this.popup = true;
    }

    startTesting() {
      this.popup = false;
    }
  }
</script>

<!--<style></style>-->

<!--<template>-->
<!--  <div>-->
<!--    <Onboard></Onboard>-->
<!--    <RecallPopup></RecallPopup>-->
<!--    <v-toolbar style="position: sticky; top: 0; z-index: 10;">-->
<!--      <v-toolbar-title>-->
<!--        Study Set Options-->
<!--      </v-toolbar-title>-->
<!--      <v-spacer class="hidden-xs-only"></v-spacer>-->

<!--      <v-card-actions class="px-0 px-sm-auto">-->
<!--        <v-btn v-show="!checkAllDecks()" @click="deleteDecks">Delete</v-btn>-->
<!--        <v-btn to="/main/add/deck">Add Deck</v-btn>-->
<!--        <v-btn v-if="checkAllDecks()" to="/main/study/learn">Study All</v-btn>-->
<!--        <v-btn v-else color="primary" @click="openDecks()"-->
<!--          >Study<span class="hidden-xs-only"> Selected</span></v-btn-->
<!--        >-->
<!--      </v-card-actions>-->
<!--    </v-toolbar>-->
<!--    <v-data-table-->
<!--      v-model="selected"-->
<!--      :headers="headers"-->
<!--      item-key="id"-->
<!--      :items="decks"-->
<!--      :items-per-page="15"-->
<!--      show-select-->
<!--      :style="{ cursor: 'pointer' }"-->
<!--      @click:row="openDeck"-->
<!--    >-->
<!--    </v-data-table>-->
<!--  </div>-->
<!--</template>-->

<!--<script lang="ts">-->
<!--  import { Component, Vue } from "vue-property-decorator";-->
<!--  import { mainStore } from "@/utils/store-accessor";-->
<!--  import { IComponents } from "@/interfaces";-->
<!--  import Onboard from "@/views/Onboard.vue";-->
<!--  import RecallPopup from "@/views/main/RecallPopup.vue";-->

<!--  @Component({-->
<!--    components: { RecallPopup, Onboard },-->
<!--  })-->
<!--  export default class Decks extends Vue {-->
<!--    public headers = [-->
<!--      {-->
<!--        text: "Deck",-->
<!--        sortable: true,-->
<!--        value: "title",-->
<!--        align: "left",-->
<!--      },-->
<!--    ];-->
<!--    selected: IComponents["Deck"][] = [];-->

<!--    async mounted() {-->
<!--      await mainStore.getUserProfile();-->
<!--    }-->

<!--    get decks() {-->
<!--      const userProfile = mainStore.userProfile;-->
<!--      return userProfile && userProfile.decks ? userProfile.decks : [];-->
<!--    }-->

<!--    public checkAllDecks() {-->
<!--      return this.selected.length == 0 || this.selected.length == this.decks.length;-->
<!--    }-->

<!--    public openDecks() {-->
<!--      // Vue router takes in arrays only as strings-->
<!--      const selectedIds = this.selected.map((a) => String(a.id));-->
<!--      this.$router.push({-->
<!--        path: "/main/study/learn",-->
<!--        query: { deck: selectedIds },-->
<!--      });-->
<!--    }-->

<!--    public openDeck(deck) {-->
<!--      this.$router.push({-->
<!--        path: "/main/study/learn",-->
<!--        query: { deck: String(deck.id) },-->
<!--      });-->
<!--    }-->

<!--    public async deleteDecks() {-->
<!--      const selectedIds = this.selected.map((a) => a.id);-->
<!--      if (selectedIds.length > 0) {-->
<!--        await mainStore.deleteDecks({ ids: selectedIds });-->
<!--        this.selected = [];-->
<!--        await mainStore.getUserProfile();-->
<!--      }-->
<!--    }-->
<!--  }-->
<!--</script>-->