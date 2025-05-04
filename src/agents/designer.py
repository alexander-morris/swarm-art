from typing import List, Dict, Any
from lxml import etree
from ..utils.svg_validator import SVGValidator
from ..utils.feedback_parser import FeedbackParser

class DesignerAgent:
    """Agent responsible for generating SVG animations."""
    
    def __init__(self):
        """Initialize the Designer agent."""
        self.svg_ns = "http://www.w3.org/2000/svg"
        self.nsmap = {"svg": self.svg_ns}
    
    def generate_frame(
        self,
        width: int,
        height: int,
        circle_radius: float,
        animation_step: float = 0,
        include_animation: bool = False
    ) -> str:
        """Generate a single SVG frame.
        
        Args:
            width: Frame width
            height: Frame height
            circle_radius: Target circle radius
            animation_step: Animation progress (0 to 1)
            include_animation: Whether to include animation elements
            
        Returns:
            SVG markup string
            
        Raises:
            ValueError: If input parameters are invalid
        """
        # Validate inputs
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        if circle_radius <= 0 or circle_radius > min(width, height) / 2:
            raise ValueError("Circle radius must be positive and fit within frame")
        if not 0 <= animation_step <= 1:
            raise ValueError("Animation step must be between 0 and 1")
        
        # Calculate current radius based on animation step
        current_radius = max(0.1, circle_radius * animation_step)  # Ensure minimum radius
        
        # Create SVG root with namespace
        root = etree.Element(f"{{{self.svg_ns}}}svg", nsmap=self.nsmap)
        root.set("width", str(width))
        root.set("height", str(height))
        root.set("version", "1.1")  # Add SVG version
        
        # Create circle with namespace
        circle = etree.SubElement(root, f"{{{self.svg_ns}}}circle")
        circle.set("cx", str(width / 2))
        circle.set("cy", str(height / 2))
        circle.set("r", str(current_radius))
        
        # Add animation if requested
        if include_animation:
            animate = etree.SubElement(circle, f"{{{self.svg_ns}}}animate")
            animate.set("attributeName", "r")
            animate.set("dur", "1s")
            animate.set("values", f"0;{circle_radius}")
            animate.set("repeatCount", "1")  # Add repeatCount
            animate.set("fill", "freeze")  # Add fill mode
        
        return etree.tostring(root, encoding="unicode", pretty_print=True)
    
    def validate_frame(self, frame: str) -> Dict[str, Any]:
        """Validate a single SVG frame.
        
        Args:
            frame: SVG markup string
            
        Returns:
            Dictionary containing validation results
        """
        return SVGValidator.validate_all(frame)
    
    def create_animation(
        self,
        width: int,
        height: int,
        circle_radius: float,
        duration: float,
        steps: int
    ) -> List[str]:
        """Create a sequence of SVG frames for animation.
        
        Args:
            width: Frame width
            height: Frame height
            circle_radius: Target circle radius
            duration: Animation duration in seconds
            steps: Number of frames to generate
            
        Returns:
            List of SVG markup strings
            
        Raises:
            ValueError: If input parameters are invalid
        """
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if steps < 2:
            raise ValueError("Animation must have at least 2 steps")
        
        frames = []
        for i in range(steps):
            animation_step = i / (steps - 1)
            frame = self.generate_frame(
                width=width,
                height=height,
                circle_radius=circle_radius,
                animation_step=animation_step,
                include_animation=True
            )
            frames.append(frame)
        
        return frames 