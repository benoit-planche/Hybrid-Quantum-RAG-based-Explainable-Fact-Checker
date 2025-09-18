# Hybrid Quantum-Classical RAG for Climate Misinformation Detection

Auteur :Benoit PLANCHE, benoit.planche@etu.umontpellier.fr
Posted Date :September 18th, 2025
Github : https://github.com/benoit-planche/RAG-based-Explainable-Fact-Checker/tree/quantum

## Abstract

This report describes the conceptualization and implementation of an innovative AI agent based on quantum algorithms, carried out as part of a second-year DevOps engineering internship abroad. The project focuses on the creation of a Retrieval-Augmented Generation (RAG) system designed to verify and detect misinformation related to climate change. This solution could enable social network–style applications to integrate rapid moderation fact checks on user-generated content.

## Introduction

### Problématique

Aujourd’hui, la désinformation climatique est un problème majeur qui affecte la société. Elle peut entraîner des dommages importants sur la santé, l’économie et l’environnement. La désinformation climatique peut également conduire à des décisions politiques erronées et à des conflits sociaux. La lutte contre la désinformation climatique est donc une priorité majeure pour la société. C’est pourquoi il est crucial de développer des outils automatisés de vérification des faits pour protéger l’intégrité de l’information scientifique autour des questions climatiques.

### Présentation du projet

Cette article s’inscrit dans le cadre du projet de recherche "Edge-LLM-basedshieldagainst misinformation" développé à l’Université du Danemark du Sud. L’objectif principal est de créer un système automatisé de détection et de vérification de la désinformation climatique en temps réel. Le projet combine plusieurs technologies de pointe : l’intelligence artificielle avec les modèles de langage de grande taille (LLMs), les technologies quantiques pour l’optimisation de la recherche d’information, et l’architecture RAG (Retrieval-Augmented Generation) pour assurer la traçabilité des sources. Cette approche multidisciplinaire vise à développer un outil robuste capable de lutter efficacement contre la propagation de fausses informations sur les questions climatiques.

### Objectif de l’article

Ce document présente la mission réalisée, les défis techniques relevés, et les résultats obtenus dans le cadre de ce projet de recherche.

## Contexte

### Le projet de recherche : "Edge-LLM-based shield against misinformation"

Le projet s’inscrit dans le cadre plus large de la lutte contre la désinformation, avec un focus spécifique sur les informations climatiques. L’objectif principal était de développer un système hybride combinant à la fois des approches de recherche quantique et classique pour l’analyse de documents, dans le but d’obtenir une précision maximale tout en minimisant le temps de traitement.

Le système automatisé développé est capable de :

- Analyser et vérifier les affirmations liées au changement climatique
- Fournir des explications transparentes et vérifiables
- Fonctionner en temps réel dans des applications

### Justification technologique et objectifs techniques

L’utilisation des LLMs (Large Language Models) se justifie par leur capacité à comprendre le contexte et la nuance dans les textes, ce qui est essentiel pour la détection de désinformation sophistiquée. Pour l’intégration de ces modèles, nous avons choisi Ollama, une plateforme open-source qui permet d’exécuter localement des modèles de langage de grande taille. Ollama offre plusieurs avantages : déploiement simplifié, gestion automatique des modèles. Cette solution permet d’éviter les coûts et les limitations des APIs cloud tout en garantissant la confidentialité des données.

Cependant, pour garantir la traçabilité et la vérifiabilité des réponses générées, il est nécessaire d’aller au-delà de la simple génération de texte. C’est dans ce contexte que l’architecture RAG (Retrieval-Augmented Generation) prend tout son sens : elle combine la puissance des LLMs avec un module de recherche documentaire, permettant au système de s’appuyer sur des sources fiables et de citer explicitement les documents utilisés lors de la vérification d’une affirmation. Ainsi, le RAG permet d’améliorer la transparence et la robustesse du système face à la désinformation.

Par ailleurs, l’approche quantique offre des perspectives d’amélioration des performances de recherche et de similarité, particulièrement dans le traitement de grandes bases de données documentaires. L’intégration de techniques quantiques dans le module de retrieval du RAG permet d’obtenir une capture du contexte plus précise et plus rapide, renforçant ainsi l’efficacité globale du système.

Les objectifs techniques de cette mission consistaient à :

- Maîtriser les technologies quantiques appliquées à la recherche d’information
- Intégrer des modèles de langage de grande taille dans un système de production
- Mettre en œuvre une architecture RAG pour assurer la traçabilité des sources et la robustesse du fact-checking
- Optimiser les performances de traitement afin de permettre une utilisation en temps réel adapté à la dynamique des réseaux sociaux et des médias sociaux
- Évaluer les performances globales du système sur un corpus de revendications climatiques

