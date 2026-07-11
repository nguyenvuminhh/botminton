import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth-context'

type Step = 'request' | 'verify'
interface AdminOption {
  telegram_id: string
  telegram_user_name: string | null
  full_name: string | null
  is_admin: boolean
  is_super_admin: boolean
}

function adminLabel(admin: AdminOption) {
  const name = admin.full_name || (admin.telegram_user_name ? '@' + admin.telegram_user_name : admin.telegram_id)
  return admin.is_super_admin ? `${name} (super admin)` : name
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState<Step>('request')
  const [admins, setAdmins] = useState<AdminOption[]>([])
  const [selectedTelegramId, setSelectedTelegramId] = useState('')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const selectedAdmin = admins.find((admin) => admin.telegram_id === selectedTelegramId)

  useEffect(() => {
    let cancelled = false
    api.get<AdminOption[]>('/auth/admins')
      .then((response) => {
        if (cancelled) return
        setAdmins(response.data)
        setSelectedTelegramId((current) => current || response.data[0]?.telegram_id || '')
      })
      .catch(() => {
        if (!cancelled) setError('Failed to load admins.')
      })
    return () => { cancelled = true }
  }, [])

  async function handleRequestOtp() {
    if (!selectedTelegramId) {
      setError('Choose who you are first.')
      return
    }
    setLoading(true)
    setError('')
    try {
      await api.post('/auth/request-otp', { telegram_id: selectedTelegramId })
      setStep('verify')
    } catch {
      setError('Failed to send OTP. Check bot configuration.')
    } finally {
      setLoading(false)
    }
  }

  async function handleVerify(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/auth/verify-otp', { telegram_id: selectedTelegramId, otp })
      login(data.access_token)
      navigate('/', { replace: true })
    } catch {
      setError('Invalid or expired OTP.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <div className="login-logo">🏸</div>
        <h1 className="login-title">Botminton admin</h1>
        <p className="login-subtitle">Weekly sessions, batches & billing — at a glance.</p>

        {step === 'request' ? (
          <div className="stack">
            <div className="field">
              <label className="field-label">Who are you?</label>
              <select
                className="select"
                value={selectedTelegramId}
                onChange={(event) => setSelectedTelegramId(event.target.value)}
                disabled={loading || admins.length === 0}
              >
                {admins.map((admin) => (
                  <option key={admin.telegram_id} value={admin.telegram_id}>
                    {adminLabel(admin)}
                  </option>
                ))}
              </select>
            </div>
            <p className="muted text-small">We'll send a one-time code to the selected Telegram user.</p>
            <button
              onClick={handleRequestOtp}
              disabled={loading || !selectedTelegramId}
              className="btn btn-primary login-btn"
            >
              {loading ? 'Sending…' : 'Send code via Telegram'}
            </button>
          </div>
        ) : (
          <form onSubmit={handleVerify} className="stack">
            <p className="muted text-small">
              Enter the 6-digit code sent to {selectedAdmin ? adminLabel(selectedAdmin) : 'Telegram'}.
            </p>
            <input
              type="text"
              inputMode="numeric"
              maxLength={6}
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
              placeholder="••••••"
              autoFocus
              className="otp-input"
            />
            <button
              type="submit"
              disabled={loading || otp.length !== 6}
              className="btn btn-primary login-btn"
            >
              {loading ? 'Verifying…' : 'Verify & sign in'}
            </button>
            <button
              type="button"
              onClick={() => { setStep('request'); setOtp(''); setError('') }}
              className="link-btn"
            >
              Choose another admin or resend
            </button>
          </form>
        )}

        {error && <div className="error-banner" style={{ marginTop: 18, marginBottom: 0 }}>{error}</div>}
      </div>
    </div>
  )
}
