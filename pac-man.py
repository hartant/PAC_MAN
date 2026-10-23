import sys
import logging
import pygame as pg


from src.ui.config import load_config  # Or wherever your config loader is
from src.ui.menu import MenuScreen



def main() -> None:
    # 1. Check command-line arguments (must take exactly one config file)[cite: 9]
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json")
        sys.exit(1)

    config_path = sys.argv[1]

    # 2. Load configuration safely (handles comments and errors)[cite: 9, 10]
    config = load_config(config_path)

    # 3. Initialize Pygame and set up the window
    pg.init()
    screen_width = 800
    screen_height = 600
    screen = pg.display.set_mode((screen_width, screen_height))
    pg.display.set_caption("Pac-Man")

    # Mock highscores list for now (until integrated with teammate's backend)
    # Format: list of (name, score)
    dummy_highscores = [
        ("Sannaka", 1110),
        ("foliole", 20),
        ("Marmelade", 20),
        ("goldfish", 20)
    ]

    # 4. Run the Menu Screen loop
    menu_screen = MenuScreen(screen, dummy_highscores)
    action = menu_screen.run()

    # 5. Handle transitions from the menu
    if action == "playing":
        print("Transitioning to gameplay view (to be built with teammate)...")
        # TODO: Launch game loop here
    elif action == "quit":
        print("Exiting Pac-Man.")

    pg.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
