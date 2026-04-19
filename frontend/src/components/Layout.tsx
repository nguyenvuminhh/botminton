import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import type { ReactNode } from 'react'

const navItems = [
  { to: '/', label: 'Home' },
  { to: '/periods', label: 'Periods' },
  { to: '/shuttlecocks', label: 'Shuttlecocks' },
  { to: '/settings', label: 'Settings' },
]

export default function Layout({ children }: { children: ReactNode }) {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      <nav
        style={{
          width: 200,
          background: '#1a1a2e',
          color: '#fff',
          display: 'flex',
          flexDirection: 'column',
          padding: '1rem 0',
        }}
      >
        <div style={{ padding: '0 1rem 1.5rem', fontSize: 18, fontWeight: 700 }}>
          🏸 Botminton
        </div>
        {navItems.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            style={({ isActive }) => ({
              padding: '0.6rem 1rem',
              color: isActive ? '#60a5fa' : '#cbd5e1',
              textDecoration: 'none',
              background: isActive ? 'rgba(255,255,255,0.07)' : 'transparent',
            })}
          >
            {label}
          </NavLink>
        ))}
        <button
          onClick={handleLogout}
          style={{
            marginTop: 'auto',
            margin: '1rem',
            padding: '0.5rem',
            background: 'transparent',
            color: '#94a3b8',
            border: '1px solid #334155',
            borderRadius: 4,
            cursor: 'pointer',
          }}
        >
          Logout
        </button>
      </nav>
      <main style={{ flex: 1, padding: '2rem', background: '#f8fafc' }}>{children}</main>
    </div>
  )
}
