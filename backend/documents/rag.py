from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .models import Document, DocumentChunk
import anthropic
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.chunks = []
        self.chunk_to_doc = {}  # Maps chunk index to document ID
        
        # Initialize FAISS index
        self.index = faiss.IndexFlatL2(384)  # 384 is the dimension of all-MiniLM-L6-v2 embeddings
        
        # Load existing chunks and create index
        self._load_existing_chunks()
        
        # Configure Anthropic
        self.client = anthropic.Anthropic(api_key=os.getenv('OPENAI_API_KEY'))
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY environment variable is not set")

    def _load_existing_chunks(self):
        """Load existing chunks from the database and create FAISS index."""
        chunks = DocumentChunk.objects.all()
        if not chunks:
            return

        # Get all chunk contents and their embeddings
        chunk_contents = [chunk.content for chunk in chunks]
        embeddings = self.model.encode(chunk_contents)
        
        # Store chunks and their document mappings
        self.chunks = chunk_contents
        self.chunk_to_doc = {i: chunk.document.id for i, chunk in enumerate(chunks)}
        
        # Add embeddings to FAISS index
        self.index.add(embeddings)

    def process_document(self, document):
        """Process a document and create chunks with embeddings."""
        content = self._extract_text(document)
        chunks = self._create_chunks(content)
        
        # Create embeddings for chunks
        embeddings = self.model.encode(chunks)
        
        # Store chunks and their embeddings
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_chunk = DocumentChunk.objects.create(
                document=document,
                content=chunk,
                chunk_index=i,
                embedding_id=f"{document.id}_{i}"
            )
            self.chunks.append(chunk)
            self.chunk_to_doc[len(self.chunks) - 1] = document.id

        # Create or update FAISS index
        if self.index is None:
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def _extract_text(self, document):
        """Extract text from different file types."""
        file_path = document.file.path
        file_type = document.file_type.lower()

        if file_type == 'pdf':
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text

        elif file_type == 'docx':
            from docx import Document as DocxDocument
            doc = DocxDocument(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])

        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()

        return ""

    def _create_chunks(self, text, chunk_size=500, overlap=50):
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            
        return chunks

    def answer_question(self, question, top_k=3):
        """Answer a question using the RAG pipeline."""
        if not self.chunks:
            raise ValueError("No documents have been processed yet. Please upload and process some documents first.")
            
        # Get question embedding
        question_embedding = self.model.encode([question])[0]
        
        # Search for relevant chunks
        D, I = self.index.search(np.array([question_embedding]), top_k)
        
        # Check if we got valid results
        if len(I[0]) == 0 or I[0][0] == -1:
            raise ValueError("No relevant chunks found for the question. Try rephrasing or upload more documents.")
        
        # Get relevant chunks and their documents
        relevant_chunks = []
        relevant_docs = []
        for idx in I[0]:
            if idx != -1 and idx < len(self.chunks):  # Check for valid index
                relevant_chunks.append(self.chunks[idx])
                relevant_docs.append(self.chunk_to_doc[idx])
        
        if not relevant_chunks:
            raise ValueError("No relevant content found for the question. Try rephrasing or upload more documents.")
        
        # Create context from chunks
        context = "\n\n".join(relevant_chunks)
        
        # Generate answer using Claude
        try:
            message = self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": f"""Based on the following context, please answer the question. Always cite your sources.

Context:
{context}

Question: {question}

Please provide a clear and concise answer, citing the relevant sources from the context."""
                    }
                ]
            )
            
            answer = message.content[0].text
            
            # Get document titles for citations
            citations = []
            for doc_id in set(relevant_docs):
                doc = Document.objects.get(id=doc_id)
                citations.append(doc.title)
            
            return {
                "answer": answer,
                "citations": citations
            }
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise ValueError(f"Error generating answer: {str(e)}") 