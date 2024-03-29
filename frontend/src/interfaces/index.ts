import { DataTableHeader } from "vuetify";

export interface IAppNotification {
  content: string;
  color?: string;
  showProgress?: boolean;
}

export interface IStudyShow {
  text: string;
  fact?: IComponents["Fact"];
  enable_report: boolean;
  enable_actions: boolean;
  enable_show_back: boolean;
  marked: boolean;
}

export enum Field {
  text = "text",
  answer = "answer",
  deck = "deck",
  identifier = "identifier",
  category = "category",
  extra = "extra",
}

export enum Permission {
  owner = "owner",
  viewer = "viewer",
}

export interface IStatus {
  marked?: boolean | undefined;
  suspended?: boolean;
  reported?: boolean;
}
export interface IComponents {
  Deck: { title: string; public: boolean; id: number; deck_type: string };
  DeckCreate: { title: string };
  SuperDeckCreate: { title: string; public?: boolean };
  DeckUpdate: { title?: string };
  SuperDeckUpdate: { title?: string; public?: boolean };
  Fact: {
    text: string;
    answer: string;
    category?: string;
    deck_id: number;
    identifier?: string;
    answer_lines: string[];
    extra?: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
    fact_id: number;
    user_id: number;
    create_date: string;
    update_date: string;
    deck: IComponents["Deck"];
    rationale?: string;
    marked?: boolean;
    suspended?: boolean;
    reported?: boolean;
    permission?: Permission;
    reports?: IComponents["FactReported"][];
  };
  FactCreate: {
    text: string;
    answer: string;
    category?: string;
    deck_id: number;
    identifier?: string;
    answer_lines: string[];
    extra?: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
  };
  FactUpdate: {
    text?: string;
    answer?: string;
    category?: string;
    deck_id?: number;
    identifier?: string;
    answer_lines?: string[];
    extra?: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
  };
  FactToReport: {
    text?: string;
    answer?: string;
    category?: string;
    deck_id?: number;
    identifier?: string;
    answer_lines?: string[];
    extra?: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
  };
  FactReported: {
    text?: string;
    answer?: string;
    category?: string;
    deck_id?: number;
    identifier?: string;
    answer_lines?: string[];
    extra?: { [key: string]: any }; // eslint-disable-line @typescript-eslint/no-explicit-any
    report_id?: number;
    reporter_id?: number;
    reporter_username?: number;
  };
  FactSearch: {
    skip?: number;
    limit?: number;
    all?: string;
    text?: string;
    answer?: string;
    category?: string;
    deck_id?: number;
    identifier?: string;
    deck_ids?: number[];
    marked?: boolean;
    suspended?: boolean;
    reported?: boolean;
  };
  FactBrowse: {
    facts: IComponents["Fact"][];
    total: number;
  };
  FactUpload: {
    headers: Field[];
    deck_id: number;
    delimeter?: string;
    upload_file: File;
  };
  HTTPValidationError: {
    detail?: IComponents["ValidationError"][];
  };
  MnemonicLearningFeedbackLog: {
    study_id: number;
    fact_id: number;
    user_id: number;
    user_rating: number;
    is_offensive: boolean;
    is_incorrect_definition: boolean;
    is_difficult_to_understand: boolean;
    is_not_memorable: boolean;
    is_bad_phonetic_keyword: boolean;
    is_bad_circular_keyword: boolean;
    is_bad_keyword_explanation: boolean;
    is_bad_for_other_reason: boolean;
    other_reason_text: string;
    correct: boolean;
    mnemonic_used_id: string;
    mnemonic_used_text: string;
  };
  MnemonicComparisonFeedbackLog: {
    study_id: number;
    fact_id: number;
    user_id: number;
    mnemonic_a: string;
    mnemonic_b: string;
    comparison_rating: string | null;
    passed_sanity_check: boolean | null;
    correct: boolean;
  };
  MnemonicSearch: {
    user_id: number;
    fact_ids: number[];
  };
  Msg: { msg: string };
  Schedule: {
    fact_id: number;
    typed: string;
    response: boolean;
    elapsed_milliseconds_text: number;
    elapsed_milliseconds_answer: number;
    recommendation: boolean;
    test_mode: number;
    used_mnemonic?: boolean;
  };
  SuperUserCreate: {
    email: string;
    username: string;
    is_active?: boolean;
    repetition_model?:
      | "leitner"
      | "sm-2"
      | "karl"
      | "karl50"
      | "karl85"
      | "settles"
      | "fsrs"
      | "karl-ablation";
    password: string;
    is_superuser?: boolean;
  };
  SuperUserUpdate: {
    email?: string;
    username?: string;
    is_active?: boolean;
    repetition_model?:
      | "leitner"
      | "sm-2"
      | "karl"
      | "karl50"
      | "karl85"
      | "settles"
      | "fsrs"
      | "karl-ablation";
    password?: string;
    default_deck_id?: number;
    is_superuser?: boolean;
  };
  Token: { access_token: string; token_type: string };
  User: {
    email: string;
    username: string;
    is_active: boolean;
    repetition_model?:
      | "leitner"
      | "sm-2"
      | "karl"
      | "karl50"
      | "karl85"
      | "settles"
      | "fsrs"
      | "karl-ablation";
    id: number;
    is_superuser: boolean;
    show_help: boolean;
    show_mnemonic_help: boolean,
    default_deck: IComponents["Deck"];
    decks?: IComponents["Deck"][];
    suspended_facts?: IComponents["Fact"][];
    facts?: IComponents["Fact"][];
    dark_mode: boolean;
    pwa_tip: boolean;
    recall_target: number;
    test_mode: number;
    // resume_studyset: boolean;
    in_test_mode: boolean;
    study_set_expiry_date?: string;
  };
  UserCreate: {
    email: string;
    username: string;
    is_active?: boolean;
    repetition_model?:
      | "leitner"
      | "sm-2"
      | "karl"
      | "karl50"
      | "karl85"
      | "settles"
      | "fsrs"
      | "karl-ablation";
    password: string;
  };
  UserUpdate: {
    email?: string;
    username?: string;
    is_active?: boolean;
    repetition_model?:
      | "leitner"
      | "sm-2"
      | "karl"
      | "karl50"
      | "karl85"
      | "settles"
      | "fsrs"
      | "karl-ablation";
    password?: string;
    default_deck_id?: number;
    show_help?: boolean;
    show_mnemonic_help?: boolean;
    dark_mode?: boolean;
    pwa_tip?: boolean;
    recall_target?: number;
    test_mode?: number;
  };
  ValidationError: { loc: string[]; msg: string; type: string };
  StatSearch: {
    date_start?: string;
    date_end?: string;
    deck_id?: number;
  };
  Statistics: {
    name: string;
    user_id: number;
    new_known_rate: number;
    review_known_rate: number;
    known_rate: number;
    new_facts: number;
    reviewed_facts: number;
    total_seen: number;
    total_minutes: number;
    elapsed_minutes_text: number;
    user: IComponents["User"];
  };
  LeaderboardSearch: {
    rank_type: string;
    skip?: number;
    limit?: number;
    min_studied?: number;
    deck_id?: number;
    date_start?: string;
    date_end?: string;
  };
  LeaderboardUser: {
    value: number;
    user: IComponents["User"];
  };
  Leaderboard: {
    leaderboard: IComponents["LeaderboardUser"][];
    total: number;
    name: string;
    headers: DataTableHeader[];
    details: string;
    rank_type: string;
    user?: IComponents["User"];
    user_place?: number;
    limit?: number;
  };
  StudySet: {
    id: number;
    completed: boolean;
    unstudied_facts: IComponents["Fact"][];
    all_decks: IComponents["Deck"][];
    all_facts: IComponents["Fact"][];
    set_type: "normal" | "test" | "post_test";
    num_facts: number;
    num_unstudied: number;
    user: IComponents["User"];
    short_description: string;
    expanded_description: string;
    is_first_pass: string;
    needs_restudy?: boolean;
  };
}