## Rapport Technique

### Architecture du système

Le système RAG développé repose sur une architecture hybride combinant plusieurs composants.L’ensemble du développement a été réalisé en Python, un choix technologique justifié par la richesse de son écosystème pour l’intelligence artificielle, le traitement quantique et la gestion de bases de données. Python offre des bibliothèques spécialisées comme Qiskit pour la simulation quantique, Ollama pour l’intégration des LLMs, et Cassandra pour la gestion de la base vectorielle, permettant une intégration harmonieuse de tous les composants du système.

![Schéma d’architecture du système RAG](ressource/architecture.png)

L’architecture du système RAG (Retrieval-Augmented Generation) s’appui sur plusieurs composants qui interagissent pour permettre la recherche de connaissances pertinentes et la génération de réponses adaptées. Le processus débute avec le prompt de l’utilisateur, qui constitue la requête initiale. Ce prompt est traité par le pipeline RAG, dont le rôle est d’enrichir la requête avec des informations issues de sources externes avant de la transmettre au modèle de langage. La base de connaissances est constituée de documents de référence (par exemple des fichiers PDF), qui sont d’abord découpés en plus petits segments appelés chunks.

Ces chunks sont ensuite transformés en vecteurs grâce à OllamaEmbedding. Les vecteurs sont stockés dans une base vectorielle (Cassandra), ce qui permet de réaliser une recherche de similarité afin d’identifier rapidement les passages les plus pertinents pour répondre à la question posée. Le contexte ainsi retrouvé est ensuite transmis à un circuit quantique (8 qubits), dont le rôle est d’optimiser ou de reclasser l’information avant de l’envoyer au modèle. Enfin, le LLM (llama 7B) exploite à la fois le prompt initial et le contexte enrichi pour produire la réponse finale qui est renvoyée à l’utilisateur.

### Base vectorielle Cassandra

#### Création et configuration de la base de données

La base vectorielle Cassandra constitue le cœur du système de retrieval du RAG. Elle stocke les embeddings vectoriels des documents climatiques et permet une recherche rapide et efficace. La configuration de la base de données a été réalisée avec les paramètres suivants :

```python
CREATE KEYSPACE climate_fact_checking
WITH replication = {'class':'SimpleStrategy','replication_factor': 1};
CREATE TABLE document_embeddings (
document_id UUID PRIMARY KEY,
title TEXT,
content TEXT,
embedding VECTOR <FLOAT, 4096>, # Embeddings 4096D
metadata MAP <TEXT, TEXT>,
created_atT I M E S T A M P
);
```

#### Processus d’ingestion des documents

Le processus d’ingestion des documents climatiques commence par une phase de prétraitement, au cours de laquelle le texte est extrait et nettoyé à partir des fichiers PDF scientifiques. Une fois cette étape réalisée, les documents sont découpés en segments n’excédant pas 512 tokens, afin d’optimiser la gestion et l’analyse des données textuelles. Pour chaque segment ainsi obtenu, des embeddings vectoriels de dimension 4096 sont générés à l’aide du modèle ‘Ollama Embedding‘ via l’API Ollama. Enfin, ces représentations vectorielles, accompagnées de leurs métadonnées, sont stockées dans la base Cassandra, ce qui permet d’assurer une indexation efficace et une recherche rapide au sein du système.

```python
def ingest_document(document_path:str):
"""Processus d'ingestion d'un document climatique"""
# 1. Extraction du texte
text_content = extract_text_from_pdf(document_path)
# 2. Decoupage en chunks
chunks = create_text_chunks(text_content , max_tokens=512)
# 3. Generation des embeddings
embeddings = generate_embeddings(chunks)
# 4. Stockage dans Cassandra
forchunk , embeddingin zip(chunks , embeddings ):
store_in_cassandra(chunk , embedding , metadata)
```

#### Recherche vectorielle et pré-filtrage

Lors d’une requête utilisateur,le système prend le contenu de la requête et le transforme en embedding vectoriel à l’aide du modèle ‘OllamaEmbedding‘. Ensuite, une recherche vectorielle est effectuée dans la base Cassandra pour trouver les 300 documents les plus similaires à l’embedding de la requête. Ces documents sont ensuite utilisés pour la recherche quantique. Grace à ce pré-filtrage, le système peut limiter le nombre de documents à comparer dans la recherche quantique, ce qui permet d’améliorer les performances du système.

```python
def vector_search(query_embedding: np.ndarray , top_k:int= 300):
"""Recherche vectorielle dans Cassandra"""
# Requete de similarité cosinus
query = """
   SELECT document_id , title , content , embedding , metadata
   FROM document_embeddings
   ORDER BY embedding ANN OF %s
   LIMIT %s
   """
results = session . execute(query , [query_embedding , top_k])
return[(row.document_id , row. title , row. content , row.embedding)
for row in results ]
```

