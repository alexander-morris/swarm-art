import os
import sys
import json
import time
import tkinter as tk
from tkinter import ttk
import cairosvg
from PIL import Image, ImageTk
import io
import re
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.designer import DesignerAgent
from src.agents.critic import CriticAgent
from src.utils.svg_validator import SVGValidator
from src.utils.feedback_parser import FeedbackParser
from src.agents.director import DirectorAgent
from src.utils.agent_memory import AgentMemory

class TestDisplay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vennkoii Consensus Visualization")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create canvas for SVG display
        self.canvas = tk.Canvas(self.main_frame, width=800, height=600, bg='black')
        self.canvas.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        
        # Create status label
        self.status_label = ttk.Label(self.main_frame, text="Initializing visualization...", foreground='white')
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Create agent output frames
        self.create_agent_outputs()
        
        # Initialize agents
        self.designer = DesignerAgent()
        self.critic = CriticAgent()
        self.director = DirectorAgent()
        self.memory = AgentMemory()
        self.iteration = 0
        self.max_iterations = 10
        self.output_dir = "output"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load initial parameters
        self.load_parameters()
        
        # Start test loop
        self.root.after(100, self.run_tests)
    
    def create_agent_outputs(self):
        """Create frames for agent outputs."""
        # Create a frame for agent outputs
        self.agent_frame = ttk.Frame(self.main_frame)
        self.agent_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Designer output
        self.designer_frame = ttk.LabelFrame(self.agent_frame, text="Designer Agent", padding="5")
        self.designer_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.designer_text = tk.Text(self.designer_frame, height=6, width=40, bg='black', fg='#2196F3')
        self.designer_text.pack(fill=tk.BOTH, expand=True)
        
        # Critic output
        self.critic_frame = ttk.LabelFrame(self.agent_frame, text="Critic Agent", padding="5")
        self.critic_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        self.critic_text = tk.Text(self.critic_frame, height=6, width=40, bg='black', fg='#FFD700')
        self.critic_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        self.agent_frame.columnconfigure(0, weight=1)
        self.agent_frame.columnconfigure(1, weight=1)
    
    def update_agent_output(self, agent_name: str, message: str):
        """Update the output text for a specific agent."""
        if agent_name == "designer":
            text_widget = self.designer_text
        elif agent_name == "critic":
            text_widget = self.critic_text
        else:
            return
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        # Update text
        text_widget.insert(tk.END, formatted_message)
        text_widget.see(tk.END)  # Scroll to bottom
        
        # Keep only last 100 lines
        lines = text_widget.get("1.0", tk.END).splitlines()
        if len(lines) > 100:
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, "\n".join(lines[-100:]) + "\n")
    
    def load_parameters(self):
        """Load visualization parameters from prompt file."""
        try:
            with open(os.path.join(project_root, 'prompt-update.md'), 'r') as f:
                content = f.read()
                
            # Extract JSON parameters
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                self.params = json.loads(json_match.group(1))
            else:
                self.params = {
                    "animation": {"duration": 2.0, "steps": 30},
                    "visualization": {
                        "circle_count": 3,
                        "base_radius": 40,
                        "color_scheme": {
                            "individual": ["#2196F3", "#9C27B0"],
                            "consensus": ["#FFD700", "#FFA500"]
                        }
                    }
                }
                
            # Extract title
            title_match = re.search(r'### Title: (.*?)\n', content)
            if title_match:
                self.root.title(f"Vennkoii - {title_match.group(1)}")
                
        except Exception as e:
            self.status_label.config(text=f"Error loading parameters: {str(e)}")
            self.params = {}
    
    def create_svg_with_parameters(self, step):
        """Create SVG with current parameters."""
        try:
            # Calculate positions for Venn diagram style overlap
            center_x = 400
            center_y = 300
            radius = 120
            offset = 80  # Increased overlap between circles
            
            # Create base SVG with multiple circles
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
    <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#111111;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="4.5" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="brightness">
            <feComponentTransfer>
                <feFuncR type="linear" slope="2.5"/>
                <feFuncG type="linear" slope="2.5"/>
                <feFuncB type="linear" slope="2.5"/>
            </feComponentTransfer>
        </filter>
        <filter id="saturation">
            <feColorMatrix type="saturate" values="2.0"/>
        </filter>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgGradient)"/>
    
    <!-- First circle -->
    <circle cx="{center_x - offset}" cy="{center_y}" r="{radius}" 
            fill="#ff00ff"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="1.0">
        <animate attributeName="r" dur="4s" values="{radius};{radius + 40};{radius}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="8s" values="#ff00ff;#00ffff;#ff00ff" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Second circle -->
    <circle cx="{center_x + offset}" cy="{center_y}" r="{radius}"
            fill="#00ffff"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="1.0">
        <animate attributeName="r" dur="4s" values="{radius};{radius + 40};{radius}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="8s" values="#00ffff;#ff00ff;#00ffff" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Third circle -->
    <circle cx="{center_x}" cy="{center_y + offset}" r="{radius}"
            fill="#ffff00"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="1.0">
        <animate attributeName="r" dur="4s" values="{radius};{radius + 40};{radius}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="8s" values="#ffff00;#ff00ff;#ffff00" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Additional decorative circles -->
    <circle cx="{center_x}" cy="{center_y}" r="{radius * 0.5}"
            fill="#ff8800"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="0.9">
        <animate attributeName="r" dur="4s" values="{radius * 0.5};{radius * 0.8};{radius * 0.5}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="8s" values="#ff8800;#ff00ff;#ff8800" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Additional accent circle -->
    <circle cx="{center_x + offset * 0.5}" cy="{center_y - offset * 0.5}" r="{radius * 0.3}"
            fill="#00ff88"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="0.8">
        <animate attributeName="r" dur="4s" values="{radius * 0.3};{radius * 0.5};{radius * 0.3}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="8s" values="#00ff88;#ff00ff;#00ff88" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Additional accent circle 2 -->
    <circle cx="{center_x - offset * 0.5}" cy="{center_y - offset * 0.5}" r="{radius * 0.3}"
            fill="#ff0088"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="0.8">
        <animate attributeName="r" dur="4s" values="{radius * 0.3};{radius * 0.5};{radius * 0.3}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="8s" values="#ff0088;#ff00ff;#ff0088" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
