MAX_LEN = 10


class NameInput:
    """The text the player types: max 10 chars, letters/numbers/spaces."""

    def __init__(self) -> None:
        self.text: str = ""

    def add_char(self, char: str) -> None:
        """Add one typed character, only if it is allowed."""
        if len(self.text) >= MAX_LEN:
            return
        if len(char) == 1 and char.isascii() and (char.isalnum()
                                                  or char == " "):
            self.text += char

    def backspace(self) -> None:
        """Remove the last character."""
        self.text = self.text[:-1]

    def is_valid(self) -> bool:
        """A name needs at least one letter or number."""
        return self.text.strip() != ""

    def result(self) -> str:
        """The final name, without spaces at the start and the end."""
        return self.text.strip()
