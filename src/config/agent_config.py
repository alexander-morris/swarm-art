"""Configuration settings for agents."""
from typing import Dict, Any

DEFAULT_DIRECTOR_CONFIG: Dict[str, Any] = {
    "max_iterations": 30,
    "improvement_threshold": 0.02,
    "convergence_threshold": 0.90,
    "memory_persistence": True,
    "memory_path": "output/agent_memory.json",
    "analysis_weights": {
        "brightness": 0.25,
        "contrast": 0.25,
        "color_variety": 0.2,
        "distribution": 0.15,
        "animation_smoothness": 0.15
    },
    "improvement_thresholds": {
        "critical": 0.4,
        "moderate": 0.7,
        "minor": 0.85
    },
    "auto_recovery": {
        "enabled": True,
        "max_retries": 3,
        "retry_delay": 2,
        "backup_interval": 3
    },
    "logging": {
        "enabled": True,
        "level": "INFO",
        "file": "output/director.log",
        "max_files": 5,
        "max_size": 1024 * 1024  # 1MB
    }
} 