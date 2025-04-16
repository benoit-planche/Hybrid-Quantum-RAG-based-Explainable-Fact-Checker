import re
import uuid
from datetime import datetime
import json
import os

def parse_verdict(analysis_text):
    """Extract the verdict from the analysis text."""
    verdict_match = re.search(r'VERDICT:\s*(\w+(?:\s+\w+)*)', analysis_text)
    if verdict_match:
        return verdict_match.group(1).strip()
    return "UNVERIFIABLE"

def extract_claim_components(analysis_text):
    """Extract claim components from analysis text."""
    components_section = re.search(r'CLAIM COMPONENTS:(.*?)(?=EVIDENCE ANALYSIS:|$)', 
                                  analysis_text, re.DOTALL)
    if not components_section:
        return []
    
    components_text = components_section.group(1).strip()
    components = re.findall(r'[-•*]\s*(.*?)(?=\n[-•*]|\n\n|$)', components_text, re.DOTALL)
    return [comp.strip() for comp in components if comp.strip()]

def extract_evidence_analysis(analysis_text):
    """Extract evidence analysis from analysis text."""
    analysis_section = re.search(r'EVIDENCE ANALYSIS:(.*?)(?=MISSING INFORMATION:|VERDICT:|$)', 
                                analysis_text, re.DOTALL)
    if not analysis_section:
        return {}
    
    analysis_text = analysis_section.group(1).strip()
    
    # Match component headers and their content
    components = re.findall(r'[-•*]\s*(Component \d+|[^:]+):\s*(.*?)(?=\n[-•*]|\n\n|$)', 
                           analysis_text, re.DOTALL)
    
    analysis_dict = {}
    for comp_name, comp_analysis in components:
        analysis_dict[comp_name.strip()] = comp_analysis.strip()
    
    return analysis_dict

def highlight_document_references(text, doc_ids):
    """Highlight document references in text."""
    highlighted_text = text
    for doc_id in doc_ids:
        pattern = f"Document {doc_id}"
        replacement = f"<span style='background-color: #fff2cc; font-weight: bold;'>{pattern}</span>"
        highlighted_text = highlighted_text.replace(pattern, replacement)
    
    return highlighted_text

def save_fact_check_to_file(fact_check, directory="fact_checks"):
    """Save a fact check to a JSON file."""
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    # Generate filename based on ID and timestamp
    filename = f"{directory}/fact_check_{fact_check['id']}.json"
    
    # Save to file
    with open(filename, 'w') as f:
        json.dump(fact_check, f, indent=2)
    
    return filename

def load_fact_check_from_file(filename):
    """Load a fact check from a JSON file."""
    with open(filename, 'r') as f:
        fact_check = json.load(f)
    
    return fact_check

def get_saved_fact_checks(directory="fact_checks"):
    """Get a list of all saved fact checks."""
    if not os.path.exists(directory):
        return []
    
    fact_checks = []
    for filename in os.listdir(directory):
        if filename.startswith("fact_check_") and filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            fact_checks.append(load_fact_check_from_file(filepath))
    
    # Sort by timestamp, newest first
    fact_checks.sort(key=lambda x: x['timestamp'], reverse=True)
    return fact_checks
