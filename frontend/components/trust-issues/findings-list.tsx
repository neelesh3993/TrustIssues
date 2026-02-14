interface FindingsListProps {
  findings: string[]
}

export function FindingsList({ findings }: FindingsListProps) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground">
        Findings
      </h3>
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
