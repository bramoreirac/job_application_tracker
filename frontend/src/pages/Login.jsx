import { useState } from 'react'

function Login({ message, setMessage, onLogin }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setMessage('')
    setIsSubmitting(true)

    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/auth/login/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, password }),
        },
      )

      if (!response.ok) {
        setError(response.status === 401
          ? 'Unable to sign in. Check your credentials and try again.'
          : 'Sign in is unavailable. Please try again later.')
        return
      }

      const data = await response.json()
      setPassword('')
      onLogin(data.token)
    } catch {
      setError('Unable to reach the server. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <h2>Sign in</h2>
      {message && <p role="status">{message}</p>}
      <label htmlFor="username">Username</label>
      <input
        id="username"
        name="username"
        autoComplete="username"
        value={username}
        onChange={(event) => setUsername(event.target.value)}
        required
      />
      <label htmlFor="password">Password</label>
      <input
        id="password"
        name="password"
        type="password"
        autoComplete="current-password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        required
      />
      {error && <p role="alert">{error}</p>}
      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Signing in…' : 'Sign in'}
      </button>
    </form>
  )
}

export default Login
