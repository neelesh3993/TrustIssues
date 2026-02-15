# Source Retrieval Flow - Complete Guide

## 📊 **Data Flow Diagram**

```
Browser Extension (Frontend)
    ↓
    └─→ Gets page content (2000+ chars)

HTTP POST to Backend
    ↓
    ├─ URL: http://localhost:8000/api/analyze
    ├─ Content: Article text
    └─ Title: Page title

Backend Analysis Pipeline
    ↓
    ├─ Step 1: Extract Claims (using Gemini AI)
    │   └─ Input: Article text
    │   └─ Output: ["Claim 1", "Claim 2", "Claim 3"]
    │
    ├─ Step 2: Verify Claims (using NewsAPI + Gemini)
    │   └─ For EACH claim:
    │       ├─ Search NewsAPI for articles
    │       │  └─ `search_news_with_fallback(claim)`
    │       │     └─ Returns: [article1, article2, article3, ...]
    │       │
    │       ├─ Send articles to Gemini for reasoning
    │       │  ├─ Input: Claim + articles from NewsAPI
    │       │  └─ Output: "verified" | "disputed" | "uncertain"
    │       │
    │       └─ Return verification result with sources:
    │           {
    │               "claim": "Paris is capital",
    │               "status": "verified",
    │               "rationale": "Multiple sources confirm...",
    │               "sources": [          ← FROM NewsAPI!
    │                   {"name": "BBC", "headline": "...", "snippet": "..."},
    │                   {"name": "CNN", "headline": "...", "snippet": "..."},
    │                   ...
    │               ]
    │           }
    │
    ├─ Step 3: Format for Response
    │   └─ _format_sources() function
    │       ├─ Extract top 2 sources per claim
    │       ├─ Create Source objects with:
    │       │   ├─ name (source domain)
    │       │   ├─ headline
    │       │   └─ status (verified/disputed/uncertain)
    │       └─ Return: List[Source]
    │
    └─ Step 4: Return Response to Frontend
        {
            "aiGenerationLikelihood": 40.0,
            "credibilityScore": 75.0,
            "manipulationRisk": 30.0,
            "findings": ["✓ VERIFIED: Paris is capital", ...],
            "sources": [    ← FORMATTED SOURCES FOR UI
                {
                    "name": "BBC",
                    "headline": "Paris is the capital of France",
                    "status": "verified"
                },
                {
                    "name": "Wikipedia",
                    "headline": "Cities of France: Paris facts",
                    "status": "verified"
                }
            ],
            "report": "Overall credibility is high..."
        }

Browser Extension (Frontend)
    ↓
    └─→ Display in popup:
        ├─ Scores
        ├─ Report text
        ├─ Findings list
        └─ Sources in "Sources Checked" section
```

---

## 🔍 **Detailed Breakdown**

### **1️⃣ NewsAPI Call in Verifier**

