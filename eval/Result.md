# 📊 Comparative Analysis: RAG with MMR vs RAG without MMR

## **General Critique**

**Major problem identified**: Both evaluations show **very poor performance** with average scores around 0.5-0.6 out of 1.0, indicating that my RAG system has fundamental quality issues, regardless of MMR usage.

## **Performance Comparison Table**

| Version | Answer Relevancy | Contextual Relevancy | Faithfulness | Contextual Recall | Contextual Precision | Document Diversity | Avg Similarity |
|---------|------------------|---------------------|--------------|-------------------|---------------------|-------------------|----------------|
| **With MMR (λ=0.5)** | 0.20-0.71 | 0.50-0.80 | 0.50-0.67 | 0.50-0.86 | 0.00-1.00 | 5 unique sources | 0.0 |
| **Without MMR** | 0.20-0.71 | 0.50-0.80 | 0.50-0.67 | 0.50-0.86 | 0.00-1.00 | 3-4 similar sources | 0.0 |
| **Cassandra MMR (λ=0.5)** | 0.20-0.67 | 0.33-0.86 | 0.50-0.67 | 0.50 | 0.0-1.0 | 12 unique sources | 0.11 |

> **Note**: The range format (e.g., 0.20-0.71) represents the **minimum and maximum scores** across all test cases. This indicates **high variability** in performance, suggesting inconsistent results rather than stable performance.

## **Verdict Analysis**

### **With MMR (λ=0.5)**

- **Correct verdicts**: 6/10 (60%)
- **Incorrect verdicts**: 3/10 (30%)
- **Mixed/uncertain verdicts**: 1/10 (10%)

### **Without MMR**

- **Correct verdicts**: 6/10 (60%)
- **Incorrect verdicts**: 3/10 (30%)
- **Mixed/uncertain verdicts**: 1/10 (10%)

### **Cassandra MMR (λ=0.5)**

- **Correct verdicts**: 0/10 (0%) - All verdicts were "TRUE" regardless of expected output
- **Incorrect verdicts**: 10/10 (100%)
- **Mixed/uncertain verdicts**: 0/10 (0%)

## **Identified Improvement Points**

### ✅ **Improvements brought by MMR**

1. **Source diversity**: MMR selects more varied documents
2. **Redundancy reduction**: Fewer repetitions in contexts
3. **Better coverage**: More balanced sources

### ❌ **Persistent Problems**

1. **Embedding quality**: Very low similarity scores (0.0-0.11)
2. **Contextual relevance**: Documents often off-topic
3. **Faithfulness**: Contradictions between context and answers
4. **Precision**: Incorrect or missing information
5. **Verdict accuracy**: Cassandra version shows 0% correct verdicts

## **Priority Recommendations**

### **1. Improve MMR**

- **Problem**: My implementation of MMR is not working as expected
- **Solution**: Change embedding model to use Llama-index embeddings model and integrate Llama-index MMR.

### **2. Improve document segmentation**

- **Problem**: The chunk size is not working as expected
- **Solution**: Change chunk size to 500 characters and chunk overlap to 100 characters. (Currently 1000 characters and 200 characters)

### **3. Lamba parameter**

- **Problem**: The lambda parameter is 0.5
- **Solution**: Try to change the lambda parameter

### **4. Fix verdict generation**

- **Problem**: Cassandra version always returns "TRUE" regardless of input
- **Solution**: Debug the prompt engineering and fact-checking logic

## **Conclusion**

**MMR does not significantly improve performance** because fundamental problems (poor embedding quality, inappropriate segmentation, irrelevant search) mask the potential benefits of diversification.

**Priority**: Fix basic problems optimizing MMR.
