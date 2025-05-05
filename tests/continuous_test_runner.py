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
import logging

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.agents.designer import DesignerAgent
from src.agents.critic import CriticAgent
from src.utils.svg_validator import SVGValidator
from src.utils.feedback_parser import FeedbackParser
from src.agents.director import DirectorAgent
from src.utils.agent_memory import AgentMemory
from src.config.agent_config import DEFAULT_DIRECTOR_CONFIG

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
        
        # Initialize agents with config if available
        if hasattr(self, 'config'):
            self.director = DirectorAgent(self.config)
        else:
            self.director = DirectorAgent(DEFAULT_DIRECTOR_CONFIG)
            
        self.designer = DesignerAgent()
        self.critic = CriticAgent()
        
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
            # Get performance history to adjust parameters
            history = self.director.get_iteration_history()
            last_metrics = {}
            if history:
                last_feedback = self.memory.get_feedback_history("designer")
                if last_feedback:
                    last_metrics = last_feedback[-1].get("metrics", {})
            
            # Adjust parameters based on feedback
            center_x = 400
            center_y = 300
            radius = 120 + (step * 5)  # Gradually increase size
            offset = 80 - (step * 2)  # Gradually increase overlap
            
            # Adjust visual parameters based on metrics
            brightness = 2.5
            saturation = 2.0
            glow = 4.5
            
            if last_metrics:
                if last_metrics.get("brightness", 0.7) < 0.6:
                    brightness += 0.5
                if last_metrics.get("color_variety", 0.9) < 0.6:
                    saturation += 0.5
                if last_metrics.get("contrast", 0.8) < 0.6:
                    glow += 1.0
            
            # Create base SVG with adjusted parameters
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">
    <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#111111;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#333333;stop-opacity:1" />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="{glow}" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
        <filter id="brightness">
            <feComponentTransfer>
                <feFuncR type="linear" slope="{brightness}"/>
                <feFuncG type="linear" slope="{brightness}"/>
                <feFuncB type="linear" slope="{brightness}"/>
            </feComponentTransfer>
        </filter>
        <filter id="saturation">
            <feColorMatrix type="saturate" values="{saturation}"/>
        </filter>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgGradient)"/>
    
    <!-- First circle -->
    <circle cx="{center_x - offset}" cy="{center_y}" r="{radius}" 
            fill="#ff00ff"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="1.0">
        <animate attributeName="r" dur="{4 - step * 0.2}s" values="{radius};{radius + 40};{radius}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="{8 - step * 0.4}s" values="#ff00ff;#00ffff;#ff00ff" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Second circle -->
    <circle cx="{center_x + offset}" cy="{center_y}" r="{radius}"
            fill="#00ffff"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="1.0">
        <animate attributeName="r" dur="{4 - step * 0.2}s" values="{radius};{radius + 40};{radius}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="{8 - step * 0.4}s" values="#00ffff;#ff00ff;#00ffff" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Third circle -->
    <circle cx="{center_x}" cy="{center_y + offset}" r="{radius}"
            fill="#ffff00"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="1.0">
        <animate attributeName="r" dur="{4 - step * 0.2}s" values="{radius};{radius + 40};{radius}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="{8 - step * 0.4}s" values="#ffff00;#ff00ff;#ffff00" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
    
    <!-- Additional decorative circles -->
    <circle cx="{center_x}" cy="{center_y}" r="{radius * 0.5}"
            fill="#ff8800"
            filter="url(#glow) url(#brightness) url(#saturation)" opacity="0.9">
        <animate attributeName="r" dur="{4 - step * 0.2}s" values="{radius * 0.5};{radius * 0.8};{radius * 0.5}" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
        <animate attributeName="fill" dur="{8 - step * 0.4}s" values="#ff8800;#ff00ff;#ff8800" repeatCount="indefinite" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1;0.4 0 0.2 1"/>
    </circle>
