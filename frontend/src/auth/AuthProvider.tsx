import { useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { authApi, type User } from '@/api/auth'
import { setUnauthorizedHandler, tokenStore } from '@/api/client'
import { AuthContext } from './useAuth'

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(() => tokenStore.get() !== null)

  const logout = useCallback(() => {
    tokenStore.clear()
    setUser(null)
    queryClient.clear() // drop cached salary data
  }, [queryClient])

  useEffect(() => {
    setUnauthorizedHandler(logout)
    return () => setUnauthorizedHandler(null)
  }, [logout])

  useEffect(() => {
    if (!tokenStore.get()) return
    authApi
      .me()
      .then(setUser)
      .catch(() => tokenStore.clear())
      .finally(() => setChecking(false))
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    tokenStore.set(await authApi.login(username, password))
    setUser(await authApi.me())
  }, [])

  const value = useMemo(() => ({ user, checking, login, logout }), [user, checking, login, logout])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
