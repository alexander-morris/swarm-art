from typing import List, Dict, Any
from lxml import etree
from ..utils.svg_validator import SVGValidator
from ..utils.feedback_parser import FeedbackParser
import re
import numpy as np
from PIL import Image
import io
import cairosvg
import openai
import json
import os
from dotenv import load_dotenv
import time

class CriticAgent:
    """Agent responsible for analyzing and providing feedback on SVG animations."""
    
    def __init__(self):
        """Initialize the Critic agent."""
        self.timing_weight = 0.3
        self.alignment_weight = 0.3
        self.structure_weight = 0.2
        self.visual_weight = 0.2
        
        # Penalty factors
        self.timing_error_factor = 3.0
        self.duration_error_factor = 2.0
        self.alignment_error_factor = 5.0
        self.position_threshold = 10.0
        self.base_score_boost = 0.2
        self.alignment_penalty = 0.25
        self.extreme_position_threshold = 100.0
        self.timing_penalty = 0.3
        
        # Visual analysis parameters
        self.min_contrast = 0.3
        self.min_brightness = 0.2
        self.max_brightness = 0.8
        self.min_saturation = 0.3
        self.max_saturation = 0.8
        
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client if API key is available
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.use_llm = bool(self.api_key)
        
        if self.use_llm:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            print("\n" + "="*80)
            print("OpenAI API key not found. To enable LLM-powered feedback:")
            print("1. Create a .env file in the project root")
            print("2. Add your OpenAI API key:")
            print("   OPENAI_API_KEY=sk-your-api-key-here")
            print("3. Optional: Specify model (default: gpt-4-turbo-preview):")
            print("   OPENAI_MODEL=gpt-4-turbo-preview")
            print("="*80 + "\n")
        
        # Enhanced system prompt for the LLM
        self.system_prompt = """You are an expert animation critic and visual designer with deep knowledge of SVG animations, motion design, and user experience. Your role is to provide detailed, constructive feedback on SVG animations.

Focus Areas:
1. Visual Design & Aesthetics
   - Color harmony and contrast
   - Composition and balance
   - Visual hierarchy
   - Animation smoothness
   - Element distribution

2. Technical Implementation
   - SVG structure and efficiency
   - Animation timing and easing
   - Performance considerations
   - Cross-browser compatibility

3. User Experience
   - Visual clarity
   - Motion comfort
   - Engagement factors
   - Accessibility considerations

Feedback Guidelines:
- Be specific and actionable
- Reference exact metrics and values
- Explain the impact of each observation
- Provide concrete improvement suggestions
- Consider both technical and aesthetic aspects
- Balance positive feedback with constructive criticism

Example Good Feedback:
✓ "The color transition between #2196F3 and #9C27B0 creates a pleasing harmony, but the contrast ratio of 2.1:1 falls below the WCAG standard. Consider using #1565C0 for better accessibility."
✓ "The animation timing of 2.0s creates a smooth flow, but the easing function could be improved. Try using cubic-bezier(0.4, 0, 0.2, 1) for more natural motion."
✓ "The circle distribution shows good balance with a distribution score of 0.85, but the spacing between elements could be more consistent. Consider using a grid-based layout."

Example Poor Feedback:
✗ "The colors look nice."
✗ "The animation could be smoother."
✗ "Try to improve the layout."

Always provide specific, measurable feedback that can be directly implemented."""
        
        # Feedback templates
        self.feedback_templates = {
            "timing": {
                "good": "Animation timing is smooth and consistent",
                "fair": "Consider adjusting animation duration for smoother transitions",
                "poor": "Animation timing needs significant improvement - try using consistent durations"
            },
            "alignment": {
                "good": "Circle positions are well-aligned and stable",
                "fair": "Some circle positions could be better aligned",
                "poor": "Circle positions need significant adjustment for better alignment"
            },
            "structure": {
                "good": "SVG structure is clean and well-organized",
                "fair": "SVG structure could be improved for better performance",
                "poor": "SVG structure needs significant improvement"
            },
            "visual": {
                "good": "Visual appearance is clear and aesthetically pleasing",
                "fair": "Visual appearance could be improved for better clarity",
                "poor": "Visual appearance needs significant improvement"
            }
        }
    
    def generate_llm_feedback(self, metrics: Dict[str, Any], technical_issues: List[str]) -> Dict[str, List[str]]:
        """Generate natural language feedback using LLM.
        
        Args:
            metrics: Dictionary of visual and technical metrics
            technical_issues: List of technical issues found
            
        Returns:
            Dictionary containing feedback and suggestions
        """
        if not self.use_llm:
            return self.generate_fallback_feedback(metrics, technical_issues)
        
        try:
            # Add a small delay to avoid rate limiting
            time.sleep(1)  # 1 second delay between API calls
            
            # Enhanced prompt with more context and specific questions
            prompt = f"""Analyze this SVG animation with the following detailed metrics:

Visual Metrics:
- Brightness: {metrics.get('brightness', 0):.2f} (target: 0.5)
- Contrast: {metrics.get('contrast', 0):.2f} (minimum: 0.3)
- Saturation: {metrics.get('saturation', 0):.2f} (target range: 0.3-0.8)
- Color Variety: {metrics.get('color_variety', 0):.2f} (minimum: 0.1)
- Distribution Score: {metrics.get('distribution_score', 0):.2f} (minimum: 0.7)

Technical Issues:
{chr(10).join(f'- {issue}' for issue in technical_issues) if technical_issues else 'No technical issues found'}

Please provide detailed feedback in these areas:

1. Visual Design (2-3 points):
   - How do the current metrics affect the visual appeal?
   - What specific color or composition improvements would enhance the design?
   - How could the visual hierarchy be improved?

2. Technical Implementation (2-3 points):
   - What specific timing or animation improvements would enhance the flow?
   - How could the SVG structure be optimized?
   - What performance considerations should be addressed?

3. User Experience (2-3 points):
   - How does the current implementation affect user engagement?
   - What accessibility improvements could be made?
   - How could the motion design be enhanced?

Format your response as JSON with these keys:
- 'positive_feedback': List of specific positive aspects with metrics
- 'improvements': List of specific areas for improvement with metrics
- 'suggestions': List of concrete, actionable suggestions with specific values

Example format:
{{
    "positive_feedback": [
        "The color harmony between #2196F3 and #9C27B0 creates a pleasing contrast ratio of 3.2:1",
        "The animation timing of 2.0s provides a smooth, comfortable viewing experience"
    ],
    "improvements": [
        "The brightness of 0.75 exceeds the optimal range of 0.2-0.8",
        "The distribution score of 0.65 indicates uneven element spacing"
    ],
    "suggestions": [
        "Reduce brightness to 0.6 for better visual comfort",
        "Adjust circle positions to achieve a distribution score above 0.7"
    ]
}}"""
            
            # Get response from LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            feedback = response.choices[0].message.content
            feedback_dict = json.loads(feedback)
            
            return {
                "feedback": feedback_dict.get("positive_feedback", []) + feedback_dict.get("improvements", []),
                "suggestions": feedback_dict.get("suggestions", [])
            }
            
        except Exception as e:
            print(f"Error generating LLM feedback: {str(e)}")
            return self.generate_fallback_feedback(metrics, technical_issues)
    
    def generate_fallback_feedback(self, metrics: Dict[str, Any], technical_issues: List[str]) -> Dict[str, List[str]]:
        """Generate fallback feedback when LLM is not available.
        
        Args:
            metrics: Dictionary of visual and technical metrics
            technical_issues: List of technical issues found
            
        Returns:
            Dictionary containing feedback and suggestions
        """
        feedback = []
        suggestions = []
        
        # Add feedback based on metrics
        if metrics.get('brightness', 0) < self.min_brightness:
            feedback.append("The animation appears too dark")
            suggestions.append("Consider increasing the brightness of the circles")
        elif metrics.get('brightness', 0) > self.max_brightness:
            feedback.append("The animation appears too bright")
            suggestions.append("Consider decreasing the brightness of the circles")
        
        if metrics.get('contrast', 0) < self.min_contrast:
            feedback.append("The animation lacks contrast")
            suggestions.append("Try increasing the contrast between elements")
        
        if metrics.get('saturation', 0) < self.min_saturation:
            feedback.append("The colors appear too muted")
            suggestions.append("Consider increasing color saturation")
        elif metrics.get('saturation', 0) > self.max_saturation:
            feedback.append("The colors appear too intense")
            suggestions.append("Consider decreasing color saturation")
        
        if metrics.get('color_variety', 0) < 0.1:
            feedback.append("Limited color variety in the animation")
            suggestions.append("Try using more diverse colors")
        
        if metrics.get('distribution_score', 0) < 0.7:
            feedback.append("Elements could be better distributed")
            suggestions.append("Adjust circle positions for better balance")
        
        # Add technical issues
        feedback.extend(technical_issues)
        
        # Add generic feedback if none was generated
        if not feedback:
            feedback.append("The animation appears well-balanced")
            feedback.append("Colors and timing are consistent")
            suggestions.append("Consider experimenting with different color combinations")
            suggestions.append("Try adjusting animation timing for different effects")
        
        return {
            "feedback": feedback,
            "suggestions": suggestions
        }
    
    def analyze_visual_appearance(self, svg_content: str) -> Dict[str, Any]:
        """Analyze the visual appearance of the rendered SVG.
        
        Args:
            svg_content: SVG markup string
            
        Returns:
            Dictionary containing visual analysis results
        """
        try:
            # Convert SVG to PNG
            png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
            image = Image.open(io.BytesIO(png_data))
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            
            # Calculate basic metrics
            brightness = np.mean(img_array) / 255.0
            contrast = np.std(img_array) / 255.0
            
            # Calculate color metrics
            if len(img_array.shape) == 3:  # Color image
                # Convert to HSV for better color analysis
                hsv = np.array(image.convert('HSV'))
                saturation = np.mean(hsv[:, :, 1]) / 255.0
                
                # Analyze color distribution
                unique_colors = np.unique(img_array.reshape(-1, img_array.shape[2]), axis=0)
                color_variety = len(unique_colors) / (256 * 256 * 256)  # Normalize by possible colors
            else:
                saturation = 0.0
                color_variety = 0.0
            
            # Analyze composition
            # Check if circles are well-distributed
            circle_positions = []
            for match in re.finditer(r'<(?:svg:)?circle[^>]+>', svg_content):
                circle = match.group(0)
                cx_match = re.search(r'cx="([^"]+)"', circle)
                cy_match = re.search(r'cy="([^"]+)"', circle)
                if cx_match and cy_match:
                    circle_positions.append((float(cx_match.group(1)), float(cy_match.group(1))))
            
            # Calculate distribution score
            if len(circle_positions) > 1:
                positions = np.array(circle_positions)
                center = np.mean(positions, axis=0)
                distances = np.linalg.norm(positions - center, axis=1)
                distribution_score = 1.0 - np.std(distances) / np.mean(distances)
            else:
                distribution_score = 1.0
            
            # Collect technical issues
            technical_issues = []
            if brightness < self.min_brightness:
                technical_issues.append("Image is too dark")
            elif brightness > self.max_brightness:
                technical_issues.append("Image is too bright")
            if contrast < self.min_contrast:
                technical_issues.append("Image lacks contrast")
            if len(img_array.shape) == 3:
                if saturation < self.min_saturation:
                    technical_issues.append("Colors are too muted")
                elif saturation > self.max_saturation:
                    technical_issues.append("Colors are too intense")
                if color_variety < 0.1:
                    technical_issues.append("Limited color variety")
            if distribution_score < 0.7:
                technical_issues.append("Elements are not well-distributed")
            
            # Generate LLM feedback
            llm_feedback = self.generate_llm_feedback(
                metrics={
                    "brightness": brightness,
                    "contrast": contrast,
                    "saturation": saturation,
                    "color_variety": color_variety,
                    "distribution_score": distribution_score
                },
                technical_issues=technical_issues
            )
            
            # Calculate visual score
            visual_score = (
                0.3 * (1.0 - abs(brightness - 0.5) * 2) +  # Brightness score
                0.3 * min(1.0, contrast / self.min_contrast) +  # Contrast score
                0.2 * (1.0 - abs(saturation - 0.5) * 2) +  # Saturation score
                0.2 * distribution_score  # Distribution score
            )
            
            return {
                "score": visual_score,
                "feedback": llm_feedback["feedback"],
                "suggestions": llm_feedback["suggestions"],
                "metrics": {
                    "brightness": brightness,
                    "contrast": contrast,
                    "saturation": saturation,
                    "color_variety": color_variety,
                    "distribution_score": distribution_score
                }
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "feedback": [f"Error analyzing visual appearance: {str(e)}"],
                "suggestions": ["Fix SVG rendering issues"],
                "metrics": {}
            }
    
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
            - suggestions: List of suggestions for improvement
        """
        if not frames:
            return {
                "is_valid": False,
                "score": 0.0,
                "errors": ["No frames provided"],
                "feedback": ["Animation must contain at least one frame"],
                "suggestions": ["Add at least one frame to the animation"]
            }
        
        # Initialize results
        errors = []
        feedback = []
        suggestions = []
        
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
                "feedback": ["Animation contains invalid SVG frames"],
                "suggestions": ["Fix SVG structure issues in all frames"]
            }
        
        # Analyze timing
        timing_scores = []
        timing_consistency = []
        prev_duration = None
        for frame in frames:
            try:
                duration_match = re.search(r'dur="([^"]+)s"', frame)
                if not duration_match:
                    duration_match = re.search(r'<svg:animate[^>]+dur="([^"]+)s"', frame)
                
                if duration_match:
                    duration = float(duration_match.group(1))
                    if duration <= 0:
                        errors.append(f"Invalid duration: {duration}s")
                        timing_scores.append(0.0)
                        suggestions.append(f"Set a positive duration for frame {len(timing_scores)}")
                    else:
                        timing_scores.append(1.0)
                        if prev_duration is not None:
                            if abs(duration - prev_duration) > 1.0:
                                consistency_score = max(0.0, 1.0 - self.timing_error_factor * (abs(duration - prev_duration) / 10.0))
                                timing_consistency.append(consistency_score)
                                feedback.append(f"Inconsistent timing detected (difference: {abs(duration - prev_duration):.1f}s)")
                                suggestions.append(f"Use consistent duration of {prev_duration:.1f}s across all frames")
                            else:
                                timing_consistency.append(1.0)
                    prev_duration = duration
                else:
                    errors.append("Missing or invalid duration attribute")
                    timing_scores.append(0.0)
                    suggestions.append("Add duration attribute to animation elements")
            except (AttributeError, ValueError):
                errors.append("Missing or invalid duration attribute")
                timing_scores.append(0.0)
                suggestions.append("Fix duration attribute format in animation elements")
        
        # Calculate average timing score
        avg_timing = sum(timing_scores) / len(timing_scores) if timing_scores else 0.0
        if timing_consistency:
            avg_consistency = sum(timing_consistency) / len(timing_consistency)
            if avg_consistency < 0.8:
                avg_timing *= (1.0 - self.timing_penalty)
        
        # Analyze alignment
        alignment_scores = []
        prev_cx = None
        prev_cy = None
        has_alignment_issues = False
        
        for frame in frames:
            try:
                circle_match = re.search(r'<(?:svg:)?circle[^>]+>', frame)
                if not circle_match:
                    errors.append("Missing circle element")
                    alignment_scores.append(0.0)
                    suggestions.append("Add circle element to frame")
                    continue
                
                circle = circle_match.group(0)
                cx_match = re.search(r'cx="([^"]+)"', circle)
                cy_match = re.search(r'cy="([^"]+)"', circle)
                
                if cx_match and cy_match:
                    cx = float(cx_match.group(1))
                    cy = float(cy_match.group(1))
                    
                    if prev_cx is not None and prev_cy is not None:
                        position_diff = ((cx - prev_cx) ** 2 + (cy - prev_cy) ** 2) ** 0.5
                        if position_diff > self.extreme_position_threshold:
                            alignment_score = max(0.0, 1.0 - self.alignment_error_factor * (position_diff / 200.0))
                            alignment_scores.append(alignment_score)
                            feedback.append(f"Extreme circle position change detected (distance: {position_diff:.1f}px)")
                            suggestions.append(f"Reduce position change to less than {self.position_threshold}px")
                            has_alignment_issues = True
                        elif position_diff > self.position_threshold:
                            alignment_score = max(0.0, 1.0 - self.alignment_error_factor * (position_diff / 100.0))
                            alignment_scores.append(alignment_score)
                            feedback.append(f"Significant circle position change detected (distance: {position_diff:.1f}px)")
                            suggestions.append(f"Consider using smaller position changes for smoother animation")
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
                    suggestions.append("Add valid cx and cy attributes to circle elements")
            except (AttributeError, ValueError):
                errors.append("Missing or invalid circle position attributes")
                alignment_scores.append(0.0)
                suggestions.append("Fix circle position attribute format")
        
        if has_alignment_issues:
            feedback.append("Position changes detected in animation")
            suggestions.append("Use consistent circle positions across frames")
        
        # Analyze visual appearance of the last frame
        visual_analysis = self.analyze_visual_appearance(frames[-1])
        visual_score = visual_analysis["score"]
        feedback.extend(visual_analysis["feedback"])
        suggestions.extend(visual_analysis["suggestions"])
        
        # Calculate weighted scores
        avg_structure = sum(structure_scores) / len(structure_scores) if structure_scores else 0.0
        avg_alignment = sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
        
        # Calculate base score with visual weight
        base_score = (
            self.structure_weight * avg_structure +
            self.timing_weight * avg_timing +
            self.alignment_weight * avg_alignment +
            self.visual_weight * visual_score
        )
        
        # Apply quality bonuses and penalties
        if avg_structure >= 0.9 and len(errors) == 0:
            base_score = min(1.0, base_score + self.base_score_boost)
            if avg_timing >= 0.9 and avg_alignment >= 0.9 and visual_score >= 0.9:
                base_score = min(1.0, base_score + 0.1)
        
        # Apply penalties
        total_score = base_score
        if has_alignment_issues:
            total_score *= (1.0 - self.alignment_penalty)
            if any(score < 0.5 for score in alignment_scores):
                total_score *= (1.0 - self.alignment_penalty)
        if avg_timing < 0.8:
            total_score *= (1.0 - self.timing_penalty)
            if any(score < 0.5 for score in timing_consistency):
                total_score *= (1.0 - self.timing_penalty)
        if visual_score < 0.8:
            total_score *= (1.0 - self.timing_penalty)  # Use timing penalty for visual issues
        
        # Ensure minimum score for valid animations
        if len(errors) == 0 and avg_structure >= 0.9:
            if not (any(score < 0.5 for score in timing_consistency) or 
                   any(score < 0.5 for score in alignment_scores) or 
                   visual_score < 0.5):
                total_score = max(0.6, total_score)
        
        # Ensure score is between 0 and 1
        total_score = max(0.0, min(1.0, total_score))
        
        # Generate quality-based feedback
        if total_score > 0.9:
            feedback.append(self.feedback_templates["timing"]["good"])
            feedback.append(self.feedback_templates["alignment"]["good"])
            feedback.append(self.feedback_templates["structure"]["good"])
            feedback.append(self.feedback_templates["visual"]["good"])
        elif total_score > 0.7:
            feedback.append(self.feedback_templates["timing"]["fair"])
            feedback.append(self.feedback_templates["alignment"]["fair"])
            feedback.append(self.feedback_templates["structure"]["fair"])
            feedback.append(self.feedback_templates["visual"]["fair"])
        elif total_score > 0.5:
            feedback.append(self.feedback_templates["timing"]["poor"])
            feedback.append(self.feedback_templates["alignment"]["poor"])
            feedback.append(self.feedback_templates["structure"]["poor"])
            feedback.append(self.feedback_templates["visual"]["poor"])
        else:
            feedback.append("Animation needs significant improvement in all aspects")
        
        return {
            "is_valid": len(errors) == 0,
            "score": total_score,
            "errors": errors,
            "feedback": feedback,
            "suggestions": suggestions,
            "visual_metrics": visual_analysis["metrics"]
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