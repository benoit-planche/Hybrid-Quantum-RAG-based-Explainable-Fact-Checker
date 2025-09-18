# Hybrid Quantum-Classical RAG for Climate Misinformation Detection

Author: Benoit PLANCHE, <benoit.planche@etu.umontpellier.fr>  
Posted Date: September 18th, 2025

## Abstract

This report describes the conceptualization and implementation of an innovative AI agent based on quantum algorithms, carried out as part of a second-year DevOps engineering internship abroad. The project focuses on the creation of a Retrieval-Augmented Generation (RAG) system designed to verify and detect misinformation related to climate change. This solution could enable social network–style applications to integrate rapid moderation fact checks on user-generated content.

## Introduction

### Problem Statement

Today, climate misinformation is a major problem that affects society. It can lead to significant damage to health, the economy, and the environment. Climate misinformation can also lead to erroneous political decisions and social conflicts. The fight against climate misinformation is therefore a major priority for society. This is why it is crucial to develop automated fact-checking tools to protect the integrity of scientific information around climate issues.

### Project Presentation

This article is part of the research project "Edge-LLM-based shield against misinformation" developed at the University of Southern Denmark. The main objective is to create an automated system for detecting and verifying climate misinformation in real-time. The project combines several cutting-edge technologies: artificial intelligence with Large Language Models (LLMs), quantum technologies for information retrieval optimization, and RAG (Retrieval-Augmented Generation) architecture to ensure source traceability. This multidisciplinary approach aims to develop a robust tool capable of effectively combating the spread of false information on climate issues.

### Article Objective

This document presents the mission carried out, the technical challenges overcome, and the results obtained as part of this research project.

## Context

### Research Project: "Edge-LLM-based shield against misinformation"

The project is part of the broader fight against misinformation, with a specific focus on climate information. The main objective was to develop a hybrid system combining both quantum and classical search approaches for document analysis, with the aim of obtaining maximum accuracy while minimizing processing time.

The automated system developed is capable of:

- Analyzing and verifying claims related to climate change
- Providing transparent and verifiable explanations
- Operating in real-time in applications

### Technological Justification and Technical Objectives

The use of LLMs (Large Language Models) is justified by their ability to understand context and nuance in texts, which is essential for detecting sophisticated misinformation. For the integration of these models, we chose Ollama, an open-source platform that allows running large language models locally. Ollama offers several advantages: simplified deployment, automatic model management. This solution avoids the costs and limitations of cloud APIs while ensuring data privacy.

However, to guarantee the traceability and verifiability of generated responses, it is necessary to go beyond simple text generation. This is where the RAG (Retrieval-Augmented Generation) architecture makes perfect sense: it combines the power of LLMs with a document search module, allowing the system to rely on reliable sources and explicitly cite the documents used during claim verification. Thus, RAG improves the transparency and robustness of the system against misinformation.

Furthermore, the quantum approach offers prospects for improving search and similarity performance, particularly in processing large document databases. The integration of quantum techniques in the RAG retrieval module allows for more precise and faster context capture, thus strengthening the overall efficiency of the system.

The technical objectives of this mission were to:

- Master quantum technologies applied to information retrieval
- Integrate large language models into a production system
- Implement a RAG architecture to ensure source traceability and fact-checking robustness
- Optimize processing performance to enable real-time use adapted to the dynamics of social networks and social media
- Evaluate the overall performance of the system on a corpus of climate claims

## Technical Report

### System Architecture

The developed RAG system is based on a hybrid architecture combining several components. The entire development was carried out in Python, a technological choice justified by the richness of its ecosystem for artificial intelligence, quantum processing, and database management. Python offers specialized libraries like Qiskit for quantum simulation, Ollama for LLM integration, and Cassandra for vector database management, enabling harmonious integration of all system components.

![System RAG Architecture Diagram](ressource/architecture.png)

The RAG (Retrieval-Augmented Generation) system architecture relies on several components that interact to enable relevant knowledge search and adapted response generation. The process begins with the user prompt, which constitutes the initial query. This prompt is processed by the RAG pipeline, whose role is to enrich the query with information from external sources before transmitting it to the language model. The knowledge base consists of reference documents (for example PDF files), which are first divided into smaller segments called chunks.

These chunks are then transformed into vectors using OllamaEmbedding. The vectors are stored in a vector database (Cassandra), which allows performing similarity search to quickly identify the most relevant passages to answer the question asked. The context thus found is then transmitted to a quantum circuit (8 qubits), whose role is to optimize or reclassify the information before sending it to the model. Finally, the LLM (llama 7B) exploits both the initial prompt and the enriched context to produce the final response that is returned to the user.

### Cassandra Vector Database

#### Database Creation and Configuration

The Cassandra vector database constitutes the heart of the RAG retrieval system. It stores vector embeddings of climate documents and enables fast and efficient search. The database configuration was implemented with the following parameters:

