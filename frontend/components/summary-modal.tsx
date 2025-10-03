"use client"

import { useEffect, useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { AlertTriangle, Download, Loader2 } from "lucide-react"
import { memoApi, API_BASE_URL } from "@/lib/api"
import type { Memo } from "@/types/api"

interface SummaryModalProps {
  open: boolean
  onClose: () => void
  taskId?: string
}

export function SummaryModal({ open, onClose, taskId }: SummaryModalProps) {
  const [memo, setMemo] = useState<Memo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open && taskId) {
      fetchMemo()
    }
  }, [open, taskId])

  const fetchMemo = async () => {
    if (!taskId) return

    setIsLoading(true)
    setError(null)

    try {
      const data = await memoApi.get(taskId)
      setMemo(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load memo")
    } finally {
      setIsLoading(false)
    }
  }

  const handleExport = async () => {
    if (!taskId) return

    setIsExporting(true)

    try {
      const result = await memoApi.export(taskId)
      // Open the exported file in a new tab
      window.open(`${API_BASE_URL}${result.file_url}`, "_blank")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to export memo")
    } finally {
      setIsExporting(false)
    }
  }
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[85vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Due Diligence Memo</span>
            <Button variant="outline" size="sm" onClick={handleExport} disabled={isExporting || !memo}>
              {isExporting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
              Export
            </Button>
          </DialogTitle>
        </DialogHeader>

        <ScrollArea className="h-[600px] pr-4">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
              <AlertTriangle className="w-5 h-5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {memo && (
            <div className="space-y-6">
              {/* Summary */}
              <div className="bg-accent rounded-lg p-4 border border-border">
                <h3 className="text-sm font-semibold text-foreground mb-3">Executive Summary</h3>
                <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">{memo.summary}</p>
              </div>

              {/* Key Metrics */}
              <div>
                <h3 className="text-sm font-semibold text-foreground mb-3">Key Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  {Object.entries(memo.metrics).map(([key, value]) => (
                    <div key={key} className="border border-border rounded-lg p-4">
                      <p className="text-xs text-muted-foreground mb-1 capitalize">
                        {key.replace(/_/g, " ")}
                      </p>
                      <p className="text-lg font-semibold text-foreground flex items-center gap-2">
                        {value}
                        {typeof value === "string" && value.includes("🚩") && (
                          <AlertTriangle className="w-4 h-4 text-destructive" />
                        )}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {!isLoading && !error && !memo && (
            <div className="text-center py-12 text-muted-foreground">
              <p>No memo available yet. Upload documents and chat with the agent to generate insights.</p>
            </div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
