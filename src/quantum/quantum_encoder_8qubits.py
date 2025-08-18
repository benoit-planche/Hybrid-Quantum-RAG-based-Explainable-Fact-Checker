import os
import numpy as np
from qiskit import QuantumCircuit
from sklearn.decomposition import PCA

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

def true_amplitude_encoding_8qubits(vec, n_qubits=8):
    """
    Vraie amplitude encoding pour 8 qubits utilisant l'algorithme de Grover-Rudolph
    """
    # Normaliser le vecteur
    vec = np.array(vec, dtype=float)
    if np.linalg.norm(vec) > 0:
        vec = vec / np.linalg.norm(vec)
    
    # Limiter à 256 amplitudes (2^8)
    if len(vec) > 256:
        vec = vec[:256]
    elif len(vec) < 256:
        vec = np.pad(vec, (0, 256 - len(vec)), 'constant')
    
    # Créer le circuit avec 8 qubits
    qc = QuantumCircuit(8)
    
    # Algorithme d'amplitude encoding récursif
    def encode_amplitudes(amplitudes, qubit_idx, start_idx, end_idx):
        if qubit_idx >= 8:
            return
        
        # Calculer les probabilités pour ce niveau
        mid = (start_idx + end_idx) // 2
        left_norm = np.linalg.norm(amplitudes[start_idx:mid])
        right_norm = np.linalg.norm(amplitudes[mid:end_idx])
        total_norm = np.linalg.norm(amplitudes[start_idx:end_idx])
        
        if total_norm > 0:
            # Calculer l'angle de rotation
            cos_theta = left_norm / total_norm
            theta = 2 * np.arccos(np.clip(cos_theta, 0, 1))
            
            # Appliquer la rotation
            qc.ry(theta, qubit_idx)
            
            # Récursion pour les sous-arbres
            if left_norm > 0:
                encode_amplitudes(amplitudes, qubit_idx + 1, start_idx, mid)
            if right_norm > 0:
                encode_amplitudes(amplitudes, qubit_idx + 1, mid, end_idx)
    
    # Démarrer l'encodage récursif
    encode_amplitudes(vec, 0, 0, len(vec))
    
    return qc

def sophisticated_amplitude_encoding_8qubits(vec, n_qubits=8):
    """
    Amplitude encoding sophistiqué pour 8 qubits avec meilleure différenciation
    """
    # Normaliser le vecteur
    vec = np.array(vec, dtype=float)
    if np.linalg.norm(vec) > 0:
        vec = vec / np.linalg.norm(vec)
    
    # Créer le circuit avec 8 qubits
    qc = QuantumCircuit(8)
    
    # Encodage sophistiqué utilisant l'espace complet 2^8 = 256 états
    # Diviser le vecteur en 8 parties et encoder chaque partie sur un qubit
    
    # Méthode 1: Encodage par qubit avec rotations multiples
    for i in range(8):
        # Utiliser différentes caractéristiques du vecteur pour chaque qubit
        if i < len(vec):
            # Rotation principale basée sur la valeur du vecteur
            angle1 = 2 * np.arccos(np.clip(abs(vec[i]), 0, 1))
            qc.ry(angle1, i)
            
            # Rotation secondaire basée sur la position relative
            angle2 = (i / 8.0) * np.pi
            qc.rz(angle2, i)
            
            # Rotation tertiaire basée sur la variance locale
            if i > 0 and i < len(vec) - 1:
                local_var = np.var(vec[max(0, i-1):min(len(vec), i+2)])
                angle3 = np.arctan2(local_var, abs(vec[i]))
                qc.rx(angle3, i)
    
    # Méthode 2: Entrelacement entre qubits pour capturer les corrélations
    for i in range(7):
        if i < len(vec) - 1:
            # Calculer la corrélation entre qubits adjacents
            correlation = vec[i] * vec[i+1]
            if abs(correlation) > 0.01:  # Seuil pour éviter le bruit
                # Appliquer une porte CNOT pour entrelacer
                qc.cx(i, i+1)
                
                # Rotation conditionnelle basée sur la corrélation
                angle_corr = np.arctan2(correlation, 1.0)
                qc.rz(angle_corr, i+1)
    
    # Méthode 3: Encodage global avec Hadamard pour superposition
    # Appliquer Hadamard sur les premiers qubits pour créer de la superposition
    for i in range(4):
        qc.h(i)
    
    # Méthode 4: Encodage différentiel
    # Encoder les différences entre composantes consécutives
    for i in range(7):
        if i < len(vec) - 1:
            diff = vec[i+1] - vec[i]
            angle_diff = np.arctan2(diff, 1.0)
            qc.ry(angle_diff, i)
    
    return qc

def improved_amplitude_encoding_8qubits(vec, n_qubits=8):
    """
    Amplitude encoding optimisé pour 8 qubits avec meilleure différenciation
    """
    # Normaliser le vecteur
    vec = np.array(vec, dtype=float)
    if np.linalg.norm(vec) > 0:
        vec = vec / np.linalg.norm(vec)
    
    # Créer le circuit avec 8 qubits
    qc = QuantumCircuit(8)
    
    # Encodage amplitude amélioré avec rotations multiples
    for i in range(8):
        # Extraire les amplitudes pour ce qubit (32 amplitudes par qubit)
        start_idx = i * 32
        end_idx = (i + 1) * 32
        amplitudes = vec[start_idx:end_idx]
        
        # Calculer plusieurs angles pour ce qubit
        mean_amp = np.mean(np.abs(amplitudes))
        std_amp = np.std(amplitudes)
        max_amp = np.max(np.abs(amplitudes))
        
        # Rotation principale basée sur la moyenne
        angle1 = 2 * np.arccos(np.clip(mean_amp, 0, 1))
        qc.ry(angle1, i)
        
        # Rotation secondaire basée sur la variance (pour différenciation)
        if std_amp > 0:
            angle2 = np.arctan2(std_amp, mean_amp)
            qc.rz(angle2, i)
        
        # Rotation tertiaire basée sur le maximum
        if max_amp > 0:
            angle3 = np.arcsin(np.clip(max_amp, 0, 1))
            qc.rx(angle3, i)
    
    return qc

def encode_and_save_embedding_amplitude_8qubits(vector, chunk_id, qasm_dir):
    """
    Encode et sauvegarde un embedding avec amplitude encoding 8 qubits
    """
    # Créer le circuit quantique avec l'encodage sophistiqué
    qc = sophisticated_amplitude_encoding_8qubits(vector, n_qubits=8)
    
    # Convertir en QASM (méthode correcte pour Qiskit 2.x)
    try:
        from qiskit.qasm2 import dumps
        qasm_str = dumps(qc)
    except ImportError:
        # Fallback pour les versions plus anciennes
        try:
            qasm_str = qc.qasm()
        except AttributeError:
            qasm_str = qc.qasm(formatted=True)
    
    # Sauvegarder le fichier QASM
    qasm_filename = f"{chunk_id}_8qubits.qasm"
    qasm_path = os.path.join(qasm_dir, qasm_filename)
    
    with open(qasm_path, 'w') as f:
        f.write(qasm_str)
    
    return qasm_path

def load_qasm_circuit_8qubits(qasm_path):
    """
    Charge un circuit QASM 8 qubits
    """
    from qiskit import QuantumCircuit
    return QuantumCircuit.from_qasm_file(qasm_path)
