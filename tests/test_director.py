import pytest
from src.agents.director import DirectorAgent

def test_director_initialization():
    """Test that DirectorAgent initializes correctly with config."""
    config = {"test_param": "value"}
    director = DirectorAgent(config)
    assert director.config == config
    assert director.history == []
    assert "frames" in director.default_constraints
    assert "start_radius" in director.default_constraints
    assert "end_radius" in director.default_constraints
    assert "duration" in director.default_constraints

def test_director_initial_prompt():
    """Test initial prompt generation."""
    director = DirectorAgent({})
    prompt = director.generate_initial_prompt()
    
    # Check structure
    assert isinstance(prompt, dict)
    assert "goal" in prompt
    assert "constraints" in prompt
    assert "parameters" in prompt
    
    # Check content
    assert prompt["goal"] == "Create a smooth circle animation"
    assert prompt["constraints"]["frames"] == 30
    assert prompt["constraints"]["start_radius"] == 0
    assert prompt["constraints"]["end_radius"] == 100
    assert prompt["parameters"]["easing"] == "ease-in-out"
    
    # Check history
    assert len(director.history) == 1
    assert director.history[0]["type"] == "initial_prompt"

def test_director_refinement():
    """Test prompt refinement based on feedback."""
    director = DirectorAgent({})
    initial_prompt = director.generate_initial_prompt()
    
    feedback = {
        "alignment_errors": ["radius too small"],
        "timing_mismatch": 0.2
    }
    
    refined = director.refine_prompt(feedback)
    
    # Check that refinement occurred
    assert refined["constraints"]["start_radius"] > initial_prompt["constraints"]["start_radius"]
    assert refined["parameters"]["easing"] == "linear"  # Changed due to timing mismatch
    
    # Check history
    assert len(director.history) == 2
    assert director.history[1]["type"] == "refined_prompt"
    assert director.history[1]["feedback"] == feedback

def test_director_act_method():
    """Test the act method with different inputs."""
    director = DirectorAgent({})
    
    # Test with empty input (should generate initial prompt)
    result = director.act({})
    assert "goal" in result
    assert "constraints" in result
    
    # Test with feedback
    feedback = {
        "alignment_errors": ["radius too small"],
        "timing_mismatch": 0.2
    }
    result = director.act({"feedback": feedback})
    assert result["constraints"]["start_radius"] > 0
    assert result["parameters"]["easing"] == "linear"

def test_director_input_validation():
    """Test input validation."""
    director = DirectorAgent({})
    
    # Test valid inputs
    assert director.validate_input({}) is True
    assert director.validate_input({"feedback": {
        "alignment_errors": [],
        "timing_mismatch": 0.0
    }}) is True
    
    # Test invalid inputs
    assert director.validate_input(None) is False
    assert director.validate_input({"feedback": {}}) is False
    assert director.validate_input({"feedback": {"alignment_errors": []}}) is False

def test_director_error_handling():
    """Test error handling for invalid inputs."""
    director = DirectorAgent({})
    
    with pytest.raises(ValueError):
        director.act(None)
    
    with pytest.raises(ValueError):
        director.act({"feedback": {}}) 