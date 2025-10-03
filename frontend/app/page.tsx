"use client"

import { useState, useEffect } from "react"
import { DataroomSidebar } from "@/components/dataroom-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { DocumentsModal } from "@/components/documents-modal"
import { UploadModal } from "@/components/upload-modal"
import { SummaryModal } from "@/components/summary-modal"
import { DocumentValidationToast, ValidationResult } from "@/components/document-validation-toast"
import { tasksApi } from "@/lib/api"
import type { Task } from "@/types/api"

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)
  const [showDocuments, setShowDocuments] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [showSummary, setShowSummary] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [validations, setValidations] = useState<ValidationResult[]>([])

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    setIsLoading(true)
    try {
      const data = await tasksApi.list()
      setTasks(data)
    } catch (error) {
      console.error("Failed to fetch tasks:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleValidationStart = (filename: string) => {
    setValidations((prev) => [
      ...prev,
      {
        filename,
        status: "validating",
      },
    ])
  }

  const handleValidationComplete = (
    filename: string,
    result: { success: boolean; summary?: string; error?: string },
  ) => {
    setValidations((prev) =>
      prev.map((v) =>
        v.filename === filename
          ? {
              ...v,
              status: result.success ? "success" : "error",
              summary: result.summary,
              error: result.error,
            }
          : v,
      ),
    )
  }

  const handleCloseValidation = (filename: string) => {
    setValidations((prev) => prev.filter((v) => v.filename !== filename))
  }

  const selectedTask = tasks.find((t) => t.id === selectedTaskId)

  return (
    <div className="flex h-screen bg-background dark">
      <DataroomSidebar
        datarooms={tasks}
        selectedId={selectedTaskId}
        onSelect={setSelectedTaskId}
        onRefresh={fetchTasks}
      />

      <ChatInterface
        selectedDataroom={selectedTask}
        onShowDocuments={() => setShowDocuments(true)}
        onShowUpload={() => setShowUpload(true)}
        onShowSummary={() => setShowSummary(true)}
      />

      <DocumentsModal
        open={showDocuments}
        onClose={() => setShowDocuments(false)}
        taskId={selectedTaskId || undefined}
        taskName={selectedTask?.name}
      />

      <UploadModal
        open={showUpload}
        onClose={() => setShowUpload(false)}
        taskId={selectedTaskId || undefined}
        taskName={selectedTask?.name}
        onValidationStart={handleValidationStart}
        onValidationComplete={handleValidationComplete}
      />

      <SummaryModal
        open={showSummary}
        onClose={() => setShowSummary(false)}
        taskId={selectedTaskId || undefined}
      />

      {/* Validation Toasts */}
      <DocumentValidationToast validations={validations} onClose={handleCloseValidation} />
    </div>
  )
}
