#!/usr/bin/env python3
"""
API pour le système de fact-checking quantique
Remplace l'interface Streamlit par une API REST
"""

import os
import sys
import time
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

# Configuration des logs vers un fichier
log_file = "api_quantum_fact_checker.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler()  # Garder aussi la console
    ]
)
logger = logging.getLogger(__name__)

# Ajouter le dossier system au PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
system_dir = os.path.join(os.path.dirname(current_dir), 'system')
quantum_dir = os.path.join(os.path.dirname(current_dir), 'src', 'quantum')
sys.path.insert(0, system_dir)
sys.path.insert(0, quantum_dir)

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Imports du système quantique
from quantum_search import retrieve_top_k
from cassandra_manager import create_cassandra_manager
from ollama_utils import OllamaClient, format_prompt
from performance_metrics import (
    start_performance_session, 
    get_performance_summary, 
    save_performance_metrics,
    time_operation_context,
    log_llm_operation,
    log_database_operation
)

# Configuration de l'API
app = FastAPI(
    title="Quantum Fact-Checker API",
    description="API pour vérifier la véracité des messages liés au climat",
    version="1.0.0"
)

# Configuration CORS pour permettre l'accès depuis les applications web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic pour l'API
class FactCheckRequest(BaseModel):
    message: str = Field(..., description="Message à vérifier", min_length=1, max_length=1000)
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur (optionnel)")
    context: Optional[str] = Field(None, description="Contexte supplémentaire (optionnel)")
    language: str = Field("en", description="Langue du message (défaut: en)")

class FactCheckResponse(BaseModel):
    message_id: str
    certainty_score: float = Field(..., ge=0.0, le=1.0, description="Score de certitude (0-1)")
    verdict: str = Field(..., description="Verdict: TRUE, FALSE, MIXED, UNVERIFIABLE")
    explanation: str = Field(..., description="Explication détaillée du verdict")
    confidence_level: str = Field(..., description="Niveau de confiance: HIGH, MEDIUM, LOW")
    sources_used: List[str] = Field(..., description="Sources utilisées pour la vérification")
    processing_time: float = Field(..., description="Temps de traitement en secondes")
    timestamp: str = Field(..., description="Timestamp de la vérification")

class HealthResponse(BaseModel):
    status: str
    quantum_system: str
    cassandra_status: str
    ollama_status: str
    timestamp: str

