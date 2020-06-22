<template>
  <v-content>
    <v-card class="elevation-24">
      <v-toolbar dark color="primary">
        <v-toolbar-title
          >{{ appName }} IRB Form/Privacy Policy (Scroll Down To Accept and Dismiss)
        </v-toolbar-title>
        <v-spacer></v-spacer>
      </v-toolbar>
      <v-card-text>
        <div>
          <h2>
            Project: Streamlining Knowledge Acquisition Through A Novel
            Spaced-Repetition Model
          </h2>
          <h3>Purpose of the Study</h3>
          <p style="text-align:left">
            This research is being conducted by Jordan Boyd-Graber at the University of
            Maryland, College Park. We are inviting you to participate in this research
            project because you are interested in trivia, quizbowl, Jeopardy, and/or
            general knowledge. The purpose of this research project is to make it easier
            and more efficient to study new facts that may come up in these scenarios.
          </p>

          <h3>Procedures</h3>
          <p style="text-align:left">
            The procedures of this study involve first signing up on either the website
            or mobile app with an email and password. You will then be asked to select
            what decks of facts (Jeopardy, history, literature) you would like to learn
            with. You are then encouraged to consistently study facts for as long as you
            would like each day until the end of the experiment. While it is encouraged
            that you study every day, this is not required. We estimate that you will
            spend between 10 and 200 hours over the course of this study, depending on
            your interest, which will continue to the end of June 2021.
          </p>
          <h3>Potential Risks and Discomforts</h3>
          <p style="text-align:left">
            There are no known risks beyond that of using a computer associated to
            participants of this study.
          </p>

          <h3>Potential Benefits</h3>
          <p style="text-align:left">
            The benefits to you include the ability to practice trivia online. We hope
            that, in the future, other people might benefit from this study through
            improved understanding of how to introduce and schedule flashcards for
            learning and review.
          </p>

          <h3>Confidentiality</h3>
          <p style="text-align:left">
            We will not ask you for any personal information beyond your email address.
            Any potential loss of confidentiality will be minimized by storing data
            securely in password-protected account on Amazon Web Services.
          </p>
          <p style="text-align:left">
            If we write a report or article about this research project, your identity
            will be protected to the maximum extent possible. Your information may be
            shared with representatives of the University of Maryland, College Park or
            governmental authorities if you or someone else is in danger or if we are
            required to do so by law.
          </p>
          <h3>Compensation</h3>
          <p style="text-align:left">
            A $20 giftcard will be given to the five users who spend the most time
            studying in the app over the course of the study, which will last until the
            end of June 2021. 10 other users who answer over 200 questions will be
            randomly selected to receive $10 gift cards. If you will earn $100 or more
            as a research participant in this study, you must provide your name, address
            and SSN to receive compensation. If you do not earn over $100 only your name
            and address will be collected to receive compensation.
          </p>
          <h3>Right to Withdraw and Questions</h3>
          <p style="text-align:left">
            Your participation in this research is completely voluntary. You may choose
            not to take part at all. If you decide to participate in this research, you
            may stop participating at any time. If you decide not to participate in this
            study or if you stop participating at any time, you will not be penalized or
            lose any benefits to which you otherwise qualify.
          </p>

          <p style="text-align:left">
            If you decide to stop taking part in the study, if you have questions,
            concerns, or complaints, or if you need to report an injury related to the
            research, please contact the investigator:
          </p>

          <p style="text-align:left">
            Jordan Boyd-Graber<br />
            Iribe 4146 University of Maryland <br />
            jbg@umiacs.umd.edu<br />
            (301)-405-6766<br />
          </p>

          <h3>Participant Rights</h3>
          <p style="text-align:left">
            If you have questions about your rights as a research participant or wish to
            report a research-related injury, please contact:
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
            For more information regarding participant rights, please visit:
            <a src="https://research.umd.edu/irb-research-participants"
              >https://research.umd.edu/irb-research-participants</a
            >
          </p>
          <p style="text-align:left">
            This research has been reviewed according to the University of Maryland IRB
            procedures for research involving human subjects.
          </p>

          <h3>Statement of Consent</h3>
          <p style="text-align:left">
            Your signature indicates that you are at least 18 years of age; you have
            read this consent form or have had it read to you; your questions have been
            answered to your satisfaction and you voluntarily agree to participate in
            this research study. You will receive a copy of this signed consent form.
          </p>

          <p style="text-align:left">
            By clicking “Sign Up” or otherwise exiting this page, you indicate that you
            are at least 18 years of age; you have read this consent form or have had it
            read to you; your questions have been answered to your satisfaction and you
            voluntarily agree to participate in this research study.
          </p>
        </div>
      </v-card-text>
      <v-card-actions>
        <v-btn @click="login">Login</v-btn>
        <v-spacer></v-spacer>
        <v-btn @click="close">Accept</v-btn>
        <v-spacer></v-spacer>
        <v-btn @click="signup">Sign Up</v-btn>
      </v-card-actions>
    </v-card>
  </v-content>
</template>

<script lang="ts">
  import { Component, Vue } from "vue-property-decorator";
  import { appName } from "@/env";
  import { saveVisited } from "@/utils";

  @Component
  export default class SignUp extends Vue {
    appName = appName;

    public login() {
      saveVisited();
      this.$router.push("/login");
    }

    public signup() {
      saveVisited();
      this.$router.push("/sign-up");
    }

    public close() {
      saveVisited();
      this.$router.push("/landing");
    }
  }
</script>
