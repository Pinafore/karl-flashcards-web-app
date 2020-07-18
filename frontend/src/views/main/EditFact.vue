<template>
  <validation-observer ref="observer" v-slot="{ invalid }">
    <v-card v-if="oldReport">
      <v-card-title>
        <span class="headline primary--text">Pending Report</span>
      </v-card-title>
      <v-card-text>
        Your current report is shown below with suggested changes. You can clear the
        report if you no longer believe there are errors or submit a new report
        overriding the previous report if you spot more errors.
        <v-textarea
          v-show="oldReport.text != null"
          v-model="oldReport.text"
          readonly
          auto-grow
          rows="1"
          label="Text"
        ></v-textarea>

        <v-textarea
          v-show="oldReport.answer != null"
          v-model="oldReport.answer"
          auto-grow
          rows="1"
          label="Answer"
          type="answer"
          readonly
        ></v-textarea>

        <v-select
          v-show="oldReport.deck_id != null"
          v-model="oldReport.deck_id"
          :items="decks"
          item-text="title"
          item-value="id"
          label="Choose Deck"
          readonly
        >
        </v-select>

        <v-text-field
          v-show="oldReport.category != null"
          v-model="oldReport.category"
          label="Category"
          type="category"
          readonly
        ></v-text-field>

        <!-- identifier -->
        <v-text-field
          v-show="oldReport.identifier != null"
          v-model="oldReport.identifier"
          label="Identifier"
          type="identifier"
          readonly
        ></v-text-field>
      </v-card-text>
    </v-card>
    <v-card v-if="reports">
      <v-card-title>
        <span class="headline primary--text">Pending Reports</span>
      </v-card-title>
      <v-card-text>
        <!-- eslint-disable-next-line vue/require-v-for-key -->
        <div v-for="report in reports" :key="report.report_id" class="mt-4">
          <v-card class="pa-4">
            <v-textarea
              v-show="report.text !== null"
              v-model="report.text"
              auto-grow
              rows="1"
              label="Text"
            ></v-textarea>
            <v-textarea
              v-show="report.answer !== null"
              v-model="report.answer"
              auto-grow
              rows="1"
              label="Answer"
              type="answer"
            ></v-textarea>
            <v-select
              v-show="report.deck_id !== null"
              v-model="report.deck_id"
              :items="decks"
              item-text="title"
              item-value="id"
              label="Choose Deck"
            >
            </v-select>
            <v-text-field
              v-show="report.category !== null"
              v-model="report.category"
              label="Category"
              type="category"
            ></v-text-field>
            <v-text-field
              v-show="report.identifier !== null"
              v-model="report.identifier"
              label="Identifier"
              type="identifier"
            ></v-text-field>
            <v-btn @click="acceptReport(report)">Accept Changes</v-btn>
          </v-card>
        </div>
      </v-card-text>
    </v-card>
    <form @submit.prevent="save" @reset.prevent="onReset">
      <v-card>
        <v-card-title>
          <span class="headline">{{ formTitle }}</span>
        </v-card-title>
        <v-card-text>
          <div v-if="formTitle === 'Report Fact'">
            Reported facts will not be shown to you again until the owner resolves the
            report. While optional, it would be helpful if you could suggest changes to
            the reported fact below.
          </div>
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
          <v-btn @click="close">{{ cancel }}</v-btn>
          <v-btn v-show="showClearReport()" @click="clearReport">Discard Report</v-btn>
          <v-btn type="reset"> {{ reset }}</v-btn>
          <v-btn type="submit" :disabled="invalid">{{ saveMsg }}</v-btn>
        </v-card-actions>
      </v-card>
    </form>
  </validation-observer>
</template>

