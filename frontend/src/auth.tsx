import { useState } from 'react'
import type { ReactNode } from 'react'
import { AuthContext } from './auth-context'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('jwt'))

  function login(t: string) {
    localStorage.setItem('jwt', t)
    setToken(t)
  }

  function logout() {
    localStorage.removeItem('jwt')
    setToken(null)
  }

  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>
}
