import axios from "axios";
import { apiUrl } from "@/env";
import { IComponents } from "./interfaces";

function authHeaders(token: string) {
  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
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
    let url = `${apiUrl}/api/facts/?`
    if (data.skip) {
      url += `&skip=${data.skip}`
    }
    if (data.limit) {
      url += `&limit=${data.limit}`
    }
    if (data.text) {
      url += `&text=${data.text}`
    }
    if (data.answer) {
      url += `&answer=${data.answer}`
    }
    if (data.category) {
      url += `&category=${data.category}`
    }
    if (data.deck_id) {
      url += `&deck_id=${data.deck_id}`
    }
    if (data.marked) {
      url += `&marked=${data.marked}`
    }
    if (data.suspended) {
      url += `&suspended=${data.suspended}`
    }
    if (data.reported) {
      url += `&reported=${data.reported}`
    }
    return axios.get<IComponents["FactBrowse"]>(url, authHeaders(token));
  },
  async getStudyFacts(token: string, deckIds: number[]) {
    let url = `${apiUrl}/api/study/`;
    if (deckIds.length > 0) {
      url += `?`;
      for (const eachId in deckIds) {
        url += `deck_ids=${deckIds[eachId]}&`;
      }
      url = url.slice(0, -1);
    }
    return axios.get<IComponents["Fact"][]>(url, authHeaders(token));
  },
  async createFact(token: string, data: IComponents["FactCreate"]) {
    return axios.post(`${apiUrl}/api/facts/`, data, authHeaders(token));
  },
  async createDeck(token: string, data: IComponents["DeckCreate"]) {
    return axios.post(`${apiUrl}/api/decks/`, data, authHeaders(token));
  },
  async suspendFact(token: string, factId: number) {
    const url = `${apiUrl}/api/facts/suspend/${factId}`;
    return axios.put<IComponents["Fact"]>(url, null, authHeaders(token));
  },
  async reportFact(token: string, factId: number) {
    const url = `${apiUrl}/api/facts/report/${factId}`;
    return axios.put<IComponents["Fact"]>(url, null, authHeaders(token));
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
  async updateSchedule(token: string, data: IComponents["Schedule"][]) {
    return axios.put(`${apiUrl}/api/study/`, data, authHeaders(token));
  },
  async updateFact(token: string, id: number, data: IComponents["FactUpdate"]) {
    return axios.put(`${apiUrl}/api/facts/${id}`, data, authHeaders(token));
  },
};
