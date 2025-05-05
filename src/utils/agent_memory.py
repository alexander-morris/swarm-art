"""Memory module for storing and managing agent experiences."""
import json
from datetime import datetime
from typing import Dict, List, Optional

class AgentMemory:
    def __init__(self):
        self.experiences = []
        self.feedback_history = []
        self.performance_metrics = {}
        
    def add_experience(self, agent_id: str, action: str, result: str, score: float):
        """Store a new experience."""
        experience = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "action": action,
            "result": result,
            "score": score
        }
        self.experiences.append(experience)
        
    def add_feedback(self, from_agent: str, to_agent: str, feedback: str, metrics: Dict):
        """Store feedback between agents."""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "from_agent": from_agent,
            "to_agent": to_agent,
            "feedback": feedback,
            "metrics": metrics
        }
        self.feedback_history.append(feedback_entry)
        
    def update_metrics(self, agent_id: str, metrics: Dict):
        """Update performance metrics for an agent."""
        if agent_id not in self.performance_metrics:
            self.performance_metrics[agent_id] = []
        self.performance_metrics[agent_id].append({
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics
        })
        
    def get_recent_experiences(self, agent_id: str, limit: int = 5) -> List[Dict]:
        """Get recent experiences for an agent."""
        agent_experiences = [exp for exp in self.experiences if exp["agent_id"] == agent_id]
        return sorted(agent_experiences, key=lambda x: x["timestamp"], reverse=True)[:limit]
        
    def get_feedback_history(self, agent_id: str) -> List[Dict]:
        """Get feedback history for an agent."""
        return [fb for fb in self.feedback_history if fb["to_agent"] == agent_id]
        
    def get_performance_trend(self, agent_id: str) -> Dict:
        """Calculate performance trend for an agent."""
        if agent_id not in self.performance_metrics:
            return {}
            
        metrics = self.performance_metrics[agent_id]
        if not metrics:
            return {}
            
        latest = metrics[-1]["metrics"]
        trend = {}
        
        if len(metrics) > 1:
            previous = metrics[-2]["metrics"]
            for key in latest:
                if key in previous:
                    trend[key] = {
                        "current": latest[key],
                        "previous": previous[key],
                        "change": latest[key] - previous[key]
                    }
                    
        return trend
        
    def save_to_file(self, filepath: str):
        """Save memory to a file."""
        memory_data = {
            "experiences": self.experiences,
            "feedback_history": self.feedback_history,
            "performance_metrics": self.performance_metrics
        }
        with open(filepath, 'w') as f:
            json.dump(memory_data, f, indent=2)
            
    def load_from_file(self, filepath: str):
        """Load memory from a file."""
        try:
            with open(filepath, 'r') as f:
                memory_data = json.load(f)
                self.experiences = memory_data.get("experiences", [])
                self.feedback_history = memory_data.get("feedback_history", [])
                self.performance_metrics = memory_data.get("performance_metrics", {})
        except Exception as e:
            print(f"Error loading memory from file: {e}") 