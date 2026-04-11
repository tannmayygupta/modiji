import re
from typing import Dict, Any

class FraudDetector:
    """
    ML/Rules-Based engine to evaluate if an incoming PM Internship Schema posting
    is completely genuine or a fraudulent post/scam.
    """
    
    # Scams often ask for payments, deposits, guarantee jobs without interviews, etc.
    SUSPICIOUS_TERMS = [
        r'\bpay us\b', r'\bdeposit required\b', r'\binvestment\b',
        r'\bguaranteed job\b', r'\bprocessing fee\b', r'\bno interview\b',
        r'\bearn fast\b', r'\blaptop fee\b', r'\bregistration fees?\b'
    ]
    
    # Free email domains are highly suspicious for corporate internships
    FREE_EMAIL_DOMAINS = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'rediffmail.com']
    
    @classmethod
    def evaluate_internship(cls, internship_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes an internship dict and returns a risk score (0.0 to 1.0)
        and verification notes. A score > 0.6 is typically auto-rejected.
        """
        risk_score = 0.0
        flags = []
        
        description = internship_data.get("description", "").lower()
        company_name = internship_data.get("company_name", "").lower()
        stipend = internship_data.get("stipend_amount", 0)
        contact_email = internship_data.get("contact_email", "").lower()

        # 1. NLP Content Analysis (Suspicious keywords)
        for pattern in cls.SUSPICIOUS_TERMS:
            if re.search(pattern, description):
                risk_score += 0.4
                flags.append(f"Suspicious terminology found: '{pattern}'")
                
        # 2. Stipend Anomaly Detection
        # PMIS guidelines typically state a fixed standard (e.g., ₹4000-₹5000 from company + govt match)
        # If someone implies absurdly high stipends without reason, it's a flag
        if stipend < 4000 and stipend > 0:
            risk_score += 0.2
            flags.append("Stipend is below the standard minimum threshold.")
        elif stipend > 20000:
            risk_score += 0.2
            flags.append(f"Stipend (₹{stipend}) is unusually high for a basic PMIS internship.")
            
        # 3. Domain / Email Verification (Identity check)
        if contact_email:
            domain = contact_email.split('@')[-1] if '@' in contact_email else ""
            if domain in cls.FREE_EMAIL_DOMAINS:
                risk_score += 0.3
                flags.append("Company is using a free email domain instead of a corporate one.")
            
            # Simple check if company name matches domain loosely
            company_slug = re.sub(r'[^a-z0-9]', '', company_name)
            domain_slug = domain.split('.')[0] if domain else ""
            
            if domain_slug and domain_slug not in company_slug and company_slug not in domain_slug:
                # If they are totally dissimilar, slight risk increase
                risk_score += 0.1
                flags.append("Email domain does not logically map to the company name.")
                
        # 4. Description Length / Quality Check
        if len(description) < 50:
            risk_score += 0.2
            flags.append("Description is unusually short, lacking necessary corporate details.")

        # Cap the risk score at 1.0
        final_risk = min(risk_score, 1.0)
        is_verified = final_risk < 0.4
        
        notes = " | ".join(flags) if flags else "Perfectly genuine. Verified."
        if is_verified and final_risk > 0.0:
            notes = "Passed verification with minor warnings: " + notes

        return {
            "fraud_risk_score": round(final_risk, 2),
            "is_verified": is_verified,
            "verification_notes": notes
        }
