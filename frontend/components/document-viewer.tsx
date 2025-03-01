"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Eye, Download, Code } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

// Mock data for demonstration
const mockDocument = {
  id: "doc-123",
  name: "Invoice-2023-04-15.pdf",
  processedAt: "2023-04-15T14:30:00Z",
  pages: [
    {
      pageNumber: 1,
      imageUrl: "/placeholder.svg?height=800&width=600",
      extractedData: {
        "Invoice Number": "INV-2023-0415",
        Date: "April 15, 2023",
        Customer: "Acme Corporation",
        Amount: "$1,250.00",
        Tax: "$112.50",
        Total: "$1,362.50",
      },
      confidence: 0.92,
    },
  ],
}

export function DocumentViewer() {
  const [currentPage, setCurrentPage] = useState(0)
  const [showRawData, setShowRawData] = useState(false)

  // In a real app, you would fetch documents from an API
  const document = mockDocument
  const page = document.pages[currentPage]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold">{document.name}</h2>
          <p className="text-sm text-muted-foreground">
            Processed on {new Date(document.processedAt).toLocaleString()}
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button variant="outline" size="sm" onClick={() => setShowRawData(!showRawData)}>
            <Code className="mr-2 h-4 w-4" />
            {showRawData ? "Hide Raw" : "Show Raw"}
          </Button>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardContent className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-medium">
                Page {page.pageNumber} of {document.pages.length}
              </h3>
              <Badge variant="outline" className="flex items-center">
                <Eye className="mr-1 h-3 w-3" />
                Confidence: {(page.confidence * 100).toFixed(0)}%
              </Badge>
            </div>
            <div className="overflow-hidden rounded-lg border">
              <img
                src={page.imageUrl || "/placeholder.svg"}
                alt={`Page ${page.pageNumber}`}
                className="h-auto w-full object-contain"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <Tabs defaultValue="extracted" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="extracted">Extracted Data</TabsTrigger>
                <TabsTrigger value="raw">Raw JSON</TabsTrigger>
              </TabsList>
              <TabsContent value="extracted" className="mt-4">
                <ScrollArea className="h-[500px] rounded-md border p-4">
                  <div className="space-y-4">
                    {Object.entries(page.extractedData).map(([key, value]) => (
                      <div key={key} className="space-y-1">
                        <h4 className="text-sm font-medium text-muted-foreground">{key}</h4>
                        <p className="rounded-md bg-secondary p-2 text-sm">{value}</p>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </TabsContent>
              <TabsContent value="raw" className="mt-4">
                <ScrollArea className="h-[500px] rounded-md border">
                  <pre className="p-4 text-xs">{JSON.stringify(page, null, 2)}</pre>
                </ScrollArea>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

