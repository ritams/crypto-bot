import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow

# The scope for Gmail IMAP access via XOAUTH2
SCOPES = ['https://mail.google.com/']

def main():
    """
    Performs the OAuth2 flow to get a refresh token using client_secret.json.
    """
    client_secret_path = os.path.join('secrets', 'client_secret.json')
    
    if not os.path.exists(client_secret_path):
        print(f"Error: {client_secret_path} not found.")
        print("Please ensure you have downloaded your client_secret.json from the Google Cloud Console")
        print("and placed it in the secrets/ directory.")
        return

    # Load client secrets from file
    with open(client_secret_path, 'r') as f:
        client_config = json.load(f)
    
    # Identify if it's 'installed' or 'web' type
    client_type = 'installed' if 'installed' in client_config else 'web'
    client_id = client_config[client_type]['client_id']
    client_secret = client_config[client_type]['client_secret']

    print(f"Using Client ID: {client_id}")
    
    # Create the flow
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secret_path,
        scopes=SCOPES
    )

    # Run the local server to handle the redirect
    # This will open a browser window for authentication
    creds = flow.run_local_server(port=0)

    print("\n" + "="*50)
    print("GOOGLE OAUTH CREDENTIALS GENERATED")
    print("="*50)
    print(f"GOOGLE_CLIENT_ID={client_id}")
    print(f"GOOGLE_CLIENT_SECRET={client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print("="*50)
    print("\nCopy the above lines into your .env file.")

if __name__ == '__main__':
    main()
