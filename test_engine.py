import sys
import os

# Add paths to test ML engines without needing the database
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
from ml.engine.fraud_detector import FraudDetector
from ml.engine.resume_parser import ResumeParser

def test_fraud_engine():
    print("="*60)
    print("🧪 TESTING: Fraud Detection Engine (Phase 1)")
    print("="*60)
    
    # 1. Genuine Internship Post
    genuine_post = {
        "company_name": "Tata Consultancy Services",
        "description": "We are hiring undergraduate interns for our backend infrastructure team. Must know Python and SQL.",
        "stipend_amount": 5000,
        "contact_email": "hr@tcs.com"
    }
    print("\n[Input 1] Genuine Corporate Post (TCS)")
    result1 = FraudDetector.evaluate_internship(genuine_post)
    print(f"Result: {result1}")
    
    # 2. Fake Internship Post
    fake_post = {
        "company_name": "Earn Fast Corp",
        "description": "Guaranteed job with no interview! Just pay us a small registration fee of 1000 INR as a deposit.",
        "stipend_amount": 50000,
        "contact_email": "earnfast123@gmail.com"
    }
    print("\n[Input 2] Scam/Fake Post (With spam keywords & high stipend)")
    result2 = FraudDetector.evaluate_internship(fake_post)
    print(f"Result: {result2}")
    
def test_resume_parser():
    print("\n" + "="*60)
    print("🧪 TESTING: Resume Skill Extractor (Magic Pre-fill)")
    print("="*60)
    
    # Simulating the text that PyPDF2 would extract from a Resume PDF
    sample_resume_text = """
    John Doe - Resume
    Education: B.Tech in Computer Science (Graduate)
    Experience: 
    - Built a web application using React and Node.js.
    - Strong communication skills, led a team of 4.
    - Experienced in Data Analysis and Microsoft Excel for tracking metrics.
    """
    
    skills = ResumeParser.parse_skills(sample_resume_text.lower())
    education = ResumeParser.parse_education(sample_resume_text.lower())
    
    print(f"\n[Raw Resume Text Input]: \n{sample_resume_text}")
    print(f"[Extracted Education Rank]: {education}")
    print(f"[Extracted Magic Skills]: {skills}")
    print("\n(These mapped skills bypass manual entry in the UI!)")

if __name__ == "__main__":
    test_fraud_engine()
    test_resume_parser()
