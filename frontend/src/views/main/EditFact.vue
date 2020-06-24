<template>
  <validation-observer ref="observer" v-slot="{ invalid }">
    <form @submit.prevent="save" @reset.prevent="onReset">
      <v-card>
        <v-card-title>
          <span class="headline">{{ formTitle }}</span>
        </v-card-title>

        <v-card-text>
          <span v-if="fact">
            <!-- text -->
            <validation-provider
              v-slot="{ errors }"
              name="Text"
              :rules="{
                required: true,
              }"
            >
              <v-textarea
                v-model="fact.text"
                auto-grow
                rows="1"
                label="Text"
                :error-messages="errors[0]"
                required
              ></v-textarea>
            </validation-provider>

            <!-- answer -->
            <validation-provider v-slot="{ errors }" rules="required" name="Answer">
              <v-textarea
                v-model="fact.answer"
                auto-grow
                rows="1"
                label="Answer"
                type="answer"
                :error-messages="errors[0]"
                required
              ></v-textarea>
            </validation-provider>

            <v-select
              v-model="fact.deck_id"
              :items="decks"
              item-text="title"
              item-value="id"
              label="Choose Deck"
            >
            </v-select>

            <!-- category -->
            <validation-provider v-slot="{ errors }" name="Category">
              <v-text-field
                v-model="fact.category"
                label="Category"
                type="category"
                :error-messages="errors[0]"
              ></v-text-field>
            </validation-provider>

            <!-- identifier -->
            <validation-provider v-slot="{ errors }" name="Identifier">
              <v-text-field
                v-model="fact.identifier"
                label="Identifier"
                type="identifier"
                :error-messages="errors[0]"
              ></v-text-field>
            </validation-provider>
          </span>
          <span v-else>
            loading...
          </span>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="close">Cancel</v-btn>
          <v-btn type="reset">Reset</v-btn>
          <v-btn type="submit" :disabled="invalid" @click="save">Save</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </validation-observer>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
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
  export default class EditFact extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };

    editedIndex = -1;
    formTitle = "Edit Fact";
    fact: IComponents["Fact"] | null = null;

    async mounted() {
      this.editedIndex = Number(this.$router.currentRoute.params.id);
      this.storedFact();
      await mainStore.getUserProfile();
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      return userProfile && userProfile.decks ? userProfile.decks : [];
    }

    get facts() {
      return mainStore.facts;
    }

    @Watch("facts")
    onFactsChanged() {
      this.storedFact();
    }

    storedFact() {
      this.fact = JSON.parse(JSON.stringify(this.facts[this.editedIndex]));
    }

    onReset() {
      this.$refs.observer.reset();
      this.editedIndex = Number(this.$router.currentRoute.params.id);
      this.storedFact();
    }

    close() {
      this.$router.push({ name: "browse" });
    }

    async save() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      if (this.editedIndex > -1 && this.fact) {
        const fact_update: IComponents["FactUpdate"] = {
          text: this.fact.text,
          deck_id: this.fact.deck_id,
          answer: this.fact.answer,
          category: this.fact.category,
          identifier: this.fact.identifier,
        };
        this.close();
        await mainStore.updateFact({
          id: this.fact.fact_id,
          data: fact_update,
        });
        mainStore.updateFactInFacts({ index: this.editedIndex, fact: this.fact });
      } else {
        this.close();
      }
    }
  }
</script>
