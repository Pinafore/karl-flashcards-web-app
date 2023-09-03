<template>
  <v-container fluid>
    <validation-observer ref="observer" v-slot="{ invalid }">
      <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="ma-3 pa-3">
          <v-card-title primary-title>
            <div class="headline primary--text">Upload Fact</div>
          </v-card-title>
          <v-card-text>
            <p>
              KAR³L can import txt/tsv/csv files exported from other flashcard apps and
              allows you to map columns to different fields.
              <br />
              <b>Note</b>: Facts added to public decks are NOT shared to other users and
              remain private.
              <br />
              <b>Warning</b>: Import may silently fail and stop if an unexpected error
              is encountered. Contact us if you believe this has occurred.
            </p>
            <p>
              <b>From Anki</b>: Export -> Export Format: Card in Plain Text (*.txt). Do
              not include HTML and media references
              <br />
              <b>From Mnemosyne</b>: Export -> File format: Tab-separated text files
            </p>

            <template>
              <validation-provider
                v-slot="{ errors }"
                name="File Input"
                :rules="{
                  required: true,
                }"
              >
                <v-file-input
                  v-model="file"
                  accept="text/csv, text/plain"
                  label="Select File"
                  :error-messages="errors[0]"
                  required
                  @change="validate($event)"
                ></v-file-input>
              </validation-provider>

              <validation-provider
                v-slot="{ errors }"
                name="Headers"
                :rules="{
                  required: true,
                }"
              >
                <v-select
                  v-model="selectedHeaders"
                  :items="headers"
                  multiple
                  chips
                  deletable-chips
                  :error-messages="errors[0]"
                  label="Column Headers"
                  hint="Order of selection matters. To reorder, uncheck and check in the right order."
                  persistent-hint
                >
                </v-select>
              </validation-provider>
              <v-select
                v-model="deck_id"
                :items="decks"
                item-text="title"
                item-value="id"
                label="Choose Default Deck"
                hint="Assign facts to this deck when no deck is specified in a column"
                persistent-hint
              >
              </v-select>
              <validation-provider v-slot="{ errors }" name="Delimeter">
                <v-text-field
                  v-model="delimeter"
                  label="Field Separator"
                  hint="By default, columns are separated by a tab. Specify a custom delimeter here (e.g ,)"
                  persistent-hint
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
  import { Field, IComponents } from "@/interfaces";
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

    deck_id = 1;
    delimeter = "";
    file: File | null = null;
    headers: Field[] = [
      Field.text,
      Field.answer,
      Field.deck,
      Field.identifier,
      Field.category,
    ];
    selectedHeaders: Field[] = [Field.text, Field.answer];

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

      this.selectedHeaders = [Field.text, Field.answer];
      this.file = null;
      this.delimeter = "";
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

      if (!success || this.file === null) {
        return;
      }

      const fact: IComponents["FactUpload"] = {
        headers: this.selectedHeaders,
        deck_id: this.deck_id,
        upload_file: this.file,
      };
      if (this.delimeter !== "") {
        fact.delimeter = this.delimeter;
      }
      await mainStore.uploadFacts(fact);
      this.onReset();
    }
  }
</script>
