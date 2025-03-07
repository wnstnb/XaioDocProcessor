"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Chart, ChartContainer, ChartTooltip } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, Tooltip, XAxis, YAxis, Legend } from "recharts"
import { METRICS_QUERIES } from "@/app/metrics/page"

// Types for the data
interface DocumentTypeDataPoint {
  name: string;
  value: number;
  color?: string;
}

interface ConfidenceByTypeDataPoint {
  type: string;
  confidence: number;
}

export function DocumentTypeMetrics() {
  // State for the data
  const [documentTypeData, setDocumentTypeData] = useState<DocumentTypeDataPoint[]>([]);
  const [confidenceByTypeData, setConfidenceByTypeData] = useState<ConfidenceByTypeDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  // Colors for the charts
  const colors = ["#3b82f6", "#10b981", "#f59e0b", "#6366f1", "#ec4899", "#8b5cf6"];

  useEffect(() => {
    // Function to fetch data from the backend
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch document type distribution data
        const distributionResponse = await fetch('/api/metrics/document-type-distribution', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.documentTypeDistributionQuery }),
        });
        
        if (!distributionResponse.ok) {
          throw new Error('Failed to fetch document type distribution data');
        }
        
        const distributionResponseData = await distributionResponse.json();
        console.log('Document type distribution response:', distributionResponseData);
        
        // Parse the response data
        const distributionRawData = parseResponseData(distributionResponseData);
        console.log('Parsed document type distribution data:', distributionRawData);
        
        if (distributionRawData.length > 0) {
          // Convert value to number and add colors
          const distributionDataWithColors = distributionRawData.map((item: any, index: number) => ({
            name: item.name.replace(/_/g, ' '),  // Replace underscores with spaces for better display
            value: parseInt(item.value, 10),
            color: colors[index % colors.length]
          }));
          
          console.log('Transformed document type distribution data:', distributionDataWithColors);
          
          setDocumentTypeData(distributionDataWithColors);
        } else {
          // Use mock data as fallback
          setDocumentTypeData([
            { name: "Invoices", value: 45, color: "#3b82f6" },
            { name: "Receipts", value: 30, color: "#10b981" },
            { name: "Forms", value: 15, color: "#f59e0b" },
            { name: "Other", value: 10, color: "#6366f1" },
          ]);
        }
        
        // Fetch confidence by document type data
        const confidenceResponse = await fetch('/api/metrics/confidence-by-type', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.confidenceByTypeQuery }),
        });
        
        if (!confidenceResponse.ok) {
          throw new Error('Failed to fetch confidence by document type data');
        }
        
        const confidenceResponseData = await confidenceResponse.json();
        console.log('Confidence by type response:', confidenceResponseData);
        
        // Parse the response data
        const confidenceRawData = parseResponseData(confidenceResponseData);
        console.log('Parsed confidence by type data:', confidenceRawData);
        
        if (confidenceRawData.length > 0) {
          // Convert confidence to number
          const confidenceDataWithNumbers = confidenceRawData.map((item: any) => ({
            type: item.type.replace(/_/g, ' '),  // Replace underscores with spaces for better display
            confidence: parseFloat(item.confidence)
          }));
          
          console.log('Transformed confidence by type data:', confidenceDataWithNumbers);
          
          setConfidenceByTypeData(confidenceDataWithNumbers);
        } else {
          // Use mock data as fallback
          setConfidenceByTypeData([
            { type: "Invoices", confidence: 94 },
            { type: "Receipts", confidence: 91 },
            { type: "Forms", confidence: 87 },
            { type: "Other", confidence: 82 },
          ]);
        }
      } catch (error) {
        console.error('Error fetching document type metrics data:', error);
        // Use mock data as fallback
        setDocumentTypeData([
          { name: "Invoices", value: 45, color: "#3b82f6" },
          { name: "Receipts", value: 30, color: "#10b981" },
          { name: "Forms", value: 15, color: "#f59e0b" },
          { name: "Other", value: 10, color: "#6366f1" },
        ]);
        
        setConfidenceByTypeData([
          { type: "Invoices", confidence: 94 },
          { type: "Receipts", confidence: 91 },
          { type: "Forms", confidence: 87 },
          { type: "Other", confidence: 82 },
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  // Helper function to parse the response data
  const parseResponseData = (responseData: any) => {
    if (!responseData) return [];
    
    // Check if the response is already an array of objects
    if (Array.isArray(responseData)) {
      return responseData;
    }
    
    // If the response is a string, parse it
    if (typeof responseData === 'string') {
      // Split the string by newlines to get rows
      const rows = responseData.trim().split('\n');
      
      // The first row contains the column headers
      const headers = rows[0].trim().split(/\s+/);
      
      // Parse the remaining rows
      return rows.slice(1).map(row => {
        const values = row.trim().split(/\s+/);
        const obj: any = {};
        
        headers.forEach((header, index) => {
          obj[header] = values[index];
        });
        
        return obj;
      });
    }
    
    // If the response has a 'result' field, parse that
    if (responseData.result) {
      return parseResponseData(responseData.result);
    }
    
    return [];
  };

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Document Type Distribution</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-[300px]">
              <p>Loading data...</p>
            </div>
          ) : documentTypeData.length > 0 ? (
            <div className="h-[300px] relative">
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
                    <Tooltip />
                  </PieChart>
                </ChartContainer>
              </Chart>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[300px]">
              <p>No data available</p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Average Confidence by Document Type</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-[300px]">
              <p>Loading data...</p>
            </div>
          ) : confidenceByTypeData.length > 0 ? (
            <div className="h-[300px] relative">
              <Chart className="h-[300px]">
                <ChartContainer>
                  <BarChart data={confidenceByTypeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="confidence" name="Confidence Score">
                      {confidenceByTypeData.map((entry, index) => {
                        // Find the corresponding color from documentTypeData if available
                        const docType = documentTypeData.find(doc => doc.name === entry.type);
                        const color = docType?.color || colors[index % colors.length];
                        return <Cell key={`cell-${index}`} fill={color} />;
                      })}
                    </Bar>
                  </BarChart>
                </ChartContainer>
              </Chart>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[300px]">
              <p>No data available</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

