'use client';

import { useState } from 'react';

interface Message {
  type: 'question' | 'answer';
  content: string;
  citations?: string[];
}

export default function QASection() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;

    setError(null);
    setIsLoading(true);
    const currentQuestion = question;
    setQuestion('');

    // Add question to messages
    setMessages(prev => [...prev, { type: 'question', content: currentQuestion }]);

    try {
      const response = await fetch('http://localhost:8000/api/documents/ask_question/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: currentQuestion }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get answer');
      }

      const data = await response.json();
      setMessages(prev => [...prev, {
        type: 'answer',
        content: data.answer,
        citations: data.citations
      }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get answer');
      console.error('Error asking question:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px]">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 px-1">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'question' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`qa-message max-w-[85%] rounded-lg p-3 ${
                message.type === 'question'
                  ? 'bg-gradient-to-r from-pink-500 to-pink-600 text-white'
                  : 'bg-gray-50 text-gray-900 border border-gray-100'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              {message.type === 'answer' && message.citations && message.citations.length > 0 && (
                <div className="mt-2 pt-2 border-t border-gray-200">
                  <p className="text-xs text-gray-500">
                    Sources: {message.citations.join(', ')}
                  </p>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
              <div className="flex space-x-1.5">
                <div className="w-1.5 h-1.5 bg-pink-400 rounded-full animate-bounce" />
                <div className="w-1.5 h-1.5 bg-pink-400 rounded-full animate-bounce delay-100" />
                <div className="w-1.5 h-1.5 bg-pink-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-3 p-2.5 bg-red-50 text-red-600 rounded-lg text-xs border border-red-100">
          {error}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your documents..."
          className="flex-1 text-xs rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="px-3 py-2 bg-gradient-to-r from-pink-500 to-pink-600 text-white text-xs rounded-lg hover:from-pink-600 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-pink-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Ask
        </button>
      </form>
    </div>
  );
} 