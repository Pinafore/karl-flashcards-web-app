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
  marked: boolean;
}

export interface IBrowser {
  facts: IComponents["Fact"][];
  totalFacts: number;
}

export enum Permission {
  owner = "owner",
  viewer = "viewer",
}
export interface IComponents {
  Deck: { title: string; public: boolean; id: number };
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
    permission?: Permission;
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
  FactSearch: {
    skip?: number;
    limit?: number;
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
  }
  HTTPValidationError: {
    detail?: IComponents["ValidationError"][];
  };
  Msg: { msg: string };
  Schedule: {
    fact_id: number;
    typed: string;
    response: boolean;
    elapsed_seconds_text: number;
    elapsed_seconds_answer: number;
  };
  Statistics: {
    new_known_rate?: number;
    review_known_rate?: number;
    new_facts: number;
    reviewed_facts: number;
    total_seen: number;
    total_seconds: number;
    user: IComponents["User"];
  };
  SuperUserCreate: {
    email: string;
    username: string;
    is_active?: boolean;
    repetition_model?: "leitner" | "sm-2" | "karl";
    password: string;
    is_superuser?: boolean;
  };
  SuperUserUpdate: {
    email?: string;
    username?: string;
    is_active?: boolean;
    repetition_model?: "leitner" | "sm-2" | "karl";
    password?: string;
    default_deck_id?: number;
    is_superuser?: boolean;
  };
  Token: { access_token: string; token_type: string };
  User: {
    email: string;
    username: string;
    is_active: boolean;
    repetition_model?: "leitner" | "sm-2" | "karl";
    id: number;
    is_superuser: boolean;
    default_deck: IComponents["Deck"];
    decks?: IComponents["Deck"][];
    suspended_facts?: IComponents["Fact"][];
    facts?: IComponents["Fact"][];
  };
  UserCreate: {
    email: string;
    username: string;
    is_active?: boolean;
    repetition_model?: "leitner" | "sm-2" | "karl";
    password: string;
  };
  UserUpdate: {
    email?: string;
    username?: string;
    is_active?: boolean;
    repetition_model?: "leitner" | "sm-2" | "karl";
    password?: string;
    default_deck_id?: number;
  };
  ValidationError: { loc: string[]; msg: string; type: string };
}
