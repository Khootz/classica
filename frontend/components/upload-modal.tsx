"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Upload, X, FileText, AlertCircle, CheckCircle2, Loader2 } from "lucide-react"
import { documentsApi } from "@/lib/api"
import { validateDocuments } from "@/lib/validation"
import { RedFlagsPopup, type DocumentRedFlags } from "@/components/redflags-popup"

interface UploadModalProps {
  open: boolean
  onClose: () => void
  taskId?: string
  taskName?: string
}

interface FileUploadStatus {
  file: File
  status: "pending" | "uploading" | "success" | "error"
  redFlags?: Record<string, string>
  error?: string
}

export function UploadModal({ open, onClose, taskId, taskName }: UploadModalProps) {
  const [files, setFiles] = useState<FileUploadStatus[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [isValidating, setIsValidating] = useState(false)
  const [showRedFlagsPopup, setShowRedFlagsPopup] = useState(false)
  const [validationResults, setValidationResults] = useState<DocumentRedFlags[]>([])

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const droppedFiles = Array.from(e.dataTransfer.files)
    const fileStatuses: FileUploadStatus[] = droppedFiles.map((file) => ({
      file,
      status: "pending",
    }))
    setFiles((prev) => [...prev, ...fileStatuses])
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      const fileStatuses: FileUploadStatus[] = selectedFiles.map((file) => ({
        file,
        status: "pending",
      }))
      setFiles((prev) => [...prev, ...fileStatuses])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (!taskId) return

    setIsUploading(true)
    const uploadedFilenames: string[] = []

    // Upload all files
    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== "pending") continue

      setFiles((prev) => prev.map((f, idx) => (idx === i ? { ...f, status: "uploading" as const } : f)))

      try {
        const result = await documentsApi.upload(taskId, files[i].file)
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? {
                  ...f,
                  status: "success" as const,
                  redFlags: result.red_flags,
                }
              : f,
          ),
        )
        uploadedFilenames.push(files[i].file.name)
      } catch (error) {
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? {
                  ...f,
                  status: "error" as const,
                  error: error instanceof Error ? error.message : "Upload failed",
                }
              : f,
          ),
        )
      }
    }

    setIsUploading(false)

    // Run batch validation after all uploads complete
    if (uploadedFilenames.length > 0) {
      setIsValidating(true)
      
      try {
        const validationResult = await validateDocuments(taskId, uploadedFilenames)
        
        if (validationResult.success && validationResult.summary) {
          // Parse the validation summary to extract red flags per document
          const parsedResults = parseValidationSummary(validationResult.summary, uploadedFilenames)
          setValidationResults(parsedResults)
          setShowRedFlagsPopup(true)
        }
      } catch (error) {
        console.error("Validation error:", error)
      } finally {
        setIsValidating(false)
      }
    }
  }

  // Helper function to parse validation summary into structured red flags
  const parseValidationSummary = (summary: string, filenames: string[]): DocumentRedFlags[] => {
    // Simple parsing: split by document sections and extract red flags
    // This is a basic implementation - you may want to enhance it based on actual AI response format
    const results: DocumentRedFlags[] = []
    
    for (const filename of filenames) {
      // Try to find the section for this document in the summary
      const docSection = summary.toLowerCase().includes(filename.toLowerCase())
        ? summary
        : ""
      
      // Extract red flags (look for common patterns)
      const redFlags: string[] = []
      const lines = summary.split("\n")
      
      let isInRedFlagsSection = false
      for (const line of lines) {
        const lowerLine = line.toLowerCase()
        
        // Check if we're entering a red flags section
        if (lowerLine.includes("red flag") || lowerLine.includes("critical") || lowerLine.includes("risk")) {
          isInRedFlagsSection = true
        }
        
        // Extract bullet points or numbered items that might be red flags
        if (isInRedFlagsSection && (line.trim().startsWith("-") || line.trim().startsWith("•") || /^\d+\./.test(line.trim()))) {
          const flag = line.replace(/^[-•\d.]\s*/, "").trim()
          if (flag.length > 10) { // Only include substantial flags
            redFlags.push(flag)
          }
        }
      }
      
      results.push({
        filename,
        redFlags,
        summary: summary, // Include full summary for now
      })
    }
    
    return results
  }

  const handleClose = () => {
    setFiles([])
    onClose()
  }

  const getStatusIcon = (status: FileUploadStatus["status"]) => {
    switch (status) {
      case "success":
        return <CheckCircle2 className="w-5 h-5 text-green-600" />
      case "error":
        return <AlertCircle className="w-5 h-5 text-destructive" />
      case "uploading":
        return <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      default:
        return <FileText className="w-5 h-5 text-primary" />
    }
  }

  return (
    <>
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Upload Documents - {taskName || "Dataroom"}</DialogTitle>
          </DialogHeader>

          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="border-2 border-dashed border-border rounded-lg p-12 text-center hover:border-primary transition-colors cursor-pointer"
            onClick={() => document.getElementById("file-input")?.click()}
          >
            <Upload className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-sm font-medium text-foreground mb-1">Drop files here or click to browse</p>
            <p className="text-xs text-muted-foreground">Supports PDF, DOCX, XLSX, and other document formats</p>
            <input id="file-input" type="file" multiple onChange={handleFileInput} className="hidden" />
          </div>

          {/* Validation Status */}
          {isValidating && (
            <div className="bg-primary/10 border border-primary rounded-lg p-4">
              <div className="flex items-center gap-3">
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
                <div>
                  <p className="text-sm font-medium text-white">Running Automated Document Validation...</p>
                  <p className="text-xs text-white/70">Analyzing documents for potential red flags</p>
                </div>
              </div>
            </div>
          )}

        {files.length > 0 && (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {files.map((fileStatus, index) => (
              <div key={index} className="rounded-lg border border-border">
                <div className="flex items-center justify-between p-3">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    {getStatusIcon(fileStatus.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{fileStatus.file.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {(fileStatus.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  {fileStatus.status === "pending" && (
                    <Button variant="ghost" size="sm" onClick={() => removeFile(index)} disabled={isUploading}>
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {/* Red Flags */}
                {fileStatus.redFlags && Object.keys(fileStatus.redFlags).length > 0 && (
                  <div className="px-3 pb-3 space-y-1">
                    <p className="text-xs font-semibold text-muted-foreground mb-1">Red Flags:</p>
                    {Object.entries(fileStatus.redFlags).map(([key, value]) => (
                      <div key={key} className="text-xs text-destructive flex items-start gap-1">
                        <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                        <span>
                          <strong>{key}:</strong> {value}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Error Message */}
                {fileStatus.error && (
                  <div className="px-3 pb-3">
                    <div className="text-xs text-destructive flex items-start gap-1">
                      <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      <span>{fileStatus.error}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="flex justify-end gap-3">
          <Button variant="outline" onClick={handleClose} disabled={isUploading || isValidating}>
            {isUploading || isValidating ? "Close" : "Cancel"}
          </Button>
          <Button
            onClick={handleUpload}
            disabled={files.length === 0 || isUploading || isValidating || !taskId || files.every((f) => f.status !== "pending")}
          >
            {isUploading ? "Uploading..." : isValidating ? "Validating..." : `Upload ${files.length > 0 ? `(${files.length})` : ""}`}
          </Button>
        </div>
      </DialogContent>
    </Dialog>

    {/* Red Flags Popup */}
    <RedFlagsPopup
      open={showRedFlagsPopup}
      onClose={() => setShowRedFlagsPopup(false)}
      documents={validationResults}
      taskName={taskName}
    />
  </>
  )
}
