import type { Metadata, Viewport } from 'next'
import { IBM_Plex_Mono } from 'next/font/google'

import './globals.css'

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-mono',
})

export const metadata: Metadata = {
  title: 'Trust Issues — Web Content Investigation Tool',
  description: 'Investigate the authenticity and credibility of web content.',
}

export const viewport: Viewport = {
  themeColor: '#0d0d0d',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={ibmPlexMono.variable}>
      <body className="font-mono antialiased">{children}</body>
    </html>
  )
}
