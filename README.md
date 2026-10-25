# TrustLens AI 🔍🛡️

TrustLens AI is a full-stack, cloud-native cybersecurity application designed to detect and explain phishing URLs in real time. Rather than operating as a black-box detector, the system couples machine learning classification with game-theory explainability (SHAP) to inform users exactly why a link is deemed malicious.

> **Status:** Backend API fully containerized & hosted on Hugging Face Spaces. Frontend UI ready for local execution (Vercel deployment planned).

---

## 🏗️ Architecture & Pipeline Flow

```text
[ Next.js Dashboard ]
│   (POST /api/v1/scan)
▼
[ FastAPI / Uvicorn Server ]
│   (Extract URL telemetry: entropy, hyphens, keyword patterns)
▼
[ XGBoost Classifier + SHAP Explainability Engine ]
│   (Calculates Risk Score & Top Contributing Threat Factors)
▼
[ MongoDB Atlas ] ───► Logs Scan Ledger & Telemetry
│
▼
[ Real-Time UI Render ] ───► Threat Verdict + Factor Breakdown
```

1. **User Input (Frontend)**: The user submits a suspicious link through the Next.js/React web dashboard.
2. **Feature Extraction (Backend)**: The FastAPI server computes mathematical URL telemetry—including Shannon entropy, anomaly counts (hyphens, dots), and deceptive keyword signatures.
3. **Threat Classification (AI Engine)**: An XGBoost classifier evaluates the extracted telemetry against trained patterns to produce a calibrated risk score.
4. **Explainability Engine (SHAP)**: The system applies SHAP (SHapley Additive exPlanations) values to isolate the primary feature responsible for the threat verdict.
5. **Telemetry & Ledger Logging (Database)**: The complete scan record (URL, risk score, verdict, explanation, timestamp) is persisted in MongoDB Atlas via PyMongo.
6. **Live Telemetry Output**: The client dashboard renders the risk score, security badges, threat analysis, and previous scan logs.

---

## 🛠 Tech Stack

### Frontend (User Interface)
* **Framework**: Next.js (App Router), React, TypeScript (`.tsx`)
* **Styling**: Modern CSS / Tailwind CSS

### Backend (API & Server)
* **Framework**: FastAPI (Python 3.11)
* **Server**: Uvicorn (ASGI)
* **Validation**: Pydantic models (request/response schemas)

### Artificial Intelligence & Machine Learning
* **Classifier**: XGBoost (Extreme Gradient Boosting)
* **Explainability**: SHAP (SHapley Additive exPlanations)
* **Data Processing**: Pandas, NumPy

### Database (Storage)
* **Database**: MongoDB Atlas (Cloud NoSQL)
* **Driver**: PyMongo

### DevOps & Infrastructure
* **Backend Hosting**: Hugging Face Spaces (16GB RAM environment)
* **Containerization**: Docker
* **Version Control**: Git, GitHub
* **Frontend Hosting Target**: Vercel (Planned)

---

## 🗺️ Deployment Roadmap
- [x] Train and serialize XGBoost detection model.
- [x] Implement SHAP explainability calculations for top threat vectors.
- [x] Dockerize FastAPI backend with dedicated non-root user permissions.
- [x] Deploy containerized backend microservice to Hugging Face Spaces.
- [x] Configure MongoDB Atlas telemetry logging via PyMongo.
- [ ] Deploy production Next.js frontend to Vercel and link custom domain.

---

## 🚀 Running Locally

### 1. Clone the Repository
```bash
git clone [https://github.com/pratham009thakur-dev/trustlens-ai.git](https://github.com/pratham009thakur-dev/trustlens-ai.git)
cd trustlens-ai
```

### 2. Backend Setup (FastAPI)
```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup (Next.js)
```bash
cd ../frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.