# Start of Selection
#!/usr/bin/env python3
"""
Dataset de fact-checking sur le changement climatique
100+ claims et affirmations avec réponses attendues
"""

CLIMATE_DATASET = [
    # Scientific consensus (moitié claims, moitié affirmations)
    {
        "claim": "Is there a scientific consensus on climate change?",
        "expected_verdict": "TRUE",
        "expected_output": "There is an overwhelming scientific consensus (97%+) that climate change is caused by human activity.",
        "category": "consensus"
    },
    {
        "claim": "Scientists are divided on the issue of climate change.",
        "expected_verdict": "FALSE",
        "expected_output": "There is an overwhelming scientific consensus on human-caused climate change. The divisions are mainly in media and politics.",
        "category": "consensus"
    },
    {
        "claim": "Do 97% of climate scientists agree on human-caused climate change?",
        "expected_verdict": "TRUE",
        "expected_output": "Multiple studies have shown that 97% or more of climate scientists agree that climate change is primarily caused by human activities.",
        "category": "consensus"
    },
    {
        "claim": "There is disagreement among climate scientists about the basic facts.",
        "expected_verdict": "FALSE",
        "expected_output": "There is strong agreement among climate scientists about the basic facts of climate change, including human causation.",
        "category": "consensus"
    },
    {
        "claim": "Have major scientific organizations endorsed the consensus on climate change?",
        "expected_verdict": "TRUE",
        "expected_output": "All major scientific organizations worldwide have endorsed the scientific consensus on human-caused climate change.",
        "category": "consensus"
    },

    # Temperatures (moitié claims, moitié affirmations)
    {
        "claim": "Global warming stopped in 1998.",
        "expected_verdict": "FALSE",
        "expected_output": "Global warming did not stop in 1998. Data shows a continued warming trend since that date.",
        "category": "temperature"
    },
    {
        "claim": "Have temperatures increased since the early 20th century?",
        "expected_verdict": "TRUE",
        "expected_output": "Global average temperatures have significantly increased since the early 20th century.",
        "category": "temperature"
    },
    {
        "claim": "The Earth is cooling.",
        "expected_verdict": "FALSE",
        "expected_output": "The Earth is not cooling. Global temperatures have been rising consistently for decades.",
        "category": "temperature"
    },
    {
        "claim": "Are current temperatures the highest in history?",
        "expected_verdict": "TRUE",
        "expected_output": "Current temperatures are among the highest in the past 2000 years, surpassing even the Medieval Warm Period.",
        "category": "temperature"
    },
    {
        "claim": "Temperature records are being manipulated.",
        "expected_verdict": "FALSE",
        "expected_output": "There is no evidence that temperature records are being manipulated. Multiple independent datasets show the same warming trend.",
        "category": "temperature"
    },
    {
        "claim": "Is the warming trend statistically significant?",
        "expected_verdict": "TRUE",
        "expected_output": "The global warming trend is statistically significant and cannot be explained by natural variability alone.",
        "category": "temperature"
    },
    {
        "claim": "Both satellite and surface temperature measurements show the same warming trend.",
        "expected_verdict": "TRUE",
        "expected_output": "Both satellite and surface measurements are reliable and show the same warming trend. Satellites measure different parts of the atmosphere.",
        "category": "temperature"
    },
    {
        "claim": "Are satellite temperature measurements more reliable than surface measurements?",
        "expected_verdict": "FALSE",
        "expected_output": "Both satellite and surface measurements are reliable and show the same warming trend. Satellites measure different parts of the atmosphere.",
        "category": "temperature"
    },

    # CO2 and greenhouse gases (moitié claims, moitié affirmations)
    {
        "claim": "What is CO2's contribution to global warming?",
        "expected_verdict": "TRUE",
        "expected_output": "CO2 is a major greenhouse gas that significantly contributes to global warming.",
        "category": "co2"
        
    },
    {
        "claim": "CO2 is a pollutant.",
        "expected_verdict": "FALSE",
        "expected_output": "CO2 is not a traditional pollutant but is a greenhouse gas that contributes to global warming.",
        "category": "co2"
    },
    {
        "claim": "Have CO2 levels increased since the pre-industrial era?",
        "expected_verdict": "TRUE",
        "expected_output": "CO2 levels have increased by more than 40% since the pre-industrial era, rising from 280 ppm to over 400 ppm.",
        "category": "co2"
    },
    {
        "claim": "CO2 is beneficial for plants.",
        "expected_verdict": "FALSE",
        "expected_output": "Although CO2 is necessary for photosynthesis, excessive CO2 levels can have negative effects on some ecosystems.",
        "category": "co2"
    },
    {
        "claim": "Is CO2 the most important greenhouse gas?",
        "expected_verdict": "FALSE",
        "expected_output": "CO2 is the most important long-lived greenhouse gas, but methane and other gases also contribute significantly to warming.",
        "category": "co2"
    },
    {
        "claim": "Current CO2 levels are higher than at any time in the past 800,000 years.",
        "expected_verdict": "TRUE",
        "expected_output": "Current CO2 levels are higher than at any time in the past 800,000 years, based on ice core data.",
        "category": "co2"
    },
    {
        "claim": "Does CO2 cause global warming?",
        "expected_verdict": "TRUE",
        "expected_output": "CO2 is a greenhouse gas that traps heat in the atmosphere and causes global warming.",
        "category": "co2"
    },
    {
        "claim": "The greenhouse effect is a natural phenomenon.",
        "expected_verdict": "MIXED",
        "expected_output": "The greenhouse effect is a natural phenomenon, but human activities have enhanced it by increasing greenhouse gas concentrations.",
        "category": "co2"
    },

    # Climate models (moitié claims, moitié affirmations)
    {
        "claim": "Are climate models reliable?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate models are reliable scientific tools that have proven effective in predicting climate changes.",
        "category": "models"
    },
    {
        "claim": "Climate models have accurately predicted the warming trend observed since the 1970s.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate models have accurately predicted the warming trend observed since the 1970s.",
        "category": "models"
    },
    {
        "claim": "Do climate models overestimate warming?",
        "expected_verdict": "FALSE",
        "expected_output": "Climate models have not overestimated warming. Observations closely match predictions.",
        "category": "models"
    },
    {
        "claim": "Climate models are too complex to be trusted.",
        "expected_verdict": "FALSE",
        "expected_output": "Climate models are based on well-established physics and have been validated against historical data.",
        "category": "models"
    },
    {
        "claim": "Do climate models include natural variability?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate models include natural variability such as solar cycles, volcanic eruptions, and ocean oscillations.",
        "category": "models"
    },
    {
        "claim": "Climate models have been tested against past climate changes.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate models have been extensively tested against historical climate data and past climate changes.",
        "category": "models"
    },

    # Warming pause (moitié claims, moitié affirmations)
    {
        "claim": "There was a pause in global warming.",
        "expected_verdict": "FALSE",
        "expected_output": "The so-called 'pause' in global warming has been refuted by recent data showing a continued warming trend.",
        "category": "pause"
    },
    {
        "claim": "Did warming stop between 1998 and 2013?",
        "expected_verdict": "FALSE",
        "expected_output": "Warming did not stop between 1998 and 2013. That period was misinterpreted, and warming continued.",
        "category": "pause"
    },
    {
        "claim": "There is evidence of a global warming hiatus.",
        "expected_verdict": "FALSE",
        "expected_output": "There is no evidence of a global warming hiatus. The warming trend has continued consistently.",
        "category": "pause"
    },
    {
        "claim": "Did temperatures plateau after 1998?",
        "expected_verdict": "FALSE",
        "expected_output": "Temperatures did not plateau after 1998. The warming trend continued, though with natural year-to-year variations.",
        "category": "pause"
    },
    {
        "claim": "The warming trend is linear.",
        "expected_verdict": "FALSE",
        "expected_output": "The warming trend is not perfectly linear due to natural variability, but the long-term trend is clearly upward.",
        "category": "pause"
    },

    # Natural cycles (moitié claims, moitié affirmations)
    {
        "claim": "Is climate change part of a natural cycle?",
        "expected_verdict": "FALSE",
        "expected_output": "Although climate has experienced natural cycles, current warming is primarily caused by human activity.",
        "category": "natural_cycles"
    },
    {
        "claim": "Solar cycles explain current warming.",
        "expected_verdict": "FALSE",
        "expected_output": "Solar cycles cannot explain current climate change. Solar activity has actually slightly decreased.",
        "category": "natural_cycles"
    },
    {
        "claim": "Is current warming comparable to the Medieval Warm Period?",
        "expected_verdict": "FALSE",
        "expected_output": "Current warming is faster and more widespread than the Medieval Warm Period.",
        "category": "natural_cycles"
    },
    {
        "claim": "Natural cycles are causing the current warming.",
        "expected_verdict": "FALSE",
        "expected_output": "Natural cycles cannot explain the current rate and pattern of warming. Human activities are the primary cause.",
        "category": "natural_cycles"
    },
    {
        "claim": "Is the sun responsible for recent warming?",
        "expected_verdict": "FALSE",
        "expected_output": "Solar activity has been relatively stable or slightly decreasing during the period of rapid warming.",
        "category": "natural_cycles"
    },
    {
        "claim": "Volcanic eruptions are causing global cooling.",
        "expected_verdict": "FALSE",
        "expected_output": "Volcanic eruptions can cause temporary cooling, but they cannot explain the long-term warming trend.",
        "category": "natural_cycles"
    },
    {
        "claim": "Is the current warming rate unprecedented?",
        "expected_verdict": "TRUE",
        "expected_output": "The current rate of warming is unprecedented in the context of natural climate changes over the past 10,000 years.",
        "category": "natural_cycles"
    },

    # Ice and glaciers (moitié claims, moitié affirmations)
    {
        "claim": "Most glaciers around the world are melting at an accelerated rate due to climate change.",
        "expected_verdict": "TRUE",
        "expected_output": "Most glaciers around the world are melting at an accelerated rate due to climate change.",
        "category": "ice"
    },
    {
        "claim": "Is the Arctic losing ice?",
        "expected_verdict": "TRUE",
        "expected_output": "The Arctic has been losing sea ice at an accelerated rate for several decades.",
        "category": "ice"
    },
    {
        "claim": "Antarctica is gaining ice.",
        "expected_verdict": "FALSE",
        "expected_output": "Antarctica is losing ice mass overall, despite some localized gains.",
        "category": "ice"
    },
    {
        "claim": "Is Greenland losing ice?",
        "expected_verdict": "TRUE",
        "expected_output": "Greenland is losing ice mass at an accelerating rate due to climate change.",
        "category": "ice"
    },
    {
        "claim": "Mountain glaciers are retreating worldwide.",
        "expected_verdict": "FALSE",
        "expected_output": "Not all mountain glaciers are retreating; a small number are stable or advancing, but the vast majority are retreating worldwide.",
        "category": "ice"
    },
    {
        "claim": "Is sea ice extent decreasing?",
        "expected_verdict": "FALSE",
        "expected_output": "Antarctic sea ice extent has shown periods of increase, but overall, global sea ice extent is decreasing, especially in the Arctic.",
        "category": "ice"
    },
    {
        "claim": "Permafrost is melting in many regions due to rising temperatures.",
        "expected_verdict": "TRUE",
        "expected_output": "Permafrost is melting in many regions due to rising temperatures.",
        "category": "ice"
    },

    # Sea level (moitié claims, moitié affirmations)
    {
        "claim": "Is sea level rising?",
        "expected_verdict": "TRUE",
        "expected_output": "Sea level is rising at an accelerating rate due to climate change.",
        "category": "sea_level"
    },
    {
        "claim": "Sea level rise is natural.",
        "expected_verdict": "FALSE",
        "expected_output": "While sea levels have fluctuated naturally, the current rise is mainly caused by human-induced climate change.",
        "category": "sea_level"
    },
    {
        "claim": "Is sea level rise accelerating?",
        "expected_verdict": "TRUE",
        "expected_output": "Sea level rise is accelerating due to thermal expansion and ice melt.",
        "category": "sea_level"
    },
    {
        "claim": "Coastal areas worldwide are at increasing risk from sea level rise and associated flooding.",
        "expected_verdict": "TRUE",
        "expected_output": "Coastal areas worldwide are at increasing risk from sea level rise and associated flooding.",
        "category": "sea_level"
    },
    {
        "claim": "Is sea level rise uniform globally?",
        "expected_verdict": "FALSE",
        "expected_output": "Sea level rise is not uniform globally due to ocean currents, land movement, and gravitational effects.",
        "category": "sea_level"
    },
    {
        "claim": "Small island nations are particularly vulnerable to sea level rise and associated impacts.",
        "expected_verdict": "TRUE",
        "expected_output": "Small island nations are particularly vulnerable to sea level rise and associated impacts.",
        "category": "sea_level"
    },

    # Extreme events (moitié claims, moitié affirmations)
    {
        "claim": "Does climate change cause more extreme weather events?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change increases the frequency and intensity of many extreme weather events.",
        "category": "extreme_events"
    },
    {
        "claim": "Climate change does not necessarily increase the number of hurricanes but can increase their intensity.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change does not necessarily increase the number of hurricanes but can increase their intensity.",
        "category": "extreme_events"
    },
    {
        "claim": "Are heat waves becoming more frequent?",
        "expected_verdict": "TRUE",
        "expected_output": "Heat waves are becoming more frequent, intense, and longer-lasting due to climate change.",
        "category": "extreme_events"
    },
    {
        "claim": "Climate change is increasing the frequency and severity of droughts in many regions.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change is increasing the frequency and severity of droughts in many regions.",
        "category": "extreme_events"
    },
    {
        "claim": "Are floods becoming more common?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change is increasing the frequency and intensity of heavy rainfall events and floods.",
        "category": "extreme_events"
    },
    {
        "claim": "Climate change is contributing to more frequent and severe wildfires through increased temperatures and drought.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change is contributing to more frequent and severe wildfires through increased temperatures and drought.",
        "category": "extreme_events"
    },

    # Oceans (moitié claims, moitié affirmations)
    {
        "claim": "The oceans absorb more than 90% of the excess heat from the climate system and are warming.",
        "expected_verdict": "TRUE",
        "expected_output": "The oceans absorb more than 90% of the excess heat from the climate system and are warming.",
        "category": "oceans"
    },
    {
        "claim": "Is ocean acidification caused by CO2?",
        "expected_verdict": "TRUE",
        "expected_output": "Ocean acidification is caused by the absorption of atmospheric CO2 by the oceans.",
        "category": "oceans"
    },
    {
        "claim": "Climate change is affecting ocean circulation patterns, including the Atlantic Meridional Overturning Circulation.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change is affecting ocean circulation patterns, including the Atlantic Meridional Overturning Circulation.",
        "category": "oceans"
    },
    {
        "claim": "Is sea surface temperature increasing?",
        "expected_verdict": "TRUE",
        "expected_output": "Sea surface temperatures have been increasing globally due to climate change.",
        "category": "oceans"
    },
    {
        "claim": "Coral reefs are threatened by climate change through ocean warming and acidification.",
        "expected_verdict": "TRUE",
        "expected_output": "Coral reefs are threatened by climate change through ocean warming and acidification.",
        "category": "oceans"
    },
    {
        "claim": "Is the ocean losing oxygen?",
        "expected_verdict": "TRUE",
        "expected_output": "Ocean oxygen levels are decreasing due to warming and changes in ocean circulation.",
        "category": "oceans"
    },

    # Controversies (moitié claims, moitié affirmations)
    {
        "claim": "Is the 'hockey stick' graph reliable?",
        "expected_verdict": "TRUE",
        "expected_output": "The 'hockey stick' graph is scientifically reliable and has been confirmed by many independent studies.",
        "category": "controversies"
    },
    {
        "claim": "Climate scientists manipulate temperature data.",
        "expected_verdict": "FALSE",
        "expected_output": "There is no evidence that climate scientists manipulate temperature data.",
        "category": "controversies"
    },
    {
        "claim": "Is the IPCC a political body?",
        "expected_verdict": "FALSE",
        "expected_output": "The IPCC is a scientific body that assesses scientific literature, not a political organization.",
        "category": "controversies"
    },
    {
        "claim": "The 'Climategate' incident involved stolen emails but multiple independent investigations found no evidence of scientific misconduct.",
        "expected_verdict": "TRUE",
        "expected_output": "The 'Climategate' incident involved stolen emails but multiple independent investigations found no evidence of scientific misconduct.",
        "category": "controversies"
    },
    {
        "claim": "Are climate scientists biased?",
        "expected_verdict": "FALSE",
        "expected_output": "Climate scientists follow rigorous scientific methods and their findings have been independently verified.",
        "category": "controversies"
    },
    {
        "claim": "The basic science of climate change is well-established, though details continue to be refined.",
        "expected_verdict": "TRUE",
        "expected_output": "The basic science of climate change is well-established, though details continue to be refined.",
        "category": "controversies"
    },
    {
        "claim": "Are climate predictions reliable?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate predictions are based on well-established physics and have been validated against observations.",
        "category": "controversies"
    },

    # Economic impacts (moitié claims, moitié affirmations)
    {
        "claim": "Addressing climate change requires investment, but the costs of inaction are much higher than the costs of action.",
        "expected_verdict": "TRUE",
        "expected_output": "While addressing climate change requires investment, the costs of inaction are much higher than the costs of action.",
        "category": "economics"
    },
    {
        "claim": "Will climate change affect the global economy?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change is expected to have significant negative impacts on the global economy.",
        "category": "economics"
    },
    {
        "claim": "The costs of renewable energy technologies have decreased significantly in recent years.",
        "expected_verdict": "TRUE",
        "expected_output": "The costs of renewable energy technologies have decreased significantly in recent years.",
        "category": "economics"
    },
    {
        "claim": "Is climate action economically beneficial?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate action can provide economic benefits through job creation, energy security, and avoided damages.",
        "category": "economics"
    },
    {
        "claim": "Climate change is expected to affect agricultural productivity and food security in many regions.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change is expected to affect agricultural productivity and food security in many regions.",
        "category": "economics"
    },

    # Health impacts (moitié claims, moitié affirmations)
    {
        "claim": "Does climate change have no effect on human health?",
        "expected_verdict": "FALSE",
        "expected_output": "Climate change affects human health through heat stress, air quality, infectious diseases, and extreme weather events.",
        "category": "health"
    },
    {
        "claim": "Heat-related deaths are increasing due to climate change and more frequent heat waves.",
        "expected_verdict": "TRUE",
        "expected_output": "Heat-related deaths are increasing due to climate change and more frequent heat waves.",
        "category": "health"
    },
    {
        "claim": "Does climate change affect air quality?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change affects air quality through increased ozone levels and wildfire smoke.",
        "category": "health"
    },
    {
        "claim": "Climate change is expanding the range of disease-carrying vectors like mosquitoes.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change is expanding the range of disease-carrying vectors like mosquitoes.",
        "category": "health"
    },
    {
        "claim": "Does climate change affect mental health?",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change can affect mental health through stress, anxiety, and trauma from extreme weather events.",
        "category": "health"
    },

    # Solutions and mitigation (moitié claims, moitié affirmations)
    {
        "claim": "Climate change can be addressed through rapid reduction of greenhouse gas emissions and adaptation measures.",
        "expected_verdict": "TRUE",
        "expected_output": "Climate change can be addressed through rapid reduction of greenhouse gas emissions and adaptation measures.",
        "category": "solutions"
    },
    {
        "claim": "Is renewable energy sufficient to meet our needs?",
        "expected_verdict": "TRUE",
        "expected_output": "Renewable energy sources can meet global energy needs with proper infrastructure and storage.",
        "category": "solutions"
    },
    {
        "claim": "Nuclear energy can contribute to reducing emissions, but it has its own challenges including waste disposal and safety concerns.",
        "expected_verdict": "TRUE",
        "expected_output": "Nuclear energy can contribute to reducing emissions, but it has its own challenges including waste disposal and safety concerns.",
        "category": "solutions"
    },
    {
        "claim": "Can individual actions make a difference?",
        "expected_verdict": "MIXED",
        "expected_output": "Individual actions can contribute, but systemic changes and policy action are needed for significant impact.",
        "category": "solutions"
    },
    {
        "claim": "Carbon capture and storage can help reduce emissions, but it's not a complete solution and should complement emission reductions.",
        "expected_verdict": "TRUE",
        "expected_output": "Carbon capture and storage can help reduce emissions, but it's not a complete solution and should complement emission reductions.",
        "category": "solutions"
    },
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
    print(f"Dataset créé avec {len(CLIMATE_DATASET)} items (claims et affirmations)")
    print("Catégories disponibles:", set(item["category"] for item in CLIMATE_DATASET))
    
    # Afficher les statistiques par catégorie
    categories = {}
    for item in CLIMATE_DATASET:
        cat = item["category"]
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
    
    print("\n📊 Statistiques par catégorie:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count} items")
    
    # Compter les verdicts TRUE/FALSE
    true_count = 0
    false_count = 0
    other_count = 0
    
    for item in CLIMATE_DATASET:
        answer = item["expected_verdict"].upper()
        if answer.startswith("TRUE"):
            true_count += 1
        elif answer.startswith("FALSE"):
            false_count += 1
        else:
            other_count += 1
    
    print(f"\n🎯 Répartition des verdicts:")
    print(f"  TRUE: {true_count}")
    print(f"  FALSE: {false_count}")
    print(f"  Autres: {other_count}") 
# End of Selection