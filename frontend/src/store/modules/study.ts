import { api } from "@/api";
import { Action, Module, Mutation, VuexModule } from "vuex-module-decorators";
import { IComponents, IStudyShow, Permission } from "@/interfaces";
import { mainStore, studyStore } from "@/utils/store-accessor";
import router from "@/router";

@Module({ name: "study" })
export default class StudyModule extends VuexModule {
  study: IComponents["Fact"][] = [];
  studyset: IComponents["StudySet"] | null = null;
  deckIds: number[] | null = null;
  schedule: IComponents["Schedule"][] = [];
  recommendation = false;
  show: IStudyShow = {
    text: "Loading...",
    enable_report: false,
    enable_actions: false,
    marked: false,
  };
  frontTime = 0;
  time = 0;
  timer: NodeJS.Timeout | undefined = undefined;
  backTime = 0;
  inTestMode = false;

  @Mutation
  setDeckIds(payload) {
    this.deckIds = payload;
  }

  @Mutation
  addToSchedule(payload) {
    this.schedule.push(payload);
  }

  @Mutation
  emptySchedule() {
    this.schedule = [];
  }

  @Mutation
  updateUnstudied() {
    if (this.studyset) {
      this.studyset.num_unstudied -= 1;
    }
  }

  @Mutation
  setRecommendation(payload: boolean) {
    this.recommendation = payload;
  }

  @Mutation
  setShow(payload: IComponents["Fact"]) {
    this.show = {
      text: payload.text,
      fact: payload,
      enable_report: payload.permission === Permission.owner,
      enable_actions: true,
      marked: payload.marked ?? false,
    };
  }

  @Mutation
  setShowLoading() {
    this.show = {
      text: "Loading...",
      enable_report: false,
      enable_actions: false,
      marked: false,
    };
  }

  @Mutation
  setShowEmpty() {
    this.show = {
      text: "You have finished studying these decks for now, check back in later!",
      enable_report: false,
      enable_actions: false,
      marked: false,
    };
  }

  @Mutation
  setShowError() {
    this.show = {
      text: "A problem occurred, please check back in later!",
      enable_report: false,
      enable_actions: false,
      marked: false,
    };
  }

  @Mutation
  setStudy(payload: IComponents["Fact"][]) {
    this.study = payload;
  }

  @Mutation
  setStudySet(payload: IComponents["StudySet"]) {
    this.studyset = payload;
  }

  @Mutation
  editShowFact(payload: IComponents["FactUpdate"]) {
    if (payload.text) {
      this.show.text = payload.text;
    }
    if (payload.answer && this.show.fact) {
      this.show.fact.answer = payload.answer;
    }
    if (payload.category && this.show.fact) {
      this.show.fact.category = payload.category;
    }
    if (payload.identifier && this.show.fact) {
      this.show.fact.identifier = payload.identifier;
    }
  }

  @Mutation
  removeFirstFact() {
    this.study.shift();
    if (this.studyset) {
      this.studyset.unstudied_facts.shift();
    }
  }

  @Mutation
  loading() {
    this.show = {
      text: "loading",
      enable_report: false,
      enable_actions: false,
      marked: false,
    };
  }

  @Mutation
  updateTimer() {
    this.time += 250;
  }

  @Mutation
  clearTime() {
    this.time = 0;
  }

  @Mutation
  setIsTestMode(payload: boolean) {
    this.inTestMode = payload;
  }

  @Action
  clearTimer() {
    if (this.timer) {
      clearInterval(this.timer);
    }
    this.clearTime();
  }

