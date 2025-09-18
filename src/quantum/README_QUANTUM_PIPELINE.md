# Conceptualisation du Système de Recherche Documentaire Purement Quantique

## Objectif

Développer un pipeline de recherche documentaire qui repose uniquement sur des techniques quantiques pour l'encodage, la recherche et la sélection de documents, sans recours à une base vectorielle classique.

## Architecture Générale

1. **Prétraitement des documents**
   - Nettoyage, découpage, préparation des textes.
2. **Encodage quantique (angle encoding)**
   - Conversion de chaque document (ou passage) en circuit ou état quantique via l'angle encoding (rotations Ry).
   - Utilisation de Qiskit pour la génération des circuits.
3. **Stockage local des circuits/états**
   - Sauvegarde des circuits (QASM) ou états (vecteurs numpy) sur le disque local pour la base documentaire.
4. **Encodage quantique de la requête (angle encoding)**
   - Transformation de la requête utilisateur en circuit ou état quantique via l'angle encoding.
5. **Recherche documentaire quantique (overlap)**
   - Calcul de similarité quantique par overlap (produit scalaire des états) entre la requête et chaque document.
   - Sélection des top-k documents les plus proches.
6. **Décodage/interprétation**
   - Extraction et affichage des documents pertinents.
7. **Interface utilisateur**
   - Application Streamlit (réutilisation/adaptation de l'app existante dans le dossier system).

## Schéma du Pipeline

```
[Corpus de documents]
        |
   (prétraitement)
        |
[Encodage quantique (angle encoding, Qiskit)]
        |
[Stockage local des circuits/états] (QASM/.npy)
        |
[Encodage quantique de la requête (angle encoding)]
        |
[Recherche documentaire quantique (overlap)]
        |
[Top-k documents quantiques]
        |
[Décodage/interprétation]
        |
[Réponse finale]
        |
[Interface utilisateur Streamlit]
```

## Choix technologiques

- **Qiskit** : création et manipulation de circuits quantiques, simulation, calcul de similarité (overlap).
- **NumPy** : manipulation des vecteurs d'états.
- **Python** : orchestration du pipeline.
- **Streamlit** : interface utilisateur interactive (adaptation de l'app existante).

## Prochaines étapes

1. Valider la structure du pipeline et les choix technos.
2. Prototyper chaque étape sur un petit corpus.
3. Itérer sur l'encodage et la recherche quantique (angle encoding + overlap).
4. Adapter l'interface Streamlit pour intégrer la recherche documentaire quantique.
5. Documenter chaque choix et résultat.
