class DesignerAgent:
    def __init__(self):
        self.base_radius = 160
        self.circle_spacing = 128
        self.center_x = 400
        self.center_y = 300
        
    def generate_animation_params(self):
        """Generate consistent animation parameters."""
        base_duration = 2.0  # Base duration in seconds
        radius_scale = 1.25  # Scale factor for radius animation
        
        return {
            'duration': base_duration,
            'fill_duration': base_duration * 2,
            'radius_min': self.base_radius,
            'radius_max': self.base_radius * radius_scale,
            'keysplines': "0.4 0 0.2 1;0.4 0 0.2 1",
            'calcMode': "spline"
        }
        
    def generate_circle_animations(self, circle_params, animation_params):
        """Generate consistent circle animations."""
        return f'''
            <animate attributeName="r" 
                     dur="{animation_params['duration']}s" 
                     values="{circle_params['radius']};{circle_params['radius'] * 1.25};{circle_params['radius']}" 
                     repeatCount="indefinite" 
                     fill="freeze" 
                     calcMode="{animation_params['calcMode']}"
                     keySplines="{animation_params['keysplines']}"/>
            <animate attributeName="fill" 
                     dur="{animation_params['fill_duration']}s" 
                     values="{circle_params['fill']};{circle_params['alt_fill']};{circle_params['fill']}" 
                     repeatCount="indefinite" 
                     fill="freeze"
                     calcMode="{animation_params['calcMode']}"
                     keySplines="{animation_params['keysplines']}"/>
        ''' 
        
    def generate_svg(self, parameters=None):
        """Generate SVG content with the given parameters."""
        if parameters is None:
            parameters = {
                'brightness': 2.5,
                'saturation': 2.0,
                'glow': 4.5
            }
        
        # Get animation parameters
        animation_params = self.generate_animation_params()
        
        # Calculate circle positions
        circles = [
            {
                'cx': self.center_x - self.circle_spacing/2,
                'cy': self.center_y,
                'radius': self.base_radius,
                'fill': '#ff00ff',
                'alt_fill': '#00ffff',
                'opacity': 1.0
            },
            {
                'cx': self.center_x + self.circle_spacing/2,
                'cy': self.center_y,
                'radius': self.base_radius,
                'fill': '#00ffff',
                'alt_fill': '#ff00ff',
                'opacity': 1.0
            },
            {
                'cx': self.center_x,
                'cy': self.center_y + self.circle_spacing*0.8,
                'radius': self.base_radius,
                'fill': '#ffff00',
                'alt_fill': '#ff00ff',
                'opacity': 1.0
            }
        ]
        
        # Generate SVG content
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
    <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#111111;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="{parameters['glow']}" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="brightness">
            <feComponentTransfer>
                <feFuncR type="linear" slope="{parameters['brightness']}"/>
                <feFuncG type="linear" slope="{parameters['brightness']}"/>
                <feFuncB type="linear" slope="{parameters['brightness']}"/>
            </feComponentTransfer>
        </filter>
        <filter id="saturation">
            <feColorMatrix type="saturate" values="{parameters['saturation']}"/>
        </filter>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgGradient)"/>
    
    <!-- Main circles -->
    {self._generate_circles(circles, animation_params)}
    
    <!-- Center decorative circle -->
    {self._generate_decorative_circle(animation_params)}
</svg>'''
        
        return svg_content
        
    def _generate_circles(self, circles, animation_params):
        """Generate SVG for the main circles."""
        svg = ""
        for i, circle in enumerate(circles):
            svg += f'''
    <!-- Circle {i+1} -->
    <circle cx="{circle['cx']}" cy="{circle['cy']}" r="{circle['radius']}" 
            fill="{circle['fill']}"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="{circle['opacity']}">
        {self.generate_circle_animations(circle, animation_params)}
    </circle>
    '''
        return svg
        
    def _generate_decorative_circle(self, animation_params):
        """Generate SVG for the decorative center circle."""
        circle = {
            'cx': self.center_x,
            'cy': self.center_y,
            'radius': self.base_radius/2,
            'fill': '#ff8800',
            'alt_fill': '#ff00ff',
            'opacity': 0.9
        }
        
        return f'''
    <!-- Decorative circle -->
    <circle cx="{circle['cx']}" cy="{circle['cy']}" r="{circle['radius']}"
            fill="{circle['fill']}"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="{circle['opacity']}">
        {self.generate_circle_animations(circle, animation_params)}
    </circle>''' 