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


def make_fake_state() -> FakeState:
    return FakeState(
        player_pos=(2, 2),
        ghosts=[(0, 0, False), (14, 0, False),
                (0, 14, True), (14, 14, False)],
        pacgums={(1, 1), (2, 1), (3, 1), (4, 1)},
        super_pacgums={(0, 0), (14, 0), (0, 14), (14, 14)},
        score=1250,
        lives=3,
        level=1,
        time_left=90,
        status="playing",
    )
