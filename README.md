# Document Intelligence Platform

A full-stack web application that allows users to upload documents, ask questions, and receive AI-powered answers using RAG (Retrieval Augmented Generation).

## Features

- Document upload support (TXT, PDF, DOCX)
- Natural language question answering
- RAG-based contextual responses
- Document management dashboard
- Interactive Q&A interface

## Tech Stack

### Backend
- Django & Django REST Framework
- MySQL Database
- FAISS/ChromaDB for vector storage
- Sentence Transformers for embeddings
- OpenAI/Claude for answer generation

### Frontend
- React/Next.js
- Tailwind CSS
- Axios for API calls

## Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with:
```
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost:3306/doc_intelligence
OPENAI_API_KEY=your-openai-api-key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

## Project Structure

```
document-intelligence/
├── backend/
│   ├── doc_intelligence/
│   │   ├── api/
│   │   ├── documents/
│   │   ├── rag/
│   │   └── manage.py
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
└── README.md
```

## API Endpoints

- `POST /api/documents/upload/` - Upload a document
- `GET /api/documents/` - List all documents
- `POST /api/qa/ask/` - Ask a question about a document

## License

MIT 