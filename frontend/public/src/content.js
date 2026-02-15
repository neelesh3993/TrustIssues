function u(){const e=window.location.href,c=window.location.hostname,n=["doubleclick.net","googleadservices.com","pagead","ads.","adserver","adservice","analytics","tracking","facebook.com/tr","twitter.com/i/","pubmatic","openx","criteo","appnexus","amazon-adsystem","scorecardresearch","quantserve","chartbeat","outbrain","taboola","sharethis","addthis","js/showad","pixeltrack","beacon","dpm.demdex","recaptcha","challenges.cloudflare","challenge.cloudflare","captcha","turnstile","facebook.com/plugins","instagram.com/embed","twitter.com/embed","youtube.com/embed","youtube-nocookie.com"];for(const t of n)if(e.toLowerCase().includes(t)||c.toLowerCase().includes(t))return console.debug(`[Content Script] 🚫 Detected ad/iframe frame: ${c} (matched: ${t})`),!0;return document.body.innerText.length<10&&e!==window.top?.location.href?(console.debug("[Content Script] 🚫 Detected empty iframe (likely ad)"),!0):!1}function h(){try{return window.self===window.top}catch{return!1}}function m(){console.debug("[Content Script] Starting text extraction...");let e="";console.debug("[Content Script] Attempting article-specific extraction...");const c=["article",'[role="main"]',"main",".article-content",".post-content",".entry-content",".content",".page-content",'[class*="article"]','[class*="content"]'];for(const n of c){const t=document.querySelector(n);if(t){const i=t.innerText?.split(`
`).map(o=>o.trim()).filter(o=>o.length>0).join(`
`)||"";i.length>e.length&&(e=i,console.debug(`[Content Script] Found content via selector "${n}": ${e.length} chars`))}}if(e.length<100){console.debug("[Content Script] Article selector failed, trying clone method...");const n=document.documentElement.cloneNode(!0);n.querySelectorAll('script, style, meta, noscript, svg, iframe, [style*="display:none"], nav, header, footer, .ad, .advertisement').forEach(o=>o.remove());const i=n.innerText?.split(`
`).map(o=>o.trim()).filter(o=>o.length>0).join(`
`)||"";console.debug(`[Content Script] Clone method: ${i.length} chars`),i.length>e.length&&(e=i)}if(e.length<100){console.debug("[Content Script] Still <100 chars, trying body.innerText...");const n=document.body.innerText?.split(`
`).map(t=>t.trim()).filter(t=>t.length>0).join(`
`)||"";console.debug(`[Content Script] Body method: ${n.length} chars`),n.length>e.length&&(e=n)}if(e.length<100){console.debug("[Content Script] Still <100 chars, trying textContent...");const n=document.body.textContent?.split(`
`).map(t=>t.trim()).filter(t=>t.length>0).join(`
`)||"";console.debug(`[Content Script] TextContent method: ${n.length} chars`),n.length>e.length&&(e=n)}return console.debug(`[Content Script] Final extracted text: ${e.length} chars`),e.length<200&&(console.warn(`[Content Script] ⚠️  WARNING: Only ${e.length} chars extracted!`),console.debug(`[Content Script] First 100 chars: "${e.substring(0,100)}"`),console.debug(`[Content Script] Page title: "${document.title}"`),console.debug(`[Content Script] Page URL: "${window.location.href}"`)),e.substring(0,1e4)}async function p(){const e=[],c=document.querySelectorAll("img");for(let n=0;n<Math.min(c.length,5);n++){const t=c[n];if(!(t.width<100||t.height<100))try{const i=document.createElement("canvas"),o=i.getContext("2d");if(!o)continue;const a=800,g=t.naturalHeight/t.naturalWidth,l=Math.min(t.naturalWidth,a),s=l*g;i.width=l,i.height=s;const r=new Image;r.crossOrigin="anonymous",r.onload=()=>{o.drawImage(r,0,0,l,s);const d=i.toDataURL("image/jpeg",.7);d.length<5e5&&e.push(d)},r.src=t.src}catch(i){console.debug("Could not extract image:",i)}}return e}async function f(){const e=await p();return{url:window.location.href,title:document.title,content:m(),images:e.length>0?e:void 0,timestamp:new Date().toISOString()}}chrome.runtime.onMessage.addListener((e,c,n)=>{if(e.type==="REQUEST_PAGE_CONTENT"){const t=window.location.href,i=h();return console.debug(`[Content Script] Received page content request from frameId ${c.frameId} (main: ${i}, url: ${t})`),u()?(console.debug("[Content Script] 🚫 Ignoring request - running in ad frame, not responding"),!1):(i||(console.debug("[Content Script] ⚠️  Running in iframe (not main frame): "+t),console.debug("[Content Script] Still responding because it passed ad frame check")),f().then(o=>{console.debug("[Content Script] Sending page content:",{url:o.url,contentLength:o.content.length,imageCount:o.images?.length??0}),n(o)}).catch(o=>{console.error("[Content Script] Error extracting content:",o),n({error:"Failed to extract page content",details:o.message})}),!0)}e.type==="SHOW_ANALYSIS_BADGE"&&x(e.payload),e.type==="HIGHLIGHT_FINDINGS"&&b(e.payload)});function x(e){if(console.debug("[Content Script] Showing analysis badge"),document.getElementById("trust-issues-badge"))return;const c=document.createElement("div");c.id="trust-issues-badge";const n=Math.round(e.credibilityScore),t=n>70?"#4ade80":n>40?"#facc15":"#ef4444",i=Math.round(e.manipulationRisk);c.style.cssText=`
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
  `,c.innerHTML=`
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
        Risk: ${i}% | AI: ${Math.round(e.aiGenerationLikelihood)}%
      </div>
    </div>
  `,document.body.appendChild(c),c.addEventListener("click",()=>{console.debug("[Content Script] Badge clicked, opening popup"),chrome.runtime.sendMessage({type:"OPEN_POPUP"}).catch(()=>{})}),setTimeout(()=>{c.remove()},1e4)}function b(e){console.debug("[Content Script] Highlighting findings:",e.length);const c=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null,!1),n=[];let t;for(;t=c.nextNode();){let i=!1,o=document.createDocumentFragment(),a=0;e.forEach(g=>{const l=t.textContent.toLowerCase(),s=g.toLowerCase();let r=l.indexOf(s);for(;r!==-1;){i=!0,r>a&&o.appendChild(document.createTextNode(t.textContent.substring(a,r)));const d=document.createElement("mark");d.style.cssText=`
          background-color: #fef08a;
          text-decoration: underline wavy #ef4444;
          cursor: pointer;
          padding: 2px 4px;
          border-radius: 2px;
        `,d.textContent=t.textContent.substring(r,r+s.length),o.appendChild(d),a=r+s.length,r=l.indexOf(s,a)}}),i&&(a<t.textContent.length&&o.appendChild(document.createTextNode(t.textContent.substring(a))),n.push([t,o]))}n.forEach(([i,o])=>{i.parentNode?.replaceChild(o,i)})}console.log("[Content Script] Trust Issues content script loaded");
