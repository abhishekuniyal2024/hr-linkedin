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
        breakdown = scoring.get('breakdown', {})
        summary_rows.append({
            'candidate': r['from_email'],
            'file': r['filename'],
            'score': scoring.get('score', 0),
            'matched': ", ".join(scoring.get('matched', [])[:4]),
            'missing': ", ".join(scoring.get('missing', [])[:4]),
            'breakdown': breakdown
        })
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


