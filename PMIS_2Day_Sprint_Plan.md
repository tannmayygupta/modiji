# PMIS AI Recommendation Engine — 2-Day Sprint Plan
> Problem Statement #25033 · Ministry of Corporate Affairs · Smart Allocation Engine
> Goal: Ship a **fully working prototype** that solves the core problem end-to-end within 48 hours.

---

## Context for AI (Read This Before Every Session)

You are building an **AI-Based Smart Allocation Engine** for India's PM Internship Scheme (PMIS) for Problem Statement #25033 by the Ministry of Corporate Affairs.

### What the problem actually is
- 621,000 applications → 127,000 opportunities → only 8,700 actually joined (10.6% conversion)
- Candidates cannot find internships that match them → they apply randomly → rejection → dropout
- The system needs to intelligently **match candidates to internships** using AI/ML

### What you must build
A working prototype with:
1. A **hybrid AI recommendation engine** (content-based + collaborative filtering)
2. A **React frontend** showing a 4-step profile wizard → recommendation cards with match %
3. A **Flask REST API** connecting the frontend to the ML engine
4. **Affirmative action scoring** (rural boost, SC/ST/OBC weighting) — this is in the problem statement
5. **"Why this match?" explainability** on every recommendation card

### What "working" means for this submission
- User fills a 4-step form → gets 3–5 ranked internship recommendations in under 2 seconds
- Each card shows: company, role, sector, stipend, location, match %, reason breakdown
- The AI logic is real (not hardcoded) — it actually scores based on skills + education + location
- Affirmative action weights are applied and visible

### Tech stack decided
- **Frontend**: React 18 + TypeScript + Tailwind CSS + Vite
- **Backend**: Python Flask + SQLAlchemy + Redis
- **ML**: scikit-learn (TF-IDF + cosine similarity) + Surprise (SVD for CF)
- **DB**: PostgreSQL (or SQLite for the sprint, swap later)
- **Auth**: Simple JWT for the sprint (Aadhaar stubbed)
- **Deploy**: Docker Compose (single command startup)

### Key constraints
- Must work offline / on low bandwidth (PWA basics)
- Must support Hindi UI (at least the labels)
- Affirmative action boost must be a configurable weight, not hardcoded
- Every recommendation must have a machine-readable explanation (not just a score)

---

## Day 1 — Backend + ML Engine (Complete by midnight)

### Slots overview
| Time | Focus | Output |
|------|-------|--------|
| 9:00–10:30 | Repo setup + DB schema + seed data | Running DB with 500 fake profiles + 50 internships |
| 10:30–13:00 | Content-based recommender | `/recommend` endpoint returning ranked internships |
| 13:00–14:00 | Break | — |
| 14:00–16:30 | Affirmative action scoring + explainability | Scoring layer with boost weights + reason dict |
| 16:30–18:30 | Collaborative filtering scaffold | SVD model trained on seed interaction data |
| 18:30–19:30 | Flask API complete + tested | All endpoints tested via Postman / curl |
| 19:30–21:00 | Docker Compose setup + CORS + mock data polish | `docker-compose up` launches everything |

---

### Day 1 · Slot 1 — Repo + Schema + Seed Data (9:00–10:30)

#### AI Prompt to use
```
You are setting up the backend for a PMIS AI internship recommendation engine.

Create the following:
1. A Python Flask project structure:
   pmis-backend/
   ├── app/
   │   ├── __init__.py
   │   ├── models.py        # SQLAlchemy models
   │   ├── routes/
   │   │   ├── recommend.py
   │   │   ├── profile.py
   │   │   └── internships.py
   │   ├── ml/
   │   │   ├── content_based.py
   │   │   ├── collaborative.py
   │   │   └── hybrid_scorer.py
   │   └── utils/
   │       └── affirmative_action.py
   ├── seed/
   │   └── generate_seed.py
   ├── config.py
   ├── requirements.txt
   └── run.py

2. SQLAlchemy models for:
   - Candidate: id, name, education_level, field_of_study, cgpa, skills (JSON array), 
     sector_interests (JSON array), state, district, is_rural (bool), category (GEN/OBC/SC/ST),
     has_prior_internship (bool), created_at
   - Internship: id, company, role, sector, required_skills (JSON array), 
     min_education, preferred_field, location_state, location_city, stipend_monthly,
     total_slots, filled_slots, is_active (bool)
   - Application: id, candidate_id, internship_id, status (applied/accepted/rejected), 
     recommendation_score (float), created_at
   - RecommendationLog: id, candidate_id, internship_id, content_score, cf_score, 
     affirmative_boost, final_score, reasons (JSON), created_at

3. A seed script that generates:
   - 500 candidate profiles with realistic Indian names, mixed rural/urban, 
     all 4 social categories, 5 education levels (10th/12th/ITI/Diploma/Graduate),
     20+ skill types, 8 sectors
   - 100 internship listings across 24 sectors, 10 states, 
     varied stipends (5000-15000), varied slot sizes
   - 200 past application records (for CF training data)

Use SQLite for the sprint. Include requirements.txt with all dependencies.
Output all files completely.
```

