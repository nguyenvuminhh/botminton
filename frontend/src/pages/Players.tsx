import { useEffect, useState } from 'react'
import { api } from '../api'

interface User {
  id: string
  telegram_id: string
  telegram_user_name: string | null
  full_name: string | null
  is_admin: boolean
}

export default function Players() {
  const [users, setUsers] = useState<User[]>([])

  function load() {
    api.get<User[]>('/users').then((r) => setUsers(r.data))
  }

  useEffect(() => { load() }, [])

  async function handleDelete(telegramId: string) {
    if (!confirm(`Delete user ${telegramId}?`)) return
    await api.delete(`/users/${telegramId}`)
    load()
  }

  async function handleToggleAdmin(u: User) {
    await api.put(`/users/${u.telegram_id}`, { is_admin: !u.is_admin })
    load()
  }

  return (
    <div>
      <h2>Players</h2>
      <table style={tableStyle}>
        <thead>
          <tr>{['Telegram ID', 'Full Name', 'Username', 'Admin', ''].map((h) => <th key={h} style={thStyle}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td style={tdStyle}>{u.telegram_id}</td>
              <td style={tdStyle}>{u.full_name ?? '—'}</td>
              <td style={tdStyle}>{u.telegram_user_name ?? '—'}</td>
              <td style={tdStyle}>{u.is_admin ? '✅' : '—'}</td>
              <td style={{ ...tdStyle, display: 'flex', gap: '0.4rem' }}>
                <button onClick={() => handleToggleAdmin(u)} style={btnStyle}>
                  {u.is_admin ? 'Revoke admin' : 'Make admin'}
                </button>
                <button onClick={() => handleDelete(u.telegram_id)} style={{ ...btnStyle, background: '#ef4444' }}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const btnStyle: React.CSSProperties = { padding: '0.4rem 0.8rem', borderRadius: 4, border: 'none', background: '#3b82f6', color: '#fff', cursor: 'pointer', fontSize: 14 }
const tableStyle: React.CSSProperties = { width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8, overflow: 'hidden', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }
const thStyle: React.CSSProperties = { textAlign: 'left', padding: '0.75rem 1rem', background: '#f1f5f9', fontSize: 13, color: '#475569' }
const tdStyle: React.CSSProperties = { padding: '0.75rem 1rem', borderTop: '1px solid #f1f5f9', fontSize: 14 }
