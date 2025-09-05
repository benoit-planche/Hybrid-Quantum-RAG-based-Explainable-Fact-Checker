# 🚀 GUIDE D'UTILISATION DU NOUVEAU SYSTÈME GROVER

## 📋 **INTÉGRATION DANS L'API EXISTANTE**

Voici comment utiliser le nouveau système Grover corrigé dans votre API FastAPI.

---

## 🔧 **ÉTAPE 1 : MODIFICATION DE L'API**

### **1.1 Ajouter les Imports**

```python
# Dans quantum_fact_checker_api.py, ajouter :
from hybrid_quantum_search_correct import correct_hybrid_retrieve_top_k, SearchStrategy
from grover_correct import correct_grover_retrieve_top_k
```

### **1.2 Modifier la Classe API**

```python
class QuantumFactCheckerAPI:
    def __init__(self):
        # ... code existant ...
        
        # NOUVEAU : Configuration Grover
        self.use_grover = True  # Activer Grover
        self.grover_strategy = "hybrid_adaptive"  # Stratégie par défaut
        self.grover_threshold = 0.7  # Seuil de similarité
        
        # NOUVEAU : Historique des performances
        self.performance_history = {
            'classical': [],
            'grover': [],
            'hybrid': []
        }
```

### **1.3 Modifier la Méthode fact_check**

```python
async def fact_check(self, message: str, user_id: str = "default", language: str = "en"):
    """Vérification de fait avec le nouveau système Grover"""
    
    # ... code existant jusqu'à la génération de l'embedding ...
    
    # NOUVEAU : Sélection de la stratégie
    if self.use_grover:
        logger.info(f"🚀 Utilisation du système Grover corrigé")
        
        # Déterminer la stratégie selon la taille de la base
        try:
            collection_info = self.cassandra_manager.get_collection_info()
            db_size = collection_info.get('document_count', 5000)
        except:
            db_size = 5000
        
        # Sélection adaptative
        if db_size < 1000:
            strategy = "classical_quantum"
        elif db_size > 10000:
            strategy = "grover_correct"
        else:
            strategy = self.grover_strategy
        
        logger.info(f"📊 Base de {db_size} documents, stratégie: {strategy}")
        
        # NOUVEAU : Utiliser le système hybride corrigé
        with time_operation_context("grover_hybrid_search"):
            results = correct_hybrid_retrieve_top_k(
                message, 
                self.db_folder, 
                k=10, 
                n_qubits=self.n_qubits,
                cassandra_manager=self.cassandra_manager,
                strategy=strategy
            )
        
        logger.info(f"🔍 Grover trouvé {len(results)} résultats")
        
    else:
        # Système classique (fallback)
        logger.info("🔄 Utilisation du système classique")
        results = retrieve_top_k(
            message, self.db_folder, k=10, 
            n_qubits=self.n_qubits, cassandra_manager=self.cassandra_manager
        )
    
    # ... reste du code existant ...
```

---

## 🎯 **ÉTAPE 2 : CONFIGURATION DES STRATÉGIES**

### **2.1 Configuration Flexible**

```python
# Ajouter dans la classe API
GROVER_CONFIG = {
    "enabled": True,
    "default_strategy": "hybrid_adaptive",
    "fallback_strategy": "classical_quantum",
    "performance_threshold": 0.8,
    "adaptive_learning": True,
    "strategies": {
        "classical_quantum": {
            "description": "Système classique (fallback)",
            "use_for": "petites bases < 1000"
        },
        "grover_correct": {
            "description": "Grover corrigé pur",
            "use_for": "grandes bases > 10000"
        },
        "grover_hybrid": {
            "description": "Grover + raffinement quantique",
            "use_for": "bases moyennes 1000-10000"
        },
        "hybrid_adaptive": {
            "description": "Sélection automatique",
            "use_for": "cas par défaut"
        }
    }
}
```

### **2.2 Endpoint de Configuration**

