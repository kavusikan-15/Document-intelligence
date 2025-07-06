from django.db import models
import uuid

# Create your models here.

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    file_type = models.CharField(max_length=10)  # PDF, DOCX, TXT
    page_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class DocumentChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    page_number = models.IntegerField(null=True, blank=True)  # Make page_number optional
    chunk_index = models.IntegerField()
    embedding_id = models.CharField(max_length=255, unique=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.embedding_id:
            self.embedding_id = f"{self.document.id}_{self.chunk_index}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
