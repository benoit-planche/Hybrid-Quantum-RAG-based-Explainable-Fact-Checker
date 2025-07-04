import os
from dotenv import load_dotenv
from pinecone import Pinecone
from ollama_config import config
from ollama_utils import OllamaEmbeddings, SimpleTextSplitter
from pdf_loader import PDFDocumentLoader

# Load environment variables
load_dotenv()

# Initialize Pinecone (nouvelle API)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

def load_local_documents(data_dir="/home/moi/Documents/internship/climat-misinformation-detection/rapport"):
    """Load documents from a local directory."""
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
        print("Please add your PDF files to this directory and run again.")
        return []

    documents = PDFDocumentLoader.load_directory(data_dir)
    print(f"Loaded {len(documents)} documents from {data_dir}")
    return documents

def load_web_documents(urls):
    """Load documents from web URLs."""
    # Note: This is a simplified version. In a real implementation,
    # you would need to implement web scraping functionality
    documents = []
    for url in urls:
        # Create a mock document for demonstration
        mock_content = f"Content from {url}. In a real implementation, this would contain the actual web page content."
        documents.append({
            'page_content': mock_content,
            'metadata': {'source': url}
        })
    print(f"Loaded {len(documents)} documents from web URLs")
    return documents

def split_documents(documents):
    """Split documents into chunks."""
    text_splitter = SimpleTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks")
    return splits

def upload_to_pinecone(splits):
    """Upload document chunks to Pinecone."""
    try:
        embeddings = OllamaEmbeddings()
        
        # Extract text content and metadata
        texts = [split['page_content'] for split in splits]
        metadatas = [split['metadata'] for split in splits]
        
        # Get embeddings
        embeddings_list = embeddings.embed_documents(texts)
        
        # Upload to Pinecone
        index = pc.Index(INDEX_NAME)
        
        # Prepare vectors for upload
        vectors = []
        for i, (text, metadata, embedding) in enumerate(zip(texts, metadatas, embeddings_list)):
            vector_id = f"doc_{i}"
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': {
                    'text': text,
                    'source': metadata.get('source', 'Unknown')
                }
            })
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            index.upsert(vectors=batch)
        
        print(f"Uploaded {len(splits)} document chunks to Pinecone index {INDEX_NAME}")
        return True
        
    except Exception as e:
        print(f"Error uploading to Pinecone: {e}")
        print("Note: Ollama embeddings might not be compatible with Pinecone.")
        print("Consider using a different vector store or implementing a custom solution.")
        return False

def simple_vector_store(splits):
    """Create a simple in-memory vector store as fallback."""
    try:
        embeddings = OllamaEmbeddings()
        
        # Extract text content
        texts = [split['page_content'] for split in splits]
        metadatas = [split['metadata'] for split in splits]
        
        # Get embeddings
        embeddings_list = embeddings.embed_documents(texts)
        
        # Create simple vector store
        vector_store = {
            'texts': texts,
            'embeddings': embeddings_list,
            'metadatas': metadatas
        }
        
        print(f"Created simple vector store with {len(splits)} document chunks")
        return vector_store
        
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None

def main():    
    # # Example URLs - you can replace these with trusted fact-checking sites
    # urls = [
    #     "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters",
    #     "https://www.cdc.gov/coronavirus/2019-ncov/your-health/index.html",
    #     "https://www.reuters.com/fact-check"
    # ]
    
    # Load documents
    local_docs = load_local_documents()
    # web_docs = load_web_documents(urls)
    all_docs = local_docs #+ web_docs
    
    if not all_docs:
        print("No documents loaded. Please add documents and try again.")
        return
    
    # Split documents
    splits = split_documents(all_docs)
    
    # Try to upload to Pinecone, fallback to simple vector store
    success = upload_to_pinecone(splits)
    if not success:
        print("Falling back to simple vector store...")
        vector_store = simple_vector_store(splits)
        if vector_store:
            print("Simple vector store created successfully")
        else:
            print("Failed to create vector store")
    else:
        print("Documents successfully processed and uploaded to Pinecone")

if __name__ == "__main__":
    main() 