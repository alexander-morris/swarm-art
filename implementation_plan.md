# Swarm Testing Implementation Plan

## Project Overview
This project implements a three-agent swarm system for testing and validating design iterations through a Director → Designer → Critic feedback loop.

## 1. Project Structure
```
swarms_testing/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── director.py
│   │   ├── designer.py
│   │   └── critic.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── svg_validator.py
│   │   └── feedback_parser.py
│   └── config/
│       ├── __init__.py
│       └── settings.py
├── tests/
│   ├── __init__.py
│   ├── test_director.py
│   ├── test_designer.py
│   ├── test_critic.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

## 2. Core Components Specification

### 2.1 Base Agent (src/agents/base.py)
```python
class BaseAgent:
    def __init__(self, config: dict):
        self.config = config
        self.history = []

    def act(self, input_data: dict) -> dict:
        raise NotImplementedError

    def validate_input(self, input_data: dict) -> bool:
        raise NotImplementedError
```

### 2.2 Director Agent (src/agents/director.py)
```python
class DirectorAgent(BaseAgent):
    def generate_initial_prompt(self) -> dict:
        """Generate the initial design directive"""
        return {
            "goal": str,
            "constraints": dict,
            "parameters": dict
        }

    def refine_prompt(self, feedback: dict) -> dict:
        """Refine the prompt based on critic feedback"""
        pass
```

### 2.3 Designer Agent (src/agents/designer.py)
```python
class DesignerAgent(BaseAgent):
    def generate_svg(self, directive: dict) -> list[str]:
        """Generate SVG frames based on directive"""
        pass

    def validate_svg(self, svg: str) -> bool:
        """Validate SVG syntax and structure"""
        pass
```

### 2.4 Critic Agent (src/agents/critic.py)
```python
class CriticAgent(BaseAgent):
    def analyze_svg(self, svg_frames: list[str]) -> dict:
        """Analyze SVG frames and generate feedback"""
        return {
            "alignment_errors": list,
            "color_issues": list,
            "timing_mismatch": float,
            "overall_error": float
        }
```

## 3. Test Specifications

### 3.1 Director Tests (tests/test_director.py)
```python
def test_director_initial_prompt():
    """Test initial prompt generation"""
    director = DirectorAgent(config={})
    prompt = director.generate_initial_prompt()
    assert isinstance(prompt, dict)
    assert "goal" in prompt
    assert "constraints" in prompt

def test_director_refinement():
    """Test prompt refinement based on feedback"""
    director = DirectorAgent(config={})
    feedback = {
        "alignment_errors": ["radius too small"],
        "timing_mismatch": 0.2
    }
    refined = director.refine_prompt(feedback)
    assert isinstance(refined, dict)
    assert refined["constraints"]["start_radius"] > 0
```

### 3.2 Designer Tests (tests/test_designer.py)
```python
def test_svg_generation():
    """Test SVG frame generation"""
    designer = DesignerAgent(config={})
    directive = {
        "goal": "circle animation",
        "constraints": {
            "frames": 30,
            "start_radius": 0,
            "end_radius": 100
        }
    }
    svgs = designer.generate_svg(directive)
    assert isinstance(svgs, list)
    assert len(svgs) == 30
    for svg in svgs:
        assert designer.validate_svg(svg)
```

### 3.3 Critic Tests (tests/test_critic.py)
```python
def test_feedback_generation():
    """Test feedback generation from SVG analysis"""
    critic = CriticAgent(config={})
    test_svgs = [
        "<svg><circle cx='50' cy='50' r='40'/></svg>",
        "<svg><rect x='10' y='10' width='80' height='80'/></svg>"
    ]
    feedback = critic.analyze_svg(test_svgs)
    assert "alignment_errors" in feedback
    assert "color_issues" in feedback
    assert "timing_mismatch" in feedback
    assert 0 <= feedback["overall_error"] <= 1
```

### 3.4 Integration Tests (tests/test_integration.py)
```python
def test_end_to_end_convergence():
    """Test full agent interaction loop"""
    director = DirectorAgent(config={})
    designer = DesignerAgent(config={})
    critic = CriticAgent(config={})
    
    directive = director.generate_initial_prompt()
    max_iterations = 5
    error_threshold = 0.05
    
    for _ in range(max_iterations):
        svgs = designer.generate_svg(directive)
        feedback = critic.analyze_svg(svgs)
        if feedback["overall_error"] < error_threshold:
            break
        directive = director.refine_prompt(feedback)
    
    assert feedback["overall_error"] < error_threshold
```

## 4. Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up project structure
- [ ] Implement BaseAgent class
- [ ] Create configuration system
- [ ] Set up testing framework

### Phase 2: Agent Implementation (Week 2)
- [ ] Implement DirectorAgent
- [ ] Implement DesignerAgent
- [ ] Implement CriticAgent
- [ ] Write unit tests for each agent

### Phase 3: Integration (Week 3)
- [ ] Implement agent communication
- [ ] Develop integration tests
- [ ] Set up end-to-end testing
- [ ] Implement error handling

### Phase 4: Refinement (Week 4)
- [ ] Optimize agent interactions
- [ ] Fine-tune convergence parameters
- [ ] Complete documentation
- [ ] Performance testing and optimization

## 5. Dependencies
```
pytest>=7.0.0
lxml>=4.9.0
numpy>=1.21.0
pydantic>=2.0.0
```

## 6. Success Criteria
1. All unit tests pass with 100% coverage
2. Integration tests demonstrate convergence within 5 iterations
3. SVG generation meets W3C standards
4. Feedback system provides actionable insights
5. System can handle various animation types and constraints 