import datetime
import os
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

class CalendarService:
    def __init__(self, credentials_file: str, calendar_id: Optional[str] = None):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        creds = service_account.Credentials.from_service_account_file(
            credentials_file, scopes=self.SCOPES
        )
        # Optional: impersonate a Workspace user (requires Domain-Wide Delegation)
        subject = os.getenv('GOOGLE_CALENDAR_IMPERSONATE')
        if subject:
            try:
                creds = creds.with_subject(subject)
            except Exception:
                pass
        self.credentials = creds
        self.service = build('calendar', 'v3', credentials=self.credentials)
        self.calendar_id = calendar_id or 'primary'
        # In personal Gmail contexts, inviting attendees via service accounts is forbidden.
        # Allow invites only if explicitly enabled.
        self.allow_attendee_invites = os.getenv('CALENDAR_ALLOW_ATTENDEE_INVITES', 'false').lower() == 'true'

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
            'reminders': {
                'useDefault': True,
            },
        }
        # Only include attendees and send updates if explicitly allowed
        send_updates = 'none'
        if self.allow_attendee_invites and attendees:
            event['attendees'] = [{'email': email} for email in attendees]
            send_updates = 'all'

        created_event = self.service.events().insert(calendarId=self.calendar_id, body=event, sendUpdates=send_updates).execute()
        return created_event.get('htmlLink')
