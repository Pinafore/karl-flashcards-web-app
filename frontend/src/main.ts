import "./component-hooks";
import Vue from "vue";
import App from "./App.vue";
import "./registerServiceWorker";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import * as Sentry from "@sentry/browser";
import { Vue as VueIntegration } from "@sentry/integrations";
import VueGtag from "vue-gtag";

const IGNORE = [/ServiceWorker/, /service worker/, /newestWorker/];

function shouldIgnoreException(s: string): boolean {
  return IGNORE.find((pattern) => pattern.test(s)) != null;
}

if (process.env.VUE_APP_ENV == "production") {
  Sentry.init({
    dsn: "https://ac296d2d7e8c4115ab8f2713520612cf@o283930.ingest.sentry.io/5259730",
    integrations: [new VueIntegration({ Vue, attachProps: true, logErrors: true })],
    beforeSend: function(event, hint: Sentry.EventHint) {
      console.log("Processing before sending to Sentry")
      console.log(event.message);
      console.log(hint.originalException);
      const error = hint.originalException;
      if (error instanceof Error) {
        console.log(error.message);
      } else {
        console.log("not instance of error")
      }
      if (hint) {
        const error = hint.originalException;
        if (typeof error === "string") {
          if (shouldIgnoreException(error)) {
            console.log("ignoring error");
            return null;
          } else {
            console.log("Not ignoring error 1");
          }
        } else if (error instanceof Error) {
          if (shouldIgnoreException(error.message)) {
            console.log("ignoring error");
            return null;
          } else {
            console.log("Not ignoring error 2");
          }
        }
      }
      if(event.message) {
        if (shouldIgnoreException(event.message)) {
          console.log("ignoring error");
          return null;
        } else {
          console.log("Not ignoring error 1");
        }
      }
      console.log("Sending Sentry event")
      return event;
    },
  });
}

Vue.config.productionTip = false;

if (process.env.VUE_APP_ENV == "production") {
  Vue.use(
    VueGtag,
    {
      config: { id: "UA-170799823-1" },
    },
    router,
  );
}

new Vue({
  router,
  store,
  vuetify,
  render: (h) => h(App),
}).$mount("#app");
