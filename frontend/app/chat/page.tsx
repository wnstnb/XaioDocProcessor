import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChatInterface } from "@/components/chat-interface"

export default function ChatPage() {
  return (
    <div className="container py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">SQL Chat Interface</h1>
        <p className="text-muted-foreground">Query your document data using natural language</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-1">
          <CardHeader>
            <CardTitle>How It Works</CardTitle>
            <CardDescription>Ask questions about your document data in plain English</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 text-sm">
              <div>
                <h3 className="font-medium">Example Questions:</h3>
                <ul className="mt-2 list-disc space-y-1 pl-4">
                  <li>Show me all invoices from last month</li>
                  <li>What's the average amount across all receipts?</li>
                  <li>Which customer has the most invoices?</li>
                  <li>List documents with confidence below 80%</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium">Behind the Scenes:</h3>
                <p className="mt-1">
                  Your questions are converted to SQL queries that run against the document database, retrieving the
                  information you need.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Chat</CardTitle>
            <CardDescription>Ask questions about your document data</CardDescription>
          </CardHeader>
          <CardContent>
            <ChatInterface />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

