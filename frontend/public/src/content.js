function u(){const e=window.location.href,r=window.location.hostname,n=["doubleclick.net","googleadservices.com","pagead","ads.","adserver","adservice","analytics","tracking","facebook.com/tr","twitter.com/i/","pubmatic","openx","criteo","appnexus","amazon-adsystem","scorecardresearch","quantserve","chartbeat","outbrain","taboola","sharethis","addthis","js/showad","pixeltrack","beacon","dpm.demdex"];for(const t of n)if(e.toLowerCase().includes(t)||r.toLowerCase().includes(t))return console.debug(`[Content Script] 🚫 Detected ad frame: ${r}`),!0;return document.body.innerText.length<10&&e!==window.top?.location.href?(console.debug("[Content Script] 🚫 Detected empty iframe (likely ad)"),!0):!1}function h(){try{return window.self===window.top}catch{return!1}}function p(){console.debug("[Content Script] Starting text extraction...");let e="";console.debug("[Content Script] Attempting article-specific extraction...");const r=["article",'[role="main"]',"main",".article-content",".post-content",".entry-content",".content",".page-content",'[class*="article"]','[class*="content"]'];for(const n of r){const t=document.querySelector(n);if(t){const o=t.innerText?.split(`
`).map(i=>i.trim()).filter(i=>i.length>0).join(`
`)||"";o.length>e.length&&(e=o,console.debug(`[Content Script] Found content via selector "${n}": ${e.length} chars`))}}if(e.length<100){console.debug("[Content Script] Article selector failed, trying clone method...");const n=document.documentElement.cloneNode(!0);n.querySelectorAll('script, style, meta, noscript, svg, iframe, [style*="display:none"], nav, header, footer, .ad, .advertisement').forEach(i=>i.remove());const o=n.innerText?.split(`
`).map(i=>i.trim()).filter(i=>i.length>0).join(`
`)||"";console.debug(`[Content Script] Clone method: ${o.length} chars`),o.length>e.length&&(e=o)}if(e.length<100){console.debug("[Content Script] Still <100 chars, trying body.innerText...");const n=document.body.innerText?.split(`
`).map(t=>t.trim()).filter(t=>t.length>0).join(`
`)||"";console.debug(`[Content Script] Body method: ${n.length} chars`),n.length>e.length&&(e=n)}if(e.length<100){console.debug("[Content Script] Still <100 chars, trying textContent...");const n=document.body.textContent?.split(`
`).map(t=>t.trim()).filter(t=>t.length>0).join(`
`)||"";console.debug(`[Content Script] TextContent method: ${n.length} chars`),n.length>e.length&&(e=n)}return console.debug(`[Content Script] Final extracted text: ${e.length} chars`),e.length<200&&(console.warn(`[Content Script] ⚠️  WARNING: Only ${e.length} chars extracted!`),console.debug(`[Content Script] First 100 chars: "${e.substring(0,100)}"`),console.debug(`[Content Script] Page title: "${document.title}"`),console.debug(`[Content Script] Page URL: "${window.location.href}"`)),e.substring(0,1e4)}async function m(){const e=[],r=document.querySelectorAll("img");for(let n=0;n<Math.min(r.length,5);n++){const t=r[n];if(!(t.width<100||t.height<100))try{const o=document.createElement("canvas"),i=o.getContext("2d");if(!i)continue;const a=800,g=t.naturalHeight/t.naturalWidth,l=Math.min(t.naturalWidth,a),s=l*g;o.width=l,o.height=s;const c=new Image;c.crossOrigin="anonymous",c.onload=()=>{i.drawImage(c,0,0,l,s);const d=o.toDataURL("image/jpeg",.7);d.length<5e5&&e.push(d)},c.src=t.src}catch(o){console.debug("Could not extract image:",o)}}return e}async function f(){const e=await m();return{url:window.location.href,title:document.title,content:p(),images:e.length>0?e:void 0,timestamp:new Date().toISOString()}}chrome.runtime.onMessage.addListener((e,r,n)=>{if(e.type==="REQUEST_PAGE_CONTENT")return console.debug("[Content Script] Received page content request"),u()?(console.debug("[Content Script] 🚫 Ignoring request - running in ad frame"),!1):(h()||console.debug("[Content Script] ⚠️  Running in iframe (not main frame): "+window.location.href),f().then(t=>{console.debug("[Content Script] Sending page content:",{url:t.url,contentLength:t.content.length,imageCount:t.images?.length??0}),n(t)}).catch(t=>{console.error("[Content Script] Error extracting content:",t),n({error:"Failed to extract page content",details:t.message})}),!0);e.type==="SHOW_ANALYSIS_BADGE"&&x(e.payload),e.type==="HIGHLIGHT_FINDINGS"&&b(e.payload)});function x(e){if(console.debug("[Content Script] Showing analysis badge"),document.getElementById("trust-issues-badge"))return;const r=document.createElement("div");r.id="trust-issues-badge";const n=Math.round(e.credibilityScore),t=n>70?"#4ade80":n>40?"#facc15":"#ef4444",o=Math.round(e.manipulationRisk);r.style.cssText=`
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #0d0d0d;
    border: 2px solid ${t};
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
          background: ${t};
          border-radius: 50%;
        "></div>
        <span style="font-weight: bold;">Credibility: ${n}%</span>
      </div>
      <div style="font-size: 11px; opacity: 0.8;">
        Risk: ${o}% | AI: ${Math.round(e.aiGenerationLikelihood)}%
      </div>
    </div>
  `,document.body.appendChild(r),r.addEventListener("click",()=>{console.debug("[Content Script] Badge clicked, opening popup"),chrome.runtime.sendMessage({type:"OPEN_POPUP"}).catch(()=>{})}),setTimeout(()=>{r.remove()},1e4)}function b(e){console.debug("[Content Script] Highlighting findings:",e.length);const r=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null,!1),n=[];let t;for(;t=r.nextNode();){let o=!1,i=document.createDocumentFragment(),a=0;e.forEach(g=>{const l=t.textContent.toLowerCase(),s=g.toLowerCase();let c=l.indexOf(s);for(;c!==-1;){o=!0,c>a&&i.appendChild(document.createTextNode(t.textContent.substring(a,c)));const d=document.createElement("mark");d.style.cssText=`
          background-color: #fef08a;
          text-decoration: underline wavy #ef4444;
          cursor: pointer;
          padding: 2px 4px;
          border-radius: 2px;
        `,d.textContent=t.textContent.substring(c,c+s.length),i.appendChild(d),a=c+s.length,c=l.indexOf(s,a)}}),o&&(a<t.textContent.length&&i.appendChild(document.createTextNode(t.textContent.substring(a))),n.push([t,i]))}n.forEach(([o,i])=>{o.parentNode?.replaceChild(i,o)})}console.log("[Content Script] Trust Issues content script loaded");
