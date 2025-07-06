from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Document, DocumentChunk
from .serializers import DocumentSerializer, DocumentChunkSerializer
import os
from PyPDF2 import PdfReader
from docx import Document as DocxDocument
import mimetypes
from rest_framework.decorators import action
from .rag import RAGPipeline
import logging

logger = logging.getLogger(__name__)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def create(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file')
            logger.info(f"Received request with files: {request.FILES}")
            logger.info(f"Request content type: {request.content_type}")
            
            if not file:
                logger.error("No file provided in request")
                return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

            logger.info(f"Processing file upload: {file.name} (size: {file.size} bytes)")

            # Get file type using mimetypes
            try:
                file_type = mimetypes.guess_type(file.name)[0]
                if not file_type:
                    file_type = file.content_type
                logger.info(f"Detected file type: {file_type}")
            except Exception as e:
                logger.error(f"Error detecting file type: {str(e)}")
                return Response({'error': 'Error detecting file type'}, status=status.HTTP_400_BAD_REQUEST)

            # Extract title from filename
            title = os.path.splitext(file.name)[0]

            # Count pages based on file type
            page_count = 0
            try:
                if file_type == 'application/pdf':
                    pdf = PdfReader(file)
                    page_count = len(pdf.pages)
                    file.seek(0)  # Reset file pointer
                elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    doc = DocxDocument(file)
                    page_count = len(doc.sections)  # Approximate page count
                    file.seek(0)  # Reset file pointer
                elif file_type == 'text/plain':
                    page_count = 1  # Text files are treated as single page
                else:
                    return Response({'error': f'Unsupported file type: {file_type}'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                return Response({'error': 'Error processing file'}, status=status.HTTP_400_BAD_REQUEST)

            # Create document
            try:
                document = Document.objects.create(
                    title=title,
                    file=file,
                    file_type=file_type.split('/')[-1].upper(),
                    page_count=page_count
                )
                logger.info(f"Document created successfully: {document.id}")
            except Exception as e:
                logger.error(f"Error creating document: {str(e)}")
                return Response({'error': 'Error creating document'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = self.get_serializer(document)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Unexpected error in document upload: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def ask_question(self, request):
        """Ask a question about the documents."""
        try:
            question = request.data.get('question')
            if not question:
                return Response({'error': 'Question is required'}, status=400)

            # Initialize RAG pipeline
            try:
                rag = RAGPipeline()
            except ValueError as e:
                return Response({'error': str(e)}, status=400)
            except Exception as e:
                logger.error(f"Error initializing RAG pipeline: {str(e)}")
                return Response({'error': f'Error initializing RAG pipeline: {str(e)}'}, status=500)

            # Get answer
            try:
                result = rag.answer_question(question)
                return Response(result)
            except ValueError as e:
                return Response({'error': str(e)}, status=400)
            except Exception as e:
                logger.error(f"Error getting answer: {str(e)}")
                return Response({'error': f'Error getting answer: {str(e)}'}, status=500)

        except Exception as e:
            logger.error(f"Unexpected error in ask_question: {str(e)}")
            return Response({'error': f'Unexpected error: {str(e)}'}, status=500)
