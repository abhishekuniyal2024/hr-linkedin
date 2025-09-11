import os
from calendar_service import CalendarService
import datetime
import schedule
import time

from email_service import EmailService
from ai_service import AIService
from job_automation_workflow import JobAutomationWorkflow


def load_latest_requirements() -> list[str]:
    try:
        from pathlib import Path
        p = Path('latest_requirements.txt')
        if p.exists():
            return [line.strip() for line in p.read_text().splitlines() if line.strip()]
    except Exception:
        pass
    return [
        "Machine learning model development",
        "Python",
        "TensorFlow or PyTorch",
        "Data pipelines",
        "AWS or GCP",
    ]


def run_inbox_scan():
    # Delegate to the LangGraph-powered subgraph inside the workflow
    # This keeps inbox processing agentic and consistent with the main flow
    try:
        workflow = JobAutomationWorkflow()
        workflow.run_resume_intake_graph_once()
    except Exception as e:
        # Fallback to direct processing if the workflow is unavailable
        email_svc = EmailService()
        ai = AIService()
        requirements = load_latest_requirements()

        resumes = email_svc.fetch_resumes_from_inbox()
        if not resumes:
            print("No new resumes found.")
            return
        summary_rows = []
        credentials_file = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "google_service_account.json")
        calendar_id = os.getenv("GOOGLE_CALENDAR_ID", os.getenv("EMAIL_USERNAME"))
        calendar = CalendarService(credentials_file, calendar_id)
        accepted_count = 0
        # Start 2 days later at 14:00 and roll forward to a weekday if needed
        base_dt = datetime.datetime.combine((datetime.datetime.now() + datetime.timedelta(days=2)).date(), datetime.time(14, 0))
        while base_dt.weekday() >= 5:  # 5=Sat, 6=Sun
            base_dt = base_dt + datetime.timedelta(days=1)
        interview_duration = 30  # minutes
        # First pass: score all resumes and build summary
        for r in resumes:
            text = r.get('text', '') or ''
            scoring = ai.score_resume_against_requirements(text, requirements)
            breakdown = scoring.get('breakdown', {})
            summary_rows.append({
                'candidate': r['from_email'],
                'file': r['filename'],
                'score': scoring.get('score', 0),
                'matched': ", ".join(scoring.get('matched', [])[:4]),
                'missing': ", ".join(scoring.get('missing', [])[:4]),
                'breakdown': breakdown
            })

        # Determine top 3 candidates strictly by score
        ordered = sorted(summary_rows, key=lambda row: row.get('score', 0), reverse=True)
        invitees = {row.get('candidate') for row in ordered[:3] if row.get('candidate')}

        # Second pass: send invites to top 3 and rejections to the rest
        slot_index = 0
        for row in summary_rows:
            to_email = row.get('candidate') or ''
            if not to_email:
                continue
            if to_email in invitees:
                interview_datetime = base_dt + datetime.timedelta(minutes=slot_index * 30)
                summary = f"Interview: {to_email}"
                description = f"Interview scheduled for candidate {to_email} (auto)"
                attendees = [to_email, os.getenv('EMAIL_USERNAME')]
                try:
                    event_link = calendar.create_interview_event(summary, description, interview_datetime, attendees, duration_minutes=interview_duration)
                    print(f"Google Calendar event created: {event_link}")
                    email_svc.send_interview_invitation(
                        {'name': to_email, 'email': to_email},
                        "Interview for your application",
                        interview_datetime=interview_datetime,
                        event_link=event_link,
                    )
                    slot_index += 1
                except Exception as _cal_err:
                    print(f"Warning: Failed to schedule calendar event: {_cal_err}")
                    email_svc.send_interview_invitation(
                        {'name': to_email, 'email': to_email},
                        "Interview for your application",
                    )
                accepted_count += 1
            else:
                email_svc.send_rejection_email(
                    {'name': to_email, 'email': to_email},
                    "Interview for your application"
                )
        # Print detailed summary with scoring breakdown
        print("\n📊 ATS Summary (new resumes):")
        for row in summary_rows:
            print(f"\n👤 {row['candidate']} | 📄 {row['file']}")
            print(f"   🎯 Overall Score: {row['score']}/100")
            if row['breakdown']:
                print(f"   📝 Keywords: {row['breakdown'].get('keywords', 0)}/30")
                print(f"   🛠️  Skills: {row['breakdown'].get('skills', 0)}/25")
                print(f"   💼 Experience: {row['breakdown'].get('experience', 0)}/20")
                print(f"   🎓 Education: {row['breakdown'].get('education', 0)}/15")
                print(f"   📋 Format: {row['breakdown'].get('format', 0)}/10")
            print(f"   ✅ Matched: {row['matched']}")
            print(f"   ❌ Missing: {row['missing']}")


def main():
    print("📬 Inbox watcher running (every 60 minutes)...")
    schedule.every(60).minutes.do(run_inbox_scan)
    run_inbox_scan()
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    main()


