# Claim Verification Issue - ROOT CAUSE & FIX

## 🔴 The Problem You Were Seeing

**Symptom:** All 5 claims show as UNCERTAIN with message:
```
"Could not retrieve verification sources due to technical error. Manual verification recommended."
```

## 🔍 Root Cause

The `_verify_single_claim_ai()` function in `backend/app/pipeline/verifier.py` had **broken implementation**:

### ❌ BEFORE (Broken Code)
```python
def _verify_single_claim_ai(claim: str) -> Dict:
    """Use the AI model to verify a claim"""
    # ... code to get sources ...
    
    prompt = f"""You are a world-class fact-checking AI. ..."""
    
    # PROBLEM: Returns hardcoded result without calling Gemini!
    return {
        "claim": claim,
        "status": "uncertain",  # ← ALWAYS returned this
        "rationale": "Could not retrieve verification sources due to technical error.",
        "sources": sources[:3] if sources else []
    }
```

**What was happening:**
- ✗ NewsAPI sources were retrieved (or not)
- ✗ Evidence was formatted for Gemini
- ✗ Gemini was **NEVER CALLED** - function returned hardcoded "uncertain" instead
- ✗ No actual verification happened

---

## ✅ The Fix

### Fixed Implementation

**Step 1:** Rewrote `_verify_single_claim_ai()` to actually call Gemini:

```python
def _verify_single_claim_ai(claim: str) -> Dict:
    try:
        # Step 1: Get news evidence
        sources = search_news_with_fallback(claim)
        
        # Step 2: Format evidence for Gemini
        source_text = "Retrieved evidence:\n..." if sources else "No sources found..."
        
        # Step 3: USE GEMINI TO CLASSIFY ← THIS WAS MISSING!
        result = _classify_claim_with_gemini(claim, source_text, sources)
        return result
        
    except Exception as e:
        logger.error(f"Error verifying claim: {str(e)}")
        return {"claim": claim, "status": "uncertain", ...}
```

**Step 2:** Implemented proper `_classify_claim_with_gemini()`:

```python
def _classify_claim_with_gemini(claim: str, source_text: str, sources: List[Dict]) -> Dict:
    prompt = f"""Classify claim as VERIFIED, DISPUTED, or UNCERTAIN..."""
    
    try:
        client = get_ai_client()  # Get Gemini (or Backboard if configured)
        response_text = client.generate_text(prompt, temperature=0.2, max_tokens=256)
        
        parsed = _parse_classification_json(response_text)  # Extract JSON response
        
        return {
            "claim": claim,
            "status": parsed.get("status"),  # Actual classification from Gemini!
            "rationale": parsed.get("rationale"),  # Actual reasoning!
            "sources": sources[:3]
        }
    except Exception as e:
        logger.error(f"Gemini failed: {str(e)}")
        return fallback result
```

**Result:**
- ✓ Gemini is now actually called for each claim
- ✓ Claims will be classified as VERIFIED, DISPUTED, or UNCERTAIN based on evidence
- ✓ Rationale will contain actual reasoning from Gemini
- ✓ Sources will be included in results

---

## 🔧 Why This Matters

### Before Fix
```
Claim: "Iran signals flexibility on nuclear issues"
Result: UNCERTAIN  ← Hardcoded, no reasoning
Sources: Retrieved but ignored
Gemini calls: ✗ ZERO
```

### After Fix
```
Claim: "Iran signals flexibility on nuclear issues"
Result: VERIFIED/DISPUTED/UNCERTAIN  ← Based on actual evidence
Rationale: "Multiple Iranian diplomats confirmed..."  ← From Gemini
Sources: Displayed with headline and snippet
Gemini calls: ✓ ONE PER CLAIM (5 claims = 5 Gemini API calls)
```

---

## 📋 How It Works Now

### Verification Flow

1. **Extract Claims** (in analyze_content)
   ```
   Content → Gemini → 5 claims
   ```

2. **Verify Each Claim** (for each of 5 claims)
   ```
   Claim → NewsAPI → Find sources
        → Gemini → Classify (verified/disputed/uncertain)
        → Return result with sources
   ```

3. **Display Results** (Case Report)
   - Shows breakdown: X verified, Y disputed, Z uncertain
   - Shows each claim with rationale
   - Shows confidence based on classification

---

## 🧪 API Requirements to See Results

The fix now requires:
- ✓ **GEMINI_API_KEY** OR **BACKBOARD_API_KEY** - For claim classification
- ✓ **NEWS_API_KEY** - Optional (but recommended) for source retrieval

### Error Scenarios

| Scenario | What Happens |
|----------|--------------|
| No API keys | Returns "uncertain" with error details |
| No NEWS_API_KEY | Uses Gemini's knowledge only (no news sources) |
| NEWS_API_KEY set | Retrieves actual news sources for verification |
| All keys set | Full verification with news evidence |

---

## 📝 Summary of Changes

### Files Modified
- **backend/app/pipeline/verifier.py**
  - Rewrote `_verify_single_claim_ai()` to call Gemini
  - Fixed `_classify_claim_with_gemini()` function definition
  - Removed duplicate/broken code

### Result
- ✓ Gemini API now actually called for claim verification
- ✓ Claims can be verified, disputed, or uncertain (was always uncertain)
- ✓ Proper error handling and logging
- ✓ Full integration with NewsAPI for evidence retrieval

---

## ✨ What Users Will See Now

Before (Broken):
```
✗ All 5 claims UNCERTAIN
✗ All show "technical error" message
✗ No actual verification happening
```

After (Fixed):
```
✓ Claims properly classified (e.g., 2 verified, 1 disputed, 2 uncertain)
✓ Each shows reasoning from Gemini
✓ Sources displayed with relevant snippets
✓ Case Report shows accurate breakdown
```

---

## Testing the Fix

To verify the fix is working:

```bash
# Test 1: Check verifier syntax
python -m py_compile app/pipeline/verifier.py

# Test 2: Run diagnostic
python backend/test_diagnosis.py

# Test 3: Test full analysis
python backend/test_case_report.py  # Requires API keys
```

**Note:** Full verification requires GEMINI_API_KEY and NEWS_API_KEY to be set in .env
