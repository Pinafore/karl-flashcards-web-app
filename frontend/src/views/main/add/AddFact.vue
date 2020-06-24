<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Create Fact</div>
          </v-card-title>
          <v-card-text>
            <template>
              <!-- front -->
              <validation-provider
                v-slot="{ errors }"
                name="Front"
                :rules="{
                  required: true,
                }"
              >
                <v-textarea
                  v-model="front"
                  label="Front"
                  auto-grow
                  rows="1"
                  :error-messages="errors[0]"
                  required
                ></v-textarea>
              </validation-provider>

              <!-- back -->
              <validation-provider v-slot="{ errors }" rules="required" name="Back">
                <v-textarea
                  v-model="back"
                  label="Back"
                  type="back"
                  auto-grow
                  rows="1"
                  :error-messages="errors[0]"
                  required
                ></v-textarea>
              </validation-provider>

              <v-select
                v-model="deck_id"
                :items="decks"
                item-text="title"
                item-value="id"
                label="Choose Deck"
              >
              </v-select>

              <!-- category -->
              <validation-provider v-slot="{ errors }" name="Category">
                <v-text-field
                  v-model="category"
                  label="Category"
                  type="category"
                  :error-messages="errors[0]"
                ></v-text-field>
              </validation-provider>

              <!-- identifier -->
              <validation-provider v-slot="{ errors }" name="Identifier">
                <v-text-field
                  v-model="identifier"
                  label="Identifier"
                  type="identifier"
                  :error-messages="errors[0]"
                ></v-text-field>
              </validation-provider>
            </template>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn @click="cancel">Cancel</v-btn>
            <v-btn type="reset">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid">Save</v-btn>
          </v-card-actions>
        </v-card>
      </form>
    </validation-observer>
  </v-container>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { IComponents } from "@/interfaces";
  import { mainStore } from "@/store";
  import { required } from "vee-validate/dist/rules";
  import { ValidationProvider, ValidationObserver, extend } from "vee-validate";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class CreateFact extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };

    front = "";
    back = "";
    category = "";
    identifier = "";
    deck_id = 1;

    async mounted() {
      await mainStore.getUserProfile();
      const userProfile = mainStore.userProfile;
      if (userProfile && userProfile.default_deck) {
        this.deck_id = userProfile.default_deck.id;
      }
      this.onReset();
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }

    onReset() {
      this.$refs.observer.reset();

      this.front = "";
      this.back = "";
      this.identifier = "";
      this.category = "";
      const userProfile = mainStore.userProfile;
      if (userProfile && userProfile.default_deck) {
        this.deck_id = userProfile.default_deck.id;
      }
    }

    cancel() {
      this.$router.back();
    }

    async onSubmit() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      const fact: IComponents["FactCreate"] = {
        text: this.front,
        deck_id: this.deck_id,
        answer: this.back,
        category: this.category,
        identifier: this.identifier,
        answer_lines: [this.back],
        extra: { type: "user created" },
      };
      await mainStore.createFact(fact);
      this.front = "";
      this.back = "";
      this.identifier = "";
      this.category = "";
      this.$refs.observer.reset();
    }
  }
</script>
