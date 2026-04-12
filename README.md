# PM Internship Scheme: Intelligent Recommendation Engine

## Introduction

The PM Internship Recommendation Engine is an AI-driven platform built to address Problem Statement #25033 from the Ministry of Corporate Affairs, Government of India. As the volume of youth entering the workforce increases, traditional internship and job platforms suffer from significant friction points: poor skill-to-role matching, generic data entry forms, lack of verified documentation, and an inability to assess qualitative candidate traits like communication and clarity.

## What We Are Solving

This platform serves as a modern bridge between aspiring candidates and corporations offering internships under the Prime Minister's Scheme. We specifically solve the following issues:

1. **Information Friction:** Creating an intuitive, step-by-step onboarding wizard rather than an exhausting single-page form.
2. **Qualitative Blindspots:** Establishing a custom AI video analysis pipeline that evaluates a candidate's introduction video to automatically score their clarity and confidence.
3. **Ineffective Matching:** Moving away from static keyword filtering to a robust Hybrid Machine Learning Recommendation Engine leveraging Content-Based (TF-IDF/Semantic) and Collaborative Filtering mathematics to ensure high-accuracy skill and sector mapping.
4. **Administrative Verification:** Providing an isolated, fast-action Admin Gateway to review candidate credentials (10th, 12th, and Diploma marksheets) directly from Cloud CDN Storage.

## System Architecture

The architecture is built on a highly decoupled structure, prioritizing raw performance, distinct separation of concerns, and ease of scalability.

- **Frontend Application:** Built using Next.js 14 and React. It operates entirely as a static, pre-rendered client communicating externally to the API layer. State management is handled locally, and complex aesthetic transitions rely heavily on custom CSS alongside Framer Motion.
- **Backend Service:** Powered by FastAPI (Python 3.12). This layer handles all heavy lifting, including relational database transactions, authentication routing, file handling, and synchronous bridging to the Machine Learning pipelines.
- **Data Persistence:** Relational data operations are handled via SQLite, heavily abstracted by SQLAlchemy ORM to allow effortless migration to PostgreSQL. Document payloads are handled cleanly via Supabase Cloud Storage APIs, rather than straining local server disk operations.
- **AI Processing Pipeline:** Incorporates Groq's Large Language Models and specialized audio extraction protocols to securely evaluate human dialogue without exhausting standard infrastructure limits.

## Project Structure

```text
pm-internship-engine/
├── frontend/          # Next.js 14 Client Server
│   ├── src/app/       # Application routing
│   └── src/components/# Isolated UI components and flows
├── backend/           # FastAPI Application Core
│   ├── app/
│   │   ├── api/       # RESTful HTTP routers
│   │   ├── models/    # Database table architectures
│   │   ├── services/  # Cloud and Video extraction logic
│   │   └── db/        # Data seed scripts
├── ml/                # Machine Learning Operations
│   ├── engine/        # Hybrid Algorithm logic
│   └── data/          # Synthetic dataset generators
```

## Setup Instructions

This platform utilizes separate servers for the Frontend and Backend to simulate production-grade interactions.

### 1. Environment Configurations
Ensure you have Python 3.11+ and Node.js 18+ installed on your system.
You will need a `.env` file at the root of the `/backend` directory containing your respective Supabase and Groq keys, as well as the standard backend port definition.

### 2. Backend Initialization
Navigate to the backend directory, initialize a virtual environment, and install the required dependencies.

```bash
cd backend
python -m venv venv
venv\Scripts\activate      # For Windows systems
pip install -r requirements.txt
```

Initialize the baseline synthetic data generation and seed the database to test the Machine Learning algorithms immediately.

```bash
cd ../ml/data
python synthetic_generator.py

cd ../../backend
python -m app.db.seed
```

Start the FastAPI ASGI server on port 8000.

```bash
uvicorn app.main:app --reload --port 8000
```
The REST API and its interactive documentation will now be available at `http://localhost:8000/docs`.

### 3. Frontend Initialization
In a separate terminal, navigate to the frontend directory. Install Node package modules and spin up the development instance.

```bash
cd frontend
npm install
npm run dev
```
The Client Interface will be live at `http://localhost:3000`.

## Administrative Access

To protect user data, the Administrative Verification queue is decoupled from the main interface structure. To access pending user documents, navigate manually to `/admin`.
- Default Username: modiji
- Default Password: Modiji123

This panel automatically pulls unverified candidate payloads and dictates the progression of a candidate's authorization step based on document veracity.

## Machine Learning Integration Strategy

The project implements a Hybrid Engine weighing multiple aspects of a candidate's profile. Content-Based filtering dictates geographic and educational alignments, while TF-IDF vectorization clusters matching terminology. Following initial MVP evaluations, this sub-system is configured to shift from static seeded arrays toward a full Kaggle-ingested dataset pipeline, significantly enhancing model training depth.

## Team Attributes
- Tanmay Gupta | Aarya Bhangadia | Rounak Nagwani | Sahil Roy | Paras Sharma
- Shri Ramdeobaba College of Engineering and Management, Nagpur
