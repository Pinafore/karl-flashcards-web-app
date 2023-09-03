import "@mdi/font/css/materialdesignicons.css";
import Vue from "vue";
import Vuetify, { colors } from "vuetify/lib";

Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    iconfont: "mdi",
  },
  theme: {
    themes: {
      light: {
        primary: colors.blueGrey.darken2,
        navigation: colors.blueGrey.darken2,
      },
      dark: {
        primary: colors.lightBlue.lighten3,
        navigation: colors.blue.darken4,
      },
    },
  },
});
