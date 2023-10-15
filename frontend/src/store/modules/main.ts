import { api } from "@/api";
import { getLocalToken, removeLocalToken, saveLocalToken } from "@/utils";
import router from "@/router";
import { AxiosError } from "axios";
import { VuexModule, Module, Mutation, Action } from "vuex-module-decorators";
import { IComponents, IAppNotification } from "@/interfaces";
import { UNAUTHORIZED } from "http-status-codes";
import { mainStore } from "@/utils/store-accessor";
import { format, startOfDay } from "date-fns";

@Module({ name: "main" })
export default class MainModule extends VuexModule {
  token = "";
  isLoggedIn: boolean | null = null;
  logInError = false;
  signUpError = false;
  userProfile: IComponents["User"] | null = null;
  dashboardShowDrawer = true;
  notifications: IAppNotification[] = [];
  publicDecks: IComponents["Deck"][] = [];
  facts: IComponents["Fact"][] = [];
  totalFacts = 0;
  isOnHomeScreenPopup: boolean | null = null;
  connectionError = false;
  schedulerError = false;
  inaccessibleDeckError = false;
  filteredStat: IComponents["Statistics"] | null = null;
  savedStats: IComponents["Statistics"][] = [];
  homeStats: IComponents["Statistics"][] = [];
  homeLeaderboards: IComponents["Leaderboard"][] = [];
  savedLeaderboards: IComponents["Leaderboard"][] = [];
  filteredLeaderboard: IComponents["Leaderboard"] | null = null;
  types = [
    { text: "Total Seen:", value: "total_seen" },
    { text: "Days Studied", value: "n_days_studied" },
    { text: "New Facts:", value: "new_facts" },
    { text: "Reviewed Facts:", value: "reviewed_facts" },
    { text: "Recall %:", value: "known_rate" },
    { text: "New Recall %:", value: "new_known_rate" },
    { text: "Review Recall %:", value: "review_known_rate" },
    { text: "Minutes Spent:", value: "total_minutes" },
    { text: "Minutes Spent (Front):", value: "elapsed_minutes_text" },
  ];
  rankTypes = [
    { text: "Total Studied", value: "total_seen" },
    { text: "Days Studied", value: "n_days_studied" },
    { text: "New Facts", value: "new_facts" },
    { text: "Reviewed Facts", value: "reviewed_facts" },
    { text: "Recall %", value: "known_rate" },
    { text: "New Recall %", value: "new_known_rate" },
    { text: "Review Recall %", value: "review_known_rate" },
    { text: "Minutes Spent", value: "total_minutes" },
    { text: "Minutes Spent (Front)", value: "elapsed_minutes_text" },
  ];
  today = format(startOfDay(new Date()), "yyyy-MM-dd'T'HH:mm:ss.SSSxxxx");
  onboarding: boolean | null = null;
  recallPopup: boolean | null = null;
  connectionPopup: boolean | null = null;
  testModePopup: boolean | null = null;

  get hasAdminAccess() {
    return (
      this.userProfile && this.userProfile.is_superuser && this.userProfile.is_active
    );
  }

  get firstNotification() {
    return this.notifications.length > 0 && this.notifications[0];
  }

  @Mutation
  setToken(payload: string) {
    this.token = payload;
  }

  @Mutation
  setLoggedIn(payload: boolean) {
    this.isLoggedIn = payload;
  }

  @Mutation
  setisOnHomeScreenPopup(payload: boolean) {
    this.isOnHomeScreenPopup = payload;
  }

  @Mutation
  setLogInError(payload: boolean) {
    this.logInError = payload;
  }

  @Mutation
  setSignUpError(payload: boolean) {
    this.signUpError = payload;
  }

  @Mutation
  setConnectionPopup(payload: boolean) {
    this.connectionPopup = payload;
  }

  @Mutation
  setTestModePopup(payload: boolean) {
    this.testModePopup = payload;
  }

  @Mutation
  setUserProfile(payload: IComponents["User"]) {
    this.userProfile = payload;
  }

  @Mutation
  setOnboarding(payload: boolean | null) {
    this.onboarding = payload;
  }

  @Mutation
  setRecallPopup(payload: boolean) {
    this.recallPopup = payload;
  }

  @Mutation
  setDashboardShowDrawer(payload: boolean) {
    this.dashboardShowDrawer = payload;
  }

  @Mutation
  addNotification(payload: IAppNotification) {
    this.notifications.push(payload);
  }

  @Mutation
  removeNotification(payload: IAppNotification) {
    this.notifications = this.notifications.filter(
      (notification) => notification !== payload,
    );
  }

  @Mutation
  setFacts(payload: IComponents["Fact"][]) {
    this.facts = payload;
  }

