"""
Hybrid Recommendation Engine

Combines Content-Based and Collaborative Filtering with Affirmative Action
scoring to produce final ranked recommendations.

Architecture:
  Content-Based (60%) ──┐
                        ├──> Hybrid Score ──> AA Boost ──> Diversity Filter ──> Top-K Results
  Collaborative (40%) ──┘

Cold-Start Strategy:
  - Phase 1 (0-4 interactions):   100% content-based
  - Phase 2 (5-49 interactions):  Linear ramp from 100/0 to 60/40
  - Phase 3 (50+ interactions):   Stable at 60/40

This is the main entry point for the recommendation pipeline.
"""
import time
import logging
from typing import Optional

from ml.engine.content_based import ContentBasedEngine
from ml.engine.collaborative import CollaborativeEngine
from ml.engine.affirmative_action import AffirmativeActionScorer
from ml.engine.explainer import MatchExplainer

logger = logging.getLogger(__name__)

def add_video_bonus(candidate: dict, internship: dict, base_score: float) -> float:
    """Add communication score bonus if candidate uploaded a video intro."""
    
    if not candidate.get("video_uploaded") or not candidate.get("video_overall_score"):
        return base_score   # no video = no change, just return existing score
    
    comm_normalized = candidate.get("video_overall_score", 0) / 100.0
    
    # Communication-heavy internships (sales, customer service, HR, teaching)
    COMM_HEAVY_SECTORS = {
        'banking', 'financial services', 'retail', 'fmcg',
        'consulting', 'media', 'education', 'travel', 'hospitality',
        'healthcare', 'telecom'
    }
    
    sector_lower = internship.get("sector", "").lower()
    is_comm_heavy = any(s in sector_lower for s in COMM_HEAVY_SECTORS)
    
    if is_comm_heavy:
        video_bonus = comm_normalized * 0.15   # up to +15% for comm-heavy roles
    else:
        video_bonus = comm_normalized * 0.05   # up to +5% for all other roles
    
    # Also add detected skills from video to the skill matching signal
    video_skills_detected = candidate.get("video_skills_detected")
    if video_skills_detected:
        import json
        try:
            video_skills = json.loads(video_skills_detected)
            required_skills = internship.get("required_skills", [])
            if video_skills and required_skills:
                required = set(s.lower() for s in required_skills)
                detected = set(s.lower() for s in video_skills)
                video_skill_overlap = len(required & detected) / max(len(required), 1)
                video_bonus += video_skill_overlap * 0.08
        except Exception:
            pass
    
    return min(base_score + video_bonus, 1.0)


class HybridEngine:
    """
    The main recommendation engine that combines all scoring components.
    """

    def __init__(
        self,
        use_semantic: bool = False,
        aa_boosts: Optional[dict] = None,
    ):
        self.content_engine = ContentBasedEngine(use_semantic=use_semantic)
        self.collaborative_engine = CollaborativeEngine()
        self.aa_scorer = AffirmativeActionScorer(boosts=aa_boosts)
        self.explainer = MatchExplainer()

        logger.info("Hybrid recommendation engine initialized")

    def recommend(
        self,
        candidate: dict,
        internships: list[dict],
        interaction_count: int = 0,
        top_k: int = 5,
    ) -> list[dict]:
        """
        Generate top-K recommendations for a candidate.

        Args:
            candidate: Candidate profile dict
            internships: List of available internship dicts
            interaction_count: Number of prior interactions (for cold-start weight)
            top_k: Number of recommendations to return

        Returns:
            List of recommendation dicts with scores and explanations
        """
        start_time = time.time()

        if not internships:
            logger.warning("No internships available for recommendation")
            return []

        # Step 1: Content-based scoring
        content_results = self.content_engine.score_all(candidate, internships)
        content_scores = {iid: score for iid, score, _ in content_results}
        content_metadata = {iid: meta for iid, _, meta in content_results}

        # Step 2: Collaborative filtering scoring (if model trained)
        collab_weight = self.collaborative_engine.get_collaborative_weight(interaction_count)
        content_weight = 1.0 - collab_weight

        internship_ids = [i.get("id", "") for i in internships]
        collab_scores = self.collaborative_engine.predict_all(
            candidate.get("id", ""), internship_ids
        )

        # Step 3: Hybrid combination + Video Bonus
        internship_map = {i.get("id", ""): i for i in internships}
        hybrid_scores = {}
        for iid in internship_ids:
            cs = content_scores.get(iid, 0.0)
            cfs = collab_scores.get(iid, 0.0)
            base_hybrid = content_weight * cs + collab_weight * cfs
            # Apply Groq video bonus calculation if valid
            hybrid_scores[iid] = add_video_bonus(candidate, internship_map.get(iid, {}), base_hybrid)

        # Step 4: Affirmative action boost
        scored_list = [(iid, score) for iid, score in hybrid_scores.items()]
        adjusted_list = self.aa_scorer.apply_to_scores(candidate, scored_list)

        # Step 5: Sort by adjusted score
        adjusted_list.sort(key=lambda x: x[1], reverse=True)

        # Step 6: Build recommendation objects with explanations
        internship_map = {i.get("id", ""): i for i in internships}
        recommendations = []

        for iid, adj_score, aa_boost in adjusted_list:
            internship = internship_map.get(iid, {})
            meta = content_metadata.get(iid, {})
            sub_scores = meta.get("sub_scores", {})
            skill_alignment = meta.get("skill_alignment", {})

            # Generate explanation
            aa_boost_val, aa_reasons = self.aa_scorer.compute_boost(candidate)
            explanation = self.explainer.explain(
                candidate, internship, sub_scores, skill_alignment, aa_reasons
            )

            recommendations.append({
                "internship_id": iid,
                "company_name": internship.get("company_name", ""),
                "role_title": internship.get("role_title", ""),
                "sector": internship.get("sector", ""),
                "city": internship.get("city", ""),
                "state": internship.get("state", ""),
                "stipend_amount": internship.get("stipend_amount"),
                "content_score": content_scores.get(iid, 0.0),
                "collaborative_score": collab_scores.get(iid, 0.0),
                "affirmative_score": aa_boost,
                "final_score": adj_score,
                "match_percentage": explanation.get("match_percentage", 50),
                "explanation": explanation,
            })

        # Step 7: Apply diversity constraints
        diversified = self.aa_scorer.enforce_diversity(recommendations, top_k=top_k * 2)

        # Step 8: Final top-K
        final_recs = diversified[:top_k]

        # Add display ranks
        for rank, rec in enumerate(final_recs, 1):
            rec["display_rank"] = rank

        latency_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Generated {len(final_recs)} recommendations in {latency_ms:.1f}ms "
            f"(content_weight={content_weight:.2f}, collab_weight={collab_weight:.2f})"
        )

        return final_recs

    def get_engine_info(self) -> dict:
        """Return engine configuration and status."""
        return {
            "version": "hybrid-v1",
            "content_engine": "TF-IDF + cosine similarity",
            "collaborative_engine": f"SVD (trained={self.collaborative_engine.is_trained})",
            "affirmative_action": self.aa_scorer.get_config(),
            "training_stats": self.collaborative_engine.training_stats,
        }
