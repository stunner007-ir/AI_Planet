from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import pdfplumber
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader



# from llama_index import LlamaIndex


app = FastAPI()


# CORS (Cross-Origin Resource Sharing) settings
origins = [
    "http://localhost",
    "http://localhost:5173",  # Update with your React.js frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    # Add "OPTIONS" to allow preflight requests
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Database setup
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://ishuraj:testing321@localhost/pdf_qa_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    content = Column(Text)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class QuestionRequest(BaseModel):
    doc_id: int
    question: str

# Upload and process PDF


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDFs are allowed.")

    content = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            content += page.extract_text()

    document = Document(filename=file.filename, content=content)
    db.add(document)
    db.commit()
    db.refresh(document)

    return {"filename": file.filename, "id": document.id}

# Ask question


@app.post("/ask/")
async def ask_question(doc_id: int = Form(...), question: str = Form(...), db: Session = Depends(get_db)):
    
    document = db.query(Document).filter(Document.id == doc_id).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    documents = SimpleDirectoryReader(document.content).load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine()
    answer = query_engine.query(question)

    return JSONResponse(content={"answer": answer})
