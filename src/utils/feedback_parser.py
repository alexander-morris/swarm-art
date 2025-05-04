from typing import List, Dict, Any, Tuple
from lxml import etree
import numpy as np
from .svg_validator import SVGValidator

class FeedbackParser:
    """Utility class for analyzing SVG animations and generating feedback."""
    
    @staticmethod
    def parse_animation_timing(svg_string: str) -> Dict[str, Any]:
        """Parse animation timing information from SVG.
        
        Args:
            svg_string: String containing SVG markup
            
        Returns:
            Dictionary containing timing analysis
        """
        try:
            root = etree.fromstring(svg_string.encode('utf-8'))
            animate = SVGValidator._find_element(root, 'animate')
            
            if animate is None:
                return {
                    "has_timing": False,
                    "duration": 0,
                    "timing_error": 1.0
                }
            
            # Parse duration
            dur = animate.get('dur', '0s')
            duration = float(dur.replace('s', ''))
            
            # Parse values
            values = animate.get('values', '').split(';')
            if len(values) < 2:
                return {
                    "has_timing": True,
                    "duration": duration,
                    "timing_error": 0.8
                }
            
            # Check timing distribution
            try:
                values = [float(v) for v in values]
                expected_step = (values[-1] - values[0]) / (len(values) - 1)
                actual_steps = np.diff(values)
                timing_error = np.mean(np.abs(actual_steps - expected_step)) / expected_step
            except (ValueError, ZeroDivisionError):
                timing_error = 0.5
            
            return {
                "has_timing": True,
                "duration": duration,
                "timing_error": min(timing_error, 1.0)
            }
        except (etree.XMLSyntaxError, ValueError):
            return {
                "has_timing": False,
                "duration": 0,
                "timing_error": 1.0
            }
    
    @staticmethod
    def analyze_circle_attributes(svg_string: str) -> Dict[str, Any]:
        """Analyze circle element attributes.
        
        Args:
            svg_string: String containing SVG markup
            
        Returns:
            Dictionary containing circle analysis
        """
        try:
            root = etree.fromstring(svg_string.encode('utf-8'))
            circle = SVGValidator._find_element(root, 'circle')
            
            if circle is None:
                return {
                    "has_circle": False,
                    "alignment_errors": ["No circle element found"],
                    "attribute_errors": []
                }
            
            alignment_errors = []
            attribute_errors = []
            
            # Check required attributes
            for attr in ['cx', 'cy', 'r']:
                if attr not in circle.attrib:
                    attribute_errors.append(f"Missing {attr} attribute")
                    continue
                
                try:
                    value = float(circle.attrib[attr])
                    if value < 0:
                        alignment_errors.append(f"Negative {attr} value")
                except ValueError:
                    attribute_errors.append(f"Invalid {attr} value")
            
            # Check centering
            if 'cx' in circle.attrib and 'cy' in circle.attrib:
                try:
                    cx = float(circle.attrib['cx'])
                    cy = float(circle.attrib['cy'])
                    if abs(cx - cy) > 1:  # Allow small difference
                        alignment_errors.append("Circle not centered (cx != cy)")
                except ValueError:
                    pass
            
            return {
                "has_circle": True,
                "alignment_errors": alignment_errors,
                "attribute_errors": attribute_errors
            }
        except etree.XMLSyntaxError:
            return {
                "has_circle": False,
                "alignment_errors": ["Invalid SVG syntax"],
                "attribute_errors": []
            }
    
    @staticmethod
    def generate_feedback(svg_frames: List[str]) -> Dict[str, Any]:
        """Generate comprehensive feedback for a sequence of SVG frames.
        
        Args:
            svg_frames: List of SVG markup strings
            
        Returns:
            Dictionary containing feedback analysis
        """
        if not svg_frames:
            return {
                "alignment_errors": ["No frames provided"],
                "timing_mismatch": 1.0,
                "overall_error": 1.0
            }
        
        # Analyze first frame for structure
        circle_analysis = FeedbackParser.analyze_circle_attributes(svg_frames[0])
        
        # Analyze timing across frames
        timing_errors = []
        for frame in svg_frames:
            timing = FeedbackParser.parse_animation_timing(frame)
            if timing["has_timing"]:
                timing_errors.append(timing["timing_error"])
        
        timing_mismatch = max(timing_errors) if timing_errors else 1.0
        
        # Combine all errors
        all_errors = circle_analysis["alignment_errors"] + circle_analysis["attribute_errors"]
        
        # Calculate overall error score (0 to 1)
        error_score = 0.0
        if all_errors:
            error_score += 0.5  # 50% weight for structural errors
        if timing_mismatch > 0.1:
            error_score += 0.5 * timing_mismatch  # 50% weight for timing
        
        return {
            "alignment_errors": all_errors,
            "timing_mismatch": timing_mismatch,
            "overall_error": error_score
        } 