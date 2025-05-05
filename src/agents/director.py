from typing import Dict, Any, List
from copy import deepcopy
from .base import BaseAgent
from src.utils.agent_memory import AgentMemory

class DirectorAgent(BaseAgent):
    """Agent responsible for generating and refining design directives."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Director agent.
        
        Args:
            config: Dictionary containing agent configuration parameters
        """
        super().__init__(config)
        self.default_constraints = {
            "frames": 30,
            "start_radius": 0,
            "end_radius": 100,
            "duration": 1.0  # seconds
        }
        self.memory = AgentMemory()
        self.iteration = 0
        self.improvement_threshold = 0.1
    
    def act(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a response.
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            Dictionary containing the agent's response
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data")
        
        if "feedback" in input_data:
            return self.refine_prompt(input_data["feedback"])
        return self.generate_initial_prompt()
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate the input data.
        
        Args:
            input_data: Dictionary containing input data to validate
            
        Returns:
            Boolean indicating whether the input is valid
        """
        if not isinstance(input_data, dict):
            return False
        
        if "feedback" in input_data:
            required_keys = ["alignment_errors", "timing_mismatch"]
            return all(key in input_data["feedback"] for key in required_keys)
        
        return True
    
    def generate_initial_prompt(self) -> Dict[str, Any]:
        """Generate the initial design directive.
        
        Returns:
            Dictionary containing the initial design directive
        """
        directive = {
            "goal": "Create a smooth circle animation",
            "constraints": deepcopy(self.default_constraints),
            "parameters": {
                "easing": "ease-in-out",
                "color": "#000000"
            }
        }
        self.add_to_history({"type": "initial_prompt", "directive": deepcopy(directive)})
        return directive
    
    def refine_prompt(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Refine the prompt based on critic feedback.
        
        Args:
            feedback: Dictionary containing feedback from the critic
            
        Returns:
            Dictionary containing the refined design directive
        """
        # Get the last directive from history
        last_directive = deepcopy(self.history[-1]["directive"]) if self.history else self.generate_initial_prompt()
        
        # Create a new directive based on feedback
        new_directive = deepcopy(last_directive)
        
        # Adjust constraints based on feedback
        if "alignment_errors" in feedback:
            for error in feedback["alignment_errors"]:
                if "radius too small" in error:
                    current_radius = new_directive["constraints"]["start_radius"]
                    new_directive["constraints"]["start_radius"] = current_radius + 5
        
        if "timing_mismatch" in feedback:
            timing_error = feedback["timing_mismatch"]
            if timing_error > 0.1:  # Significant timing mismatch
                new_directive["parameters"]["easing"] = "linear"  # Try linear timing
        
        self.add_to_history({
            "type": "refined_prompt",
            "directive": deepcopy(new_directive),
            "feedback": deepcopy(feedback)
        })
        
        return new_directive
    
    def coordinate_iteration(self, designer_output: Dict, critic_analysis: Dict) -> Dict:
        """Coordinate one iteration between Designer and Critic."""
        self.iteration += 1
        
        # Store experiences
        self.memory.add_experience(
            agent_id="designer",
            action="generate_svg",
            result="svg_generated",
            score=critic_analysis.get("score", 0.0)
        )
        
        self.memory.add_experience(
            agent_id="critic",
            action="analyze_frames",
            result="analysis_complete",
            score=critic_analysis.get("score", 0.0)
        )
        
        # Store feedback
        self.memory.add_feedback(
            from_agent="critic",
            to_agent="designer",
            feedback="\n".join(critic_analysis.get("feedback", [])),
            metrics=critic_analysis.get("visual_metrics", {})
        )
        
        # Update performance metrics
        self.memory.update_metrics(
            agent_id="designer",
            metrics=critic_analysis.get("visual_metrics", {})
        )
        
        # Generate instructions for next iteration
        instructions = self._generate_instructions(critic_analysis)
        
        return {
            "iteration": self.iteration,
            "score": critic_analysis.get("score", 0.0),
            "instructions": instructions,
            "should_continue": self._should_continue(critic_analysis)
        }
        
    def _generate_instructions(self, critic_analysis: Dict) -> Dict:
        """Generate specific instructions for the next iteration."""
        metrics = critic_analysis.get("visual_metrics", {})
        feedback = critic_analysis.get("feedback", [])
        suggestions = critic_analysis.get("suggestions", [])
        
        # Get performance trends
        designer_trend = self.memory.get_performance_trend("designer")
        
        instructions = {
            "designer": {
                "priority_improvements": [],
                "secondary_improvements": [],
                "constraints": []
            }
        }
        
        # Analyze metrics and generate priority improvements
        for metric, value in metrics.items():
            if value < 0.3:  # Low performance threshold
                instructions["designer"]["priority_improvements"].append(
                    f"Significantly improve {metric} (current: {value:.2f})"
                )
            elif value < 0.6:  # Medium performance threshold
                instructions["designer"]["secondary_improvements"].append(
                    f"Moderately improve {metric} (current: {value:.2f})"
                )
                
        # Add specific suggestions from critic
        for suggestion in suggestions:
            if any(kw in suggestion.lower() for kw in ["critical", "significant", "important"]):
                instructions["designer"]["priority_improvements"].append(suggestion)
            else:
                instructions["designer"]["secondary_improvements"].append(suggestion)
                
        # Add constraints based on feedback
        for fb in feedback:
            if "constraint" in fb.lower() or "limit" in fb.lower():
                instructions["designer"]["constraints"].append(fb)
                
        return instructions
        
    def _should_continue(self, critic_analysis: Dict) -> bool:
        """Determine if iterations should continue."""
        # Check if we've reached maximum iterations
        if self.iteration >= 10:
            return False
            
        # Check if we've achieved a high enough score
        if critic_analysis.get("score", 0.0) >= 0.95:
            return False
            
        # Check if we're still making meaningful improvements
        if self.iteration > 1:
            trend = self.memory.get_performance_trend("designer")
            improvements = [metric["change"] for metric in trend.values()]
            if all(abs(change) < self.improvement_threshold for change in improvements):
                return False
                
        return True
        
    def get_iteration_history(self) -> List[Dict]:
        """Get history of all iterations."""
        return self.memory.experiences
        
    def save_state(self, filepath: str):
        """Save director's state to file."""
        self.memory.save_to_file(filepath)
        
    def load_state(self, filepath: str):
        """Load director's state from file."""
        self.memory.load_from_file(filepath) 