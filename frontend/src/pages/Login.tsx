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
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      gap: '1.5rem',
      background: '#f8fafc',
    }}>
      <h1 style={{ fontSize: 28, fontWeight: 700 }}>🏸 Botminton Admin</h1>

      {step === 'request' ? (
        <>
          <p style={{ color: '#64748b' }}>Send a one-time code to your Telegram</p>
          <button onClick={handleRequestOtp} disabled={loading} style={btnStyle}>
            {loading ? 'Sending…' : 'Send OTP via Telegram'}
          </button>
        </>
      ) : (
        <form onSubmit={handleVerify} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', alignItems: 'center' }}>
          <p style={{ color: '#64748b' }}>Enter the 6-digit code sent to your Telegram</p>
          <input
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={otp}
            onChange={e => setOtp(e.target.value.replace(/\D/g, ''))}
            placeholder="000000"
            autoFocus
            style={inputStyle}
          />
          <button type="submit" disabled={loading || otp.length !== 6} style={btnStyle}>
            {loading ? 'Verifying…' : 'Verify'}
          </button>
          <button type="button" onClick={() => { setStep('request'); setOtp(''); setError('') }} style={linkStyle}>
            Resend code
          </button>
        </form>
      )}

      {error && <p style={{ color: '#ef4444' }}>{error}</p>}
    </div>
  )
}

const btnStyle: React.CSSProperties = {
  padding: '0.6rem 1.4rem',
  fontSize: 16,
  borderRadius: 8,
  border: 'none',
  background: '#2563eb',
  color: '#fff',
  cursor: 'pointer',
}

const inputStyle: React.CSSProperties = {
  fontSize: 28,
  letterSpacing: '0.4em',
  textAlign: 'center',
  width: 180,
  padding: '0.5rem',
  borderRadius: 8,
  border: '1px solid #cbd5e1',
}

const linkStyle: React.CSSProperties = {
  background: 'none',
  border: 'none',
  color: '#2563eb',
  cursor: 'pointer',
  fontSize: 14,
}
