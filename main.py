import os
import contextlib
import sys
from arg_parser import setup_argparser


def main():
    args = setup_argparser().parse_args()

    with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
        import pygame
    from board import init_board
    from graphics import init_graphics
    from agent import SnakeAgent
    from display_training_history import display_training_history
    from training import run_training
    from evaluation import run_evaluation

    try:
        from lobby import run_lobby
    except ImportError:
        run_lobby = None

    map_width = max(3, min(24, args.map_width))
    map_height = max(3, min(13, args.map_height))

    if map_width != args.map_width or map_height != args.map_height:
        print(f"Warning: Map dimensions adjusted "
              f"to valid range: {map_width}x{map_height}")
        args.map_width = map_width
        args.map_height = map_height

    if run_lobby is not None and args.use_lobby:
        lobby_args, eval_mode = run_lobby()
        if lobby_args is None:
            return

        args = setup_argparser().parse_args(lobby_args)
        args.evaluation_mode = eval_mode

        args.map_width = max(3, min(24, args.map_width))
        args.map_height = max(3, min(13, args.map_height))

    board = init_board(args.map_height, args.map_width)
    agent = SnakeAgent(board, first_layer=args.first_layer,
                       second_layer=args.second_layer)
    agent.evaluation_mode = args.evaluation_mode

    if args.load_model:
        agent.load_model(args.load_model)

    graphics = None if args.no_graphics else init_graphics(board)

    try:
        if args.evaluation_mode:
            run_evaluation(agent, board, graphics, args)
        else:
            run_training(agent, board, graphics, args)

    finally:
        if graphics:
            pygame.quit()

        if not args.evaluation_mode and args.show_history:
            display_training_history(agent, show_plot=args.show_history)


if __name__ == "__main__":
    if '-h' in sys.argv or '--help' in sys.argv:
        setup_argparser().print_help()
    else:
        main()