class QuantumFactCheckerAPI:
    """Classe principale pour gérer l'API de fact-checking quantique"""
    
    def __init__(self):
        """Initialiser l'API"""
        self.db_folder = "../src/quantum/quantum_db_8qubits/"
        self.n_qubits = 8
        self.k_results = 10
        
        # Initialiser les composants
        self._initialize_components()
        
        # Template pour l'analyse LLM - VERSION STRICTE ET DIRECTIVE
        self.analysis_prompt_template = """
You are a RIGOROUS and DECISIVE fact-checker. Your job is to verify the following claim using ONLY the provided evidence. 
You MUST take a clear position and be willing to CONTRADICT the claim if the evidence doesn't support it.
- Be EXTRA CRITICAL of claims that seem too good to be true
- If a claim sounds like climate denial talking points, be especially skeptical
- Look for evidence that DIRECTLY contradicts the claim
- Remember: absence of evidence is not evidence of absence

CLAIM: {claim}

EVIDENCE (from chunks):
{retrieved_docs}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. You MUST be DECISIVE. No hedging, no "maybe", no uncertainty.
2. If the evidence DIRECTLY supports the claim, say TRUE.
3. If the evidence CONTRADICTS the claim, say FALSE.
4. If the evidence is UNRELATED or INSUFFICIENT, say UNVERIFIABLE.
5. You MUST quote SPECIFIC text from the evidence to justify your verdict.
6. If the evidence talks about OTHER regions (like Karakoram, Himalayas) but NOT Antarctica, this is NOT evidence for the claim.
7. Be willing to say FALSE if the evidence doesn't specifically support the claim about Antarctica.

ANTARCTICA-SPECIFIC ANALYSIS:
- Look for DIRECT statements about Antarctica ice loss/gain
- If evidence mentions other glaciers (Karakoram, Himalayas), this is NOT about Antarctica
- If evidence is about general climate change but not Antarctica ice, this is NOT sufficient
- The claim is SPECIFICALLY about Antarctica gaining ice due to climate change

Format your response EXACTLY as follows:
VERDICT: [TRUE/FALSE/UNVERIFIABLE]
EXPLANATION: [Your decisive reasoning with specific quotes from the evidence. Be direct and clear about why you chose this verdict.]
"""
    
    def _initialize_components(self):
        """Initialiser tous les composants du système"""
        try:
            print("🔌 Initialisation de l'API Quantum Fact-Checker...")
            
            # Connexion Cassandra
            print("  📊 Connexion à Cassandra...")
            self.cassandra_manager = create_cassandra_manager(
                table_name="fact_checker_docs", 
                keyspace="fact_checker_keyspace"
            )
            # Utiliser la session Cassandra du cassandra_manager
            self.cassandra_session = self.cassandra_manager.session
            print("  ✅ Session Cassandra initialisée")
            
            # Client Ollama
            print("  🤖 Initialisation du client Ollama...")
            self.ollama_client = OllamaClient()
            
            # Test de connexion
            print("  ✅ Test de connexion...")
            test_response = self.ollama_client.generate("Test", max_tokens=5)
            print(f"  ✅ Ollama OK: {len(test_response)} caractères générés")
            
            print("✅ API initialisée avec succès!")
            
        except Exception as e:
            print(f"❌ Erreur d'initialisation: {e}")
            raise
    
    def get_chunk_info(self, chunk_id: str) -> tuple[str, str]:
        """Récupérer les informations d'un chunk depuis Cassandra"""
        try:
            # Utiliser la session Cassandra existante si disponible
            if hasattr(self, 'cassandra_session'):
                session = self.cassandra_session
            else:
                # Créer une nouvelle session si nécessaire
                from cassandra.cluster import Cluster
                cluster = Cluster(['localhost'], port=9042)
                session = cluster.connect()
                self.cassandra_session = session
            
            # Le chunk_id est maintenant au format "doc_157" (après nettoyage dans quantum_search.py)
            # Essayer d'abord avec partition_id = "None"
            partition_id = "None"
            row_id = chunk_id  # Utiliser "doc_157" comme row_id
            
            query = "SELECT body_blob, metadata_s FROM fact_checker_keyspace.fact_checker_docs WHERE partition_id=%s AND row_id=%s;"
            row = session.execute(query, (partition_id, row_id)).one()
            
            # Si pas trouvé, essayer de récupérer directement par row_id
            if not row or not row.body_blob:
                query_fallback = "SELECT body_blob, metadata_s FROM fact_checker_keyspace.fact_checker_docs WHERE row_id=%s LIMIT 1 ALLOW FILTERING;"
                row = session.execute(query_fallback, (row_id,)).one()
            
            if row and row.body_blob:
                chunk_text = row.body_blob
                pdf_name = row.metadata_s.get('source', '[PDF inconnu]') if row.metadata_s else '[PDF inconnu]'
                return chunk_text, pdf_name
            else:
                return "[Texte non trouvé]", "[PDF inconnu]"
                
        except Exception:
            return "[Erreur de récupération]", "[Erreur]"
    
    def generate_llm_response(self, claim: str, chunk_ids: List[str]) -> tuple[str, str]:
        """Générer la réponse LLM pour l'analyse"""
        try:
            # Préparer les documents (même format que l'app Streamlit)
            docs = []
            for chunk_id in chunk_ids:
                chunk_text, pdf_name = self.get_chunk_info(chunk_id)
                # Prendre plus de contexte pour une meilleure analyse (comme l'app Streamlit)
                excerpt = chunk_text[:1500] + ("..." if len(chunk_text) > 1500 else "")
                docs.append(f"[Source PDF: {pdf_name}]\n[Chunk ID: {chunk_id}]\n{excerpt}")
            
            retrieved_docs = "\n\n".join(docs)
            
            # Formater le prompt
            prompt = format_prompt(
                self.analysis_prompt_template, 
                claim=claim, 
                retrieved_docs=retrieved_docs
            )
            
            # Générer la réponse avec température très basse pour être décisif
            response = self.ollama_client.generate(
                prompt, 
                temperature=0.01  # Température très basse pour des réponses décisives et cohérentes
            )
            
            return prompt, response
            
        except Exception as e:
            return "", f"Erreur lors de l'analyse: {str(e)}"
    
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parser la réponse LLM pour extraire les informations (même format que l'app Streamlit)"""
        try:
            lines = response.strip().split('\n')
            result = {
                'verdict': 'UNVERIFIABLE',
                'confidence': 'MEDIUM',  # Valeur par défaut
                'explanation': 'Impossible de parser la réponse LLM',
                'sources': []
            }
            
            current_section = None
            explanation_lines = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('VERDICT:'):
                    verdict = line.replace('VERDICT:', '').strip()
                    if verdict in ['TRUE', 'FALSE', 'UNVERIFIABLE']:
                        result['verdict'] = verdict
                    current_section = 'verdict'
                elif line.startswith('EXPLANATION:'):
                    current_section = 'explanation'
                    # Commencer à collecter l'explication
                    explanation_text = line.replace('EXPLANATION:', '').strip()
                    if explanation_text:
                        explanation_lines.append(explanation_text)
                elif current_section == 'explanation' and line:
                    # Continuer à collecter l'explication
                    explanation_lines.append(line)
            
            # Joindre toutes les lignes d'explication
            if explanation_lines:
                result['explanation'] = '\n'.join(explanation_lines)
            else:
                # Si pas d'explication trouvée, prendre tout après VERDICT:
                response_parts = response.split('VERDICT:')
                if len(response_parts) > 1:
                    explanation_part = response_parts[1].split('\n', 1)
                    if len(explanation_part) > 1:
                        result['explanation'] = explanation_part[1].strip()
                    else:
                        result['explanation'] = "Pas d'explication fournie"
            
            # Déterminer la confiance basée sur le verdict et l'explication
            if result['verdict'] in ['TRUE', 'FALSE'] and len(result['explanation']) > 100:
                result['confidence'] = 'HIGH'
            elif result['verdict'] in ['TRUE', 'FALSE']:
                result['confidence'] = 'MEDIUM'
            else:
                result['confidence'] = 'LOW'
            
            return result
            
        except Exception as e:
            print(f"⚠️ Erreur parsing LLM: {e}")
            return {
                'verdict': 'UNVERIFIABLE',
                'confidence': 'LOW',
                'explanation': f'Erreur de parsing: {str(e)}',
                'sources': []
            }
    
    def calculate_certainty_score(self, similarity_scores: List[float], llm_result: Dict[str, Any]) -> float:
        """Calculer le score de certitude basé sur les similarités et le verdict LLM"""
        try:
            if not similarity_scores:
                return 0.0
            
            # Score basé sur la similarité moyenne
            avg_similarity = np.mean(similarity_scores)
            max_similarity = max(similarity_scores)
            
            # Score basé sur le verdict LLM
            verdict_scores = {
                'TRUE': 0.8,
                'FALSE': 0.8,
                'UNVERIFIABLE': 0.2
            }
            
            confidence_multipliers = {
                'HIGH': 1.0,
                'MEDIUM': 0.8,
                'LOW': 0.6
            }
            
            # Calculer le score final
            similarity_score = (avg_similarity * 0.6 + max_similarity * 0.4)
            verdict_score = verdict_scores.get(llm_result['verdict'], 0.5)
            confidence_multiplier = confidence_multipliers.get(llm_result['confidence'], 0.7)
            
            # Combiner les scores
            final_score = (similarity_score * 0.4 + verdict_score * 0.6) * confidence_multiplier
            
            # Normaliser entre 0 et 1
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            print(f"⚠️ Erreur calcul score: {e}")
            return 0.5
    
    async def fact_check_message(self, request: FactCheckRequest) -> FactCheckResponse:
        """Vérifier la véracité d'un message"""
        start_time = time.time()
        message_id = f"msg_{int(time.time() * 1000)}"
        
        try:
            # Démarrer la session de performance
            start_time = time.time()
            
            # Recherche quantique
            quantum_search_start = time.time()
            with time_operation_context("quantum_search"):
                results = retrieve_top_k(
                    request.message,
                    self.db_folder,
                    k=self.k_results,
                    n_qubits=self.n_qubits,
                    cassandra_manager=self.cassandra_manager
                )
            quantum_search_time = time.time() - quantum_search_start
            
            # Analyser les résultats
            chunk_ids = [chunk_id for score, qasm_path, chunk_id in results]
            similarity_scores = [score for score, qasm_path, chunk_id in results]
            
            # Générer la réponse LLM
            llm_start = time.time()
            with time_operation_context("llm_analysis"):
                prompt, llm_response = self.generate_llm_response(request.message, chunk_ids)
            llm_time = time.time() - llm_start
            
            # Parser la réponse LLM
            parsing_start = time.time()
            llm_result = self.parse_llm_response(llm_response)
            parsing_time = time.time() - parsing_start
            
            # Calculer le score de certitude
            score_start = time.time()
            certainty_score = self.calculate_certainty_score(similarity_scores, llm_result)
            score_time = time.time() - score_start
            
            # Récupérer les sources utilisées
            sources_start = time.time()
            sources_used = []
            for chunk_id in chunk_ids[:5]:  # Limiter aux 5 premières sources
                _, pdf_name = self.get_chunk_info(chunk_id)
                if pdf_name not in sources_used:
                    sources_used.append(pdf_name)
            sources_time = time.time() - sources_start
            
            # Log des métriques de performance
            print(f"\n⏱️ MÉTRIQUES DE PERFORMANCE:")
            print(f"{'='*80}")
            print(f"🔍 Recherche quantique: {quantum_search_time:.3f}s")
            print(f"🤖 Génération LLM: {llm_time:.3f}s")
            print(f"📝 Parsing LLM: {parsing_time:.3f}s")
            print(f"📊 Calcul score: {score_time:.3f}s")
            print(f"📚 Récupération sources: {sources_time:.3f}s")
            print(f"⏱️ Temps total: {time.time() - start_time:.3f}s")
            print(f"{'='*80}")
            
            # Log détaillé des chunks récupérés (top 10)
            print(f"\n🔍 TOP 10 CHUNKS RÉCUPÉRÉS PAR LE CIRCUIT QUANTIQUE:")
            print(f"{'='*80}")
            for i, (score, _qasm_path, chunk_id) in enumerate(results[:10]):
                chunk_text, pdf_name = self.get_chunk_info(chunk_id)
                excerpt = chunk_text[:200] + ("..." if len(chunk_text) > 200 else "")
                print(f"{i+1:2d}. Chunk: {chunk_id}")
                print(f"    📊 Similarité: {score:.4f}")
                print(f"    📄 PDF: {pdf_name}")
                print(f"    📝 Extrait: {excerpt}")
                print(f"    {'-'*60}")
            
            # Log de la réponse brute du LLM
            print(f"\n🤖 RÉPONSE BRUTE DU LLM (OLLAMA):")
            print(f"{'='*80}")
            print(f"📝 Prompt envoyé:")
            print(f"{'='*40}")
            print(prompt)
            print(f"{'='*40}")
            print(f"📤 Réponse brute reçue:")
            print(f"{'='*40}")
            print(llm_response)
            print(f"{'='*40}")
            
            processing_time = time.time() - start_time
            
            return FactCheckResponse(
                message_id=message_id,
                certainty_score=certainty_score,
                verdict=llm_result['verdict'],
                explanation=llm_result['explanation'],
                confidence_level=llm_result['confidence'],
                sources_used=sources_used,
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
            )
            
        except Exception as e:
            print(f"❌ Erreur fact-checking: {e}")
            processing_time = time.time() - start_time
            
            return FactCheckResponse(
                message_id=message_id,
                certainty_score=0.0,
                verdict="UNVERIFIABLE",
                explanation=f"Erreur lors de la vérification: {str(e)}",
                confidence_level="LOW",
                sources_used=[],
                processing_time=processing_time,
                timestamp=datetime.now().isoformat()
            )

# Instance globale de l'API
api_instance = None

@app.on_event("startup")
async def startup_event():
    """Événement de démarrage de l'API"""
    global api_instance
    try:
        api_instance = QuantumFactCheckerAPI()
        print("🚀 API Quantum Fact-Checker démarrée avec succès!")
    except Exception as e:
        print(f"❌ Erreur de démarrage: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint racine"""
    return {
        "message": "Quantum Fact-Checker API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de santé de l'API"""
    try:
        # Test des composants
        quantum_status = "OK"
        cassandra_status = "OK"
        ollama_status = "OK"
        
        # Test Ollama
        try:
            test_response = api_instance.ollama_client.generate("Test", max_tokens=5)
            ollama_status = "OK"
        except:
            ollama_status = "ERROR"
        
        # Test Cassandra
        try:
            test_query = f"SELECT COUNT(*) FROM {api_instance.cassandra_manager.keyspace}.{api_instance.cassandra_manager.table_name} LIMIT 1"
            api_instance.cassandra_manager.session.execute(test_query)
            cassandra_status = "OK"
        except:
            cassandra_status = "ERROR"
        
        return HealthResponse(
            status="healthy" if all(s == "OK" for s in [quantum_status, cassandra_status, ollama_status]) else "degraded",
            quantum_system=quantum_status,
            cassandra_status=cassandra_status,
            ollama_status=ollama_status,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            quantum_system="ERROR",
            cassandra_status="ERROR",
            ollama_status="ERROR",
            timestamp=datetime.now().isoformat()
        )

@app.post("/fact-check", response_model=FactCheckResponse)
async def fact_check(request: FactCheckRequest):
    """Vérifier la véracité d'un message"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API non initialisée")
    
    try:
        result = await api_instance.fact_check_message(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification: {str(e)}")

@app.post("/fact-check/batch", response_model=List[FactCheckResponse])
async def fact_check_batch(requests: List[FactCheckRequest]):
    """Vérifier plusieurs messages en lot"""
    if not api_instance:
        raise HTTPException(status_code=503, detail="API non initialisée")
    
    try:
        results = []
        for request in requests:
            result = await api_instance.fact_check_message(request)
            results.append(result)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification en lot: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Obtenir les statistiques de l'API"""
    try:
        performance_summary = get_performance_summary()
        return {
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": performance_summary,
            "system_info": {
                "n_qubits": api_instance.n_qubits,
                "db_folder": api_instance.db_folder,
                "k_results": api_instance.k_results
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des stats: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "quantum_fact_checker_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
