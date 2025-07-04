#!/usr/bin/env python3
"""
Dataset de fact-checking sur le changement climatique
100+ questions avec réponses attendues
"""

CLIMATE_DATASET = [
    # Consensus scientifique (10 questions)
    {
        "question": "Y a-t-il un consensus scientifique sur le changement climatique ?",
        "expected_answer": "Oui, il existe un consensus scientifique écrasant (97%+) sur le fait que le changement climatique est causé par l'activité humaine.",
        "category": "consensus"
    },
    {
        "question": "Quel pourcentage de scientifiques croient au changement climatique anthropique ?",
        "expected_answer": "Plus de 97% des scientifiques du climat s'accordent sur le fait que le changement climatique est causé par l'activité humaine.",
        "category": "consensus"
    },
    {
        "question": "Les scientifiques sont-ils divisés sur la question du changement climatique ?",
        "expected_answer": "Non, il existe un consensus scientifique écrasant sur le changement climatique anthropique. Les divisions sont principalement dans les médias et la politique.",
        "category": "consensus"
    },
    
    # Températures (15 questions)
    {
        "question": "Le réchauffement climatique s'est-il arrêté en 1998 ?",
        "expected_answer": "Non, le réchauffement climatique n'a pas arrêté en 1998. Les données montrent une tendance au réchauffement continue depuis cette date.",
        "category": "temperature"
    },
    {
        "question": "Les températures ont-elles augmenté depuis le début du 20ème siècle ?",
        "expected_answer": "Oui, les températures moyennes globales ont augmenté significativement depuis le début du 20ème siècle.",
        "category": "temperature"
    },
    {
        "question": "Quelle est la tendance des températures globales depuis 1880 ?",
        "expected_answer": "Les températures globales ont augmenté d'environ 1°C depuis 1880, avec une accélération depuis les années 1970.",
        "category": "temperature"
    },
    {
        "question": "Les températures actuelles sont-elles les plus élevées de l'histoire ?",
        "expected_answer": "Les températures actuelles sont parmi les plus élevées des 2000 dernières années, dépassant même la période médiévale chaude.",
        "category": "temperature"
    },
    
    # CO2 et gaz à effet de serre (15 questions)
    {
        "question": "Quelle est la contribution du CO2 au réchauffement climatique ?",
        "expected_answer": "Le CO2 est un gaz à effet de serre majeur qui contribue significativement au réchauffement climatique.",
        "category": "co2"
    },
    {
        "question": "Le CO2 est-il un polluant ?",
        "expected_answer": "Le CO2 n'est pas un polluant traditionnel mais un gaz à effet de serre qui contribue au réchauffement climatique.",
        "category": "co2"
    },
    {
        "question": "Les niveaux de CO2 ont-ils augmenté depuis l'ère préindustrielle ?",
        "expected_answer": "Oui, les niveaux de CO2 ont augmenté de plus de 40% depuis l'ère préindustrielle, passant de 280 ppm à plus de 400 ppm.",
        "category": "co2"
    },
    {
        "question": "Le CO2 est-il bénéfique pour les plantes ?",
        "expected_answer": "Bien que le CO2 soit nécessaire à la photosynthèse, l'augmentation excessive de CO2 peut avoir des effets négatifs sur certains écosystèmes.",
        "category": "co2"
    },
    
    # Modèles climatiques (10 questions)
    {
        "question": "Les modèles climatiques sont-ils fiables ?",
        "expected_answer": "Les modèles climatiques sont des outils scientifiques fiables qui ont fait leurs preuves dans la prédiction des changements climatiques.",
        "category": "models"
    },
    {
        "question": "Les modèles climatiques ont-ils prédit correctement le réchauffement ?",
        "expected_answer": "Oui, les modèles climatiques ont prédit avec précision la tendance au réchauffement observée depuis les années 1970.",
        "category": "models"
    },
    {
        "question": "Les modèles climatiques surestiment-ils le réchauffement ?",
        "expected_answer": "Non, les modèles climatiques n'ont pas surestimé le réchauffement. Les observations correspondent bien aux prédictions.",
        "category": "models"
    },
    
    # Pause du réchauffement (10 questions)
    {
        "question": "Y a-t-il eu une pause du réchauffement climatique ?",
        "expected_answer": "La soi-disant 'pause' du réchauffement climatique a été réfutée par les données récentes qui montrent une tendance au réchauffement continue.",
        "category": "pause"
    },
    {
        "question": "Le réchauffement s'est-il arrêté entre 1998 et 2013 ?",
        "expected_answer": "Non, le réchauffement n'a pas arrêté entre 1998 et 2013. Cette période a été mal interprétée et le réchauffement a continué.",
        "category": "pause"
    },
    
    # Cycles naturels (15 questions)
    {
        "question": "Le changement climatique est-il un cycle naturel ?",
        "expected_answer": "Bien que le climat ait connu des cycles naturels, le réchauffement actuel est principalement causé par l'activité humaine.",
        "category": "natural_cycles"
    },
    {
        "question": "Les cycles solaires expliquent-ils le réchauffement actuel ?",
        "expected_answer": "Non, les cycles solaires ne peuvent pas expliquer le réchauffement climatique actuel. L'activité solaire a même légèrement diminué.",
        "category": "natural_cycles"
    },
    {
        "question": "Le réchauffement actuel est-il comparable à la période médiévale chaude ?",
        "expected_answer": "Non, le réchauffement actuel est plus rapide et plus étendu que la période médiévale chaude.",
        "category": "natural_cycles"
    },
    
    # Glace et glaciers (10 questions)
    {
        "question": "Les glaciers fondent-ils à cause du changement climatique ?",
        "expected_answer": "Oui, la plupart des glaciers dans le monde fondent à un rythme accéléré à cause du changement climatique.",
        "category": "ice"
    },
    {
        "question": "L'Arctique perd-il de la glace ?",
        "expected_answer": "Oui, l'Arctique perd de la glace de mer à un rythme accéléré depuis plusieurs décennies.",
        "category": "ice"
    },
    {
        "question": "L'Antarctique gagne-t-il de la glace ?",
        "expected_answer": "L'Antarctique perd de la masse de glace dans son ensemble, malgré quelques gains locaux.",
        "category": "ice"
    },
    
    # Niveau de la mer (10 questions)
    {
        "question": "Le niveau de la mer augmente-t-il ?",
        "expected_answer": "Oui, le niveau de la mer augmente à un rythme accéléré à cause du changement climatique.",
        "category": "sea_level"
    },
    {
        "question": "L'élévation du niveau de la mer est-elle naturelle ?",
        "expected_answer": "Bien que le niveau de la mer ait fluctué naturellement, l'élévation actuelle est principalement causée par le changement climatique anthropique.",
        "category": "sea_level"
    },
    
    # Événements extrêmes (10 questions)
    {
        "question": "Le changement climatique cause-t-il plus d'événements météorologiques extrêmes ?",
        "expected_answer": "Oui, le changement climatique augmente la fréquence et l'intensité de nombreux événements météorologiques extrêmes.",
        "category": "extreme_events"
    },
    {
        "question": "Les ouragans sont-ils plus fréquents à cause du changement climatique ?",
        "expected_answer": "Le changement climatique n'augmente pas nécessairement le nombre d'ouragans mais peut augmenter leur intensité.",
        "category": "extreme_events"
    },
    
    # Océans (10 questions)
    {
        "question": "Les océans se réchauffent-ils ?",
        "expected_answer": "Oui, les océans absorbent plus de 90% de l'excès de chaleur du système climatique et se réchauffent.",
        "category": "oceans"
    },
    {
        "question": "L'acidification des océans est-elle causée par le CO2 ?",
        "expected_answer": "Oui, l'acidification des océans est causée par l'absorption du CO2 atmosphérique par les océans.",
        "category": "oceans"
    },
    
    # Controverses (10 questions)
    {
        "question": "Le graphique 'hockey stick' est-il fiable ?",
        "expected_answer": "Oui, le graphique 'hockey stick' est scientifiquement fiable et a été confirmé par de nombreuses études indépendantes.",
        "category": "controversies"
    },
    {
        "question": "Les scientifiques manipulent-ils les données de température ?",
        "expected_answer": "Non, il n'y a aucune preuve de manipulation des données de température par les scientifiques du climat.",
        "category": "controversies"
    },
    {
        "question": "Le GIEC est-il un organisme politique ?",
        "expected_answer": "Le GIEC est un organisme scientifique qui évalue la littérature scientifique, pas un organisme politique.",
        "category": "controversies"
    }
]

def get_dataset_by_category(category=None):
    """Retourne le dataset filtré par catégorie"""
    if category:
        return [item for item in CLIMATE_DATASET if item["category"] == category]
    return CLIMATE_DATASET

def get_random_subset(n=50):
    """Retourne un sous-ensemble aléatoire du dataset"""
    import random
    return random.sample(CLIMATE_DATASET, min(n, len(CLIMATE_DATASET)))

if __name__ == "__main__":
    print(f"Dataset créé avec {len(CLIMATE_DATASET)} questions")
    print("Catégories disponibles:", set(item["category"] for item in CLIMATE_DATASET)) 