"use client"

import { useRef, useState, useEffect } from "react"
import { Upload, File, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

// If you're using shadcn's tab components or Radix UI:
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

// We assume you have a CompactDataTable for displaying pages/extracted/info
import { CompactDataTable } from "@/components/CompactDataTable"
import { HistoryViewer } from "@/components/HistoryViewer"

interface FileUploaderProps {
  onUploadSuccess: (data: any) => void
}

export function FileUploader({ onUploadSuccess }: FileUploaderProps) {
  // --- Upload Tab State ---
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [uploadStatus, setUploadStatus] = useState("")

  // For selecting files from the OS
  const fileInputRef = useRef<HTMLInputElement>(null)

  // --- Processing History Tab State ---
  const [allFiles, setAllFiles] = useState<string[]>([])       // List of filenames from DB
  const [selectedFile, setSelectedFile] = useState<string>("") // Currently chosen file
  const [historyData, setHistoryData] = useState<any>(null)    // Detailed data (pages, extracted, info) for selected file

  // On mount, fetch the list of previously processed files
  useEffect(() => {
    async function fetchFiles() {
      try {
        const res = await fetch("http://localhost:8000/list-files")
        const filenames = await res.json()
        setAllFiles(filenames)
      } catch (error) {
        console.error("Error fetching file list:", error)
      }
    }
    fetchFiles()
  }, [])

  // When user selects a file from the dropdown, fetch the data
  const handleSelectFile = async (filename: string) => {
    setSelectedFile(filename)
    if (!filename) {
      setHistoryData(null)
      return
    }

    try {
      const res = await fetch(`http://localhost:8000/get-file?filename=${encodeURIComponent(filename)}`)
      if (!res.ok) {
        throw new Error("Failed to fetch file data")
      }
      const data = await res.json()
      setHistoryData(data)
    } catch (error) {
      console.error("Error fetching file data:", error)
    }
  }

  // Upload logic
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setFiles((prev) => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setUploading(true)
    setProgress(0)
    setUploadStatus("")

    const formData = new FormData()
    formData.append("file", files[0])

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error("Upload failed")
      }

      const data = await response.json()
      console.log("Data from backend:", data)
      setProgress(100)
      setUploadStatus(`Success: ${data.message}`)
      onUploadSuccess(data)
      setFiles([])
    } catch (error: any) {
      console.error("Error during upload:", error)
      setUploadStatus(`Error: ${error.message}`)
    } finally {
      setUploading(false)
    }
  }

  const triggerFileInput = () => {
    fileInputRef.current?.click()
  }

  return (
    <Tabs defaultValue="upload" className="w-full">
      {/* Tab triggers */}
      <TabsList className="grid w-full max-w-md grid-cols-2">
        <TabsTrigger value="upload">Upload</TabsTrigger>
        <TabsTrigger value="history">Processing History</TabsTrigger>
      </TabsList>

      {/* --- Tab Content 1: Upload --- */}
      <TabsContent value="upload" className="mt-6">
        <div className="space-y-4">
          <div
            className="flex flex-col items-center justify-center
                       rounded-lg border border-dashed border-gray-300
                       p-4 text-center hover:bg-gray-50
                       dark:border-gray-600 dark:hover:bg-gray-900/50"
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault()
              if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
                const newFiles = Array.from(e.dataTransfer.files)
                setFiles((prev) => [...prev, ...newFiles])
              }
            }}
          >
            <div className="flex flex-col items-center justify-center">
              <Upload className="mb-4 h-10 w-10 text-muted-foreground" />
              <h3 className="mb-2 text-lg font-semibold">Drag and drop files</h3>
              <p className="mb-4 text-sm text-muted-foreground">
                or click to browse (PDF, JPG, PNG)
              </p>
              <Button variant="outline" onClick={triggerFileInput}>
                Select Files
              </Button>
              <input
                ref={fileInputRef}
                id="file-upload"
                type="file"
                multiple
                accept=".pdf,.jpg,.jpeg,.png"
                className="sr-only"
                onChange={handleFileChange}
              />
            </div>
          </div>

          {files.length > 0 && (
            <div className="space-y-4">
              <h4 className="font-medium">Selected Files ({files.length})</h4>
              <div className="max-h-60 space-y-2 overflow-y-auto rounded-md border p-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between
                               rounded-md bg-secondary p-2"
                  >
                    <div className="flex items-center">
                      <File className="mr-2 h-4 w-4" />
                      <span className="text-sm">{file.name}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6"
                      onClick={() => removeFile(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>

              {uploading ? (
                <div className="space-y-2">
                  <Progress value={progress} />
                  <p className="text-xs text-muted-foreground">
                    Uploading... {progress}%
                  </p>
                </div>
              ) : (
                <Button className="w-full" onClick={handleUpload}>
                  Upload {files.length} {files.length === 1 ? "File" : "Files"}
                </Button>
              )}

              {uploadStatus && <p className="mt-2 text-sm">{uploadStatus}</p>}
            </div>
          )}
        </div>
      </TabsContent>

      {/* --- Tab Content 2: Processing History --- */}
      <TabsContent value="history" className="mt-6">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Previously Processed Files</h3>

          {/* File selection dropdown */}
          {allFiles.length > 0 ? (
            <div className="mb-4">
              <label htmlFor="history-file-select" className="mr-2 font-medium">
                Select a File:
              </label>
              <select
                id="history-file-select"
                className="border rounded p-1"
                value={selectedFile}
                onChange={(e) => handleSelectFile(e.target.value)}
              >
                <option value="">-- Choose a File --</option>
                {allFiles.map((fname) => (
                  <option key={fname} value={fname}>
                    {fname}
                  </option>
                ))}
              </select>
            </div>
          ) : (
            <p>No files found in the database.</p>
          )}

          {/* Display data for the chosen file */}
          {historyData && (
            <HistoryViewer historyData={historyData} />
          )}
        </div>
      </TabsContent>

    </Tabs>
  )
}
