"""
ml/engine/hybrid_scorer.py
Main recommendation function combining:
  - Content-based scoring (semantic skill matching)
  - SVD collaborative filtering (trained on interaction data)
  - Video communication bonus
  - Affirmative action boosts

Called by the FastAPI recommendation service.
"""

import json
import pickle
import logging
from pathlib import Path
from ml.engine.content_based import (
    ContentBasedEngine,
    compute_affirmative_boost,
    compute_video_bonus,
)

logger = logging.getLogger(__name__)

# ─── Model Loading ─────────────────────────────────────────────────────────

_content_engine = None
_cf_model = None
_intern_cache = None
_interaction_counts = None
_loaded = False


def load_models():
    """Load all trained models into memory. Called once at startup."""
    global _content_engine, _cf_model, _intern_cache, _interaction_counts, _loaded

    model_dir = Path(__file__).parent.parent / "models"
    data_dir = Path(__file__).parent.parent / "data" / "generated"

    # Content engine (loads taxonomy internally)
    _content_engine = ContentBasedEngine(use_semantic=True)

    # SVD collaborative filter
    cf_path = model_dir / "svd_cf_model.pkl"
    if cf_path.exists():
        with open(cf_path, "rb") as f:
            _cf_model = pickle.load(f)
        logger.info("SVD collaborative filter loaded")
    else:
        _cf_model = None
        logger.warning("SVD model not found — running content-only mode")

    # Internship cache (for scoring without DB queries)
    intern_path = data_dir / "internships.json"
    if intern_path.exists():
        with open(intern_path) as f:
            internships = json.load(f)
        _intern_cache = {i["id"]: i for i in internships}
        logger.info(f"Loaded {len(_intern_cache)} internships into cache")
    else:
        _intern_cache = {}

    # Interaction counts for cold-start
    counts_path = model_dir / "interaction_counts.json"
    if counts_path.exists():
        with open(counts_path) as f:
            _interaction_counts = json.load(f)
    else:
        _interaction_counts = {}

    _loaded = True
    logger.info("All ML models loaded successfully")


def _ensure_loaded():
    if not _loaded:
        load_models()


# ─── Cold Start Detection ─────────────────────────────────────────────────

def is_cold_start(candidate_id: str) -> bool:
    """True if candidate has fewer than 3 interactions (not enough for CF)."""
    if _interaction_counts is None:
        return True
    count = _interaction_counts.get(str(candidate_id), 0)
    return count < 3


def cf_predict(candidate_id: str, internship_id: str) -> float:
    """Predict a CF score using SVD. Returns 0.5 (neutral) for cold-start."""
    if is_cold_start(candidate_id) or _cf_model is None:
        return 0.5
    try:
        cand_to_idx = _cf_model.get("cand_to_idx", {})
        intern_to_idx = _cf_model.get("intern_to_idx", {})
        predicted = _cf_model.get("predicted")

        if predicted is None:
            return 0.5

        c_idx = cand_to_idx.get(str(candidate_id))
        i_idx = intern_to_idx.get(str(internship_id))

        if c_idx is None or i_idx is None:
            return 0.5

        # Raw prediction, normalize to 0-1 range (original scale is ~1-5)
        raw = predicted[c_idx, i_idx]
        normalized = max(0.0, min(1.0, (raw - 1.0) / 4.0))
        return normalized
    except Exception:
        return 0.5


# ─── Main Recommendation Function ─────────────────────────────────────────

def recommend(candidate: dict, internships: list = None, top_n: int = 5) -> list:
    """
    Generate top-N internship recommendations for a candidate.

    Uses hard filters for location (HOME_STATE/NEARBY) and sector preferences.
    If filters return too few results, gracefully widens the search area.

    Args:
        candidate: dict with keys like education_level, skills, sector_preferences, state, etc.
        internships: optional list of internship dicts. If None, uses the cached dataset.
        top_n: number of recommendations to return.

    Returns:
        List of recommendation dicts with scores, explanations, and metadata.
    """
    _ensure_loaded()

    # Try with original preferences first
    results = _score_internships(candidate, internships, top_n)

    # Graceful fallback: if HOME_STATE returned 0 results, widen to NEARBY
    original_pref = (candidate.get("location_preference") or "HOME_STATE").upper()
    fallback_note = None

    if len(results) == 0 and original_pref == "HOME_STATE":
        candidate_copy = dict(candidate)
        candidate_copy["location_preference"] = "NEARBY"
        results = _score_internships(candidate_copy, internships, top_n)
        if results:
            fallback_note = f"No internships found in {candidate.get('state', 'your state')}. Showing nearby region matches."

    # If NEARBY also returned 0, widen to PAN_INDIA
    if len(results) == 0 and original_pref in ("HOME_STATE", "NEARBY"):
        candidate_copy = dict(candidate)
        candidate_copy["location_preference"] = "PAN_INDIA"
        results = _score_internships(candidate_copy, internships, top_n)
        if results:
            fallback_note = f"No internships found near {candidate.get('state', 'your state')}. Showing best matches across India."

    # Add fallback note to all results if applicable
    if fallback_note:
        for r in results:
            r["explanation"]["reasons"].insert(0, {
                "icon": "info",
                "text": fallback_note,
                "category": "fallback",
            })

    return results


