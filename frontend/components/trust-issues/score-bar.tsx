"use client"

import { useEffect, useState } from "react"

interface ScoreBarProps {
  label: string
  value: number
  delay?: number
}

export function ScoreBar({ label, value, delay = 0 }: ScoreBarProps) {
  const [animated, setAnimated] = useState(0)

  useEffect(() => {
    const timeout = setTimeout(() => {
      setAnimated(value)
    }, delay)
    return () => clearTimeout(timeout)
  }, [value, delay])

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <span className="text-xs uppercase tracking-widest text-muted-foreground">
          {label}
        </span>
        <span className="text-xs font-semibold text-foreground">
          {animated}%
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-sm bg-muted">
        <div
          className="h-full rounded-sm bg-foreground transition-all duration-1000 ease-out"
          style={{ width: `${animated}%` }}
        />
      </div>
    </div>
  )
}
