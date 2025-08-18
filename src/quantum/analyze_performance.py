#!/usr/bin/env python3
"""
Script d'analyse des métriques de performance pour identifier les goulots d'étranglement
"""

import json
import os
import glob
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def load_performance_data(filename: str) -> Dict[str, Any]:
    """Charge les données de performance depuis un fichier JSON"""
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_performance_file(filename: str) -> Dict[str, Any]:
    """Analyse un fichier de métriques de performance"""
    data = load_performance_data(filename)
    session_summary = data.get('session_summary', {})
    
    analysis = {
        'filename': filename,
        'total_duration': session_summary.get('total_duration', 0),
        'operations_count': session_summary.get('metrics_count', 0),
        'operations': {},
        'bottlenecks': [],
        'recommendations': []
    }
    
    # Analyser chaque opération
    operations = session_summary.get('operations', {})
    for op_name, stats in operations.items():
        analysis['operations'][op_name] = {
            'total_time': stats['total_time'],
            'avg_time': stats['avg_time'],
            'count': stats['count'],
            'percentage': (stats['total_time'] / session_summary['total_duration']) * 100 if session_summary['total_duration'] > 0 else 0
        }
    
    # Identifier les goulots d'étranglement (opérations > 10% du temps total)
    for op_name, stats in analysis['operations'].items():
        if stats['percentage'] > 10:
            analysis['bottlenecks'].append({
                'operation': op_name,
                'percentage': stats['percentage'],
                'total_time': stats['total_time'],
                'avg_time': stats['avg_time']
            })
    
    # Générer des recommandations
    for bottleneck in analysis['bottlenecks']:
        op_name = bottleneck['operation']
        if 'quantum' in op_name.lower():
            analysis['recommendations'].append(
                f"🔬 {op_name}: Optimiser les calculs quantiques (considérer la parallélisation ou réduire le nombre de qubits)"
            )
        elif 'llm' in op_name.lower():
            analysis['recommendations'].append(
                f"🤖 {op_name}: Optimiser les appels LLM (considérer le caching ou un modèle plus rapide)"
            )
        elif 'database' in op_name.lower() or 'cassandra' in op_name.lower():
            analysis['recommendations'].append(
                f"🗄️ {op_name}: Optimiser les requêtes base de données (considérer l'indexation ou le caching)"
            )
        elif 'embedding' in op_name.lower():
            analysis['recommendations'].append(
                f"🧠 {op_name}: Optimiser la génération d'embeddings (considérer le batching ou un modèle plus rapide)"
            )
        else:
            analysis['recommendations'].append(
                f"⚡ {op_name}: Analyser et optimiser cette opération"
            )
    
    return analysis

def compare_performance_files(filenames: List[str]) -> Dict[str, Any]:
    """Compare plusieurs fichiers de métriques de performance"""
    comparisons = {
        'files': [],
        'total_durations': [],
        'operation_times': {},
        'improvements': []
    }
    
    analyses = []
    for filename in filenames:
        analysis = analyze_performance_file(filename)
        analyses.append(analysis)
        comparisons['files'].append(filename)
        comparisons['total_durations'].append(analysis['total_duration'])
    
    # Comparer les durées totales
    if len(analyses) >= 2:
        first_duration = analyses[0]['total_duration']
        last_duration = analyses[-1]['total_duration']
        improvement = ((first_duration - last_duration) / first_duration) * 100
        comparisons['improvements'].append(f"Amélioration globale: {improvement:.1f}%")
    
    # Comparer les opérations
    all_operations = set()
    for analysis in analyses:
        all_operations.update(analysis['operations'].keys())
    
    for op_name in all_operations:
        op_times = []
        for analysis in analyses:
            op_times.append(analysis['operations'].get(op_name, {}).get('total_time', 0))
        comparisons['operation_times'][op_name] = op_times
    
    return comparisons

def generate_performance_report(analysis: Dict[str, Any]) -> str:
    """Génère un rapport de performance formaté"""
    report = f"""
# 📊 Rapport de Performance - {os.path.basename(analysis['filename'])}

## ⏱️ Vue d'ensemble
- **Temps total**: {analysis['total_duration']:.2f} secondes
- **Nombre d'opérations**: {analysis['operations_count']}
- **Date d'analyse**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🐌 Goulots d'étranglement identifiés
"""
    
    if analysis['bottlenecks']:
        for bottleneck in analysis['bottlenecks']:
            report += f"""
### {bottleneck['operation']}
- **Pourcentage du temps total**: {bottleneck['percentage']:.1f}%
- **Temps total**: {bottleneck['total_time']:.3f}s
- **Temps moyen**: {bottleneck['avg_time']:.3f}s
"""
    else:
        report += "Aucun goulot d'étranglement majeur identifié (toutes les opérations < 10% du temps total)\n"
    
    report += "\n## 📋 Détail des opérations\n"
    for op_name, stats in analysis['operations'].items():
        report += f"""
### {op_name}
- **Temps total**: {stats['total_time']:.3f}s ({stats['percentage']:.1f}%)
- **Temps moyen**: {stats['avg_time']:.3f}s
- **Nombre d'exécutions**: {stats['count']}
"""
    
    if analysis['recommendations']:
        report += "\n## 💡 Recommandations d'optimisation\n"
        for rec in analysis['recommendations']:
            report += f"- {rec}\n"
    
    return report

