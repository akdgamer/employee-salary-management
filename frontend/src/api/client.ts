import axios from 'axios'

const TOKEN_KEY = 'access_token'

/** The JWT lives in localStorage so a reload keeps the HR manager signed in. */
export const tokenStore = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (token: string) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1',
})

api.interceptors.request.use((config) => {
  const token = tokenStore.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let onUnauthorized: (() => void) | null = null

/** Called when an authenticated request gets a 401 (e.g. the token expired). */
export function setUnauthorizedHandler(handler: (() => void) | null) {
  onUnauthorized = handler
}

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    const isLoginAttempt = axios.isAxiosError(error) && error.config?.url === '/auth/login'
    if (axios.isAxiosError(error) && error.response?.status === 401 && !isLoginAttempt) {
      onUnauthorized?.()
    }
    return Promise.reject(error)
  },
)