</svg>'''
            
            # Log designer's output
            self.update_agent_output("designer", f"Generated frame {step + 1} with overlapping circles in Venn diagram style")
            
            # Validate the SVG before returning
            validation = SVGValidator.validate_all(svg_content)
            if not validation["is_valid"]:
                print("\nSVG Validation Errors:")
                for error in validation["errors"]:
                    print(f"- {error}")
                return None
            
            return svg_content
            
        except Exception as e:
            self.status_label.config(text=f"Error creating SVG: {str(e)}")
            return None
    
    def display_svg(self, svg_content):
        """Display SVG content on canvas."""
        try:
            # Convert SVG to PNG
            png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
            
            # Convert PNG to PhotoImage
            image = Image.open(io.BytesIO(png_data))
            photo = ImageTk.PhotoImage(image)
            
            # Clear previous content
            self.canvas.delete("all")
            
            # Update canvas
            self.canvas.create_image(400, 300, image=photo)
            self.canvas.image = photo  # Keep reference
            
        except Exception as e:
            self.status_label.config(text=f"Error displaying SVG: {str(e)}")
    
    def run_tests(self):
        """Run tests and display results."""
        try:
            # Check for parameter updates
            self.load_parameters()
            
            # Generate 9 frames
            frames = []
            for step in range(9):
                svg_content = self.create_svg_with_parameters(step)
                if svg_content:
                    frames.append(svg_content)
            
            if frames:
                # Get Critic's analysis of all frames
                analysis = self.critic.analyze_animation(frames)
                
                # Display the last frame
                self.display_svg(frames[-1])
                self.status_label.config(text=f"Generated 9 frames - Score: {analysis['score']:.2f}")
                
                # Log critic's output with visual metrics
                critic_output = f"Analyzed 9 frames:\n"
                critic_output += f"Overall Score: {analysis['score']:.2f}\n\n"
                
                # Add visual metrics
                if "visual_metrics" in analysis:
                    metrics = analysis["visual_metrics"]
                    critic_output += "Visual Metrics:\n"
                    critic_output += f"- Brightness: {metrics.get('brightness', 0):.2f}\n"
                    critic_output += f"- Contrast: {metrics.get('contrast', 0):.2f}\n"
                    critic_output += f"- Saturation: {metrics.get('saturation', 0):.2f}\n"
                    critic_output += f"- Color Variety: {metrics.get('color_variety', 0):.2f}\n"
                    critic_output += f"- Distribution: {metrics.get('distribution_score', 0):.2f}\n\n"
                
                # Add feedback
                if analysis['feedback']:
                    critic_output += "Feedback:\n"
                    for feedback in analysis['feedback']:
                        critic_output += f"- {feedback}\n"
                
                # Add suggestions
                if analysis['suggestions']:
                    critic_output += "\nSuggestions:\n"
                    for suggestion in analysis['suggestions']:
                        critic_output += f"- {suggestion}\n"
                
                self.update_agent_output("critic", critic_output)
                
                # Print detailed analysis to console
                print("\n=== Detailed Analysis ===")
                print("9 Frames Analysis:")
                print(f"Overall Score: {analysis['score']:.2f}")
                print("\nVisual Metrics:")
                for metric, value in analysis.get('visual_metrics', {}).items():
                    print(f"- {metric}: {value:.2f}")
                print("\nFeedback:")
                for feedback in analysis['feedback']:
                    print(f"- {feedback}")
                print("\nSuggestions:")
                for suggestion in analysis['suggestions']:
                    print(f"- {suggestion}")
                print("======================\n")
                
                # Don't schedule next update - just one cycle
                self.root.after(5000, self.root.quit)  # Quit after 5 seconds
            else:
                self.status_label.config(text="Failed to generate frames")
                self.root.after(5000, self.root.quit)  # Quit after 5 seconds
            
        except Exception as e:
            self.status_label.config(text=f"Test Error: {str(e)}")
            self.root.after(5000, self.root.quit)  # Quit after 5 seconds
    
    def run(self):
        """Start the test display."""
        self.root.mainloop()

class ContinuousTestRunner:
    def __init__(self):
        self.director = DirectorAgent()
        self.memory = AgentMemory()
        self.iteration = 0
        self.max_iterations = 10
        self.output_dir = "output"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def run_iteration(self):
        """Run one iteration of the test."""
        try:
            # Generate SVG
            svg_content = self.create_svg_with_parameters(self.iteration)
            if not svg_content:
                return False
                
            # Save SVG
            svg_path = os.path.join(self.output_dir, f"frame_{self.iteration}.svg")
            with open(svg_path, "w") as f:
                f.write(svg_content)
                
            # Analyze SVG
            analysis = self.analyze_svg(svg_content)
            
            # Let director coordinate the iteration
            result = self.director.coordinate_iteration(
                designer_output={"svg_content": svg_content},
                critic_analysis=analysis
            )
            
            # Save state
            self.director.save_state(os.path.join(self.output_dir, "director_state.json"))
            
            # Print progress
            print(f"\nIteration {self.iteration + 1} complete:")
            print(f"Score: {result['score']:.2f}")
            print("\nPriority Improvements:")
            for imp in result["instructions"]["designer"]["priority_improvements"]:
                print(f"- {imp}")
            print("\nSecondary Improvements:")
            for imp in result["instructions"]["designer"]["secondary_improvements"]:
                print(f"- {imp}")
                
            self.iteration += 1
            return result["should_continue"]
            
        except Exception as e:
            print(f"Error in iteration {self.iteration}: {str(e)}")
            return False
            
    def run(self):
        """Run continuous test iterations."""
        print("Starting continuous test runner...")
        
        while self.iteration < self.max_iterations:
            should_continue = self.run_iteration()
            if not should_continue:
                print("\nStopping iterations - convergence reached or maximum iterations hit")
                break
                
        print("\nTest run complete!")
        print(f"Total iterations: {self.iteration}")
        
        # Print final statistics
        history = self.director.get_iteration_history()
        if history:
            final_score = history[-1]["score"]
            print(f"Final score: {final_score:.2f}")
            
            if len(history) > 1:
                initial_score = history[0]["score"]
                improvement = final_score - initial_score
                print(f"Total improvement: {improvement:.2f}")
                
    def analyze_svg(self, svg_content):
        """Analyze SVG and return metrics."""
        # Add your existing SVG analysis code here
        return {
            "score": 0.8,  # Example score
            "visual_metrics": {
                "brightness": 0.7,
                "contrast": 0.8,
                "color_variety": 0.9
            },
            "feedback": [
                "Good use of color transitions",
                "Consider improving animation timing"
            ],
            "suggestions": [
                "Increase brightness in darker regions",
                "Add more variety to animation durations"
            ]
        }
        
if __name__ == "__main__":
    runner = ContinuousTestRunner()
    runner.run() 