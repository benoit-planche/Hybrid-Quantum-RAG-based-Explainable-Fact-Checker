import os
from typing import List, Tuple
from PyPDF2 import PdfReader

def extract_texts_from_folder(pdf_folder: str) -> List[Tuple[str, str]]:
    """Extrait le texte brut de tous les PDF d'un dossier.
    Retourne une liste de tuples (nom_fichier, texte)."""
    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]
    results = []
    for fname in pdf_files:
        path = os.path.join(pdf_folder, fname)
        try:
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or '' for page in reader.pages)
            results.append((fname, text))
        except Exception as e:
            print(f"Erreur lors de la lecture de {fname}: {e}")
    return results

# Exemple d'utilisation :
# pdf_folder = '/chemin/vers/tes/pdf'
# docs = extract_texts_from_folder(pdf_folder)
# for fname, text in docs:
#     print(fname, text[:200]) 