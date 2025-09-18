# 🔬 API Quantum Fact-Checker

## 📋 Vue d'ensemble

Cette API remplace l'interface Streamlit par une API REST pour intégrer votre système de fact-checking quantique dans des applications de réseaux sociaux. Elle permet de vérifier automatiquement la véracité des messages liés au climat.

## 🚀 Fonctionnalités

### **Endpoints principaux**

- **`POST /fact-check`** : Vérifier un message individuel
- **`POST /fact-check/batch`** : Vérifier plusieurs messages en lot
- **`GET /health`** : Vérifier l'état de santé de l'API
- **`GET /stats`** : Obtenir les statistiques de performance

### **Réponse standard**

```json
{
  "message_id": "msg_1703123456789",
  "certainty_score": 0.85,
  "verdict": "TRUE",
  "explanation": "Cette affirmation est confirmée par plusieurs études scientifiques...",
  "confidence_level": "HIGH",
  "sources_used": ["IPCC_Report_2023.pdf", "Nature_Climate_Change_2022.pdf"],
  "processing_time": 2.34,
  "timestamp": "2023-12-21T10:30:45.123Z"
}
```

## 🛠️ Installation

### **1. Installer les dépendances**

```bash
cd api
pip install -r requirements_api.txt
```

### **2. Vérifier les prérequis**

- **Cassandra** : En cours d'exécution avec la base de données fact-checker
- **Ollama** : En cours d'exécution avec le modèle llama2:7b
- **Circuits QASM** : Présents dans `src/quantum/quantum_db/`

### **3. Lancer l'API**

```bash
cd api
python quantum_fact_checker_api.py
```

L'API sera accessible sur `http://localhost:8000`

## 📡 Utilisation de l'API

### **Vérification d'un message individuel**

```python
import requests

def check_climate_message(message: str, user_id: str = None):
    """Vérifier la véracité d'un message lié au climat"""
    
    payload = {
        "message": message,
        "user_id": user_id,
        "language": "en"
    }
    
    response = requests.post(
        "http://localhost:8000/fact-check",
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Interpréter le score de certitude
        if result['certainty_score'] >= 0.7:
            status = "✅ FIABLE"
        elif result['certainty_score'] >= 0.4:
            status = "❓ INCERTAIN"
        else:
            status = "⚠️ TROMPEUR"
        
        return {
            "status": status,
            "score": result['certainty_score'],
            "verdict": result['verdict'],
            "explanation": result['explanation'],
            "sources": result['sources_used']
        }
    else:
        return {"error": "Erreur lors de la vérification"}
```

### **Vérification en lot**

```python
def check_multiple_messages(messages: list):
    """Vérifier plusieurs messages en une seule requête"""
    
    payload = [
        {"message": msg, "language": "en"}
        for msg in messages
    ]
    
    response = requests.post(
        "http://localhost:8000/fact-check/batch",
        json=payload
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Erreur lors de la vérification en lot"}
```

### **Intégration dans une application web**

```javascript
// JavaScript/Node.js
async function checkClimateMessage(message) {
    try {
        const response = await fetch('http://localhost:8000/fact-check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                language: 'en'
            })
        });
        
        const result = await response.json();
        
        // Afficher le résultat
        if (result.certainty_score >= 0.7) {
            showFactCheckResult('reliable', result.explanation);
        } else if (result.certainty_score >= 0.4) {
            showFactCheckResult('uncertain', result.explanation);
        } else {
            showFactCheckResult('misleading', result.explanation);
        }
        
        return result;
    } catch (error) {
        console.error('Erreur:', error);
    }
}
```

## 🧪 Tests

### **Lancer les tests**

```bash
cd api
python test_api.py
```

### **Tests disponibles**

- ✅ Test de santé de l'API
- ✅ Test de fact-checking individuel
- ✅ Test de fact-checking en lot
- ✅ Test des statistiques

## 📊 Interprétation des résultats

### **Score de certitude (0-1)**

