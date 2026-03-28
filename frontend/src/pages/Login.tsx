import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'

declare global {
  interface Window {
    onTelegramAuth: (user: Record<string, unknown>) => void
  }
}

export default function Login() {
  const { login, token } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (token) {
      navigate('/', { replace: true })
      return
    }

    const botUsername = import.meta.env.VITE_BOT_USERNAME
    if (!botUsername) {
      console.error('VITE_BOT_USERNAME is not set')
      return
    }

    window.onTelegramAuth = async (user) => {
      try {
        const { data } = await api.post('/auth/telegram', user)
        login(data.access_token)
        navigate('/', { replace: true })
      } catch (err: unknown) {
        const msg =
          err instanceof Error ? err.message : 'Authentication failed. Make sure you are the admin.'
        alert(msg)
      }
    }

    const script = document.createElement('script')
    script.src = 'https://telegram.org/js/telegram-widget.js?22'
    script.setAttribute('data-telegram-login', botUsername)
    script.setAttribute('data-size', 'large')
    script.setAttribute('data-onauth', 'onTelegramAuth(user)')
    script.setAttribute('data-request-access', 'write')
    script.async = true

    document.getElementById('tg-login-container')?.appendChild(script)

    return () => {
      document.getElementById('tg-login-container')?.replaceChildren()
    }
  }, [login, navigate, token])

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        gap: '1.5rem',
        background: '#f8fafc',
      }}
    >
      <h1 style={{ fontSize: 28, fontWeight: 700 }}>🏸 Botminton Admin</h1>
      <p style={{ color: '#64748b' }}>Sign in with your Telegram account</p>
      <div id="tg-login-container" />
    </div>
  )
}
