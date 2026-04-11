"""
Collaborative Filtering Engine

Uses matrix factorization (SVD) to learn from past successful matches.
Powered by the `surprise` library for sparse interaction data.

Cold-Start Strategy:
  - New candidates (< 5 interactions): collaborative_weight → 0, content-only
  - Growing candidates (5-50 interactions): gradually increase collaborative weight
  - Active candidates (50+ interactions): full 40% collaborative weight

The engine retrains weekly on the full interaction dataset.
"""
import os
import logging
import pickle
from typing import Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Try to import surprise — it's optional for prototype
try:
    from surprise import Dataset, Reader, SVD
    from surprise.model_selection import cross_validate
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    logger.warning("scikit-surprise not installed. Collaborative filtering disabled.")


# Interaction type → implicit rating mapping
RATING_MAP = {
    "VIEW": 1.0,
    "SAVE": 2.5,
    "APPLY": 4.0,
    "ACCEPT": 5.0,
    "REJECT": 0.5,
    "COMPLETE": 5.0,
}

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")


class CollaborativeEngine:
    """
    Collaborative Filtering using SVD matrix factorization.

    Learns latent factors from the candidate-internship interaction matrix
    to predict how much a candidate would like a new internship.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.model: Optional[SVD] = None
        self.is_trained = False
        self.model_path = model_path or os.path.join(MODEL_DIR, "cf_svd_model.pkl")
        self.training_stats = {}

        # Try to load existing model
        self._load_model()

    def _load_model(self):
        """Load a previously trained model from disk."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, "rb") as f:
                    data = pickle.load(f)
                    self.model = data["model"]
                    self.training_stats = data.get("stats", {})
                    self.is_trained = True
                    logger.info(f"Loaded CF model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load CF model: {e}")

    def _save_model(self):
        """Save the trained model to disk."""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump({
                    "model": self.model,
                    "stats": self.training_stats,
                }, f)
            logger.info(f"Saved CF model to {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to save CF model: {e}")

    def train(self, interactions_df: pd.DataFrame) -> dict:
        """
        Train the SVD model on interaction data.

        Args:
            interactions_df: DataFrame with columns:
                - candidate_id (str)
                - internship_id (str)
                - interaction_type (str): VIEW, SAVE, APPLY, ACCEPT, REJECT, COMPLETE

        Returns:
            Training metrics dict
        """
        if not SURPRISE_AVAILABLE:
            logger.warning("Cannot train: scikit-surprise not installed")
            return {"error": "scikit-surprise not installed"}

        if interactions_df.empty:
            logger.warning("Cannot train: no interaction data")
            return {"error": "no interaction data"}

        # Convert interaction types to ratings
        df = interactions_df.copy()
        df["rating"] = df["interaction_type"].map(RATING_MAP).fillna(1.0)

        # Aggregate: take the max rating per (candidate, internship) pair
        df_agg = df.groupby(["candidate_id", "internship_id"])["rating"].max().reset_index()

        n_users = df_agg["candidate_id"].nunique()
        n_items = df_agg["internship_id"].nunique()
        n_interactions = len(df_agg)

        logger.info(f"Training CF model: {n_users} users, {n_items} items, {n_interactions} interactions")

        # Build surprise dataset
        reader = Reader(rating_scale=(0.5, 5.0))
        data = Dataset.load_from_df(
            df_agg[["candidate_id", "internship_id", "rating"]], reader
        )

        # Train SVD
        # Hyperparameters tuned for sparse data (typical in early-stage PMIS)
        self.model = SVD(
            n_factors=50,       # Latent dimensions (low for sparse data)
            n_epochs=20,        # Training iterations
            lr_all=0.005,       # Learning rate
            reg_all=0.02,       # Regularization (prevent overfitting)
            random_state=42,
        )

        trainset = data.build_full_trainset()
        self.model.fit(trainset)
        self.is_trained = True

        # Cross-validate for metrics
        try:
            cv_results = cross_validate(
                SVD(n_factors=50, n_epochs=20, lr_all=0.005, reg_all=0.02, random_state=42),
                data, measures=["RMSE", "MAE"], cv=3, verbose=False
            )
            rmse = float(np.mean(cv_results["test_rmse"]))
            mae = float(np.mean(cv_results["test_mae"]))
        except Exception:
            rmse, mae = 0.0, 0.0

        self.training_stats = {
            "n_users": n_users,
            "n_items": n_items,
            "n_interactions": n_interactions,
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "density": round(n_interactions / (n_users * n_items) * 100, 2) if n_users * n_items > 0 else 0,
        }

        self._save_model()
        logger.info(f"CF model trained: RMSE={rmse:.4f}, MAE={mae:.4f}")

        return self.training_stats

    def predict(self, candidate_id: str, internship_id: str) -> float:
        """
        Predict the rating a candidate would give to an internship.

        Returns:
            Normalized score between 0 and 1.
        """
        if not self.is_trained or not self.model:
            return 0.0

        try:
            prediction = self.model.predict(candidate_id, internship_id)
            # Normalize from [0.5, 5.0] → [0, 1]
            return max(0.0, min(1.0, (prediction.est - 0.5) / 4.5))
        except Exception as e:
            logger.error(f"CF prediction failed: {e}")
            return 0.0

    def predict_all(
        self,
        candidate_id: str,
        internship_ids: list[str],
    ) -> dict[str, float]:
        """
        Predict scores for a candidate against multiple internships.

        Returns:
            Dict mapping internship_id → normalized score
        """
        if not self.is_trained:
            return {iid: 0.0 for iid in internship_ids}

        return {
            iid: self.predict(candidate_id, iid)
            for iid in internship_ids
        }

    def get_collaborative_weight(self, interaction_count: int) -> float:
        """
        Dynamic weight for collaborative filtering based on data availability.

        Cold-start mitigation:
          - 0-4 interactions: 0% collaborative (pure content-based)
          - 5-49 interactions: linearly increase from 0% to 40%
          - 50+ interactions: full 40%
        """
        if interaction_count < 5:
            return 0.0
        elif interaction_count < 50:
            return 0.4 * (interaction_count - 5) / 45
        else:
            return 0.4
