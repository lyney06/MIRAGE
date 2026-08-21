"""
Script to run the RoguelikeRPG game with visual interface.
"""
import random
import argparse
from RoguelikeRPG.constants import GameMode
from RoguelikeRPG.game import Game
from RoguelikeRPG.visualization import create_visualization

def parse_arguments():
    """Parse command line arguments for game settings."""
    parser = argparse.ArgumentParser(description='RoguelikeRPG Game (Visual Mode)')
    
    # Add difficulty option
    parser.add_argument(
        '-d', '--difficulty',
        type=str,
        choices=['easy', 'hard'],
        default='easy',
        help='Set game difficulty (default: easy)'
    )
    
    # Add seed option
    parser.add_argument(
        '-s', '--seed',
        type=int,
        help='Set specific seed for game generation (default: random)'
    )
    
    # Add window size options
    parser.add_argument(
        '--width',
        type=int,
        default=1024,
        help='Set window width (default: 1024)'
    )
    
    parser.add_argument(
        '--height',
        type=int,
        default=768,
        help='Set window height (default: 768)'
    )
    
    # Parse arguments
    return parser.parse_args()

def main():
    """Main function to create and run a game with visualization."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Convert difficulty string to GameMode enum
    difficulty_map = {
        'easy': GameMode.EASY,
        'hard': GameMode.HARD,
    }
    game_mode = difficulty_map[args.difficulty.lower()]
    
    # Get seed (use provided seed or generate random)
    seed = args.seed if args.seed is not None else random.randint(1, 1000)
    
    print(f"Creating a new RoguelikeRPG game in {args.difficulty.capitalize()} Mode...")
    print(f"Seed: {seed}")
    
    # Create a new game with the specified parameters
    game = Game(mode=game_mode, seed=seed)
    
    # Verify that the game is solvable
    verification = game.verify_solvability()
    if verification["solvable"]:
        print("✅ Game is solvable!")
        print(f"Boss element: {verification['boss_element']}")
        print(f"Solution element: {verification['solution_element']}")
        print(f"Required weapon: {verification['advanced_weapon']}")
    else:
        print("❌ Game is NOT solvable!")
        print(f"Reason: {verification['reason']}")
        return
    
    # Create visualization
    print("Starting visualization...")
    visualization = create_visualization(game, args.width, args.height)
    
    # Run the visualization
    visualization.run()

if __name__ == "__main__":
    main()