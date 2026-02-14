import { ExternalLink } from "lucide-react"

const SOURCES = [
  { name: "Reuters", headline: "Fact-check database cross-referenced" },
  { name: "BBC News", headline: "Related reporting found — partial match" },
  { name: "Associated Press", headline: "Wire service corroboration pending" },
  { name: "Snopes", headline: "No matching claim investigation found" },
  { name: "PolitiFact", headline: "Claim rating unavailable" },
]

export function SourceList() {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground">
        Sources Checked
      </h3>
      <div className="flex flex-col gap-0">
        {SOURCES.map((source, i) => (
          <div
            key={source.name}
            className={`flex items-center justify-between px-2 py-2 ${
              i !== SOURCES.length - 1 ? "border-b border-border/50" : ""
            }`}
          >
            <div className="flex flex-col gap-0.5">
              <span className="text-[11px] font-medium text-foreground">
                {source.name}
              </span>
              <span className="text-[10px] text-muted-foreground">
                {source.headline}
              </span>
            </div>
            <ExternalLink className="h-3 w-3 flex-shrink-0 text-muted-foreground/50" />
          </div>
        ))}
      </div>
    </div>
  )
}
