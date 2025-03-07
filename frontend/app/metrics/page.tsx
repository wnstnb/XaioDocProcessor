"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { MetricsOverview } from "@/components/metrics-overview"
import { DocumentTypeMetrics } from "@/components/document-type-metrics"
import { ProcessingTimeMetrics } from "@/components/processing-time-metrics"

// SQL Queries for metrics
export const METRICS_QUERIES = {
  // Total Documents Processed with percentage change from last month
  totalDocumentsQuery: `
    WITH current_month AS (
      SELECT COUNT(DISTINCT filename) as count
      FROM pages
      WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
    ),
    previous_month AS (
      SELECT COUNT(DISTINCT filename) as count
      FROM pages
      WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
        AND created_at < DATE_TRUNC('month', CURRENT_DATE)
    ),
    total AS (
      SELECT COUNT(DISTINCT filename) as count
      FROM pages
    )
    SELECT 
      t.count as total,
      c.count as current_month,
      p.count as previous_month,
      CASE 
        WHEN p.count = 0 THEN 100
        ELSE ROUND(((c.count::numeric - p.count::numeric) / p.count::numeric) * 100, 1)
      END as percentage_change
    FROM total t, current_month c, previous_month p
  `,

  // Average Confidence Score with percentage change from last month
  avgConfidenceQuery: `
    WITH current_month AS (
      SELECT AVG(page_confidence) as avg_confidence
      FROM pages
      WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
    ),
    previous_month AS (
      SELECT AVG(page_confidence) as avg_confidence
      FROM pages
      WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
        AND created_at < DATE_TRUNC('month', CURRENT_DATE)
    ),
    total AS (
      SELECT AVG(page_confidence) as avg_confidence
      FROM pages
    )
    SELECT 
      ROUND(t.avg_confidence::numeric * 100, 1) as total,
      ROUND(c.avg_confidence::numeric * 100, 1) as current_month,
      ROUND(p.avg_confidence::numeric * 100, 1) as previous_month,
      CASE 
        WHEN p.avg_confidence = 0 THEN 0
        ELSE ROUND(((c.avg_confidence::numeric - p.avg_confidence::numeric) / p.avg_confidence::numeric) * 100, 1)
      END as percentage_change
    FROM total t, current_month c, previous_month p
  `,

  // Average Processing Time with change from last month
  avgProcessingTimeQuery: `
    WITH current_month AS (
      SELECT AVG(processing_time) as avg_time
      FROM pages
      WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
    ),
    previous_month AS (
      SELECT AVG(processing_time) as avg_time
      FROM pages
      WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
        AND created_at < DATE_TRUNC('month', CURRENT_DATE)
    ),
    total AS (
      SELECT AVG(processing_time) as avg_time
      FROM pages
    )
    SELECT 
      ROUND(t.avg_time::numeric, 1) as total,
      ROUND(c.avg_time::numeric, 1) as current_month,
      ROUND(p.avg_time::numeric, 1) as previous_month,
      ROUND((c.avg_time::numeric - p.avg_time::numeric), 1) as time_change
    FROM total t, current_month c, previous_month p
  `,

  // Confidence Scores by Document Type over time (for MetricsOverview)
  confidenceByTypeOverTimeQuery: `
    SELECT 
      TO_CHAR(DATE_TRUNC('month', created_at), 'Mon') as month,
      page_label,
      ROUND(AVG(page_confidence::numeric) * 100, 1) as confidence
    FROM pages
    WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY DATE_TRUNC('month', created_at), page_label
    ORDER BY DATE_TRUNC('month', created_at), page_label
  `,

  // Document Processing Volume over time (for MetricsOverview)
  volumeOverTimeQuery: `
    SELECT 
      TO_CHAR(DATE_TRUNC('month', created_at), 'Mon') as month,
      COUNT(DISTINCT filename) as count
    FROM pages
    WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
    GROUP BY DATE_TRUNC('month', created_at)
    ORDER BY DATE_TRUNC('month', created_at)
  `,

  // Field Extraction Success Rate (for MetricsOverview)
  fieldExtractionSuccessQuery: `
    WITH extraction_attempts AS (
      SELECT 
        key,
        COUNT(*) as total_attempts,
        COUNT(CASE WHEN value IS NOT NULL AND value != '' THEN 1 END) as successful_extractions
      FROM extracted2
      GROUP BY key
      ORDER BY total_attempts DESC
      LIMIT 6
    )
    SELECT 
      key as name,
      ROUND((successful_extractions::numeric / total_attempts) * 100, 1) as success,
      ROUND(((total_attempts::numeric - successful_extractions::numeric) / total_attempts) * 100, 1) as failure
    FROM extraction_attempts
  `,

  // Document Type Distribution (for DocumentTypeMetrics)
  documentTypeDistributionQuery: `
    SELECT 
      page_label as name,
      COUNT(*) as value
    FROM pages
    GROUP BY page_label
    ORDER BY value DESC
  `,

  // Average Confidence by Document Type (for DocumentTypeMetrics)
  confidenceByTypeQuery: `
    SELECT 
      page_label as type,
      ROUND(AVG(page_confidence::numeric) * 100, 1) as confidence
    FROM pages
    GROUP BY page_label
    ORDER BY confidence DESC
  `,

  // Processing Time Trend (for ProcessingTimeMetrics)
  processingTimeTrendQuery: `
    SELECT 
      TO_CHAR(created_at, 'YYYY-MM-DD') as date,
      ROUND(AVG(processing_time::numeric), 1) as time
    FROM pages
    WHERE created_at >= CURRENT_DATE - INTERVAL '14 days'
    GROUP BY TO_CHAR(created_at, 'YYYY-MM-DD')
    ORDER BY date
  `,

  // Processing Time by Document Type and Page Count (for ProcessingTimeMetrics)
  processingTimeByTypeAndPagesQuery: `
    SELECT 
      page_label as type,
      ROUND(AVG(CASE WHEN page_number = 1 THEN processing_time::numeric END), 1) as pages1,
      ROUND(AVG(CASE WHEN page_number = 2 THEN processing_time::numeric END), 1) as pages2,
      ROUND(AVG(CASE WHEN page_number >= 3 THEN processing_time::numeric END), 1) as pages3Plus
    FROM pages
    GROUP BY page_label
  `
};

