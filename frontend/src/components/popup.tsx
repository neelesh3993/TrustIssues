/**
 * Popup Component
 * Main extension popup entry point
 */

'use client'

import React from 'react'
import { PopupContainer } from '@/components/trust-issues/popup-container'
import { ThemeProvider } from '@/components/theme-provider'

export function PopupApp() {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      <PopupContainer />
    </ThemeProvider>
  )
}

export default PopupApp