#### What to verify after this slot
- [ ] `python run.py` starts Flask on port 5000
- [ ] DB seeded with 500 candidates + 100 internships
- [ ] `/api/internships` returns list of internships as JSON

---

### Day 1 · Slot 2 — Content-Based Recommender (10:30–13:00)

#### AI Prompt to use
```
Build the content-based filtering module for a PMIS internship recommendation engine.

Context:
- Candidate has: education_level, field_of_study, skills (list), sector_interests (list), 
  state (location preference), district, is_rural, category
- Internship has: required_skills, min_education, preferred_field, sector, 
  location_state, stipend_monthly, total_slots, filled_slots

Build app/ml/content_based.py with a ContentBasedRecommender class that:

1. SKILL MATCHING (weight: 0.35)
   - TF-IDF vectorise candidate skills + internship required_skills
   - Cosine similarity between candidate skill vector and internship skill vector
   - Score: float 0.0–1.0

2. EDUCATION MATCHING (weight: 0.25)
   - Education hierarchy: 10th < 12th < ITI < Diploma < Graduate < Postgraduate
   - Score 1.0 if candidate meets or exceeds requirement
   - Score 0.5 if one level below
   - Score 0.0 if two or more levels below

3. SECTOR INTEREST MATCHING (weight: 0.20)
   - Check if internship sector is in candidate's sector_interests list
   - Score 1.0 if direct match, 0.5 if related sector, 0.0 otherwise
   - Include a SECTOR_RELATIONS dict mapping related sectors

4. LOCATION MATCHING (weight: 0.15)
   - Score 1.0 if same state, 0.6 if candidate prefers pan-India, 0.3 otherwise

5. CAPACITY CHECK (weight: 0.05)
   - Score based on (total_slots - filled_slots) / total_slots
   - 0.0 if internship is full

Final content_score = weighted sum of all 5 components

Also generate for each recommendation a `reasons` dict:
{
  "skill_match": {"score": 0.85, "matched_skills": ["Python", "SQL"], "missing_skills": ["React"]},
  "education_match": {"score": 1.0, "reason": "BCA meets Graduate requirement"},
  "sector_match": {"score": 1.0, "reason": "IT sector matches your interest"},
  "location_match": {"score": 0.6, "reason": "Located in Mumbai, you prefer pan-India"},
  "capacity": {"score": 0.8, "slots_available": 4}
}

Include a method recommend(candidate_id, top_n=5) that returns top N internships with scores + reasons.

Use scikit-learn for TF-IDF. Load all internships from DB at startup and cache them.
Output the complete file.
```

#### What to verify after this slot
- [ ] `recommender.recommend(candidate_id=1, top_n=5)` returns 5 internships with scores
- [ ] Each result has a `reasons` dict with human-readable fields
- [ ] Skills comparison is working (cosine similarity, not string match)

---

### Day 1 · Slot 3 — Affirmative Action Scoring (14:00–15:30)

