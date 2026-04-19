import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'

type Step = 'request' | 'verify'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [step, setStep] = useState<Step>('request')
  const [otp, setOtp] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleRequestOtp() {
    setLoading(true)
    setError('')
    try {
      await api.post('/auth/request-otp')
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
      const { data } = await api.post('/auth/verify-otp', { otp })
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
            <p className="muted text-small">We'll send a one-time code to your Telegram.</p>
            <button
              onClick={handleRequestOtp}
              disabled={loading}
              className="btn btn-primary login-btn"
            >
              {loading ? 'Sending…' : 'Send code via Telegram'}
            </button>
          </div>
        ) : (
          <form onSubmit={handleVerify} className="stack">
            <p className="muted text-small">Enter the 6-digit code from your Telegram.</p>
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
              Resend code
            </button>
          </form>
        )}

        {error && <div className="error-banner" style={{ marginTop: 18, marginBottom: 0 }}>{error}</div>}
      </div>
    </div>
  )
}
