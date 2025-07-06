'use client';

import { useEffect, useState } from 'react';
import { DocumentIcon, TrashIcon } from '@heroicons/react/24/outline';

interface Document {
  id: string;
  title: string;
  file_type: string;
  page_count: number;
  created_at: string;
}

interface DocumentListProps {
  documents: Document[];
}

export default function DocumentList({ documents }: DocumentListProps) {
  if (documents.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-xs text-gray-500">No documents uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="document-card group bg-white border border-gray-100 rounded-lg p-2.5 hover:shadow-md transition-all duration-200 hover:border-purple-100"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <h3 className="text-xs font-medium text-gray-900 truncate group-hover:text-purple-600 transition-colors">
                {doc.title}
              </h3>
              <div className="mt-1 flex items-center text-[10px] text-gray-500">
                <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-purple-50 text-purple-700 mr-1.5">
                  {doc.file_type}
                </span>
                <span>{doc.page_count} pages</span>
                <span className="mx-1.5">•</span>
                <span>
                  {new Date(doc.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
} 