  @Action
  pauseTimer() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }

  @Action
  startTimer() {
    if (this.timer) {
      clearInterval(this.timer);
    }
    this.timer = setInterval(() => {
      if (this.time < 30000) {
        this.updateTimer();
      }
    }, 250);
  }

  @Mutation
  markFrontTime() {
    this.frontTime = this.time;
  }

  @Mutation
  markBackTime() {
    this.backTime = this.time;
  }

  @Mutation
  changeMarked() {
    this.show.marked = !this.show.marked;
  }

  @Action
  async getNextShow() {
    this.clearTimer();
    if (this.studyset && this.studyset.unstudied_facts.length > 0) {
      this.setShow(this.studyset.unstudied_facts[0]);
      this.startTimer();
      this.removeFirstFact();
    } else {
      await this.getStudyFacts();
    }
  }

  @Action
  async getStudyFacts() {
    this.clearTimer();
    try {
      this.setShowLoading();
      const response = await api.getStudyFacts(mainStore.token, this.deckIds ?? []);
      console.log(response.data);
      if (response.data.unstudied_facts.length == 0) {
        this.setShowEmpty();
        this.setStudy([]);
      } else {
        this.setStudySet(response.data);
        this.setStudy(response.data.unstudied_facts);
        console.log(response.data.is_test);
        this.setIsTestMode(response.data.is_test);
        await this.getNextShow();
      }
      mainStore.setConnectionError(false);
      mainStore.setSchedulerError(false);
    } catch (error) {
      console.log(error);
      await mainStore.checkApiError(error);
      this.setShowError();
    }
  }

  @Action
  async markFact() {
    if (this.show.fact && this.show.enable_actions) {
      try {
        await api.markFact(mainStore.token, this.show.fact.fact_id);
        mainStore.addNotification({
          content: "Fact marked/unmarked",
          color: "success",
        });
        this.changeMarked();
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async suspendFact() {
    this.clearTimer();
    if (this.show.fact && this.show.enable_actions) {
      try {
        await api.suspendFact(mainStore.token, this.show.fact.fact_id);
        mainStore.addNotification({
          content: "Fact suspended",
          color: "success",
        });
        await this.getNextShow();
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async reportFact(payload: IComponents["FactUpdate"]) {
    this.clearTimer();
    if (this.show.fact && this.show.enable_report) {
      try {
        await api.reportFact(mainStore.token, this.show.fact.fact_id, payload);
        mainStore.addNotification({
          content: "Fact reported",
          color: "success",
        });
        await this.getNextShow();
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async editFact(payload: IComponents["FactUpdate"]) {
    this.clearTimer();
    if (this.show.fact && !this.show.enable_report) {
      try {
        await api.updateFact(mainStore.token, this.show.fact.fact_id, payload);
        mainStore.addNotification({
          content: "Fact edited",
          color: "success",
        });
        this.editShowFact(payload);
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async editFactDialog() {
    this.pauseTimer();
    if (this.show.fact && !this.show.enable_report) {
      try {
        if (router.currentRoute.name == "learn") {
          router.push({ name: "learn-edit" });
        } else {
          router.back();
        }
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async reportFactDialog() {
    this.pauseTimer();
    if (this.show.fact && this.show.enable_report) {
      try {
        if (router.currentRoute.name == "learn") {
          router.push({ name: "learn-report" });
        } else {
          router.back();
        }
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async deleteFact() {
    this.clearTimer();
    if (this.show.fact && this.show.enable_actions) {
      try {
        mainStore.addNotification({
          content: "Fact deleted",
          color: "success",
        });
        await api.deleteFact(mainStore.token, this.show.fact.fact_id);
        await this.getNextShow();
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async evaluateAnswer(typed: string) {
    if (this.show.fact && this.show.enable_actions) {
      try {
        this.markFrontTime();
        this.clearTimer();
        const response = await api.evalAnswer(
          mainStore.token,
          this.show.fact.fact_id,
          typed,
        );
        this.setRecommendation(response.data);
        this.startTimer();
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    }
  }

  @Action
  async updateSchedule() {
    if (this.show.fact && this.show.enable_actions && this.studyset) {
      try {
        this.setShowLoading();
        await api.updateSchedule(mainStore.token, this.studyset.id, this.schedule);
        this.emptySchedule();
        this.updateUnstudied();
        await this.getNextShow();
        mainStore.setConnectionError(false);
        mainStore.setSchedulerError(false);
      } catch (error) {
        await mainStore.checkApiError(error);
      }
    } else {
      console.log("SDFSLDFJSLDJFLSDF");
    }
  }
}
