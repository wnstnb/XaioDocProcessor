import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MetricsOverview } from "@/components/metrics-overview"
import { DocumentTypeMetrics } from "@/components/document-type-metrics"
import { ProcessingTimeMetrics } from "@/components/processing-time-metrics"

export default function MetricsPage() {
  return (
    <div className="container py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Performance Metrics</h1>
        <p className="text-muted-foreground">Analyze extraction performance and processing statistics</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Documents Processed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,284</div>
            <p className="text-xs text-muted-foreground">+24% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Confidence Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">89.7%</div>
            <p className="text-xs text-muted-foreground">+2.3% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Processing Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.8s</div>
            <p className="text-xs text-muted-foreground">-0.3s from last month</p>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="mt-8">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="document-types">Document Types</TabsTrigger>
          <TabsTrigger value="processing-time">Processing Time</TabsTrigger>
        </TabsList>
        <TabsContent value="overview" className="mt-6">
          <MetricsOverview />
        </TabsContent>
        <TabsContent value="document-types" className="mt-6">
          <DocumentTypeMetrics />
        </TabsContent>
        <TabsContent value="processing-time" className="mt-6">
          <ProcessingTimeMetrics />
        </TabsContent>
      </Tabs>
    </div>
  )
}