def _score_internships(candidate: dict, internships: list = None, top_n: int = 5) -> list:
    """Core scoring loop. Separated so recommend() can retry with widened filters."""
    candidate_id = str(candidate.get("id", "unknown"))
    cold_start = is_cold_start(candidate_id)

    # CF weights based on interaction history
    if cold_start:
        content_weight, cf_weight = 1.0, 0.0
        scoring_mode = "content_only"
    else:
        content_weight, cf_weight = 0.60, 0.40
        scoring_mode = "hybrid"

    # Use provided internships or fall back to cache
    if internships is None:
        if _intern_cache:
            internship_list = list(_intern_cache.values())
        else:
            return []
    else:
        internship_list = internships

    results = []

    for internship in internship_list:
        if not internship.get("is_active", True):
            continue

        intern_id = str(internship.get("id", ""))

        # Content score (includes semantic skill matching)
        c_score, c_meta = _content_engine.score(candidate, internship)

        # ── HARD FILTERS ──────────────────────────────────────────
        # Location: if HOME_STATE selected + internship is in another state → skip
        # Sector:   if user has sector prefs + no match at all → skip
        if not c_meta.get("location_eligible", True):
            continue
        if not c_meta.get("sector_eligible", True):
            continue

        # CF score
        cf_s = cf_predict(candidate_id, intern_id)

        # Hybrid combination
        hybrid = (content_weight * c_score) + (cf_weight * cf_s)

        # Get boosts separately for explanation
        aa_boost, aa_breakdown = compute_affirmative_boost(candidate)
        vid_bonus = compute_video_bonus(candidate)

        final = min(hybrid + aa_boost + vid_bonus, 1.0)
        match_pct = min(99, max(1, int(final * 100)))

        # Build explanation reasons
        reasons = []
        sub_scores = c_meta.get("sub_scores", {})
        skill_align = c_meta.get("skill_alignment", {})

        if sub_scores.get("skills", 0) > 0.5:
            matched = skill_align.get("matched", [])
            if matched:
                reasons.append({
                    "icon": "code",
                    "text": f"Your skills match: {', '.join(matched[:3])}",
                    "category": "skills",
                })

        if sub_scores.get("education", 0) >= 1.0:
            reasons.append({
                "icon": "graduation-cap",
                "text": f"Your {candidate.get('education_level', 'education')} meets the requirement",
                "category": "education",
            })

        if sub_scores.get("location", 0) >= 0.8:
            reasons.append({
                "icon": "map-pin",
                "text": f"{internship.get('city', '')} is in your preferred area",
                "category": "location",
            })

        if sub_scores.get("sector", 0) >= 0.7:
            reasons.append({
                "icon": "briefcase",
                "text": f"{internship.get('sector', '')} matches your sector interest",
                "category": "sector",
            })

        if vid_bonus > 0:
            reasons.append({
                "icon": "video",
                "text": f"Video intro adds +{int(vid_bonus * 100)}% boost",
                "category": "video",
            })

        for aa_item in aa_breakdown:
            reasons.append({
                "icon": "shield-check",
                "text": aa_item["reason"],
                "category": "affirmative",
            })

        results.append({
            "internship_id": intern_id,
            "company_name": internship.get("company_name", internship.get("company", "")),
            "role_title": internship.get("role_title", internship.get("role", "")),
            "sector": internship.get("sector", ""),
            "city": internship.get("city", internship.get("location_city", "")),
            "state": internship.get("state", internship.get("location_state", "")),
            "stipend_amount": internship.get("stipend_amount", internship.get("stipend_monthly", 5000)),
            "content_score": round(c_score, 4),
            "collaborative_score": round(cf_s, 4),
            "affirmative_score": round(aa_boost, 4),
            "final_score": round(final, 4),
            "match_percentage": match_pct,
            "scoring_mode": scoring_mode,
            "explanation": {
                "match_percentage": match_pct,
                "reasons": reasons,
                "skill_alignment": skill_align,
            },
            "display_rank": 0,  # Set after sorting
        })

    # Sort by final score descending
    results.sort(key=lambda x: x["final_score"], reverse=True)

    # Set ranks
    for rank, rec in enumerate(results[:top_n], 1):
        rec["display_rank"] = rank

    return results[:top_n]
