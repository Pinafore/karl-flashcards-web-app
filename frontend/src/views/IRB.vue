<template>
  <v-main>
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
            Project Title: Streamlining Knowledge Acquisition Through A Novel
            Spaced-Repetition Model
          </h2>
          <h3>Purpose of the Study</h3>
          <p style="text-align:left">
            This research is being conducted by Jordan Boyd-Graber at the University of
            Maryland, College Park. We are inviting you to participate in this research
            project because you are interested in trivia, Quizbowl, Jeopardy, and/or
            general knowledge. The purpose of this research project is to make it easier
            and more efficient to study new facts that may come up in these scenarios.
          </p>

          <h3>Procedures</h3>
          <p style="text-align:left">
            To begin the study, you need to sign up with an email and a password either
            on the website or through the mobile app. Once logged in, you will be asked
            to select decks of flashcards you would like to study. The app provides some
            default decks such as Jeopardy and History, but you can also create your own
            decks and change what to study any time.
          </p>
          <p style="text-align:left">
            During the course of our study, we estimate that you will spend between 10
            and 500 hours. Participating in this research is a requirement for using our
            application but there is no minimum required time commitment for using the
            application. However, we encourage users to study at least 10 minutes a day
            in our app, which would help us gather data about performance and memory
            over time.
          </p>
          <p style="text-align:left">
            Our app has two modes: study mode and test mode. The study mode resembles
            how you would normally study with flashcards: our app shows the front of a
            flashcard, asks for your answer, and tells you whether the answer is
            correct. Our algorithm then chooses the next flashcard that is most suitable
            given your existing knowledge.
          </p>
          <p style="text-align:left">
            In test mode, you will be asked to review 10-30 cards (exact number TBD)
            until you recall every flashcard. Every time a fact is studied, information
            including the date studied, time taken, user id, response information, and
            whether you were learning a new fact is stored in a database. Additionally,
            information about your interaction with flashcards (creation, marking,
            editing) will also be recorded. The only identifying information tied to
            these user ids are the emails and usernames of users in this study.
          </p>
          <p style="text-align:left">
            Our study will take place between Mar. 2022 and Dec. 2022. You are
            encouraged (but not required) to study consistently for as long as you would
            like each day. During the course of our study, we estimate that you will
            spend between 10 and 500 hours. Continual usage is not required, but we
            encourage spending at least 10 minutes a day for continued practice over
            time.
          </p>
          <p style="text-align:left">
            At the end of our study, we will give out rewards (detailed below). An
            optional official group chat will allow you to provide quick user feedback
            and discussion. All participants will be able to see the responses and
            usernames of other participants in the group chat.
          </p>
          <h3>Potential Risks and Discomforts</h3>
          <p style="text-align:left">
            The only known risk to participants of this study is in confidentiality of
            study participation and data from studying flashcards with the app. This
            risk will be mitigated through the procedures described in Confidentiality.
          </p>

          <h3>Potential Benefits</h3>
          <p style="text-align:left">
            The benefits to you include the ability to practice trivia online, but there
            are no other direct benefits. However, this study aims to use techniques in
            machine learning and natural language processing to make learning and
            retaining information more efficient. Participants in this study may
            therefore benefit from being able to better study information they are
            interested in online. Practice with this application could also help
            participants prepare for academic competitions like quizbowl and Jeopardy
            through exposure to new facts and a potentially improved system for
            scheduling flashcards.
          </p>

          <h3>Confidentiality</h3>
          <p style="text-align:left">
            We will not ask you for any personal information beyond your username and
            email. Data collected in this study will be securely stored in a database
            hosted on password-protected webservers and cloud-based file storage. Only
            researchers will have access to users’ emails and no other identifying
            information will be collected in the app. After the end of the experiment,
            data will be anonymized and released publicly. Your email will be kept in a
            separate table and linked to a username and user id. These user ids and
            usernames are used throughout the experiment to schedule flashcards and for
            statistical leaderboards, but the collected usernames and emails will be
            stored in secured file storage and destroyed after the completion of this
            study. To maintain linkage in study data, a new randomized user id will be
            generated in replacement of the identification keys in use during the study.
          </p>
          <p style="text-align:left">
            If we write a report or article about this research project, your identity
            will be protected to the maximum extent possible. Your information may be
            shared with representatives of the University of Maryland, College Park or
            governmental authorities if you or someone else is in danger or if we are
            required to do so by law.
          </p>
          <p style="text-align:left">
            During the course of the study, the collected data will only be accessible
            to PI Jordan Boyd-Graber and Co-PIs Shi Feng & Matthew Shu. Your
            identifiable information (email address) will be deleted at the end of the
            study.
          </p>
          <h3>Compensation</h3>
          <p style="text-align:left">
            We will conduct our study between Mar. 2022 and Dec. 2022.
          </p>
          <p style="text-align:left">
            Top five users who studied the most cards during this time will each receive
            a $20 gift card. Other users who studied over 200 cards each round will
            enter a raffle to win one of ten gift cards, $10 each.
          </p>
          <p style="text-align:left">
            If you will earn $100 or more as a research participant in this study, you
            must provide your name, address and SSN to receive compensation.
          </p>
          <p style="text-align:left">
            If you do not earn over $100 only your name and address will be collected to
            receive compensation. Gift cards will be distributed through email.
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
            4146 Iribe University of Maryland <br />
            College Park, Maryland, 20742 <br />
            E-mail: jbg@umiacs.umd.edu<br />
            Telephone: (301)-405-6766<br />
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
            This research has been reviewed according to the University of Maryland,
            College Park IRB procedures for research involving human subjects.
          </p>

          <h3>Statement of Consent</h3>
          <p style="text-align:left">
            By clicking “Sign Up” or otherwise exiting this page, you indicate that you
            are at least 18 years of age; you have read this consent form or have had it
            read to you; your questions have been answered to your satisfaction and you
            voluntarily agree to participate in this research study.
          </p>
          <p style="text-align:left">
            If you agree to participate, please fill out the form below.
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
  </v-main>
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
