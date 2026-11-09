import { useState } from "react"
import { Link } from "react-router"

function Register() {
	const [username, setUsername] = useState('')
	const [password, setPassword] = useState('')
	const [email, setEmail] = useState('')
	const [passwordConf, setPasswordConf] = useState('')
	const [error, setError] = useState('')
	const [fieldErrors, setFieldErrors] = useState({})
	const [message, setMessage] = useState('')
	const [isSubmitting, setIsSubmitting] = useState(false)

	const handleSubmit = async (event) => {
		event.preventDefault()
		setError('')
		setFieldErrors({})
		setMessage('')
		setIsSubmitting(true)

		try {
			const response = await fetch(
				`${import.meta.env.VITE_API_BASE_URL}/auth/register/`,
				{
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({
						username,
						email,
						password,
						password_confirm: passwordConf,
					}),
				},
			)

			const data = await response.json()
			if (!response.ok) {
				if (response.status === 400) {
					setFieldErrors(data)
					setError('Please correct the errors below.')
				} else {
					setError('Unable to register. Please try again later.')
				}
				return
			}

			setPassword('')
			setPasswordConf('')
			setMessage('Account created. Please sign in.')
		} catch {
			setError('Unable to complete registration. Please try again.')
		} finally {
			setIsSubmitting(false)
		}
	}

	return (
		<form className="register-form" onSubmit={handleSubmit}>
			<h2>Register</h2>
			{message && <p role="status">{message}</p>}
			{error && <p role="alert">{error}</p>}
			<label htmlFor="username">Username</label>
			<input
				id="username"
				name="username"
				value={username}
				onChange={(event) => setUsername(event.target.value)}
				aria-invalid={Boolean(fieldErrors.username)}
				aria-describedby={fieldErrors.username ? 'username-error' : undefined}
				required
			/>
			{fieldErrors.username && <p id="username-error">{fieldErrors.username.join(' ')}</p>}
			<label htmlFor="email">Email</label>
			<input
				id="email"
				name="email"
				type="email"
				value={email}
				onChange={(event) => setEmail(event.target.value)}
				aria-invalid={Boolean(fieldErrors.email)}
				aria-describedby={fieldErrors.email ? 'email-error' : undefined}
			/>
			{fieldErrors.email && <p id="email-error">{fieldErrors.email.join(' ')}</p>}
			<label htmlFor="password">Password</label>
			<input
				id="password"
				name="password"
				type="password"
				autoComplete="new-password"
				value={password}
				onChange={(event) => setPassword(event.target.value)}
				aria-invalid={Boolean(fieldErrors.password)}
				aria-describedby={fieldErrors.password ? 'password-error' : undefined}
				required
			/>
			{fieldErrors.password && <p id="password-error">{fieldErrors.password.join(' ')}</p>}
			<label htmlFor="password-confirm">Confirm password</label>
			<input
				id="password-confirm"
				name="password-confirm"
				type="password"
				autoComplete="new-password"
				value={passwordConf}
				onChange={(event) => setPasswordConf(event.target.value)}
				aria-invalid={Boolean(fieldErrors.password_confirm)}
				aria-describedby={fieldErrors.password_confirm ? 'password-confirm-error' : undefined}
				required
			/>
			{fieldErrors.password_confirm && <p id="password-confirm-error">{fieldErrors.password_confirm.join(' ')}</p>}
			<button type="submit" disabled={isSubmitting}>
				{isSubmitting ? 'Creating account...' : 'Create account'}
			</button>
			<Link to="/login">Back to sign in</Link>
		</form>
	)

}

export default Register
