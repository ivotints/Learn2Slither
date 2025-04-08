import argparse


def setup_argparser():
    parser = argparse.ArgumentParser(
        description="Snake game with Reinforcement Learning")
    parser.add_argument('--no_graphics', '-ng', action='store_true',
                        help='Turn off graphics')
    parser.add_argument('--evaluation_mode', '-e', action='store_true',
                        help='Run in evaluation mode (no training)')
    parser.add_argument('--load_model', '-lm', type=str,
                        help='Path to model to load')
    parser.add_argument('--name', '-n', type=str, default='model',
                        help='Name of model folder')
    parser.add_argument('--first_layer', '-fl', type=int, default=32,
                        help='Number of neurons in the first layer')
    parser.add_argument('--second_layer', '-sl', type=int, default=16,
                        help='Number of neurons in the second layer')
    parser.add_argument('--episodes', '-ep', type=int, default=10000,
                        help='Number of training episodes')
    parser.add_argument('--show_vision', '-sv', action='store_true',
                        help='Show agent vision in terminal')
    parser.add_argument('--use_lobby', '-ul', action='store_true',
                        help='Show configuration lobby')
    parser.add_argument('--map_width', '-mw', type=int, default=10,
                        help='Width of the map (3-24)')
    parser.add_argument('--map_height', '-mh', type=int, default=10,
                        help='Height of the map (3-13)')
    parser.add_argument('--show_history', '-sh', action='store_true',
                        help='Show training history plot after training')
    return parser
