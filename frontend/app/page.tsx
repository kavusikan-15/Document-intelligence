'use client';

import { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import DocumentList from './components/DocumentList';
import QASection from './components/QASection';

interface Document {
  id: string;
  title: string;
  file_type: string;
  page_count: number;
  created_at: string;
}

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleDocumentUpload = async (file: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/documents/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to upload document');
      }

      const data = await response.json();
      setDocuments([...documents, data]);
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Error uploading document: ' + error.message);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2 gradient-text">
            Document Intelligence
          </h1>
          <p className="text-sm text-gray-600">
            Upload documents and ask questions about their content
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Upload Document Section */}
          <div className="glass-effect rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-all duration-200">
            <h2 className="text-base font-semibold text-center text-blue-600 mb-3">
              Upload Document
            </h2>
            <div className="upload-section">
              <DocumentUpload onUpload={handleDocumentUpload} isUploading={isUploading} />
            </div>
          </div>

          {/* Your Documents Section */}
          <div className="glass-effect rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-all duration-200">
            <h2 className="text-base font-semibold text-center text-purple-600 mb-3">
              Your Documents
            </h2>
            <DocumentList documents={documents} />
          </div>

          {/* Q&A Section */}
          <div className="glass-effect rounded-xl shadow-sm border border-gray-100 p-4 hover:shadow-md transition-all duration-200">
            <h2 className="text-base font-semibold text-center text-pink-600 mb-3">
              Ask Questions
            </h2>
            <QASection />
          </div>
        </div>
      </div>
    </main>
  );
} 