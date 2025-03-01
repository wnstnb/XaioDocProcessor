import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { FileUploader } from "@/components/file-uploader"
import { DocumentViewer } from "@/components/document-viewer"

export default function DocumentsPage() {
  return (
    <div className="container py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Document Processing</h1>
        <p className="text-muted-foreground">Upload documents to extract structured data using AI</p>
      </div>

      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="upload">Upload</TabsTrigger>
          <TabsTrigger value="history">Processing History</TabsTrigger>
        </TabsList>
        <TabsContent value="upload" className="mt-6">
          <div className="grid gap-6 md:grid-cols-2">
            <Card>
              <CardContent className="p-6">
                <FileUploader />
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6">
                <h3 className="mb-4 text-lg font-medium">Processing Options</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <Button variant="outline" className="w-full">
                      Debug Mode
                    </Button>
                    <Button variant="outline" className="w-full">
                      Show Raw Data
                    </Button>
                  </div>
                  <Button className="w-full">Process Documents</Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
        <TabsContent value="history" className="mt-6">
          <DocumentViewer />
        </TabsContent>
      </Tabs>
    </div>
  )
}