Cette architecture permet de traiter efficacement une base de plus de 10 000 documents tout en maintenant des temps de réponse acceptables pour l’utilisation en temps réel qu’on ne pourrait pas assumé avec de la simulation quantique uniquement.

### Développement du système quantique

Une fois les documents selectionnés, le système quantique est utilisé pour comparer les documents entre eux et trouver les 10 résultats les plus similaires.

#### Préparation des données pour le traitement quantique

Avant d’utiliser le circuit quantique, il est nécessaire d’adapter les embeddings des documents à la représentation quantique. Pour cela, chaque embedding est réduit à une dimension de 8, correspondant au nombre de qubits du circuit. Ensuite, chaque vecteur est normalisé. Cette normalisation est indispensable pour permettre l’encodage des données sous forme d’amplitudes quantiques, conformément aux exigences de l’amplitude encoding.

#### Implémentation et utilisation du circuit quantique

Le cœur du système repose sur un circuit quantique à 8 qubits, qui permet de représenter les embeddings normalisés sous forme d’états quantiques. Pour chaque document et pour la requête de l’utilisateur, un circuit quantique est créé et initialisé à l’aide de la méthode ‘initialize‘, qui encode directement l’embedding dans l’état quantique du circuit.

La comparaison entre documents s’effectue par le calcul du recouvrement quantique (overlap) entre les états préparés,ce qui permet de mesurer la similarité entre deux états quantiques. Plus cette valeur est élevée, plus les documents sont considérés comme similaires. Un circuit de comparaison est alors construit pour préparer successivement les deux états à comparer,puis une mesure spécifique est réalisée, par exemple en évaluant la probabilité de retrouver le système dans un état de référence donné. Cette mesure fournit une estimation quantitative de la similarité entre la requête et chaque document.

Enfin, les 10 documents les plus similaires sont sélectionnés et renvoyés au LLM, accompagnés de toutes les informations nécessaires, afin d’analyser la requête utilisateur et de générer un verdict ainsi qu’une explication adaptée à la réalité scientifique.

### Intégration du LLM

#### Configuration Ollama

L’intégration du modèle Llama2:7B via Ollama a nécessité l’optimisation des paramètres :

```python
classQuantumFactChecker:
def__init__( self ):
self . ollama_client = OllamaClient(
model="llama2:7b" ,
temperature=0.01,
timeout=300
)
```

Le modèle Llama2:7B a été choisi pour sa rapidité et sa précision. Le 7B signifie que le modèle a 7 milliards de paramètres. Ces paramètres définissent la capacité du modèle à comprendre le contexte et la nuance dans les textes. Il existe d’autre modèles (Mistral :7B, CodeLlama:7B,DeepSeek-R1:7B) et avec plus de paramètres (13B,70B,130B). Ici,le modèle Llama2 :7B a été choisi pour sa rapidité et sa précision.

Aussi, la température a été réduite à 0.01 pour des réponses décisives et cohérentes. La température est un paramètre qui définit la créativité du modèle. Plus la température est élevée, plus le modèle est créatif. Plus la température est basse, plus le modèle est déterministe.

#### Prompt engineering

Le développement d’un prompt efficace a été crucial pour la qualité des résultats. Le prompt est le texte qui est envoyé au modèle pour qu’il génère une réponse. Il est important de bien formater le prompt pour que le modèle puisse comprendre la requête utilisateur et générer une réponse adaptée à la réalité scientifique. Voici le prompt utilisé pour l’analyse du LLM :

```python
analysis_prompt = """
You are a climate science fact−checker . Analyze the following claim ...
CLAIM: {claim}
EVIDENCE: {evidence}
INSTRUCTIONS:
− Be EXTREMELY CRITICAL and skeptical
−Look for evidence that DIRECTLY contradicts the claim
−Quote specific text from the evidence
−Distinguish between Antarctica and other regions
− If evidence is insufficient , state FALSE
RESPONSE FORMAT:
VERDICT: [TRUE/FALSE/UNVERIFIABLE]
EXPLANATION: [ Detailed reasoning ]
"""
```

### Défi techniques et solutions

Finalement, le développement du système a nécessité de surmonter plusieurs défis techniques majeurs. L’optimisation des performances a été obtenue grâce à l’adoption d’une architecture hybride avec pré-filtrage, divisant par vingt le temps de traitement par requête. Enfin, l’efficacité du fact-checking a été renforcée par l’amélioration du prompt et le réglage fin de la température du LLM, permettant de limiter les biais et d’obtenir des réponses plus critiques et fiables. Ces solutions ont permis d’aboutir à un système performant, stable et pertinent pour la vérification automatisée de faits scientifiques.

