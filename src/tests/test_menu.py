from src.ui.menu import MainMenu

def test_main_menu_navigation():
    menu = MainMenu()
    # Initial selection should be 0 ("Start Game")
    assert menu.selected == 0
    assert menu.items[menu.selected].target == "playing"

    # Pressing down should move selection to 1 ("View Highscores")
    next_action = menu.handle_key("down")
    assert menu.selected == 1
    assert menu.items[menu.selected].target == "highscores"
    assert next_action == "menu"

    # Pressing enter on "View Highscores" should return its target
    action = menu.handle_key("enter")
    assert action == "highscores"