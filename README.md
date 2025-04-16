# Learn2Slither

A reinforcement learning project where a snake learns to navigate and survive in a dynamic environment through Q-learning.

![Learn2Slither Demo](animation.gif)

## Project Overview

Learn2Slither implements a classic snake game controlled by an AI agent that learns optimal strategies through reinforcement learning. Using a neural network built with Keras/TensorFlow, the snake progressively improves its performance through multiple training sessions.

## Features

### Game Environment
- **Flexible Board Size**: Default 10x10 grid, configurable to any size (width 3-24, height 3-13)
- **Dynamic Elements**: Green apples (increase length), red apples (decrease length)
- **Snake**: Starts with length of 3, randomly positioned

### AI Implementation
- **Learning Framework**: Q-learning with neural networks (Keras/TensorFlow)
- **State Representation**:  
  The snake's "vision" is encoded as 12 neurons (3 features × 4 directions: UP, DOWN, LEFT, RIGHT):  
  - 0/1: Is it an obstacle?
  - 0/1: Is it green food?
  - 0-1: Normalized distance to that object
- **Action Space**: 4 possible movements
- **Reward System**: Simple yet effective (+1 for eating apple, -5 for death)

### Performance
- **Average Length**: 28 cells
- **Maximum Length**: 50 cells
- **Multiple Trained Models**: Various training configurations available

### Technical Features
- **Model Management**: Save and load trained models
- **Visualization**: Graphical interface with adjustable speed
- **Step-by-Step Mode**: For detailed analysis of agent decisions
- **Training Configuration**: Command line parameters for sessions, learning mode, map size, etc.

## Installation

```bash
git clone https://github.com/ivotints/Learn2Slither.git
cd Learn2Slither
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running the Snake

```bash
# Start with default settings
python3 start.py

# Start with a pre-trained model
python3 start.py --load_model models/Gorynych_v1.5_4/snake_model_190_20250410_15:20.keras

# Train a new model with 10000 episodes
python3 start.py --episodes 10000 --name my_model

# Run without graphics
python3 start.py --no_graphics

# Run in evaluation (no training) mode
python3 start.py --evaluation_mode --load_model models/Gorynych_v1.5_4/snake_model_190_20250410_15:20.keras

# Show agent vision in terminal
python3 start.py --show_vision

# Use a custom map size (e.g. 20x13)
python3 start.py --map_width 20 --map_height 13

# Use graphical lobby
python3 start.py -ul
```

## Command Line Arguments

| Argument                | Short | Type    | Default   | Description                                                         |
|-------------------------|-------|---------|-----------|---------------------------------------------------------------------|
| --no_graphics           | -ng   | flag    | False     | Turn off graphics                                                   |
| --evaluation_mode       | -e    | flag    | False     | Run in evaluation mode (no training)                                |
| --load_model            | -lm   | str     | None      | Path to model to load                                               |
| --name                  | -n    | str     | model     | Name of model folder                                                |
| --first_layer           | -fl   | int     | 32        | Number of neurons in the first layer                                |
| --second_layer          | -sl   | int     | 16        | Number of neurons in the second layer                               |
| --episodes              | -ep   | int     | 10000     | Number of training episodes                                         |
| --show_vision           | -sv   | flag    | False     | Show agent vision in terminal                                       |
| --use_lobby             | -ul   | flag    | False     | Show configuration lobby                                            |
| --map_width             | -mw   | int     | 10        | Width of the map (3-24)                                             |
| --map_height            | -mh   | int     | 10        | Height of the map (3-13)                                            |
| --show_history          | -sh   | flag    | False     | Show training history plot after training                           |

## Training Process

The agent learns through trial and error, with the neural network adjusting its weights based on the rewards received. The learning process involves:

1. **Exploration**: Initially taking random actions to discover the environment
2. **Exploitation**: Gradually favoring actions that lead to higher rewards
3. **Iterative Learning**: Refining decision-making over thousands of game sessions

## Results

After extensive training, the snake AI demonstrates impressive capabilities:
- Efficiently navigates to food sources
- Avoids walls and self-collisions
- Achieves an average length of 28 cells
- Maximum recorded length of 50 cells
