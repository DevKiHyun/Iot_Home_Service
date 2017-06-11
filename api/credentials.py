import httplib2, os, json
from oauth2client import client, GOOGLE_TOKEN_URI

config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
with open(config_file) as json_data:
    client_secret_json = json.load(json_data)['web']
    json_data.close()

CLIENT_ID = client_secret_json["client_id"]
CLIENT_SECRET = client_secret_json["client_secret"]

def get_credentials(refresh_token):
    credentials = client.OAuth2Credentials(
        access_token = None,
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        refresh_token = refresh_token ,
        token_expiry = None,
        token_uri = GOOGLE_TOKEN_URI,
        user_agent = None)

    credentials.refresh(httplib2.Http())

    return credentials
