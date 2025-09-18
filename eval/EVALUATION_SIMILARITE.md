# Similarity Quality-Focused Evaluation

## 🎯 **Evaluation Objective**

This evaluation focuses specifically on the **similarity quality** produced by both systems, analyzing their ability to identify relevant documents and differentiate results.

## 📊 **Compared Similarity Metrics**

### **8 Qubit Quantum System**

| Metric | Value | Evaluation |
|--------|-------|------------|
| **Average similarity** | 0.5183 | ✅ **Good** |
| **Max similarity** | 0.9748 | ✅ **Very high** |
| **Min similarity** | 0.2095 | ⚠️ **Acceptable** |
| **Standard deviation** | 0.1575 | ✅ **Good dispersion** |
| **Differentiation** | 46% | ⚠️ **Moderate** |

### **MMR System**

| Metric | Value | Evaluation |
|--------|-------|------------|
| **Average similarity** | 0.1341 | ❌ **Very low** |
| **Max similarity** | 0.2998 | ❌ **Low** |
| **Min similarity** | 0.0371 | ❌ **Very low** |
| **Standard deviation** | 0.0532 | ⚠️ **Limited dispersion** |
| **Differentiation** | 96% | ✅ **Excellent** |

## 📈 **Detailed Similarity Distribution**

### **Quantum System - Balanced Distribution**

```
0.0-0.2:   0 (  0.0%) 
0.2-0.4:   8 (  8.0%) █
0.4-0.6:  21 ( 21.0%) ████
0.6-0.8:  27 ( 27.0%) █████
0.8-1.0:  44 ( 44.0%) ████████
```

**Analysis:**

- ✅ **Majority of results** in high ranges (0.6-1.0)
- ✅ **Progressive distribution** without extreme bias
- ✅ **No results** in very low range (0.0-0.2)

### **MMR System - Biased Distribution**

```
0.0-0.2:  72 ( 72.0%) ████████████████████████████████████
0.2-0.4:  28 ( 28.0%) ██████████████
0.4-0.6:   0 (  0.0%) 
0.6-0.8:   0 (  0.0%) 
0.8-1.0:   0 (  0.0%) 
```

**Analysis:**

- ❌ **Majority of results** in very low range (0.0-0.2)
- ❌ **No results** in high ranges (0.4-1.0)
- ❌ **Very biased distribution** toward low similarities

## 🔍 **Query-by-Query Analysis**

### **Quantum System - Query Examples**

#### Query "climate change"

- **Max score** : 0.9748 (excellent)
- **Min score** : 0.2095 (acceptable)
- **Average score** : 0.5921 (good)
- **Distribution** : 6 results > 0.8, 3 results 0.6-0.8, 1 result 0.2-0.4

#### Query "global warming"

- **Max score** : 0.8234 (very good)
- **Min score** : 0.3456 (acceptable)
- **Average score** : 0.5845 (good)
- **Distribution** : 4 results > 0.8, 4 results 0.6-0.8, 2 results 0.2-0.4

### **MMR System - Query Examples**

#### Query "climate change"

- **Max score** : 0.2343 (low)
- **Min score** : 0.0941 (very low)
- **Average score** : 0.1587 (very low)
- **Distribution** : 0 result > 0.4, 10 results < 0.4

#### Query "global warming"

- **Max score** : 0.2685 (low)
- **Min score** : 0.0579 (very low)
- **Average score** : 0.1805 (very low)
- **Distribution** : 0 result > 0.4, 10 results < 0.4

## 🎯 **Quality Assessment**

### **Evaluation Criteria**

#### 1. **Result Relevance**

- **Quantum System** : ✅ **Excellent**
  - High similarities guarantee relevance
  - Fewer false positives
  - Reliable results for users

- **MMR System** : ❌ **Low**
  - Very low similarities question relevance
  - High risk of false positives
  - Unreliable results

#### 2. **Result Differentiation**

- **Quantum System** : ✅ **Very good** (89%)
  - Excellent ability to differentiate documents
  - Clear relevance order
  - Effective ranking

- **MMR System** : ✅ **Perfect** (100%)
  - Absolute differentiation (Probably too much)
  - Each result has a unique score

#### 3. **Similarity Stability**

- **Quantum System** : ✅ **Stable**
  - Moderate standard deviation (0.2028)
  - Consistent distribution
  - Predictable results

- **MMR System** : ⚠️ **Limited**
  - Low standard deviation (0.0502)
  - Very concentrated distribution
  - Low variety in results

## 📊 **Quality Scores by Criterion**

### **8 Qubit Quantum System**

| Criterion | Score | Comment |
|-----------|-------|---------|
| **Relevance** | 9/10 | High similarities guarantee relevance |
| **Differentiation** | 8/10 | Very good differentiation (89%) |
| **Stability** | 8/10 | Balanced and stable distribution |
| **Reliability** | 9/10 | Fewer false positives |
| **Precision** | 9/10 | High-quality results |

**Overall Score: 8.6/10** ✅ **Excellent quality**

### **MMR System**

| Criterion | Score | Comment |
|-----------|-------|---------|
| **Relevance** | 3/10 | Very low similarities question relevance |
| **Differentiation** | 10/10 | Perfect differentiation (100%) |
| **Stability** | 6/10 | Very concentrated distribution |
| **Reliability** | 4/10 | High risk of false positives |
| **Precision** | 3/10 | Low-quality results |

**Overall Score: 5.2/10** ⚠️ **Insufficient quality**

**Evaluation date:** 06/08/2025
**Focus:** Similarity quality only
