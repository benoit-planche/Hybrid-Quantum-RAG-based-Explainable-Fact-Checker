#!/bin/bash

# Script pour faire un dump de Cassandra via Docker
# Utilise le conteneur fact_checker_cassandra directement

echo "🚀 Début du dump Cassandra via Docker..."

# Créer le dossier de sortie
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR="cassandra_dump_docker_${TIMESTAMP}"
mkdir -p "$OUTPUT_DIR"

echo "📁 Dossier de sortie: $OUTPUT_DIR"

# Vérifier que le conteneur est en cours d'exécution
if ! docker ps | grep -q fact_checker_cassandra; then
    echo "❌ Conteneur fact_checker_cassandra non trouvé ou arrêté"
    echo "🔄 Démarrage du conteneur..."
    docker start fact_checker_cassandra
    echo "⏳ Attente du démarrage de Cassandra..."
    sleep 30
fi

# Attendre que Cassandra soit prêt
echo "⏳ Vérification que Cassandra est prêt..."
MAX_ATTEMPTS=10
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker exec fact_checker_cassandra cqlsh -e "SELECT release_version FROM system.local;" >/dev/null 2>&1; then
        echo "✅ Cassandra est prêt!"
        break
    else
        ATTEMPT=$((ATTEMPT + 1))
        echo "⏳ Tentative $ATTEMPT/$MAX_ATTEMPTS - Cassandra n'est pas encore prêt..."
        sleep 10
    fi
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo "❌ Cassandra n'est pas prêt après $MAX_ATTEMPTS tentatives"
    exit 1
fi

# Dump de la structure du keyspace
echo "🏗️ Export de la structure du keyspace..."
docker exec fact_checker_cassandra cqlsh -e "DESCRIBE KEYSPACE fact_checker_keyspace;" > "$OUTPUT_DIR/keyspace_structure.cql" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Structure du keyspace exportée"
else
    echo "⚠️ Erreur lors de l'export de la structure du keyspace"
fi

# Dump de la structure de la table
echo "📊 Export de la structure de la table..."
docker exec fact_checker_cassandra cqlsh -e "DESCRIBE TABLE fact_checker_keyspace.fact_checker_docs;" > "$OUTPUT_DIR/table_structure.cql" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Structure de la table exportée"
else
    echo "⚠️ Erreur lors de l'export de la structure de la table"
fi

# Dump des données en format brut
echo "📥 Export des données..."
docker exec fact_checker_cassandra cqlsh -e "SELECT * FROM fact_checker_keyspace.fact_checker_docs;" > "$OUTPUT_DIR/data_raw.txt" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Données exportées (format brut)"
    
    # Compter les lignes de données (exclure l'en-tête et les lignes vides)
    DATA_LINES=$(grep -v "^$" "$OUTPUT_DIR/data_raw.txt" | grep -v "partition_id" | wc -l)
    echo "📊 Nombre de lignes de données: $DATA_LINES"
    
    # Créer un fichier CSV plus lisible
    echo "partition_id,row_id,body_blob,metadata_s" > "$OUTPUT_DIR/data.csv"
    docker exec fact_checker_cassandra cqlsh -e "SELECT partition_id, row_id, body_blob, metadata_s FROM fact_checker_keyspace.fact_checker_docs;" | \
        grep -v "^$" | \
        grep -v "partition_id" | \
        sed 's/|/,/g' | \
        sed 's/^ //' | \
        sed 's/ $//' >> "$OUTPUT_DIR/data.csv" 2>/dev/null
    
    echo "✅ Données converties en CSV"
else
    echo "⚠️ Erreur lors de l'export des données"
fi

# Dump des métadonnées système
echo "🔍 Export des métadonnées système..."
docker exec fact_checker_cassandra cqlsh -e "SELECT table_name, comment FROM system_schema.tables WHERE keyspace_name = 'fact_checker_keyspace';" > "$OUTPUT_DIR/system_metadata.txt" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Métadonnées système exportées"
else
    echo "⚠️ Erreur lors de l'export des métadonnées système"
fi

# Dump des informations sur les colonnes
echo "📋 Export des informations sur les colonnes..."
docker exec fact_checker_cassandra cqlsh -e "SELECT column_name, type, kind FROM system_schema.columns WHERE keyspace_name = 'fact_checker_keyspace' AND table_name = 'fact_checker_docs' ORDER BY position;" > "$OUTPUT_DIR/columns_info.txt" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Informations sur les colonnes exportées"
else
    echo "⚠️ Erreur lors de l'export des informations sur les colonnes"
fi

# Créer un fichier de résumé
echo "📋 Création du résumé..."
cat > "$OUTPUT_DIR/dump_summary.txt" << EOF
Résumé du dump Cassandra (Docker)
==================================
Timestamp: $TIMESTAMP
Keyspace: fact_checker_keyspace
Table: fact_checker_docs
Fichiers créés:
- keyspace_structure.cql: Structure du keyspace
- table_structure.cql: Structure de la table
- data_raw.txt: Données brutes
- data.csv: Données en format CSV
- system_metadata.txt: Métadonnées système
- columns_info.txt: Informations sur les colonnes
- dump_summary.txt: Ce fichier

EOF

if [ -f "$OUTPUT_DIR/data.csv" ]; then
    CSV_LINES=$(wc -l < "$OUTPUT_DIR/data.csv")
    CSV_LINES=$((CSV_LINES - 1))  # Soustraire l'en-tête
    echo "Lignes exportées en CSV: $CSV_LINES" >> "$OUTPUT_DIR/dump_summary.txt"
fi

echo "✅ Résumé créé"

# Afficher le contenu des fichiers pour vérification
echo ""
echo "📂 Contenu des fichiers exportés:"
echo "=================================="

if [ -f "$OUTPUT_DIR/keyspace_structure.cql" ]; then
    echo "🏗️ Structure du keyspace:"
    head -20 "$OUTPUT_DIR/keyspace_structure.cql"
    echo ""
fi

if [ -f "$OUTPUT_DIR/table_structure.cql" ]; then
    echo "📊 Structure de la table:"
    head -20 "$OUTPUT_DIR/table_structure.cql"
    echo ""
fi

if [ -f "$OUTPUT_DIR/columns_info.txt" ]; then
    echo "📋 Informations sur les colonnes:"
    cat "$OUTPUT_DIR/columns_info.txt"
    echo ""
fi

if [ -f "$OUTPUT_DIR/data.csv" ]; then
    echo "📊 Aperçu des données (premières 5 lignes):"
    head -6 "$OUTPUT_DIR/data.csv"
    echo ""
fi

echo ""
echo "🎉 Dump terminé avec succès!"
echo "📁 Tous les fichiers sont dans: $OUTPUT_DIR"

# Afficher le contenu du dossier
echo ""
echo "📂 Contenu du dossier:"
ls -la "$OUTPUT_DIR"
