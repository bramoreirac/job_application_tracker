import { useEffect, useState } from "react";


function Applications({ token, message, error, isSubmitting, handleLogout }) {

	const [applications, setApplications] = useState([])
	const [isLoading, setIsLoading] = useState(true)

	useEffect(() => {
		const controller = new AbortController()

		async function loadApplications() {
			try {
				const response = await fetch(
					`${import.meta.env.VITE_API_BASE_URL}/applications/`,
					{
						headers: { Authorization: `Token ${token}` },
						signal: controller.signal,
					},
				)

				if (!response.ok) throw new Error(`HTTP ${response.status}`)

				const data = await response.json()
				setApplications(data)
			} catch (error) {
				if (error.name !== 'AbortError') {
					console.error('Unable to load applications:', error)
				}
			} finally {
				if (!controller.signal.aborted) {
					setIsLoading(false)
				}
			}
		}

		loadApplications()
		return () => controller.abort()
	}, [token])

	return (
		<div>
			<p role="status">{message}</p>
			{error && <p role="alert">{error}</p>}
			<button
				className="logout-button"
				type="button"
				onClick={handleLogout}
				disabled={isSubmitting}
			>
				{isSubmitting ? 'Signing out…' : 'Sign out'}
			</button>

			<h2>My applications</h2>
			{isLoading && <p>Loading Applications...</p>}
			<ul>
				{applications.map((application) => (
					<li key={application.id}>
						{application.company} — {application.role}
					</li>
				))}
			</ul>
		</div>
	);
}

export default Applications;