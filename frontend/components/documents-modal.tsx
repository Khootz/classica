"use client"

import { useEffect, useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { FileText, AlertCircle, Loader2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { documentsApi } from "@/lib/api"
import type { Document } from "@/types/api"

interface DocumentsModalProps {
  open: boolean
  onClose: () => void
  taskId?: string
  taskName?: string
}

export function DocumentsModal({ open, onClose, taskId, taskName }: DocumentsModalProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (open && taskId) {
      fetchDocuments()
    }
  }, [open, taskId])

  const fetchDocuments = async () => {
    if (!taskId) return

    setIsLoading(true)
    setError(null)

    try {
      const data = await documentsApi.list(taskId)
      setDocuments(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents")
    } finally {
      setIsLoading(false)
    }
  }
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[80vh]">
        <DialogHeader>
          <DialogTitle>Documents - {taskName || "Dataroom"}</DialogTitle>
        </DialogHeader>

        <ScrollArea className="h-[500px] pr-4">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
              <AlertCircle className="w-5 h-5" />
              <p className="text-sm">{error}</p>
            </div>
          )}

          {!isLoading && !error && documents.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No documents uploaded yet</p>
            </div>
          )}

          {documents.length > 0 && (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div key={doc.id} className="rounded-lg border border-border">
                  <div className="flex items-center gap-3 p-3">
                    <FileText className="w-5 h-5 text-primary flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{doc.filename}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <Badge variant={doc.ingested ? "default" : "secondary"} className="text-xs">
                          {doc.ingested ? "Processed" : "Processing"}
                        </Badge>
                        {Object.keys(doc.red_flags).length > 0 && (
                          <Badge variant="destructive" className="text-xs">
                            {Object.keys(doc.red_flags).length} Red Flag{Object.keys(doc.red_flags).length > 1 ? "s" : ""}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Red Flags */}
                  {Object.keys(doc.red_flags).length > 0 && (
                    <div className="px-3 pb-3 space-y-1">
                      {Object.entries(doc.red_flags).map(([key, value]) => (
                        <div key={key} className="text-xs text-destructive flex items-start gap-1">
                          <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                          <span>
                            <strong>{key}:</strong> {value}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