def plot_performance_metrics(analysis: Dict[str, Any], output_file: str = None):
    """Génère des graphiques de performance"""
    operations = analysis['operations']
    
    if not operations:
        print("Aucune donnée d'opération à tracer")
        return
    
    # Créer les graphiques
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Analyse de Performance - {os.path.basename(analysis["filename"])}', fontsize=16)
    
    # Graphique 1: Temps total par opération
    op_names = list(operations.keys())
    total_times = [operations[op]['total_time'] for op in op_names]
    ax1.bar(op_names, total_times)
    ax1.set_title('Temps Total par Opération')
    ax1.set_ylabel('Temps (secondes)')
    ax1.tick_params(axis='x', rotation=45)
    
    # Graphique 2: Pourcentage du temps total
    percentages = [operations[op]['percentage'] for op in op_names]
    ax2.pie(percentages, labels=op_names, autopct='%1.1f%%')
    ax2.set_title('Répartition du Temps par Opération')
    
    # Graphique 3: Temps moyen par opération
    avg_times = [operations[op]['avg_time'] for op in op_names]
    ax3.bar(op_names, avg_times, color='orange')
    ax3.set_title('Temps Moyen par Opération')
    ax3.set_ylabel('Temps (secondes)')
    ax3.tick_params(axis='x', rotation=45)
    
    # Graphique 4: Nombre d'exécutions par opération
    counts = [operations[op]['count'] for op in op_names]
    ax4.bar(op_names, counts, color='green')
    ax4.set_title('Nombre d\'Exécutions par Opération')
    ax4.set_ylabel('Nombre d\'exécutions')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Graphique sauvegardé dans {output_file}")
    else:
        plt.show()

def main():
    """Fonction principale"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyse les métriques de performance')
    parser.add_argument('--file', '-f', help='Fichier de métriques à analyser')
    parser.add_argument('--pattern', '-p', default='performance_metrics_*.json', 
                       help='Pattern pour trouver les fichiers de métriques')
    parser.add_argument('--output', '-o', help='Fichier de sortie pour le rapport')
    parser.add_argument('--plot', action='store_true', help='Générer des graphiques')
    parser.add_argument('--compare', action='store_true', help='Comparer plusieurs fichiers')
    
    args = parser.parse_args()
    
    if args.file:
        # Analyser un fichier spécifique
        if not os.path.exists(args.file):
            print(f"Erreur: Le fichier {args.file} n'existe pas")
            return
        
        analysis = analyze_performance_file(args.file)
        report = generate_performance_report(analysis)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Rapport sauvegardé dans {args.output}")
        else:
            print(report)
        
        if args.plot:
            plot_file = args.output.replace('.txt', '.png') if args.output else 'performance_plot.png'
            plot_performance_metrics(analysis, plot_file)
    
    elif args.compare:
        # Comparer plusieurs fichiers
        files = glob.glob(args.pattern)
        if not files:
            print(f"Aucun fichier trouvé avec le pattern: {args.pattern}")
            return
        
        files.sort()  # Trier par ordre chronologique
        print(f"Fichiers trouvés: {files}")
        
        comparison = compare_performance_files(files)
        
        print("\n=== COMPARAISON DES PERFORMANCES ===")
        for i, (filename, duration) in enumerate(zip(comparison['files'], comparison['total_durations'])):
            print(f"{i+1}. {os.path.basename(filename)}: {duration:.2f}s")
        
        if comparison['improvements']:
            print("\n=== AMÉLIORATIONS ===")
            for improvement in comparison['improvements']:
                print(improvement)
    
    else:
        # Mode interactif
        files = glob.glob(args.pattern)
        if not files:
            print(f"Aucun fichier trouvé avec le pattern: {args.pattern}")
            return
        
        files.sort()
        print("Fichiers de métriques disponibles:")
        for i, file in enumerate(files):
            print(f"{i+1}. {file}")
        
        try:
            choice = int(input("\nChoisissez un fichier à analyser (numéro): ")) - 1
            if 0 <= choice < len(files):
                analysis = analyze_performance_file(files[choice])
                report = generate_performance_report(analysis)
                print(report)
                
                if input("\nGénérer des graphiques? (y/n): ").lower() == 'y':
                    plot_performance_metrics(analysis)
            else:
                print("Choix invalide")
        except (ValueError, KeyboardInterrupt):
            print("Opération annulée")

if __name__ == "__main__":
    main() 