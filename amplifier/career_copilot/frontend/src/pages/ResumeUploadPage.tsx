import React, { useState } from 'react'
import toast from 'react-hot-toast'
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

const ResumeUploadPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<any>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (file: File) => {
    const allowedTypes = ['.pdf', '.docx', '.txt', '.json', '.md']
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()

    if (!allowedTypes.includes(fileExtension || '')) {
      toast.error('Please upload a PDF, DOCX, TXT, JSON, or Markdown file')
      return
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast.error('File size must be less than 10MB')
      return
    }

    setSelectedFile(file)
    setUploadResult(null)
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file to upload')
      return
    }

    setIsUploading(true)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch('/api/v1/resume/upload', {
        method: 'POST',
        body: formData,
      })

      const result = await response.json()

      if (result.success) {
        setUploadResult(result.data)
        toast.success('Resume uploaded and parsed successfully!')
      } else {
        toast.error(result.message || 'Failed to upload resume')
      }
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Failed to upload resume. Please try again.')
    } finally {
      setIsUploading(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload Resume</h1>
        <p className="mt-2 text-gray-600">
          Upload your resume to get AI-powered analysis and structured data extraction.
        </p>
      </div>

      {!uploadResult ? (
        <div className="space-y-6">
          {/* Upload Area */}
          <div
            className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-colors duration-200 ${
              dragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.json,.md"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              disabled={isUploading}
            />

            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4">
              <p className="text-lg font-medium text-gray-900">
                Drop your resume here, or click to browse
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Supports PDF, DOCX, TXT, JSON, and Markdown files up to 10MB
              </p>
            </div>
          </div>

          {/* Selected File */}
          {selectedFile && (
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <DocumentTextIcon className="h-8 w-8 text-gray-400" />
                  <div>
                    <p className="font-medium text-gray-900">{selectedFile.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => {
                    setSelectedFile(null)
                    setUploadResult(null)
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <ExclamationTriangleIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <div className="flex justify-center">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className="btn btn-primary btn-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isUploading ? 'Uploading...' : 'Upload Resume'}
            </button>
          </div>

          {/* File Format Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Supported File Formats</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• PDF (.pdf) - Most common resume format</li>
              <li>• Microsoft Word (.docx) - Direct parsing support</li>
              <li>• Plain Text (.txt) - Simple text files</li>
              <li>• JSON (.json) - Structured resume data</li>
              <li>• Markdown (.md) - Formatted text files</li>
            </ul>
          </div>
        </div>
      ) : (
        /* Upload Results */
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-green-900 mb-4">
              Resume Successfully Parsed!
            </h3>

            <div className="space-y-4">
              {/* Personal Info */}
              {uploadResult.personal_info && Object.keys(uploadResult.personal_info).length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Personal Information</h4>
                  <div className="bg-white rounded border border-gray-200 p-3">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      {uploadResult.personal_info.name && (
                        <div><strong>Name:</strong> {uploadResult.personal_info.name}</div>
                      )}
                      {uploadResult.personal_info.email && (
                        <div><strong>Email:</strong> {uploadResult.personal_info.email}</div>
                      )}
                      {uploadResult.personal_info.phone && (
                        <div><strong>Phone:</strong> {uploadResult.personal_info.phone}</div>
                      )}
                      {uploadResult.personal_info.location && (
                        <div><strong>Location:</strong> {uploadResult.personal_info.location}</div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Summary */}
              {uploadResult.summary && (
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Professional Summary</h4>
                  <div className="bg-white rounded border border-gray-200 p-3">
                    <p className="text-sm text-gray-700">{uploadResult.summary}</p>
                  </div>
                </div>
              )}

              {/* Experience Count */}
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-white rounded border border-gray-200 p-3 text-center">
                  <div className="text-2xl font-bold text-primary-600">
                    {uploadResult.work_experience?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Work Experience</div>
                </div>
                <div className="bg-white rounded border border-gray-200 p-3 text-center">
                  <div className="text-2xl font-bold text-primary-600">
                    {uploadResult.skills?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Skills</div>
                </div>
                <div className="bg-white rounded border border-gray-200 p-3 text-center">
                  <div className="text-2xl font-bold text-primary-600">
                    {uploadResult.education?.length || 0}
                  </div>
                  <div className="text-sm text-gray-600">Education</div>
                </div>
              </div>
            </div>

            <div className="flex justify-center space-x-4">
              <button
                onClick={() => {
                  setUploadResult(null)
                  setSelectedFile(null)
                }}
                className="btn btn-outline"
              >
                Upload Another Resume
              </button>
              <button
                onClick={() => {
                  // Navigate to profile page with the resume data
                  window.location.href = '/profile'
                }}
                className="btn btn-primary"
              >
                View My Profile
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ResumeUploadPage