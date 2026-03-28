import { useEffect, useState } from 'react'
import { api } from '../api'

interface Period {
  id: string
  start_date: string
  end_date: string | null
  total_money: number | null
}

interface Session {
  id: string
  date: string
  venue_name: string | null
  slots: number
  is_poll_open: boolean
}

function Card({ title, value }: { title: string; value: string | number | null }) {
  return (
    <div
      style={{
        background: '#fff',
        borderRadius: 8,
        padding: '1.5rem',
        boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
        minWidth: 180,
      }}
    >
      <div style={{ fontSize: 13, color: '#64748b', marginBottom: 8 }}>{title}</div>
      <div style={{ fontSize: 22, fontWeight: 700 }}>{value ?? '—'}</div>
    </div>
  )
}

export default function Dashboard() {
  const [period, setPeriod] = useState<Period | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [openSession, setOpenSession] = useState<Session | null>(null)

  useEffect(() => {
    api.get<Period>('/periods/current').then((r) => setPeriod(r.data)).catch(() => {})
    api.get<Session>('/sessions/current').then((r) => setSession(r.data)).catch(() => {})
    api.get<Session>('/sessions/open').then((r) => setOpenSession(r.data)).catch(() => {})
  }, [])

  return (
    <div>
      <h2 style={{ marginBottom: '1.5rem' }}>Dashboard</h2>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <Card title="Current period start" value={period?.start_date ?? null} />
        <Card title="Period end" value={period?.end_date ?? 'Open'} />
        <Card title="Today's session" value={session?.date ?? 'None'} />
        <Card title="Open poll" value={openSession ? openSession.date : 'None'} />
        <Card title="Session slots" value={session?.slots ?? null} />
        <Card title="Session venue" value={session?.venue_name ?? null} />
      </div>
    </div>
  )
}