  @Mutation
  updateFactInFacts(payload: { index: number; fact: IComponents["Fact"] }) {
    Object.assign(this.facts[payload.index], payload.fact);
  }

  @Mutation
  setTotalFacts(payload: number) {
    this.totalFacts = payload;
  }

  @Mutation
  setPublicDecks(payload: IComponents["Deck"][]) {
    this.publicDecks = payload;
  }

  @Mutation
  setConnectionError(payload: boolean) {
    this.connectionError = payload;
  }

  @Mutation
  setSchedulerError(payload: boolean) {
    this.schedulerError = payload;
  }

  @Mutation
  setInaccessibleDeckError(payload: boolean) {
    this.inaccessibleDeckError = payload;
  }

  @Mutation
  setSavedStats(payload: IComponents["Statistics"][]) {
    this.savedStats = payload;
  }

  @Mutation
  setSavedLeaderboards(payload: IComponents["Leaderboard"][]) {
    this.savedLeaderboards = payload;
  }

  @Mutation
  setFilteredStat(payload: IComponents["Statistics"]) {
    this.filteredStat = payload;
  }

  @Mutation
  setFilteredLeaderboard(payload: IComponents["Leaderboard"]) {
    this.filteredLeaderboard = payload;
  }

  @Mutation
  setHomeStats(payload: IComponents["Statistics"][]) {
    this.homeStats = payload;
  }

  @Mutation
  setHomeLeaderboards(payload: IComponents["Leaderboard"][]) {
    this.homeLeaderboards = payload;
  }

  @Mutation
  addToLeaderboards(payload: IComponents["Leaderboard"]) {
    this.savedLeaderboards.unshift(payload);
  }

  @Mutation
  addToHomeLeaderboards(payload: IComponents["Leaderboard"]) {
    this.homeLeaderboards.unshift(payload);
  }

  @Mutation
  updateHomeLeaderboardToday(payload: IComponents["Leaderboard"]) {
    if (this.homeLeaderboards.length == 2) {
      this.homeLeaderboards[0] = payload;
    } else {
      this.homeLeaderboards = [payload];
    }
  }

  @Mutation
  updateHomeLeaderboardAllTime(payload: IComponents["Leaderboard"]) {
    if (this.homeLeaderboards.length > 1) {
      this.homeLeaderboards[1] = payload;
    } else {
      this.homeLeaderboards.push(payload);
    }
  }

  @Mutation
  addToStats(payload: IComponents["Statistics"]) {
    this.savedStats.unshift(payload);
  }

  @Action
  async logIn(payload: { username: string; password: string }) {
    try {
      const response = await api.logInGetToken(payload.username, payload.password);
      const token = response.data.access_token;
      if (token) {
        saveLocalToken(token);
        this.setToken(token);
        this.setLoggedIn(true);
        this.setLogInError(false);
        await this.getUserProfile();
        await this.routeLoggedIn();
        this.addNotification({ content: "Logged in", color: "success" });
      } else {
        await this.logOut();
      }
    } catch (err) {
      this.setLogInError(true);
      await this.logOut();
    }
  }

