import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import MoneyMatrix from '../components/MoneyMatrix'

interface MatrixPayload {
  period: { start_date: string; end_date: string | null }
  sessions: { id: string; date: string; total_money: number }[]
  participants_by_session: Record<string, {
    user_telegram_id: string
    user_name: string | null
    additional_participants: number
  }[]>
  shuttlecock_total: number
  shuttlecock_tubes: number
  total_period_money: number
  personal_report: {
    person_id: string
    telegram_user_name: string
    full_name: string | null
    period_money: number
  }[]
  users: {
    telegram_id: string
    telegram_user_name: string | null
    full_name: string | null
  }[]
}

export default function SharedPeriod() {
  const { token = '' } = useParams<{ token: string }>()
  const [data, setData] = useState<MatrixPayload | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    axios
      .get<MatrixPayload>(`/api/public/periods/${token}/matrix`)
      .then((r) => { setData(r.data); setError('') })
      .catch(() => setError('This link is invalid or has expired.'))
      .finally(() => setLoading(false))
  }, [token])

  return (
    <div style={{ minHeight: '100svh', padding: '32px 16px 64px' }}>
      <div style={{ maxWidth: 1400, margin: '0 auto' }}>
        <div className="page-header">
          <div
            className="sidebar-brand-logo"
            style={{ width: 40, height: 40, fontSize: 20, borderRadius: 12 }}
          >
            🏸
          </div>
          <div>
            <h1 style={{ marginBottom: 2 }}>Botminton · Period summary</h1>
            {data && (
              <span className="page-subtitle">
                {data.period.start_date} → {data.period.end_date ?? 'open'}
              </span>
            )}
          </div>
          {data && (
            <div className="page-header-actions">
              <span className="pill pill-accent">Total €{data.total_period_money.toFixed(2)}</span>
            </div>
          )}
        </div>

        {loading && <div className="card empty-state">Loading…</div>}
        {error && <div className="card"><div className="error-banner" style={{ marginBottom: 0 }}>{error}</div></div>}

        {data && (
          <div className="card">
            <MoneyMatrix
              sessions={data.sessions}
              participantsBySession={data.participants_by_session}
              shuttlecockTotal={data.shuttlecock_total}
              shuttlecockTubes={data.shuttlecock_tubes}
              totalPeriodMoney={data.total_period_money}
              personalReport={data.personal_report}
              users={data.users}
            />
          </div>
        )}
      </div>
    </div>
  )
}