```python
CREATE KEYSPACE climate_fact_checking
WITH replication = {'class':'SimpleStrategy','replication_factor': 1};
CREATE TABLE document_embeddings (
document_id UUID PRIMARY KEY,
title TEXT,
content TEXT,
embedding VECTOR <FLOAT, 4096>, # 4096D Embeddings
metadata MAP <TEXT, TEXT>,
created_at TIMESTAMP
);
```

#### Document Ingestion Process

The climate document ingestion process begins with a preprocessing phase, during which text is extracted and cleaned from scientific PDF files. Once this step is completed, documents are divided into segments not exceeding 512 tokens, to optimize the management and analysis of textual data. For each segment thus obtained, 4096-dimensional vector embeddings are generated using the 'Ollama Embedding' model via the Ollama API. Finally, these vector representations, along with their metadata, are stored in the Cassandra database, ensuring efficient indexing and fast search within the system.

```python
def ingest_document(document_path: str):
    """Climate document ingestion process"""
    # 1. Text extraction
    text_content = extract_text_from_pdf(document_path)
    # 2. Chunking
    chunks = create_text_chunks(text_content, max_tokens=512)
    # 3. Embedding generation
    embeddings = generate_embeddings(chunks)
    # 4. Storage in Cassandra
    for chunk, embedding in zip(chunks, embeddings):
        store_in_cassandra(chunk, embedding, metadata)
```

#### Vector Search and Pre-filtering

During a user query, the system takes the query content and transforms it into a vector embedding using the 'OllamaEmbedding' model. Then, a vector search is performed in the Cassandra database to find the 300 most similar documents to the query embedding. These documents are then used for quantum search. Thanks to this pre-filtering, the system can limit the number of documents to compare in quantum search, which improves system performance.

```python
def vector_search(query_embedding: np.ndarray, top_k: int = 300):
    """Vector search in Cassandra"""
    # Cosine similarity query
    query = """
       SELECT document_id, title, content, embedding, metadata
       FROM document_embeddings
       ORDER BY embedding ANN OF %s
       LIMIT %s
       """
    results = session.execute(query, [query_embedding, top_k])
    return [(row.document_id, row.title, row.content, row.embedding)
            for row in results]
```

This architecture allows efficient processing of a database of more than 10,000 documents while maintaining acceptable response times for real-time use that we could not assume with quantum simulation alone.

### Quantum System Development

Once the documents are selected, the quantum system is used to compare the documents with each other and find the 10 most similar results.

#### Data Preparation for Quantum Processing

Before using the quantum circuit, it is necessary to adapt the document embeddings to the quantum representation. For this, each embedding is reduced to a dimension of 8, corresponding to the number of qubits in the circuit. Then, each vector is normalized. This normalization is essential to enable data encoding in the form of quantum amplitudes, in accordance with the requirements of amplitude encoding.

#### Quantum Circuit Implementation and Use

The heart of the system relies on an 8-qubit quantum circuit, which allows representing normalized embeddings in the form of quantum states. For each document and for the user query, a quantum circuit is created and initialized using the 'initialize' method, which directly encodes the embedding in the quantum state of the circuit.

The comparison between documents is performed by calculating the quantum overlap between the prepared states, which allows measuring the similarity between two quantum states. The higher this value, the more similar the documents are considered. A comparison circuit is then built to successively prepare the two states to be compared, then a specific measurement is performed, for example by evaluating the probability of finding the system in a given reference state. This measurement provides a quantitative estimate of the similarity between the query and each document.

Finally, the 10 most similar documents are selected and returned to the LLM, along with all necessary information, to analyze the user query and generate a verdict as well as an explanation adapted to scientific reality.

### LLM Integration

#### Ollama Configuration

The integration of the Llama2:7B model via Ollama required parameter optimization:

```python
class QuantumFactChecker:
    def __init__(self):
        self.ollama_client = OllamaClient(
            model="llama2:7b",
            temperature=0.01,
            timeout=300
        )
```

The Llama2:7B model was chosen for its speed and accuracy. The 7B means the model has 7 billion parameters. These parameters define the model's ability to understand context and nuance in texts. There are other models (Mistral:7B, CodeLlama:7B, DeepSeek-R1:7B) and with more parameters (13B, 70B, 130B). Here, the Llama2:7B model was chosen for its speed and accuracy.

Also, the temperature was reduced to 0.01 for decisive and consistent responses. Temperature is a parameter that defines the model's creativity. The higher the temperature, the more creative the model. The lower the temperature, the more deterministic the model.

#### Prompt Engineering

The development of an effective prompt was crucial for the quality of results. The prompt is the text that is sent to the model so that it generates a response. It is important to format the prompt well so that the model can understand the user query and generate a response adapted to scientific reality. Here is the prompt used for LLM analysis:

```python
analysis_prompt = """
You are a climate science fact-checker. Analyze the following claim ...
CLAIM: {claim}
EVIDENCE: {evidence}
INSTRUCTIONS:
- Be EXTREMELY CRITICAL and skeptical
- Look for evidence that DIRECTLY contradicts the claim
- Quote specific text from the evidence
- Distinguish between Antarctica and other regions
- If evidence is insufficient, state FALSE
RESPONSE FORMAT:
VERDICT: [TRUE/FALSE/UNVERIFIABLE]
EXPLANATION: [Detailed reasoning]
"""
```

### Technical Challenges and Solutions

Finally, the development of the system required overcoming several major technical challenges. Performance optimization was achieved through the adoption of a hybrid architecture with pre-filtering, reducing processing time per query by twenty. Finally, fact-checking efficiency was strengthened by improving the prompt and fine-tuning the LLM temperature, allowing to limit biases and obtain more critical and reliable responses. These solutions led to a performant, stable, and relevant system for automated verification of scientific facts.

## Results Obtained

### Overall Performance

The final system achieves 76% accuracy on a corpus of 50 climate claims, representing a significant improvement over the baseline system (22%). This improvement is due to the use of the hybrid quantum-classical architecture, which allows combining the advantages of each approach. Processing speed is 27.59 seconds on average, which is acceptable for a real-time application. This cost is largely due to the quantum part, as for now we can only simulate quantum and not execute it on a quantum computer.

### Comparison with Other Systems

It is also important to evaluate the system by comparing it with other systems. Here are the results of the comparison with the Raw LLM and the Hybrid system.

| System | Accuracy | Average Time | Improvement |
|--------|----------|--------------|-------------|
| Raw LLM | 22% | 2-5 seconds | - |
| Hybrid System | 76% | 27.59 seconds | +256.36% |

### Examples of Results

Here are some examples of results obtained with the Hybrid system.

#### Example 1: Successful Detection of a False Claim

```python
CLAIM: "Antarctica is gaining ice due to climate change"
VERDICT: FALSE
EXPLANATION: "The evidence shows that Antarctica is actually losing ice mass. The continent has experienced significant ice loss over recent decades, contradicting the claim of ice gain."
sources: ...
```

#### Example 2: Validation of an Established Fact

```python
CLAIM: "CO2 levels have increased since the pre-industrial era"
VERDICT: TRUE
EXPLANATION: "Multiple sources confirm that atmospheric CO2 concentrations have risen from approximately 280 ppm to over 400 ppm since 1750."
sources: ...
```

### Conclusion and Improvement Perspectives

We therefore have a hybrid RAG architecture that allows us to achieve 76% accuracy with only a 7B LLM model. A clear improvement over the Raw LLM. Also, the API interface allows integrating the system into external applications and facilitating tests. All with an average processing speed of 27.59 seconds. Reasonable for a real-time application. However, we can admit that processing speed is a central point in the improvement perspectives of our architecture.

## Bibliography

```
"About the NIPCC – Climate Change Reconsidered." Climate Change Reconsidered,
https://climatechangereconsidered.org/about-the-nipcc/. Accessed 12 Sept. 2025.
Anouska-Abhisikta. "GitHub-Anouska-Abhisikta/RAG-Based-Explainable-Fact-Checker:
A Transparent and Auditable Fact-Checking System Powered by Retrieval-Augmented Generation (RAG), LangChain, and Large Language Models." GitHub,
https://github.com/Anouska-Abhisikta/RAG-based-Explainable-Fact-Checker. Accessed 12 Sept. 2025.
Arif-PhyChem. "GitHub - Arif-PhyChem/QD3SET: The First and the Only Dataset in
the Field of Quantum Dissipative Dynamics." GitHub,
https://github.com/Arif-PhyChem/QD3SET. Accessed 12 Sept. 2025.
"ClimateChangeMissionControl-NASAScience." NASAScience, https://www.facebook.com/NASA, 6 Oct. 2021,
https://science.nasa.gov/earth/climate-change/climate-change-mission-control/.
FujiiLabCollaboration. "GitHub-FujiiLabCollaboration/MNISQ-Quantum-Circuit-Dataset:
MNISQ Circuit Dataset for Machine Learning and Quantum Machine Learning." GitHub,
https://github.com/FujiiLabCollaboration/MNISQ-quantum-circuit-dataset. Accessed 12 Sept. 2025.
"Global Warming Links." Skeptical Science,
https://skepticalscience.com/resources.php. Accessed 12 Sept. 2025.
"IPCC — Intergovernmental Panel on Climate Change." IPCC — Intergovernmental Panel
on Climate Change,
https://www.ipcc.ch/. Accessed 12 Sept. 2025.
LSchatzki. "GitHub - LSchatzki/NTangled_Datasets: Entanglement-Based Datasets and
Generators for Quantum Machine Learning." GitHub,
https://github.com/LSchatzki/NTangled_Datasets. Accessed 12 Sept. 2025.
sysadmin-info. "GitHub - Sysadmin-Info/N8n-K3s." GitHub,
https://github.com/sysadmin-info/n8n-k3s. Accessed 12 Sept. 2025.
```