  @Action
  async getUserProfile() {
    try {
      const response = await api.getMe(this.token);
      if (response.data) {
        this.setUserProfile(response.data);
      }
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async updateUserProfile(payload: IComponents["UserUpdate"]) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      this.addNotification(loadingNotification);
      const response = (
        await Promise.all([
          api.updateMe(this.token, payload),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.setUserProfile(response.data);
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Profile successfully updated",
        color: "success",
      });
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async updateUserHelp(payload: boolean) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      this.addNotification(loadingNotification);
      const response = (
        await Promise.all([
          api.updateMe(this.token, { show_help: payload }),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.setUserProfile(response.data);
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Profile successfully updated",
        color: "success",
      });
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async updatePWA(payload: boolean) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      this.addNotification(loadingNotification);
      const response = (
        await Promise.all([
          api.updateMe(this.token, { pwa_tip: payload }),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.setUserProfile(response.data);
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Profile successfully updated",
        color: "success",
      });
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async checkLoggedIn() {
    if (!this.isLoggedIn) {
      let token = this.token;
      if (!token) {
        const localToken = getLocalToken();
        if (localToken) {
          this.setToken(localToken);
          token = localToken;
        }
      }
      if (token) {
        try {
          const response = await api.getMe(token);
          this.setLoggedIn(true);
          this.setUserProfile(response.data);
        } catch (error) {
          await this.removeLogIn();
        }
      } else {
        await this.removeLogIn();
      }
    }
  }

  @Action
  async removeLogIn() {
    removeLocalToken();
    this.setToken("");
    this.setLoggedIn(false);
  }

  @Action
  async logOut() {
    await this.removeLogIn();
    await this.routeLogOut();
  }

  @Action
  async userLogOut() {
    await this.logOut();
    this.addNotification({ content: "Logged out", color: "success" });
  }

  @Action
  async routeLogOut() {
    if (router.currentRoute.path !== "/login") {
      await router.push("/landing");
    }
  }

  @Action
  async checkApiError(payload: AxiosError) {
    if (payload.response) {
      if (payload.response.status === UNAUTHORIZED) {
        this.addNotification({
          content: "This action is unauthorized. You are logged out.",
          color: "error",
        });
        await this.logOut();
      }
      if (
        payload.response.status === 503 ||
        payload.response.status === 502 ||
        payload.response.status === 401
      ) {
        this.addNotification({
          content: "A temporary error occurred. Please log in again.",
          color: "error",
        });
        await this.logOut();
      }
      if (payload.response.status == 555) {
        this.setConnectionError(true);
      }
      if (payload.response.status == 556) {
        this.setSchedulerError(true);
      }
    }
  }

  @Action
  async routeLoggedIn() {
    if (router.currentRoute.path === "/login" || router.currentRoute.path === "/") {
      router.push("/main/dashboard");
    } else if (router.currentRoute.path === "/sign-up") {
      router.push({
        path: "main/add/public-decks",
      });
    }
  }

  @Action
  async removeNotificationDelayed(payload: {
    notification: IAppNotification;
    timeout: number;
  }) {
    return new Promise((resolve, _reject) => {
      setTimeout(() => {
        this.removeNotification(payload.notification);
        resolve(true);
      }, payload.timeout);
    });
  }

  @Action
  async recoverPassword(payload: { email: string }) {
    const loadingNotification = {
      content: "Sending password recovery email",
      showProgress: true,
    };
    try {
      this.addNotification(loadingNotification);
      await Promise.all([
        api.passwordRecovery(payload.email),
        await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
      ]);
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Password recovery email sent",
        color: "success",
      });
      await this.logOut();
    } catch (error) {
      this.removeNotification(loadingNotification);
      this.addNotification({ color: "error", content: "Incorrect username" });
    }
  }

  @Action
  async resetPassword(payload: { password: string; token: string }) {
    const loadingNotification = { content: "Resetting password", showProgress: true };
    try {
      this.addNotification(loadingNotification);
      await Promise.all([
        api.resetPassword(payload.password, payload.token),
        await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
      ]);
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Password successfully reset",
        color: "success",
      });
      await this.logOut();
    } catch (error) {
      this.removeNotification(loadingNotification);
      this.addNotification({
        color: "error",
        content: "Error resetting password",
      });
    }
  }

  @Action
  async createUserOpen(payload: IComponents["UserCreate"]) {
    const loadingNotification = { content: "Creating account", showProgress: true };
    try {
      this.addNotification(loadingNotification);
      const response = (
        await Promise.all([
          api.createUserOpen(this.token, payload),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.removeNotification(loadingNotification);
      this.setSignUpError(false);
      this.addNotification({ content: "User successfully created", color: "success" });
      this.setUserProfile(response.data);
      return true;
    } catch (error) {
      console.log(error);
      this.removeNotification(loadingNotification);
      this.setSignUpError(true);
      this.addNotification({ content: "An error occurred", color: "error" });
      await this.checkApiError(error);
    }
  }

  @Action
  async createDeck(payload: IComponents["DeckCreate"]) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      this.addNotification(loadingNotification);
      const _response = (
        await Promise.all([
          api.createDeck(this.token, payload),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Deck successfully created",
        color: "success",
      });
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async createFact(payload: IComponents["FactCreate"]) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      this.addNotification(loadingNotification);
      const _response = (
        await Promise.all([
          api.createFact(this.token, payload),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Fact successfully created",
        color: "success",
      });
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async uploadFacts(payload: IComponents["FactUpload"]) {
    try {
      const loadingNotification = { content: "validating file", showProgress: true };
      this.addNotification(loadingNotification);
      const _response = (
        await Promise.all([
          api.uploadFacts(this.token, payload),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "File accepted and import begins",
        color: "success",
      });
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async getFacts(payload: IComponents["FactSearch"]) {
    try {
      const response = await api.getFacts(this.token, payload);
      if (response) {
        this.setFacts(response.data.facts);
        this.setTotalFacts(response.data.total);
        return response.data;
      }
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async getPublicDecks() {
    try {
      const response = await api.getPublicDecks(this.token);
      if (response) {
        this.setPublicDecks(response.data);
      }
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async assignDecks(payload: number[]) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      this.addNotification(loadingNotification);
      const response = (
        await Promise.all([
          api.assignDecks(this.token, payload),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      this.setUserProfile(response.data);
      this.removeNotification(loadingNotification);
      this.addNotification({
        content: "Decks assigned",
        color: "success",
      });
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async updateFact(payload: { id: number; data: IComponents["FactUpdate"] }) {
    try {
      const loadingNotification = { content: "saving", showProgress: true };
      mainStore.addNotification(loadingNotification);
      const _response = (
        await Promise.all([
          api.updateFact(mainStore.token, payload.id, payload.data),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      mainStore.removeNotification(loadingNotification);
      mainStore.addNotification({
        content: "Fact updated",
        color: "success",
      });
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async createMnemonic(payload: { data: IComponents["MnemonicCreate"] }) {
    try {
      const _response = (
        await Promise.all([
          api.createMnemonic(this.token, payload.data),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async getMnemonic(payload: { data: IComponents["MnemonicSearch"]  }) {
    try {
      const _response = (
        await Promise.all([
          api.getMnemonics(this.token, payload.data),
          await new Promise((resolve, _reject) => setTimeout(() => resolve(), 500)),
        ])
      )[0];
      return _response.data
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async markFact(payload: { id: number; todo: boolean }) {
    try {
      await api.markFact(mainStore.token, payload.id);
      if (payload.todo) {
        mainStore.addNotification({
          content: "Fact marked",
          color: "success",
        });
      } else {
        mainStore.addNotification({
          content: "Fact unmarked",
          color: "success",
        });
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async suspendFact(payload: { id: number; todo: boolean }) {
    try {
      await api.suspendFact(mainStore.token, payload.id);
      if (payload.todo) {
        mainStore.addNotification({
          content: "Fact suspended",
          color: "success",
        });
      } else {
        mainStore.addNotification({
          content: "Fact unsuspended",
          color: "success",
        });
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async reportFact(payload: { id: number; data: IComponents["FactToReport"] }) {
    try {
      await api.reportFact(mainStore.token, payload.id, payload.data);
      mainStore.addNotification({
        content: "Fact reported",
        color: "success",
      });
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async clearReportFact(payload: { id: number }) {
    try {
      await api.clearReportFact(mainStore.token, payload.id);
      mainStore.addNotification({
        content: "Fact report discarded",
        color: "success",
      });
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async clearReportsFact(payload: { id: number }) {
    try {
      await api.clearReportsFact(mainStore.token, payload.id);
      mainStore.addNotification({
        content: "Fact Reports Resolved",
        color: "success",
      });
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async deleteDecks(payload: { ids: number[] }) {
    try {
      for (const id of payload.ids) {
        await api.deleteDeck(mainStore.token, id);
      }
      mainStore.addNotification({
        content: "Deck(s) deleted",
        color: "success",
      });
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async deleteFact(payload: { id: number; todo: boolean }) {
    try {
      await api.deleteFact(mainStore.token, payload.id);
      if (payload.todo) {
        mainStore.addNotification({
          content: "Fact deleted",
          color: "success",
        });
      } else {
        mainStore.addNotification({
          content: "Fact deletion undone",
          color: "success",
        });
      }
    } catch (error) {
      await mainStore.checkApiError(error);
    }
  }

  @Action
  async getHomeStatistics() {
    try {
      const response = await api.getHomeStats(this.token);
      this.setHomeStats(response.data);
      this.setConnectionError(false);
      this.setSchedulerError(false);
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async getSavedStatistics() {
    try {
      const response = await api.getSavedStats(this.token);
      this.setSavedStats(response.data);
      this.setConnectionError(false);
      this.setSchedulerError(false);
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async getStatistic(payload: IComponents["StatSearch"]) {
    try {
      const response = await api.getUserStats(this.token, payload);
      this.setFilteredStat(response.data);
      this.setConnectionError(false);
      this.setSchedulerError(false);
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async getHomeLeaderboards(payload: IComponents["LeaderboardSearch"][]) {
    try {
      const response = await api.getLeaderboard(this.token, payload[0]);
      this.updateHomeLeaderboardToday(response.data);

      const response2 = await api.getLeaderboard(this.token, payload[1]);
      this.updateHomeLeaderboardAllTime(response2.data);
      this.setConnectionError(false);
      this.setSchedulerError(false);
    } catch (error) {
      await this.checkApiError(error);
    }
  }

  @Action
  async getLeaderboard(payload: IComponents["LeaderboardSearch"]) {
    try {
      const response = await api.getLeaderboard(this.token, payload);
      this.setFilteredLeaderboard(response.data);
      this.setConnectionError(false);
      this.setSchedulerError(false);
    } catch (error) {
      await this.checkApiError(error);
    }
  }
}
