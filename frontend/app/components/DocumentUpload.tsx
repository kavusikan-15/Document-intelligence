'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface DocumentUploadProps {
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
}

export default function DocumentUpload({ onUpload, isUploading }: DocumentUploadProps) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setError(null);
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    if (!file.type.match(/^(application\/pdf|application\/vnd\.openxmlformats-officedocument\.wordprocessingml\.document|text\/plain)$/)) {
      setError('Please upload a PDF, DOCX, or TXT file');
      return;
    }

    try {
      await onUpload(file);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload file');
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt']
    },
    maxFiles: 1,
    disabled: isUploading
  });

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-all duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50 scale-[1.02]' 
            : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
          }
          ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <div className="space-y-1.5">
          <svg
            className={`mx-auto h-8 w-8 ${isDragActive ? 'text-blue-500' : 'text-gray-400'}`}
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <div className="text-xs text-gray-600">
            {isUploading ? (
              <span className="text-blue-600">Uploading...</span>
            ) : isDragActive ? (
              <span className="text-blue-600 font-medium">Drop the file here</span>
            ) : (
              <span>
                Drag and drop a file here, or click to select
                <br />
                <span className="text-[10px] text-gray-500 mt-0.5 inline-block">
                  (PDF, DOCX, or TXT files only)
                </span>
              </span>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="text-xs text-red-600 bg-red-50 p-2 rounded-md border border-red-100">
          {error}
        </div>
      )}
    </div>
  );
} 