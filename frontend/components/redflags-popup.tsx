"use client"

import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { AlertCircle, AlertTriangle, CheckCircle2, FileText } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"

export interface DocumentRedFlags {
  filename: string
  redFlags: string[]
  summary?: string
}

interface RedFlagsPopupProps {
  open: boolean
  onClose: () => void
  documents: DocumentRedFlags[]
  taskName?: string
}

export function RedFlagsPopup({ open, onClose, documents, taskName }: RedFlagsPopupProps) {
  const totalRedFlags = documents.reduce((sum, doc) => sum + doc.redFlags.length, 0)
  const hasRedFlags = totalRedFlags > 0

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {hasRedFlags ? (
              <>
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                <span>Document Validation Complete - Red Flags Found</span>
              </>
            ) : (
              <>
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                <span>Document Validation Complete - No Issues Found</span>
              </>
            )}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4 p-4 bg-accent/50 rounded-lg">
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{documents.length}</p>
              <p className="text-xs text-white/70">Documents Analyzed</p>
            </div>
            <div className="text-center">
              <p className={`text-2xl font-bold ${hasRedFlags ? "text-yellow-500" : "text-green-600"}`}>
                {totalRedFlags}
              </p>
              <p className="text-xs text-white/70">Red Flags Found</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-white">{taskName || "N/A"}</p>
              <p className="text-xs text-white/70">Dataroom</p>
            </div>
          </div>

          {/* Document Details */}
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-4">
              {documents.map((doc, index) => (
                <div key={index} className="border border-border rounded-lg p-4 bg-card">
                  <div className="flex items-start gap-3 mb-3">
                    <FileText className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-white truncate">{doc.filename}</p>
                      <p className="text-xs text-white/70 mt-1">
                        {doc.redFlags.length === 0 ? (
                          <span className="text-green-600 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            No issues found
                          </span>
                        ) : (
                          <span className="text-yellow-500 flex items-center gap-1">
                            <AlertTriangle className="w-3 h-3" />
                            {doc.redFlags.length} red flag{doc.redFlags.length > 1 ? "s" : ""} identified
                          </span>
                        )}
                      </p>
                    </div>
                  </div>

                  {/* Summary */}
                  {doc.summary && (
                    <div className="mb-3 p-3 bg-accent/30 rounded text-xs text-white/90 whitespace-pre-wrap">
                      {doc.summary}
                    </div>
                  )}

                  {/* Red Flags List */}
                  {doc.redFlags.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-xs font-semibold text-white/70">Critical Issues:</p>
                      {doc.redFlags.map((flag, flagIndex) => (
                        <div key={flagIndex} className="flex items-start gap-2 text-xs">
                          <AlertCircle className="w-4 h-4 text-destructive flex-shrink-0 mt-0.5" />
                          <span className="text-white/90">{flag}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-border">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            {hasRedFlags && (
              <Button variant="default">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Review in Detail
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
