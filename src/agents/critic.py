from typing import List, Dict, Any
from lxml import etree
from ..utils.svg_validator import SVGValidator
from ..utils.feedback_parser import FeedbackParser
import re

class CriticAgent:
    """Agent responsible for analyzing and providing feedback on SVG animations."""
    
    def __init__(self):
        """Initialize the Critic agent."""
        self.timing_weight = 0.4
        self.alignment_weight = 0.4
        self.structure_weight = 0.2
        
        # Penalty factors
        self.timing_error_factor = 3.0  # More aggressive timing penalty
        self.duration_error_factor = 2.0  # Penalty for duration inconsistency
        self.alignment_error_factor = 5.0  # Even more aggressive alignment penalty
        self.position_threshold = 10.0  # Threshold for position changes (in pixels)
        self.base_score_boost = 0.2  # Boost for structurally valid animations
        self.alignment_penalty = 0.25  # Additional penalty for alignment issues
        self.extreme_position_threshold = 100.0  # Threshold for extreme position changes
        self.timing_penalty = 0.3  # Additional penalty for timing issues
    
    def analyze_animation(self, frames: List[str]) -> Dict[str, Any]:
        """Analyze an SVG animation sequence.
        
        Args:
            frames: List of SVG markup strings
            
        Returns:
            Dictionary containing analysis results:
            - is_valid: Whether the animation is valid
            - score: Overall quality score (0 to 1)
            - errors: List of error messages
            - feedback: List of feedback messages
        """
        if not frames:
            return {
                "is_valid": False,
                "score": 0.0,
                "errors": ["No frames provided"],
                "feedback": ["Animation must contain at least one frame"]
            }
        
        # Initialize results
        errors = []
        feedback = []
        
        # Validate SVG structure
        structure_scores = []
        for i, frame in enumerate(frames):
            validation = SVGValidator.validate_all(frame, require_animation=True)
            if not validation["is_valid"]:
                errors.extend([f"Frame {i}: {error}" for error in validation["errors"]])
                structure_scores.append(0.0)
            else:
                structure_scores.append(1.0)
        
        # Early return if no valid frames
        if not structure_scores or all(score == 0 for score in structure_scores):
            return {
                "is_valid": False,
                "score": 0.0,
                "errors": errors,
                "feedback": ["Animation contains invalid SVG frames"]
            }
        
        # Analyze timing
        timing_scores = []
        timing_consistency = []
        prev_duration = None
        for frame in frames:
            try:
                # Handle both namespaced and non-namespaced SVG
                duration_match = re.search(r'dur="([^"]+)s"', frame)
                if not duration_match:
                    duration_match = re.search(r'<svg:animate[^>]+dur="([^"]+)s"', frame)
                
                if duration_match:
                    duration = float(duration_match.group(1))
                    if duration <= 0:
                        errors.append(f"Invalid duration: {duration}s")
                        timing_scores.append(0.0)
                    else:
                        timing_scores.append(1.0)
                        if prev_duration is not None:
                            # Check timing consistency
                            if abs(duration - prev_duration) > 1.0:  # More than 1 second difference
                                consistency_score = max(0.0, 1.0 - self.timing_error_factor * (abs(duration - prev_duration) / 10.0))
                                timing_consistency.append(consistency_score)
                                feedback.append(f"Inconsistent timing detected (difference: {abs(duration - prev_duration):.1f}s)")
                            else:
                                timing_consistency.append(1.0)
                    prev_duration = duration
                else:
                    errors.append("Missing or invalid duration attribute")
                    timing_scores.append(0.0)
            except (AttributeError, ValueError):
                errors.append("Missing or invalid duration attribute")
                timing_scores.append(0.0)
        
        # Calculate average timing score with consistency
        if timing_scores:
            avg_timing_value = sum(timing_scores) / len(timing_scores)
            if timing_consistency:
                avg_consistency = sum(timing_consistency) / len(timing_consistency)
                # Apply timing penalty for inconsistent timing
                if avg_consistency < 0.8:
                    avg_timing = avg_timing_value * (1.0 - self.timing_penalty)
                else:
                    avg_timing = avg_timing_value
            else:
                avg_timing = avg_timing_value
        else:
            avg_timing = 0.0
        
        # Analyze alignment
        alignment_scores = []
        prev_cx = None
        prev_cy = None
        has_alignment_issues = False
        
        for frame in frames:
            try:
                # Handle both namespaced and non-namespaced SVG
                circle_match = re.search(r'<(?:svg:)?circle[^>]+>', frame)
                if not circle_match:
                    errors.append("Missing circle element")
                    alignment_scores.append(0.0)
                    continue
                
                circle = circle_match.group(0)
                cx_match = re.search(r'cx="([^"]+)"', circle)
                cy_match = re.search(r'cy="([^"]+)"', circle)
                
                if cx_match and cy_match:
                    cx = float(cx_match.group(1))
                    cy = float(cy_match.group(1))
                    
                    # Check position consistency
                    if prev_cx is not None and prev_cy is not None:
                        position_diff = ((cx - prev_cx) ** 2 + (cy - prev_cy) ** 2) ** 0.5  # Euclidean distance
                        if position_diff > self.extreme_position_threshold:
                            # Extreme penalty for very large position changes
                            alignment_score = max(0.0, 1.0 - self.alignment_error_factor * (position_diff / 200.0))
                            alignment_scores.append(alignment_score)
                            feedback.append(f"Extreme circle position change detected (distance: {position_diff:.1f}px)")
                            has_alignment_issues = True
                        elif position_diff > self.position_threshold:
                            # Standard penalty for moderate position changes
                            alignment_score = max(0.0, 1.0 - self.alignment_error_factor * (position_diff / 100.0))
                            alignment_scores.append(alignment_score)
                            feedback.append(f"Significant circle position change detected (distance: {position_diff:.1f}px)")
                            has_alignment_issues = True
                        else:
                            alignment_scores.append(1.0)
                    else:
                        alignment_scores.append(1.0)
                    
                    prev_cx = cx
                    prev_cy = cy
                else:
                    errors.append("Missing or invalid circle position attributes")
                    alignment_scores.append(0.0)
            except (AttributeError, ValueError):
                errors.append("Missing or invalid circle position attributes")
                alignment_scores.append(0.0)
        
        if has_alignment_issues:
            feedback.append("Position changes detected in animation")
        
        # Calculate weighted scores with safeguards
        avg_structure = sum(structure_scores) / len(structure_scores) if structure_scores else 0.0
        avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
        
        # Check if this is a perfect animation
        is_perfect = (
            avg_structure == 1.0 and
            all(score >= 0.95 for score in timing_scores) and
            all(score >= 0.95 for score in timing_consistency) and
            all(score >= 0.95 for score in alignment_scores)
        )
        
        # Check if this is a good animation
        is_good = (
            avg_structure >= 0.9 and
            all(score >= 0.9 for score in timing_scores) and
            all(score >= 0.9 for score in timing_consistency) and
            all(score >= 0.9 for score in alignment_scores)
        )
        
        # Check if this is a decent animation
        is_decent = (
            avg_structure >= 0.8 and
            all(score >= 0.8 for score in timing_scores) and
            (not timing_consistency or all(score >= 0.8 for score in timing_consistency)) and
            all(score >= 0.8 for score in alignment_scores)
        )
        
        # Calculate base score with boost for valid animations
        base_score = (
            self.structure_weight * avg_structure +
            self.timing_weight * avg_timing +
            self.alignment_weight * avg_alignment
        )
        
        # Apply boost for structurally valid animations
        if avg_structure >= 0.9 and len(errors) == 0:
            base_score = min(1.0, base_score + self.base_score_boost)
            if avg_timing >= 0.9 and avg_alignment >= 0.9:
                base_score = min(1.0, base_score + 0.1)  # Additional boost for good timing and alignment
        
        # Apply quality bonuses and penalties
        if is_perfect:
            total_score = 1.0
        elif is_good:
            total_score = 0.9
        elif is_decent:
            total_score = 0.85
        elif base_score >= 0.6 and avg_alignment >= 0.8 and avg_timing >= 0.8:
            total_score = 0.8
        else:
            # Apply penalties for specific issues
            total_score = base_score
            if has_alignment_issues:
                total_score *= (1.0 - self.alignment_penalty)  # Stronger penalty for alignment issues
                if any(score < 0.5 for score in alignment_scores):  # Additional penalty for severe alignment issues
                    total_score *= (1.0 - self.alignment_penalty)
            if avg_timing < 0.8:
                total_score *= (1.0 - self.timing_penalty)  # Stronger penalty for timing issues
                if any(score < 0.5 for score in timing_consistency):  # Additional penalty for severe timing issues
                    total_score *= (1.0 - self.timing_penalty)
        
        # Ensure minimum score for valid animations with good structure
        if len(errors) == 0 and avg_structure >= 0.9:
            # Only apply minimum score if there are no severe issues
            if not (any(score < 0.5 for score in timing_consistency) or any(score < 0.5 for score in alignment_scores)):
                total_score = max(0.6, total_score)  # Minimum score of 0.6 for valid animations
        
        # Ensure score is between 0 and 1
        total_score = max(0.0, min(1.0, total_score))
        
        # Generate overall feedback
        if total_score > 0.9:
            feedback.append("Animation demonstrates excellent quality and smooth transitions")
        elif total_score > 0.7:
            feedback.append("Animation is good but has minor issues that could be improved")
        elif total_score > 0.5:
            feedback.append("Animation needs significant improvements in timing and alignment")
        else:
            feedback.append("Animation has major issues and requires extensive revision")
        
        return {
            "is_valid": len(errors) == 0,
            "score": total_score,
            "errors": errors,
            "feedback": feedback
        }
    
    def generate_feedback(self, frames: List[str]) -> List[str]:
        """Generate detailed feedback for an animation sequence.
        
        Args:
            frames: List of SVG markup strings
            
        Returns:
            List of feedback messages
        """
        analysis = self.analyze_animation(frames)
        return analysis["feedback"]
    
    def calculate_score(self, frames: List[str]) -> float:
        """Calculate the overall quality score for an animation.
        
        Args:
            frames: List of SVG markup strings
            
        Returns:
            Quality score between 0 and 1
        """
        analysis = self.analyze_animation(frames)
        return analysis["score"] 