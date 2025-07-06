from rest_framework import serializers
from .models import Document, DocumentChunk

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'content', 'page_number', 'chunk_index', 'embedding_id']

class DocumentSerializer(serializers.ModelSerializer):
    chunks = DocumentChunkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'file_type', 'page_count', 'created_at', 'updated_at', 'chunks']
        read_only_fields = ['id', 'created_at', 'updated_at'] 