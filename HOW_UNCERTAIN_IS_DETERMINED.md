# How "UNCERTAIN" Claims Are Determined

## Overview

When you see a claim marked as **UNCERTAIN**, it means one of the following happened during verification:

---

## 4 Ways a Claim Becomes UNCERTAIN

### 1️⃣ **No News Evidence + No Gemini Knowledge**

**Flow:**
```
Claim extracted → NewsAPI searched → NO SOURCES FOUND
              → Gemini asked → "I don't have information about this"
              → Result: UNCERTAIN
```

**Example:**
- Claim: "A new discovery was made yesterday at a small lab"
- Problem: Too recent, too specific for news databases to cover
- Result: **UNCERTAIN** (Gemini can't confidently verify without sources)

**Rationale shown:** "Insufficient evidence found"

---

### 2️⃣ **Mixed or Conflicting Evidence**

**Flow:**
```
Claim extracted → NewsAPI searched → SOURCES FOUND
              → Evidence is contradictory or unclear
              → Gemini evaluates → "Evidence doesn't clearly support or refute"
              → Result: UNCERTAIN
```

**Example:**
- Claim: "Remote work productivity is higher than office work"
- Evidence: Some studies say yes, others say no, depends on context
- Result: **UNCERTAIN** (Evidence is mixed, not conclusive)

**Rationale shown:** "Evidence is mixed and inconclusive"

---

### 3️⃣ **Technical Error During Verification**

**Flow:**
```
Claim extracted → NewsAPI searched → (may or may not find sources)
              → Gemini called → ERROR OCCURS
              → Exception caught → Fallback to UNCERTAIN
              → Result: UNCERTAIN
```

**Possible Errors:**
- ❌ API key missing or invalid
- ❌ Network timeout
- ❌ Gemini API rate limit exceeded
- ❌ Settings attribute missing (this was your error)

**Rationale shown:** "AI verification failed: [error details]"

**Your Error:**
```
"AI verification failed: 'Settings' object has no attribute 'backboard_api_key'"
```

This has been **FIXED** - added `backboard_api_key` to Settings class.

---

### 4️⃣ **Ambiguous or Opinion-Based Claims**

**Flow:**
```
Claim extracted → NewsAPI searched → SOURCES FOUND
              → Sources don't provide clear verification
              → Gemini evaluates → "This is subjective/ambiguous"
              → Result: UNCERTAIN
```

**Example:**
- Claim: "The best way to learn programming is through projects"
- Problem: Can't be verified objectively, it's subjective
- Result: **UNCERTAIN** (Not a verifiable fact)

**Rationale shown:** "Claim is subjective and cannot be definitively verified"

---

## The Decision Logic in Code

```python
def _classify_claim_with_gemini(claim: str, source_text: str, sources: List) -> Dict:
    
    prompt = """Classify as VERIFIED, DISPUTED, or UNCERTAIN based on evidence:
    
    CLAIM: {claim}
    EVIDENCE: {source_text}
    """
    
    try:
        # Call Gemini with the claim and evidence
        response = client.generate_text(prompt)
        
        # Parse response
        parsed = _parse_classification_json(response)
        status = parsed.get("status", "uncertain")  # Default to uncertain
        
        # Validate status
        if status not in ["verified", "disputed", "uncertain"]:
            status = "uncertain"  # Fallback if invalid
        
        return {"status": status, "rationale": parsed.get("rationale")}
        
    except Exception as e:
        # If ANY error occurs, return uncertain
        return {
            "status": "uncertain",
            "rationale": f"AI verification failed: {str(e)}"
        }
```

---

## When Claims Get Each Status

| Status | Meaning | Requires | Example |
|--------|---------|----------|---------|
| **VERIFIED** | Strong evidence confirms the claim | News sources OR Gemini's authoritative knowledge | "Paris is the capital of France" |
| **DISPUTED** | Evidence contradicts the claim | News sources showing contradictory info | "The Earth is flat" |
| **UNCERTAIN** | No clear evidence either way | Missing sources, mixed evidence, or errors | "A new theory was proposed yesterday" |

---

## Why All Your Claims Were UNCERTAIN

**Before Fix:**
```
All 5 claims → Gemini called → ERROR: missing backboard_api_key
            → Exception caught → Returned UNCERTAIN
            
Result: All 5 claims = UNCERTAIN ❌
```

**After Fix:**
```
All 5 claims → Gemini called → Successfully classifies using evidence
            → Returns verified/disputed/uncertain based on actual analysis
            
Result: Mix of statuses based on real verification ✅
```

---

## The Gemini Classification Prompt

Gemini uses this exact prompt for each claim:

```
You are a fact-checking expert. Classify the following claim as 
VERIFIED, DISPUTED, or UNCERTAIN based on the provided evidence.

CLAIM: [The claim being verified]

EVIDENCE:
[News articles found by NewsAPI, or "No news evidence found"]

Respond with ONLY a JSON object:
{
  "status": "verified" or "disputed" or "uncertain",
  "rationale": "1-2 sentence explanation"
}

Be specific:
- VERIFIED = strong corroborating evidence found
- DISPUTED = contradictory evidence found  
- UNCERTAIN = insufficient evidence
```

---

## Examples of Each Status

### VERIFIED ✅
```
Claim: "The Great Wall of China is in China"
Evidence: Multiple news sources confirm
Rationale: "Multiple sources confirm the Great Wall is located in China"
Status: VERIFIED
```

### DISPUTED ❌
```
Claim: "The Earth is flat"
Evidence: Multiple sources about Earth's spherical shape
Rationale: "Scientific evidence and multiple sources confirm the Earth is spherical, contradicting this claim"
Status: DISPUTED
```

### UNCERTAIN ❓
```
Claim: "A new quantum breakthrough was announced yesterday"
Evidence: No news sources found (too recent/specific)
Rationale: "Insufficient evidence available"
Status: UNCERTAIN
```

---

## How to Get Better Results

| Problem | Solution |
|---------|----------|
| All claims UNCERTAIN | ✅ **FIXED** - Added backboard_api_key to Settings |
| Still UNCERTAIN after fix | Set GEMINI_API_KEY in .env or environment |
| Still UNCERTAIN with key set | Set NEWS_API_KEY to find actual news sources |
| Mostly UNCERTAIN | Use more specific, factual claims (not opinions) |

---

## Summary

**"UNCERTAIN" means:** The system couldn't confidently verify the claim either way - likely because:
1. No news evidence was found
2. Evidence is contradictory 
3. A technical error occurred (now fixed)
4. The claim is too subjective to verify

**Your specific error:** "`'Settings' object has no attribute 'backboard_api_key'`"
- This is now **FIXED** by adding the attribute to Settings
- Claims should now be properly verified instead of all returning UNCERTAIN
