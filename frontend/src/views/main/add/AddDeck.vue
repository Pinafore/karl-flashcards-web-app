<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <v-card class="ma-3 pa-3">
        <v-card-title primary-title>
          <div class="headline primary--text">Add Deck</div>
        </v-card-title>
        <v-card-text>
          <template>
            <validation-provider
              v-slot="{ errors }"
              name="Deck name"
              :rules="{
                required: true,
                excluded: deckTitles,
              }"
            >
              <v-text-field
                ref="title"
                v-model="title"
                label="Deck Name"
                required
                :error-messages="errors"
              ></v-text-field>
            </validation-provider>
          </template>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="cancel">Back</v-btn>
          <v-btn @click="onReset">Reset</v-btn>
          <v-btn :disabled="invalid" @click="onSubmit">
            Add
          </v-btn>
        </v-card-actions>
      </v-card>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { extend, ValidationObserver, ValidationProvider } from "vee-validate";
  import { mainStore } from "@/utils/store-accessor";
  import { excluded, required } from "vee-validate/dist/rules";

  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("excluded", {
    ...excluded,
    message: "You already have a deck with this name.",
  });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class CreateNewDeck extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
      title: HTMLInputElement;
    };
    public title = "";

    public async mounted() {
      this.onReset();
    }

    get deckTitles() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks
        ? userProfile.decks.map((a) => String(a.title))
        : [];
    }

    onReset() {
      this.title = "";
      this.$refs.observer.reset();
      this.$nextTick(() => {
        this.$refs.title.focus();
      });
    }

    public cancel() {
      this.$router.back();
    }

    async onSubmit() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      await mainStore.createDeck({
        title: this.title,
      });
      this.onReset();
    }
  }
</script>
