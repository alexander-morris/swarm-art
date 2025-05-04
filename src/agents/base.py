from typing import Dict, Any
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all agents in the swarm system."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the agent with configuration.
        
        Args:
            config: Dictionary containing agent configuration parameters
        """
        self.config = config
        self.history = []
    
    @abstractmethod
    def act(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a response.
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            Dictionary containing the agent's response
        """
        raise NotImplementedError
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate the input data.
        
        Args:
            input_data: Dictionary containing input data to validate
            
        Returns:
            Boolean indicating whether the input is valid
        """
        raise NotImplementedError
    
    def add_to_history(self, data: Dict[str, Any]) -> None:
        """Add an interaction to the agent's history.
        
        Args:
            data: Dictionary containing the interaction data
        """
        self.history.append(data)
    
    def get_history(self) -> list[Dict[str, Any]]:
        """Get the agent's interaction history.
        
        Returns:
            List of dictionaries containing historical interactions
        """
        return self.history 