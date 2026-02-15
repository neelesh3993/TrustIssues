"use client"

import { useEffect, useState } from "react"
import { Search } from "lucide-react"

const MESSAGES = [
  "Scanning page...",
  "Checking sources...",
  "Analyzing authenticity...",
  "Compiling report...",
]

export function LoadingState() {
  const [messageIndex, setMessageIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % MESSAGES.length)
    }, 1800)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex flex-col items-center gap-4 py-6">
      <div className="relative">
        <Search className="h-6 w-6 animate-pulse text-foreground" />
        <div className="absolute -inset-2 animate-ping rounded-full border border-foreground/10" />
      </div>
      <p className="animate-pulse text-xs uppercase tracking-[0.2em] text-muted-foreground">
        {MESSAGES[messageIndex]}
      </p>
      <div className="flex gap-1">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-0.5 w-6 rounded-full bg-foreground/20"
            style={{
              animation: `loading-bar 1.4s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>
    </div>
  )
}
