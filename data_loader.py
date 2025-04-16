import os
from dotenv import load_dotenv
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.document_loaders import DirectoryLoader, TextLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Initialize OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize Pinecone
pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV")
)

INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

def create_pinecone_index():
    """Create Pinecone index if it doesn't exist."""
    if INDEX_NAME not in pinecone.list_indexes():
        pinecone.create_index(
            name=INDEX_NAME,
            metric="cosine",
            dimension=1536  # OpenAI embedding dimension
        )
        print(f"Created new Pinecone index: {INDEX_NAME}")
    else:
        print(f"Pinecone index {INDEX_NAME} already exists")

def load_local_documents(data_dir="./data"):
    """Load documents from a local directory."""
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
        print("Please add your text files to this directory and run again.")
        return []

    loader = DirectoryLoader(
        data_dir, 
        glob="**/*.txt",
        loader_cls=TextLoader
    )
    
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from {data_dir}")
    return documents

def load_web_documents(urls):
    """Load documents from web URLs."""
    loader = WebBaseLoader(urls)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from web URLs")
    return documents

def split_documents(documents):
    """Split documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"Split into {len(splits)} chunks")
    return splits

def upload_to_pinecone(splits):
    """Upload document chunks to Pinecone."""
    embeddings = OpenAIEmbeddings()
    
    # Create and upload to Pinecone vector store
    vectorstore = Pinecone.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=INDEX_NAME
    )
    
    print(f"Uploaded {len(splits)} document chunks to Pinecone index {INDEX_NAME}")
    return vectorstore

def main():
    # Create Pinecone index
    create_pinecone_index()
    
    # Example URLs - you can replace these with trusted fact-checking sites
    urls = [
        "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public/myth-busters",
        "https://www.cdc.gov/coronavirus/2019-ncov/your-health/index.html",
        "https://www.reuters.com/fact-check"
    ]
    
    # Load documents
    local_docs = load_local_documents()
    web_docs = load_web_documents(urls)
    all_docs = local_docs + web_docs
    
    if not all_docs:
        print("No documents loaded. Please add documents and try again.")
        return
    
    # Split documents
    splits = split_documents(all_docs)
    
    # Upload to Pinecone
    vectorstore = upload_to_pinecone(splits)
    print("Documents successfully processed and uploaded to Pinecone")

if __name__ == "__main__":
    main()
