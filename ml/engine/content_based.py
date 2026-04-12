"""
Content-Based Filtering Engine

Matches candidate profiles against internship requirements using
multi-dimensional similarity scoring:
  - Skill similarity (TF-IDF + cosine / semantic embeddings)
  - Education level matching (hierarchical)
  - Location proximity scoring
  - Sector alignment
  - Field of study relevance

This is the primary engine (60% weight) and works from Day 1
with zero historical interaction data — critical for cold-start.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Optional
import logging

logger = logging.getLogger(__name__)


# Education hierarchy for ordered comparison
EDUCATION_HIERARCHY = {
    "10TH": 1,
    "12TH": 2,
    "ITI": 2,
    "DIPLOMA": 3,
    "GRADUATE": 4,
    "PG": 5,
}

# Feature weights (must sum to 1.0)
WEIGHTS = {
    "skills": 0.35,
    "education": 0.20,
    "location": 0.20,
    "sector": 0.15,
    "field": 0.10,
}


class ContentBasedEngine:
    """
    Content-Based Filtering for internship recommendation.

    Computes a similarity score between a candidate's profile and each
    internship's requirements across multiple dimensions.
    """

    def __init__(self, use_semantic: bool = False):
        """
        Args:
            use_semantic: If True, use sentence-transformers for skill matching.
                         If False, use TF-IDF (faster, good for prototype).
        """
        self.use_semantic = use_semantic
        self._tfidf = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            max_features=5000,
        )
        self._semantic_model = None

        if use_semantic:
            try:
                from sentence_transformers import SentenceTransformer
                self._semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Loaded sentence-transformer model for semantic matching")
            except ImportError:
                logger.warning("sentence-transformers not installed, using difflib for lightweight semantic matching")
                self.use_semantic = True
                self._semantic_model = None

    # ──────────────────────────────────────────────
    # Sub-Score Computations
    # ──────────────────────────────────────────────

    def compute_skill_similarity(
        self,
        candidate_skills: list[str],
        internship_skills: list[str],
    ) -> tuple[float, dict]:
        """
        Compute skill similarity between candidate and internship.

        Returns:
            (score, skill_alignment) where skill_alignment has matched/partial/missing
        """
        if not internship_skills:
            return 0.5, {"matched": [], "partial": [], "missing": []}

        if not candidate_skills:
            return 0.0, {"matched": [], "partial": [], "missing": internship_skills}

        c_lower = set(s.lower().strip() for s in candidate_skills)
        i_lower = set(s.lower().strip() for s in internship_skills)

        # Exact matches
        matched = c_lower & i_lower
        missing = i_lower - c_lower

        # Partial matches: check for substring containment
        partial = set()
        remaining_missing = set()
        for m in missing:
            found_partial = False
            for c in c_lower:
                if m in c or c in m:
                    partial.add(m)
                    found_partial = True
                    break
            if not found_partial:
                remaining_missing.add(m)

        # Score: exact match = 1.0, partial = 0.5, missing = 0.0
        if len(i_lower) > 0:
            score = (len(matched) * 1.0 + len(partial) * 0.5) / len(i_lower)
        else:
            score = 0.5

        # If semantic mode is enabled, use it for remaining missing skills
        if self.use_semantic and remaining_missing and candidate_skills:
            semantic_score = self._semantic_skill_match(
                list(c_lower - matched - partial), list(remaining_missing)
            )
            # Blend: 60% exact/partial + 40% semantic
            score = (score * 0.6) + (semantic_score * 0.4)

        skill_alignment = {
            "matched": list(matched)[:10],
            "partial": list(partial)[:5],
            "missing": list(remaining_missing)[:5],
        }

        return min(1.0, score), skill_alignment

    def _semantic_skill_match(self, candidate_skills: list, missing_skills: list) -> float:
        """Use sentence-transformer or lightweight difflib for semantic skill similarity."""
        if not candidate_skills or not missing_skills:
            return 0.0

        if self._semantic_model:
            try:
                c_embeddings = self._semantic_model.encode(candidate_skills)
                m_embeddings = self._semantic_model.encode(missing_skills)
                similarities = cosine_similarity(c_embeddings, m_embeddings)
                max_sims = similarities.max(axis=0)
                return float(np.mean(max_sims))
            except Exception as e:
                logger.error(f"Semantic matching failed: {e}")
                return 0.0
        
        # Lightweight fallback: Text sequence matching
        import difflib
        total_sim = 0.0
        for m_skill in missing_skills:
            best_match = 0.0
            for c_skill in candidate_skills:
                # SequenceMatcher yields a ratio 0.0 to 1.0 (e.g. 'React' vs 'React.js' -> ~0.83)
                sim = difflib.SequenceMatcher(None, c_skill, m_skill).ratio()
                if sim > best_match:
                    best_match = sim
            total_sim += best_match
            
        return total_sim / len(missing_skills)

    def compute_education_match(
        self,
        candidate_education: str,
        required_education: str,
    ) -> float:
        """
        Compare candidate's education level against requirement.

        Over-qualified: full score (1.0)
        Exact match: full score (1.0)
        Under-qualified: partial score based on gap
        """
        c_rank = EDUCATION_HIERARCHY.get(candidate_education, 4)
        r_rank = EDUCATION_HIERARCHY.get(required_education, 4)

        if c_rank >= r_rank:
            return 1.0
        else:
            # Partial credit — larger gap = lower score
            return max(0.2, 1.0 - (r_rank - c_rank) * 0.25)

    # Indian geographic regions for NEARBY matching
    REGION_MAP = {
        "north": ["delhi", "haryana", "himachal pradesh", "jammu & kashmir", "ladakh",
                   "punjab", "rajasthan", "uttarakhand", "uttar pradesh", "chandigarh"],
        "south": ["andhra pradesh", "karnataka", "kerala", "tamil nadu", "telangana",
                   "puducherry", "andaman & nicobar", "lakshadweep"],
        "east": ["bihar", "jharkhand", "odisha", "west bengal"],
        "west": ["goa", "gujarat", "maharashtra", "dadra & nagar haveli"],
        "central": ["chhattisgarh", "madhya pradesh"],
        "northeast": ["arunachal pradesh", "assam", "manipur", "meghalaya",
                       "mizoram", "nagaland", "sikkim", "tripura"],
    }

    def _get_region(self, state: str) -> str:
        """Find region name for a given state."""
        s = state.lower().strip()
        for region, states in self.REGION_MAP.items():
            if s in states:
                return region
        return "unknown"

    def compute_location_score(
        self,
        candidate_state: Optional[str],
        candidate_preference: Optional[str],
        internship_state: str,
        internship_city: Optional[str] = None,
    ) -> tuple[float, bool]:
        """
        Score based on geographic match and candidate location preference.
        Returns (score, is_eligible) where is_eligible=False means HARD FILTER OUT.

        HOME_STATE  → same state only (hard filter)
        NEARBY      → same region only (hard filter)
        PAN_INDIA   → everything allowed
        """
        if not candidate_state:
            return 0.5, True  # No preference = neutral, eligible

        same_state = (
            candidate_state.lower().strip() == internship_state.lower().strip()
            if candidate_state and internship_state else False
        )

        pref = (candidate_preference or "HOME_STATE").upper()

        if same_state:
            return 1.0, True

        if pref == "HOME_STATE":
            # Hard filter: only same state allowed
            return 0.0, False

        if pref == "NEARBY":
            # Check if same geographic region
            c_region = self._get_region(candidate_state)
            i_region = self._get_region(internship_state)
            if c_region != "unknown" and c_region == i_region:
                return 0.8, True
            else:
                return 0.0, False

        # PAN_INDIA: everything eligible
        return 0.6, True

    def compute_sector_score(
        self,
        candidate_sectors: list[str],
        internship_sector: str,
    ) -> float:
        """Score based on sector preference match."""
        if not candidate_sectors:
            return 0.5
        if not internship_sector:
            return 0.5

        c_sectors = [s.lower().strip() for s in candidate_sectors]
        i_sector = internship_sector.lower().strip()

        if i_sector in c_sectors:
            return 1.0

        # Check partial match
        for cs in c_sectors:
            if cs in i_sector or i_sector in cs:
                return 0.7

        return 0.2

    def compute_field_score(
        self,
        candidate_field: Optional[str],
        preferred_fields: list[str],
    ) -> float:
        """Score based on field of study relevance."""
        if not candidate_field or not preferred_fields:
            return 0.5

        c_field = candidate_field.lower().strip()
        p_fields = [f.lower().strip() for f in preferred_fields]

        if c_field in p_fields:
            return 1.0

        # Check partial match
        for pf in p_fields:
            if c_field in pf or pf in c_field:
                return 0.7

        return 0.3

    # ──────────────────────────────────────────────
    # Main Scoring
    # ──────────────────────────────────────────────

    def score(self, candidate: dict, internship: dict) -> tuple[float, dict]:
        """
        Compute the overall content-based similarity score.

        Args:
            candidate: Dict with keys: skills, education_level, state,
                      location_preference, sector_preferences, field_of_study
            internship: Dict with keys: required_skills, min_education,
                       state, city, sector, preferred_fields

        Returns:
            (final_score, metadata) where metadata contains sub-scores and explanations
        """
        # Skill similarity
        skill_score, skill_alignment = self.compute_skill_similarity(
            candidate.get("skills", []),
            internship.get("required_skills", []),
        )

        # Education match
        edu_score = self.compute_education_match(
            candidate.get("education_level", "GRADUATE"),
            internship.get("min_education", "GRADUATE"),
        )

        # Location
        loc_score, location_eligible = self.compute_location_score(
            candidate.get("state"),
            candidate.get("location_preference"),
            internship.get("state", ""),
            internship.get("city"),
        )

        # Sector
        sector_score = self.compute_sector_score(
            candidate.get("sector_preferences", []),
            internship.get("sector", ""),
        )

        # Sector eligibility: if candidate has sector prefs and score is very low, filter out
        sector_eligible = True
        if candidate.get("sector_preferences") and len(candidate["sector_preferences"]) > 0:
            if sector_score <= 0.2:
                sector_eligible = False

        # Field of study
        field_score = self.compute_field_score(
            candidate.get("field_of_study"),
            internship.get("preferred_fields", []),
        )

        # Weighted combination
        final_score = (
            WEIGHTS["skills"] * skill_score +
            WEIGHTS["education"] * edu_score +
            WEIGHTS["location"] * loc_score +
            WEIGHTS["sector"] * sector_score +
            WEIGHTS["field"] * field_score
        )

        metadata = {
            "sub_scores": {
                "skills": round(skill_score, 4),
                "education": round(edu_score, 4),
                "location": round(loc_score, 4),
                "sector": round(sector_score, 4),
                "field": round(field_score, 4),
            },
            "skill_alignment": skill_alignment,
            "weights": WEIGHTS,
            "location_eligible": location_eligible,
            "sector_eligible": sector_eligible,
        }

        return round(final_score, 4), metadata

    def score_all(
        self,
        candidate: dict,
        internships: list[dict],
    ) -> list[tuple[str, float, dict]]:
        """
        Score a candidate against all internships.

        Returns:
            List of (internship_id, score, metadata) sorted by score descending.
        """
        results = []
        for internship in internships:
            score, metadata = self.score(candidate, internship)
            results.append((internship.get("id", ""), score, metadata))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

def compute_affirmative_boost(candidate: dict) -> tuple[float, list]:
    boost = 0.0
    breakdown = []
    
    if candidate.get("social_category") in ["SC", "ST", "OBC"]:
        boost += 0.05
        breakdown.append({"reason": "Social category representation boost (+5%)"})
        
    if candidate.get("is_rural"):
        boost += 0.03
        breakdown.append({"reason": "Rural background uplift (+3%)"})
        
    if candidate.get("is_aspirational_district"):
        boost += 0.03
        breakdown.append({"reason": "Aspirational District uplift (+3%)"})
        
    return min(boost, 0.15), breakdown

def compute_video_bonus(candidate: dict) -> float:
    if not candidate.get("video_uploaded"):
        return 0.0
    score = candidate.get("video_overall_score", 0)
    if not score:
        return 0.0
    return (score / 100.0) * 0.10
