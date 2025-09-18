#!/usr/bin/env python3
"""
Script d'indexation des documents PDF pour la recherche documentaire quantique
Extrait le texte des PDF, encode en circuits quantiques, sauvegarde en QASM
"""

import os
import sys
from pdf_extractor import extract_texts_from_folder
from quantum_encoder import encode_and_save

def index_documents(pdf_folder, db_folder, n_qubits=8):
    """Indexe tous les PDF d'un dossier en circuits quantiques QASM."""
    print(f"🔍 Extraction des PDF depuis : {pdf_folder}")
    docs = extract_texts_from_folder(pdf_folder)
    print(f"📄 {len(docs)} documents PDF trouvés")
    
    print(f"🔬 Encodage quantique avec {n_qubits} qubits...")
    for i, (fname, text) in enumerate(docs):
        doc_id = os.path.splitext(fname)[0]
        print(f"  [{i+1}/{len(docs)}] Encodage de {fname}...")
        qasm_path = encode_and_save(text, doc_id, db_folder, n_qubits=n_qubits)
        print(f"     ✅ Circuit sauvegardé : {qasm_path}")
    
    print(f"\n🎉 Indexation terminée ! {len(docs)} circuits QASM créés dans {db_folder}")

if __name__ == "__main__":
    # Paramètres par défaut
    pdf_folder = "/home/moi/Documents/internship/climat-misinformation-detection/rapport"
    db_folder = "src/quantum/quantum_db/"
    n_qubits = 8
    
    # Permettre de changer les paramètres via ligne de commande
    if len(sys.argv) > 1:
        pdf_folder = sys.argv[1]
    if len(sys.argv) > 2:
        db_folder = sys.argv[2]
    if len(sys.argv) > 3:
        n_qubits = int(sys.argv[3])
    
    print("🚀 Démarrage de l'indexation des documents PDF")
    print(f"📁 Dossier PDF : {pdf_folder}")
    print(f"💾 Dossier QASM : {db_folder}")
    print(f"🔢 Nombre de qubits : {n_qubits}")
    print("-" * 50)
    
    index_documents(pdf_folder, db_folder, n_qubits) 