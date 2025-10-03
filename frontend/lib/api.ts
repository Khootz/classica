// API Base URL - Change this to point to your backend
export const API_BASE_URL = "http://localhost:8000"

import type {
  Task,
  CreateTaskRequest,
  Document,
  ChatRequest,
  ChatResponse,
  ChatStatus,
  ChatAnswer,
  Memo,
  MemoExportResponse,
} from "@/types/api"

// Helper function for API calls
async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

// Tasks API
export const tasksApi = {
  // GET /tasks - List all tasks
  list: () => apiRequest<Task[]>("/tasks"),

  // POST /tasks - Create a new task
  create: (data: CreateTaskRequest) =>
    apiRequest<Task>("/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),
}

// Documents API
export const documentsApi = {
  // GET /tasks/{task_id}/documents - List documents for a task
  list: (taskId: string) => apiRequest<Document[]>(`/tasks/${taskId}/documents`),

  // POST /tasks/{task_id}/documents - Upload a document
  upload: async (taskId: string, file: File): Promise<Document> => {
    const formData = new FormData()
    formData.append("file", file)

    const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/documents`, {
      method: "POST",
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`)
    }

    return response.json()
  },
}

// Chat API
export const chatApi = {
  // POST /tasks/{task_id}/chat - Send a message
  send: (taskId: string, data: ChatRequest) =>
    apiRequest<ChatResponse>(`/tasks/${taskId}/chat`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // GET /tasks/{task_id}/chat/{chat_id}/status - Poll chat status
  getStatus: (taskId: string, chatId: string) =>
    apiRequest<ChatStatus>(`/tasks/${taskId}/chat/${chatId}/status`),

  // GET /tasks/{task_id}/chat/{chat_id} - Get final chat answer
  getAnswer: (taskId: string, chatId: string) => apiRequest<ChatAnswer>(`/tasks/${taskId}/chat/${chatId}`),
}

// Memo API
export const memoApi = {
  // GET /tasks/{task_id}/memo - Get live memo
  get: (taskId: string) => apiRequest<Memo>(`/tasks/${taskId}/memo`),

  // POST /tasks/{task_id}/memo/export - Export memo
  export: (taskId: string) =>
    apiRequest<MemoExportResponse>(`/tasks/${taskId}/memo/export`, {
      method: "POST",
    }),
}

// Polling utility for chat status with 404 retry logic
export async function pollChatStatus(
  taskId: string,
  chatId: string,
  onProgress: (status: ChatStatus) => void,
  intervalMs: number = 2000,
  maxRetries: number = 30,
): Promise<ChatStatus> {
  return new Promise((resolve, reject) => {
    let retryCount = 0

    const poll = async () => {
      try {
        const status = await chatApi.getStatus(taskId, chatId)
        onProgress(status)

        // Reset retry count on successful fetch
        retryCount = 0

        if (status.status === "done") {
          resolve(status)
        } else {
          setTimeout(poll, intervalMs)
        }
      } catch (error) {
        // Check if it's a 404 error (chat not created yet)
        if (error instanceof Error && error.message.includes("404")) {
          retryCount++
          
          if (retryCount <= maxRetries) {
            // Chat not created yet, retry after interval
            console.log(`Chat ${chatId} not found yet, retrying... (${retryCount}/${maxRetries})`)
            setTimeout(poll, intervalMs)
          } else {
            reject(new Error(`Chat ${chatId} not found after ${maxRetries} retries`))
          }
        } else {
          // Other errors should fail immediately
          reject(error)
        }
      }
    }

    poll()
  })
}
