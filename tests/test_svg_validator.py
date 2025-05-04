import pytest
from src.utils.svg_validator import SVGValidator

def test_validate_syntax():
    """Test SVG syntax validation."""
    # Valid SVG
    valid_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>'
    is_valid, message = SVGValidator.validate_syntax(valid_svg)
    assert is_valid
    assert message == ""
    
    # Invalid SVG
    invalid_svg = '<svg><circle cx="50" cy="50" r="40"></svg>'  # Missing closing circle tag
    is_valid, message = SVGValidator.validate_syntax(invalid_svg)
    assert not is_valid
    assert "Invalid SVG syntax" in message

def test_validate_structure():
    """Test SVG structure validation."""
    # Valid structure
    valid_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>'
    is_valid, message = SVGValidator.validate_structure(valid_svg)
    assert is_valid
    assert message == ""
    
    # Missing required attributes
    invalid_svg = '<svg><circle cx="50" cy="50" r="40"/></svg>'
    is_valid, message = SVGValidator.validate_structure(invalid_svg)
    assert not is_valid
    assert "Missing required attributes" in message
    
    # Wrong root element
    invalid_svg = '<div width="100" height="100"><circle cx="50" cy="50" r="40"/></div>'
    is_valid, message = SVGValidator.validate_structure(invalid_svg)
    assert not is_valid
    assert "Root element must be 'svg'" in message

def test_validate_animation():
    """Test SVG animation validation."""
    # Valid animation
    valid_svg = '''
    <svg width="100" height="100">
        <circle cx="50" cy="50" r="40">
            <animate attributeName="r" dur="1s" values="0;40"/>
        </circle>
    </svg>
    '''
    is_valid, message = SVGValidator.validate_animation(valid_svg)
    assert is_valid
    assert message == ""
    
    # Missing animation element
    invalid_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>'
    is_valid, message = SVGValidator.validate_animation(invalid_svg)
    assert not is_valid
    assert "No animation elements found" in message
    
    # Missing animation attributes
    invalid_svg = '''
    <svg width="100" height="100">
        <circle cx="50" cy="50" r="40">
            <animate attributeName="r"/>
        </circle>
    </svg>
    '''
    is_valid, message = SVGValidator.validate_animation(invalid_svg)
    assert not is_valid
    assert "Animation element missing required attributes" in message

def test_validate_circle():
    """Test circle element validation."""
    # Valid circle
    valid_svg = '<svg width="100" height="100"><circle cx="50" cy="50" r="40"/></svg>'
    is_valid, message = SVGValidator.validate_circle(valid_svg)
    assert is_valid
    assert message == ""
    
    # Missing circle element
    invalid_svg = '<svg width="100" height="100"><rect x="10" y="10" width="80" height="80"/></svg>'
    is_valid, message = SVGValidator.validate_circle(invalid_svg)
    assert not is_valid
    assert "No circle element found" in message
    
    # Missing circle attributes
    invalid_svg = '<svg width="100" height="100"><circle/></svg>'
    is_valid, message = SVGValidator.validate_circle(invalid_svg)
    assert not is_valid
    assert "Circle missing required attributes" in message
    
    # Invalid numeric values
    invalid_svg = '<svg width="100" height="100"><circle cx="invalid" cy="50" r="40"/></svg>'
    is_valid, message = SVGValidator.validate_circle(invalid_svg)
    assert not is_valid
    assert "Invalid numeric value" in message

def test_validate_all():
    """Test comprehensive validation."""
    # Valid SVG with all components
    valid_svg = '''
    <svg width="100" height="100">
        <circle cx="50" cy="50" r="40">
            <animate attributeName="r" dur="1s" values="0;40"/>
        </circle>
    </svg>
    '''
    results = SVGValidator.validate_all(valid_svg)
    assert results["is_valid"]
    assert not results["errors"]
    assert not results["warnings"]
    
    # Invalid SVG with multiple issues
    invalid_svg = '''
    <svg>
        <circle>
            <animate attributeName="r"/>
        </circle>
    </svg>
    '''
    results = SVGValidator.validate_all(invalid_svg)
    assert not results["is_valid"]
    assert len(results["errors"]) > 1  # Should have multiple errors
    assert any("Missing required attributes" in error for error in results["errors"])
    assert any("Animation element missing required attributes" in error for error in results["errors"]) 