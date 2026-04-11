"""
Match Explainer Module

Generates human-readable explanations for why each internship was
recommended to a candidate.

Output is used in the "Why This Match?" section of recommendation cards.

DPDP Act 2023 Compliance:
- Explanations never reveal social category or AA boost details to third parties
- Only the candidate sees their own match explanation
- Company view shows only "recommended candidate" without AA reasoning
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Icon mapping for different explanation categories
CATEGORY_ICONS = {
    "education": "🎓",
    "skills": "💻",
    "location": "📍",
    "sector": "🏢",
    "field": "📚",
    "experience": "⭐",
    "affirmative": "🌟",
}


class MatchExplainer:
    """
    Generates transparent, user-friendly explanations for recommendations.

    Key design decisions:
    1. Use simple language (target: 6th-grade reading level for accessibility)
    2. Always lead with the strongest match reason
    3. Show skill alignment visually (matched/partial/missing)
    4. Never expose raw scores — translate to percentage and icons
    """

    def explain(
        self,
        candidate: dict,
        internship: dict,
        scores: dict,
        skill_alignment: Optional[dict] = None,
        aa_reasons: Optional[list[str]] = None,
    ) -> dict:
        """
        Generate a complete explanation for a recommendation.

        Args:
            candidate: Candidate profile dict
            internship: Internship details dict
            scores: Dict of sub-scores {skills, education, location, sector, field}
            skill_alignment: Dict with matched/partial/missing skills
            aa_reasons: List of affirmative action reason strings

        Returns:
            Explanation dict suitable for the frontend RecommendationCard
        """
        reasons = []

        # Generate reasons from sub-scores (ordered by score descending)
        score_reasons = [
            ("education", scores.get("education", 0)),
            ("skills", scores.get("skills", 0)),
            ("location", scores.get("location", 0)),
            ("sector", scores.get("sector", 0)),
            ("field", scores.get("field", 0)),
        ]
        score_reasons.sort(key=lambda x: x[1], reverse=True)

        for category, score in score_reasons:
            reason = self._generate_reason(
                category, score, candidate, internship, skill_alignment
            )
            if reason:
                reasons.append(reason)

        # Compute match percentage from final score
        final_score = sum(scores.values()) if isinstance(scores, dict) else 0
        # The weighted sum max is about 1.0, so normalize
        max_possible = 0.35 + 0.20 + 0.20 + 0.15 + 0.10  # = 1.0
        match_pct = min(99, max(1, int((final_score / max_possible) * 100))) if max_possible > 0 else 50

        explanation = {
            "match_percentage": match_pct,
            "reasons": reasons[:4],  # Show top 4 reasons
            "skill_alignment": skill_alignment or {
                "matched": [],
                "partial": [],
                "missing": [],
            },
        }

        return explanation

    def _generate_reason(
        self,
        category: str,
        score: float,
        candidate: dict,
        internship: dict,
        skill_alignment: Optional[dict] = None,
    ) -> Optional[dict]:
        """Generate a single human-readable reason for a score category."""

        icon = CATEGORY_ICONS.get(category, "✅")

        if category == "education" and score > 0.6:
            edu = candidate.get("education_level", "your education")
            return {
                "icon": icon,
                "text": f"Your {edu} qualification meets the requirements",
                "category": category,
            }
        elif category == "education" and score <= 0.6:
            return {
                "icon": icon,
                "text": "Consider upskilling to improve your eligibility",
                "category": category,
            }

        elif category == "skills":
            if skill_alignment:
                matched = skill_alignment.get("matched", [])
                if matched:
                    skills_str = ", ".join(matched[:3])
                    return {
                        "icon": icon,
                        "text": f"Your skills match: {skills_str}",
                        "category": category,
                    }
            if score > 0.5:
                return {
                    "icon": icon,
                    "text": "Your skill profile aligns well with this role",
                    "category": category,
                }

        elif category == "location":
            city = internship.get("city", "")
            state = internship.get("state", "")
            candidate_state = candidate.get("state", "")

            if score >= 0.9:
                return {
                    "icon": icon,
                    "text": f"{city} is in your home state ({state})",
                    "category": category,
                }
            elif score >= 0.6:
                pref = candidate.get("location_preference", "")
                if pref == "PAN_INDIA":
                    return {
                        "icon": icon,
                        "text": f"You're open to opportunities across India",
                        "category": category,
                    }
                return {
                    "icon": icon,
                    "text": f"{city}, {state} is accessible from your location",
                    "category": category,
                }

        elif category == "sector":
            sector = internship.get("sector", "")
            if score >= 0.8:
                return {
                    "icon": icon,
                    "text": f"{sector} matches your sector interest",
                    "category": category,
                }

        elif category == "field":
            if score >= 0.8:
                field = candidate.get("field_of_study", "your field")
                return {
                    "icon": icon,
                    "text": f"Your {field} background is relevant to this role",
                    "category": category,
                }

        return None

    def generate_summary(self, match_pct: int) -> str:
        """Generate a one-line summary based on match percentage."""
        if match_pct >= 90:
            return "Excellent match! This opportunity aligns strongly with your profile."
        elif match_pct >= 75:
            return "Great match! Most of your qualifications align well."
        elif match_pct >= 60:
            return "Good match with room for growth in some areas."
        elif match_pct >= 40:
            return "Partial match — consider this for skill development."
        else:
            return "This opportunity has limited alignment with your current profile."
