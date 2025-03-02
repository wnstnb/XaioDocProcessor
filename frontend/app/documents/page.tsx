"use client"
import { useState, useMemo } from "react"
import { FileUploader } from "@/components/file-uploader"
import { CompactDataTable } from "@/components/CompactDataTable"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { exportToCsv } from "@/components/exportCsv" // adjust the import path as needed
import { Button } from "@/components/ui/button" // adjust the import path as needed


export default function DocumentsPage() {
  const [processedData, setProcessedData] = useState<{
    pages: { page_num: number; page_number: number; s3_url: string }[];
    extracted: any[];
    info: any[];
    message: string;
    filename: string;
  } | null>(null);

  const [currentPage, setCurrentPage] = useState<number>(1);

  const handleUploadSuccess = (data: any) => {
    console.log("Upload success callback data:", data);
    setProcessedData(data);
    setCurrentPage(1);
  };

  // Unique page numbers from extracted
  const pageNumbers = useMemo(() => {
    if (!processedData || !processedData.extracted) return [];
    const pages = processedData.extracted.map((item) => item.page_num);
    return Array.from(new Set(pages)).sort((a, b) => a - b);
  }, [processedData]);

  // Filter extracted by current page
  const currentExtracted = useMemo(() => {
    if (!processedData || !processedData.extracted) return [];
    return processedData.extracted.filter(
      (item) => item.page_num === currentPage
    );
  }, [processedData, currentPage]);

  // Get image for the current page
  const currentPageImage = useMemo(() => {
    if (!processedData || !processedData.pages) return null;
    const pageObj = processedData.pages.find(
      (p) => p.page_number === currentPage
    );
    return pageObj ? pageObj.s3_url : null;
  }, [processedData, currentPage]);

  return (
    <div className="container py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Document Processing</h1>
        <p className="text-muted-foreground">
          Upload documents to extract structured data using AI
        </p>
      </div>

      <FileUploader onUploadSuccess={handleUploadSuccess} />

      {processedData && (
        <div className="mt-6">
          <h2 className="text-2xl font-bold">
            Processed Data for {processedData.filename}
          </h2>

          {/* Page selection dropdown */}
          {pageNumbers.length > 0 && (
            <div className="my-4">
              <label htmlFor="page-select" className="mr-2 font-medium">
                Select Page:
              </label>
              <select
                id="page-select"
                value={currentPage}
                onChange={(e) => setCurrentPage(Number(e.target.value))}
                className="border rounded p-1"
              >
                {pageNumbers.map((pageNum) => {
                  // Find the first row in extracted with this pageNum to get its label
                  const matchingRow = processedData.extracted.find(
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
            {/* Left: image display */}
            <div className="md:w-1/2">
              {currentPageImage ? (
                <img
                  src={currentPageImage}
                  alt={`Page ${currentPage}`}
                  className="w-full object-contain rounded shadow"
                />
              ) : (
                <p>No image available for this page.</p>
              )}
            </div>

            {/* Right: extracted fields table */}
            <div className="md:w-1/2">
            <div className="flex items-center justify-between mb-2">
            <h2 className="mr-2 font-medium">
              Extracted Fields - Page {currentPage}
            </h2>
              {/* <div className="sticky top-0 bg-gray-50 p-2 rounded shadow"> */}
                      <Button
                        onClick={() =>
                          exportToCsv(
                            `${processedData.filename}-page-${currentPage}.csv`,
                            currentExtracted
                          )
                        }
                        className="mb-2"
                      >
                        Export CSV
                      </Button>
                </div>
              <div className="sticky top-16 overflow-y-auto border rounded">
              <CompactDataTable
                data={currentExtracted}
                // title={`Extracted Fields - Page ${currentPage}`}
              />
                </div>
              </div>
            </div>
          </div>
        // </div>
      )}
    </div>
  );
}
