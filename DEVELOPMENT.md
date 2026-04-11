# 🚀 PM Internship Recommendation Engine: Development Retrospective

## 1. Project Overview & Vision
**The Goal:** To build a high-performance, intelligent platform for the Government of India's PM Internship Scheme. The platform is designed to effortlessly ingest candidate profiles, verify technical and educational backgrounds, and leverage advanced AI to analyze self-introduction videos. This ultimately powers a Collaborative Filtering engine to accurately match candidates with optimal internship sectors and locations.

**Core Philosophy:** 
- **Frictionless Onboarding:** A deeply interactive multi-step wizard.
- **AI-Powered Assessment:** Moving beyond just text by evaluating candidate confidence and clarity via video transcription and Large Language Model analysis.
- **Scalable Architecture:** A completely decoupled frontend-backend microservices model.

---

## 2. Technical Stack Definition
We selected a hyper-modern, scalable stack aimed at extreme developer velocity and production readiness.

### Frontend 💻
*   **Framework:** Next.js 14 (App Router)
*   **Styling:** Tailwind CSS (v4) with dark mode and custom CSS tokens.
*   **UI Components:** Custom mapped `shadcn/ui` logic with Framer Motion for liquid-smooth transitions.
*   **State Management:** React Hooks (`useState`, `useRef`) for local wizard tracking and layout encapsulation.

### Backend ⚙️
*   **Core:** FastAPI (Python) for ultra-fast asynchronous REST APIs.
*   **Database:** SQLite (MVP phase) managed dynamically via SQLAlchemy ORM.
*   **Validation:** Pydantic (v2) for rigid schema typing and `.env` parsing.
*   **AI Integration:** Groq Cloud SDK natively interacting with `whisper-large-v3-turbo` (transcription) and `llama-3.3-70b-versatile` (semantic analysis).
*   **Media Processing:** `imageio-ffmpeg` for headless, cross-platform audio extraction.

---

## 3. Implementation Phasing

### Phase 1: Authentication & Schema Setup
We bypassed expensive standard OTP platforms by engineering a **Dev Bypass Token architecture** mimicking Firebase. Concurrently, we established robust ORM models tracking `Candidate` metrics (skills, locations) and `CandidateDocuments` (10th/12th marksheets).

### Phase 2: The Interactive Wizard Flow
Instead of a boring single-page form, we built `WizardFlow.tsx`:
1.  Aadhaar Mock Verification.
2.  Document Upload (Marksheets).
3.  Resume Upload (AI Text Extraction).
4.  Academic & Skill Selection.
5.  State & District Geo-Mapping.
6.  The **Video Introduction Analysis**.

### Phase 3: The AI Engine implementation
We integrated Groq to process candidate videos in under 3 seconds. The backend intercepts the `.mp4`, strips the heavy video layer off to create an audio track, funnels it through Whisper to get a raw transcript, and finally feeds that transcript to Llama 3.3 to score the candidate's **Communication, Confidence, and Clarity**.

---

## 4. Key Engineering Challenges & Triumphs

Throughout development, we encountered several intense blockers that required deep architectural pivoting.

### 🔴 Challenge 1: The Database Schema Drift (`sqlite3.OperationalError`)
*   **The Issue:** Midway through development, we upgraded the `Candidate` model to track new metric columns (`communication_score`, `clarity_score`, `video_path`). SQLAlchemy crashed because the existing SQLite physical database file was stale.
*   **The Fix:** We implemented a brutal but effective database reset protocol, completely destroying the corrupted `pmis.db` and forcing the ORM engine to perfectly rebuild the relational tables from scratch upon the next Uvicorn boot cycle.

### 🔴 Challenge 2: Sticky Document Conflict Errors (`HTTP 409 Conflict`)
*   **The Issue:** When users made a mistake and tried to re-upload their 10th marksheet, the REST API threw a `409` error because the database logically rejected duplicate `doc_type` keys to protect disk space.
*   **The Fix:** We rewrote the `documents.py` controller to handle aggressive **Upserting**. If a file exists, the Python OS module physically wipes the legacy file from the hard drive, drops the old database row, and cleanly swaps in the newly uploaded payload.

### 🔴 Challenge 3: Pydantic Settings Validation Crash (`extra_forbidden`)
*   **The Issue:** Fast API failed to even start after injecting `GROQ_API_KEY` into the `.env` file. Pydantic v2 has an aggressive security lock that crashes the server if it detects environment variables not explicitly typed inside `app/config.py`.
*   **The Fix:** We securely whitelisted the key by mapping `GROQ_API_KEY: str | None = None` inside the `Settings` class, and permanently altered the Pydantic parser logic to `extra = "ignore"`, bulletproofing the backend against future variable crashes.

### 🔴 Challenge 4: The Whisper Media Bottleneck (`HTTP 413 Entity Too Large`)
*   **The Issue:** Ffmpeg wasn't natively installed on the host Windows machine. When users uploaded 50MB video files, the audio extraction sequence silently crashed and triggered a fallback mechanism that blindly forwarded the massive 50MB `.mp4` file directly to the Groq API. Groq intercepted this and instantly threw a `413 Request Entity Too Large` error due to their strict 25 MB file limit.
*   **The Fix:** We abandoned the system-level dependency and strategically installed `imageio-ffmpeg` via Python Pip. This embedded a headless Ffmpeg binary directly inside the backend. We updated the extraction script to convert the heavy video into a highly compressed **64kbps mono MP3**. Now, a 50MB video is compressed to ~500KB in milliseconds, effortlessly passing through the AI pipeline constraints. We also hard-rebooted the entire Node.js/Python server matrix to clear the Python module caches, finally resolving the ghost crashes.

---

## 5. Looking Forward
With the foundational UI, Database, and extremely robust AI-video pipeline completely stabilized, the platform is now fully primed for:
1.  **Cloud Storage Integration:** Hooking up the document routers permanently to AWS S3 or Cloudinary.
2.  **The Collaborative Filtering ML Model:** Utilizing the newly extracted database parameters (Scores, Skills, Sectors) to dynamically feed PyTorch/Scikit-Learn recommendation engines.
