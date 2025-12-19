from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

def process_document(path):
    # 1. Load the file
    loader = PyPDFLoader(path)
    # 2. Split into small chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.load_and_split()
    # 3. turn chunks to embeddings
    return chunks