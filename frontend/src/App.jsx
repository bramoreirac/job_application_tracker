import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [health, setHealth] = useState('Checking API…')

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

  return (
    <main className="health-page">
      <h1>Job Application Tracker</h1>
      <p>Backend status: <strong>{health}</strong></p>
    </main>
  )
}

export default App
