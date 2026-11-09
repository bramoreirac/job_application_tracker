import { useEffect, useState } from 'react'
import './App.css'
import Login from './pages/Login.jsx'
import Applications from './pages/Applications.jsx'
import Register from './pages/Register.jsx'
import { Routes, Route, Navigate } from 'react-router'

function App() {
  const [health, setHealth] = useState('Checking API…')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [token, setToken] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    const controller = new AbortController()

    async function checkHealth() {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL}/health/`,
          { signal: controller.signal },
        )
        if (!response.ok) throw new Error(`HTTP ${response.status}`)

        const data = await response.json()
        setHealth(data.status)
      } catch (error) {
        if (error.name !== 'AbortError') setHealth('API unavailable')
      }
    }
    checkHealth()
    return () => controller.abort()
  }, [])

  const handleLogout = async () => {
    setError('')
    setIsSubmitting(true)

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/auth/logout/`,
        {
          method: 'POST',
          headers: { Authorization: `Token ${token}` },
        },
      )

      if (!response.ok && response.status !== 401) {
        setError('Unable to sign out. Please try again.')
        return
      }

      setToken(null)
      setMessage(response.status === 401
        ? 'Your session has ended. Please sign in again.'
        : 'Signed out successfully.')
    } catch {
      setError('Unable to reach the server. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="health-page">
      <h1>Job Application Tracker</h1>
      <p>Backend status: <strong>{health}</strong></p>

      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />

        <Route
          path="/login"
          element={
            token ? (
              <Navigate to="/applications" replace />
            ) : (
              <Login
                message={message}
                setMessage={setMessage}
                onLogin={(newToken) => {
                  setToken(newToken)
                  setMessage('Signed in successfully.')
                }}
              />
            )
          }
        />
        <Route
          path="/applications"
          element={
            token ? (
              <Applications
                message={message}
                error={error}
                isSubmitting={isSubmitting}
                handleLogout={handleLogout}
              />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/register"
          element={
            token ? (
              <Navigate to="/applications" replace />
            ) : (
              <Register />
            )
          }
        />
      </Routes>
    </main>
  )
}

export default App
