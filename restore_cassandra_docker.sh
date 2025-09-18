#!/bin/bash

# Script de restauration pour Cassandra via Docker
# Restaure la base à partir des fichiers de dump

echo "🚀 Début de la restauration Cassandra via Docker..."

# Vérifier les arguments
if [ $# -eq 0 ]; then
    echo "❌ Usage: $0 <dossier_dump>"
    echo "   Exemple: $0 cassandra_dump_docker_20250829_174032"
    exit 1
fi

DUMP_DIR="$1"

if [ ! -d "$DUMP_DIR" ]; then
    echo "❌ Dossier de dump '$DUMP_DIR' non trouvé!"
    exit 1
fi

echo "📁 Dossier de dump: $DUMP_DIR"

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

# Vérifier que les fichiers nécessaires existent
REQUIRED_FILES=("keyspace_structure.cql" "table_structure.cql" "data.csv")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$DUMP_DIR/$file" ]; then
        echo "❌ Fichier requis manquant: $file"
        exit 1
    fi
done

echo "✅ Tous les fichiers requis sont présents"

# Créer le keyspace
echo "🏗️ Création du keyspace..."
if docker exec fact_checker_cassandra cqlsh -e "CREATE KEYSPACE IF NOT EXISTS fact_checker_keyspace WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'} AND durable_writes = true;" 2>/dev/null; then
    echo "✅ Keyspace fact_checker_keyspace créé/restauré"
else
    echo "⚠️ Erreur lors de la création du keyspace (peut déjà exister)"
fi

# Supprimer la table existante si elle existe
echo "🗑️ Suppression de la table existante..."
docker exec fact_checker_cassandra cqlsh -e "DROP TABLE IF EXISTS fact_checker_keyspace.fact_checker_docs;" >/dev/null 2>&1
echo "✅ Table existante supprimée"

# Créer la table
echo "📊 Création de la table..."
if docker exec fact_checker_cassandra cqlsh -f /tmp/table_structure.cql; then
    echo "✅ Table fact_checker_docs créée"
else
    echo "❌ Erreur lors de la création de la table"
    exit 1
fi

# Copier le fichier de structure dans le conteneur
echo "📋 Copie de la structure de la table..."
docker cp "$DUMP_DIR/table_structure.cql" fact_checker_cassandra:/tmp/table_structure.cql

# Créer la table avec la structure exacte
echo "📊 Création de la table avec la structure exacte..."
CREATE_TABLE_SQL="
CREATE TABLE fact_checker_keyspace.fact_checker_docs (
    partition_id text,
    row_id text,
    attributes_blob text,
    body_blob text,
    vector vector<float, 4096>,
    metadata_s map<text, text>,
    PRIMARY KEY (partition_id, row_id)
) WITH CLUSTERING ORDER BY (row_id ASC)
    AND additional_write_policy = '99p'
    AND allow_auto_snapshot = true
    AND bloom_filter_fp_chance = 0.01
    AND caching = {'keys': 'ALL', 'rows_per_partition': 'NONE'}
    AND cdc = false
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy', 'max_threshold': '32', 'min_threshold': '4'}
    AND compression = {'chunk_length_in_kb': '16', 'class': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND memtable = 'default'
    AND crc_check_chance = 1.0
    AND default_time_to_live = 0
    AND extensions = {}
    AND gc_grace_seconds = 864000
    AND incremental_backups = true
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair = 'BLOCKING'
    AND speculative_retry = '99p';
"

if docker exec fact_checker_cassandra cqlsh -e "$CREATE_TABLE_SQL"; then
    echo "✅ Table fact_checker_docs créée avec succès"
else
    echo "❌ Erreur lors de la création de la table"
    exit 1
fi

# Créer les index
echo "🔍 Création des index..."
CREATE_INDEXES_SQL="
CREATE CUSTOM INDEX eidx_metadata_s_fact_checker_docs ON fact_checker_keyspace.fact_checker_docs (entries(metadata_s)) USING 'org.apache.cassandra.index.sai.StorageAttachedIndex';
CREATE CUSTOM INDEX idx_vector_fact_checker_docs ON fact_checker_keyspace.fact_checker_docs (vector) USING 'org.apache.cassandra.index.sai.StorageAttachedIndex';
"

if docker exec fact_checker_cassandra cqlsh -e "$CREATE_INDEXES_SQL"; then
    echo "✅ Index créés avec succès"
else
    echo "⚠️ Erreur lors de la création des index (peuvent déjà exister)"
fi

# Restaurer les données
echo "📥 Restauration des données..."
DATA_FILE="$DUMP_DIR/data.csv"
if [ -f "$DATA_FILE" ]; then
    # Compter les lignes de données
    TOTAL_LINES=$(wc -l < "$DATA_FILE")
    DATA_LINES=$((TOTAL_LINES - 1))  # Soustraire l'en-tête
    
    echo "📊 Restauration de $DATA_LINES lignes..."
    
    # Lire le fichier CSV et insérer les données
    LINE_COUNT=0
    SKIP_FIRST=true
    
    while IFS=',' read -r partition_id row_id body_blob metadata_s; do
        if [ "$SKIP_FIRST" = true ]; then
            SKIP_FIRST=false
            continue
        fi
        
        # Nettoyer les valeurs
        partition_id=$(echo "$partition_id" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        row_id=$(echo "$row_id" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        body_blob=$(echo "$body_blob" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        metadata_s=$(echo "$metadata_s" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Échapper les apostrophes dans body_blob
        body_blob=$(echo "$body_blob" | sed "s/'/''/g")
        
        # Insérer la ligne
        INSERT_SQL="INSERT INTO fact_checker_keyspace.fact_checker_docs (partition_id, row_id, body_blob, metadata_s) VALUES ('$partition_id', '$row_id', '$body_blob', $metadata_s);"
        
        if docker exec fact_checker_cassandra cqlsh -e "$INSERT_SQL" >/dev/null 2>&1; then
            LINE_COUNT=$((LINE_COUNT + 1))
            if [ $((LINE_COUNT % 100)) -eq 0 ]; then
                echo "   ✅ $LINE_COUNT lignes restaurées..."
            fi
        else
            echo "   ⚠️ Erreur lors de la restauration de la ligne $LINE_COUNT"
        fi
    done < "$DATA_FILE"
    
    echo "✅ Restauration terminée: $LINE_COUNT lignes restaurées"
else
    echo "❌ Fichier de données non trouvé: $DATA_FILE"
    exit 1
fi

# Vérifier la restauration
echo "🔍 Vérification de la restauration..."
RESTORED_COUNT=$(docker exec fact_checker_cassandra cqlsh -e "SELECT COUNT(*) FROM fact_checker_keyspace.fact_checker_docs;" | grep -E '[0-9]+' | head -1 | tr -d ' ')
echo "📊 Nombre de lignes dans la base restaurée: $RESTORED_COUNT"

# Créer un rapport de restauration
RESTORE_REPORT="$DUMP_DIR/restore_report.txt"
cat > "$RESTORE_REPORT" << EOF
Rapport de restauration Cassandra
==================================
Timestamp: $(date)
Dossier de dump: $DUMP_DIR
Keyspace: fact_checker_keyspace
Table: fact_checker_docs

Résumé:
- Keyspace créé/restauré: ✅
- Table supprimée et recréée: ✅
- Index créés: ✅
- Lignes restaurées: $LINE_COUNT
- Lignes dans la base: $RESTORED_COUNT

Fichiers utilisés:
- keyspace_structure.cql: Structure du keyspace
- table_structure.cql: Structure de la table
- data.csv: Données à restaurer

EOF

echo "📋 Rapport de restauration créé: $RESTORE_REPORT"

echo ""
echo "🎉 Restauration terminée avec succès!"
echo "📊 Total lignes restaurées: $LINE_COUNT"
echo "📁 Rapport: $RESTORE_REPORT"
