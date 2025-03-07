"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Chart, ChartContainer, ChartTooltip, ChartLegend } from "@/components/ui/chart"
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts"
import { METRICS_QUERIES } from "@/app/metrics/page"

// Types for the data
interface ConfidenceDataPoint {
  month: string;
  [key: string]: string | number;
}

interface VolumeDataPoint {
  month: string;
  count: number;
}

interface FieldExtractionDataPoint {
  name: string;
  success: number;
  failure: number;
}

export function MetricsOverview() {
  // State for the data
  const [confidenceData, setConfidenceData] = useState<ConfidenceDataPoint[]>([]);
  const [volumeData, setVolumeData] = useState<VolumeDataPoint[]>([]);
  const [fieldExtractionData, setFieldExtractionData] = useState<FieldExtractionDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Function to fetch data from the backend
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch confidence data
        const confidenceResponse = await fetch('/api/metrics/confidence-by-type-over-time', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.confidenceByTypeOverTimeQuery }),
        });
        
        if (!confidenceResponse.ok) {
          throw new Error('Failed to fetch confidence data');
        }
        
        const responseData = await confidenceResponse.json();
        console.log('Confidence data response:', responseData);
        
        // Parse the response data
        const confidenceRawData = parseResponseData(responseData);
        console.log('Parsed confidence data:', confidenceRawData);
        
        if (confidenceRawData.length > 0) {
          // Transform the data to the format needed by the chart
          // Group by month and create a data point for each document type
          const confidenceByMonth: { [key: string]: ConfidenceDataPoint } = {};
          
          confidenceRawData.forEach((item: any) => {
            if (!confidenceByMonth[item.month]) {
              confidenceByMonth[item.month] = { month: item.month };
            }
            
            // Clean up the page_label to make it a valid property name
            const cleanLabel = item.page_label.replace(/[^a-zA-Z0-9_]/g, '_');
            confidenceByMonth[item.month][cleanLabel] = parseFloat(item.confidence);
          });
          
          const transformedData = Object.values(confidenceByMonth);
          console.log('Transformed confidence data:', transformedData);
          
          setConfidenceData(transformedData);
        } else {
          // Use mock data as fallback
          setConfidenceData([
            { month: "Jan", invoices: 92, receipts: 88, forms: 85 },
            { month: "Feb", invoices: 93, receipts: 87, forms: 86 },
            { month: "Mar", invoices: 91, receipts: 89, forms: 84 },
          ]);
        }
        
        // Fetch volume data
        const volumeResponse = await fetch('/api/metrics/volume-over-time', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.volumeOverTimeQuery }),
        });
        
        if (!volumeResponse.ok) {
          throw new Error('Failed to fetch volume data');
        }
        
        const volumeResponseData = await volumeResponse.json();
        console.log('Volume data response:', volumeResponseData);
        
        // Parse the response data
        const volumeRawData = parseResponseData(volumeResponseData);
        console.log('Parsed volume data:', volumeRawData);
        
        if (volumeRawData.length > 0) {
          // Convert count to number
          const volumeDataWithNumbers = volumeRawData.map((item: any) => ({
            month: item.month,
            count: parseInt(item.count, 10)
          }));
          
          console.log('Transformed volume data:', volumeDataWithNumbers);
          
          setVolumeData(volumeDataWithNumbers);
        } else {
          // Use mock data as fallback
          setVolumeData([
            { month: "Jan", count: 120 },
            { month: "Feb", count: 150 },
            { month: "Mar", count: 180 },
          ]);
        }
        
        // Fetch field extraction data
        const fieldExtractionResponse = await fetch('/api/metrics/field-extraction-success', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.fieldExtractionSuccessQuery }),
        });
        
        if (!fieldExtractionResponse.ok) {
          throw new Error('Failed to fetch field extraction data');
        }
        
        const fieldExtractionResponseData = await fieldExtractionResponse.json();
        console.log('Field extraction data response:', fieldExtractionResponseData);
        
        // Parse the response data
        const fieldExtractionRawData = parseResponseData(fieldExtractionResponseData);
        console.log('Parsed field extraction data:', fieldExtractionRawData);
        
        if (fieldExtractionRawData.length > 0) {
          // Convert success and failure to numbers
          const fieldExtractionDataWithNumbers = fieldExtractionRawData.map((item: any) => ({
            name: item.name,
            success: parseFloat(item.success),
            failure: parseFloat(item.failure)
          }));
          
          console.log('Transformed field extraction data:', fieldExtractionDataWithNumbers);
          
          setFieldExtractionData(fieldExtractionDataWithNumbers);
        } else {
          // Use mock data as fallback
          setFieldExtractionData([
            { name: "Invoice Number", success: 98, failure: 2 },
            { name: "Date", success: 97, failure: 3 },
            { name: "Customer", success: 92, failure: 8 },
          ]);
        }
      } catch (error) {
        console.error('Error fetching metrics data:', error);
        // Use mock data as fallback
        setConfidenceData([
          { month: "Jan", invoices: 92, receipts: 88, forms: 85 },
          { month: "Feb", invoices: 93, receipts: 87, forms: 86 },
          { month: "Mar", invoices: 91, receipts: 89, forms: 84 },
        ]);
        
        setVolumeData([
          { month: "Jan", count: 120 },
          { month: "Feb", count: 150 },
          { month: "Mar", count: 180 },
        ]);
        
        setFieldExtractionData([
          { name: "Invoice Number", success: 98, failure: 2 },
          { name: "Date", success: 97, failure: 3 },
          { name: "Customer", success: 92, failure: 8 },
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
    
    // If the response has a 'result' field, parse that
    if (responseData.result) {
      try {
        // The result is a string with tab-separated values
        const resultStr = responseData.result;
        
        // Split the string by newlines to get rows
        const rows = resultStr.trim().split('\n');
        
        // The first row contains the column headers
        const headerRow = rows[0].trim();
        const headers = headerRow.split(/\s+/);
        
        console.log('Headers:', headers);
        
        // Parse the remaining rows
        const parsedData = rows.slice(1).map((row: string) => {
          const values = row.trim().split(/\s+/);
          const obj: any = {};
          
          headers.forEach((header: string, index: number) => {
            if (index < values.length) {
              obj[header] = values[index];
            }
          });
          
          return obj;
        });
        
        console.log('Parsed data from result string:', parsedData);
        return parsedData;
      } catch (error) {
        console.error('Error parsing result string:', error);
        return [];
      }
    }
    
    // If the response is a string, parse it
    if (typeof responseData === 'string') {
      try {
        // Split the string by newlines to get rows
        const rows = responseData.trim().split('\n');
        
        // The first row contains the column headers
        const headerRow = rows[0].trim();
        const headers = headerRow.split(/\s+/);
        
        console.log('Headers:', headers);
        
        // Parse the remaining rows
        const parsedData = rows.slice(1).map((row: string) => {
          const values = row.trim().split(/\s+/);
          const obj: any = {};
          
          headers.forEach((header: string, index: number) => {
            if (index < values.length) {
              obj[header] = values[index];
            }
          });
          
          return obj;
        });
        
        console.log('Parsed data from string:', parsedData);
        return parsedData;
      } catch (error) {
        console.error('Error parsing string:', error);
        return [];
      }
    }
    
    return [];
  };

  // Get unique document types for the line chart
  const documentTypes = confidenceData.length > 0
    ? Object.keys(confidenceData[0]).filter(key => key !== 'month')
    : [];
  
  console.log('Document types for chart:', documentTypes);
  console.log('Confidence data for chart:', confidenceData);
  console.log('Volume data for chart:', volumeData);
  console.log('Field extraction data for chart:', fieldExtractionData);

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Confidence Scores by Document Type</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-[300px]">
              <p>Loading data...</p>
            </div>
          ) : confidenceData.length > 0 ? (
            <div className="h-[300px] relative">
              <Chart className="h-[300px]">
                <ChartContainer>
                  <LineChart data={confidenceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    {/* Limit to 5 document types to avoid overcrowding */}
                    {documentTypes.slice(0, 5).map((type, index) => {
                      const colors = ["#3b82f6", "#10b981", "#f59e0b", "#6366f1", "#ec4899"];
                      return (
                        <Line 
                          key={type}
                          type="monotone" 
                          dataKey={type} 
                          stroke={colors[index]} 
                          name={type.replace(/_/g, ' ')} 
                          strokeWidth={2} 
                        />
                      );
                    })}
                  </LineChart>
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
          <CardTitle>Document Processing Volume</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-[300px]">
              <p>Loading data...</p>
            </div>
          ) : volumeData.length > 0 ? (
            <div className="h-[300px] relative">
              <Chart className="h-[300px]">
                <ChartContainer>
                  <BarChart data={volumeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#3b82f6" name="Documents" />
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

      <Card className="md:col-span-2">
        <CardHeader>
          <CardTitle>Field Extraction Success Rate</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-[300px]">
              <p>Loading data...</p>
            </div>
          ) : fieldExtractionData.length > 0 ? (
            <div className="h-[300px] relative">
              <Chart className="h-[300px]">
                <ChartContainer>
                  <BarChart data={fieldExtractionData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis dataKey="name" type="category" width={150} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="success" stackId="a" fill="#10b981" name="Success" />
                    <Bar dataKey="failure" stackId="a" fill="#ef4444" name="Failure" />
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

