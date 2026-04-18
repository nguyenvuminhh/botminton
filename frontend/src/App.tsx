import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './auth'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Periods from './pages/Periods'
import Sessions from './pages/Sessions'
import Players from './pages/Players'
import Payments from './pages/Payments'
import Venues from './pages/Venues'
import Shuttlecocks from './pages/Shuttlecocks'
import Settings from './pages/Settings'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuth()
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/*"
            element={
              <PrivateRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/periods" element={<Periods />} />
                    <Route path="/sessions" element={<Sessions />} />
                    <Route path="/players" element={<Players />} />
                    <Route path="/payments" element={<Payments />} />
                    <Route path="/venues" element={<Venues />} />
                    <Route path="/shuttlecocks" element={<Shuttlecocks />} />
                    <Route path="/settings" element={<Settings />} />
                  </Routes>
                </Layout>
              </PrivateRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
