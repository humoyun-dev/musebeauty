import type { AuthProvider } from "@refinedev/core";

import { apiFetch, HttpError, TOKEN_KEY } from "./apiClient";

export const authProvider: AuthProvider = {
  login: async ({ username, password }) => {
    try {
      const data = await apiFetch<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: { username, password },
      });
      localStorage.setItem(TOKEN_KEY, data.access_token);
      return { success: true, redirectTo: "/" };
    } catch (e) {
      const msg = e instanceof HttpError ? e.message : "Login amalga oshmadi";
      return {
        success: false,
        error: { name: "Login xatosi", message: msg },
      };
    }
  },

  logout: async () => {
    localStorage.removeItem(TOKEN_KEY);
    return { success: true, redirectTo: "/login" };
  },

  check: async () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) return { authenticated: true };
    return { authenticated: false, redirectTo: "/login" };
  },

  onError: async (error) => {
    if (error?.statusCode === 401) {
      return { logout: true, redirectTo: "/login", error };
    }
    return {};
  },

  getIdentity: async () => {
    try {
      return await apiFetch<{ id: number; username: string; role: string }>(
        "/auth/me",
      );
    } catch {
      return null;
    }
  },

  getPermissions: async () => {
    return null;
  },
};