#### AI Prompt to use
```
Build the affirmative action scoring layer for PMIS internship recommendation engine.

Context: The PM Internship Scheme explicitly requires representation from rural/aspirational 
districts, SC/ST/OBC categories, and first-generation learners.

Build app/utils/affirmative_action.py with an AffirmativeActionScorer class:

BOOST WEIGHTS (all configurable via constructor, these are defaults):
- is_rural = True: +0.08 boost to final score
- category SC/ST: +0.10 boost
- category OBC: +0.05 boost
- district is in aspirational_districts list: +0.06 boost
- has_prior_internship = False (first timer): +0.04 boost
- is_first_generation_learner = True: +0.03 boost

Total max boost: capped at +0.20 (so a great match doesn't get buried by a weaker one with boosts)

Include:
1. A list of 112 aspirational districts from the government's list (at least 20 real ones, 
   rest can be plausible names)
2. apply_boost(candidate, content_score) -> (boosted_score, boost_breakdown) where 
   boost_breakdown is a dict showing which boosts were applied and why
3. The boost must be ADDITIVE to content score, capped at 1.0 total

The boost_breakdown becomes part of the reasons dict on the recommendation card, 
so it must be human-readable:
{
  "affirmative_boosts_applied": [
    {"reason": "Rural district candidate", "boost": +0.08},
    {"reason": "SC/ST category", "boost": +0.10}
  ],
  "total_boost": 0.18,
  "note": "Diversity boost applied per PM Internship Scheme guidelines"
}

Output the complete file.
```

#### What to verify after this slot
- [ ] Rural SC/ST candidate gets higher final score than identical urban GEN candidate
- [ ] Boost breakdown appears in the reasons dict
- [ ] Total boost never pushes score above 1.0

---

### Day 1 · Slot 4 — Collaborative Filtering + Hybrid Scorer (15:30–18:30)

#### AI Prompt to use
```
Build the collaborative filtering module and hybrid scorer for PMIS recommendation engine.

PART 1 — app/ml/collaborative.py

Use the Surprise library (scikit-surprise) to build a CollaborativeFilter class:

1. Load Application records from DB (candidate_id, internship_id, status)
   - Accepted application = rating 5.0
   - Applied but pending = rating 3.0
   - Rejected = rating 1.0

2. Train an SVD model on this interaction matrix

3. Method: predict_score(candidate_id, internship_id) -> float 0.0–1.0
   - Return 0.5 (neutral) if candidate has fewer than 2 interaction records (cold start)
   - Log when cold start is triggered

4. Method: is_cold_start(candidate_id) -> bool
   - True if fewer than 2 interactions

5. Retrain method: retrain() that rebuilds the model from fresh DB data

PART 2 — app/ml/hybrid_scorer.py

Build a HybridScorer class that combines both:

SCORING LOGIC:
- If cold start: weight = 100% content-based, 0% CF
- If 2–10 interactions: weight = 80% content, 20% CF  
- If 10+ interactions: weight = 60% content, 40% CF

hybrid_score = (content_weight * content_score) + (cf_weight * cf_score)
final_score = affirmative_action_scorer.apply_boost(candidate, hybrid_score)

Method: get_recommendations(candidate_id, top_n=5) returns:
[
  {
    "internship_id": 12,
    "company": "Tata Consultancy Services",
    "role": "Software Developer Intern",
    "sector": "IT",
    "location": "Mumbai, Maharashtra",
    "stipend_monthly": 5000,
    "match_percentage": 87,
    "content_score": 0.82,
    "cf_score": 0.79,
    "affirmative_boost": 0.08,
    "final_score": 0.87,
    "reasons": { ...full reasons dict... },
    "scoring_mode": "hybrid"  // or "content_only" for cold start
  }
]

Output both complete files.
```

---

### Day 1 · Slot 5 — Flask API Routes + Docker (18:30–21:00)

