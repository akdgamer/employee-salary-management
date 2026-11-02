import { api } from './client'

export interface User {
  id: number
  username: string
}

export const authApi = {
  login: (username: string, password: string) =>
    api
      .post<{ access_token: string }>('/auth/login', { username, password })
      .then((r) => r.data.access_token),
  me: () => api.get<User>('/auth/me').then((r) => r.data),
}
