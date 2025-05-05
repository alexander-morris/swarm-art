# Vennkoii - SVG Animation Analysis System

## Overview
Vennkoii is a sophisticated system for analyzing and evaluating SVG animations. It employs a multi-agent architecture to design, analyze, and provide feedback on SVG animations, with a particular focus on timing consistency and element alignment.

## Architecture

### Core Components

#### 1. Designer Agent (`src/agents/designer.py`)
- Responsible for generating SVG animations
- Creates frames with configurable parameters:
  - Width and height
  - Circle radius
  - Animation duration
  - Number of steps
- Ensures consistent timing and positioning across frames

#### 2. Critic Agent (`src/agents/critic.py`)
- Analyzes SVG animations for quality and consistency
- Evaluates multiple aspects:
  - SVG structure validity
  - Animation timing consistency
  - Element alignment
  - Overall animation smoothness
- Provides detailed feedback and scoring

#### 3. SVG Validator (`src/utils/svg_validator.py`)
- Validates SVG structure and content
- Checks for required elements and attributes
- Ensures proper animation syntax
- Handles both namespaced and non-namespaced SVG elements

#### 4. Feedback Parser (`src/utils/feedback_parser.py`)
- Processes and formats feedback from the Critic agent
- Structures feedback for clear communication
- Handles error messages and suggestions

### Scoring System

The Critic agent employs a sophisticated scoring system that considers multiple factors:

1. **Structure Score (20% weight)**
   - SVG validity
   - Required elements presence
   - Proper attribute formatting

2. **Timing Score (40% weight)**
   - Duration consistency
   - Animation smoothness
   - Timing pattern analysis

3. **Alignment Score (40% weight)**
   - Element position consistency
   - Movement patterns
   - Position change analysis

#### Score Categories
- Perfect (1.0): Flawless animation
- Good (0.9): Minor issues
- Decent (0.85): Some inconsistencies
- Valid (≥0.6): Basic functionality
- Invalid (<0.6): Major issues

### Penalty System

The system applies penalties for various issues:

1. **Timing Penalties**
   - Inconsistent durations
   - Sudden timing changes
   - Base penalty: 30%

2. **Alignment Penalties**
   - Position inconsistencies
   - Extreme position changes
   - Base penalty: 25%

3. **Severe Issue Penalties**
   - Additional penalties for critical issues
   - Applied when scores drop below 0.5

## Usage

### Basic Usage
```python
from src.agents.designer import DesignerAgent
from src.agents.critic import CriticAgent

# Create agents
designer = DesignerAgent()
critic = CriticAgent()

# Generate animation
frames = designer.create_animation(
    width=100,
    height=100,
    circle_radius=40,
    duration=1.0,
    steps=3
)

# Analyze animation
analysis = critic.analyze_animation(frames)
```

### Analysis Results
The analysis returns a dictionary containing:
- `is_valid`: Boolean indicating animation validity
- `score`: Overall quality score (0-1)
- `errors`: List of error messages
- `feedback`: List of feedback messages

## Testing

The system includes comprehensive test suites:
- `tests/test_critic_agent.py`: Tests for the Critic agent
- `tests/test_designer_agent.py`: Tests for the Designer agent
- `tests/test_svg_validator.py`: Tests for SVG validation
- `tests/test_feedback_parser.py`: Tests for feedback parsing

Run tests using:
```bash
python3 -m pytest tests/
```

## Error Handling

The system handles various error cases:
1. Invalid SVG structure
2. Missing required elements
3. Inconsistent timing
4. Alignment issues
5. Missing or invalid attributes

Each error case provides specific feedback and appropriate score penalties.

## Performance Considerations

1. **Memory Usage**
   - Efficient SVG parsing
   - Minimal frame storage
   - Optimized analysis algorithms

2. **Processing Speed**
   - Quick validation checks
   - Efficient scoring calculations
   - Optimized feedback generation

## Future Enhancements

1. **Planned Features**
   - Support for more SVG elements
   - Additional animation types
   - Enhanced feedback system
   - Performance optimizations

2. **Potential Improvements**
   - Machine learning-based analysis
   - Real-time feedback
   - Extended animation patterns
   - Custom scoring rules

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# Vennkoii Swarm Art

A collaborative art generation system using swarm intelligence and consensus algorithms.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/alexander-morris/swarm-art.git
cd swarm-art
```

2. Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
   - Copy `.env.template` to `.env`
   - Add your OpenAI API key to `.env`
   - Adjust other settings as needed

## Environment Variables

The following environment variables are required:

- `OPENAI_API_KEY`: Your OpenAI API key
- `DEBUG`: Set to "true" for debug mode (default: false)
- `LOG_LEVEL`: Logging level (default: INFO)
- `OUTPUT_DIR`: Directory for output files (default: output)
- `BACKUP_INTERVAL`: Interval for state backups (default: 3)

## Animation Settings

The following settings can be adjusted in `.env`:

- `BASE_DURATION`: Base duration for animations (default: 2.0)
- `RADIUS_SCALE`: Scale factor for radius animations (default: 1.25)
- `BRIGHTNESS`: Brightness level (default: 2.5)
- `SATURATION`: Saturation level (default: 2.0)
- `GLOW`: Glow effect intensity (default: 4.5)

## Security

- Never commit your `.env` file
- Keep your API keys secure
- Use environment variables for sensitive data
- Check the `.gitignore` file to ensure sensitive files are excluded

## Running Tests

```bash
python tests/continuous_test_runner.py
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests to ensure everything works
4. Create a pull request

## License

MIT License - See LICENSE file for details 