</svg>'''
            
            # Log designer's output
            self.logger.info(f"Generated frame {step + 1} with parameters: brightness={brightness}, saturation={saturation}, glow={glow}")
            
            # Validate the SVG before returning
            validation = SVGValidator.validate_all(svg_content)
            if not validation["is_valid"]:
                self.logger.error("SVG Validation Errors:")
                for error in validation["errors"]:
                    self.logger.error(f"- {error}")
                return None
            
            return svg_content
            
        except Exception as e:
            self.logger.error(f"Error creating SVG: {e}")
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

class ContinuousTestRunner(TestDisplay):
    def __init__(self):
        # Initialize configuration first
        self.config = DEFAULT_DIRECTOR_CONFIG
        
        # Initialize logging
        self.setup_logging()
        
        # Initialize parent class with config
        super().__init__()
        
        # Initialize agents and memory
        self.director = DirectorAgent(self.config)
        self.designer = DesignerAgent()
        self.critic = CriticAgent()
        self.memory = AgentMemory()
        self.iteration = 0
        self.max_iterations = self.config["max_iterations"]
        self.output_dir = "output"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load previous state if available
        self.load_previous_state()
        
    def setup_logging(self):
        """Setup logging configuration."""
        log_config = DEFAULT_DIRECTOR_CONFIG["logging"]
        if log_config["enabled"]:
            os.makedirs(os.path.dirname(log_config["file"]), exist_ok=True)
            logging.basicConfig(
                level=log_config["level"],
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler(log_config["file"]),
                    logging.StreamHandler()
                ]
            )
        self.logger = logging.getLogger(__name__)
        
    def load_previous_state(self):
        """Load previous state if available."""
        try:
            memory_path = self.config["memory_path"]
            if os.path.exists(memory_path):
                self.logger.info("Loading previous state...")
                self.director.load_state(memory_path)
                self.iteration = len(self.director.get_iteration_history())
                self.logger.info(f"Loaded previous state. Starting from iteration {self.iteration}")
        except Exception as e:
            self.logger.error(f"Error loading previous state: {e}")
            
    def backup_state(self):
        """Backup current state."""
        try:
            if self.iteration % self.config["auto_recovery"]["backup_interval"] == 0:
                backup_path = os.path.join(self.output_dir, f"backup_state_{self.iteration}.json")
                self.director.save_state(backup_path)
                self.logger.info(f"State backed up to {backup_path}")
        except Exception as e:
            self.logger.error(f"Error backing up state: {e}")
            
    def run_iteration(self):
        """Run one iteration of the test with error handling and recovery."""
        try:
            self.logger.info(f"Starting iteration {self.iteration + 1}")
            
            # Generate SVG
            svg_content = self.create_svg_with_parameters(self.iteration)
            if not svg_content:
                self.logger.error("Failed to generate SVG content")
                return self.handle_error("svg_generation")
                
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
            self.director.save_state(self.config["memory_path"])
            self.backup_state()
            
            # Log progress
            self.logger.info(f"Iteration {self.iteration + 1} complete - Score: {result['score']:.2f}")
            self.logger.info("Priority Improvements:")
            for imp in result["instructions"]["designer"]["priority_improvements"]:
                self.logger.info(f"- {imp}")
                
            self.iteration += 1
            return result["should_continue"]
            
        except Exception as e:
            self.logger.error(f"Error in iteration {self.iteration}: {e}")
            return self.handle_error("iteration")
            
    def handle_error(self, error_type: str) -> bool:
        """Handle errors with retry logic."""
        if not self.config["auto_recovery"]["enabled"]:
            return False
            
        retries = self.config["auto_recovery"]["max_retries"]
        delay = self.config["auto_recovery"]["retry_delay"]
        
        while retries > 0:
            self.logger.warning(f"Attempting recovery for {error_type} error. Retries left: {retries}")
            time.sleep(delay)
            
            try:
                if error_type == "svg_generation":
                    svg_content = self.create_svg_with_parameters(self.iteration)
                    if svg_content:
                        self.logger.info("Recovery successful")
                        return True
                elif error_type == "iteration":
                    # Try to restore from last backup
                    backup_files = sorted([f for f in os.listdir(self.output_dir) if f.startswith("backup_state_")])
                    if backup_files:
                        latest_backup = backup_files[-1]
                        self.director.load_state(os.path.join(self.output_dir, latest_backup))
                        self.logger.info(f"Restored from backup: {latest_backup}")
                        return True
            except Exception as e:
                self.logger.error(f"Recovery attempt failed: {e}")
                
            retries -= 1
            
        self.logger.error(f"Recovery failed after {self.config['auto_recovery']['max_retries']} attempts")
        return False
        
    def run(self):
        """Run continuous test iterations with monitoring."""
        self.logger.info("Starting continuous test runner...")
        
        try:
            while self.iteration < self.max_iterations:
                should_continue = self.run_iteration()
                if not should_continue:
                    self.logger.info("Stopping iterations - convergence reached or maximum iterations hit")
                    break
                    
            self.logger.info("Test run complete!")
            self.logger.info(f"Total iterations: {self.iteration}")
            
            # Print final statistics
            history = self.director.get_iteration_history()
            if history:
                final_score = history[-1]["score"]
                self.logger.info(f"Final score: {final_score:.2f}")
                
                if len(history) > 1:
                    initial_score = history[0]["score"]
                    improvement = final_score - initial_score
                    self.logger.info(f"Total improvement: {improvement:.2f}")
                    
        except KeyboardInterrupt:
            self.logger.info("Test run interrupted by user")
            self.director.save_state(self.config["memory_path"])
            self.logger.info("State saved successfully")
            
        except Exception as e:
            self.logger.error(f"Unexpected error in test run: {e}")
            self.director.save_state(self.config["memory_path"])
            self.logger.error("State saved despite error")
            
    def analyze_svg(self, svg_content):
        """Analyze SVG and return metrics."""
        try:
            # Extract metrics from SVG content using more robust regex patterns
            brightness_match = re.search(r'<feFuncR type="linear" slope="([^"]+)"', svg_content)
            brightness_value = float(brightness_match.group(1)) if brightness_match else 2.5
            
            saturation_match = re.search(r'<feColorMatrix type="saturate" values="([^"]+)"', svg_content)
            saturation_value = float(saturation_match.group(1)) if saturation_match else 2.0
            
            glow_match = re.search(r'<feGaussianBlur stdDeviation="([^"]+)"', svg_content)
            glow_value = float(glow_match.group(1)) if glow_match else 4.5
            
            # Calculate normalized scores
            brightness_score = min(brightness_value / 4.0, 1.0)
            saturation_score = min(saturation_value / 3.0, 1.0)
            contrast_score = min(glow_value / 6.0, 1.0)
            
            # Calculate color variety score
            unique_colors = set(re.findall(r'#[0-9a-fA-F]{6}', svg_content))
            color_variety_score = min(len(unique_colors) / 10.0, 1.0)
            
            # Calculate animation smoothness
            animation_times = [float(t.replace('s', '')) for t in re.findall(r'dur="([^"]+)s"', svg_content)]
            if animation_times:
                animation_smoothness = 1.0 - (max(animation_times) - min(animation_times)) / max(animation_times)
            else:
                animation_smoothness = 0.5
            
            # Calculate overall score with weighted components
            weights = self.config["analysis_weights"]
            overall_score = (
                weights["brightness"] * brightness_score +
                weights["contrast"] * contrast_score +
                weights["color_variety"] * color_variety_score +
                weights["distribution"] * animation_smoothness +
                weights["animation_smoothness"] * animation_smoothness
            )
            
            # Generate feedback and suggestions
            feedback = []
            suggestions = []
            
            if brightness_score < 0.6:
                feedback.append("Brightness levels are too low")
                suggestions.append("Increase brightness values")
            if contrast_score < 0.6:
                feedback.append("Contrast could be improved")
                suggestions.append("Increase glow effect and color contrast")
            if color_variety_score < 0.6:
                feedback.append("Limited color palette")
                suggestions.append("Add more unique colors to the design")
            if animation_smoothness < 0.6:
                feedback.append("Animation timing variations are too extreme")
                suggestions.append("Make animation durations more consistent")
            
            # Log analysis results
            self.logger.info(f"Analysis results:")
            self.logger.info(f"- Brightness: {brightness_score:.2f}")
            self.logger.info(f"- Contrast: {contrast_score:.2f}")
            self.logger.info(f"- Color variety: {color_variety_score:.2f}")
            self.logger.info(f"- Animation smoothness: {animation_smoothness:.2f}")
            self.logger.info(f"- Overall score: {overall_score:.2f}")
            
            return {
                "score": overall_score,
                "visual_metrics": {
                    "brightness": brightness_score,
                    "contrast": contrast_score,
                    "color_variety": color_variety_score,
                    "animation_smoothness": animation_smoothness
                },
                "feedback": feedback,
                "suggestions": suggestions
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing SVG: {e}")
            return {
                "score": 0.5,
                "visual_metrics": {
                    "brightness": 0.5,
                    "contrast": 0.5,
                    "color_variety": 0.5,
                    "animation_smoothness": 0.5
                },
                "feedback": ["Error analyzing SVG content"],
                "suggestions": ["Check SVG generation parameters"]
            }
        
if __name__ == "__main__":
    runner = ContinuousTestRunner()
    runner.run() 