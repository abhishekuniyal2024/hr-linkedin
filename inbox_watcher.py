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
    summary_rows = []
    for r in resumes:
        text = r.get('text', '') or ''
        scoring = ai.score_resume_against_requirements(text, requirements)
        summary_rows.append({
            'candidate': r['from_email'],
            'file': r['filename'],
            'score': scoring.get('score', 0),
            'matched': ", ".join(scoring.get('matched', [])[:6]),
            'missing': ", ".join(scoring.get('missing', [])[:6]),
        })
    # Print compact summary
    print("\nATS Summary (new resumes):")
    for row in summary_rows:
        print(f"- {row['candidate']} | {row['file']} | Score: {row['score']} | Matched: {row['matched']} | Missing: {row['missing']}")


def main():
    print("📬 Inbox watcher running (every 60 minutes)...")
    schedule.every(60).minutes.do(run_inbox_scan)
    run_inbox_scan()
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    main()


