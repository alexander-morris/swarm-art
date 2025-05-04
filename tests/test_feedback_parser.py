import pytest
import numpy as np
from src.utils.feedback_parser import FeedbackParser

def test_parse_animation_timing():
    """Test animation timing analysis."""
    # Valid animation with good timing
    valid_svg = '''
    <svg width="100" height="100">
        <circle cx="50" cy="50" r="40">
            <animate attributeName="r" dur="1s" values="0;20;40"/>
        </circle>
    </svg>
    '''
    result = FeedbackParser.parse_animation_timing(valid_svg)
    assert result["has_timing"]
    assert result["duration"] == 1.0
    assert result["timing_error"] < 0.1  # Good timing
    
    # Missing animation element
    invalid_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>'
    result = FeedbackParser.parse_animation_timing(invalid_svg)
    assert not result["has_timing"]
    assert result["timing_error"] == 1.0
    
    # Invalid values attribute
    invalid_svg = '''
    <svg width="100" height="100">
        <circle cx="50" cy="50" r="40">
            <animate attributeName="r" dur="1s" values="0"/>
        </circle>
    </svg>
    '''
    result = FeedbackParser.parse_animation_timing(invalid_svg)
    assert result["has_timing"]
    assert result["timing_error"] > 0.5  # Significant error

def test_analyze_circle_attributes():
    """Test circle attribute analysis."""
    # Valid circle
    valid_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>'
    result = FeedbackParser.analyze_circle_attributes(valid_svg)
    assert result["has_circle"]
    assert not result["alignment_errors"]
    assert not result["attribute_errors"]
    
    # Missing attributes
    invalid_svg = '<svg width="100" height="100"><circle cx="50"/></svg>'
    result = FeedbackParser.analyze_circle_attributes(invalid_svg)
    assert result["has_circle"]
    assert len(result["attribute_errors"]) == 2  # Missing cy and r
    
    # Invalid values
    invalid_svg = '<svg width="100" height="100"><circle cx="50" cy="invalid" r="-40"/></svg>'
    result = FeedbackParser.analyze_circle_attributes(invalid_svg)
    assert result["has_circle"]
    assert any("Invalid cy value" in err for err in result["attribute_errors"])
    assert any("Negative r value" in err for err in result["alignment_errors"])
    
    # Not centered
    invalid_svg = '<svg width="100" height="100"><circle cx="50" cy="60" r="40"/></svg>'
    result = FeedbackParser.analyze_circle_attributes(invalid_svg)
    assert result["has_circle"]
    assert any("not centered" in err for err in result["alignment_errors"])

def test_generate_feedback():
    """Test comprehensive feedback generation."""
    # Valid animation sequence
    valid_frames = [
        '''
        <svg width="100" height="100">
            <circle cx="50" cy="50" r="0">
                <animate attributeName="r" dur="1s" values="0;20;40"/>
            </circle>
        </svg>
        ''',
        '''
        <svg width="100" height="100">
            <circle cx="50" cy="50" r="20">
                <animate attributeName="r" dur="1s" values="0;20;40"/>
            </circle>
        </svg>
        ''',
        '''
        <svg width="100" height="100">
            <circle cx="50" cy="50" r="40">
                <animate attributeName="r" dur="1s" values="0;20;40"/>
            </circle>
        </svg>
        '''
    ]
    result = FeedbackParser.generate_feedback(valid_frames)
    assert not result["alignment_errors"]
    assert result["timing_mismatch"] < 0.1
    assert result["overall_error"] < 0.1
    
    # Invalid sequence
    invalid_frames = [
        '''
        <svg width="100" height="100">
            <circle cx="50" cy="60" r="-10">
                <animate attributeName="r" dur="1s" values="0"/>
            </circle>
        </svg>
        '''
    ]
    result = FeedbackParser.generate_feedback(invalid_frames)
    assert result["alignment_errors"]  # Should have alignment errors
    assert result["timing_mismatch"] > 0.5  # Should have timing issues
    assert result["overall_error"] > 0.5  # Should have significant overall error
    
    # Empty sequence
    result = FeedbackParser.generate_feedback([])
    assert "No frames provided" in result["alignment_errors"]
    assert result["overall_error"] == 1.0 