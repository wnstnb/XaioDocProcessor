"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Chart, ChartContainer, ChartTooltip, ChartLegend } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts"

// Mock data for demonstration
const processingTimeData = [
  { date: "2023-06-01", time: 2.1 },
  { date: "2023-06-02", time: 2.0 },
  { date: "2023-06-03", time: 1.9 },
  { date: "2023-06-04", time: 2.2 },
  { date: "2023-06-05", time: 1.8 },
  { date: "2023-06-06", time: 1.7 },
  { date: "2023-06-07", time: 1.6 },
  { date: "2023-06-08", time: 1.7 },
  { date: "2023-06-09", time: 1.5 },
  { date: "2023-06-10", time: 1.6 },
  { date: "2023-06-11", time: 1.4 },
  { date: "2023-06-12", time: 1.5 },
  { date: "2023-06-13", time: 1.3 },
  { date: "2023-06-14", time: 1.4 },
]

const processingTimeByTypeData = [
  { type: "Invoices", pages1: 1.2, pages2: 1.8, pages3Plus: 2.5 },
  { type: "Receipts", pages1: 1.0, pages2: 1.5, pages3Plus: 2.2 },
  { type: "Forms", pages1: 1.4, pages2: 2.0, pages3Plus: 2.8 },
  { type: "Other", pages1: 1.6, pages2: 2.3, pages3Plus: 3.1 },
]

export function ProcessingTimeMetrics() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Processing Time Trend (Last 14 Days)</CardTitle>
        </CardHeader>
        <CardContent>
          <Chart className="h-[300px]">
            <ChartContainer>
              <LineChart data={processingTimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) =>
                    new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric" })
                  }
                />
                <YAxis label={{ value: "Seconds", angle: -90, position: "insideLeft" }} />
                <Tooltip content={<ChartTooltip />} labelFormatter={(value) => new Date(value).toLocaleDateString()} />
                <Line type="monotone" dataKey="time" stroke="#3b82f6" name="Processing Time (s)" strokeWidth={2} />
              </LineChart>
            </ChartContainer>
          </Chart>
        </CardContent>
      </Card>

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Processing Time by Document Type and Page Count</CardTitle>
        </CardHeader>
        <CardContent>
          <Chart className="h-[300px]">
            <ChartContainer>
              <BarChart data={processingTimeByTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="type" />
                <YAxis label={{ value: "Seconds", angle: -90, position: "insideLeft" }} />
                <Tooltip content={<ChartTooltip />} />
                <Legend content={<ChartLegend />} />
                <Bar dataKey="pages1" fill="#3b82f6" name="1 Page" />
                <Bar dataKey="pages2" fill="#10b981" name="2 Pages" />
                <Bar dataKey="pages3Plus" fill="#f59e0b" name="3+ Pages" />
              </BarChart>
            </ChartContainer>
          </Chart>
        </CardContent>
      </Card>
    </div>
  )
}

