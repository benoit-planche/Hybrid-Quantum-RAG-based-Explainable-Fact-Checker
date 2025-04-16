# RAG-based-Explainable-Fact-Checker
A transparent and auditable fact-checking system powered by Retrieval-Augmented Generation (RAG), LangChain, and Large Language Models. This system verifies claims against reliable sources and clearly explains its reasoning process with full traceability.

## Features

- **Transparent Fact-Checking**: Claims are verified against a database of reliable sources with full explanation of reasoning
- **Source Attribution**: All verdicts are tied to specific evidence snippets from the source database
- **Multi-step Analysis**: Claims are broken down into components for thorough verification
- **Explainable Verdicts**: Clear reasoning chain from evidence to conclusion
- **Interactive UI**: User-friendly Streamlit interface with detailed source exploration
- **Analytics Dashboard**: Track fact-checking patterns and trends
- **Auditability**: Complete trace of the fact-checking process for accountability

## Tech Stack

- **LangChain**: Orchestration framework for connecting LLMs with data sources
- **OpenAI API**: Powers the language understanding and reasoning components
- **Pinecone**: Vector database for semantic search across source documents
- **Streamlit**: User interface and visualization
- **Python**: Core programming language

## Usage

### 1. Load data into Pinecone

First, load your trusted source documents into the Pinecone vector database:

```bash
python data_loader.py
```

This script will:
- Create a new Pinecone index if needed
- Process documents from the `./data` directory and the specified web URLs
- Split documents into chunks
- Embed these chunks and store them in Pinecone

### 2. Run the Streamlit application

```bash
streamlit run app.py
```

The application will start and be accessible at http://localhost:8501

### 3. Using the Fact-Checker

1. Enter a claim to fact-check in the text area
2. Click "Fact Check" to start the process
3. Review the verdict and summary
4. Explore the "Detailed Analysis" tab to see the complete reasoning
5. Check the "Source Tracking" tab to explore exactly which sources were used

## How It Works

The system follows a multi-step process to verify claims:

1. **Query Generation**: The claim is analyzed to generate effective search queries
2. **Retrieval**: Relevant documents are retrieved from the Pinecone vector database
3. **Analysis**: The LLM breaks down the claim into components and analyzes each against the evidence
4. **Verdict Assignment**: Based on the evidence, a verdict is assigned (TRUE, MOSTLY TRUE, MIXED, MOSTLY FALSE, FALSE, or UNVERIFIABLE)
5. **Explanation Generation**: A human-readable explanation is generated
6. **Source Attribution**: All evidence is linked back to its original sources

## Advanced Features

### Dashboard

Navigate to the Dashboard page to see analytics about your fact-checking activities:
- Verdict distribution
- Fact checks over time
- Recent fact checks

### Batch Processing

The system includes functionality for processing multiple claims at once through the Advanced Features page.

### Trend Analysis

Analyze patterns across multiple fact-checks to identify common themes and narrative trends.

## Project Structure

```
rag-fact-checker/
├── app.py                   # Main Streamlit application
├── data_loader.py           # Script for loading documents into Pinecone
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in repo)
├── data/                    # Directory for source documents
├── fact_checks/             # Saved fact check results
└── pages/                   # Additional Streamlit pages
    ├── 01_Dashboard.py      # Analytics dashboard
    └── 02_Advanced_Features.py # Advanced capabilities
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project uses LangChain, developed by LangChain, Inc.
- Vector search powered by Pinecone
- LLM capabilities provided by OpenAI
