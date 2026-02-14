function u(){const t=document.documentElement.cloneNode(!0);return t.querySelectorAll('script, style, meta, noscript, svg, iframe, [style*="display:none"]').forEach(e=>e.remove()),t.innerText.split(`
`).map(e=>e.trim()).filter(e=>e.length>0).join(`
`).substring(0,1e4)}async function p(){const t=[],i=document.querySelectorAll("img");for(let n=0;n<Math.min(i.length,5);n++){const e=i[n];if(!(e.width<100||e.height<100))try{const o=document.createElement("canvas"),a=o.getContext("2d");if(!a)continue;const c=800,g=e.naturalHeight/e.naturalWidth,d=Math.min(e.naturalWidth,c),s=d*g;o.width=d,o.height=s;const r=new Image;r.crossOrigin="anonymous",r.onload=()=>{a.drawImage(r,0,0,d,s);const l=o.toDataURL("image/jpeg",.7);l.length<5e5&&t.push(l)},r.src=e.src}catch(o){console.debug("Could not extract image:",o)}}return t}async function h(){const t=await p();return{url:window.location.href,title:document.title,content:u(),images:t.length>0?t:void 0,timestamp:new Date().toISOString()}}chrome.runtime.onMessage.addListener((t,i,n)=>{if(t.type==="REQUEST_PAGE_CONTENT")return console.debug("[Content Script] Received page content request"),h().then(e=>{console.debug("[Content Script] Sending page content:",{url:e.url,contentLength:e.content.length,imageCount:e.images?.length??0}),n(e)}).catch(e=>{console.error("[Content Script] Error extracting content:",e),n({error:"Failed to extract page content",details:e.message})}),!0;t.type==="SHOW_ANALYSIS_BADGE"&&m(t.payload),t.type==="HIGHLIGHT_FINDINGS"&&x(t.payload)});function m(t){if(console.debug("[Content Script] Showing analysis badge"),document.getElementById("trust-issues-badge"))return;const i=document.createElement("div");i.id="trust-issues-badge";const n=Math.round(t.credibilityScore),e=n>70?"#4ade80":n>40?"#facc15":"#ef4444",o=Math.round(t.manipulationRisk);i.style.cssText=`
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #0d0d0d;
    border: 2px solid ${e};
    border-radius: 8px;
    padding: 12px 16px;
    color: #fff;
    font-size: 12px;
    font-family: system-ui, -apple-system, sans-serif;
    z-index: 999999;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    cursor: pointer;
    font-weight: 500;
  `,i.innerHTML=`
    <div style="display: flex; flex-direction: column; gap: 8px;">
      <div style="display: flex; align-items: center; gap: 8px;">
        <div style="
          width: 12px;
          height: 12px;
          background: ${e};
          border-radius: 50%;
        "></div>
        <span style="font-weight: bold;">Credibility: ${n}%</span>
      </div>
      <div style="font-size: 11px; opacity: 0.8;">
        Risk: ${o}% | AI: ${Math.round(t.aiGenerationLikelihood)}%
      </div>
    </div>
  `,document.body.appendChild(i),i.addEventListener("click",()=>{console.debug("[Content Script] Badge clicked, opening popup"),chrome.runtime.sendMessage({type:"OPEN_POPUP"}).catch(()=>{})}),setTimeout(()=>{i.remove()},1e4)}function x(t){console.debug("[Content Script] Highlighting findings:",t.length);const i=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT,null,!1),n=[];let e;for(;e=i.nextNode();){let o=!1,a=document.createDocumentFragment(),c=0;t.forEach(g=>{const d=e.textContent.toLowerCase(),s=g.toLowerCase();let r=d.indexOf(s);for(;r!==-1;){o=!0,r>c&&a.appendChild(document.createTextNode(e.textContent.substring(c,r)));const l=document.createElement("mark");l.style.cssText=`
          background-color: #fef08a;
          text-decoration: underline wavy #ef4444;
          cursor: pointer;
          padding: 2px 4px;
          border-radius: 2px;
        `,l.textContent=e.textContent.substring(r,r+s.length),a.appendChild(l),c=r+s.length,r=d.indexOf(s,c)}}),o&&(c<e.textContent.length&&a.appendChild(document.createTextNode(e.textContent.substring(c))),n.push([e,a]))}n.forEach(([o,a])=>{o.parentNode?.replaceChild(a,o)})}console.log("[Content Script] Trust Issues content script loaded");
