#!/usr/bin/env python3

from ai_service import AIService

def test_score_validation():
    ai = AIService()
    
    # Test with a resume that might trigger high format scores
    resume_text = """
    RAHUL RAWAT
    Assistant Manager- AI & Analytics
    +91-7404422001 
    Rahulrawat178@gmail.com 
    Noida, Uttar pradesh, India 
    M.TECH Software Engineering 
    2014 - 2016 | UIET, KUK 
    8.86 CGPA
    
    EDUCATION
    Dynamic Assistant Manager with 8+ years of experience in AI & Analytics
    Strong communication skills and team collaboration
    Problem-solving mindset with engineering background
    """
    
    requirements = [
        "Experience in Engineering",
        "Strong communication skills", 
        "Team collaboration",
        "Problem-solving mindset"
    ]
    
    print("Testing score validation...")
    result = ai.score_resume_against_requirements(resume_text, requirements)
    
    print(f"\nResult: {result}")
    
    # Check if all scores are within limits
    breakdown = result.get('breakdown', {})
    print(f"\nScore validation:")
    print(f"Keywords: {breakdown.get('keywords', 0)}/30 (max: 30)")
    print(f"Skills: {breakdown.get('skills', 0)}/25 (max: 25)")
    print(f"Experience: {breakdown.get('experience', 0)}/20 (max: 20)")
    print(f"Education: {breakdown.get('education', 0)}/15 (max: 15)")
    print(f"Format: {breakdown.get('format', 0)}/10 (max: 10)")
    print(f"Total: {result.get('score', 0)}/100 (max: 100)")
    
    # Verify all scores are within limits
    assert breakdown.get('keywords', 0) <= 30, f"Keywords score {breakdown.get('keywords', 0)} exceeds 30"
    assert breakdown.get('skills', 0) <= 25, f"Skills score {breakdown.get('skills', 0)} exceeds 25"
    assert breakdown.get('experience', 0) <= 20, f"Experience score {breakdown.get('experience', 0)} exceeds 20"
    assert breakdown.get('education', 0) <= 15, f"Education score {breakdown.get('education', 0)} exceeds 15"
    assert breakdown.get('format', 0) <= 10, f"Format score {breakdown.get('format', 0)} exceeds 10"
    assert result.get('score', 0) <= 100, f"Total score {result.get('score', 0)} exceeds 100"
    
    print("\n✅ All scores are within valid limits!")

if __name__ == "__main__":
    test_score_validation()
