"use client"

import { useEffect } from "react"
import { useAnalysis } from "@/src/hooks/useAnalysis"
import { ScanButton } from "./scan-button"
import { LoadingState } from "./loading-state"
import { ScoreBar } from "./score-bar"
import { CaseReport } from "./case-report"
import { SourceList } from "./source-list"
import { FindingsList } from "./findings-list"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"

export function PopupContainer() {
  const { status, data, error, analyze, reset } = useAnalysis()

  const handleScan = async () => {
    await analyze()
  }

  const handleReset = () => {
    reset()
  }

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-[360px] flex-col bg-background">
      {/* Header */}
      <header className="flex flex-col gap-0.5 px-4 pb-3 pt-5">
        <h1 className="text-sm font-bold uppercase tracking-[0.3em] text-foreground">
          Trust Issues
        </h1>
        <p className="text-[10px] uppercase tracking-[0.15em] text-muted-foreground">
          Web Content Investigation Tool
        </p>
        <div className="mt-3 h-px w-full bg-border" />
      </header>

      {/* Main Content */}
      <main className="flex flex-1 flex-col gap-5 px-4 py-3">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Scan Button / Loading */}
        {status === "idle" && <ScanButton onClick={handleScan} />}
        {status === "analyzing" && <LoadingState />}

        {/* Results */}
        {status === "done" && data && (
          <div className="flex flex-col gap-5">
            {/* Score Bars */}
            <div className="flex flex-col gap-4 rounded-sm border border-border bg-card p-3">
              <ScoreBar
                label="AI-Generated Content Likelihood"
                value={Math.round(data.aiGenerationLikelihood)}
                delay={200}
              />
              <ScoreBar
                label="Credibility Score"
                value={Math.round(data.credibilityScore)}
                delay={400}
              />
              <ScoreBar
                label="Manipulation Risk"
                value={Math.round(data.manipulationRisk)}
                delay={600}
              />
            </div>

            {/* Case Report */}
            <div className="flex flex-col gap-2">
              <h3 className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground">
                Case Report
              </h3>
              <div className="rounded-sm border border-border bg-muted/50 p-3">
                <p className="text-[11px] leading-relaxed text-secondary-foreground">
                  {data.report}
                </p>
              </div>
            </div>

            {/* Sources */}
            <SourceList sources={data.sources} />

            {/* Findings */}
            <FindingsList findings={data.findings} />

            {/* Rescan */}
            <button
              onClick={handleReset}
              className="text-[10px] uppercase tracking-[0.2em] text-muted-foreground transition-colors hover:text-foreground"
            >
              {"[ Run New Scan ]"}
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="px-4 pb-4 pt-3">
        <div className="h-px w-full bg-border" />
        <p className="mt-3 text-center text-[9px] uppercase tracking-[0.2em] text-muted-foreground/60">
          {"Trust Issues \u2014 Siren\u2019s Call Track"}
        </p>
      </footer>
    </div>
  )
}
