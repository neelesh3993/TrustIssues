"""
Claim Verifier - BATCHED VERIFICATION (Single Gemini Call)
NOW WITH: Batch processing, cheap keyword matching fallback, retry logic
FIXES: 429 rate limit issues by reducing API calls from N to 1 per scan
"""

import json
import logging
from typing import List, Dict, Optional
from app.clients.gemini_client import get_gemini_client
from app.clients.news_client import search_news_with_fallback
from app.core.settings import get_settings

logger = logging.getLogger(__name__)


HIGH_TIER_SOURCES = {
    "reuters", "ap news", "associated press", "bbc", 
    "new york times", "nyt", "the guardian", "npr", "nature", "science"
}

MEDIUM_TIER_SOURCES = {
    "cnn", "fox news", "washington post", "wall street journal", 
    "wsj", "politico", "the hill", "axios", "time", "usa today"
}


def verify_claims(claims: List[str], content_context: str = "", page_url: str = "") -> List[Dict]:
    """
    Verify ALL claims in a SINGLE batched Gemini call.
    MUCH more efficient - prevents 429 rate limits.
    
    Strategy:
    1. Gather sources for all claims (cheap NewsAPI calls)
    2. Do cheap keyword matching for obvious cases
    3. Use ONE Gemini call to reason over all claims at once
    
    Args:
        claims: List of claims to verify
        content_context: Full page content
        page_url: URL of the page
    
    Returns:
        List of verification results for all claims
    """
    if not claims:
        logger.info("No claims to verify")
        return []
    
    settings = get_settings()
    claims_to_verify = claims[: settings.max_claims]
    
    logger.info(f"\n{'='*80}")
    logger.info(f"BATCHED VERIFICATION - Processing {len(claims_to_verify)} claims")
    logger.info(f"Page: {page_url}")
    logger.info(f"{'='*80}\n")
    
    # Step 1: Gather sources for all claims (parallelizable, no Gemini yet)
    claims_with_sources = []
    total_sources = 0
    
    for i, claim in enumerate(claims_to_verify, 1):
        logger.info(f"[{i}/{len(claims_to_verify)}] Gathering sources for: {claim[:60]}...")
        
        sources = _gather_sources_for_claim(claim, content_context, page_url)
        sources = _add_credibility_ratings(sources)
        
        logger.info(f"  → Found {len(sources)} sources")
        total_sources += len(sources)
        
        claims_with_sources.append({
            "claim": claim,
            "sources": sources
        })
    
    logger.info(f"\n✓ Source gathering complete: {total_sources} total sources\n")
    
    # Step 2: Try cheap keyword matching first (no Gemini needed)
    verification_results = []
    needs_gemini = []
    
    for item in claims_with_sources:
        cheap_result = _cheap_keyword_verification(item["claim"], item["sources"])
        
        if cheap_result["confidence"] == "high":
            # We're confident without Gemini!
            logger.info(f"✓ Cheap match: '{item['claim'][:50]}...' → {cheap_result['status']}")
            
            client = get_gemini_client()
            verification_results.append({
                "claim": item["claim"],
                "status": cheap_result["status"],
                "rationale": cheap_result["rationale"],
                "ai_model_used": client.model_name,
                "sources": item["sources"][:3]
            })
        else:
            # Need Gemini reasoning
            needs_gemini.append(item)
    
    # Step 3: If we have claims that need Gemini, batch them into ONE call
    if needs_gemini:
        logger.info(f"\n⚡ Batching {len(needs_gemini)} claims for Gemini reasoning...")
        
        gemini_results = _batch_verify_with_gemini(needs_gemini, content_context)
        verification_results.extend(gemini_results)
    
    # Summary
    verified = sum(1 for r in verification_results if r['status'] == 'verified')
    disputed = sum(1 for r in verification_results if r['status'] == 'disputed')
    uncertain = sum(1 for r in verification_results if r['status'] == 'uncertain')
    
    logger.info(f"\n{'='*80}")
    logger.info(f"VERIFICATION COMPLETE")
    logger.info(f"{'='*80}")
    logger.info(f"Verified: {verified}, Disputed: {disputed}, Uncertain: {uncertain}")
    logger.info(f"Total sources: {total_sources}")
    logger.info(f"Gemini calls: {'1' if needs_gemini else '0'} (batched)")
    logger.info(f"{'='*80}\n")
    
    return verification_results


def _gather_sources_for_claim(claim: str, content: str, page_url: str) -> List[Dict]:
    """
    Gather sources for a claim WITHOUT using Gemini yet.
    Just collect evidence - reasoning comes later in batch.
    """
    # Extract context
    surrounding_context = _extract_context_for_claim(claim, content)
    
    # Build search queries
    search_queries = _build_search_queries(claim, surrounding_context, page_url)
    
    # Try each query
    sources = []
    for query in search_queries[:3]:  # Limit to 3 queries per claim to avoid hitting rate limits
        sources = search_news_with_fallback(query)
        if sources:
            logger.debug(f"  Query '{query[:40]}...' → {len(sources)} sources")
            break
    
    # Fallback to content-based source
    if not sources and content:
        page_name = "Wikipedia Article" if "wikipedia" in page_url.lower() else "Page Content"
        sources = [{
            "name": page_name,
            "headline": "Content-based verification available",
            "url": page_url if page_url else None,
            "snippet": surrounding_context[:200] if surrounding_context else content[:200],
            "publishedAt": "",
            "credibility_rating": "medium"
        }]
    
    return sources


