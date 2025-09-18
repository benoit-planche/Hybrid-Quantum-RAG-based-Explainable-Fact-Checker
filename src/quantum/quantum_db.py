import os
from qiskit import QuantumCircuit

def list_qasm_files(db_folder):
    """Liste les fichiers QASM présents dans le dossier."""
    return [os.path.join(db_folder, f) for f in os.listdir(db_folder) if f.endswith('.qasm')]

def load_qasm_circuit(qasm_path):
    """Charge un circuit Qiskit depuis un fichier QASM."""
    with open(qasm_path, 'r') as f:
        qasm_str = f.read()
    qc = QuantumCircuit.from_qasm_str(qasm_str)
    return qc

def save_qasm_circuit(qc, qasm_path):
    """Sauvegarde un circuit Qiskit en fichier QASM."""
    try:
        # Essayer d'abord la méthode moderne (Qiskit >= 1.0)
        from qiskit.qasm2 import dumps
        qasm_str = dumps(qc)
    except ImportError:
        # Fallback pour les versions plus anciennes
        try:
            qasm_str = qc.qasm()
        except AttributeError:
            qasm_str = qc.qasm(formatted=True)
    
    with open(qasm_path, 'w') as f:
        f.write(qasm_str)

# Exemple d'utilisation :
# files = list_qasm_files('quantum_db/')
# qc = load_qasm_circuit(files[0]) 