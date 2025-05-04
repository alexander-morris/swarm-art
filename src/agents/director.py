from typing import Dict, Any
from copy import deepcopy
from .base import BaseAgent

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