#!/usr/bin/env python3
"""
Debug de la structure des chunks
"""

import sys
import os
sys.path.append('system')
sys.path.append('src/quantum')

from cassandra_manager import CassandraVectorStoreManager

def debug_chunks_structure():
    """Debug de la structure des chunks"""
    
    print("🔍 Debug de la structure des chunks...")
    
    # Connexion à Cassandra
    cassandra_manager = CassandraVectorStoreManager()
    
    # Récupération de quelques chunks
    chunks = cassandra_manager.get_all_chunks_with_embeddings()
    print(f"📈 {len(chunks)} chunks récupérés")
    
    if len(chunks) > 0:
        # Analyser le premier chunk
        first_chunk = chunks[0]
        print(f"📊 Structure du premier chunk:")
        print(f"   Type: {type(first_chunk)}")
        print(f"   Clés: {list(first_chunk.keys()) if hasattr(first_chunk, 'keys') else 'Pas un dict'}")
        
        if hasattr(first_chunk, 'keys'):
            for key in first_chunk.keys():
                value = first_chunk[key]
                print(f"   {key}: {type(value)} - {str(value)[:100]}...")
        
        # Chercher les vecteurs
        print(f"\n🔍 Recherche des vecteurs...")
        vectors_found = 0
        for i, chunk in enumerate(chunks[:5]):
            if hasattr(chunk, 'keys') and 'vector' in chunk:
                vectors_found += 1
                print(f"   Chunk {i}: vector trouvé, type: {type(chunk['vector'])}")
            elif hasattr(chunk, 'vector'):
                vectors_found += 1
                print(f"   Chunk {i}: vector trouvé (attribut), type: {type(chunk.vector)}")
            else:
                print(f"   Chunk {i}: pas de vector")
        
        print(f"📊 Vecteurs trouvés: {vectors_found}/5")

if __name__ == "__main__":
    debug_chunks_structure()
