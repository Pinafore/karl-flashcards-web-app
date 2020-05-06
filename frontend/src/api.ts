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
  async getFacts(token: string) {
    return axios.get<IComponents["Fact"][]>(
      `${apiUrl}/api/facts/`,
      authHeaders(token)
    );
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
  async suspendFact(token: string, factId: number, undo?: boolean) {
    let url = `${apiUrl}/api/facts/suspend/${factId}`;
    if (undo) {
      url += undo;
    }
    return axios.put<IComponents["Fact"]>(url, null, authHeaders(token));
  },
  async reportFact(token: string, factId: number, undo?: boolean) {
    let url = `${apiUrl}/api/facts/report/${factId}`;
    if (undo) {
      url += undo;
    }
    return axios.put<IComponents["Fact"]>(url, null, authHeaders(token));
  },
  async deleteFact(token: string, factId: number, undo?: boolean) {
    let url = `${apiUrl}/api/facts/${factId}`;
    if (undo) {
      url += undo;
    }
    return axios.delete<IComponents["Fact"]>(url, authHeaders(token));
  },
  async getPublicDecks(token: string) {
    return axios.get<IComponents["Deck"][]>(
      `${apiUrl}/api/decks/public/`,
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
};
