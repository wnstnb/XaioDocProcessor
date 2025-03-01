import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { ArrowRight, FileText, BarChart2, MessageSquare, Upload, Database, Zap } from "lucide-react"

export default function Home() {
  return (
    <main className="container py-10">
      <section className="mx-auto flex max-w-[980px] flex-col items-center gap-2 py-8 md:py-12 lg:py-16">
        <h1 className="text-center text-3xl font-bold leading-tight tracking-tighter md:text-5xl lg:text-6xl lg:leading-[1.1]">
          Extract structured data from documents with AI
        </h1>
        <p className="max-w-[750px] text-center text-lg text-muted-foreground sm:text-xl">
          FormSage uses Gemini 2.0 Flash API to extract key-value pairs from PDFs and images with high accuracy
        </p>
        <div className="flex flex-col gap-4 sm:flex-row">
          <Button asChild size="lg">
            <Link href="/documents">
              Upload Documents <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button variant="outline" size="lg" asChild>
            <Link href="/metrics">
              View Metrics <BarChart2 className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </section>

      <section className="mx-auto max-w-[980px] py-8 md:py-12 lg:py-16">
        <h2 className="mb-8 text-center text-2xl font-bold md:text-3xl">How It Works</h2>
        <div className="grid gap-6 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-lg font-medium">Upload</CardTitle>
              <Upload className="h-5 w-5 text-primary" />
            </CardHeader>
            <CardContent>
              <CardDescription className="text-sm">
                Upload PDFs or images containing forms, invoices, receipts, or other structured documents.
              </CardDescription>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-lg font-medium">Process</CardTitle>
              <Zap className="h-5 w-5 text-primary" />
            </CardHeader>
            <CardContent>
              <CardDescription className="text-sm">
                Gemini AI analyzes the documents, identifies key fields, and extracts structured data.
              </CardDescription>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-lg font-medium">Analyze</CardTitle>
              <Database className="h-5 w-5 text-primary" />
            </CardHeader>
            <CardContent>
              <CardDescription className="text-sm">
                View extracted data alongside the original document, analyze metrics, or query the data using natural
                language.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </section>

      <section className="mx-auto max-w-[980px] py-8 md:py-12 lg:py-16">
        <h2 className="mb-8 text-center text-2xl font-bold md:text-3xl">Key Features</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="mr-2 h-5 w-5" /> Document Processing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Upload and process multiple document types including PDFs, images, invoices, and forms.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart2 className="mr-2 h-5 w-5" /> Performance Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Track extraction accuracy, confidence scores, and processing times across document types.
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MessageSquare className="mr-2 h-5 w-5" /> SQL Chat Interface
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Query your document data using natural language, which gets converted to SQL behind the scenes.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>
    </main>
  )
}

