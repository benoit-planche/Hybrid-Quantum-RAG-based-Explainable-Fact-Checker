import os
import numpy as np
from qiskit_aer import Aer
from qiskit import transpile
from quantum_encoder import text_to_vector, angle_encoding, amplitude_encoding
from quantum_db import list_qasm_files, load_qasm_circuit
from performance_metrics import time_operation, time_operation_context, log_quantum_operation
import logging
import time

# Configuration des logs pour supprimer Qiskit et autres bruits
import logging
logging.getLogger('qiskit').setLevel(logging.ERROR)
logging.getLogger('qiskit.passmanager').setLevel(logging.ERROR)
logging.getLogger('qiskit.compiler').setLevel(logging.ERROR)
logging.getLogger('qiskit.transpiler').setLevel(logging.ERROR)
logging.getLogger('qiskit.quantum_info').setLevel(logging.ERROR)
logging.getLogger('performance_metrics').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

@time_operation("quantum_overlap_calculation")
def quantum_overlap_similarity(qc1, qc2):
    """Calcule l'overlap (fidelity) entre deux circuits via simulation Qiskit Aer."""
    try:
        backend = Aer.get_backend('statevector_simulator')
        qc1_t = transpile(qc1, backend)
        qc2_t = transpile(qc2, backend)
        state1 = backend.run(qc1_t).result().get_statevector()
        state2 = backend.run(qc2_t).result().get_statevector()
        
        # Calculer la fidélité (overlap) entre les deux états quantiques
        # La fidélité est |<ψ1|ψ2>|²
        overlap = np.abs(np.vdot(state1, state2)) ** 2
        
        # Amélioration: Appliquer une transformation non-linéaire pour mieux différencier
        # Cela permet d'avoir une meilleure séparation entre les similarités
        if overlap > 0.9:
            # Pour les très hautes similarités, appliquer une compression
            overlap = 0.9 + 0.1 * (overlap - 0.9) ** 2
        elif overlap < 0.1:
            # Pour les très basses similarités, appliquer une expansion
            overlap = overlap ** 0.5
        
        return overlap
    except Exception as e:
        print(f"⚠️ Erreur dans quantum_overlap_similarity: {e}")
        print(f"   Circuit 1: {qc1.name if hasattr(qc1, 'name') else 'Unknown'}")
        print(f"   Circuit 2: {qc2.name if hasattr(qc2, 'name') else 'Unknown'}")
        print(f"   Circuit 1 num_qubits: {qc1.num_qubits if hasattr(qc1, 'num_qubits') else 'Unknown'}")
        print(f"   Circuit 2 num_qubits: {qc2.num_qubits if hasattr(qc2, 'num_qubits') else 'Unknown'}")
        # Fallback vers une similarité basique
        return 0.5

