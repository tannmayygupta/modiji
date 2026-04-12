"""
ml/engine/skill_taxonomy.py
Builds a skill-to-skill similarity matrix using TF-IDF co-occurrence.
After training: "Python" knows it's related to "SQL" (0.81), "Machine Learning" (0.72), etc.

Run: python -m ml.engine.skill_taxonomy
"""

import json
import numpy as np
import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import scipy.sparse as sp


def build_skill_taxonomy(internships_path: str = None) -> dict:
    """
    Build a skill similarity dictionary from internship listings.
    Each internship becomes a TF-IDF document: role + sector + skills.
    Skills that co-occur in similar internships have high cosine similarity.
    """
    if internships_path is None:
        internships_path = str(Path(__file__).parent.parent / "data" / "generated" / "internships.json")

    with open(internships_path) as f:
        internships = json.load(f)

    # Each internship becomes a document
    documents = []
    all_skills_set = set()

    for i in internships:
        skills_text = " ".join(i["required_skills"]) + " " + i["role_title"] + " " + i["sector"]
        documents.append(skills_text.lower())
        all_skills_set.update(s.lower() for s in i["required_skills"])

    all_skills = sorted(all_skills_set)
    print(f"  Found {len(all_skills)} unique skills across {len(internships)} internships")

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
    tfidf_matrix = vectorizer.fit_transform(documents)

    # For each skill, compute its weighted TF-IDF vector
    skill_vectors = {}
    for skill in all_skills:
        skill_mask = np.array([1.0 if skill in doc else 0.0 for doc in documents])
        if skill_mask.sum() > 0:
            weighted = tfidf_matrix.multiply(skill_mask[:, np.newaxis])
            skill_vectors[skill] = weighted.sum(axis=0)

    # Compute pairwise cosine similarity
    similarity_dict = {}
    skills_with_vectors = [s for s in all_skills if s in skill_vectors]

    if len(skills_with_vectors) > 1:
        skill_matrix = sp.vstack([sp.csr_matrix(skill_vectors[s]) for s in skills_with_vectors])
        sim_matrix = cosine_similarity(skill_matrix)

        for i, s1 in enumerate(skills_with_vectors):
            similarity_dict[s1] = {}
            for j, s2 in enumerate(skills_with_vectors):
                if i != j and sim_matrix[i, j] > 0.3:
                    similarity_dict[s1][s2] = round(float(sim_matrix[i, j]), 3)

    # Save outputs
    out_dir = Path(__file__).parent.parent / "models"
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(out_dir / "skill_taxonomy.json", "w") as f:
        json.dump(similarity_dict, f, indent=2)

    with open(out_dir / "tfidf_vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)

    skills_with_relations = sum(1 for s in similarity_dict if similarity_dict[s])
    print(f"  Skill taxonomy built: {skills_with_relations} skills have similarity mappings")

    # Show sample
    sample_skill = "python" if "python" in similarity_dict else (skills_with_vectors[0] if skills_with_vectors else None)
    if sample_skill and similarity_dict.get(sample_skill):
        top_similar = sorted(similarity_dict[sample_skill].items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"  Sample: '{sample_skill}' is similar to: {top_similar}")

    return similarity_dict


if __name__ == "__main__":
    build_skill_taxonomy()