- **0.8-1.0** : Très fiable
- **0.6-0.8** : Fiable
- **0.4-0.6** : Incertain
- **0.2-0.4** : Potentiellement trompeur
- **0.0-0.2** : Très probablement trompeur

### **Verdicts**

- **TRUE** : L'affirmation est correcte
- **FALSE** : L'affirmation est incorrecte
- **MIXED** : L'évidence est mitigée
- **UNVERIFIABLE** : Impossible de vérifier

### **Niveaux de confiance**

- **HIGH** : Confiance élevée dans le verdict
- **MEDIUM** : Confiance modérée
- **LOW** : Faible confiance

## 🔧 Configuration

### **Variables d'environnement**

```bash
# Ajouter dans .env
QUANTUM_DB_FOLDER=src/quantum/quantum_db/
QUANTUM_N_QUBITS=16
QUANTUM_K_RESULTS=10
OLLAMA_BASE_URL=http://localhost:11434
CASSANDRA_HOST=localhost
CASSANDRA_PORT=9042
```

### **Paramètres de l'API**

```python
# Dans quantum_fact_checker_api.py
class QuantumFactCheckerAPI:
    def __init__(self):
        self.db_folder = "src/quantum/quantum_db/"
        self.n_qubits = 16
        self.k_results = 10
```

## 🚀 Déploiement

### **Développement**

```bash
uvicorn quantum_fact_checker_api:app --reload --host 0.0.0.0 --port 8000
```

### **Production**

```bash
# Avec Gunicorn
gunicorn quantum_fact_checker_api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Avec Docker
docker build -t quantum-fact-checker-api .
docker run -p 8000:8000 quantum-fact-checker-api
```

## 📈 Monitoring

### **Statistiques de performance**

```bash
curl http://localhost:8000/stats
```

### **Santé du système**

```bash
curl http://localhost:8000/health
```

## 🔒 Sécurité

### **CORS**

L'API est configurée pour accepter les requêtes depuis n'importe quelle origine. En production, spécifiez les domaines autorisés :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://votre-app.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### **Rate Limiting**

Pour limiter le nombre de requêtes :

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/fact-check")
@limiter.limit("10/minute")
async def fact_check(request: FactCheckRequest):
    # ...
```

## 🐛 Dépannage

### **Erreurs courantes**

1. **API non initialisée**
   - Vérifier que Cassandra et Ollama sont en cours d'exécution
   - Vérifier les chemins des circuits QASM

2. **Timeout**
   - Augmenter le timeout dans les requêtes
   - Optimiser les paramètres quantiques

3. **Erreur de connexion**
   - Vérifier les paramètres de connexion
   - Vérifier que les services sont accessibles

### **Logs**

```bash
# Activer les logs détaillés
uvicorn quantum_fact_checker_api:app --log-level debug
```

## 💡 Exemples d'intégration

### **Application de réseaux sociaux**

```python
# Lorsqu'un utilisateur poste un message
def on_user_post(message: str, user_id: str):
    # Détecter si le message concerne le climat
    if is_climate_related(message):
        # Vérifier la véracité
        fact_check_result = check_climate_message(message, user_id)
        
        # Afficher le badge de fact-checking
        if fact_check_result['score'] < 0.4:
            show_warning_badge(fact_check_result['explanation'])
        elif fact_check_result['score'] > 0.7:
            show_verified_badge(fact_check_result['explanation'])
```

### **Bot Discord/Slack**

```python
def handle_climate_message(message: str, channel: str):
    result = check_climate_message(message)
    
    response = f"""
🔍 **Fact-Checking Climatique**
📊 Score de certitude: {result['score']:.1%}
🎯 Verdict: {result['verdict']}
📝 Explication: {result['explanation']}
📚 Sources: {', '.join(result['sources'][:3])}
    """
    
    send_message(channel, response)
```

---

**Version** : 1.0.0  
**Dernière mise à jour** : 21/12/2023  
**Auteur** : Quantum Fact-Checker Team
