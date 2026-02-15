# 2026-HackNC
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

### Backend

1. Navigate to backend folder
2. Install dependencies
3. Run FastAPI server

### Extension

1. Build React frontend
2. Load extension in Chrome developer mode
3. Connect to backend API endpoint

---

## Goals

The primary goal is to deliver a working MVP that:

* Demonstrates real-time misinformation detection
* Provides clear credibility explanations
* Offers a smooth browser-integrated experience

Future work can expand into video analysis, deeper fact-checking, and large-scale deployment.

---
