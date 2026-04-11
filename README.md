# PM Internship — AI-Based Smart Allocation Engine

> AI-powered recommendation engine for the PM Internship Scheme
> Problem Statement #25033 | Ministry of Corporate Affairs

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend   │────▶│  FastAPI      │────▶│  ML Engine       │
│   Next.js    │◀────│  Backend      │◀────│  Hybrid AI       │
└─────────────┘     └──────┬───────┘     └─────────────────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL   │
                    │  + Redis      │
                    └──────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (for PostgreSQL + Redis)

### 1. Start the database
```bash
docker-compose up -d db redis
```

### 2. Set up the backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Generate synthetic data
```bash
cd ml/data
python synthetic_generator.py
```

### 4. Seed the database
```bash
cd backend
python -m app.db.seed
```

### 5. Start the API server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API docs at: http://localhost:8000/docs

### 6. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend at: http://localhost:3000

## 📁 Project Structure

```
pm-internship-engine/
├── frontend/          # Next.js 14 + Tailwind CSS
├── backend/           # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/v1/    # REST API routes
│   │   ├── models/    # SQLAlchemy ORM models
│   │   ├── schemas/   # Pydantic request/response schemas
│   │   ├── services/  # Business logic
│   │   └── db/        # Database session + seed
│   └── tests/
├── ml/                # AI/ML Engine
│   ├── engine/        # Content-based, Collaborative, Hybrid, Explainer
│   ├── data/          # Synthetic data generator
│   └── evaluation/    # Metrics and testing
└── docker-compose.yml
```

## 🧠 AI Engine

- **Content-Based Filtering** (60%): Skills (TF-IDF + cosine), education, location, sector matching
- **Collaborative Filtering** (40%): SVD matrix factorization on interaction data
- **Affirmative Action**: Configurable boosts for aspirational districts, SC/ST/OBC, rural candidates
- **Explainability**: "Why This Match?" with per-recommendation explanations

## 👥 Team

- Tanmay Gupta | Aarya Bhangadia | Rounak Nagwani | Sahil Roy | Paras Sharma
- Shri Ramdeobaba College of Engineering and Management, Nagpur
