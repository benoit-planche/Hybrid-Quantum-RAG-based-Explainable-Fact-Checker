import os
import numpy as np
from qiskit import QuantumCircuit
from sklearn.decomposition import PCA # Added for PCA

def text_to_vector(text, n_qubits):
    vec = [ord(c) for c in text if ord(c) < 128]
    vec = np.array(vec, dtype=float)
    if len(vec) < n_qubits:
        vec = np.pad(vec, (0, n_qubits - len(vec)), 'constant')
    else:
        vec = vec[:n_qubits]
    if np.max(vec) > 0:
        vec = (vec / np.max(vec)) * np.pi
    return vec

def angle_encoding(vec):
    n_qubits = len(vec)
    qc = QuantumCircuit(n_qubits)
    for i, angle in enumerate(vec):
        qc.ry(angle, i)
    return qc

def improved_amplitude_encoding(vec, n_qubits=None):
    """
    Amélioration de l'amplitude encoding pour une meilleure différenciation.
    Utilise une approche plus sophistiquée avec des rotations conditionnelles
    et une meilleure représentation des amplitudes.
    """
    if n_qubits is None:
        n_qubits = len(vec)
    
    # Normaliser le vecteur
    norm = np.linalg.norm(vec)
    if norm == 0:
        normalized = np.zeros(n_qubits)
        normalized[0] = 1.0
    else:
        normalized = vec / norm
    
    # S'assurer que la dimension correspond
    if len(normalized) < n_qubits:
        normalized = np.pad(normalized, (0, n_qubits - len(normalized)), 'constant')
    else:
        normalized = normalized[:n_qubits]
    
    # Re-normaliser après padding
    norm = np.linalg.norm(normalized)
    if norm > 0:
        normalized = normalized / norm
    
    # Créer le circuit quantique
    qc = QuantumCircuit(n_qubits)
    
    # Amélioration 1: Utiliser des rotations plus sophistiquées
    # avec des angles non-linéaires pour mieux différencier les amplitudes
    
    for i in range(min(len(normalized), n_qubits)):
        if abs(normalized[i]) > 1e-10:
            amplitude = abs(normalized[i])
            
            # Amélioration 2: Utiliser une fonction non-linéaire pour l'angle
            # Cela permet une meilleure différenciation des amplitudes
            if amplitude < 0.1:
                # Pour les petites amplitudes, utiliser une échelle logarithmique
                angle = np.arcsin(amplitude * 2)  # Amplifier les petites valeurs
            else:
                # Pour les grandes amplitudes, utiliser une échelle plus sensible
                angle = np.arcsin(amplitude) + 0.1 * amplitude  # Ajouter un terme non-linéaire
            
            # Amélioration 3: Utiliser des rotations composées
            qc.ry(2 * angle, i)
            
            # Amélioration 4: Ajouter des rotations de phase pour capturer plus d'information
            if i > 0 and abs(normalized[i]) > 0.1:
                phase_angle = np.arctan2(normalized[i], normalized[i-1]) if i > 0 else 0
                qc.rz(phase_angle, i)
    
    return qc

def amplitude_encoding(vec, n_qubits=None):
    """
    Encode un vecteur dans les amplitudes d'un état quantique.
    Version améliorée pour une meilleure différenciation.
    """
    return improved_amplitude_encoding(vec, n_qubits)

def encode_and_save_embedding(embedding, chunk_id, db_folder): # Renamed from encode_and_save
    n_qubits = len(embedding)
    vec = np.array(embedding, dtype=float)
    if np.max(np.abs(vec)) > 0:
        vec = (vec - np.min(vec)) / (np.max(vec) - np.min(vec)) * np.pi
    qc = angle_encoding(vec)
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    qasm_path = os.path.join(db_folder, f"{chunk_id}.qasm")
    with open(qasm_path, 'w') as f:
        try:
            # Qiskit >= 1.0
            import qiskit.qasm2
            qasm_str = qiskit.qasm2.dumps(qc)
        except Exception:
            try:
                # Qiskit < 1.0
                qasm_str = qc.qasm()
            except Exception as e:
                raise RuntimeError("Impossible de générer le QASM : vérifie ta version de Qiskit.") from e
        f.write(qasm_str)
    return qasm_path

def encode_and_save_embedding_amplitude(embedding, chunk_id, db_folder):
    """
    Encode un embedding avec amplitude encoding et sauvegarde en QASM
    """
    n_qubits = len(embedding)
    vec = np.array(embedding, dtype=float)
    
    # Utiliser amplitude encoding au lieu d'angle encoding
    qc = amplitude_encoding(vec, n_qubits)
    
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    qasm_path = os.path.join(db_folder, f"{chunk_id}.qasm")
    with open(qasm_path, 'w') as f:
        try:
            # Qiskit >= 1.0
            import qiskit.qasm2
            qasm_str = qiskit.qasm2.dumps(qc)
        except Exception:
            try:
                # Qiskit < 1.0
                qasm_str = qc.qasm()
            except Exception as e:
                raise RuntimeError("Impossible de générer le QASM : vérifie ta version de Qiskit.") from e
        f.write(qasm_str)
    return qasm_path 