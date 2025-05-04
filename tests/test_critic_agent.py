import pytest
from src.agents.critic import CriticAgent
from src.agents.designer import DesignerAgent
from src.utils.feedback_parser import FeedbackParser

class TestCriticAgent:
    """Test suite for the Critic agent implementation."""
    
    @pytest.fixture
    def critic(self):
        """Create a Critic agent instance for testing."""
        return CriticAgent()
    
    @pytest.fixture
    def designer(self):
        """Create a Designer agent for generating test animations."""
        return DesignerAgent()
    
    def test_initialization(self, critic):
        """Test that the Critic agent initializes correctly."""
        assert critic is not None
        assert hasattr(critic, 'analyze_animation')
        assert hasattr(critic, 'generate_feedback')
        assert hasattr(critic, 'calculate_score')
    
    def test_analyze_animation_perfect(self, critic, designer):
        """Test analysis of a perfect animation."""
        # Generate a perfect animation sequence
        frames = designer.create_animation(
            width=100,
            height=100,
            circle_radius=40,
            duration=1.0,
            steps=3
        )
        
        analysis = critic.analyze_animation(frames)
        assert analysis["is_valid"]
        assert analysis["score"] > 0.9  # Should be nearly perfect
        assert not analysis["errors"]
        assert len(analysis["feedback"]) > 0  # Should provide positive feedback
    
    def test_analyze_animation_missing_frames(self, critic):
        """Test analysis of an animation with missing frames."""
        analysis = critic.analyze_animation([])
        assert not analysis["is_valid"]
        assert analysis["score"] == 0.0
        assert "No frames provided" in analysis["errors"]
    
    def test_analyze_animation_invalid_frames(self, critic):
        """Test analysis of an animation with invalid frames."""
        invalid_frames = ['<svg></svg>', '<invalid>xml</invalid>']
        analysis = critic.analyze_animation(invalid_frames)
        assert not analysis["is_valid"]
        assert analysis["score"] < 0.5
        assert len(analysis["errors"]) > 0
    
    def test_analyze_animation_timing_issues(self, critic):
        """Test analysis of an animation with timing issues."""
        # Create frames with inconsistent timing
        frames = [
            '<svg width="100" height="100"><circle cx="50" cy="50" r="10"><animate attributeName="r" dur="1s" values="0;10;20"/></circle></svg>',
            '<svg width="100" height="100"><circle cx="50" cy="50" r="20"><animate attributeName="r" dur="3s" values="0;10;20"/></circle></svg>',  # Different duration
            '<svg width="100" height="100"><circle cx="50" cy="50" r="40"><animate attributeName="r" dur="1s" values="0;40"/></circle></svg>'  # Different values
        ]
        
        analysis = critic.analyze_animation(frames)
        assert analysis["is_valid"]  # Still valid SVG
        assert analysis["score"] < 0.8  # Should be penalized for timing
        assert any("timing" in feedback.lower() or "duration" in feedback.lower() for feedback in analysis["feedback"])
    
    def test_analyze_animation_alignment_issues(self, critic):
        """Test analysis of an animation with alignment issues."""
        # Create frames with misaligned circles
        frames = [
            '<svg width="100" height="100"><circle cx="50" cy="50" r="10"><animate attributeName="r" dur="1s" values="0;40"/></circle></svg>',
            '<svg width="100" height="100"><circle cx="90" cy="90" r="20"><animate attributeName="r" dur="1s" values="0;40"/></circle></svg>',  # Severe misalignment
            '<svg width="100" height="100"><circle cx="50" cy="50" r="40"><animate attributeName="r" dur="1s" values="0;40"/></circle></svg>'
        ]
        
        analysis = critic.analyze_animation(frames)
        assert analysis["is_valid"]  # Still valid SVG
        assert analysis["score"] < 0.8  # Should be penalized for alignment
        assert any("position" in feedback.lower() for feedback in analysis["feedback"])  # Should mention position change
    
    def test_calculate_score_weights(self, critic):
        """Test that scoring weights different factors appropriately."""
        # Create base frames with perfect alignment and timing
        base_frames = [
            '<svg width="100" height="100"><circle cx="50" cy="50" r="10"><animate attributeName="r" dur="1s" values="0;40"/></circle></svg>',
            '<svg width="100" height="100"><circle cx="50" cy="50" r="20"><animate attributeName="r" dur="1s" values="0;40"/></circle></svg>',
            '<svg width="100" height="100"><circle cx="50" cy="50" r="40"><animate attributeName="r" dur="1s" values="0;40"/></circle></svg>'
        ]
        
        # Get base score
        base_analysis = critic.analyze_animation(base_frames)
        base_score = base_analysis["score"]
        assert base_score >= 0.6, "Base score should be decent for valid animation"
        
        # Create frames with timing issues - make duration vary significantly
        timing_frames = [
            base_frames[0],  # Keep first frame at 1s
            base_frames[1].replace('dur="1s"', 'dur="10s"'),  # Middle frame much slower
            base_frames[2]  # Keep last frame at 1s
        ]
        timing_analysis = critic.analyze_animation(timing_frames)
        
        # Create frames with alignment issues - make position change extremely dramatic
        alignment_frames = base_frames.copy()
        alignment_frames[1] = alignment_frames[1].replace('cx="50"', 'cx="250"').replace('cy="50"', 'cy="250"')  # Extreme position change
        alignment_analysis = critic.analyze_animation(alignment_frames)
        
        # Verify that both issues affect the score differently
        assert base_score > timing_analysis["score"], "Timing issues should reduce score"
        assert base_score > alignment_analysis["score"], "Alignment issues should reduce score"
        assert timing_analysis["score"] != alignment_analysis["score"], "Different issues should have different impacts" 