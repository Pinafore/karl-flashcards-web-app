<template>
  <v-content>
    <v-container fluid class="fill-height">
      <validation-observer ref="observer" v-slot="{ invalid }">
        <form @submit.prevent="onSubmit" @reset.prevent="onReset">
        <v-card class="elevation-24">
          <v-toolbar dark color="primary">
            <v-toolbar-title
              >Sign Up — {{ appName }} (IRB Form, Scroll Down To Sign Up!)
            </v-toolbar-title>
            <v-spacer></v-spacer>
          </v-toolbar>
          <v-card-text>
              <div id="consent_form">
                <h2>
                  Project: Streamlining Knowledge Acquisition Through A Novel
                  Spaced-Repetition Model
                </h2>
                <h3>Purpose of the Study</h3>
                <p style="text-align:left">
                  This research is being conducted by Jordan Boyd-Graber at the
                  University of Maryland, College Park. We are inviting you to
                  participate in this research project because you are interested in
                  trivia, quizbowl, Jeopardy, and/or general knowledge. The purpose of
                  this research project is to make it easier and more efficient to study
                  new facts that may come up in these scenarios.
                </p>

                <h3>Procedures</h3>
                <p style="text-align:left">
                  The procedures of this study involve first signing up on either the
                  website or mobile app with a name, email, and password. You will then
                  be asked to select what decks of facts (Jeopardy, history, literature)
                  you would like to learn with. An initial evaluation set of 100 facts
                  generated to gauge their pre-existing knowledge of the subject areas.
                  This training set is estimated to take between 10 to 15 minutes.
                  Following this initial evaluation, you are encouraged to consistently
                  study facts for as long as you would like each day until the
                  experiment. While it is preferred for you to study every day, that is
                  not necessarily either. We estimate that you will spend somewhere
                  between 10 to 60 hours over the course of this study, which will
                  continue to the end of December.
                </p>
                <h3>Potential Risks and Discomforts</h3>
                <p style="text-align:left">
                  There are no known risks beyond that of using a computer associated to
                  participants of this study.
                </p>

                <h3>Potential Benefits</h3>
                <p style="text-align:left">
                  The benefits to you include the ability to practice trivia online. We
                  hope that, in the future, other people might benefit from this study
                  through improved understanding of how to introduce and schedule
                  flashcards for learning and review.
                </p>

                <h3>Confidentiality</h3>
                <p style="text-align:left">
                  We will not ask you for any personal information beyond your email
                  address. Any potential loss of confidentiality will be minimized by
                  storing data securely in password-protected account on Amazon Web
                  Services.
                </p>
                <p style="text-align:left">
                  If we write a report or article about this research project, your
                  identity will be protected to the maximum extent possible. Your
                  information may be shared with representatives of the University of
                  Maryland, College Park or governmental authorities if you or someone
                  else is in danger or if we are required to do so by law.
                </p>
                <h3>Compensation</h3>
                <p style="text-align:left">
                  $20 will be given to the five users who spend the most time studying
                  in the app over the course of the study, which will last until the end
                  of December. There will be a 10 x $10 raffle for all other users who
                  were active for 80% of the days over the course of the study. If you
                  will earn $100 or more as a research participant in this study, you
                  must provide your name, address and SSN to receive compensation. If
                  you do not earn over $100 only your name and address will be collected
                  to receive compensation.
                </p>
                <h3>Right to Withdraw and Questions</h3>
                <p style="text-align:left">
                  Your participation in this research is completely voluntary. You may
                  choose not to take part at all. If you decide to participate in this
                  research, you may stop participating at any time. If you decide not to
                  participate in this study or if you stop participating at any time,
                  you will not be penalized.
                </p>

                <p style="text-align:left">
                  If you decide to stop taking part in the study, if you have questions,
                  concerns, or complaints, or if you need to report an injury related to
                  the research, please contact the investigator:
                </p>

                <p style="text-align:left">
                  Jordan Boyd-Graber<br />
                  Iribe 4146 University of Maryland <br />
                  jbg@umiacs.umd.edu<br />
                  (301)-405-6766<br />
                </p>

                <h3>Participant Rights</h3>
                <p style="text-align:left">
                  If you have questions about your rights as a research participant or
                  wish to report a research-related injury, please contact:
                </p>

                <p style="text-align:left">
                  University of Maryland College Park<br />
                  Institutional Review Board Office<br />
                  1204 Marie Mount Hall<br />
                  College Park, Maryland, 20742<br />
                  E-mail: irb@umd.edu<br />
                  Telephone: 301-405-0678<br />
                </p>

                <p style="text-align:left">
                  This research has been reviewed according to the University of
                  Maryland IRB procedures for research involving human subjects.
                </p>

                <h3>Statement of Consent</h3>
                <p style="text-align:left">
                  Your signature indicates that you are at least 18 years of age; you
                  have read this consent form or have had it read to you; your questions
                  have been answered to your satisfaction and you voluntarily agree to
                  participate in this research study. You will receive a copy of this
                  signed consent form.
                </p>

                <p style="text-align:left">
                  If you agree to participate, please fill out the form below.
                </p>
              </div>
              <validation-provider
                v-slot="{ errors }"
                name="Email"
                rules="required|email"
              >
                <v-text-field
                  v-model="email"
                  prepend-icon="mdi-account"
                  :error-messages="errors[0]"
                  label="Email"
                  type="email"
                  required
                ></v-text-field>
              </validation-provider>
              <validation-provider v-slot="{ errors }" name="Username" rules="required">
                <v-text-field
                  v-model="username"
                  prepend-icon="mdi-account"
                  label="Username"
                  :error-messages="errors[0]"
                  autocomplete="off"
                  required
                ></v-text-field>
              </validation-provider>
              <validation-provider
                v-slot="{ errors }"
                :debounce="100"
                name="Password"
                vid="password1"
                rules="required"
              >
                <v-text-field
                  v-model="password1"
                  prepend-icon="mdi-lock"
                  type="password"
                  label="Password"
                  :error-messages="errors"
                  autocomplete="off"
                ></v-text-field>
              </validation-provider>
              <validation-provider
                v-slot="{ errors }"
                :debounce="100"
                name="Password confirmation"
                vid="password2"
                rules="required|confirmed:password1"
                autocomplete="off"
              >
                <v-text-field
                  v-model="password2"
                  prepend-icon="mdi-lock"
                  type="password"
                  label="Confirm Password"
                  :error-messages="errors"
                  autocomplete="off"
                ></v-text-field>
              </validation-provider>

            <div v-if="signUpError">
              <v-alert :value="signUpError" transition="fade-transition" type="error">
                A user with this email or username already exists
              </v-alert>
            </div>
            <v-col class="caption text-right"
              ><router-link to="/recover-password"
                >Forgot your password?</router-link
              ></v-col
            >
          </v-card-text>
          <v-card-actions>
            <v-btn @click="login">Login</v-btn>
            <v-spacer></v-spacer>
              <v-btn type="reset">Reset</v-btn>
            <v-btn type="submit" :disabled="invalid">Sign Up</v-btn>
          </v-card-actions>
        </v-card>
        </form>
      </validation-observer>
    </v-container>
  </v-content>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { confirmed, email, required } from "vee-validate/dist/rules";
  import { extend, ValidationObserver, ValidationProvider } from "vee-validate";
  import { mainStore } from "@/utils/store-accessor";
  import { IComponents } from "@/interfaces";

  // register validation rules
  extend("required", { ...required, message: "{_field_} can not be empty" });
  extend("confirmed", { ...confirmed, message: "Passwords do not match" });
  extend("email", { ...email, message: "Invalid email address" });

  @Component({
    components: {
      ValidationObserver,
      ValidationProvider,
    },
  })
  export default class SignUp extends Vue {
    $refs!: {
      observer: InstanceType<typeof ValidationObserver>;
    };
    appName = appName;
    username = "";
    email = "";
    password1 = "";
    password2 = "";
    signUpError: boolean | null = null;

    async mounted() {
      this.onReset();
    }

    public login() {
      this.$router.push("/login");
    }

    onReset() {
      this.password1 = "";
      this.password2 = "";
      this.username = "";
      this.email = "";
      this.$refs.observer.reset();
    }

    async onSubmit() {
      this.signUpError = false;
      const success = await this.$refs.observer.validate();

      if (!success) {
        return;
      }

      const updatedProfile: IComponents["UserCreate"] = {
        email: this.email,
        username: this.username,
        password: this.password1,
      };
      if (await mainStore.createUserOpen(updatedProfile)) {
        await mainStore.logIn({ username: this.email, password: this.password1 });
      } else {
        this.signUpError = true;
      }
    }
  }
</script>
