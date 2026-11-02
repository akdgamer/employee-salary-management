import { createContext, useContext } from 'react'
import type { User } from '@/api/auth'

export interface AuthState {
  user: User | null
  /** True while a stored token is being checked on startup. */
  checking: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth must be used inside <AuthProvider>')
  return auth
}
