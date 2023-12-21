import axios, { CancelTokenStatic } from "axios";
import { apiUrl } from "@/env";
import { IComponents } from "./interfaces";
import { endOfDay, format, parse, startOfDay } from "date-fns";

const CancelToken = axios.CancelToken;
let cancel;

function authHeaders(token: string) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    cancelToken: new CancelToken(function executor(c) {
      cancel = c;
    }),
  };
}

export const api = {
  async logInGetToken(username: string, password: string) {
    const params = new URLSearchParams();
    params.append("username", username);
    params.append("password", password);

    return axios.post(`${apiUrl}/api/login/access-token`, params);
  },
  async getMe(token: string) {
    return axios.get<IComponents["User"]>(`${apiUrl}/api/users/me`, authHeaders(token));
  },
  async updateMe(token: string, data: IComponents["UserUpdate"]) {
    return axios.put<IComponents["User"]>(
      `${apiUrl}/api/users/me`,
      data,
      authHeaders(token),
    );
  },
  async getUsers(token: string) {
    return axios.get<IComponents["User"][]>(`${apiUrl}/api/users/`, authHeaders(token));
  },
  async updateUser(
    token: string,
    userId: number,
    data: IComponents["SuperUserUpdate"],
  ) {
    return axios.put(`${apiUrl}/api/users/${userId}`, data, authHeaders(token));
  },
  async createUser(token: string, data: IComponents["SuperUserCreate"]) {
    return axios.post(`${apiUrl}/api/users/`, data, authHeaders(token));
  },
  async createUserOpen(token: string, data: IComponents["UserCreate"]) {
    return axios.post(`${apiUrl}/api/users/open`, data, authHeaders(token));
  },
  async passwordRecovery(email: string) {
    return axios.post(`${apiUrl}/api/password-recovery/${email}`);
  },
  async resetPassword(password: string, token: string) {
    return axios.post(`${apiUrl}/api/reset-password/`, {
      new_password: password, // eslint-disable-line @typescript-eslint/camelcase
      token,
    });
  },
  async getFacts(token: string, data: IComponents["FactSearch"]) {
    cancel();
    let url = ``;
    if (data.all) {
      url += `&all=${data.all}`;
    }
    if (data.skip) {
      url += `&skip=${data.skip}`;
    }
    if (data.limit) {
      url += `&limit=${data.limit}`;
    }
    if (data.text) {
      url += `&text=${data.text}`;
    }
    if (data.answer) {
      url += `&answer=${data.answer}`;
    }
    if (data.category) {
      url += `&category=${data.category}`;
    }
    if (data.deck_id) {
      url += `&deck_id=${data.deck_id}`;
    }
    if (data.deck_ids) {
      for (const eachId in data.deck_ids) {
        url += `&deck_ids=${data.deck_ids[eachId]}`;
      }
    }
    if (data.marked) {
      url += `&marked=${data.marked}`;
    }
    if (data.suspended) {
      url += `&suspended=${data.suspended}`;
    }
    if (data.reported) {
      url += `&reported=${data.reported}`;
    }
    url = url.slice(1);
    return axios.get<IComponents["FactBrowse"]>(
      `${apiUrl}/api/facts/?${url}`,
      authHeaders(token),
    );
  },
  async getMnemonics(token: string, data: IComponents["MnemonicSearch"]) {
    return axios.post(`${apiUrl}/api/mnemonics/feedback_ids`, data, authHeaders(token));
  },
  async getStudyFacts(
    token: string,
    deckIds: number[],
    selectedNum: number,
    forceNew: boolean,
    isResume: boolean,
  ) {
    let url = `${apiUrl}/api/study/`;
    url += `?`;
    if (deckIds.length > 0) {
      for (const eachId in deckIds) {
        url += `deck_ids=${deckIds[eachId]}&`;
      }
      url = url.slice(0, -1);
    }
    url += `&limit=${selectedNum}`;
    url += `&force_new=${forceNew}`;
    url += `&is_resume=${isResume}`;
    return axios.get<IComponents["StudySet"]>(url, authHeaders(token));
  },
  async checkIfInTestMode(
    token: string,
  ) {
    const url = `${apiUrl}/api/study/test_mode`;
    return axios.get<boolean>(url, authHeaders(token)); 
  },
  async createFact(token: string, data: IComponents["FactCreate"]) {
    return axios.post(`${apiUrl}/api/facts/`, data, authHeaders(token));
  },
  async createDeck(token: string, data: IComponents["DeckCreate"]) {
    return axios.post(`${apiUrl}/api/decks/`, data, authHeaders(token));
  },
  async deleteDeck(token: string, deckId: number) {
    return axios.delete(`${apiUrl}/api/decks/${deckId}`, authHeaders(token));
  },
  async suspendFact(token: string, factId: number) {
    const url = `${apiUrl}/api/facts/suspend/${factId}`;
    return axios.put<IComponents["Fact"]>(url, null, authHeaders(token));
  },
  async reportFact(token: string, factId: number, data: IComponents["FactToReport"]) {
    const url = `${apiUrl}/api/facts/report/${factId}`;
    return axios.put<IComponents["Fact"]>(url, data, authHeaders(token));
  },
  async clearReportFact(token: string, factId: number) {
    const url = `${apiUrl}/api/facts/report/${factId}`;
    return axios.delete<IComponents["Fact"]>(url, authHeaders(token));
  },
  async clearReportsFact(token: string, factId: number) {
    const url = `${apiUrl}/api/facts/report/all/${factId}`;
    return axios.delete<IComponents["Fact"]>(url, authHeaders(token));
  },
  async markFact(token: string, factId: number) {
    const url = `${apiUrl}/api/facts/mark/${factId}`;
    return axios.put<IComponents["Fact"]>(url, null, authHeaders(token));
  },
  async deleteFact(token: string, factId: number) {
    const url = `${apiUrl}/api/facts/${factId}`;
    return axios.delete<IComponents["Fact"]>(url, authHeaders(token));
  },
  async getPublicDecks(token: string) {
    return axios.get<IComponents["Deck"][]>(
      `${apiUrl}/api/decks/public`,
      authHeaders(token),
    );
  },
  async assignDecks(token: string, deckIds: number[]) {
    let url = `${apiUrl}/api/decks/`;
    if (deckIds.length > 0) {
      url += `?`;
      for (const eachId in deckIds) {
        url += `deck_ids=${deckIds[eachId]}&`;
      }
      url = url.slice(0, -1);
    }
    return axios.put(url, null, authHeaders(token));
  },
  async evalAnswer(token: string, factId: number, data: string) {
    return axios.get<boolean>(
      `${apiUrl}/api/study/evaluate?fact_id=${factId}&typed=${data}`,
      authHeaders(token),
    );
  },
  async updateSchedule(
    token: string,
    studyset_id: number,
    data: IComponents["Schedule"][],
  ) {
    return axios.put(
      `${apiUrl}/api/study/?studyset_id=${studyset_id}`,
      data,
      authHeaders(token),
    );
  },

  async updateFact(token: string, id: number, data: IComponents["FactUpdate"]) {
    return axios.put(`${apiUrl}/api/facts/${id}`, data, authHeaders(token));
  },

  async createMnemonicFeedbackLog(token: string, data: IComponents["MnemonicCreate"]) {
    return axios.post(`${apiUrl}/api/mnemonics/`, data, authHeaders(token));
  },

  async uploadFacts(token: string, data: IComponents["FactUpload"]) {
    let url = `${apiUrl}/api/facts/upload/txt`;
    if (data.headers.length > 0) {
      url += `?`;
      for (const header of data.headers) {
        url += `headers=${header}&`;
      }
      url = url.slice(0, -1);
    }
    const formData = new FormData();
    formData.append("upload_file", data.upload_file);
    formData.append("deck_id", data.deck_id.toString());
    if (data.delimeter !== undefined) {
      formData.append("delimeter", data.delimeter);
    }

    return axios.post(url, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    });
  },
  async getUserStats(token: string, data: IComponents["StatSearch"]) {
    let url = ``;

    if (data.date_start) {
      url += `&date_start=${format(
        startOfDay(parse(data.date_start, "yyyy-MM-dd", new Date())),
        "yyyy-MM-dd'T'HH:mm:ss.SSSxxxx",
      )}`;
    }
    if (data.date_end) {
      url += `&date_end=${format(
        endOfDay(parse(data.date_end, "yyyy-MM-dd", new Date())),
        "yyyy-MM-dd'T'HH:mm:ss.SSSxxxx",
      )}`;
    }
    if (data.deck_id) {
      url += `&deck_id=${data.deck_id}`;
    }
    url = url.slice(1);
    return axios.get<IComponents["Statistics"]>(
      `${apiUrl}/api/statistics/?${url}`,
      authHeaders(token),
    );
  },
  async getHomeStats(token: string) {
    return axios.get<IComponents["Statistics"][]>(
      `${apiUrl}/api/statistics/home`,
      authHeaders(token),
    );
  },
  async getSavedStats(token: string) {
    return axios.get<IComponents["Statistics"][]>(
      `${apiUrl}/api/statistics/saved`,
      authHeaders(token),
    );
  },
  async getLeaderboard(token: string, data: IComponents["LeaderboardSearch"]) {
    let url = ``;
    if (data.date_start) {
      url += `&date_start=${format(
        startOfDay(parse(data.date_start, "yyyy-MM-dd", new Date())),
        "yyyy-MM-dd'T'HH:mm:ss.SSSxxxx",
      )}`;
    }
    if (data.date_end) {
      url += `&date_end=${format(
        endOfDay(parse(data.date_end, "yyyy-MM-dd", new Date())),
        "yyyy-MM-dd'T'HH:mm:ss.SSSxxxx",
      )}`;
    }
    if (data.deck_id) {
      url += `&deck_id=${data.deck_id}`;
    }
    if (data.rank_type) {
      url += `&rank_type=${data.rank_type}`;
    }
    if (data.skip) {
      url += `&skip=${data.skip}`;
    }
    if (data.limit) {
      url += `&limit=${data.limit}`;
    }
    if (data.min_studied) {
      url += `&min_studied=${data.min_studied}`;
    }
    url = url.slice(1);
    return axios.get<IComponents["Leaderboard"]>(
      `${apiUrl}/api/statistics/leaderboard?${url}`,
      authHeaders(token),
    );
  },
};
