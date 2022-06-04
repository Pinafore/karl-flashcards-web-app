<template class="pa-0 ma-0">
  <v-dialog v-model="popup" max-width="1000px" persistent>
    <v-card>
      <v-card-title>
        <h2>Study Set Finished</h2>
      </v-card-title>
      <v-card-text>
        <p>
          You've finished this study set! Would you like to create another set with the
          same settings or change options for your next study set?
        </p>
      </v-card-text>
      <v-card-actions class="pt-0">
        <v-spacer></v-spacer>
        <v-btn color="primary" ref="same" text @click="continueStudy">
          Same Settings
        </v-btn>
        <v-btn color="primary" text @click="goToDeck">
          Change Options
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
    $refs!: {
      same: HTMLInputElement;
    };
    popup = false;

    async mounted() {
      this.popup = this.isFinished;
    }

    get isFinished() {
      return (
        studyStore.studyset !== null &&
        studyStore.studyset.num_unstudied == 0 &&
        studyStore.studyset.needs_restudy != true
      );
    }

    continueStudy() {
      studyStore.getStudyFacts();
      this.popup = false;
    }

    goToDeck() {
      this.$router.push("/main/study/decks");
    }

    @Watch("isFinished")
    onIsFinishedChanged() {
      this.popup = true;
      setTimeout(() => {
        this.$refs.same.$el.focus();
      })
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
