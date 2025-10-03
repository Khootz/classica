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

export interface Citation {
  doc: string
  page: number
}

export interface ChatAnswer {
  chat_id: string
  role: "agent"
  response: string
  reasoning_log: ReasoningStep[]
  citations: Citation[]
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
