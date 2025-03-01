"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Send, Database, User, Bot } from "lucide-react"

type Message = {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: Date
  sql?: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      content: "Hello! I'm your SQL assistant. Ask me questions about your document data.",
      role: "assistant",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = () => {
    if (!input.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate AI response
    setTimeout(() => {
      let response: Message

      // Mock responses based on user input
      if (input.toLowerCase().includes("invoice")) {
        response = {
          id: (Date.now() + 1).toString(),
          content:
            "I found 24 invoices in the database. The total value is $28,450.75. The average invoice amount is $1,185.45.",
          role: "assistant",
          timestamp: new Date(),
          sql: "SELECT COUNT(*) as count, SUM(amount) as total, AVG(amount) as average FROM documents WHERE type = 'invoice'",
        }
      } else if (input.toLowerCase().includes("confidence")) {
        response = {
          id: (Date.now() + 1).toString(),
          content:
            "There are 5 documents with confidence score below 80%. They are: Receipt-2023-05-12.jpg, Form-2023-06-01.pdf, Invoice-2023-04-22.pdf, Receipt-2023-05-30.jpg, and Form-2023-06-05.pdf.",
          role: "assistant",
          timestamp: new Date(),
          sql: "SELECT filename FROM documents WHERE confidence < 0.8 ORDER BY confidence ASC",
        }
      } else {
        response = {
          id: (Date.now() + 1).toString(),
          content:
            "I've analyzed your question and found relevant information in the database. Is there anything specific you'd like to know about the documents?",
          role: "assistant",
          timestamp: new Date(),
        }
      }

      setMessages((prev) => [...prev, response])
      setIsLoading(false)
    }, 1500)
  }

  return (
    <div className="flex h-[500px] flex-col">
      <ScrollArea className="flex-1 p-4">
        <div className="space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                }`}
              >
                <div className="mb-1 flex items-center">
                  {message.role === "user" ? <User className="mr-2 h-4 w-4" /> : <Bot className="mr-2 h-4 w-4" />}
                  <span className="text-xs font-medium">{message.role === "user" ? "You" : "FormSage"}</span>
                  <span className="ml-2 text-xs text-muted-foreground">{message.timestamp.toLocaleTimeString()}</span>
                </div>
                <p>{message.content}</p>
                {message.sql && (
                  <div className="mt-2 rounded bg-secondary/50 p-2 text-xs font-mono">
                    <div className="flex items-center text-muted-foreground">
                      <Database className="mr-1 h-3 w-3" />
                      SQL Query:
                    </div>
                    {message.sql}
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg bg-muted px-4 py-2">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground"></div>
                  <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:0.2s]"></div>
                  <div className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:0.4s]"></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>
      <div className="border-t p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="flex space-x-2"
        >
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  )
}

