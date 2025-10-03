"use client"

import { useState, useEffect } from "react"
import { AlertCircle, CheckCircle2, FileText, Loader2, X } from "lucide-react"
import { cn } from "@/lib/utils"

export interface ValidationResult {
  filename: string
  status: "validating" | "success" | "error"
  summary?: string
  error?: string
}

interface DocumentValidationToastProps {
  validations: ValidationResult[]
  onClose: (filename: string) => void
}

export function DocumentValidationToast({ validations, onClose }: DocumentValidationToastProps) {
  if (validations.length === 0) return null

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      {validations.map((validation) => (
        <ValidationCard key={validation.filename} validation={validation} onClose={() => onClose(validation.filename)} />
      ))}
    </div>
  )
}

function ValidationCard({ validation, onClose }: { validation: ValidationResult; onClose: () => void }) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <div
      className={cn(
        "bg-card border rounded-lg shadow-lg overflow-hidden transition-all",
        validation.status === "error" && "border-destructive",
        validation.status === "success" && "border-green-500/50",
      )}
    >
      {/* Header */}
      <div className="p-4 flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          {validation.status === "validating" && <Loader2 className="w-5 h-5 text-primary animate-spin" />}
          {validation.status === "success" && <CheckCircle2 className="w-5 h-5 text-green-600" />}
          {validation.status === "error" && <AlertCircle className="w-5 h-5 text-destructive" />}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-4 h-4 text-muted-foreground" />
            <p className="text-sm font-medium text-foreground truncate">{validation.filename}</p>
          </div>

          <p className="text-xs text-muted-foreground">
            {validation.status === "validating" && "Running automated document validation..."}
            {validation.status === "success" && "Validation complete"}
            {validation.status === "error" && `Validation failed: ${validation.error}`}
          </p>

          {/* Summary Preview */}
          {validation.status === "success" && validation.summary && (
            <div className="mt-2">
              <p className="text-xs text-foreground line-clamp-2">{validation.summary}</p>
              {validation.summary.length > 100 && (
                <button
                  onClick={() => setIsExpanded(!isExpanded)}
                  className="text-xs text-primary hover:underline mt-1"
                >
                  {isExpanded ? "Show less" : "Show more"}
                </button>
              )}
            </div>
          )}
        </div>

        {/* Close button */}
        {validation.status !== "validating" && (
          <button onClick={onClose} className="flex-shrink-0 text-muted-foreground hover:text-foreground">
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Expanded Summary */}
      {isExpanded && validation.summary && (
        <div className="px-4 pb-4 pt-0">
          <div className="bg-accent/50 rounded p-3 text-xs text-foreground whitespace-pre-wrap">{validation.summary}</div>
        </div>
      )}

      {/* Progress bar for validating */}
      {validation.status === "validating" && (
        <div className="h-1 bg-accent">
          <div className="h-full bg-primary animate-pulse w-2/3" />
        </div>
      )}
    </div>
  )
}
