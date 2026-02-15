import { useHighlight } from "@/src/hooks/useHighlight"
import { useState } from "react"

interface FindingsListProps {
  findings: string[]
}

export function FindingsList({ findings }: FindingsListProps) {
  const { highlightFindings, clearHighlights } = useHighlight()
  const [highlightActive, setHighlightActive] = useState(false)

  const handleToggleHighlight = async () => {
    if (highlightActive) {
      await clearHighlights()
      setHighlightActive(false)
    } else {
      await highlightFindings(findings)
      setHighlightActive(true)
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <h3 className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground">
          Findings
        </h3>
        {findings.length > 0 && (
          <button
            onClick={handleToggleHighlight}
            className={`text-[8px] uppercase tracking-widest px-2 py-1 rounded transition-colors ${
              highlightActive
                ? 'bg-amber-500 text-white'
                : 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30'
            }`}
            title="Highlight findings in the webpage"
          >
            {highlightActive ? '✓ Highlighting' : '🔍 Highlight'}
          </button>
        )}
      </div>
      <ul className="flex flex-col gap-1.5 pl-1">
        {findings.map((finding) => (
          <li key={finding} className="flex items-start gap-2">
            <span className="mt-1 block h-1 w-1 flex-shrink-0 rounded-full bg-foreground/40" />
            <span className="text-[11px] leading-relaxed text-secondary-foreground">
              {finding}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