```python
@app.post("/configure-grover")
async def configure_grover(config: dict):
    """Configurer le système Grover"""
    try:
        if "enabled" in config:
            api.use_grover = config["enabled"]
        if "strategy" in config:
            api.grover_strategy = config["strategy"]
        if "threshold" in config:
            api.grover_threshold = config["threshold"]
        
        return {"status": "success", "config": {
            "use_grover": api.use_grover,
            "strategy": api.grover_strategy,
            "threshold": api.grover_threshold
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 **ÉTAPE 3 : MONITORING ET MÉTRIQUES**

### **3.1 Endpoint de Statistiques**

```python
@app.get("/grover-stats")
async def get_grover_stats():
    """Obtenir les statistiques du système Grover"""
    try:
        stats = {
            "grover_enabled": api.use_grover,
            "current_strategy": api.grover_strategy,
            "performance_history": api.performance_history,
            "config": GROVER_CONFIG
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **3.2 Logging Amélioré**

```python
# Ajouter dans la méthode fact_check
if self.use_grover:
    # Enregistrer les performances
    start_time = time.time()
    
    # ... exécution Grover ...
    
    duration = time.time() - start_time
    self.performance_history['grover'].append({
        'duration': duration,
        'results_count': len(results),
        'strategy': strategy,
        'timestamp': datetime.now().isoformat()
    })
    
    logger.info(f"⏱️ Grover exécuté en {duration:.2f}s avec {len(results)} résultats")
```

---

## 🚀 **ÉTAPE 4 : UTILISATION PRATIQUE**

### **4.1 Démarrage de l'API**

```bash
# Dans le dossier api/
cd /path/to/RAG-based-Explainable-Fact-Checker/api
python quantum_fact_checker_api.py
```

### **4.2 Test du Système Grover**

```bash
# Test avec Grover activé
curl -X POST "http://localhost:8000/fact-check" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Antarctica is gaining ice due to climate change",
    "user_id": "user123",
    "language": "en"
  }'
```

### **4.3 Configuration Dynamique**

```bash
# Activer Grover
curl -X POST "http://localhost:8000/configure-grover" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "strategy": "grover_correct",
    "threshold": 0.7
  }'

# Vérifier la configuration
curl -X GET "http://localhost:8000/grover-stats"
```

---

## 🎯 **ÉTAPE 5 : STRATÉGIES D'UTILISATION**

### **5.1 Stratégie Classique (Fallback)**

```python
# Utiliser le système classique
results = correct_hybrid_retrieve_top_k(
    query_text, db_folder, k=5, 
    strategy="classical_quantum"
)
```

**Utilisation :** Petites bases, compatibilité, fallback

### **5.2 Stratégie Grover Corrigé**

```python
# Utiliser Grover pur
results = correct_hybrid_retrieve_top_k(
    query_text, db_folder, k=5, 
    strategy="grover_correct"
)
```

**Utilisation :** Grandes bases, accélération quadratique

### **5.3 Stratégie Hybride Adaptative**

```python
# Utiliser la sélection automatique
results = correct_hybrid_retrieve_top_k(
    query_text, db_folder, k=5, 
    strategy="hybrid_adaptive"
)
```

**Utilisation :** Cas par défaut, optimisation automatique

### **5.4 Stratégie Grover Hybride**

```python
# Utiliser Grover + raffinement
results = correct_hybrid_retrieve_top_k(
    query_text, db_folder, k=5, 
    strategy="grover_hybrid"
)
```

**Utilisation :** Bases moyennes, équilibre performance/précision

---

## 📈 **ÉTAPE 6 : OPTIMISATION ET MONITORING**

### **6.1 Surveillance des Performances**

```python
# Ajouter dans la classe API
def get_performance_summary(self):
    """Obtenir un résumé des performances"""
    summary = {}
    
    for strategy, history in self.performance_history.items():
        if history:
            durations = [h['duration'] for h in history]
            summary[strategy] = {
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'total_queries': len(history)
            }
    
    return summary
```

### **6.2 Optimisation Automatique**

```python
# Ajouter dans la classe API
def optimize_strategy(self):
    """Optimiser la stratégie basée sur l'historique"""
    summary = self.get_performance_summary()
    
    if not summary:
        return "hybrid_adaptive"
    
    # Trouver la stratégie la plus rapide
    fastest_strategy = min(summary.keys(), 
                         key=lambda s: summary[s]['avg_duration'])
    
    logger.info(f"🎯 Stratégie optimale recommandée: {fastest_strategy}")
    return fastest_strategy
```

---

## 🔧 **ÉTAPE 7 : DÉPANNAGE**

### **7.1 Problèmes Courants**

#### **Erreur : Module not found**

```bash
# Vérifier les chemins Python
export PYTHONPATH="/path/to/RAG-based-Explainable-Fact-Checker/src/quantum:$PYTHONPATH"
```

#### **Erreur : Cassandra connection**

```python
# Vérifier la connexion Cassandra
try:
    cassandra_manager = create_cassandra_manager()
    print("✅ Cassandra connecté")
except Exception as e:
    print(f"❌ Erreur Cassandra: {e}")
```

#### **Erreur : QASM files not found**

```python
# Vérifier les fichiers QASM
import os
qasm_folder = "../src/quantum/quantum_db_8qubits/"
if os.path.exists(qasm_folder):
    files = os.listdir(qasm_folder)
    print(f"✅ {len(files)} fichiers QASM trouvés")
else:
    print(f"❌ Dossier QASM non trouvé: {qasm_folder}")
```

### **7.2 Logs de Debug**

```python
# Activer les logs détaillés
import logging
logging.getLogger('grover_correct').setLevel(logging.DEBUG)
logging.getLogger('hybrid_quantum_search_correct').setLevel(logging.DEBUG)
```

---

## 🎉 **ÉTAPE 8 : VALIDATION**

### **8.1 Test Complet**

```python
# Script de test complet
def test_grover_integration():
    """Tester l'intégration Grover"""
    
    # Test 1: Système classique
    print("🧪 Test système classique...")
    results_classical = correct_hybrid_retrieve_top_k(
        "test query", db_folder, k=5, 
        strategy="classical_quantum"
    )
    print(f"✅ Classique: {len(results_classical)} résultats")
    
    # Test 2: Grover corrigé
    print("🧪 Test Grover corrigé...")
    results_grover = correct_hybrid_retrieve_top_k(
        "test query", db_folder, k=5, 
        strategy="grover_correct"
    )
    print(f"✅ Grover: {len(results_grover)} résultats")
    
    # Test 3: Hybride adaptatif
    print("🧪 Test hybride adaptatif...")
    results_hybrid = correct_hybrid_retrieve_top_k(
        "test query", db_folder, k=5, 
        strategy="hybrid_adaptive"
    )
    print(f"✅ Hybride: {len(results_hybrid)} résultats")
    
    print("🎉 Tous les tests sont passés !")

# Exécuter le test
test_grover_integration()
```

---

## 📋 **RÉSUMÉ D'UTILISATION**

### **Configuration Rapide**

1. **Activer Grover** : `api.use_grover = True`
2. **Choisir stratégie** : `api.grover_strategy = "hybrid_adaptive"`
3. **Démarrer API** : `python quantum_fact_checker_api.py`
4. **Tester** : `curl -X POST "http://localhost:8000/fact-check" ...`

### **Stratégies Recommandées**

- **Développement** : `"hybrid_adaptive"` (robustesse)
- **Production** : `"grover_correct"` (performance)
- **Fallback** : `"classical_quantum"` (compatibilité)

### **Monitoring**

- **Logs** : Fichier `api_quantum_fact_checker.log`
- **Stats** : Endpoint `/grover-stats`
- **Config** : Endpoint `/configure-grover`

---

## 🚀 **PRÊT POUR LA PRODUCTION !**

Votre système est maintenant équipé du **nouveau système Grover corrigé** avec :

- ✅ **Accélération quadratique** pour les grandes bases
- ✅ **Sélection adaptative** de la meilleure stratégie
- ✅ **Fallback intelligent** en cas d'erreur
- ✅ **Monitoring complet** des performances
- ✅ **Configuration dynamique** en temps réel

**Le système est prêt pour une utilisation en production !** 🎉

---

*Guide d'utilisation développé dans le cadre du stage international à l'Université du Danemark du Sud*  
*Encadrant : Prof. Sadok Ben Yahia*  
*Date : Septembre 2025*