def _cheap_keyword_verification(claim: str, sources: List[Dict]) -> Dict:
    """
    Try to verify using cheap keyword matching - no Gemini needed!
    
    Returns:
        {
            "status": "verified" | "disputed" | "uncertain",
            "rationale": str,
            "confidence": "high" | "low"  # high = don't need Gemini
        }
    """
    if not sources:
        return {
            "status": "uncertain",
            "rationale": "No sources available for verification",
            "confidence": "high"
        }
    
    # Extract claim keywords (words longer than 3 chars)
    claim_words = set(w.lower() for w in claim.split() if len(w) > 3)
    
    if not claim_words:
        return {
            "status": "uncertain",
            "rationale": "Claim too vague for verification",
            "confidence": "low"
        }
    
    # Check each source
    supporting = 0
    contradicting = 0
    
    for source in sources:
        text = (source.get("headline", "") + " " + source.get("snippet", "")).lower()
        
        # Count keyword matches
        matches = sum(1 for word in claim_words if word in text)
        match_ratio = matches / len(claim_words)
        
        # Negative indicators
        negations = ["not", "no", "denies", "false", "disputed", "incorrect", "wrong"]
        has_negation = any(neg in text for neg in negations)
        
        if match_ratio >= 0.5:  # More than half the keywords match
            if has_negation:
                contradicting += 1
            else:
                supporting += 1
    
    # Make decision
    if supporting >= 2 and contradicting == 0:
        return {
            "status": "verified",
            "rationale": f"Claim supported by {supporting} source(s) with matching key terms",
            "confidence": "high"
        }
    
    elif contradicting >= 2:
        return {
            "status": "disputed",
            "rationale": f"Claim contradicted by {contradicting} source(s)",
            "confidence": "high"
        }
    
    else:
        # Not confident enough - need Gemini
        return {
            "status": "uncertain",
            "rationale": "Ambiguous evidence",
            "confidence": "low"
        }


def _batch_verify_with_gemini(claims_with_sources: List[Dict], content_context: str) -> List[Dict]:
    """
    Verify ALL claims in a SINGLE Gemini API call.
    This is the key optimization - went from N calls to 1 call.
    
    Args:
        claims_with_sources: List of {claim, sources} dicts
        content_context: Full page content for fallback
    
    Returns:
        List of verification results
    """
    # Build the batch prompt
    prompt_parts = ["You are a fact-checking expert. Verify these claims based on provided sources.\n\n"]
    
    for i, item in enumerate(claims_with_sources, 1):
        prompt_parts.append(f"CLAIM {i}: {item['claim']}\n")
        prompt_parts.append(f"SOURCES FOR CLAIM {i}:\n")
        
        if item['sources']:
            for j, source in enumerate(item['sources'][:3], 1):  # Top 3 sources
                prompt_parts.append(
                    f"  {j}. [{source.get('name')}] {source.get('headline')}\n"
                    f"     {source.get('snippet', '')[:150]}\n"
                )
        else:
            prompt_parts.append("  (No external sources available)\n")
        
        prompt_parts.append("\n")
    
    prompt_parts.append(
        f"\nRespond with ONLY a JSON array (no markdown, no explanation):\n"
        f"[\n"
        f'  {{"claim": "claim text", "status": "verified|disputed|uncertain", "rationale": "1-2 sentences"}},\n'
        f"  ...\n"
        f"]\n\n"
        f"IMPORTANT:\n"
        f"- Base your assessment ONLY on the provided sources\n"
        f"- Do NOT hallucinate sources\n"
        f"- Keep rationales concise (1-2 sentences)\n"
    )
    
    prompt = "".join(prompt_parts)
    
    logger.debug(f"Batch prompt length: {len(prompt)} chars")
    
    try:
        client = get_gemini_client()
        
        # Single Gemini call for ALL claims!
        logger.info("🚀 Making SINGLE batched Gemini call...")
        response_text = client.generate_text(
            prompt,
            temperature=0.2,
            max_tokens=2048,  # Need more tokens for multiple claims
            max_retries=3  # Will auto-retry on 429
        )
        logger.info("✓ Gemini response received")
        
        # Parse JSON array response
        results_json = _parse_batch_json(response_text)
        
        if not isinstance(results_json, list):
            raise ValueError("Expected JSON array from Gemini")
        
        # Match results back to original claims
        verification_results = []
        
        for i, item in enumerate(claims_with_sources):
            if i < len(results_json):
                result_data = results_json[i]
                
                status = result_data.get("status", "uncertain").lower()
                if status not in ["verified", "disputed", "uncertain"]:
                    status = "uncertain"
                
                verification_results.append({
                    "claim": item["claim"],
                    "status": status,
                    "rationale": result_data.get("rationale", "No rationale provided"),
                    "ai_model_used": client.model_name,
                    "sources": item["sources"][:3]
                })
            else:
                # Fallback if Gemini didn't return enough results
                logger.warning(f"Missing result for claim {i+1}, using uncertain")
                verification_results.append({
                    "claim": item["claim"],
                    "status": "uncertain",
                    "rationale": "Verification incomplete",
                    "ai_model_used": client.model_name,
                    "sources": item["sources"][:3]
                })
        
        return verification_results
    
    except Exception as e:
        logger.error(f"Batch Gemini verification failed: {str(e)}")
        
        # Fallback: return all as uncertain
        client = get_gemini_client()
        return [{
            "claim": item["claim"],
            "status": "uncertain",
            "rationale": f"Verification failed due to technical error: {str(e)[:100]}",
            "ai_model_used": client.model_name,
            "sources": item["sources"][:3]
        } for item in claims_with_sources]


