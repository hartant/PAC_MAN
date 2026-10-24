from dataclasses import dataclass, field


@dataclass
class FakeState:
    player_pos: tuple[int, int] = (2, 2)
    ghosts: list[tuple[int, int, bool]] = field(default_factory=list)
    pacgums: set[tuple[int, int]] = field(default_factory=set)
    super_pacgums: set[tuple[int, int]] = field(default_factory=set)
    score: int = 0
    lives: int = 3
    level: int = 1
    time_left: int = 90
    status: str = "playing"


def make_fake_state(maze: list[list[int]]) -> FakeState:
    """Fake numbers. The maze is used to put dots in the corridors."""
    rows = len(maze)
    cols = len(maze[0])
    corners = {(0, 0), (cols - 1, 0), (0, rows - 1), (cols - 1, rows - 1)}

    pacgums = set()
    for row in range(rows):
        for col in range(cols):
            closed = maze[row][col] == 15       # the "42" cells
            if not closed and (col, row) not in corners:
                pacgums.add((col, row))

    return FakeState(
        player_pos=(0, 0),
        ghosts=[(0, 0, False), (cols - 1, 0, False),
                (0, rows - 1, True), (cols - 1, rows - 1, False)],
        pacgums=pacgums,
        super_pacgums=corners,
        score=1250,
        lives=3,
        level=1,
        time_left=90,
        status="playing",
    )
