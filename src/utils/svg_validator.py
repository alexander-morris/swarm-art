from typing import List, Dict, Any, Tuple
from lxml import etree
import re

class SVGValidator:
    """Utility class for validating SVG content and structure."""
    
    SVG_NS = "http://www.w3.org/2000/svg"
    NSMAP = {"svg": SVG_NS}
    
    @staticmethod
    def _find_element(root: etree._Element, tag: str) -> etree._Element:
        """Helper method to find an element with or without namespace.
        
        Args:
            root: Root element to search in
            tag: Tag name to find
            
        Returns:
            Found element or None
        """
        element = root.find(f'.//{tag}')
        if element is None:
            element = root.find(f'.//{{{SVGValidator.SVG_NS}}}{tag}')
        return element
    
    @staticmethod
    def _find_elements(root: etree._Element, tag: str) -> List[etree._Element]:
        """Helper method to find all elements with or without namespace.
        
        Args:
            root: Root element to search in
            tag: Tag name to find
            
        Returns:
            List of found elements
        """
        elements = root.findall(f'.//{tag}')
        elements.extend(root.findall(f'.//{{{SVGValidator.SVG_NS}}}{tag}'))
        return elements
    
    @staticmethod
    def validate_syntax(svg_content):
        """Validate basic SVG syntax."""
        try:
            # Remove XML declaration and normalize whitespace
            content = re.sub(r'<\?xml[^>]*\?>', '', svg_content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Check for required SVG elements and proper XML structure
            if not re.search(r'<(?:svg:|)svg[^>]*>', content):
                return False, "Invalid SVG syntax: Missing SVG root element"
            
            # Count tags more accurately
            open_tags = len(re.findall(r'<([^/][^>]*?)(?<!/)>', content))  # Opening tags that aren't self-closing
            close_tags = len(re.findall(r'</[^>]+>', content))  # Closing tags
            self_closing = len(re.findall(r'<[^>]+/>', content))  # Self-closing tags
            
            # Debug output
            print(f"\nTag counting:")
            print(f"Open tags: {open_tags}")
            print(f"Close tags: {close_tags}")
            print(f"Self-closing tags: {self_closing}")
            
            # Check for basic XML structure
            if not re.search(r'<svg[^>]*>.*</svg>', content, re.DOTALL):
                return False, "Invalid SVG syntax: Missing closing SVG tag"
            
            # Check for common SVG elements
            if not re.search(r'<circle[^>]*>', content):
                return False, "Invalid SVG syntax: No circle elements found"
            
            return True, ""
        except Exception as e:
            return False, f"Invalid SVG syntax: {str(e)}"

    @staticmethod
    def validate_structure(svg_content):
        """Validate SVG structure."""
        try:
            # Remove XML declaration and normalize whitespace
            content = re.sub(r'<\?xml[^>]*\?>', '', svg_content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Check root element
            if not re.search(r'^[^<]*<(?:svg:|)svg[^>]*>', content):
                return False, "Root element must be 'svg'"
            
            # Check for required attributes
            if not re.search(r'<(?:svg:|)svg[^>]+width="[^"]+"[^>]+height="[^"]+"', content):
                return False, "Missing required attributes"
            return True, ""
        except Exception as e:
            return False, f"Invalid SVG structure: {str(e)}"

    @staticmethod
    def validate_circle(svg_content):
        """Validate circle element."""
        try:
            # Remove XML declaration and normalize whitespace
            content = re.sub(r'<\?xml[^>]*\?>', '', svg_content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Check for circle element
            if not re.search(r'<(?:svg:|)circle[^>]+/?>', content):
                return False, "No circle element found"
            
            # Check for required circle attributes
            circle_match = re.search(r'<(?:svg:|)circle[^>]+>', content)
            if not circle_match:
                return False, "Circle missing required attributes"
            
            circle = circle_match.group(0)
            
            # Extract attribute values
            cx_match = re.search(r'cx="([^"]+)"', circle)
            cy_match = re.search(r'cy="([^"]+)"', circle)
            r_match = re.search(r'r="([^"]+)"', circle)
            
            # Validate numeric values
            if cx_match and cy_match and r_match:
                try:
                    float(cx_match.group(1))
                    float(cy_match.group(1))
                    float(r_match.group(1))
                except ValueError:
                    return False, "Invalid numeric values for circle attributes"
            else:
                return False, "Circle missing required attributes"
                
            return True, ""
        except Exception as e:
            return False, f"Invalid circle element: {str(e)}"

    @staticmethod
    def validate_animation(svg_content):
        """Validate animation element."""
        try:
            # Remove XML declaration and normalize whitespace
            content = re.sub(r'<\?xml[^>]*\?>', '', svg_content)
            content = re.sub(r'\s+', ' ', content).strip()
            
            # Check for animation element
            if not re.search(r'<(?:svg:|)animate[^>]+/?>', content):
                return False, "No animation elements found"
            
            # Check for required animation attributes
            if not re.search(r'<(?:svg:|)animate[^>]+attributeName="[^"]+"[^>]+dur="[^"]+"[^>]+values="[^"]+"[^>]+repeatCount="[^"]+"', content):
                return False, "Animation element missing required attributes"
            return True, ""
        except Exception as e:
            return False, f"Invalid animation element: {str(e)}"

    @staticmethod
    def validate_all(svg_content, require_animation=False):
        """Perform comprehensive validation of SVG content.
        
        Args:
            svg_content: String containing SVG markup
            require_animation: Whether to require animation elements
            
        Returns:
            Dictionary containing validation results
        """
        results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Print the SVG content for debugging
        print("\nValidating SVG content:")
        print(svg_content)
        
        # Collect all validation results
        validations = [
            ("syntax", SVGValidator.validate_syntax),
            ("structure", SVGValidator.validate_structure),
            ("circle", SVGValidator.validate_circle)
        ]
        
        # Always check animation if present
        animation_valid, animation_message = SVGValidator.validate_animation(svg_content)
        if require_animation or not animation_message.startswith("No animation"):
            validations.append(("animation", SVGValidator.validate_animation))
        
        for name, validate in validations:
            is_valid, message = validate(svg_content)
            print(f"\n{name} validation:")
            print(f"Valid: {is_valid}")
            print(f"Message: {message}")
            if not is_valid:
                results["is_valid"] = False
                results["errors"].append(message)
        
        return results 