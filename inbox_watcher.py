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
        interview_day = (datetime.datetime.now() + datetime.timedelta(days=2)).date()
        interview_start_time = datetime.time(14, 0)  # 2:00 PM
        interview_duration = 30  # minutes
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
            # Decide acceptance (simple: score >= 60)
            if scoring.get('score', 0) >= 60:
                # Calculate interview time for this candidate
                interview_datetime = datetime.datetime.combine(
                    interview_day,
                    (datetime.datetime.combine(interview_day, interview_start_time) + datetime.timedelta(minutes=accepted_count * interview_duration)).time()
                )
                # Send acceptance email with exact slot
                email_svc.send_interview_invitation(
                    {'name': r.get('from_email'), 'email': r.get('from_email')},
                    interview_datetime,
                    "Interview for your application"
                )
                # Schedule interview on Google Calendar
                summary = f"Interview: {r.get('from_email')}"
                description = f"Interview scheduled for candidate {r.get('from_email')} (auto)"
                attendees = [r.get('from_email'), os.getenv('EMAIL_USERNAME')]
                event_link = calendar.create_interview_event(summary, description, interview_datetime, attendees, duration_minutes=interview_duration)
                print(f"Google Calendar event created: {event_link}")
                accepted_count += 1
            else:
                # Send rejection email
                email_svc.send_rejection_email(
                    {'name': r.get('from_email'), 'email': r.get('from_email')},
                    "Application Update"
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


