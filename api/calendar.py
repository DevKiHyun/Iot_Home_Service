import httplib2 ,datetime, os, json
from apiclient.discovery import build
from oauth2client import client, GOOGLE_TOKEN_URI


CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')
with open(CLIENT_SECRET_FILE) as json_data:
    client_secret_json = json.load(json_data)['web']

CLIENT_ID = client_secret_json["client_id"]
CLIENT_SECRET = client_secret_json["client_secret"]
APPLICATION_NAME = 'Google Calendar API Python'


def get_event(refresh_token):
    credentials = client.OAuth2Credentials(
        access_token = None,
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        refresh_token = refresh_token ,
        token_expiry = None,
        token_uri = GOOGLE_TOKEN_URI,
        user_agent = None)

    http = credentials.authorize(httplib2.Http())
    service = build(serviceName ='calendar', version ='v3', http = http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'

    print("Getting the upcoming 10 events")
    eventsResult = service.events().list(
        calendarId = 'primary', timeMin = now,
        maxResults = 10, singleEvents = True,
        orderBy= 'startTime').execute()
    events = eventsResult.get('items')

    if not events:
        print("No events")

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start + " " + event['summary'])

    return events

def insert_event(refresh_token):
    credentials = client.OAuth2Credentials(
        access_token = None,
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        refresh_token = refresh_token ,
        token_expiry = None,
        token_uri = GOOGLE_TOKEN_URI,
        user_agent = None)

    http = credentials.authorize(httplib2.Http())
    service = build(serviceName ='calendar', version ='v3', http = http)

    event = {
        'summary' : 'Google I/O 2015',
        'location' : '800 Howard St., San Fransico',
        'description' : 'A chance to hear more about Google',
        'start' : {
            'dateTime' : '2017-04-06T06:00:00-18:00',
            'timeZone' : 'UTC',
        },
        'end' : {
            'dateTime' : '2017-04-06T14:00:00-18:00',
            'timeZone' : 'UTC',
        },
    }

    event = service.events().insert(calendarId = 'primary', body= event).execute()
