"use client"

import React, { useState, useRef, useEffect } from "react"
import axios from "axios"
import { Send, Database, User, Bot } from "lucide-react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import ReactMarkdown from 'react-markdown'

type Message = {
  id: string
  content: string
  role: "user" | "assistant"
  timestamp: string // use a string instead of a Date
  sql?: string
}

type ChatInterfaceProps = {
  initialMessages?: Message[]
  onMessagesChange?: (messages: Message[]) => void
}

export function ChatInterface({ initialMessages, onMessagesChange }: ChatInterfaceProps = {}) {
  // Initialize with a static timestamp string or use initialMessages if provided
  const [messages, setMessages] = useState<Message[]>(
    initialMessages || [
      {
        id: "1",
        content: "Hello! I'm your SQL assistant. Ask me questions about your document data.",
        role: "assistant",
        timestamp: "Initial message", // Use a static string instead of dynamic time
      },
    ]
  )
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // For CRUD confirmation:
  const [pendingSQL, setPendingSQL] = useState<string | null>(null)
  const [awaitingConfirmation, setAwaitingConfirmation] = useState(false)

  // Reference for auto-scrolling
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
   // Scroll to bottom whenever messages change
   useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to scroll to the bottom of the messages
  const scrollToBottom = () => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return

    // Use a static format for timestamps that won't change between server/client
    const now = new Date().toLocaleTimeString(); // We'll use actual timestamps now that we've fixed hydration

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      role: "user",
      timestamp: now,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // Convert natural language to SQL
      const { data } = await axios.post("http://localhost:8000/convert-to-sql", {
        query: userMessage.content,
      })
      const sqlQuery: string = data.sqlQuery || ""

      if (/^(insert|update|delete|create|drop|alter)/i.test(sqlQuery.trim())) {
        // For modifying queries, ask for confirmation
        setPendingSQL(sqlQuery)
        setAwaitingConfirmation(true)
        const confirmMsg: Message = {
          id: (Date.now() + 1).toString(),
          content: "This operation will modify the database. Do you want to proceed? (yes/no)",
          role: "assistant",
          timestamp: new Date().toLocaleTimeString(),
          sql: sqlQuery,
        }
        setMessages((prev) => [...prev, confirmMsg])
      } else {
        // For read-only queries, run it immediately
        const runRes = await axios.post("http://localhost:8000/run-sql", {
          query: sqlQuery,
        })
        
        // Format the response without including the SQL query in the content
        const finalMsg: Message = {
          id: (Date.now() + 2).toString(),
          content: runRes.data.result,
          role: "assistant",
          timestamp: new Date().toLocaleTimeString(),
          sql: sqlQuery,
        }
        setMessages((prev) => [...prev, finalMsg])
      }
    } catch (error: any) {
      const errorMsg: Message = {
        id: (Date.now() + 3).toString(),
        content: `Error generating SQL query: ${error.message}`,
        role: "assistant",
        timestamp: new Date().toLocaleTimeString(),
      }
      setMessages((prev) => [...prev, errorMsg])
    }

    setIsLoading(false)
  }

  const handleConfirmCRUD = async (confirmation: string) => {
    setIsLoading(true)
    if (!pendingSQL) {
      setIsLoading(false)
      return
    }
  
    if (confirmation.trim().toLowerCase() === "yes") {
      try {
        const runRes = await axios.post("http://localhost:8000/run-sql", {
          query: pendingSQL,
        })
        const finalMsg: Message = {
          id: (Date.now() + 4).toString(),
          content: runRes.data.result,
          role: "assistant",
          timestamp: new Date().toLocaleTimeString(),
          sql: pendingSQL,
        }
        setMessages((prev) => [...prev, finalMsg])
      } catch (error: any) {
        const errorMsg: Message = {
          id: (Date.now() + 5).toString(),
          content: `Error running SQL query: ${error.message}`,
          role: "assistant",
          timestamp: new Date().toLocaleTimeString(),
        }
        setMessages((prev) => [...prev, errorMsg])
      }
    } else {
      const cancelMsg: Message = {
        id: (Date.now() + 6).toString(),
        content: "Operation cancelled by the user.",
        role: "assistant",
        timestamp: new Date().toLocaleTimeString(),
      }
      setMessages((prev) => [...prev, cancelMsg])
    }
  
    setAwaitingConfirmation(false)
    setPendingSQL(null)
    setIsLoading(false)
  }

  const handleSaveConversation = async () => {
    if (messages.length <= 1) {
      // Don't save if there's only the initial message
      return;
    }
    
    setIsSaving(true);
    try {
      // Convert our Message[] format to the format expected by the backend
      const conversationForBackend = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      await axios.post("http://localhost:8000/save-conversation", {
        conversation: conversationForBackend,
        title: `Conversation ${new Date().toLocaleString()}`
      });
      
      // Optional: Show success message
      alert("Conversation saved successfully!");
    } catch (error) {
      console.error("Error saving conversation:", error);
      // Optional: Show error message
      alert("Failed to save conversation");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="flex h-[500px] flex-col">
      <ScrollArea
        className="flex-1 p-4"
        style={{ maxHeight: "400px" }}
        ref={scrollAreaRef}
      >
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === "assistant"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-800 text-white"
                }`}
              >
                <div className="mb-1 flex items-center">
                  {message.role === "user" ? (
                    <User className="mr-2 h-4 w-4" />
                  ) : (
                    <Bot className="mr-2 h-4 w-4" />
                  )}
                  <span className="text-xs font-medium">
                    {message.role === "user" ? "You" : "FormSage"}
                  </span>
                  <span className="ml-2 text-xs text-muted-foreground">
                    {message.timestamp}
                  </span>
                </div>
                <div className="my-2">
                  <ReactMarkdown
                    components={{
                      p: ({node, ...props}) => <p className="my-2" {...props} />,
                      code: ({node, ...props}) => <code className="bg-gray-700 px-1 py-0.5 rounded" {...props} />
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                </div>
                {message.sql && (
                  <div className="mt-2 rounded bg-gray-700 p-2 text-xs font-mono">
                    <div className="flex items-center text-gray-400 mb-1">
                      <Database className="mr-1 h-3 w-3" />
                      SQL Query:
                    </div>
                    <div className="text-gray-200">
                      {message.sql}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg bg-blue-500 px-4 py-2 text-white">
                <div className="flex items-center space-x-2">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-white"></div>
                  <div className="h-2 w-2 animate-bounce rounded-full bg-white [animation-delay:0.2s]"></div>
                  <div className="h-2 w-2 animate-bounce rounded-full bg-white [animation-delay:0.4s]"></div>
                </div>
              </div>
            </div>
          )}
        {/* This empty div serves as a marker for scrolling to the bottom */}
        <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="border-t p-4">
        <div className="flex justify-end mb-2">
            <Button 
              onClick={handleSaveConversation} 
              disabled={isLoading || isSaving || messages.length <= 1}
              size="sm"
              variant="outline"
            >
              {isSaving ? "Saving..." : "Save Conversation"}
            </Button>
          </div>
        {awaitingConfirmation ? (
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleConfirmCRUD(input)
              setInput("")
            }}
            className="flex space-x-2"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Confirm operation (yes/no)..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        ) : (
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
        )}
      </div>
    </div>
  )
}
