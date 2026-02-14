export function CaseReport() {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground">
        Case Report
      </h3>
      <div className="rounded-sm border border-border bg-muted/50 p-3">
        <p className="text-[11px] leading-relaxed text-secondary-foreground">
          {"Subject page contains content with high probability of AI-assisted generation. Linguistic analysis reveals patterns consistent with large language model output. Cross-referencing with verified news agencies yields partial corroboration of core claims, though key assertions remain unverified. Emotional framing in headline suggests intent to drive engagement rather than inform. Recommend independent verification before citing or sharing."}
        </p>
      </div>
    </div>
  )
}