#### AI Prompt to use
```
Build the Flask API routes and Docker setup for the PMIS recommendation engine.

ROUTES to build:

1. POST /api/recommend
   Body: { "candidate_id": 1 }  OR  { "profile": { ...anonymous profile... } }
   Response: { "recommendations": [...], "candidate_name": "...", "scoring_mode": "..." }
   
   Support BOTH: logged-in candidate (by ID) AND anonymous profile (for demo/testing)
   For anonymous: create a temporary Candidate object (don't save to DB), run recommender

2. POST /api/profile/create
   Body: full candidate profile JSON
   Response: { "candidate_id": 1, "message": "Profile created" }

3. GET /api/internships
   Query params: ?sector=IT&state=Maharashtra&page=1&limit=20
   Response: paginated list of internships

4. GET /api/internships/<id>
   Response: full internship details

5. POST /api/apply
   Body: { "candidate_id": 1, "internship_id": 5 }
   Response: { "application_id": 12, "status": "applied" }

6. GET /api/stats
   Response: { "total_candidates": 500, "total_internships": 100, 
               "total_applications": 200, "conversion_rate": "10.6%" }

7. GET /api/health
   Response: { "status": "ok", "model_loaded": true, "db_connected": true }

REQUIREMENTS:
- CORS enabled for http://localhost:5173 (React dev server)
- Request/response logging
- Error handling with proper HTTP codes and messages
- All responses in JSON
- API prefix: /api/v1/

Also create:
- docker-compose.yml with services: flask-api, postgres (or sqlite volume), redis
- Dockerfile for Flask app
- .env.example with all config variables
- A README with `docker-compose up` instructions

Output all files completely.
```

#### What to verify before Day 1 ends
- [ ] `docker-compose up` starts everything with one command
- [ ] `POST /api/v1/recommend` with a candidate_id returns 5 recommendations
- [ ] Each recommendation has match_percentage, reasons, company, role
- [ ] `GET /api/v1/stats` shows real counts from seeded DB
- [ ] CORS works (test from browser console)

---

## Day 2 — Frontend + Integration + Polish (Complete by evening)

### Slots overview
| Time | Focus | Output |
|------|-------|--------|
| 9:00–10:30 | React project setup + routing + design system | Working shell with navigation |
| 10:30–13:00 | 4-step onboarding wizard | Complete profile input flow |
| 13:00–14:00 | Break | — |
| 14:00–16:30 | Recommendation results page | Cards with match %, reasons, skill charts |
| 16:30–18:00 | API integration + loading states + error handling | Full end-to-end working |
| 18:00–19:30 | Hindi language support + accessibility | i18n for key strings, WCAG basics |
| 19:30–21:00 | Demo polish + offline mode + final testing | Submission-ready build |

---

### Day 2 · Slot 1 — React Setup + Shell (9:00–10:30)

#### AI Prompt to use
```
Set up a React 18 + TypeScript + Tailwind CSS + Vite project for a PMIS internship 
recommendation frontend. The app is mobile-first, designed for users with limited 
digital literacy in rural India.

PROJECT STRUCTURE:
pmis-frontend/
├── src/
│   ├── components/
│   │   ├── ui/          # Button, Card, Badge, ProgressBar, Spinner
│   │   ├── wizard/      # Step1Education, Step2Skills, Step3Sector, Step4Location
│   │   └── results/     # RecommendationCard, MatchBreakdown, SkillChart
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── WizardPage.tsx
│   │   └── ResultsPage.tsx
│   ├── hooks/
│   │   ├── useRecommendations.ts
│   │   └── useProfile.ts
│   ├── store/
│   │   └── profileStore.ts   # Zustand store for wizard state
│   ├── types/
│   │   └── index.ts          # TypeScript interfaces
│   ├── i18n/
│   │   ├── en.json
│   │   └── hi.json
│   ├── api/
│   │   └── client.ts         # Axios client pointing to Flask API
│   └── App.tsx
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json

DESIGN REQUIREMENTS:
- Mobile-first (375px base), works on Android budget phones
- Minimum 44px touch targets on all interactive elements
- High contrast (WCAG AA minimum)
- Clean, flat design — no heavy gradients
- Color palette: primary blue (#1E40AF), success green (#15803D), 
  neutral grays, white backgrounds

TYPESCRIPT INTERFACES to define in types/index.ts:
- CandidateProfile (all fields from backend Candidate model)
- Internship
- Recommendation (includes match_percentage, reasons, all score fields)
- WizardStep enum
- SkillCategory enum

Create the HomePage with:
- PMIS logo placeholder + "PM Internship Scheme" title
- Brief 2-line explanation of what the tool does
- Large "Find My Internship" CTA button
- Stats bar: "1.18 Lakh Opportunities · 24 Sectors · 735 Districts"

Output all files completely including package.json.
```

---

### Day 2 · Slot 2 — 4-Step Wizard (10:30–13:00)

