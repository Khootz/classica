"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Progress } from "@/components/ui/progress"
import { FileText, Upload, Send, AlertCircle, CheckCircle2, ExternalLink } from "lucide-react"
import { chatApi, pollChatStatus } from "@/lib/api"
import type { ChatAnswer, Citation, ReasoningStep } from "@/types/api"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
  reasoning?: ReasoningStep[]
  citations?: Citation[]
}

interface ChatInterfaceProps {
  selectedDataroom?: { id: string; name: string }
  onShowDocuments: () => void
  onShowUpload: () => void
  onShowSummary: () => void
}

export function ChatInterface({ selectedDataroom, onShowDocuments, onShowUpload, onShowSummary }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progressStatus, setProgressStatus] = useState("")
  const [progressPercent, setProgressPercent] = useState(0)

  const handleSend = async () => {
    if (!input.trim() || !selectedDataroom) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const userInput = input
    setInput("")
    setIsAnalyzing(true)
    setProgressStatus("Sending message...")
    setProgressPercent(0)

    try {
      // Send chat message
      const chatResponse = await chatApi.send(selectedDataroom.id, { message: userInput })

      // Poll for status updates
      await pollChatStatus(
        selectedDataroom.id,
        chatResponse.chat_id,
        (status) => {
          setProgressStatus(status.message)
          setProgressPercent(status.progress)
        },
        2000,
      )

      // Fetch final answer
      const answer = await chatApi.getAnswer(selectedDataroom.id, chatResponse.chat_id)

      const assistantMessage: Message = {
        id: chatResponse.chat_id,
        role: "assistant",
        content: answer.response,
        timestamp: new Date(),
        reasoning: answer.reasoning_log,
        citations: answer.citations,
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `Error: ${error instanceof Error ? error.message : "Failed to get response"}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsAnalyzing(false)
      setProgressStatus("")
      setProgressPercent(0)
    }
  }

  if (!selectedDataroom) {
    return (
      <div className="flex-1 flex items-center justify-center bg-background">
        <div className="text-center">
          <Folder className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-foreground mb-2">No Dataroom Selected</h2>
          <p className="text-muted-foreground">Select a dataroom from the sidebar to start analyzing</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-foreground">{selectedDataroom.name}</h2>
            <p className="text-sm text-muted-foreground">AI Due Diligence Agent</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onShowDocuments} className="text-white bg-transparent">
              <FileText className="w-4 h-4 mr-2" />
              View Documents
            </Button>
            <Button variant="outline" size="sm" onClick={onShowUpload} className="text-white bg-transparent">
              <Upload className="w-4 h-4 mr-2" />
              Upload
            </Button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 px-6 py-4">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/10 mb-4">
                <AlertCircle className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">Start Your Due Diligence</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Ask questions about document validity, potential red flags, compliance issues, or request a
                comprehensive analysis of the dataroom.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-lg px-4 py-3 ${
                  message.role === "user" ? "bg-primary text-primary-foreground" : "bg-card border border-border"
                }`}
              >
                <p className="text-sm leading-relaxed whitespace-pre-wrap text-white">{message.content}</p>

                {/* Reasoning Log */}
                {message.reasoning && message.reasoning.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <p className="text-xs font-semibold text-white/70 mb-2">Reasoning:</p>
                    <div className="space-y-1">
                      {message.reasoning.map((step, idx) => (
                        <div key={idx} className="text-xs text-white/70">
                          • {step.step}: <span className="font-medium text-white">{step.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Citations */}
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50">
                    <p className="text-xs font-semibold text-white/70 mb-2">Sources:</p>
                    <div className="space-y-1">
                      {message.citations.map((citation, idx) => (
                        <div key={idx} className="text-xs text-white/70 flex items-center gap-1">
                          <ExternalLink className="w-3 h-3" />
                          {citation.doc} (Page {citation.page})
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <p className="text-xs mt-2 opacity-70 text-white">{message.timestamp.toLocaleTimeString()}</p>
              </div>
            </div>
          ))}

          {isAnalyzing && (
            <div className="bg-card border border-border rounded-lg p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                <span className="text-sm font-medium text-white">{progressStatus}</span>
              </div>
              <Progress value={progressPercent} className="mb-2" />
              <p className="text-xs text-white/70">{progressPercent}% complete</p>
            </div>
          )}

          {messages.length > 0 && !isAnalyzing && (
            <div className="flex justify-center">
              <Button onClick={onShowSummary} size="lg" className="gap-2">
                <CheckCircle2 className="w-4 h-4" />
                View Summary
              </Button>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border bg-card px-6 py-4">
        <div className="max-w-3xl mx-auto">
          <div className="flex gap-3">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
              placeholder="Ask about document validity, red flags, compliance issues..."
              className="min-h-[60px] resize-none text-white"
              disabled={isAnalyzing}
            />
            <Button onClick={handleSend} disabled={!input.trim() || isAnalyzing} size="lg" className="px-6">
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

function Folder({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z" />
    </svg>
  )
}
