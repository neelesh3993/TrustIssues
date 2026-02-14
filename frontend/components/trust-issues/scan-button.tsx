"use client"

import { Search } from "lucide-react"

interface ScanButtonProps {
  onClick: () => void
}

export function ScanButton({ onClick }: ScanButtonProps) {
  return (
    <button
      onClick={onClick}
      className="group flex w-full items-center justify-center gap-2.5 rounded-sm border border-foreground/20 bg-foreground/5 px-4 py-3 text-xs font-medium uppercase tracking-[0.2em] text-foreground transition-all hover:border-foreground/40 hover:bg-foreground/10 active:scale-[0.98]"
    >
      <Search className="h-3.5 w-3.5 transition-transform group-hover:rotate-12" />
      Scan This Page
    </button>
  )
}
