/**
 * Popup entry point for browser extension
 * Renders the React app into the popup window
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { PopupApp } from '../components/popup'
import '../app/globals.css'

// Find or create root element
let root = document.getElementById('root')
if (!root) {
  root = document.createElement('div')
  root.id = 'root'
  document.body.appendChild(root)
}

// Render React app
const reactRoot = ReactDOM.createRoot(root)
reactRoot.render(
  <React.StrictMode>
    <PopupApp />
  </React.StrictMode>
)