## Résultats obtenus

### Performances globales

Le système final atteint une accuracy de 76% sur un corpus de 50 revendications climatiques, représentant une amélioration significative par rapport au système de base (22%). Cette amélioration est due à l’utilisation de l’architecture hybride quantique-classique, qui permet de combiner les avantages de chaque approche. La vitesse de traitement est de 27.59 secondes en moyenne, ce qui est acceptable pour une application en temps réel. Ce cout est en grande partie dû à la partie quantique, car pour le moment nous ne pouvons que simuler du quantique et non l’exécuter sur un ordinateur quantique.

### Comparaison avec d’autre systèmes

Aussi il est important pour evaluer le système de comparer avec d’autre systèmes. Voici les résultats de la comparaison avec le LLM Brut et le système Hybride.

| Systeme | Accuracy | Temps moyen | Amelioration |
|---------|----------|-------------|--------------|
| LLM Brut | 22% | 2-5 secondes | - |
| Systeme Hybride | 76% | 27.59 secondes | +256.36% |

### Exemples de résultats

Voici quelques exemples de résultats obtenus avec le système Hybride.

#### Exemple 1 : Détection réussie d’une fausse revendication

```python
CLAIM: "Antarctica is gaining ice due to climate change"
VERDICT: FALSE
EXPLANATION: "The evidence shows that Antarctica is actually losing ice mass. The continent has experienced significant ice loss over recent decades , contradicting the claim of ice gain ."
sources : ...
```

#### Exemple 2 : Validation d’un fait établi

```python
CLAIM: "CO2 levels have increased since the pre−industrial era"
VERDICT: TRUE
EXPLANATION: "Multiple sources confirm that atmospheric CO2 concentrations have risen from approximately 280 ppm to over 400 ppm since 1750.
sources : ...
```

### Conclusion et perspective d’amélioration

On a donc une architecture RAG hybride qui nous permet d’atteindre une accuracy de 76% avec un model LLM de 7B seulement. Une nette amélioration par rapport au LLM Brut. Aussi, l’interface API permet d’intégrer le système dans des applications externes et faciliter les tests. Le tout avec une vitesse de traitement de 27.59 secondes en moyenne. Raisonnable pour une application en temps réel. Cependant, on peut admettre que la vitesse de traitement et un point central dans des perspectives d’amélioration de notre architecture.

## Bibliographie

```
“About the NIPCC – Climate Change Reconsidered.” Climate Change Reconsidered,
https ://climatechangereconsidered.org/about-the-nipcc/. Accessed 12 Sept. 2025.
Anouska-Abhisikta.“GitHub-Anouska-Abhisikta/RAG-Based-Explainable-Fact-Checker:
A Transparent and Auditable Fact-Checking System Powered by Retrieval-Augmented Gene-
ration (RAG), LangChain, and Large Language Models.” GitHub,
https ://github.com/Anouska-Abhisikta/RAG-based-Explainable-Fact-Checker. Accessed 12
Sept. 2025.
Arif-PhyChem. “GitHub - Arif-PhyChem/QD3SET : The First and the Only Dataset in
the Field of Quantum Dissipative Dynamics.” GitHub,
https ://github.com/Arif-PhyChem/QD3SET. Accessed 12 Sept. 2025.
“ClimateChangeMissionControl-NASAScience.” NASAScience,https://www.facebook.com/NASA, 6 Oct. 2021,
https ://science.nasa.gov/earth/climate-change/climate-change-mission-control/.
FujiiLabCollaboration.“GitHub-FujiiLabCollaboration/MNISQ-Quantum-Circuit-Dataset:
MNISQ Circuit Dataset for Machine Learning and Quantum Machine Learning.” GitHub,
https://github.com/FujiiLabCollaboration/MNISQ-quantum-circuit-dataset.Accessed12Sept.
2025.
“Global Warming Links.” Skeptical Science,
https ://skepticalscience.com/resources.php. Accessed 12 Sept. 2025.
“IPCC — Intergovernmental Panel on Climate Change.” IPCC — Intergovernmental Panel
on Climate Change,
https ://www.ipcc.ch/. Accessed 12 Sept. 2025.
LSchatzki. “GitHub - LSchatzki/NTangled_Datasets : Entanglement-Based Datasets and
Generators for Quantum Machine Learning.” GitHub,
https ://github.com/LSchatzki/NTangled_Datasets. Accessed 12 Sept. 2025.
sysadmin-info. “GitHub - Sysadmin-Info/N8n-K3s.” GitHub,
https ://github.com/sysadmin-info/n8n-k3s. Accessed 12 Sept. 2025.
```