@time_operation("retrieve_top_k_search")
def retrieve_top_k(query_text, db_folder, k=5, n_qubits=16, cassandra_manager=None):
    """
    Encode la requête avec embedding sémantique + PCA fixe + amplitude encoding, 
    charge tous les circuits QASM, calcule l'overlap, retourne les top-k chunks.
    """
    with time_operation_context("query_encoding", {"n_qubits": n_qubits, "query_length": len(query_text)}):
        if cassandra_manager is None:
            print("⚠️ Aucun cassandra_manager fourni, utilisation de l'ancienne méthode")
            # Fallback vers l'ancienne méthode
            vec = text_to_vector(query_text, n_qubits)
            qc_query = angle_encoding(vec)
        else:
            # Utiliser l'embedding sémantique + PCA fixe + amplitude encoding
            print("🔄 Génération de l'embedding sémantique pour la requête...")
            with time_operation_context("semantic_embedding_generation"):
                query_embedding = cassandra_manager.embed_model.get_text_embedding_batch([query_text])[0]
            
            # Charger le PCA fixe sauvegardé
            with time_operation_context("pca_loading"):
                try:
                    import joblib
                    pca_model_path = "src/quantum/pca_model_8qubits.pkl"
                    if os.path.exists(pca_model_path):
                        pca = joblib.load(pca_model_path)
                        print("✅ PCA fixe chargé depuis le fichier")
                    else:
                        print("⚠️ PCA fixe non trouvé, utilisation du PCA dynamique")
                        # Fallback vers l'ancienne méthode
                        all_chunks = cassandra_manager.get_all_chunks_with_embeddings()
                        all_embeddings = [np.array(c['embedding'], dtype=float) for c in all_chunks]
                        from sklearn.decomposition import PCA
                        pca = PCA(n_components=n_qubits)
                        pca.fit(all_embeddings)
                except Exception as e:
                    print(f"❌ Erreur chargement PCA: {e}")
                    # Fallback vers l'ancienne méthode
                    all_chunks = cassandra_manager.get_all_chunks_with_embeddings()
                    all_embeddings = [np.array(c['embedding'], dtype=float) for c in all_chunks]
                    from sklearn.decomposition import PCA
                    pca = PCA(n_components=n_qubits)
                    pca.fit(all_embeddings)
            
            # Réduire l'embedding de la requête avec PCA fixe
            with time_operation_context("pca_transformation"):
                query_emb_reduced = pca.transform([query_embedding])[0]
            
            # Utiliser amplitude encoding (pas de normalisation destructive)
            with time_operation_context("amplitude_encoding"):
                qc_query = amplitude_encoding(query_emb_reduced, n_qubits)
    
    # Pré-filtrer les candidats via Cassandra pour limiter le nombre de QASM comparés
    if cassandra_manager is not None:
        try:
            # Récupérer les 100 meilleurs candidats via recherche vectorielle sur les embeddings
            print(f"🔍 Recherche vectorielle sur les embeddings pour la requête: '{query_text[:50]}...'")
            
            # Étape 1: Calculer l'embedding de la requête
            from ollama import Client
            client = Client(host='http://localhost:11434')
            
            # Générer l'embedding de la requête
            query_embedding = client.embeddings(model='llama2:7b', prompt=query_text)
            query_vector = query_embedding['embedding']
            
            print(f"📊 Embedding de la requête calculé: {len(query_vector)} dimensions")
            
            # Étape 2: Récupérer TOUS les embeddings stockés et calculer les similarités
            query_cql = "SELECT row_id, metadata_s, body_blob, vector FROM fact_checker_keyspace.fact_checker_docs"
            rows = cassandra_manager.session.execute(query_cql)
            
            # Calculer les similarités et trier
            similarities = []
            total_chunks = 0
            processed_chunks = 0
            
            print(f"🧮 Calcul des similarités cosinus sur tous les chunks...")
            for row in rows:
                total_chunks += 1
                if hasattr(row, 'vector') and row.vector:
                    processed_chunks += 1
                    # Calculer la similarité cosinus
                    doc_vector = row.vector
                    # Utiliser numpy pour la similarité cosinus
                    similarity = np.dot(query_vector, doc_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(doc_vector))
                    
                    # Utiliser row_id directement car metadata_s est None
                    raw_chunk_id = row.row_id
                    
                    # Extraire le numéro du chunk depuis row_id (ex: 'doc_0' → '0')
                    if raw_chunk_id.startswith('doc_'):
                        chunk_id = raw_chunk_id.replace('doc_', '')
                    else:
                        chunk_id = str(raw_chunk_id)
                    
                    similarities.append((similarity, {
                        'metadata': {'chunk_id': chunk_id},
                        'id': row.row_id,
                        'chunk_id': chunk_id,
                        'content': row.body_blob,
                        'source': 'unknown'  # metadata_s est None
                    }))
                    
                    # Afficher le progrès tous les 1000 chunks
                    if processed_chunks % 1000 == 0:
                        print(f"   📊 {processed_chunks} chunks traités...")
            
            print(f"📊 Total chunks dans la base: {total_chunks}")
            print(f"📊 Chunks avec embeddings: {processed_chunks}")
            print(f"📊 Chunks traités pour similarité: {len(similarities)}")
            
            # Trier par similarité décroissante et prendre les 100 meilleurs
            similarities.sort(reverse=True, key=lambda x: x[0])
            base_results = [item[1] for item in similarities[:100]]
            
            print(f"🔍 Recherche vectorielle terminée: {len(base_results)} meilleurs candidats trouvés")
            if base_results:
                print(f"📊 Similarité max: {similarities[0][0]:.4f}, min: {similarities[-1][0]:.4f}")
                print(f"🔍 Top 5 documents par similarité vectorielle:")
                for i, (score, doc) in enumerate(similarities[:5]):
                    chunk_id = doc['chunk_id']
                    source = doc['source']
                    print(f"   {i+1}. Chunk {chunk_id} (Similarité: {score:.4f}) - {source}")
            
            # Construire la liste des fichiers QASM candidats
            candidate_files = []
            print(f"🔍 Construction des candidats QASM...")
            print(f"📁 Dossier QASM: {db_folder}")
            
            for i, res in enumerate(base_results):  # Traiter TOUS les candidats
                chunk_id = res.get('metadata', {}).get('chunk_id') or res.get('id') or res.get('chunk_id')
                print(f"   📝 Résultat {i+1}: chunk_id = '{chunk_id}'")
                
                if chunk_id:
                    # Adapter le nom du fichier QASM selon le format réel
                    if n_qubits == 4:
                        # Format: 0 → embedding_4qubits_None_doc_0.qasm
                        qasm_name = f"embedding_4qubits_None_doc_{chunk_id}.qasm"
                    else:
                        # Format pour 8 qubits ou autres
                        qasm_name = f"{chunk_id}.qasm"
                    
                    qasm_path = os.path.join(db_folder, qasm_name)
                    if os.path.exists(qasm_path):
                        candidate_files.append(qasm_path)
                        print(f"      ✅ AJOUTÉ")
                    else:
                        print(f"      ❌ NON TROUVÉ")
                else:
                    print(f"      ⚠️ Pas de chunk_id")
            
            print(f"\n🔍 {len(candidate_files)} fichiers QASM candidats trouvés")
            
            # Utiliser les candidats si on en a trouvé
            if len(candidate_files) > 0:
                qasm_files = candidate_files
                logger.info(f"SYSTÈME HYBRIDE ACTIVÉ: {len(qasm_files)} candidats au lieu de tous les fichiers")
            else:
                qasm_files = list_qasm_files(db_folder)
                logger.warning(f"AUCUN CANDIDAT TROUVÉ, fallback sur {len(qasm_files)} fichiers QASM")
                
        except Exception as e:
            logger.error(f"Erreur pré-filtrage: {e}")
            qasm_files = list_qasm_files(db_folder)
            logger.warning(f"Fallback sur {len(qasm_files)} fichiers QASM")
    else:
        logger.warning("Pas de cassandra_manager, utilisation de tous les fichiers QASM")
        qasm_files = list_qasm_files(db_folder)
    
    logger.info(f"Début comparaison quantique sur {len(qasm_files)} fichiers")
    with time_operation_context("quantum_similarity_computation", {"n_files": len(qasm_files)}):
        scores = []
        for i, qasm_path in enumerate(qasm_files):
            with time_operation_context(f"circuit_comparison_{i}", {"file": qasm_path}):
                qc_doc = load_qasm_circuit(qasm_path)
                score = quantum_overlap_similarity(qc_query, qc_doc)
                # Extraire le chunk_id en gérant les préfixes/suffixes de nommage
                filename = os.path.basename(qasm_path).replace('.qasm', '')
                # Retirer le suffixe spécifique 8 qubits si présent
                if filename.endswith('_8qubits'):
                    filename = filename.replace('_8qubits', '')
                # Pour les QASM 4 qubits: 'embedding_4qubits_None_doc_XXXX' → 'doc_XXXX'
                if filename.startswith('embedding_4qubits_'):
                    filename = filename.replace('embedding_4qubits_', '')
                # Retirer le préfixe 'None_' si présent
                if filename.startswith('None_'):
                    filename = filename.replace('None_', '')
                chunk_id = filename
                scores.append((score, qasm_path, chunk_id))
    
    with time_operation_context("results_sorting"):
        scores.sort(reverse=True, key=lambda x: x[0])
    
    return scores[:k]

# Optionnel : fonction pour retrouver le texte original d'un chunk à partir de son id
# (à implémenter selon la façon dont tu stockes les textes)
def get_chunk_text(chunk_id, cassandra_manager):
    partition_id, row_id = chunk_id.split('_', 1)
    query = f"SELECT body_blob FROM {cassandra_manager.keyspace}.{cassandra_manager.table_name} WHERE partition_id=%s AND row_id=%s;"
    row = cassandra_manager.session.execute(query, (partition_id, row_id)).one()
    if row and row.body_blob:
        return row.body_blob
    return "[Texte non trouvé pour ce chunk]"

# Exemple d'utilisation :
# top_chunks = retrieve_top_k("ma requête", "quantum_db/", k=5, n_qubits=16, cassandra_manager=cassandra_manager)
# for score, path, chunk_id in top_chunks:
#     print(score, chunk_id, path) 