#### AI Prompt to use
```
Build the 4-step onboarding wizard for the PMIS internship recommendation app.

The wizard collects a candidate profile. It must be extremely simple — designed for 
first-generation learners who may be using a smartphone for the first time.

WIZARD STORE (Zustand — store/profileStore.ts):
Store the complete profile across steps. Each step saves to store before moving next.
Fields: education_level, field_of_study, cgpa, skills[], sector_interests[], 
        preferred_state, open_to_pan_india, category, is_rural, district, name, phone

STEP 1 — Education (Step1Education.tsx):
- Title: "What is your education level?"
- Large tap cards (not dropdowns) for: 10th Pass, 12th Pass, ITI, Diploma, Graduate
- After selecting education, show a second question: "What did you study?"
  - Dropdown with: Engineering, Commerce, Arts, Science, Computer Science, 
    Management, Medical, Other
- Optional CGPA/percentage input (numeric, keyboard)
- Next button disabled until education selected

STEP 2 — Skills (Step2Skills.tsx):
- Title: "What are your skills?"
- Subtitle: "Tap all that apply"
- Grid of skill pill buttons (toggle on/off):
  Communication, MS Office, Computer Basics, Data Entry, English Speaking,
  Python, Java, Web Design, Accounting, Tally, Customer Service, Sales,
  Electrical Work, Mechanical, Welding, Driving Licence, 
  Graphic Design, Video Editing, Social Media, Content Writing
- At least 1 skill must be selected to proceed
- Selected pills shown in blue, unselected in gray

STEP 3 — Sector Interest (Step3Sector.tsx):
- Title: "Which fields interest you?"
- Subtitle: "Choose up to 3"
- Grid of sector cards with emoji icons:
  💻 IT & Technology, 🏦 Banking & Finance, 🏥 Healthcare, 
  🏭 Manufacturing, 🚗 Automobile, ⚡ Energy, 📦 Retail & FMCG,
  🌾 Agriculture, 📚 Education, 🏗️ Infrastructure, 
  🎬 Media & Entertainment, ✈️ Travel & Tourism
- Max 3 selectable, show count "2/3 selected"

STEP 4 — Location (Step4Location.tsx):
- Title: "Where do you want to intern?"
- State dropdown (all 28 Indian states + 8 UTs)
- Toggle: "I'm open to opportunities anywhere in India"
- Category select: General / OBC / SC / ST
- Checkbox: "I am from a rural/village area"
- District text input (optional)

PROGRESS BAR:
- Show "Step X of 4" with a 4-segment progress bar at the top
- Back button on steps 2–4

SUBMIT on Step 4 navigates to ResultsPage and triggers the API call.
All validation inline — no alerts, show error text below the field.

Output all wizard component files completely.
```

---

### Day 2 · Slot 3 — Results Page + Recommendation Cards (14:00–16:30)

#### AI Prompt to use
```
Build the Results page and Recommendation Card components for the PMIS app.

The results page is the most important screen — this is what the evaluators will see.

RESULTS PAGE (pages/ResultsPage.tsx):
- Shows candidate name (or "Your Results") + "Top 5 matches found"
- Loading skeleton (3 placeholder cards) while API call is in progress
- Once loaded: render 5 RecommendationCard components
- "Search again" button at bottom
- If API error: friendly error state with retry button

RECOMMENDATION CARD (components/results/RecommendationCard.tsx):
Each card must show:

HEADER:
- Company name (bold, 16px)
- Role title (14px, secondary color)
- Sector badge (colored pill, e.g. blue for IT, green for Agriculture)

MATCH SCORE (prominent):
- Large circular badge showing "87%" in the card's top-right
- Color: green if >75%, amber if 50–75%, gray if <50%
- Label: "Match"

KEY DETAILS ROW (icons + text):
- 📍 City, State
- 💰 ₹5,000/month stipend  
- 🎓 Graduate required
- 👥 4 slots available

"WHY THIS MATCH?" SECTION (collapsible, expanded by default):
- Show 3–4 reason rows, each with an icon, label, and mini progress bar:
  ✅ Skills matched: Python, SQL (+2 more) [bar: 85%]
  ✅ Sector: IT matches your interest  [bar: 100%]
  ✅ Location: Maharashtra preferred   [bar: 60%]
  ⚠️  Missing: React (not required but helpful)
- If affirmative boost was applied: show a small badge 
  "Diversity boost applied" with an info icon

APPLY BUTTON:
- Full-width "Apply Now" button at bottom of card
- On click: call POST /api/v1/apply and show success state ("Applied ✓")
- Disabled if already applied

SKILL ALIGNMENT CHART (components/results/SkillChart.tsx):
- Simple horizontal bar chart showing matched vs missing skills
- Use inline SVG or a minimal charting approach (no heavy libraries)
- Show: "Matching skills: 3 of 5 required"

MATCH BREAKDOWN MODAL (components/results/MatchBreakdown.tsx):
- Opens when user taps "Why this match?"
- Full breakdown of all 5 scoring components with scores
- Shows affirmative action boosts if applied
- Shows scoring_mode ("Personalised match" or "Profile-based match")

Make all cards accessible: aria-labels, keyboard navigable, 44px tap targets.
Output all component files completely.
```

