import time
import schedule
from email_service import EmailService
from ai_service import AIService


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
    email_svc = EmailService()
    ai = AIService()
    requirements = load_latest_requirements()

    resumes = email_svc.fetch_resumes_from_inbox()
    if not resumes:
        print("No new resumes found.")
        return
    for r in resumes:
        text = r.get('text', '') or ''
        scoring = ai.score_resume_against_requirements(text, requirements)
        preview = (text[:160] + '…') if len(text) > 160 else text
        print(f"Processed: {r['filename']} from {r['from_email']} — ATS Score: {scoring.get('score', 0)}")
        print(f"  Extracted text length: {len(text)}")
        if preview:
            print(f"  Text preview: {preview.replace('\n',' ') }")
        print(f"  Using {len(requirements)} requirements: {', '.join(requirements[:6])}{'…' if len(requirements)>6 else ''}")


def main():
    print("📬 Inbox watcher running (every 60 minutes)...")
    schedule.every(60).minutes.do(run_inbox_scan)
    run_inbox_scan()
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    main()