// Types for the summary metrics
interface TotalDocumentsData {
  total: number;
  percentage_change: number;
}

interface AvgConfidenceData {
  total: number;
  percentage_change: number;
}

interface AvgProcessingTimeData {
  total: number;
  time_change: number;
}

export default function MetricsPage() {
  // State for the summary metrics
  const [totalDocuments, setTotalDocuments] = useState<TotalDocumentsData | null>(null);
  const [avgConfidence, setAvgConfidence] = useState<AvgConfidenceData | null>(null);
  const [avgProcessingTime, setAvgProcessingTime] = useState<AvgProcessingTimeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Function to fetch summary metrics
    const fetchSummaryMetrics = async () => {
      try {
        setLoading(true);
        
        // Fetch total documents data
        const totalDocumentsResponse = await fetch('/api/metrics/total-documents', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.totalDocumentsQuery }),
        });
        
        if (!totalDocumentsResponse.ok) {
          throw new Error('Failed to fetch total documents data');
        }
        
        const totalDocumentsData = await totalDocumentsResponse.json();
        console.log('Total documents data:', totalDocumentsData);
        
        // Parse the response data
        const parsedTotalDocuments = parseResponseData(totalDocumentsData);
        console.log('Parsed total documents data:', parsedTotalDocuments);
        
        if (parsedTotalDocuments.length > 0) {
          setTotalDocuments({
            total: parseInt(parsedTotalDocuments[0].total, 10),
            percentage_change: parseFloat(parsedTotalDocuments[0].percentage_change)
          });
        } else {
          // Use mock data as fallback
          setTotalDocuments({ total: 1284, percentage_change: 24 });
        }
        
        // Fetch average confidence data
        const avgConfidenceResponse = await fetch('/api/metrics/avg-confidence', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.avgConfidenceQuery }),
        });
        
        if (!avgConfidenceResponse.ok) {
          throw new Error('Failed to fetch average confidence data');
        }
        
        const avgConfidenceData = await avgConfidenceResponse.json();
        console.log('Average confidence data:', avgConfidenceData);
        
        // Parse the response data
        const parsedAvgConfidence = parseResponseData(avgConfidenceData);
        console.log('Parsed average confidence data:', parsedAvgConfidence);
        
        if (parsedAvgConfidence.length > 0) {
          setAvgConfidence({
            total: parseFloat(parsedAvgConfidence[0].total),
            percentage_change: parseFloat(parsedAvgConfidence[0].percentage_change)
          });
        } else {
          // Use mock data as fallback
          setAvgConfidence({ total: 89.7, percentage_change: 2.3 });
        }
        
        // Fetch average processing time data
        const avgProcessingTimeResponse = await fetch('/api/metrics/avg-processing-time', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ query: METRICS_QUERIES.avgProcessingTimeQuery }),
        });
        
        if (!avgProcessingTimeResponse.ok) {
          throw new Error('Failed to fetch average processing time data');
        }
        
        const avgProcessingTimeData = await avgProcessingTimeResponse.json();
        console.log('Average processing time data:', avgProcessingTimeData);
        
        // Parse the response data
        const parsedAvgProcessingTime = parseResponseData(avgProcessingTimeData);
        console.log('Parsed average processing time data:', parsedAvgProcessingTime);
        
        if (parsedAvgProcessingTime.length > 0) {
          setAvgProcessingTime({
            total: parseFloat(parsedAvgProcessingTime[0].total),
            time_change: parseFloat(parsedAvgProcessingTime[0].time_change)
          });
        } else {
          // Use mock data as fallback
          setAvgProcessingTime({ total: 1.8, time_change: -0.3 });
        }
      } catch (error) {
        console.error('Error fetching summary metrics:', error);
        // Use mock data as fallback
        setTotalDocuments({ total: 1284, percentage_change: 24 });
        setAvgConfidence({ total: 89.7, percentage_change: 2.3 });
        setAvgProcessingTime({ total: 1.8, time_change: -0.3 });
      } finally {
        setLoading(false);
      }
    };
    
    fetchSummaryMetrics();
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

  // Format the percentage change with a + or - sign
  const formatPercentageChange = (value: number) => {
    return value > 0 ? `+${value}` : value;
  };

  // Format the time change with a + or - sign
  const formatTimeChange = (value: number) => {
    return value > 0 ? `+${value}` : value;
  };

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
            {loading ? (
              <div className="animate-pulse">
                <div className="h-6 w-20 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 w-32 bg-gray-200 rounded"></div>
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{totalDocuments?.total.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  {formatPercentageChange(totalDocuments?.percentage_change || 0)}% from last month
                </p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Confidence Score</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="animate-pulse">
                <div className="h-6 w-20 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 w-32 bg-gray-200 rounded"></div>
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{avgConfidence?.total}%</div>
                <p className="text-xs text-muted-foreground">
                  {formatPercentageChange(avgConfidence?.percentage_change || 0)}% from last month
                </p>
              </>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Processing Time</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="animate-pulse">
                <div className="h-6 w-20 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 w-32 bg-gray-200 rounded"></div>
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold">{avgProcessingTime?.total}s</div>
                <p className="text-xs text-muted-foreground">
                  {formatTimeChange(avgProcessingTime?.time_change || 0)}s from last month
                </p>
              </>
            )}
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

