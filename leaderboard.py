import csv
import os

import pygame

LEADERBOARD_FILE = "leaderboard.csv"
MAX_ENTRIES = 10
FONT = "assets/BlockBlueprint.ttf"
SMALL = 30


def save_score(name: str, score: int) -> None:
    file_exists = os.path.isfile(LEADERBOARD_FILE)
    with open(LEADERBOARD_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["name", "score"])
        writer.writerow([name, score])


def load_scores() -> list[tuple[str, int]]:
    if not os.path.isfile(LEADERBOARD_FILE):
        return []
    scores: list[tuple[str, int]] = []
    with open(LEADERBOARD_FILE) as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) == 2:
                scores.append((row[0], int(row[1])))
    scores.sort(key=lambda e: e[1], reverse=True)
    return scores[:MAX_ENTRIES]


def draw(surface: pygame.Surface, x: int, y: int) -> None:
    font = pygame.font.Font(FONT, SMALL)
    scores = load_scores()

    title = font.render("RECORDES", True, "yellow")
    title_w, _ = title.get_size()
    surface.blit(title, (x - title_w // 2, y))

    y += 40
    for i, (name, score) in enumerate(scores[:5]):
        text = font.render(f"{i + 1}. {name}  {score:06}", True, "white")
        surface.blit(text, (x - 150, y))
        y += 40
