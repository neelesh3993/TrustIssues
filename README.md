# TrustIssues — Real-Time Browser Misinformation Detector

## Overview

**TrustIssues** is a browser extension that helps users verify the credibility of online content in real time. When a user highlights text on any webpage and activates the extension, ScreenShield analyzes the content using an AI pipeline that extracts claims, cross-checks them against external sources, and generates a credibility summary.

The goal is to create a fast, intuitive tool that acts as a **misinformation firewall** for everyday browsing. The system prioritizes explainability: instead of just giving a score, it shows which claims are verified, disputed, or uncertain, along with supporting sources.

---

## Core Features (MVP Scope)

* Highlight text on any webpage and scan it instantly
* Extract key factual claims from the selected text
* Retrieve supporting or contradicting sources
* Generate a credibility score and explanation
* Display a structured summary in an popup UI

Stretch features (if time allows):

* Image authenticity detection
* Full page scanning
* Scan history dashboard
---
## System Architecture

The project is split into two main components:

### 1. Browser Extension (Frontend)

Responsible for:

* Reading highlighted text from webpages
* Sending analysis requests to the backend API
* Displaying credibility reports in a popup UI

Built with:

* Chrome Extension (Manifest V3)
* React for UI

### 2. Backend API Server

Responsible for:

* Running the AI analysis pipeline
* Claim extraction
* Source retrieval and verification
* Credibility scoring
* Summary generation
* Logging and caching

Built with:

* Python FastAPI
* SQLite for lightweight storage

### Data Flow

User highlights text → Extension captures text → POST request to backend → AI pipeline processes content → Structured JSON response → Extension displays results

---

## Tech Stack

### Frontend

* Chrome Extension (Manifest V3)
* React + Vite
* Fetch API for backend communication

### Backend

* Python FastAPI server
* AI pipeline using large language model APIs
* SQLite for caching and logs

### Why This Stack

* Chrome extensions allow direct access to webpage content
* React enables rapid UI development and clean state management
* FastAPI integrates easily with AI workflows and async processing
* SQLite minimizes infrastructure overhead during a hackathon

---

## API Design

### Endpoint

POST `/analyze`

### Request Format

```json
{
  "text": "Highlighted user text to analyze"
}
```

### Response Format

```json
{
  "credibility_score": 0,
  "claims": [
    {
      "claim": "Extracted claim text",
      "status": "verified | disputed | uncertain",
      "sources": [
        "https://example-source-1.com",
        "https://example-source-2.com"
      ]
    }
  ],
  "summary": "Human-readable explanation of credibility"
}
```

---

## AI Pipeline

The backend analysis pipeline runs in four stages:

### 1. Claim Extraction

The system identifies factual claims from the input text.

### 2. Retrieval

For each claim, the system searches external sources and retrieves relevant evidence.

### 3. Verification

Claims are classified as:

* Verified
* Disputed
* Uncertain

### 4. Summarization

The system generates a clear explanation and overall credibility score.

---

## Team Structure and Responsibilities

### Developer A — Extension & Frontend Lead

Responsibilities:

* Build Chrome extension structure
* Implement text selection capture
* Create React popup UI
* Integrate API requests
* Polish user experience

Deliverables:

* Functional extension interface
* Smooth demo workflow

---

### Developer B — AI Pipeline Lead

Responsibilities:

* Build FastAPI backend
* Implement claim extraction logic
* Design verification pipeline
* Generate structured summaries
* Optimize AI prompts

Deliverables:

* Working `/analyze` endpoint
* Reliable credibility output

---

### Developer C — Integration & Infrastructure Lead

Responsibilities:

* Define API schema and contracts
* Set up SQLite storage
* Handle logging and caching
* Connect extension to backend
* Test system reliability

Deliverables:

* Stable integration
* Error handling and fallback behavior

---

## Development Timeline

### Phase 1 — Skeleton Build

* Extension loads with mock data
* Backend server runs with placeholder responses
* Basic API connection works

### Phase 2 — Core Intelligence

* Implement real claim extraction
* Add retrieval and scoring
* Connect full pipeline

### Phase 3 — UI Polish

* Improve layout and formatting
* Optimize performance
* Prepare demo scenarios

### Phase 4 — Stability & Demo Prep

* Fix bugs
* Add error handling
* Finalize presentation

---

## Project Structure

```
screenshield/
├── extension/
│   ├── public/
│   ├── src/
│   ├── manifest.json
│   └── popup/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── pipeline/
│   │   └── database/
│   └── requirements.txt
│
└── README.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- Active internet connection (for API calls)

### Backend API Setup

#### 1. Get Required API Keys

You'll need two API keys for the backend to function:

**A) Google Gemini API Key** (free with Google account)
- Go to: https://makersuite.google.com/app/apikey
- Click "Create API Key" 
- Copy the key to a safe place

**B) NewsAPI Key** (free tier available)
- Go to: https://newsapi.org/
- Sign up for a free account
- Copy your API key from the dashboard

#### 2. Configure Environment Variables

Navigate to the `backend/` directory and create a `.env` file:

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your API keys:

```
GEMINI_API_KEY=your_gemini_key_here
NEWS_API_KEY=your_newsapi_key_here
```

**Alternative: Set as environment variables (Windows PowerShell)**

```powershell
$env:GEMINI_API_KEY='your_gemini_key_here'
$env:NEWS_API_KEY='your_newsapi_key_here'
```

**Alternative: Set as environment variables (Linux/macOS)**

```bash
export GEMINI_API_KEY='your_gemini_key_here'
export NEWS_API_KEY='your_newsapi_key_here'
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Run the Backend Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

**Health Check:**
```bash
curl http://localhost:8000/health
```

### Extension Setup

1. Navigate to frontend folder
2. Install dependencies: `npm install`
3. Build extension: `npm run build`
4. Load in Chrome:
   - Open `chrome://extensions/`
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `frontend` directory

### Testing the Integration

1. Ensure backend is running on port 8000
2. Ensure extension is loaded in Chrome
3. Navigate to any webpage
4. Highlight some text (minimum 50 characters)
5. Click extension icon and click "Scan Text"
6. View credibility analysis results

### Troubleshooting

**Error: "MISSING REQUIRED API KEYS"**
- Ensure you've set `GEMINI_API_KEY` and `NEWS_API_KEY`
- Check `.env` file for syntax errors
- Try setting as environment variables directly

**Error: "API Rate Limit Exceeded"**
- NewsAPI has rate limits on free tier (~100 requests/day)
- Wait a few moments and retry
- Consider upgrading to a paid NewsAPI plan

**Error: "Invalid API Key"**
- Verify keys are correct in `.env` file
- Check that keys haven't expired
- Regenerate keys from provider dashboards

---

## Goals

The primary goal is to deliver a working MVP that:

* Demonstrates real-time misinformation detection
* Provides clear credibility explanations
* Offers a smooth browser-integrated experience

Future work can expand into video analysis, deeper fact-checking, and large-scale deployment.

---
