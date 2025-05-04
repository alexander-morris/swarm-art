import pytest
from src.agents.designer import DesignerAgent
from src.utils.svg_validator import SVGValidator
from src.utils.feedback_parser import FeedbackParser
from lxml import etree

class TestDesignerAgent:
    """Test suite for the Designer agent implementation."""
    
    @pytest.fixture
    def designer(self):
        """Create a Designer agent instance for testing."""
        return DesignerAgent()
    
    def test_initialization(self, designer):
        """Test that the Designer agent initializes correctly."""
        assert designer is not None
        assert hasattr(designer, 'generate_frame')
        assert hasattr(designer, 'validate_frame')
        assert hasattr(designer, 'create_animation')
    
    def test_generate_frame_basic(self, designer):
        """Test basic frame generation with minimal requirements."""
        frame = designer.generate_frame(
            width=100,
            height=100,
            circle_radius=40,
            animation_step=0
        )
        
        # Print frame for debugging
        print("\nGenerated SVG frame:")
        print(frame)
        
        # Validate basic SVG structure
        validation = SVGValidator.validate_all(frame, require_animation=False)
        print("\nValidation result:")
        print(validation)
        
        assert validation["is_valid"], f"SVG validation failed: {validation['errors']}"
        assert not validation["errors"]
        
        # Check circle attributes
        circle_analysis = FeedbackParser.analyze_circle_attributes(frame)
        assert circle_analysis["has_circle"]
        assert not circle_analysis["alignment_errors"]
        assert not circle_analysis["attribute_errors"]
    
    def test_generate_frame_animation(self, designer):
        """Test frame generation with animation elements."""
        frame = designer.generate_frame(
            width=100,
            height=100,
            circle_radius=40,
            animation_step=0.5,
            include_animation=True
        )
        
        # Validate animation elements
        validation = SVGValidator.validate_all(frame, require_animation=True)
        assert validation["is_valid"]
        assert not validation["errors"]
        
        # Check animation timing
        timing = FeedbackParser.parse_animation_timing(frame)
        assert timing["has_timing"]
        assert timing["duration"] > 0
        assert timing["timing_error"] < 0.1
    
    def test_create_animation_sequence(self, designer):
        """Test creation of a complete animation sequence."""
        frames = designer.create_animation(
            width=100,
            height=100,
            circle_radius=40,
            duration=1.0,
            steps=3
        )
        
        assert len(frames) == 3
        
        # Validate each frame
        for frame in frames:
            validation = SVGValidator.validate_all(frame, require_animation=True)
            assert validation["is_valid"]
            assert not validation["errors"]
        
        # Check animation consistency
        feedback = FeedbackParser.generate_feedback(frames)
        assert not feedback["alignment_errors"]
        assert feedback["timing_mismatch"] < 0.1
        assert feedback["overall_error"] < 0.1
    
    def test_error_handling(self, designer):
        """Test error handling for invalid inputs."""
        # Test invalid dimensions
        with pytest.raises(ValueError):
            designer.generate_frame(width=-100, height=100, circle_radius=40)
        
        # Test invalid circle radius
        with pytest.raises(ValueError):
            designer.generate_frame(width=100, height=100, circle_radius=1000)
        
        # Test invalid animation step
        with pytest.raises(ValueError):
            designer.generate_frame(width=100, height=100, circle_radius=40, animation_step=2.0)
    
    def test_animation_progression(self, designer):
        """Test that animation frames show proper progression."""
        frames = designer.create_animation(
            width=100,
            height=100,
            circle_radius=40,
            duration=1.0,
            steps=3
        )
        
        # Extract circle radii from each frame
        radii = []
        for frame in frames:
            root = etree.fromstring(frame.encode('utf-8'))
            circle = root.find('.//{http://www.w3.org/2000/svg}circle')
            assert circle is not None
            radius = float(circle.get('r'))
            radii.append(radius)
        
        # Verify radius progression
        assert len(radii) == 3
        assert radii[0] < radii[1] < radii[2]  # Should be increasing
        assert abs(radii[2] - 40) < 1  # Final radius should be close to target 