---

### Day 2 · Slot 4 — API Integration + State Management (16:30–18:00)

#### AI Prompt to use
```
Wire the PMIS React frontend to the Flask backend API.

1. API CLIENT (api/client.ts):
   - Axios instance with baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api/v1'
   - Request interceptor: add loading state
   - Response interceptor: normalise errors
   - Functions:
     * getRecommendations(profile: CandidateProfile): Promise<Recommendation[]>
     * createProfile(profile: CandidateProfile): Promise<{candidate_id: number}>
     * applyToInternship(candidateId: number, internshipId: number): Promise<Application>
     * getStats(): Promise<Stats>
   - For anonymous flow: POST /recommend with full profile object (no DB save needed)

2. ZUSTAND STORE updates (store/profileStore.ts):
   - Add: recommendations[], isLoading, error, hasSearched
   - Action: fetchRecommendations() — calls API, stores results
   - Action: applyToInternship(internshipId) — marks as applied locally
   - Persist profile to localStorage so user doesn't re-fill on refresh

3. CUSTOM HOOKS:
   useRecommendations.ts:
   - Reads from store
   - Returns: { recommendations, isLoading, error, refetch }
   
   useProfile.ts:
   - Reads/writes wizard profile from store
   - Returns: { profile, updateProfile, clearProfile, isComplete }

4. LOADING STATES:
   - Skeleton cards (3 placeholder animated cards) while loading
   - Progress indicator: "Analysing your profile..." → "Matching internships..." → "Done"
   - Use a 3-step fake progress (0% → 40% → 80% → 100%) tied to the API call lifecycle

5. ERROR HANDLING:
   - Network error: "Could not connect. Please check your internet."
   - No results: "No internships matched your profile. Try broadening your interests."
   - Server error: "Something went wrong. Try again."
   - All errors have a Retry button

6. VITE PROXY CONFIG (vite.config.ts):
   Set up proxy so /api calls in dev go to localhost:5000 to avoid CORS issues.

Output all files completely.
```

---

### Day 2 · Slot 5 — Hindi i18n + Accessibility (18:00–19:30)

#### AI Prompt to use
```
Add Hindi language support and accessibility improvements to the PMIS React app.

1. i18n SETUP (react-i18next):
   Translate all user-facing strings in en.json and hi.json:
   
   Key strings to translate:
   - All step titles and subtitles
   - All skill names
   - All sector names
   - Button labels (Next, Back, Apply Now, Find My Internship)
   - Result labels (Match, Skills matched, Why this match, Apply Now)
   - Error messages
   - Stats bar text

   Hindi translations (use Devanagari script):
   - "Find My Internship" → "मेरी इंटर्नशिप खोजें"
   - "What is your education level?" → "आपकी शिक्षा स्तर क्या है?"
   - "What are your skills?" → "आपके कौशल क्या हैं?"
   - "Match" → "मेल"
   - "Apply Now" → "अभी आवेदन करें"
   - "Why this match?" → "यह मेल क्यों?"
   - Translate all skill names, sector names, step titles

2. LANGUAGE TOGGLE:
   - Small EN | हिं toggle in the top-right of every screen
   - Saves preference to localStorage
   - Instant switch, no page reload

3. ACCESSIBILITY (WCAG AA):
   - All images: alt text
   - All interactive elements: aria-label
   - Skill pills: aria-pressed (toggle state)
   - Progress bar: aria-valuenow, aria-valuemax, role="progressbar"
   - Cards: role="article", aria-label with company + match%
   - Color is never the ONLY indicator (add icons + text for all states)
   - Focus visible on all interactive elements (don't remove outline)
   - Tab order is logical (left-to-right, top-to-bottom)

4. LOW-BANDWIDTH OPTIMISATIONS:
   - Lazy load ResultsPage with React.lazy + Suspense
   - Add service worker via vite-plugin-pwa for offline caching
   - Compress API responses (gzip on Flask side)
   - Skeleton screens instead of spinner to reduce perceived load time

Output the i18n JSON files and updated components.
```

