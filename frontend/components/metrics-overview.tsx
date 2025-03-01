"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Chart, ChartContainer, ChartTooltip, ChartLegend } from "@/components/ui/chart"
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts"

// Mock data for demonstration
const confidenceData = [
  { month: "Jan", invoices: 92, receipts: 88, forms: 85 },
  { month: "Feb", invoices: 93, receipts: 87, forms: 86 },
  { month: "Mar", invoices: 91, receipts: 89, forms: 84 },
  { month: "Apr", invoices: 94, receipts: 90, forms: 87 },
  { month: "May", invoices: 93, receipts: 91, forms: 88 },
  { month: "Jun", invoices: 95, receipts: 92, forms: 89 },
]

const volumeData = [
  { month: "Jan", count: 120 },
  { month: "Feb", count: 150 },
  { month: "Mar", count: 180 },
  { month: "Apr", count: 220 },
  { month: "May", count: 270 },
  { month: "Jun", count: 310 },
]

const fieldExtractionData = [
  { name: "Invoice Number", success: 98, failure: 2 },
  { name: "Date", success: 97, failure: 3 },
  { name: "Customer", success: 92, failure: 8 },
  { name: "Amount", success: 95, failure: 5 },
  { name: "Tax", success: 91, failure: 9 },
  { name: "Total", success: 96, failure: 4 },
]

export function MetricsOverview() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Confidence Scores by Document Type</CardTitle>
        </CardHeader>
        <CardContent>
          <Chart className="h-[300px]">
            <ChartContainer>
              <LineChart data={confidenceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis domain={[80, 100]} />
                <Tooltip content={<ChartTooltip />} />
                <Legend content={<ChartLegend />} />
                <Line type="monotone" dataKey="invoices" stroke="#3b82f6" name="Invoices" strokeWidth={2} />
                <Line type="monotone" dataKey="receipts" stroke="#10b981" name="Receipts" strokeWidth={2} />
                <Line type="monotone" dataKey="forms" stroke="#f59e0b" name="Forms" strokeWidth={2} />
              </LineChart>
            </ChartContainer>
          </Chart>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Document Processing Volume</CardTitle>
        </CardHeader>
        <CardContent>
          <Chart className="h-[300px]">
            <ChartContainer>
              <AreaChart data={volumeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip content={<ChartTooltip />} />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#3b82f6"
                  fill="#3b82f6"
                  fillOpacity={0.2}
                  name="Documents"
                />
              </AreaChart>
            </ChartContainer>
          </Chart>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Field Extraction Success Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <Chart className="h-[300px]">
            <ChartContainer>
              <BarChart data={fieldExtractionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip content={<ChartTooltip />} />
                <Legend content={<ChartLegend />} />
                <Bar dataKey="success" stackId="a" fill="#10b981" name="Success" />
                <Bar dataKey="failure" stackId="a" fill="#ef4444" name="Failure" />
              </BarChart>
            </ChartContainer>
          </Chart>
        </CardContent>
      </Card>
    </div>
  )
}

