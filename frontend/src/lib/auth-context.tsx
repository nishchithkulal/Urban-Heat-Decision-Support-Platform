"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import type { TokenPair, UserRead } from "./types";
import { api } from "./api";

const STORAGE_KEY = "heatpilot.tokens";

interface AuthContextValue {
  accessToken: string | null;
  user: UserRead | null;
  isLoading: boolean;
  login: (tokens: TokenPair) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// Tokens live in localStorage, not an httpOnly cookie. That is a real tradeoff, not
// an oversight: a cookie-based session would need a Next.js route-handler proxy in
// front of every authenticated backend call (to attach/refresh the cookie server-side)
// and CSRF protection for it, which is a bigger surface than Phase 8's "integrate the
// frontend with the backend API" scope justifies. Because the backend's XSS surface
// here is a single-page dashboard with no third-party script execution, the risk this
// accepts is limited -- but it is a real one, and the cookie+BFF pattern is the
// documented next step if this app grows a plugin/widget surface that could run
// untrusted script.
export function AuthProvider({ children }: { children: ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserRead | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    // Deferred via a microtask so no setState call here executes synchronously
    // during the effect's own commit: an async function body runs synchronously up
    // to its first `await`, which react-hooks/set-state-in-effect (new in
    // eslint-config-next 16 / React 19) flags even when reached through a called
    // function rather than written inline.
    queueMicrotask(async () => {
      const stored = window.localStorage.getItem(STORAGE_KEY);
      if (!stored) {
        if (!cancelled) setIsLoading(false);
        return;
      }
      const tokens = JSON.parse(stored) as TokenPair;
      try {
        const profile = await api.me(tokens.access_token);
        if (!cancelled) {
          setAccessToken(tokens.access_token);
          setUser(profile);
        }
      } catch {
        window.localStorage.removeItem(STORAGE_KEY);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    });

    return () => {
      cancelled = true;
    };
  }, []);

  function login(tokens: TokenPair) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens));
    setAccessToken(tokens.access_token);
    api.me(tokens.access_token).then(setUser).catch(() => setUser(null));
  }

  function logout() {
    window.localStorage.removeItem(STORAGE_KEY);
    setAccessToken(null);
    setUser(null);
  }

  const value = useMemo(
    () => ({ accessToken, user, isLoading, login, logout }),
    [accessToken, user, isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