---

### Day 2 · Slot 6 — Final Polish + Demo Build (19:30–21:00)

#### AI Prompt to use
```
Prepare the PMIS application for demo/submission. 

1. HOME PAGE POLISH:
   - Add a real impact stats section:
     "Phase 1: 621K applications → 127K opportunities → only 8.7K joined (10.6%)"
     "With AI matching, we target 35-40% conversion rate"
   - Add a "How it works" section with 4 steps and icons
   - Add a demo mode button: "Try Demo (No Sign-up)" that pre-fills a sample profile

2. DEMO MODE:
   - Pre-fill wizard with a sample rural SC/ST candidate profile from Nagpur
   - Show the journey from profile → recommendations in under 10 seconds
   - The demo profile should trigger affirmative action boosts so evaluators see that feature

3. ADMIN/STATS PAGE (simple, just for demo):
   - Route: /stats
   - Shows: total candidates, total internships, applications today, 
     conversion rate, top 5 sectors, top 5 states
   - Real data from GET /api/v1/stats
   - Simple bar charts using inline SVG

4. FINAL README (README.md):
   Write a comprehensive README with:
   - Problem Statement #25033 reference
   - Architecture diagram (ASCII)
   - Setup instructions (docker-compose up)
   - API documentation (all endpoints)
   - ML approach explanation (2 paragraphs)
   - Affirmative action scoring explanation
   - Screenshots placeholder section
   - Team names (Aarya Bhangadia, Rounak Nagwani, Sahil Roy, Tanmay Gupta, Paras Sharma)
   - College: RCOEM Nagpur, Dept. AICS, Semester VI

5. ENVIRONMENT SETUP:
   Create a single setup.sh script:
   #!/bin/bash
   cd pmis-backend && pip install -r requirements.txt && python seed/generate_seed.py
   cd ../pmis-frontend && npm install
   cd .. && docker-compose up --build

Output all files.
```

---

## End-to-End Flow (What Evaluators Will See)

```
User opens app (mobile)
    ↓
HomePage: "PM Internship Scheme — Find Your Match"
    ↓
Taps "Find My Internship" (or "Try Demo")
    ↓
Step 1: Taps "Graduate" → selects "Computer Science"
Step 2: Taps Python, SQL, Communication (3 skills)
Step 3: Taps IT & Technology, Banking & Finance
Step 4: Selects Maharashtra, category SC, is_rural = Yes
    ↓
Submits → Loading: "Analysing your profile..."
    ↓
API call: POST /api/v1/recommend
    {
      "profile": {
        "education_level": "Graduate",
        "field_of_study": "Computer Science",
        "skills": ["Python", "SQL", "Communication"],
        "sector_interests": ["IT", "Banking"],
        "preferred_state": "Maharashtra",
        "category": "SC",
        "is_rural": true
      }
    }
    ↓
ML Engine:
    1. TF-IDF skill match for all 100 internships
    2. Education + sector + location scoring
    3. Cold start → 100% content-based (no CF history)
    4. Affirmative action: SC (+0.10) + rural (+0.08) = +0.18 boost
    5. Sort by final_score descending, take top 5
    ↓
Response:
    [
      {
        "company": "TCS",
        "role": "Software Intern",
        "match_percentage": 91,
        "affirmative_boost": 0.18,
        "reasons": {
          "skill_match": {"score": 0.85, "matched": ["Python", "SQL"]},
          "sector_match": {"score": 1.0},
          "affirmative_boosts_applied": [
            {"reason": "SC category", "boost": 0.10},
            {"reason": "Rural district", "boost": 0.08}
          ]
        }
      },
      ... 4 more
    ]
    ↓
Results page: 5 cards with match %, "Why this match?", Apply Now button
    ↓
User taps Apply → POST /api/v1/apply → "Applied ✓"
```

