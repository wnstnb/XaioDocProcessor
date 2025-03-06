"use client"

import React, { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChatInterface } from "@/components/chat-interface"
import axios from "axios"


interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: string
}

interface SavedConversation {
  id: number
  title: string
  conversation: {
    role: string
    message?: string
    content?: string
  }[]
  created_at: string
}

export default function ChatPage() {
  // The main chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([])

  // State for saved conversations
  const [savedConversations, setSavedConversations] = useState<SavedConversation[]>([])
  const [selectedConversationId, setSelectedConversationId] = useState<string>("")
  const [isLoading, setIsLoading] = useState(false)

  // Get the 5 most recent conversations
  const recentConversations = savedConversations.slice(0, 5);

  // // Function to handle clicking on a recent conversation link
  // const handleRecentConversationClick = (convId: number) => {
  //   setSelectedConversationId(convId.toString());
    
  //   // Find the chosen conversation
  //   const conv = savedConversations.find((c) => c.id === convId);
  //   if (conv) {
  //     // Convert the saved conversation format to the ChatMessage format
  //     const formattedMessages: ChatMessage[] = conv.conversation.map((msg, index) => ({
  //       id: index.toString(),
  //       role: msg.role as "user" | "assistant",
  //       content: msg.content || msg.message || "",
  //       timestamp: "Loaded message"
  //     }));
      
  //     setChatMessages(formattedMessages);
  //   }
  // };

  // Load the list of saved conversations once
  useEffect(() => {
    setIsLoading(true);
    // Adjust URL to match your FastAPI route
    axios
      .get("http://localhost:8000/conversations")
      .then((res) => {
        setSavedConversations(res.data)
      })
      .catch((err) => {
        console.error("Error fetching saved conversations:", err)
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [])

  // Handler: user picks a conversation from the dropdown
  const handleSelectConversation = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const convId = e.target.value
    setSelectedConversationId(convId)
    
    if (!convId) {
      // If user picks "-- New Conversation --", just clear chat
      setChatMessages([]);
      return;
    }

    // Find the chosen conversation
    const conv = savedConversations.find((c) => String(c.id) === convId)
    if (conv) {
      console.log("Selected conversation:", conv);
      
      try {
        // Ensure conversation is an array
        let conversationArray = conv.conversation;
        
        // If it's a string (which shouldn't happen with proper backend parsing), try to parse it
        if (typeof conversationArray === 'string') {
          console.log("Conversation is a string, attempting to parse:", conversationArray);
          conversationArray = JSON.parse(conversationArray);
        }
        
        if (!Array.isArray(conversationArray)) {
          console.error("Conversation is not an array after processing:", conversationArray);
          return;
        }
        
        // Convert the saved conversation format to the ChatMessage format
        const formattedMessages: ChatMessage[] = conversationArray.map((msg, index) => {
          // Ensure we have the required fields
          if (!msg || typeof msg !== 'object') {
            console.error("Invalid message format:", msg);
            return null;
          }
          
          return {
            id: index.toString(),
            role: (msg.role || "assistant") as "user" | "assistant",
            content: msg.content || msg.message || "",
            timestamp: "Loaded message"
          };
        }).filter(Boolean) as ChatMessage[]; // Remove any null entries
        
        console.log("Formatted messages:", formattedMessages);
        
        if (formattedMessages.length > 0) {
          setChatMessages(formattedMessages);
        } else {
          console.error("No valid messages found in conversation");
        }
      } catch (error) {
        console.error("Error processing conversation:", error);
      }
    }
  }
  // Function to handle clicking on a recent conversation link
  const handleRecentConversationClick = (convId: number) => {
    setSelectedConversationId(convId.toString());
    
    // Find the chosen conversation
    const conv = savedConversations.find((c) => c.id === convId);
    if (conv) {
      try {
        // Ensure conversation is an array
        let conversationArray = conv.conversation;
        
        // If it's a string (which shouldn't happen with proper backend parsing), try to parse it
        if (typeof conversationArray === 'string') {
          console.log("Conversation is a string, attempting to parse:", conversationArray);
          conversationArray = JSON.parse(conversationArray);
        }
        
        if (!Array.isArray(conversationArray)) {
          console.error("Conversation is not an array after processing:", conversationArray);
          return;
        }
        
        // Convert the saved conversation format to the ChatMessage format
        const formattedMessages: ChatMessage[] = conversationArray.map((msg, index) => {
          // Ensure we have the required fields
          if (!msg || typeof msg !== 'object') {
            console.error("Invalid message format:", msg);
            return null;
          }
          
          return {
            id: index.toString(),
            role: (msg.role || "assistant") as "user" | "assistant",
            content: msg.content || msg.message || "",
            timestamp: "Loaded message"
          };
        }).filter(Boolean) as ChatMessage[]; // Remove any null entries
        
        console.log("Formatted messages:", formattedMessages);
        
        if (formattedMessages.length > 0) {
          setChatMessages(formattedMessages);
        } else {
          console.error("No valid messages found in conversation");
        }
      } catch (error) {
        console.error("Error processing conversation:", error);
      }
    }
  };

  return (
    <div className="container py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">SQL Chat Interface</h1>
        <p className="text-muted-foreground">Query your document data using natural language. Jump into a saved conversation, or ask questions about what data there is for specific documents.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* LEFT CARD: instructions, plus conversation dropdown & save button */}
        <Card className="md:col-span-1 flex flex-col h-[700px]">
          <CardHeader>
            <CardTitle>Previous Conversations</CardTitle>
            {/* NEW: Load & Save UI */}
            <div className="mt-6 space-y-2">
              <select
                id="convSelect"
                className="p-1 border rounded text-sm w-full"
                value={selectedConversationId}
                onChange={handleSelectConversation}
              >
                <option value="">-- New Conversation --</option>
                {savedConversations.map((conv) => (
                  <option key={conv.id} value={conv.id.toString()}>
                    {conv.title}
                  </option>
                ))}
              </select>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-sm">
              <div>
                <h3 className="font-medium">Most Recent:</h3>
                <ul className="mt-2 space-y-2">
                  {isLoading ? (
                    <li className="text-gray-500">Loading conversations...</li>
                  ) : recentConversations.length > 0 ? (
                    recentConversations.map((conv) => (
                      <li key={conv.id} className="flex items-center">
                        <button
                          onClick={() => handleRecentConversationClick(conv.id)}
                          className="text-blue-500 hover:text-blue-700 hover:underline text-left truncate max-w-full"
                          title={conv.title}
                        >
                          {conv.title}
                        </button>
                      </li>
                    ))
                  ) : (
                    <li className="text-gray-500">No recent conversations</li>
                  )}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* RIGHT CARD: The chat interface */}
        <Card className="md:col-span-2 flex flex-col h-[700px]">
          <CardHeader className="flex-shrink-0">
            <CardTitle>Chat</CardTitle>
            <CardDescription>Ask questions about your document data</CardDescription>
          </CardHeader>
          <CardContent className="flex-grow overflow-hidden p-0">
            {/* Pass in chatHistory and setChatHistory so ChatInterface can manage messages */}
            <ChatInterface 
              initialMessages={chatMessages} 
              onMessagesChange={setChatMessages}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}