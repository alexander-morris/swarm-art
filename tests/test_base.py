import pytest
from src.agents.base import BaseAgent

class TestAgent(BaseAgent):
    """Test implementation of BaseAgent for testing purposes."""
    
    def act(self, input_data):
        return {"response": "test"}
    
    def validate_input(self, input_data):
        return True

def test_base_agent_initialization():
    """Test that BaseAgent initializes correctly with config."""
    config = {"test_param": "value"}
    agent = TestAgent(config)
    assert agent.config == config
    assert agent.history == []

def test_base_agent_history():
    """Test that BaseAgent correctly manages history."""
    agent = TestAgent({})
    test_data = {"test": "data"}
    agent.add_to_history(test_data)
    assert agent.get_history() == [test_data]
    
    # Test multiple history entries
    agent.add_to_history({"another": "entry"})
    assert len(agent.get_history()) == 2

def test_base_agent_abstract_methods():
    """Test that BaseAgent abstract methods raise NotImplementedError."""
    with pytest.raises(TypeError):
        BaseAgent({})  # Should fail because BaseAgent is abstract 