---

## Checklist — What "Done" Looks Like

### Backend
- [ ] Flask API running on port 5000
- [ ] `/recommend` returns 5 ranked internships in < 2 seconds
- [ ] Content-based scoring: skill TF-IDF + cosine similarity working
- [ ] Affirmative action boost applied and visible in response
- [ ] `reasons` dict on every recommendation (human-readable)
- [ ] DB seeded with 500 candidates + 100 internships
- [ ] Docker Compose starts everything with one command
- [ ] Anonymous profile recommendation (no login needed for demo)

### Frontend
- [ ] 4-step wizard collects full profile
- [ ] Wizard validation (can't skip steps)
- [ ] Results page shows 5 recommendation cards
- [ ] Each card: company, role, match %, stipend, location, "Why this match?"
- [ ] Skill alignment shown (matched vs missing)
- [ ] Affirmative action boost badge visible on relevant cards
- [ ] Apply button works (calls API, shows success)
- [ ] Hindi language toggle (EN / हिं)
- [ ] Loading skeleton while API call in progress
- [ ] Demo mode pre-fills a sample rural SC profile
- [ ] Works on mobile (375px)

### Demo Quality
- [ ] `docker-compose up` works from scratch
- [ ] Full flow (wizard → results → apply) works end-to-end
- [ ] Demo mode shows affirmative action in action
- [ ] Stats page shows real data
- [ ] README explains the ML approach clearly

---

## Scope Decisions (What We Are NOT Building in 2 Days)

| Feature | Why skipping | When to add |
|---------|-------------|-------------|
| Aadhaar OTP auth | UIDAI integration takes weeks | Phase 2 |
| Real PMIS portal API | Requires MoCA access credentials | Phase 2 |
| Collaborative filtering with real history | No real user data yet | Phase 2 |
| Regional language NLP (IndicBERT) | Complex setup | Phase 2 |
| PWA full offline mode | Nice-to-have | Phase 2 |
| Skill-gap analysis + NSDC links | Additive feature | Phase 3 |
| K8s / production infra | Not needed for prototype | Phase 3 |
| DPDP Act compliance audit | Legal process | Phase 3 |

**What we ARE demonstrating exists and works:**
- The core AI matching algorithm (real TF-IDF + cosine similarity)
- Affirmative action scoring (real boost weights, visible in UI)
- Explainability ("Why this match?" — real reasons from the algorithm)
- The full user journey from profile → recommendation → application

---

## Quick Reference — Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| DB for sprint | SQLite | Zero setup, swap to PostgreSQL in Phase 2 |
| Auth for sprint | No auth / demo mode | Unblocks frontend development |
| CF for sprint | Scaffold only, real output from content-based | Cold start problem — no real data |
| Styling | Tailwind CSS | Fastest mobile-first UI development |
| State management | Zustand | Lighter than Redux, works for this scope |
| Charts | Inline SVG | No extra library weight |
| Language support | react-i18next | Industry standard, easy to extend |
| Seed data | 500 candidates + 100 internships | Enough for CF to produce non-trivial results |

---

## Folder Structure (Final)

```
pmis/
├── pmis-backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── recommend.py
│   │   │   ├── profile.py
│   │   │   └── internships.py
│   │   ├── ml/
│   │   │   ├── content_based.py
│   │   │   ├── collaborative.py
│   │   │   └── hybrid_scorer.py
│   │   └── utils/
│   │       └── affirmative_action.py
│   ├── seed/
│   │   └── generate_seed.py
│   ├── config.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run.py
├── pmis-frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── store/
│   │   ├── types/
│   │   ├── i18n/
│   │   └── api/
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docker-compose.yml
├── setup.sh
└── README.md
```

---

*Built by Aarya Bhangadia, Rounak Nagwani, Sahil Roy, Tanmay Gupta, Paras Sharma*
*RCOEM Nagpur · Department of AICS · B.Tech IT / CSE (AICS) · Semester VI*
*Problem Statement #25033 · Ministry of Corporate Affairs · Smart Automation*
