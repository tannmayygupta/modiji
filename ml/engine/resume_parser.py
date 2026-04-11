import re
from typing import List, Dict, Any
from io import BytesIO
import PyPDF2

# Pre-defined list of common skills mapped to our DB generated ones
KNOWN_SKILLS = [
    # Tech & IT
    "Python", "JavaScript", "Java", "SQL", "HTML/CSS", "React", "Node.js", 
    "Cloud Computing", "Git", "Linux", "Data Structures", "REST API", 
    "MongoDB", "Docker", "TypeScript", "AWS", "Machine Learning", 
    "Data Visualization", "Statistics", "R", "Tableau", "Power BI", 
    "Deep Learning", "NLP", "TensorFlow", "Pandas",
    
    # Business & Finance
    "Financial Analysis", "Tally", "Excel", "Accounting", "GST",
    "Banking Operations", "Risk Management", "KYC", "Bloomberg",
    "Mutual Funds", "Insurance", "Financial Modeling", "Compliance",
    
    # Healthcare & Manufacturing
    "Patient Care", "First Aid", "EMR Systems", "Pharmacy", "Lab Testing",
    "Quality Control", "AutoCAD", "Six Sigma", "Lean Manufacturing",
    "CNC Operation", "SolidWorks", "Mechanical Drawing",
    
    # Marketing & Retail
    "Digital Marketing", "SEO", "Social Media Marketing", "Content Writing",
    "Google Analytics", "Email Marketing", "CRM", "Sales", "Market Research",
    "Customer Service", "POS Systems", "Visual Merchandising", "Supply Chain",
    
    # HR & Soft Skills
    "Recruitment", "Employee Engagement", "Payroll", "HRIS",
    "Communication", "Problem Solving", "Teamwork", "Microsoft Office",
    "Time Management", "Project Management", "Data Entry", "Presentation",
    "Teaching", "Assessment", "Mentoring"
]

# Common educational degrees
EDUCATION_KEYWORDS = {
    "10TH": ["10th", "matriculation", "ssc", "secondary"],
    "12TH": ["12th", "hsc", "higher secondary", "intermediate"],
    "ITI": ["iti", "industrial training", "craftsmanship"],
    "DIPLOMA": ["diploma", "polytechnic"],
    "GRADUATE": ["bachelor", "b.tech", "b.e", "b.sc", "b.com", "b.a", "bba", "bca", "degree", "graduated"],
    "PG": ["master", "m.tech", "m.e", "m.sc", "m.com", "m.a", "mba", "mca", "postgraduate", "phd"]
}

class ResumeParser:
    """
    Parses an uploaded PDF resume to extract key metadata 
    (Skills and Education level) for the Recommendation Engine.
    """
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        text = ""
        try:
            reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            
        return text.lower() # Normalize to lowercase

    @staticmethod
    def parse_skills(text: str) -> List[str]:
        found_skills = []
        for skill in KNOWN_SKILLS:
            # Look for whole word boundary match (ignoring case since text is already lowered)
            # We escape the skill name to avoid regex injection on special chars like C++
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text):
                found_skills.append(skill)
        return found_skills

    @staticmethod
    def parse_education(text: str) -> str:
        # Default fallback
        highest_matched = "10TH" 
        
        # We process from highest degree down, first hit is our fallback
        for level in reversed(list(EDUCATION_KEYWORDS.keys())):
            for keyword in EDUCATION_KEYWORDS[level]:
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text):
                    return level
        
        return highest_matched

    @classmethod
    def process_resume(cls, file_bytes: bytes) -> Dict[str, Any]:
        """Entry point to process a PDF and return the extracted profile."""
        text = cls.extract_text_from_pdf(file_bytes)
        
        skills = cls.parse_skills(text)
        education = cls.parse_education(text)
        
        return {
            "success": True if text else False,
            "extracted_skills": skills,
            "extracted_education": education,
            "text_length": len(text)
        }

