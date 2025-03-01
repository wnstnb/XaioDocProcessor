"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Chart, ChartContainer, ChartTooltip } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, Tooltip, XAxis, YAxis } from "recharts"

// Mock data for demonstration
const documentTypeData = [
  { name: "Invoices", value: 45, color: "#3b82f6" },
  { name: "Receipts", value: 30, color: "#10b981" },
  { name: "Forms", value: 15, color: "#f59e0b" },
  { name: "Other", value: 10, color: "#6366f1" },
]

const confidenceByTypeData = [
  { type: "Invoices", confidence: 94 },
  { type: "Receipts", confidence: 91 },
  { type: "Forms", confidence: 87 },
  { type: "Other", confidence: 82 },
]

export function DocumentTypeMetrics() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Document Type Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          <Chart className="h-[300px]">
            <ChartContainer>
              <PieChart>
                <Pie
                  data={documentTypeData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                >
                  {documentTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<ChartTooltip />} />
              </PieChart>
            </ChartContainer>
          </Chart>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Average Confidence by Document Type</CardTitle>
        </CardHeader>
        <CardContent>
          <Chart className="h-[300px]">
            <ChartContainer>
              <BarChart data={confidenceByTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis domain={[0, 100]} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="confidence" name="Confidence Score">
                  {confidenceByTypeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={documentTypeData[index].color} />
                  ))}
                </Bar>
              </BarChart>
            </ChartContainer>
          </Chart>
        </CardContent>
      </Card>
    </div>
  )
}

