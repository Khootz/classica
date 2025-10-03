"use client"

import { useState, useEffect } from "react"
import { DataroomSidebar } from "@/components/dataroom-sidebar"
import { ChatInterface } from "@/components/chat-interface"
import { DocumentsModal } from "@/components/documents-modal"
import { UploadModal } from "@/components/upload-modal"
import { SummaryModal } from "@/components/summary-modal"
import { tasksApi } from "@/lib/api"
import type { Task } from "@/types/api"

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null)
  const [showDocuments, setShowDocuments] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [showSummary, setShowSummary] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

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
      />

      <SummaryModal
        open={showSummary}
        onClose={() => setShowSummary(false)}
        taskId={selectedTaskId || undefined}
      />
    </div>
  )
}
