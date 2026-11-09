
function Applications({ message, error, isSubmitting, handleLogout }) {

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
		</div>
	);
}

export default Applications;