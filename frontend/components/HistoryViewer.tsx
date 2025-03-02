"use client"

import { useState, useMemo } from "react"
import { CompactDataTable } from "@/components/CompactDataTable"
import { Button } from "@/components/ui/button" // adjust the import path as needed
import { exportToCsv } from "@/components/exportCsv" // adjust the import path as needed


interface HistoryViewerProps {
  historyData: {
    filename: string
    pages: Array<{ page_num?: number; page_number?: number; s3_url: string }>
    extracted: any[]
    info: any[]
  }
}

export function HistoryViewer({ historyData }: HistoryViewerProps) {
  const [historyCurrentPage, setHistoryCurrentPage] = useState<number>(1)

  // Compute available page numbers from extracted data
  const historyPageNumbers = useMemo(() => {
    if (!historyData.extracted) return []
    const pages = historyData.extracted.map(
      (item) => item.page_num ?? item.page_number
    )
    return Array.from(new Set(pages)).sort((a, b) => a - b)
  }, [historyData])

  // Filter extracted data by the current page
  const historyCurrentExtracted = useMemo(() => {
    if (!historyData.extracted) return []
    return historyData.extracted.filter(
      (item) => (item.page_num ?? item.page_number) === historyCurrentPage
    )
  }, [historyData, historyCurrentPage])

  // Get the image URL for the current page from historyData.pages
  const historyCurrentImage = useMemo(() => {
    if (!historyData.pages) return null
    const pageObj = historyData.pages.find(
      (p) => (p.page_num ?? p.page_number) === historyCurrentPage
    )
    return pageObj ? pageObj.s3_url : null
  }, [historyData, historyCurrentPage])

  return (
    <div className="mt-4 space-y-4">
      {/* Page selector for history */}
      {historyPageNumbers.length > 0 && (
        <div>
          <label htmlFor="history-page-select" className="mr-2 font-medium">
            Select Page:
          </label>
          <select
            id="history-page-select"
            value={historyCurrentPage}
            onChange={(e) => setHistoryCurrentPage(Number(e.target.value))}
            className="border rounded p-1"
          >
            {historyPageNumbers.map((pageNum) => {
                  // Find the first row in extracted with this pageNum to get its label
                  const matchingRow = historyData.extracted.find(
                    (row) => row.page_num === pageNum
                  );
                  const label = matchingRow?.page_label ?? "Unknown";
                  return (
                    <option key={pageNum} value={pageNum}>
                      {`Page ${pageNum} - ${label}`}
                    </option>
                  );
                })}
          </select>
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-6 mt-4">
        {/* Left: Image display */}
        <div className="md:w-1/2">
          {historyCurrentImage ? (
            <img
              src={historyCurrentImage}
              alt={`Page ${historyCurrentPage}`}
              className="w-full object-contain rounded shadow"
            />
          ) : (
            <p>No image available for this page.</p>
          )}
        </div>

        {/* Right: Table for extracted fields */}
        <div className="md:w-1/2">
        <div className="flex items-center justify-between mb-2">
            <h2 className="mr-2 font-medium">
              Extracted Fields - Page {historyCurrentPage}
            </h2>
              {/* <div className="sticky top-0 bg-gray-50 p-2 rounded shadow"> */}
                      <Button
                        onClick={() =>
                          exportToCsv(
                            `${historyData.filename}-page-${historyCurrentPage}.csv`,
                            historyCurrentExtracted
                          )
                        }
                        className="mb-2"
                      >
                        Export CSV
                      </Button>
                </div>
              <div className="sticky top-16 overflow-y-auto border rounded">
          <CompactDataTable
            data={historyCurrentExtracted}
            // title={`Extracted Fields - Page ${historyCurrentPage}`}
          />
          </div>
        </div>
      </div>

      {/* Optionally, display additional info */}
      <CompactDataTable data={historyData.info} title="Additional Info" />
    </div>
  )
}
