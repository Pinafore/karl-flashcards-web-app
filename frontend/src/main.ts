import "./component-hooks";
import Vue from "vue";
import App from "./App.vue";
import "./registerServiceWorker";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import * as Sentry from "@sentry/browser";
import { Vue as VueIntegration } from "@sentry/integrations";
import VueGtag from "vue-gtag"

if (process.env.VUE_APP_ENV) {
  Sentry.init({
    dsn: "https://ac296d2d7e8c4115ab8f2713520612cf@o283930.ingest.sentry.io/5259730",
    integrations: [new VueIntegration({ Vue, attachProps: true, logErrors: true })],
  });

}


Vue.config.productionTip = false;

Vue.use(VueGtag, {
  config: { id: "G-9X7E66LXQM" },
  appName: 'KAR³L',
  pageTrackerScreenviewEnabled: true
}, router);

new Vue({
  router,
  store,
  vuetify,
  render: (h) => h(App),
}).$mount("#app");
