"""
ml/engine/train_cf.py
Train SVD collaborative filter on interaction data using scipy.
No external C++ compilation needed — uses scipy.sparse.linalg.svds.

Interaction ratings: VIEW=1, SAVE=3, APPLY=5.

Run: python -m ml.engine.train_cf
"""

import json
import pickle
import numpy as np
from pathlib import Path
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import svds


def train_collaborative_filter(interactions_path: str = None, n_factors: int = 50):
    """Train SVD collaborative filter and save model."""
    if interactions_path is None:
        interactions_path = str(Path(__file__).parent.parent / "data" / "generated" / "interactions.json")

    with open(interactions_path) as f:
        interactions = json.load(f)

    print(f"  Loaded {len(interactions)} interactions")

    # Convert interaction types to ratings
    RATING_MAP = {"VIEW": 1.0, "SAVE": 3.0, "APPLY": 5.0}

    # Build candidate and internship ID mappings
    candidate_ids = sorted(set(ix["candidate_id"] for ix in interactions))
    internship_ids = sorted(set(ix["internship_id"] for ix in interactions))

    cand_to_idx = {cid: i for i, cid in enumerate(candidate_ids)}
    intern_to_idx = {iid: i for i, iid in enumerate(internship_ids)}

    n_users = len(candidate_ids)
    n_items = len(internship_ids)
    print(f"  Matrix dimensions: {n_users} candidates x {n_items} internships")

    # Build sparse user-item matrix (aggregate: keep max rating per pair)
    from collections import defaultdict
    pair_ratings = defaultdict(float)
    for ix in interactions:
        cid = ix["candidate_id"]
        iid = ix["internship_id"]
        rating = RATING_MAP.get(ix.get("interaction_type", "VIEW"), 1.0)
        key = (cand_to_idx[cid], intern_to_idx[iid])
        pair_ratings[key] = max(pair_ratings[key], rating)

    rows, cols, vals = [], [], []
    for (r, c), v in pair_ratings.items():
        rows.append(r)
        cols.append(c)
        vals.append(v)

    R = csr_matrix((vals, (rows, cols)), shape=(n_users, n_items))
    print(f"  Unique pairs: {len(pair_ratings)}, Sparsity: {1 - len(pair_ratings)/(n_users*n_items):.4f}")

    # Mean-center the ratings (subtract user mean for each non-zero entry)
    user_means = np.zeros(n_users)
    for i in range(n_users):
        row = R.getrow(i)
        if row.nnz > 0:
            user_means[i] = row.data.mean()

    # SVD decomposition
    actual_factors = min(n_factors, min(n_users, n_items) - 1)
    U, sigma, Vt = svds(R.astype(float), k=actual_factors)

    # Reconstruct predicted ratings matrix
    sigma_diag = np.diag(sigma)
    predicted = np.dot(np.dot(U, sigma_diag), Vt)

    # Compute RMSE on known ratings
    errors = []
    for (r, c), actual in pair_ratings.items():
        pred = predicted[r, c]
        errors.append((actual - pred) ** 2)
    rmse = np.sqrt(np.mean(errors))
    mae = np.mean([np.sqrt(e) for e in errors])

    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAE:  {mae:.4f}")
    print(f"  Factors: {actual_factors}")

    # Save model components
    out_dir = Path(__file__).parent.parent / "models"
    out_dir.mkdir(parents=True, exist_ok=True)

    model = {
        "U": U,
        "sigma": sigma,
        "Vt": Vt,
        "predicted": predicted,
        "user_means": user_means,
        "cand_to_idx": cand_to_idx,
        "intern_to_idx": intern_to_idx,
        "candidate_ids": candidate_ids,
        "internship_ids": internship_ids,
    }

    with open(out_dir / "svd_cf_model.pkl", "wb") as f:
        pickle.dump(model, f)

    # Save interaction counts for cold-start detection
    from collections import Counter
    candidate_counts = Counter(ix["candidate_id"] for ix in interactions)
    with open(out_dir / "interaction_counts.json", "w") as f:
        json.dump({str(k): int(v) for k, v in candidate_counts.items()}, f)

    print(f"  Models saved to ml/models/")

    return model


if __name__ == "__main__":
    train_collaborative_filter()
