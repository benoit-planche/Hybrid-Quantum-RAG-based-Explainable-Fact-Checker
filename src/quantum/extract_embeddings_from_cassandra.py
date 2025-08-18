import os
import sys
import numpy as np
from qiskit import QuantumCircuit
from sklearn.decomposition import PCA

# Ajouter le dossier system au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../system')))
from cassandra_manager import create_cassandra_manager

def angle_encoding(vec):
    n_qubits = len(vec)
    qc = QuantumCircuit(n_qubits)
    for i, angle in enumerate(vec):
        qc.ry(angle, i)
    return qc

def encode_and_save_embedding(embedding, chunk_id, db_folder):
    n_qubits = len(embedding)
    # Normalisation entre 0 et pi
    vec = np.array(embedding, dtype=float)
    if np.max(np.abs(vec)) > 0:
        vec = (vec - np.min(vec)) / (np.max(vec) - np.min(vec)) * np.pi
    qc = angle_encoding(vec)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    qasm_path = os.path.join(db_folder, f"{chunk_id}.qasm")
    with open(qasm_path, 'w') as f:
        try:
            import qiskit.qasm2
            qasm_str = qiskit.qasm2.dumps(qc)
        except Exception:
            try:
                qasm_str = qc.qasm()
            except Exception as e:
                raise RuntimeError("Impossible de générer le QASM : vérifie ta version de Qiskit.") from e
        f.write(qasm_str)
    return qasm_path

def extract_and_encode_all(db_folder, n_qubits=16):
    print("Connexion à Cassandra...")
    cassandra_manager = create_cassandra_manager(table_name="fact_checker_docs", keyspace="fact_checker_keyspace")
    print("Extraction des chunks et embeddings...")
    all_chunks = cassandra_manager.get_all_chunks_with_embeddings()
    print(f"{len(all_chunks)} chunks trouvés.")
    # Collecte tous les embeddings pour PCA
    embeddings = [np.array(chunk['embedding'], dtype=float) for chunk in all_chunks]
    print(f"Réduction de dimension à {n_qubits} qubits avec PCA...")
    pca = PCA(n_components=n_qubits)
    reduced_embeddings = pca.fit_transform(embeddings)
    for i, chunk in enumerate(all_chunks):
        chunk_id = chunk['id'] if 'id' in chunk else f"chunk_{i}"
        embedding_reduced = reduced_embeddings[i]
        print(f"[{i+1}/{len(all_chunks)}] Encodage du chunk {chunk_id}...")
        encode_and_save_embedding(embedding_reduced, chunk_id, db_folder)
    print(f"🎉 Tous les embeddings ont été réduits et encodés (PCA {n_qubits}D) et stockés dans {db_folder}")

if __name__ == "__main__":
    db_folder = "src/quantum/quantum_db/"
    extract_and_encode_all(db_folder, n_qubits=16) 