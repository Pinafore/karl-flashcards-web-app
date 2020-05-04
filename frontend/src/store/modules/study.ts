import { api } from "@/api";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";
import { IComponents } from "@/interfaces";
import { mainStore } from "@/utils/store-accessor";

@Module({ name: "study" })
export default class StudyModule extends VuexModule {
  facts: IComponents["Fact"][] = [];

  @Mutation
  setFacts(payload: IComponents["Fact"][]) {
    this.facts = payload;
  }

  @Action
  async getFacts(deckIds: number[]) {
    try {
      const response = await api.getStudyFacts(mainStore.token, deckIds);
      if (response) {
        this.setFacts(response.data);
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }
}
