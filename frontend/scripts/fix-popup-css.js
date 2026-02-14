const fs = require('fs')
const path = require('path')

const publicDir = path.resolve(__dirname, '..', 'public')
const assetsDir = path.join(publicDir, 'assets')
const popupHtmlPath = path.join(publicDir, 'popup.html')

function findPopupCss() {
  if (!fs.existsSync(assetsDir)) return null
  const files = fs.readdirSync(assetsDir)
  // Prefer files that include 'popup' in the name, else the first .css
  const popupCss = files.find(f => f.endsWith('.css') && f.includes('popup'))
  if (popupCss) return path.posix.join('assets', popupCss)
  const anyCss = files.find(f => f.endsWith('.css'))
  return anyCss ? path.posix.join('assets', anyCss) : null
}

function injectCssIntoPopup(cssHref) {
  if (!fs.existsSync(popupHtmlPath)) {
    console.error('popup.html not found at', popupHtmlPath)
    process.exit(1)
  }

  let html = fs.readFileSync(popupHtmlPath, 'utf8')
  // Remove existing generated link if present
  html = html.replace(/<!-- GENERATED_CSS_LINK_START -->[\s\S]*?<!-- GENERATED_CSS_LINK_END -->/g, '')

  const linkTag = `<!-- GENERATED_CSS_LINK_START --><link rel="stylesheet" href="${cssHref}"><!-- GENERATED_CSS_LINK_END -->\n`

  // Insert link before closing </head>
  if (html.includes('</head>')) {
    html = html.replace('</head>', linkTag + '</head>')
  } else {
    // fallback: prepend to file
    html = linkTag + html
  }

  fs.writeFileSync(popupHtmlPath, html, 'utf8')
  console.log('Injected CSS into popup.html ->', cssHref)
}

const cssHref = findPopupCss()
if (!cssHref) {
  console.warn('No CSS file found in public/assets; popup may be unstyled')
  process.exit(0)
}

injectCssIntoPopup(cssHref)
