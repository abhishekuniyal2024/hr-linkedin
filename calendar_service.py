import datetime
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

class CalendarService:
    def __init__(self, credentials_file: str, calendar_id: Optional[str] = None):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.credentials = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=self.SCOPES
        )
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.calendar_id = calendar_id or 'primary'

    def create_interview_event(self, summary: str, description: str, start_time: datetime.datetime, attendees: List[str], duration_minutes: int = 60):
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'attendees': [{'email': email} for email in attendees],
            'reminders': {
                'useDefault': True,
            },
        }
        created_event = self.service.events().insert(calendarId=self.calendar_id, body=event, sendUpdates='all').execute()
        return created_event.get('htmlLink')
