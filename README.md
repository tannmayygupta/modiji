# PM Internship Scheme: Intelligent Recommendation Engine

## Introduction

The PM Internship Recommendation Engine is an AI-driven platform built to address Problem Statement #25033 from the Ministry of Corporate Affairs, Government of India. As the volume of youth entering the workforce increases, traditional internship and job platforms suffer from significant friction points: poor skill-to-role matching, generic data entry forms, lack of verified documentation, and an inability to assess qualitative candidate traits like communication and clarity.

## What We Are Solving

This platform serves as a modern bridge between aspiring candidates and corporations offering internships under the Prime Minister's Scheme. We specifically solve the following issues:

1. **Information Friction:** Creating an intuitive, step-by-step onboarding wizard rather than an exhausting single-page form.
2. **Qualitative Blindspots:** Establishing a custom AI video analysis pipeline that evaluates a candidate's introduction video to automatically score their clarity and confidence.
3. **Ineffective Matching:** Moving away from static keyword filtering to a robust Hybrid Machine Learning Recommendation Engine leveraging Content-Based (TF-IDF/Semantic) and Collaborative Filtering mathematics to ensure high-accuracy skill and sector mapping.
4. **Administrative Verification:** Providing an isolated, fast-action Admin Gateway to review candidate credentials (10th, 12th, and Diploma marksheets) directly from Cloud CDN Storage.

---

## Machine Learning Architecture & Model Training 🧠

Our core recommendation engine is deeply customized to respect the official government mandate while using advanced Data Science for hyper-personalization.

### 1. Training Methodologies & Algorithms
We implement a **Hybrid Recommender System** running natively in Python using `scipy` and `scikit-learn`:
- **Content-Based Semantic Matching (TF-IDF & Cosine Similarity):** Rather than strictly matching text (e.g., "React" to "React JS"), we vectorize candidate skills and job requirements to map them in mathematical space. This allows the model to map raw capability versus role demands intelligently.
- **Collaborative Filtering (SVD - Singular Value Decomposition):** We use custom `scipy.sparse.linalg.svds` mathematics to decompose massive interaction matrices (Views, Saves, Applies). This powers our prediction models (e.g., *"Candidates similar to you successfully applied here"*).
- **Affirmative Action Boosting:** We engineered an algebraic multiplier based on the official PMIS guidelines to mathematically boost scores for candidates hailing from Aspirational Districts and specific socio-economic categories.
- **Cascading Geographical Fallback:** To solve "0 Results Found" dead-ends, the model enforces strict geography algorithms. If an internship isn't found in a candidate's `HOME_STATE`, the engine automatically widens the mathematical radius to `NEARBY_REGION`, and ultimately `PAN_INDIA`—transparently notifying the UI of the fallback reason.

### 2. Datasets & Literature Utilized
To build our TF-IDF token weights and structure our geographic Affirmative Action logic, we utilized the following core data reference points:
*   [Prime Minister’s Internship Scheme Guidelines (PMIS) PDF](https://pminternship.mca.gov.in/PMInternshipSchemeGuidelines.pdf) - *Used exclusively for extracting strict rules regarding stipends, location filtering blocks, and Aspirational District targeting parameters.*
*   [Kaggle: Indian Job Postings & Tech Skills Dataset](https://www.kaggle.com/datasets/promptcloud/indeed-job-posting-dataset) - *Analyzed for structuring our content-based dictionaries to recognize skill adjacencies across Indian corporate MSME sectors.*
*   *Indian Geography Demographics* - *Used for extracting regional mappings to build robust `HOME_STATE` to `NEARBY_REGION` geographic arrays in our ML module.*

### 3. Machine Learning File Structure
Our ML models and architectures are cleanly modularized inside the `/ml` directory:
- `ml/engine/hybrid_scorer.py`: **The Master Orchestrator.** Calculates final confidence probabilities, merges TF-IDF with SVD, applies Affirmative Action boosts, and executes Geo-Cascading limits.
- `ml/engine/content_based.py`: Handles pure skill math. Runs TF-IDF Vectorization, Cosine Similarity calculations, and contains the `REGION_MAP` dictionary linking states together.
- `ml/engine/collaborative.py`: Handles matrix factorization using Scipy SVD. Learns organically from live telemetry (Clicks, Applies, Saves).
- `backend/app/services/video_analysis.py`: Contains our Groq Whisper + LLaMA 3.3 data pipeline that crushes unoptimized `.mp4` payloads and extracts the "Communication Score Multiplier".

---

## System Architecture

The architecture is explicitly decoupled, prioritizing raw performance, distinct separation of concerns, and ease of scalability.

- **Frontend Application:** Next.js 14, Tailwind CSS, Framer Motion. Set up as a Server-Side Rendered (SSR) capable, incredibly fast edge client.
- **Backend Service:** FastAPI (Python 3.12). Handles ultra-fast asynchronous execution, Pydantic type safety, and synchronous bridging to our Machine Learning pipelines.
- **Database & Cloud Execution:** 100% powered by Supabase Cloud PostgreSQL (managed via SQLAlchemy ORM). Media assets (Videos, PDFs) exist natively in Supabase Storage Buckets entirely off-server.

## Project Structure

```text
pm-internship-engine/
├── frontend/          # Next.js 14 React UI
├── backend/           # FastAPI Application Core
│   ├── app/
│   │   ├── api/       # RESTful HTTP routers
│   │   ├── services/  # Cloud, Video extraction (Groq Whisper) APIs
│   │   └── db/        # Database session and setup schemas
├── ml/                # Machine Learning Operations
│   ├── engine/        # Hybrid Algorithm logic (SVD, TF-IDF)
│   └── data/          # Synthetic dataset and parsing pipelines
```

## Setup Instructions

### 1. Environment Configurations
Ensure you have Python 3.11+ and Node.js 18+ installed on your system.
You will require a PostgreSQL Database link. Create a `.env` file inside `/backend`:
```env
DATABASE_URL=postgresql://postgres.xxx:YOUR_PASSWORD@aws-0-ap-south-1.pooler.supabase.com:5432/postgres
SECRET_KEY=your_secure_randomly_generated_string
GROQ_API_KEY=gsk_yourkey
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_key
```

### 2. Backend Initialization
Open a terminal and build your Python environment:
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # For Windows systems
pip install -r requirements.txt
```

Seed the Supabase database with initial Internship Data so the ML engine has rows to target:
```bash
python -c "from app.db.seed import seed_internships_if_empty; from app.db.session import SessionLocal; db = SessionLocal(); seed_internships_if_empty(db); db.close()"
```

Start the FastAPI ASGI server:
```bash
uvicorn app.main:app --reload
```
*The REST API and its interactive documentation will now be available at `http://localhost:8000/docs`.*

### 3. Frontend Initialization
In a separate terminal, install dependencies and launch the client:
```bash
cd frontend
npm install
npm run dev
```
*The Client Interface will be live at `http://localhost:3000`.*

## Administrative Access

To protect user data, the Administrative Document Verification queue is deliberately detached from the main user navigation.
- **Access Route:** `http://localhost:3000/admin`
- **Default Target:** `modiji / Modiji123`

*(This panel directly interfaces with Supabase S3 file signatures, allowing validation of Aadhaar, 10th, 12th, and Diploma documents.)*
