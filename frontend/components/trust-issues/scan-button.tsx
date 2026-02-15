"use client"

import { Search } from "lucide-react"

interface ScanButtonProps {
  onClick: () => void
  disabled?: boolean
}

export function ScanButton({ onClick, disabled = false }: ScanButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`group flex w-full items-center justify-center gap-2.5 rounded-sm border px-4 py-3 text-xs font-medium uppercase tracking-[0.2em] transition-all ${
        disabled
          ? "cursor-not-allowed border-foreground/10 bg-foreground/5 text-foreground/30"
          : "border-foreground/20 bg-foreground/5 text-foreground hover:border-foreground/40 hover:bg-foreground/10 active:scale-[0.98]"
      }`}
    >
      <Search className={`h-3.5 w-3.5 transition-transform ${!disabled && "group-hover:rotate-12"}`} />
      {disabled ? "Cooldown Active..." : "Scan This Page"}
    </button>
  )
}
