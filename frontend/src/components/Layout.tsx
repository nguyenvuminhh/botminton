import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import type { ReactNode } from 'react'

const navItems = [
  { to: '/', label: 'Home', glyph: '🏠' },
  { to: '/periods', label: 'Periods', glyph: '🗓️' },
  { to: '/shuttlecocks', label: 'Shuttlecocks', glyph: '🏸' },
  { to: '/settings', label: 'Settings', glyph: '⚙️' },
]

export default function Layout({ children }: { children: ReactNode }) {
  const { logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="sidebar-brand-logo">🏸</span>
          <span>Botminton</span>
        </div>
        <nav className="nav-list">
          {navItems.map(({ to, label, glyph }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) => 'nav-item' + (isActive ? ' active' : '')}
            >
              <span className="nav-glyph">{glyph}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="sidebar-user">Admin console</div>
          <button onClick={handleLogout} className="btn btn-ghost" style={{ width: '100%' }}>
            Log out
          </button>
        </div>
      </aside>
      <main className="main">
        <div className="page">{children}</div>
      </main>
    </div>
  )
}
