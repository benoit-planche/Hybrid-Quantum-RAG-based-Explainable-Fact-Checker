import time
import functools
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Classe pour stocker une métrique de performance individuelle"""
    operation_name: str
    duration: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation_name': self.operation_name,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

class PerformanceTracker:
    """Classe pour tracker les métriques de performance"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.current_session_start = None
        self.session_metrics: Dict[str, List[float]] = {}
    
    def start_session(self):
        """Démarre une nouvelle session de tracking"""
        self.current_session_start = time.time()
        self.session_metrics = {}
        logger.info("🚀 Session de performance démarrée")
    
    def end_session(self) -> Dict[str, Any]:
        """Termine la session et retourne un résumé"""
        if not self.current_session_start:
            return {}
        
        total_duration = time.time() - self.current_session_start
        session_summary = {
            'total_duration': total_duration,
            'metrics_count': len(self.metrics),
            'operations': {}
        }
        
        # Grouper les métriques par opération
        for metric in self.metrics:
            op_name = metric.operation_name
            if op_name not in session_summary['operations']:
                session_summary['operations'][op_name] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }
            
            op_stats = session_summary['operations'][op_name]
            op_stats['count'] += 1
            op_stats['total_time'] += metric.duration
            op_stats['min_time'] = min(op_stats['min_time'], metric.duration)
            op_stats['max_time'] = max(op_stats['max_time'], metric.duration)
        
        # Calculer les moyennes
        for op_stats in session_summary['operations'].values():
            op_stats['avg_time'] = op_stats['total_time'] / op_stats['count']
            if op_stats['min_time'] == float('inf'):
                op_stats['min_time'] = 0
        
        logger.info(f"📊 Session terminée - Durée totale: {total_duration:.2f}s")
        return session_summary
    
    def add_metric(self, operation_name: str, duration: float, metadata: Optional[Dict[str, Any]] = None):
        """Ajoute une métrique de performance"""
        metric = PerformanceMetric(
            operation_name=operation_name,
            duration=duration,
            metadata=metadata or {}
        )
        self.metrics.append(metric)
        
        # Ajouter à la session courante
        if operation_name not in self.session_metrics:
            self.session_metrics[operation_name] = []
        self.session_metrics[operation_name].append(duration)
        
        logger.info(f"⏱️ {operation_name}: {duration:.3f}s")
    
    def get_operation_stats(self, operation_name: str) -> Dict[str, float]:
        """Retourne les statistiques pour une opération spécifique"""
        durations = [m.duration for m in self.metrics if m.operation_name == operation_name]
        if not durations:
            return {}
        
        return {
            'count': len(durations),
            'total_time': sum(durations),
            'avg_time': sum(durations) / len(durations),
            'min_time': min(durations),
            'max_time': max(durations)
        }
    
    def save_metrics(self, filename: str = None):
        """Sauvegarde les métriques dans un fichier JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
        
        data = {
            'session_summary': self.end_session(),
            'detailed_metrics': [metric.to_dict() for metric in self.metrics]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Métriques sauvegardées dans {filename}")
        return filename

# Instance globale du tracker
performance_tracker = PerformanceTracker()

def time_operation(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Décorateur pour mesurer le temps d'exécution d'une fonction"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                performance_tracker.add_metric(operation_name, duration, metadata)
                return result
            except Exception as e:
                duration = time.time() - start_time
                error_metadata = metadata or {}
                error_metadata['error'] = str(e)
                performance_tracker.add_metric(f"{operation_name}_error", duration, error_metadata)
                raise
        return wrapper
    return decorator

def time_operation_context(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """Context manager pour mesurer le temps d'exécution d'un bloc de code"""
    class TimeContext:
        def __init__(self, name, meta):
            self.name = name
            self.meta = meta
            self.start_time = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = time.time() - self.start_time
            if exc_type:
                error_meta = self.meta or {}
                error_meta['error'] = str(exc_val)
                performance_tracker.add_metric(f"{self.name}_error", duration, error_meta)
            else:
                performance_tracker.add_metric(self.name, duration, self.meta)
    
    return TimeContext(operation_name, metadata)

def get_performance_summary() -> Dict[str, Any]:
    """Retourne un résumé des performances de la session courante"""
    return performance_tracker.end_session()

def start_performance_session():
    """Démarre une nouvelle session de performance"""
    performance_tracker.start_session()

def save_performance_metrics(filename: str = None):
    """Sauvegarde les métriques de performance"""
    return performance_tracker.save_metrics(filename)

# Fonctions utilitaires pour des métriques spécifiques
def log_database_operation(operation: str, table: str, duration: float, rows_affected: int = None):
    """Log une opération de base de données"""
    metadata = {
        'operation_type': 'database',
        'table': table,
        'rows_affected': rows_affected
    }
    performance_tracker.add_metric(f"db_{operation}", duration, metadata)

def log_quantum_operation(operation: str, n_qubits: int, duration: float, circuit_depth: int = None):
    """Log une opération quantique"""
    metadata = {
        'operation_type': 'quantum',
        'n_qubits': n_qubits,
        'circuit_depth': circuit_depth
    }
    performance_tracker.add_metric(f"quantum_{operation}", duration, metadata)

def log_llm_operation(operation: str, model: str, duration: float, tokens_generated: int = None):
    """Log une opération LLM"""
    metadata = {
        'operation_type': 'llm',
        'model': model,
        'tokens_generated': tokens_generated
    }
    performance_tracker.add_metric(f"llm_{operation}", duration, metadata) 