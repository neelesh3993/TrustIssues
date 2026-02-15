# Content Extraction Debugging Guide

## The Problem
You're getting "Page content too short" error even though article is long.

## Root Cause
The **content script** (in the webpage) isn't extracting text properly. This happens because:

1. **Page framework**: Modern SPAs (React, Vue, Angular) might not have text in `innerText`
2. **Lazy loading**: Content might load after script runs
3. **Paywalls/restricted content**: Some sites block content extraction
4. **Page structure**: Text might be in non-standard locations

---

## Step 1: Check Browser Console for Extraction Logs

### How to open console:
- **Chrome/Edge**: Press `F12` → Click "Console" tab
- **Firefox**: Press `F12` → Click "Console" tab

### Look for logs like:
```
[Content Script] Starting text extraction...
[Content Script] Attempting article-specific extraction...
[Content Script] Found content via selector "article": 2500 chars
[Content Script] Final extracted text: 2500 chars
```

### What to check:
- ✅ **Good**: `Final extracted text: 2500 chars` → Article extracted successfully
- ❌ **Bad**: `Final extracted text: 25 chars` → Extraction failed
- ⚠️ **Check page**: `WARNING: Only 45 chars extracted!` → Page might be JavaScript-heavy

---

## Step 2: Test with the Example Test Article

The easiest way to verify extraction works:

### Option A: Use the included test article
```
Open in browser: file:///path/to/test-article.html
Click extension → Scan
```

### Option B: Test on real news sites
Use sites with standard article structure:
- **BBC.com** - Article page (has `<article>` tags)
- **Wikipedia** - Has `<main>` tag with content
- **Medium.com** - Articles with clear structure
- **Dev.to** - Tech articles with structure

### Avoid for testing:
- ❌ Twitter/X (mostly JavaScript)
- ❌ Reddit (complex rendering)
- ❌ Instagram (image-based)
- ❌ Video sites like YouTube
- ❌ SPA dashboards (no text content)

---

## Step 3: What's Being Sent to Backend

In the popup error message, check how many characters were extracted:

```
Page content too short (23 chars). Need at least 50 characters.
First 100 chars: "Trust Issues Web Content Investigation Tool"
```

The 23 chars is the popup UI itself, not the article content. This means:
- **Content script didn't run** on the article page, OR
- **Extraction found nothing** on that page

---

## Step 4: Improved Extraction (Already Applied)

I've updated the content script to try 4 methods:

### Method 1: Article-Specific Selectors
```javascript
article              // <article> tag
[role="main"]        // Semantic HTML5
main                 // <main> tag  
.article-content     // Common class names
.post-content
.entry-content
.content
[class*="article"]   // Anything with "article" in class
```

### Method 2: Clone and Extract (removes ads, nav, etc.)

### Method 3: document.body.innerText (full page)

### Method 4: document.body.textContent (raw text)

Each method falls back to the next if it extracts <100 characters.

---

## Step 5: Rebuild and Test

After these changes, rebuild the extension:

```bash
# From frontend directory
npm run build:extension

# Or on Windows
npm run build:extension
```

Then reload in Chrome:
1. Go to `chrome://extensions`
2. Find "Trust Issues"
3. Click the refresh icon ↻

---

## Step 6: Common Issues & Fixes

### Issue: "Only XX chars extracted" warning
**Cause**: Page doesn't have standard article structure

**Fix**:
- Try a different news site
- Check if content is loaded after page renders (wait 2-3s before clicking scan)
- Check if behind paywall (some sites block text extraction)

### Issue: Content extraction works, but claims show "uncertain"
**This is actually correct!**
- NewsAPI doesn't find sources for your claims
- Test with well-known facts instead ("Paris is capital of France")
- Or test on actual news articles (so claims are based on real events)

### Issue: Extension button not showing
- Reload extension in `chrome://extensions`
- Check manifest permissions in browser console

---

## Step 7: Debugging Commands

Open browser console and run:

```javascript
// Check what content is extracted
document.body.innerText.substring(0, 200)

// Check for article element
document.querySelector('article')

// Check for main element
document.querySelector('main')

// Check body text length
document.body.innerText.length

// Check all text
document.body.textContent.length
```

---

## Next Steps

1. ✅ **Use test article** → Verify extraction works
2. ✅ **Check browser logs** → See extraction details
3. ✅ **Test on news sites** → Try BBC, Wikipedia, etc.
4. ✅ **Rebuild extension** → Get latest improvements
5. ❌ **If still failing** → Share browser console output with me

---

## Quick Test Command

```bash
# From backend directory
cd backend
python -m uvicorn app.main:app --reload

# From another terminal, test a simple analysis:
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "title": "Test Article",
    "content": "This is a test article with substantial content that is definitely longer than fifty characters so it should process correctly and extract claims from it about various topics and events in the world."
  }'
```

If this works, the backend is fine and the issue is in frontend extraction.
