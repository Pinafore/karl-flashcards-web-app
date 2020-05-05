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
        primary: colors.blue.darken4,
        navigation: colors.blue.darken4,
      },
      dark: {
        primary: colors.lightBlue.lighten3,
        navigation: colors.blue.darken4,
      },
    },
  },
  // theme: {
  //   dark: true,
  // },
});
