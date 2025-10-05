// API Type Definitions

export interface Task {
  id: string
  name: string
  risk_level: "unknown" | "healthy" | "risky"
  created_at: string
}

export interface CreateTaskRequest {
  name: string
}

export interface Document {
  id: string
  task_id?: string
  filename: string
  ingested: boolean
  red_flags: Record<string, string>
}

export interface ChatRequest {
  message: string
}

export interface ChatResponse {
  chat_id: string
  status: "pending"
}

export interface ChatStatus {
  chat_id: string
  status: "pending" | "parsing_documents" | "searching_index" | "done"
  progress: number
  message: string
}

export interface ReasoningStep {
  step: string
  value: string
}

export interface ReasoningData {
  sub_queries?: string[]
  insights?: string[]
}

export type ReasoningLog = string | ReasoningStep | ReasoningData

export interface Citation {
  document: string  // Document filename
  page: string      // Changed from number to string to support "Chunk X" format
  sub_query?: string  // Optional: Which sub-query found this citation
  sub_query_index?: number  // Optional: Index of the sub-query
}

export interface ChatAnswer {
  chat_id: string
  role: "agent" | "user"
  response: string
  reasoning_log: ReasoningLog[] | ReasoningData  // Support both new object format and legacy array
  citations: Citation[]
  status?: string
  created_at?: string
}

export interface Memo {
  task_id: string
  summary: string
  metrics: {
    revenue_growth?: string
    debt_equity_ratio?: string
    free_cash_flow?: string
    contract_expiries?: number
    [key: string]: string | number | undefined
  }
}

export interface MemoExportResponse {
  task_id: string
  file_url: string
}
