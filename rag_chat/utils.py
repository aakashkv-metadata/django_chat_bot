import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from django.conf import settings
import requests
from dotenv import load_dotenv
from chromadb.utils import embedding_functions

load_dotenv()

# --- Custom Embedding Adapter for Memory Efficiency ---
# We use Chroma's default ONNX-based embedding (all-MiniLM-L6-v2) 
# instead of 'sentence-transformers' (PyTorch) to avoid OOM on Render free tier.

class ChromaEmbeddingAdapter:
    def __init__(self):
        self.ef = embedding_functions.DefaultEmbeddingFunction()

    def embed_documents(self, texts):
        return self.ef(texts)

    def embed_query(self, text):
        return self.ef([text])[0]

# Initialize Embeddings
embedding_function = ChromaEmbeddingAdapter()

# Initialize ChromaDB
PERSIST_DIRECTORY = os.path.join(settings.BASE_DIR, 'chroma_db')

def get_db():
    return Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embedding_function
    )

def ingest_document(file_path):
    """
    Loads, splits, and embeds a PDF document into ChromaDB.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    db = get_db()
    db.add_documents(texts)
    # db.persist() is automatic in newer Chroma versions
    return True

def query_perplexity(query, context):
    """
    Queries Perplexity API with the user query and retrieved context.
    """
    api_key = os.getenv("PPLX_API_KEY")
    if not api_key:
        return "Error: Perplexity API Key is missing."
        
    url = "https://api.perplexity.ai/chat/completions"
    
    messages = [
        {
            "role": "system",
            "content": "You are Lumina, a helpful AI assistant. Answer the user's question based on the provided context. If the answer is not in the context, say so politely."
        },
        {
            "role": "user", 
            "content": f"Context:\n{context}\n\nQuestion: {query}"
        }
    ]
    
    payload = {
        "model": "sonar", # Use a valid perplexity model
        "messages": messages,
        "temperature": 0.1
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
             error_msg += f" Response: {e.response.text}"
        return f"Error contacting AI: {error_msg}"

def get_answer(query):
    """
    Retrieves context from VectorDB and gets answer from Perplexity.
    """
    db = get_db()
    # Retrieve top 3 chunks
    docs = db.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    return query_perplexity(query, context)