**File**: [backend/app/pipeline/verifier.py](backend/app/pipeline/verifier.py#L85)

```python
def _verify_single_claim(claim: str) -> Dict:
    # Step 1: Search NewsAPI for this claim
    sources = search_news_with_fallback(claim)  # ← Gets articles from NewsAPI
    
    if not sources:
        return {
            "claim": claim,
            "status": "uncertain",
            "sources": []  # Empty if no articles found
        }
    
    # Step 2: Format articles for Gemini
    source_text = "Retrieved evidence:\n"
    for i, source in enumerate(sources, 1):
        source_text += (
            f"{i}. [{source['name']}] {source['headline']}\n"
            f"   {source['snippet']}\n"
            f"   URL: {source['url']}\n\n"
        )
    
    # Step 3: Send to Gemini with articles
    result = _classify_claim_with_gemini(claim, source_text, sources)
    #                                                              ↑↑↑↑↑↑↑
    #                                                          Passes raw sources
    
    return result
```

**What `search_news_with_fallback()` returns:**

```python
[
    {
        "name": "BBC News",              # ← Source domain
        "headline": "Paris remains...",  # ← Article title
        "url": "https://bbc.com/...",   # ← Article link
        "snippet": "The capital of...",  # ← Article excerpt
        "publishedAt": "2026-02-15"     # ← Publish date
    },
    {
        "name": "Wikipedia",
        "headline": "Paris (City)",
        "url": "https://wikipedia.org/...",
        "snippet": "Paris is the capital...",
        "publishedAt": "2026-01-20"
    },
    ...more articles...
]
```

---

### **2️⃣ Gemini Classification**

**File**: [backend/app/pipeline/verifier.py](backend/app/pipeline/verifier.py#L130)

```python
def _classify_claim_with_gemini(claim: str, source_text: str, sources: List[Dict]) -> Dict:
    prompt = f"""Classify this claim based on the evidence:

CLAIM: {claim}

EVIDENCE:
{source_text}

Respond with JSON: {{"status": "verified/disputed/uncertain", "rationale": "..."}}"""
    
    response = client.generate_text(prompt, ...)  # Gemini analyzes
    parsed = _parse_classification_json(response)
    
    # Return with original sources attached
    result = {
        "claim": claim,
        "status": parsed.get("status"),
        "rationale": parsed.get("rationale"),
        "sources": sources[:3]  # ← Top 3 articles from NewsAPI
    }
    return result
```

**Output from Gemini**:
```json
{
    "status": "verified",
    "rationale": "Multiple reliable sources confirm Paris is the capital of France."
}
```

**But we keep the NewsAPI articles** via `sources[:3]`

---

### **3️⃣ Formatting for Response**

**File**: [backend/app/routes/analyze.py](backend/app/routes/analyze.py#L380)

```python
def _format_sources(verification_results: List[dict]) -> List[Source]:
    sources = []
    
    for result in verification_results:
        # result looks like:
        # {
        #     "claim": "Paris is capital",
        #     "status": "verified",
        #     "rationale": "...",
        #     "sources": [newsapi articles...]  ← FROM VERIFIER
        # }
        
        # Extract top 2 sources per claim
        for source in result.get("sources", [])[:2]:
            source_obj = Source(
                name=source.get("name", "Unknown"),      # BBC, Wikipedia, etc.
                headline=source.get("headline", ""),     # Article title
                status=result.get("status", "uncertain") # verified/disputed
            )
            sources.append(source_obj)
    
    return sources
```

**Note**: We only pass `name`, `headline`, and `status` to frontend
- **Don't sent**: `url`, `snippet`, `publishedAt`
- **Why**: Simpler UI, less data, frontend can fetch if needed

---

### **4️⃣ Full API Response**

**File**: [backend/app/models/schemas.py](backend/app/models/schemas.py#L33)

```python
class AnalysisResponse(BaseModel):
    aiGenerationLikelihood: float
    credibilityScore: float
    manipulationRisk: float
    findings: List[str]
    sources: List[Source]  # ← What we just formatted!
    report: str

class Source(BaseModel):
    name: str              # "BBC News"
    headline: str          # "Paris is the capital of France"
    status: str            # "verified" or "disputed" or "uncertain"
```

---

## 📈 **Complete Flow Example**

### **Input Article**:
```
"Paris is the capital of France and has a population of 2 million people."
```

### **Pipeline Execution**:

**1. Extract Claims** (Gemini):
```
✓ Output: ["Paris is the capital of France", 
           "Paris has a population of 2 million"]
```

**2. Verify Claim 1: "Paris is the capital of France"**

**a) Search NewsAPI**:
```python
articles = search_news_with_fallback("Paris is the capital of France")
# Returns 5 articles from BBC, Wikipedia, Britannica, etc.
```

**b) Send to Gemini**:
```
Prompt: "CLAIM: Paris is the capital of France
         EVIDENCE: 
         1. [BBC] Paris Remains France's Capital...
         2. [Wikipedia] Geography of France...
         ..."
         
Gemini Response: {"status": "verified", 
                  "rationale": "Multiple sources confirm Paris is France's capital"}
```

**c) Package Result**:
```python
{
    "claim": "Paris is the capital of France",
    "status": "verified",
    "rationale": "Multiple sources confirm...",
    "sources": [
        {"name": "BBC", "headline": "Paris Remains...", ...},
        {"name": "Wikipedia", "headline": "Paris (City)...", ...},
        {"name": "Britannica", ...}
    ]
}
```

**3. Verify Claim 2: "Paris has a population of 2 million"**

(Same process...)

**4. Format Sources**:
```python
# Get top 2 sources from each verification result
[
    Source(name="BBC", headline="Paris Remains...", status="verified"),
    Source(name="Wikipedia", headline="Paris (City)...", status="verified"),
    Source(name="Britannica", headline="...", status="verified"),
    Source(name="Reuters", headline="...", status="uncertain")
]
```

**5. Return to Frontend**:
```json
{
    "aiGenerationLikelihood": 15.0,
    "credibilityScore": 95.0,
    "manipulationRisk": 20.0,
    "findings": [
        "Majority of claims (2/2) were verified.",
        "✓ VERIFIED: Paris is the capital of France"
    ],
    "sources": [
        {
            "name": "BBC",
            "headline": "Paris Remains France's Capital",
            "status": "verified"
        },
        {
            "name": "Wikipedia",
            "headline": "Paris (City page)",
            "status": "verified"
        }
    ],
    "report": "The content exhibits high credibility..."
}
```

---

## 🎯 **Key Functions**

| Function | File | Purpose |
|----------|------|---------|
| `search_news_with_fallback()` | news_client.py | Queries NewsAPI, returns articles |
| `_verify_single_claim()` | verifier.py | Gets sources + Gemini classification |
| `_classify_claim_with_gemini()` | verifier.py | Sends articles to Gemini, gets verdict |
| `verify_claims()` | verifier.py | Orchestrates verification for all claims |
| `_format_sources()` | analyze.py | Extracts sources for API response |
| `analyze_content()` | analyze.py | Main endpoint, orchestrates pipeline |

---

## 📋 **Source Retrieval Summary**

```
NewsAPI
   ↓
search_news_with_fallback(claim)
   ↓
Returns articles
   ↓
Sent to Gemini for classification
   ↓
Gemini returns: "verified" | "disputed" | "uncertain"
   ↓
Articles stored in result["sources"]
   ↓
_format_sources() extracts them
   ↓
Returned in API response
   ↓
Frontend displays in "Sources Checked" section
```

That's the complete flow! 🎯
