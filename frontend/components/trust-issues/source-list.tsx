import { ExternalLink } from "lucide-react"

interface Source {
  name: string
  headline: string
  status?: string
}

interface SourceListProps {
  sources: Source[]
}

export function SourceList({ sources }: SourceListProps) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground">
        Sources Checked
      </h3>
      <div className="flex flex-col gap-0">
        {sources.map((source, i) => (
          <div
            key={source.name}
            className={`flex items-center justify-between px-2 py-2 ${
              i !== sources.length - 1 ? "border-b border-border/50" : ""
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
