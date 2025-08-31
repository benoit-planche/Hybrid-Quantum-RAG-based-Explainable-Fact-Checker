#!/usr/bin/env python3
"""
Encodeur quantique optimisé pour 4 qubits
"""

import sys
import os
sys.path.append('system')
sys.path.append('src/quantum')

import numpy as np
import pickle
import os
from qiskit import QuantumCircuit
from sklearn.decomposition import PCA

def sophisticated_amplitude_encoding_4qubits(vec, n_qubits=4):
    """
    Amplitude encoding sophistiqué pour 4 qubits avec meilleure différenciation
    """
    # Normaliser le vecteur
    vec = np.array(vec, dtype=float)
    if np.linalg.norm(vec) > 0:
        vec = vec / np.linalg.norm(vec)

    # Créer le circuit avec 4 qubits
    qc = QuantumCircuit(4)

    # Encodage sophistiqué utilisant l'espace complet 2^4 = 16 états
    # Diviser le vecteur en 4 parties et encoder chaque partie sur un qubit

    # Méthode 1: Encodage par qubit avec rotations multiples
    for i in range(4):
        # Utiliser différentes caractéristiques du vecteur pour chaque qubit
        if i < len(vec):
            # Rotation principale basée sur la valeur du vecteur
            angle1 = np.arccos(np.clip(abs(vec[i]), 0, 1))
            
            # Rotation secondaire basée sur la position
            angle2 = np.arccos(np.clip(abs(vec[i] * (i + 1) / 4), 0, 1))
            
            # Rotation tertiaire basée sur la somme des valeurs précédentes
            prev_sum = sum(abs(vec[j]) for j in range(i)) if i > 0 else 0
            angle3 = np.arccos(np.clip(abs(vec[i] + prev_sum / 4), 0, 1))
            
            # Appliquer les rotations
            qc.rx(angle1, i)
            qc.ry(angle2, i)
            qc.rz(angle3, i)
        else:
            # Pour les qubits non utilisés, appliquer une rotation basée sur l'index
            angle = np.pi * (i + 1) / 8
            qc.rx(angle, i)
            qc.ry(angle * 0.5, i)

    # Ajouter des entanglements pour améliorer la différenciation
    for i in range(3):
        qc.cx(i, i + 1)
        qc.h(i)
        qc.h(i + 1)

    return qc

def encode_and_save_embedding_amplitude_4qubits(vector, chunk_id, qasm_dir):
    """
    Encode et sauvegarde un embedding avec amplitude encoding 4 qubits
    """
    # Créer le circuit quantique avec l'encodage sophistiqué
    qc = sophisticated_amplitude_encoding_4qubits(vector, n_qubits=4)
    
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
    
    # Sauvegarder le circuit QASM
    qasm_filename = f"embedding_4qubits_{chunk_id}.qasm"
    qasm_path = os.path.join(qasm_dir, qasm_filename)
    
    with open(qasm_path, 'w') as f:
        f.write(qasm_str)
    
    return qasm_path

def create_qasm_directory_4qubits():
    """
    Créer le répertoire pour les circuits QASM 4 qubits
    """
    qasm_dir = "qasm_circuits_4qubits"
    if not os.path.exists(qasm_dir):
        os.makedirs(qasm_dir)
        print(f"📁 Répertoire créé: {qasm_dir}")
    return qasm_dir

def load_qasm_circuit_4qubits(qasm_path):
    """
    Charge un circuit QASM 4 qubits
    """
    from qiskit import QuantumCircuit
    return QuantumCircuit.from_qasm_file(qasm_path)

if __name__ == "__main__":
    print("🔬 Test de l'encodeur quantique 4 qubits")
    
    # Test avec un vecteur simple
    test_vector = np.array([0.1, 0.3, 0.5, 0.7])
    print(f"📏 Vecteur de test: {test_vector}")
    
    # Créer le circuit
    qc = sophisticated_amplitude_encoding_4qubits(test_vector)
    print(f"🔧 Circuit créé avec {qc.num_qubits} qubits")
    
    # Afficher le circuit
    print("📋 Circuit généré:")
    print(qc)
    
    # Test de sauvegarde
    qasm_dir = create_qasm_directory_4qubits()
    qasm_path = encode_and_save_embedding_amplitude_4qubits(test_vector, "test", qasm_dir)
    print(f"💾 Circuit sauvegardé: {qasm_path}")
