import { ClaimDetail } from "@/src/services/api"

interface CaseReportProps {
  claims: ClaimDetail[]
  credibilityScore: number
  aiGenerationLikelihood: number
  manipulationRisk: number
  report: string
}

export function CaseReport({
  claims,
  credibilityScore,
  aiGenerationLikelihood,
  manipulationRisk,
  report,
}: CaseReportProps) {
  const verified = claims.filter((c) => c.status === "verified").length
  const disputed = claims.filter((c) => c.status === "disputed").length
  const uncertain = claims.filter((c) => c.status === "uncertain").length
  const total = claims.length

  // Determine overall credibility assessment
  let credibilityLevel = "CRITICAL"
  let credibilityColor = "text-red-500"
  if (credibilityScore >= 80) {
    credibilityLevel = "HIGHLY CREDIBLE"
    credibilityColor = "text-green-500"
  } else if (credibilityScore >= 60) {
    credibilityLevel = "GENERALLY CREDIBLE"
    credibilityColor = "text-amber-600"
  } else if (credibilityScore >= 40) {
    credibilityLevel = "QUESTIONABLE"
    credibilityColor = "text-orange-500"
  }

  // Generate recommendations based on scores
  const recommendations: string[] = []
  if (aiGenerationLikelihood > 60) {
    recommendations.push(
      "Content shows signs of AI generation - verify authenticity independently"
    )
  }
  if (manipulationRisk > 60) {
    recommendations.push(
      "Content contains manipulative language - read critically and cross-reference facts"
    )
  }
  if (disputed > 0) {
    recommendations.push(
      "Multiple claims are disputed - seek alternative perspectives and official sources"
    )
  }
  if (uncertain > 0 && verified === 0) {
    recommendations.push("No claims could be verified - conduct independent research")
  }
  if (recommendations.length === 0) {
    recommendations.push("Content appears generally reliable but continue to verify key claims")
  }

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground">
        Analysis Report
      </h3>

      {/* Overall Assessment */}
      <div className="rounded-sm border border-border bg-muted/50 p-3">
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="text-[10px] uppercase tracking-[0.1em] font-semibold text-foreground">
            Overall Assessment
          </span>
          <span className={`text-[10px] font-bold uppercase tracking-[0.05em] ${credibilityColor}`}>
            {credibilityLevel}
          </span>
        </div>
        <p className="text-[10px] leading-snug text-secondary-foreground mb-2">
          {report}
        </p>
      </div>

      {/* Claim Breakdown */}
      {total > 0 && (
        <div className="rounded-sm border border-border bg-card p-3">
          <h4 className="text-[10px] uppercase tracking-[0.1em] font-semibold text-foreground mb-2">
            Claim Verification Summary
          </h4>
          <div className="grid grid-cols-3 gap-2 mb-3">
            <div className="text-center">
              <div className="text-sm font-bold text-green-500">{verified}</div>
              <div className="text-[9px] text-muted-foreground">Verified</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-red-500">{disputed}</div>
              <div className="text-[9px] text-muted-foreground">Disputed</div>
            </div>
            <div className="text-center">
              <div className="text-sm font-bold text-amber-500">{uncertain}</div>
              <div className="text-[9px] text-muted-foreground">Uncertain</div>
            </div>
          </div>

          {/* Claim Details */}
          <div className="space-y-2">
            {claims.slice(0, 5).map((claim, idx) => (
              <div
                key={idx}
                className="text-[9px] rounded border border-border/50 bg-background p-2"
              >
                <div className="flex items-start gap-2">
                  <div className="mt-0.5">
                    {claim.status === "verified" && (
                      <span className="text-green-500 font-bold">✓</span>
                    )}
                    {claim.status === "disputed" && (
                      <span className="text-red-500 font-bold">✗</span>
                    )}
                    {claim.status === "uncertain" && (
                      <span className="text-amber-500 font-bold">?</span>
                    )}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-foreground/90 mb-1">
                      {claim.claim.length > 80
                        ? claim.claim.substring(0, 80) + "..."
                        : claim.claim}
                    </p>
                    {claim.rationale && (
                      <p className="text-[8px] text-muted-foreground">
                        {claim.rationale}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {total > 5 && (
              <p className="text-[9px] text-muted-foreground text-center">
                +{total - 5} more claims analyzed
              </p>
            )}
          </div>
        </div>
      )}

      {/* Recommendations */}
      <div className="rounded-sm border border-border bg-blue-500/10 p-3">
        <h4 className="text-[10px] uppercase tracking-[0.1em] font-semibold text-blue-600 mb-2">
          Recommendations
        </h4>
        <ul className="space-y-1">
          {recommendations.map((rec, idx) => (
            <li key={idx} className="text-[9px] text-secondary-foreground flex gap-2">
              <span className="text-blue-500 flex-shrink-0">•</span>
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