<script lang="ts">
  import { Component, Vue, Watch } from "vue-property-decorator";
  import { IComponents } from "@/interfaces";
  import { mainStore, studyStore } from "@/store";
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
    routeName = "learn-edit";
    fact: IComponents["Fact"] | null = null;
    originalFact: IComponents["Fact"] | null = null;
    cancel = "Cancel";
    reset = "Reset";
    saveMsg = "Save";
    oldReport: IComponents["FactReported"] | null = null;
    reports: IComponents["FactReported"][] | null = null;

    async mounted() {
      await mainStore.getUserProfile();
    }

    public beforeRouteEnter(to, from, next) {
      next((vm) => {
        vm.routeName = to.name;
        vm.determineRoute();
        vm.setEditedIndex();
        vm.storedFact();
      });
    }

    public async beforeRouteUpdate(to, from, next) {
      this.routeName = to.name;
      await this.determineRoute();
      this.setEditedIndex();
      this.storedFact();
      next();
    }

    async determineRoute() {
      if (this.routeName == "learn-edit" || this.routeName == "browse-edit") {
        this.formTitle = "Edit Fact";
        this.cancel = "Cancel";
        this.reset = "Reset";
        this.saveMsg = "Save";
      } else if (this.routeName == "browse-resolve") {
        this.formTitle = "Reported Fact";
        this.cancel = "Close";
        this.saveMsg = "Resolve";
      } else {
        this.formTitle = "Report Fact";
        this.cancel = "Cancel";
        this.reset = "Reset";
        this.saveMsg = "Report";
        await mainStore.getPublicDecks();
      }
    }

    showClearReport() {
      return (
        this.routeName === "browse-resolve" ||
        (this.routeName === "browse-report" && this.oldReport !== null)
      );
    }

    setEditedIndex() {
      if (this.routeName.startsWith("learn")) {
        this.editedIndex = 0;
      } else {
        this.editedIndex = Number(this.$router.currentRoute.params.id);
      }
    }

    get decks() {
      const userProfile = mainStore.userProfile;
      const decks = userProfile && userProfile.decks ? userProfile.decks : [];
      if (this.routeName.endsWith("report")) {
        decks.push(...mainStore.publicDecks);
      }
      return decks;
    }

    get facts() {
      if (this.routeName.startsWith("learn")) {
        return [studyStore.show.fact];
      } else {
        return mainStore.facts;
      }
    }

    @Watch("facts")
    onFactsChanged() {
      this.storedFact();
    }

    storedFact() {
      if (this.facts[this.editedIndex] !== undefined) {
        if (
          this.routeName == "browse-report" &&
          this.facts[this.editedIndex]?.reports?.[0] !== undefined
        ) {
          this.oldReport = JSON.parse(
            JSON.stringify(this.facts[this.editedIndex]?.reports?.[0]),
          );
          if (this.oldReport !== null) {
            this.saveMsg = "Override Report";
          }
        } else if (this.routeName == "browse-resolve") {
          this.reports = JSON.parse(
            JSON.stringify(this.facts[this.editedIndex]?.reports),
          );
        }
        this.fact = JSON.parse(JSON.stringify(this.facts[this.editedIndex]));
        this.originalFact = JSON.parse(JSON.stringify(this.facts[this.editedIndex]));
      } else {
        this.fact = null;
        this.originalFact = null;
      }
    }

    onReset() {
      this.$refs.observer.reset();
      this.setEditedIndex();
      this.storedFact();
    }

    close() {
      this.$router.back();
    }

    async acceptReport(report) {
      if (this.reports && this.originalFact && this.fact) {
        if (report.text) this.fact.text = report.text;
        if (report.deck_id) this.fact.deck_id = report.deck_id;
        if (report.answer) this.fact.answer = report.answer;
        if (report.category) this.fact.category = report.category;
        if (report.identifier) this.fact.identifier = report.identifier;
        this.reports = this.reports.filter((obj) => obj !== report);
      }
    }

    async clearReport() {
      this.wipeReport();
      this.close();
    }

    async wipeReport() {
      if (this.fact && this.facts[this.editedIndex] !== undefined) {
        if (this.routeName == "browse-resolve") {
          await mainStore.clearReportsFact({ id: this.fact.fact_id });
        } else {
          await mainStore.clearReportFact({ id: this.fact.fact_id });
        }
        this.facts[this.editedIndex]!.reports = [];
      }
    }
    async save() {
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      this.close();
      if (this.editedIndex > -1 && this.fact && this.originalFact) {
        const fact_update: IComponents["FactUpdate"] | IComponents["FactToReport"] = {};
        if (this.fact.text !== this.originalFact.text)
          fact_update.text = this.fact.text;
        if (this.fact.deck_id !== this.originalFact.deck_id)
          fact_update.deck_id = this.fact.deck_id;
        if (this.fact.answer !== this.originalFact.answer)
          fact_update.answer = this.fact.answer;
        if (this.fact.category !== this.originalFact.category)
          fact_update.category = this.fact.category;
        if (this.fact.identifier !== this.originalFact.identifier)
          fact_update.identifier = this.fact.identifier;
        if (this.routeName == "learn-edit") {
          await studyStore.editFact(fact_update);
        } else if (this.routeName == "browse-edit") {
          await mainStore.updateFact({
            id: this.fact.fact_id,
            data: fact_update,
          });
          mainStore.updateFactInFacts({ index: this.editedIndex, fact: this.fact });
        } else if (this.routeName == "browse-report") {
          await mainStore.reportFact({
            id: this.fact.fact_id,
            data: fact_update,
          });
          if (this.facts[this.editedIndex] !== undefined) {
            this.facts[this.editedIndex]!.reports = [fact_update];
          }
        } else if (this.routeName == "browse-resolve") {
          await mainStore.updateFact({
            id: this.fact.fact_id,
            data: fact_update,
          });
          mainStore.updateFactInFacts({ index: this.editedIndex, fact: this.fact });
          await this.wipeReport();
        } else if (this.routeName == "learn-report") {
          await studyStore.reportFact(fact_update);
        }
      }
    }
  }
</script>
