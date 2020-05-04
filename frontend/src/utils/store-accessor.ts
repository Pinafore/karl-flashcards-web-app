import { Store } from "vuex";
import { getModule } from "vuex-module-decorators";
import MainModule from "@/store/modules/main";
import AdminModule from "@/store/modules/admin";
import StudyModule from "@/store/modules/study";

let mainStore: MainModule;
let adminStore: AdminModule;
let studyStore: StudyModule;

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function initializeStores(store: Store<any>): void {
  mainStore = getModule(MainModule, store);
  adminStore = getModule(AdminModule, store);
  studyStore = getModule(StudyModule, store);
}

export const modules = {
  main: MainModule,
  admin: AdminModule,
  study: StudyModule,
};

export { initializeStores, mainStore, adminStore, studyStore };
