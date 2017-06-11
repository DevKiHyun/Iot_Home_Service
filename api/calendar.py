import httplib2, datetime, os, json, sys
sys.path.append('/home/nkh/IOT_test/api')
import credentials as Credentials
from apiclient.discovery import build

APPLICATION_NAME = 'Google Calendar API Python'

def get_event(refresh_token):
    credentials = Credentials.get_credentials(refresh_token)

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
    credentials = Credentials.get_credentials(refresh_token)

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
