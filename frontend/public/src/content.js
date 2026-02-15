function u(){const e=window.location.href,r=window.location.hostname,t=["doubleclick.net","googleadservices.com","pagead","ads.","adserver","adservice","analytics","tracking","facebook.com/tr","twitter.com/i/","pubmatic","openx","criteo","appnexus","amazon-adsystem","scorecardresearch","quantserve","chartbeat","outbrain","taboola","sharethis","addthis","js/showad","pixeltrack","beacon","dpm.demdex","recaptcha","challenges.cloudflare","challenge.cloudflare","captcha","turnstile","facebook.com/plugins","instagram.com/embed","twitter.com/embed","youtube.com/embed","youtube-nocookie.com"];for(const n of t)if(e.toLowerCase().includes(n)||r.toLowerCase().includes(n))return console.debug(`[Content Script] 🚫 Detected ad/iframe frame: ${r} (matched: ${n})`),!0;return document.body.innerText.length<10&&e!==window.top?.location.href?(console.debug("[Content Script] 🚫 Detected empty iframe (likely ad)"),!0):!1}function p(){try{return window.self===window.top}catch{return!1}}function m(){console.debug("[Content Script] Starting text extraction...");let e="";console.debug("[Content Script] Attempting article-specific extraction...");const r=["article",'[role="main"]',"main",".article-content",".post-content",".entry-content",".content",".page-content",'[class*="article"]','[class*="content"]'];for(const t of r){const n=document.querySelector(t);if(n){const i=n.innerText?.split(`
`).map(o=>o.trim()).filter(o=>o.length>0).join(`
`)||"";i.length>e.length&&(e=i,console.debug(`[Content Script] Found content via selector "${t}": ${e.length} chars`))}}if(e.length<100){console.debug("[Content Script] Article selector failed, trying clone method...");const t=document.documentElement.cloneNode(!0);t.querySelectorAll('script, style, meta, noscript, svg, iframe, [style*="display:none"], nav, header, footer, .ad, .advertisement').forEach(o=>o.remove());const i=t.innerText?.split(`
`).map(o=>o.trim()).filter(o=>o.length>0).join(`
`)||"";console.debug(`[Content Script] Clone method: ${i.length} chars`),i.length>e.length&&(e=i)}if(e.length<100){console.debug("[Content Script] Still <100 chars, trying body.innerText...");const t=document.body.innerText?.split(`
`).map(n=>n.trim()).filter(n=>n.length>0).join(`
`)||"";console.debug(`[Content Script] Body method: ${t.length} chars`),t.length>e.length&&(e=t)}if(e.length<100){console.debug("[Content Script] Still <100 chars, trying textContent...");const t=document.body.textContent?.split(`
`).map(n=>n.trim()).filter(n=>n.length>0).join(`
`)||"";console.debug(`[Content Script] TextContent method: ${t.length} chars`),t.length>e.length&&(e=t)}return console.debug(`[Content Script] Final extracted text: ${e.length} chars`),e.length<200&&(console.warn(`[Content Script] ⚠️  WARNING: Only ${e.length} chars extracted!`),console.debug(`[Content Script] First 100 chars: "${e.substring(0,100)}"`),console.debug(`[Content Script] Page title: "${document.title}"`),console.debug(`[Content Script] Page URL: "${window.location.href}"`)),e.substring(0,1e4)}async function f(){const e=[],r=document.querySelectorAll("img");for(let t=0;t<Math.min(r.length,5);t++){const n=r[t];if(!(n.width<100||n.height<100))try{const i=document.createElement("canvas"),o=i.getContext("2d");if(!o)continue;const l=800,s=n.naturalHeight/n.naturalWidth,d=Math.min(n.naturalWidth,l),g=d*s;i.width=d,i.height=g;const c=new Image;c.crossOrigin="anonymous",c.onload=()=>{o.drawImage(c,0,0,d,g);const a=i.toDataURL("image/jpeg",.7);a.length<5e5&&e.push(a)},c.src=n.src}catch(i){console.debug("Could not extract image:",i)}}return e}async function x(){const e=await f();return{url:window.location.href,title:document.title,content:m(),images:e.length>0?e:void 0,timestamp:new Date().toISOString()}}chrome.runtime.onMessage.addListener((e,r,t)=>{if(e.type==="REQUEST_PAGE_CONTENT"){const n=window.location.href,i=p();return console.debug(`[Content Script] Received page content request from frameId ${r.frameId} (main: ${i}, url: ${n})`),u()?(console.debug("[Content Script] 🚫 Ignoring request - running in ad frame, not responding"),!1):(i||(console.debug("[Content Script] ⚠️  Running in iframe (not main frame): "+n),console.debug("[Content Script] Still responding because it passed ad frame check")),x().then(o=>{console.debug("[Content Script] Sending page content:",{url:o.url,contentLength:o.content.length,imageCount:o.images?.length??0}),t(o)}).catch(o=>{console.error("[Content Script] Error extracting content:",o),t({error:"Failed to extract page content",details:o.message})}),!0)}if(e.type==="SHOW_ANALYSIS_BADGE"&&C(e.payload),e.type==="HIGHLIGHT_FINDINGS")return console.log("[Content Script] Received HIGHLIGHT_FINDINGS message:",e.payload),S(e.payload),t({success:!0}),!0;if(e.type==="HIGHLIGHT_CLAIMS")return console.log("[Content Script] Received HIGHLIGHT_CLAIMS message:",e.payload),y(e.payload),t({success:!0}),!0;if(e.type==="CLEAR_HIGHLIGHTS")return console.log("[Content Script] Received CLEAR_HIGHLIGHTS message"),b(),t({success:!0}),!0});function C(e){if(console.debug("[Content Script] Showing analysis badge"),document.getElementById("trust-issues-badge"))return;const r=document.createElement("div");r.id="trust-issues-badge";const t=Math.round(e.credibilityScore),n=t>70?"#4ade80":t>40?"#facc15":"#ef4444",i=Math.round(e.manipulationRisk);r.style.cssText=`
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #0d0d0d;
    border: 2px solid ${n};
    border-radius: 8px;
    padding: 12px 16px;
    color: #fff;
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
    z-index: 999999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    cursor: pointer;
    font-weight: 500;
  `,r.innerHTML=`
    <div style="display: flex; flex-direction: column; gap: 8px;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <div style="
          width: 12px;
          height: 12px;
          background: ${n};
          border-radius: 50%;
        "></div>
        <span style="font-weight: bold;">Credibility: ${t}%</span>
      </div>
      <div style="font-size: 11px; opacity: 0.8;">
        Risk: ${i}% | AI: ${Math.round(e.aiGenerationLikelihood)}%
      </div>
    </div>
  `,document.body.appendChild(r),r.addEventListener("click",()=>{console.debug("[Content Script] Badge clicked, opening popup"),chrome.runtime.sendMessage({type:"OPEN_POPUP"}).catch(()=>{})}),setTimeout(()=>{r.remove()},1e4)}function b(){console.debug("[Content Script] Clearing all highlights"),document.querySelectorAll("mark[data-trust-highlight]").forEach(r=>{const t=r.parentNode;if(t){for(;r.firstChild;)t.insertBefore(r.firstChild,r);t.removeChild(r)}})}function y(e){if(console.debug("[Content Script] Highlighting claims:",e.length),console.debug("[Content Script] Claims to highlight:",e),!e||e.length===0){console.warn("[Content Script] No claims provided");return}const r=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null,!1),t=[];let n=0,i;for(;i=r.nextNode();){let o=!1,l=document.createDocumentFragment(),s=0;e.forEach(d=>{if(!d||d.length<5)return;const g=i.textContent.toLowerCase(),c=d.toLowerCase();let a=g.indexOf(c);for(;a!==-1;){o=!0,n++,a>s&&l.appendChild(document.createTextNode(i.textContent.substring(s,a)));const h=document.createElement("mark");h.setAttribute("data-trust-highlight","claim"),h.style.cssText=`
          background-color: #3b82f6;
          color: white;
          text-decoration: none;
          cursor: pointer;
          padding: 2px 4px;
          border-radius: 2px;
          font-weight: 500;
        `,h.textContent=i.textContent.substring(a,a+c.length),l.appendChild(h),s=a+c.length,a=g.indexOf(c,s)}}),o&&(s<i.textContent.length&&l.appendChild(document.createTextNode(i.textContent.substring(s))),t.push([i,l]))}t.forEach(([o,l])=>{o.parentNode?.replaceChild(l,o)}),console.debug("[Content Script] Highlighted claims complete. Total matches:",n)}function S(e){console.debug("[Content Script] Highlighting findings:",e.length);const r=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null,!1),t=[];let n;for(;n=r.nextNode();){let i=!1,o=document.createDocumentFragment(),l=0;e.forEach(s=>{if(!s||s.length<5)return;const d=n.textContent.toLowerCase(),g=s.toLowerCase();let c=d.indexOf(g);for(;c!==-1;){i=!0,c>l&&o.appendChild(document.createTextNode(n.textContent.substring(l,c)));const a=document.createElement("mark");a.setAttribute("data-trust-highlight","finding"),a.style.cssText=`
          background-color: #fef08a;
          text-decoration: underline wavy #ef4444;
          cursor: pointer;
          padding: 2px 4px;
          border-radius: 2px;
        `,a.textContent=n.textContent.substring(c,c+g.length),o.appendChild(a),l=c+g.length,c=d.indexOf(g,l)}}),i&&(l<n.textContent.length&&o.appendChild(document.createTextNode(n.textContent.substring(l))),t.push([n,o]))}t.forEach(([i,o])=>{i.parentNode?.replaceChild(o,i)})}console.log("[Content Script] Trust Issues content script loaded");