def _parse_batch_json(response_text: str) -> List[Dict]:
    """Parse JSON array from Gemini batch response."""
    try:
        # Remove markdown fences
        text = response_text.strip()
        if text.startswith("```"):
            parts = text.split("```")
            if len(parts) >= 2:
                text = parts[1]
                if text.startswith("json"):
                    text = text[4:]
        text = text.strip()
        
        parsed = json.loads(text)
        
        if not isinstance(parsed, list):
            raise ValueError("Expected array")
        
        return parsed
    
    except Exception as e:
        logger.error(f"Failed to parse batch JSON: {str(e)}")
        logger.debug(f"Response: {response_text[:500]}")
        raise


def _add_credibility_ratings(sources: List[Dict]) -> List[Dict]:
    """Add credibility ratings to sources."""
    rated_sources = []
    
    for source in sources:
        source_copy = source.copy()
        source_name = source.get("name", "").lower()
        
        if any(tier in source_name for tier in HIGH_TIER_SOURCES):
            source_copy["credibility_rating"] = "high"
        elif any(tier in source_name for tier in MEDIUM_TIER_SOURCES):
            source_copy["credibility_rating"] = "medium"
        else:
            source_copy["credibility_rating"] = "low"
        
        rated_sources.append(source_copy)
    
    return rated_sources


def _extract_context_for_claim(claim: str, content: str) -> str:
    """Extract relevant context from page content."""
    if not content or len(content) < 100:
        return ""
    
    sentences = [s.strip() for s in content.replace('\n', ' ').split('.') if s.strip() and len(s.strip()) > 20]
    
    if not sentences:
        return content[:500]
    
    claim_words = set(w.lower() for w in claim.split() if len(w) > 3)
    
    if not claim_words:
        return " ".join(sentences[:3])[:500]
    
    # Find best matching sentence
    best_idx = -1
    best_score = 0
    
    for i, sentence in enumerate(sentences):
        sentence_words = set(w.lower() for w in sentence.split())
        overlap = len(claim_words & sentence_words)
        if overlap > best_score:
            best_score = overlap
            best_idx = i
    
    if best_idx >= 0:
        start = max(0, best_idx - 1)
        end = min(len(sentences), best_idx + 2)
        return " ".join(sentences[start:end])[:500]
    else:
        return " ".join(sentences[:3])[:500]


def _build_search_queries(claim: str, context: str, page_url: str) -> List[str]:
    """Build search queries for NewsAPI."""
    queries = []
    
    url_keywords = _extract_keywords_from_url(page_url)
    
    if len(claim.split()) >= 5:
        queries.append(claim)
    
    if url_keywords:
        queries.append(f"{claim} {url_keywords}")
    
    words = claim.split()
    important_words = [w for w in words if len(w) > 4 and w.lower() not in {'this', 'that', 'these', 'those', 'were', 'have', 'been'}]
    
    if len(important_words) >= 2:
        queries.append(" ".join(important_words[:4]))
    
    capitalized = [w for w in words if w and w[0].isupper()]
    if len(capitalized) >= 2:
        queries.append(" ".join(capitalized[:3]))
    
    if len(important_words) >= 1:
        queries.append(" ".join(important_words[:2]))
    
    # Remove duplicates
    seen = set()
    unique = []
    for q in queries:
        q_clean = q.strip()
        if q_clean.lower() not in seen and len(q_clean) > 5:
            seen.add(q_clean.lower())
            unique.append(q_clean)
    
    return unique if unique else [claim]


def _extract_keywords_from_url(url: str) -> str:
    """Extract topic keywords from URL."""
    if not url:
        return ""
    
    try:
        if 'wikipedia.org' in url:
            parts = url.split('/wiki/')
            if len(parts) > 1:
                title = parts[1].split('?')[0].split('#')[0]
                return title.replace('_', ' ')[:50]
        
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p and not p.isdigit()]
        if path_parts:
            return path_parts[-1].replace('-', ' ').replace('_', ' ')[:50]
    
    except Exception:
        pass
    
    return ""
