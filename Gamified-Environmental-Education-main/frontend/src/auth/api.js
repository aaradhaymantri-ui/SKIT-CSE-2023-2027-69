export const API_URL = import.meta.env.VITE_API_URL
  || `${window.location.protocol}//${window.location.hostname}:5000`;

let accessToken = null;
let refreshInFlight = null;

function saveUser(user) {
  localStorage.removeItem("authToken");
  localStorage.setItem("currentUser", JSON.stringify(user));
  localStorage.setItem("userName", user.name);
}

function clearSavedUser() {
  accessToken = null;
  localStorage.removeItem("currentUser");
  localStorage.removeItem("userName");
  localStorage.removeItem("authToken");
  window.dispatchEvent(new Event("ecoquest:session-expired"));
}

async function requestCsrfToken() {
  const response = await fetch(`${API_URL}/auth/csrf`, {
    credentials: "include",
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Please sign in again.");
  }
  return data.csrfToken;
}

export async function signIn(email, password) {
  const response = await fetch(`${API_URL}/signin`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Sign in failed.");
  }
  accessToken = data.accessToken;
  saveUser(data.user);
  return data.user;
}

async function rotateRefreshToken() {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    const csrfToken = await requestCsrfToken();
    const response = await fetch(`${API_URL}/auth/refresh`, {
      method: "POST",
      credentials: "include",
      headers: { "X-CSRF-Token": csrfToken },
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Your session has expired.");
    }
    accessToken = data.accessToken;
    saveUser(data.user);
    return data;
  })();
  try {
    return await refreshInFlight;
  } finally {
    refreshInFlight = null;
  }
}

export async function restoreSession() {
  try {
    const data = await rotateRefreshToken();
    return data.user;
  } catch {
    clearSavedUser();
    return null;
  }
}

export async function authFetch(url, options = {}) {
  if (!accessToken) {
    try {
      await rotateRefreshToken();
    } catch {
      // Let the protected API return its normal 401 response.
    }
  }

  const sendRequest = () => {
    const headers = new Headers(options.headers || {});
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
    return fetch(url, {
      ...options,
      headers,
      credentials: "include",
    });
  };

  let response = await sendRequest();
  if (response.status === 401) {
    try {
      await rotateRefreshToken();
      response = await sendRequest();
    } catch {
      clearSavedUser();
    }
  }
  return response;
}

export async function signOut() {
  try {
    const csrfToken = await requestCsrfToken();
    await fetch(`${API_URL}/auth/logout`, {
      method: "POST",
      credentials: "include",
      headers: { "X-CSRF-Token": csrfToken },
    });
  } finally {
    clearSavedUser();
  }
}
