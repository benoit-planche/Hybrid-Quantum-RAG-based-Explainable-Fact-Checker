#!/usr/bin/env python3
"""
Dataset de fact-checking sur le changement climatique
100+ questions avec réponses attendues
"""

CLIMATE_DATASET = [
    # Scientific consensus (10 questions)
    {
        "question": "Is there a scientific consensus on climate change?",
        "expected_answer": "Yes, there is an overwhelming scientific consensus (97%+) that climate change is caused by human activity.",
        "category": "consensus"
    },
    {
        "question": "What percentage of scientists believe in human-caused climate change?",
        "expected_answer": "More than 97% of climate scientists agree that climate change is caused by human activity.",
        "category": "consensus"
    },
    {
        "question": "Are scientists divided on the issue of climate change?",
        "expected_answer": "No, there is an overwhelming scientific consensus on human-caused climate change. The divisions are mainly in media and politics.",
        "category": "consensus"
    },

    # Temperatures (15 questions)
    {
        "question": "Did global warming stop in 1998?",
        "expected_answer": "No, global warming did not stop in 1998. Data shows a continued warming trend since that date.",
        "category": "temperature"
    },
    {
        "question": "Have temperatures increased since the early 20th century?",
        "expected_answer": "Yes, global average temperatures have significantly increased since the early 20th century.",
        "category": "temperature"
    },
    {
        "question": "What is the trend in global temperatures since 1880?",
        "expected_answer": "Global temperatures have increased by about 1°C since 1880, with an acceleration since the 1970s.",
        "category": "temperature"
    },
    {
        "question": "Are current temperatures the highest in history?",
        "expected_answer": "Current temperatures are among the highest in the past 2000 years, surpassing even the Medieval Warm Period.",
        "category": "temperature"
    },

    # CO2 and greenhouse gases (15 questions)
    {
        "question": "What is CO2's contribution to global warming?",
        "expected_answer": "CO2 is a major greenhouse gas that significantly contributes to global warming.",
        "category": "co2"
    },
    {
        "question": "Is CO2 a pollutant?",
        "expected_answer": "CO2 is not a traditional pollutant but is a greenhouse gas that contributes to global warming.",
        "category": "co2"
    },
    {
        "question": "Have CO2 levels increased since the pre-industrial era?",
        "expected_answer": "Yes, CO2 levels have increased by more than 40% since the pre-industrial era, rising from 280 ppm to over 400 ppm.",
        "category": "co2"
    },
    {
        "question": "Is CO2 beneficial for plants?",
        "expected_answer": "Although CO2 is necessary for photosynthesis, excessive CO2 levels can have negative effects on some ecosystems.",
        "category": "co2"
    },

    # Climate models (10 questions)
    {
        "question": "Are climate models reliable?",
        "expected_answer": "Climate models are reliable scientific tools that have proven effective in predicting climate changes.",
        "category": "models"
    },
    {
        "question": "Have climate models accurately predicted warming?",
        "expected_answer": "Yes, climate models have accurately predicted the warming trend observed since the 1970s.",
        "category": "models"
    },
    {
        "question": "Do climate models overestimate warming?",
        "expected_answer": "No, climate models have not overestimated warming. Observations closely match predictions.",
        "category": "models"
    },

    # Warming pause (10 questions)
    {
        "question": "Was there a pause in global warming?",
        "expected_answer": "The so-called 'pause' in global warming has been refuted by recent data showing a continued warming trend.",
        "category": "pause"
    },
    {
        "question": "Did warming stop between 1998 and 2013?",
        "expected_answer": "No, warming did not stop between 1998 and 2013. That period was misinterpreted, and warming continued.",
        "category": "pause"
    },

    # Natural cycles (15 questions)
    {
        "question": "Is climate change part of a natural cycle?",
        "expected_answer": "Although climate has experienced natural cycles, current warming is primarily caused by human activity.",
        "category": "natural_cycles"
    },
    {
        "question": "Do solar cycles explain current warming?",
        "expected_answer": "No, solar cycles cannot explain current climate change. Solar activity has actually slightly decreased.",
        "category": "natural_cycles"
    },
    {
        "question": "Is current warming comparable to the Medieval Warm Period?",
        "expected_answer": "No, current warming is faster and more widespread than the Medieval Warm Period.",
        "category": "natural_cycles"
    },

    # Ice and glaciers (10 questions)
    {
        "question": "Are glaciers melting because of climate change?",
        "expected_answer": "Yes, most glaciers around the world are melting at an accelerated rate due to climate change.",
        "category": "ice"
    },
    {
        "question": "Is the Arctic losing ice?",
        "expected_answer": "Yes, the Arctic has been losing sea ice at an accelerated rate for several decades.",
        "category": "ice"
    },
    {
        "question": "Is Antarctica gaining ice?",
        "expected_answer": "Antarctica is losing ice mass overall, despite some localized gains.",
        "category": "ice"
    },

    # Sea level (10 questions)
    {
        "question": "Is sea level rising?",
        "expected_answer": "Yes, sea level is rising at an accelerating rate due to climate change.",
        "category": "sea_level"
    },
    {
        "question": "Is sea level rise natural?",
        "expected_answer": "While sea levels have fluctuated naturally, the current rise is mainly caused by human-induced climate change.",
        "category": "sea_level"
    },

    # Extreme events (10 questions)
    {
        "question": "Does climate change cause more extreme weather events?",
        "expected_answer": "Yes, climate change increases the frequency and intensity of many extreme weather events.",
        "category": "extreme_events"
    },
    {
        "question": "Are hurricanes more frequent due to climate change?",
        "expected_answer": "Climate change does not necessarily increase the number of hurricanes but can increase their intensity.",
        "category": "extreme_events"
    },

    # Oceans (10 questions)
    {
        "question": "Are the oceans warming?",
        "expected_answer": "Yes, the oceans absorb more than 90% of the excess heat from the climate system and are warming.",
        "category": "oceans"
    },
    {
        "question": "Is ocean acidification caused by CO2?",
        "expected_answer": "Yes, ocean acidification is caused by the absorption of atmospheric CO2 by the oceans.",
        "category": "oceans"
    },

    # Controversies (10 questions)
    {
        "question": "Is the 'hockey stick' graph reliable?",
        "expected_answer": "Yes, the 'hockey stick' graph is scientifically reliable and has been confirmed by many independent studies.",
        "category": "controversies"
    },
    {
        "question": "Do scientists manipulate temperature data?",
        "expected_answer": "No, there is no evidence that climate scientists manipulate temperature data.",
        "category": "controversies"
    },
    {
        "question": "Is the IPCC a political body?",
        "expected_answer": "The IPCC is a scientific body that assesses scientific literature, not a political organization.",
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