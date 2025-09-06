import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow


def obtain_refresh_token(client_secrets_path: str) -> str:
	"""Runs a local OAuth flow to obtain a refresh token.

	Args:
		client_secrets_path: Path to the OAuth client secret JSON from Google Cloud.

	Returns:
		The refresh token string.
	"""
	load_dotenv()
	scopes = [
		"https://www.googleapis.com/auth/adwords",
	]
	flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, scopes=scopes)
	credentials = flow.run_local_server(port=0, prompt="consent")
	return credentials.refresh_token


if __name__ == "__main__":
	client_secret_file = os.environ.get("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")
	if not os.path.exists(client_secret_file):
		raise FileNotFoundError(
			f"Client secret file not found at {client_secret_file}. Place your OAuth client JSON there."
		)
	refresh_token = obtain_refresh_token(client_secret_file)
	print("Refresh token:\n" + refresh_token)

