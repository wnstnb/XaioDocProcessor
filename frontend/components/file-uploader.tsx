"use client"

import type React from "react"

import { useState } from "react"
import { Upload, File, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

export function FileUploader() {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const newFiles = Array.from(e.target.files)
      setFiles((prev) => [...prev, ...newFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const handleUpload = () => {
    if (files.length === 0) return

    setUploading(true)

    // Simulate upload progress
    let currentProgress = 0
    const interval = setInterval(() => {
      currentProgress += 5
      setProgress(currentProgress)

      if (currentProgress >= 100) {
        clearInterval(interval)
        setUploading(false)
        // In a real app, you would process the files here
      }
    }, 200)
  }

  return (
    <div className="space-y-4">
      <div
        className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 p-12 text-center hover:bg-gray-50 dark:border-gray-600 dark:hover:bg-gray-900/50"
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
          <p className="mb-4 text-sm text-muted-foreground">or click to browse (PDF, JPG, PNG)</p>
          <Button
            variant="outline"
            className="relative"
            onClick={() => document.getElementById("file-upload")?.click()}
          >
            Select Files
            <input
              id="file-upload"
              type="file"
              multiple
              accept=".pdf,.jpg,.jpeg,.png"
              className="absolute inset-0 cursor-pointer opacity-0"
              onChange={handleFileChange}
            />
          </Button>
        </div>
      </div>

      {files.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-medium">Selected Files ({files.length})</h4>
          <div className="max-h-60 space-y-2 overflow-y-auto rounded-md border p-2">
            {files.map((file, index) => (
              <div key={index} className="flex items-center justify-between rounded-md bg-secondary p-2">
                <div className="flex items-center">
                  <File className="mr-2 h-4 w-4" />
                  <span className="text-sm">{file.name}</span>
                </div>
                <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => removeFile(index)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>

          {uploading ? (
            <div className="space-y-2">
              <Progress value={progress} />
              <p className="text-xs text-muted-foreground">Uploading... {progress}%</p>
            </div>
          ) : (
            <Button className="w-full" onClick={handleUpload}>
              Upload {files.length} {files.length === 1 ? "File" : "Files"}
            </Button>
          )}
        </div>
      )}
    </div>
  )
}

