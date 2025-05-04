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
    def validate_syntax(svg_string: str) -> Tuple[bool, str]:
        """Validate SVG syntax using lxml.
        
        Args:
            svg_string: String containing SVG markup
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            etree.fromstring(svg_string.encode('utf-8'))
            return True, ""
        except etree.XMLSyntaxError as e:
            return False, f"Invalid SVG syntax: {str(e)}"
    
    @staticmethod
    def validate_structure(svg_string: str) -> Tuple[bool, str]:
        """Validate SVG structure and required elements.
        
        Args:
            svg_string: String containing SVG markup
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            root = etree.fromstring(svg_string.encode('utf-8'))
            
            # Check root element (with or without namespace)
            if not (root.tag == 'svg' or root.tag == f'{{{SVGValidator.SVG_NS}}}svg'):
                return False, "Root element must be 'svg'"
            
            # Check for required attributes
            required_attrs = ['width', 'height']
            missing_attrs = [attr for attr in required_attrs if attr not in root.attrib]
            if missing_attrs:
                return False, f"Missing required attributes: {', '.join(missing_attrs)}"
            
            return True, ""
        except etree.XMLSyntaxError as e:
            return False, f"Invalid SVG structure: {str(e)}"
    
    @staticmethod
    def validate_animation(svg_string: str) -> Tuple[bool, str]:
        """Validate SVG animation elements and attributes.
        
        Args:
            svg_string: String containing SVG markup
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            root = etree.fromstring(svg_string.encode('utf-8'))
            
            # Check for animation elements
            animate_elements = SVGValidator._find_elements(root, 'animate')
            if not animate_elements:
                return False, "No animation elements found"
            
            # Check animation attributes
            required_attrs = ['attributeName', 'dur', 'values']
            for animate in animate_elements:
                missing_attrs = [attr for attr in required_attrs if attr not in animate.attrib]
                if missing_attrs:
                    return False, f"Animation element missing required attributes: {', '.join(missing_attrs)}"
            
            return True, ""
        except etree.XMLSyntaxError as e:
            return False, f"Invalid animation structure: {str(e)}"
    
    @staticmethod
    def validate_circle(svg_string: str) -> Tuple[bool, str]:
        """Validate circle element and its attributes.
        
        Args:
            svg_string: String containing SVG markup
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            root = etree.fromstring(svg_string.encode('utf-8'))
            
            # Check for circle element
            circle = SVGValidator._find_element(root, 'circle')
            if circle is None:
                return False, "No circle element found"
            
            # Check required circle attributes
            required_attrs = ['cx', 'cy', 'r']
            missing_attrs = [attr for attr in required_attrs if attr not in circle.attrib]
            if missing_attrs:
                return False, f"Circle missing required attributes: {', '.join(missing_attrs)}"
            
            # Validate numeric values
            for attr in ['cx', 'cy', 'r']:
                try:
                    float(circle.attrib[attr])
                except ValueError:
                    return False, f"Invalid numeric value for {attr}"
            
            return True, ""
        except etree.XMLSyntaxError as e:
            return False, f"Invalid circle structure: {str(e)}"
    
    @staticmethod
    def validate_all(svg_string: str, require_animation: bool = False) -> Dict[str, Any]:
        """Perform all validations on the SVG string.
        
        Args:
            svg_string: String containing SVG markup
            require_animation: Whether to require animation elements
            
        Returns:
            Dictionary containing validation results
        """
        results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Run all validations
        validations = [
            ("syntax", SVGValidator.validate_syntax),
            ("structure", SVGValidator.validate_structure),
            ("circle", SVGValidator.validate_circle)
        ]
        
        # Only validate animation if required
        if require_animation:
            validations.append(("animation", SVGValidator.validate_animation))
        
        for name, validator in validations:
            is_valid, message = validator(svg_string)
            if not is_valid:
                results["is_valid"] = False
                results["errors"].append(f"{name}: {message}")
        
        return results 