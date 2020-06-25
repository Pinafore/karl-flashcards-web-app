import Vue from "vue";
import VueRouter from "vue-router";

import RouterComponent from "@/components/RouterComponent.vue";

Vue.use(VueRouter);

export default new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes: [
    {
      path: "/",
      component: () => import(/* webpackChunkName: "start" */ "@/views/main/Start.vue"),
      children: [
        {
          path: "landing",
          // route level code-splitting
          // this generates a separate chunk (about.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          component: () => import(/* webpackChunkName: "index" */ "@/views/Index.vue"),
        },
        {
          path: "login",
          // route level code-splitting
          // this generates a separate chunk (about.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          components: {
            default: () => import(/* webpackChunkName: "index" */ "@/views/Index.vue"),
            dialog: () => import(/* webpackChunkName: "login" */ "@/views/Login.vue"),
          },
        },
        {
          path: "sign-up",
          // route level code-splitting
          // this generates a separate chunk (about.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          components: {
            default: () => import(/* webpackChunkName: "index" */ "@/views/Index.vue"),
            dialog: () => import(/* webpackChunkName: "signup" */ "@/views/Signup.vue"),
          },
        },
        {
          path: "privacy-irb",
          // route level code-splitting
          // this generates a separate chunk (about.[hash].js) for this route
          // which is lazy-loaded when the route is visited.
          components: {
            default: () => import(/* webpackChunkName: "index" */ "@/views/Index.vue"),
            dialog: () => import(/* webpackChunkName: "signup" */ "@/views/IRB.vue"),
          },
        },
        {
          path: "recover-password",
          component: () =>
            import(
              /* webpackChunkName: "recover-password" */ "@/views/PasswordRecovery.vue"
            ),
        },
        {
          path: "reset-password",
          component: () =>
            import(
              /* webpackChunkName: "reset-password" */ "@/views/ResetPassword.vue"
            ),
        },
        {
          path: "main",
          component: () =>
            import(/* webpackChunkName: "main" */ "@/views/main/Main.vue"),
          children: [
            {
              path: "dashboard",
              component: () =>
                import(
                  /* webpackChunkName: "main-dashboard" */ "@/views/main/Dashboard.vue"
                ),
            },
            {
              path: "browse",
              name: "browse",
              component: () =>
                import(
                  /* webpackChunkName: "main-browser" */ "@/views/main/Browser.vue"
                ),
              children: [
                {
                  path: "edit/:id",
                  name: "browse-edit",
                  components: {
                    default: () =>
                      import(
                        /* webpackChunkName: "main-browser" */ "@/views/main/Browser.vue"
                      ),
                    edit: () =>
                      import(
                        /* webpackChunkName: "edit-fact" */ "@/views/main/EditFact.vue"
                      ),
                  },
                },
              ],
            },
            {
              path: "profile",
              component: RouterComponent,
              redirect: "profile/view",
              children: [
                {
                  path: "view",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-profile" */ "@/views/main/profile/UserProfile.vue"
                    ),
                },
                {
                  path: "edit",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-profile-edit" */ "@/views/main/profile/UserProfileEdit.vue"
                    ),
                },
                {
                  path: "password",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-profile-password" */ "@/views/main/profile/UserProfileEditPassword.vue"
                    ),
                },
              ],
            },
            {
              path: "add",
              component: RouterComponent,
              redirect: "add/fact",
              children: [
                {
                  path: "fact",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-add-fact" */ "@/views/main/add/AddFact.vue"
                    ),
                },
                {
                  path: "deck",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-add-deck" */ "@/views/main/add/AddDeck.vue"
                    ),
                },
                {
                  path: "public-decks",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-choose-decks" */ "@/views/main/add/ChooseDecks.vue"
                    ),
                },
                {
                  path: "upload-facts",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-upload-facts" */ "@/views/main/add/UploadFacts.vue"
                    ),
                },
              ],
            },
            {
              path: "study",
              component: RouterComponent,
              redirect: "study/decks",
              children: [
                {
                  path: "decks",
                  name: "main-study-users-decks",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-decks" */ "@/views/main/study/Decks.vue"
                    ),
                },
                {
                  path: "learn",
                  name: "learn",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-learn" */ "@/views/main/study/Learn.vue"
                    ),
                  children: [
                    {
                      path: "edit",
                      name: "learn-edit",
                      components: {
                        default: () =>
                          import(
                            /* webpackChunkName: "main-learn" */ "@/views/main/study/Learn.vue"
                            ),
                        edit: () =>
                          import(
                            /* webpackChunkName: "edit-fact" */ "@/views/main/EditFact.vue"
                            ),
                      },
                    },
                  ],
                },
              ],
            },
            {
              path: "admin",
              component: () =>
                import(
                  /* webpackChunkName: "main-admin" */ "@/views/main/admin/Admin.vue"
                ),
              redirect: "admin/users/all",
              children: [
                {
                  path: "users",
                  redirect: "users/all",
                },
                {
                  path: "users/all",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-admin-users" */ "@/views/main/admin/AdminUsers.vue"
                    ),
                },
                {
                  path: "users/edit/:id",
                  name: "main-admin-users-edit",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-admin-users-edit" */ "@/views/main/admin/EditUser.vue"
                    ),
                },
                {
                  path: "users/create",
                  name: "main-admin-users-create",
                  component: () =>
                    import(
                      /* webpackChunkName: "main-admin-users-create" */ "@/views/main/admin/CreateUser.vue"
                    ),
                },
              ],
            },
          ],
        },
      ],
    },
    {
      path: "/*",
      redirect: "/",
    },
  ],
});
