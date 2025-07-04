#!/usr/bin/env python3
"""
Chargeur de documents PDF simple pour le fact-checker
"""

import os
import PyPDF2
from typing import List, Dict, Any

class PDFDocumentLoader:
    """Chargeur simple pour les fichiers PDF"""
    
    @staticmethod
    def load_directory(directory_path: str) -> List[Dict[str, Any]]:
        """Charge tous les fichiers PDF d'un répertoire"""
        documents = []
        
        if not os.path.exists(directory_path):
            print(f"Le répertoire {directory_path} n'existe pas")
            return documents
        
        # Parcourir tous les fichiers du répertoire
        for filename in os.listdir(directory_path):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(directory_path, filename)
                try:
                    # Extraire le texte du PDF
                    text = PDFDocumentLoader.extract_text_from_pdf(file_path)
                    if text.strip():  # Vérifier que le texte n'est pas vide
                        documents.append({
                            'page_content': text,
                            'metadata': {
                                'source': filename,
                                'file_path': file_path
                            }
                        })
                        print(f"✅ Chargé: {filename}")
                    else:
                        print(f"⚠️ Fichier vide: {filename}")
                except Exception as e:
                    print(f"❌ Erreur lors du chargement de {filename}: {e}")
        
        return documents
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extrait le texte d'un fichier PDF"""
        text = ""
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extraire le texte de toutes les pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
        except Exception as e:
            print(f"Erreur lors de l'extraction du texte de {file_path}: {e}")
            return ""
        
        return text.strip()
    
    @staticmethod
    def load_single_pdf(file_path: str) -> Dict[str, Any]:
        """Charge un seul fichier PDF"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Le fichier {file_path} n'existe pas")
        
        text = PDFDocumentLoader.extract_text_from_pdf(file_path)
        filename = os.path.basename(file_path)
        
        return {
            'page_content': text,
            'metadata': {
                'source': filename,
                'file_path': file_path
            }
        } 