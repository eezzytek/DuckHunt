import pygame
import math
import random
import time
import os
import argparse
from enum import Enum

# Parser
parser = argparse.ArgumentParser(description='Duck Hunt')
parser.add_argument('--speed', type=float, default=1.0, help="Game speed factor (0.5 - faster, 1 - default, 2 - slower)")
args = parser.parse_args()

# Constants
FPS = 60
WIDTH, HEIGHT = 1366, 768
GAME_TIME = 60
RESULTS_FILE = 'scores.txt'
COLORS = ['#F6FEAA', '#C7DFC5', '#C1DBE3']
SPEED_MULTIPLIER = args.speed

# File paths
ASSETS_PATH = 'assets/'
FONT_PATH = os.path.join(ASSETS_PATH, 'font/Anton-Regular.ttf')
BG_PATH = os.path.join(ASSETS_PATH, 'bgs/')
BANNER_PATH = os.path.join(ASSETS_PATH, 'banners/')
GUN_PATH = os.path.join(ASSETS_PATH, 'guns/')
TARGET_PATH = os.path.join(ASSETS_PATH, 'targets/')
MENU_PATH = os.path.join(ASSETS_PATH, 'menus/')
MUSIC_PATH = os.path.join(ASSETS_PATH, 'music/')

# Game states
class GameState(Enum):
    ENTRY = 1
    LEVEL_CHOOSE = 2
    PAUSE = 3
    SCOREBOARD = 4
    GAME_OVER = 5
    SHOW_GAME = 6

class Game:
    def __init__(self):
        self.state = GameState.ENTRY

        # Game elements
        self.font = pygame.font.Font(FONT_PATH, 128)
        self.subfont = pygame.font.Font(FONT_PATH, 96)
        self.bgs = self.load_images(BG_PATH, 3)
        self.banners = self.load_images(BANNER_PATH, 3)
        self.guns = self.load_images(GUN_PATH, 3, scale=(100, 100))
        self.targets = self.load_images(TARGET_PATH, 3, scale=(100, 100))
        self.sounds = self.load_sounds()

        self.level = 1
        self.score = 0
        self.total_shots = 0
        self.target_position = []
        self.target_spawn_time = 0
        self.next_spawn_time = 0
        self.start_time = 0
        self.remaining_time = 0
        self.paused_duration = 0
        self.pause_start_time = 0
        self.best_scores = self.load_scores()

    # Loading images
    def load_images(self, path, count, scale=None):
        images = [pygame.image.load(f'{path}{i}.png') for i in range(1, count + 1)]
        if scale:
            images = [pygame.transform.scale(image, scale) for image in images]
        return images

    # Loading sounds
    def load_sounds(self):
        sounds = {
            "click": pygame.mixer.Sound(os.path.join(MUSIC_PATH, 'click.mp3')),
            "shot1": pygame.mixer.Sound(os.path.join(MUSIC_PATH, 'level1.mp3')),
            "shot2": pygame.mixer.Sound(os.path.join(MUSIC_PATH, 'level2.mp3')),
            "shot3": pygame.mixer.Sound(os.path.join(MUSIC_PATH, 'level3.mp3')),
            "gameover": pygame.mixer.Sound(os.path.join(MUSIC_PATH, 'gameover.mp3')),
        }
        for sound in sounds.values():
            sound.set_volume(0.5)
        return sounds

    # Loading scores from a file
    def load_scores(self):
        scores = {i: {"score": 0, "shots": 0} for i in range(1, 4)}
        if not os.path.exists(RESULTS_FILE):
            return scores
        try:
            with open(RESULTS_FILE, "r") as f:
                for line in f:
                    level, score, shots = map(int, line.strip().split())
                    scores[level] = {"score": score, "shots": shots}
        except Exception as e:
            print(f"Error loading scores: {e}")
        return scores

# Main game loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    timer = pygame.time.Clock()
    game = Game()

    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(MUSIC_PATH, 'bg.mp3'))
    pygame.mixer.music.set_volume(0.1)
    pygame.mixer.music.play(-1)

    while True:
        timer.tick(FPS)
        screen.fill('black')
        screen.blit(game.bgs[game.level - 1], (0, 0))
        screen.blit(game.banners[game.level - 1], (0, HEIGHT - 175))

        if game.state == GameState.ENTRY:
            game.draw_entry(screen)
        elif game.state == GameState.LEVEL_CHOOSE:
            game.draw_levels(screen)
        elif game.state == GameState.PAUSE:
            game.draw_pause(screen)
        elif game.state == GameState.SCOREBOARD:
            game.draw_scoreboard(screen)
        elif game.state == GameState.GAME_OVER:
            game.draw_gameover(screen)
        elif game.state == GameState.SHOW_GAME:
            if time.time() - game.target_spawn_time > game.next_spawn_time:
                game.spawn_targets()
            game.draw_gun(screen)
            game.draw_targets(screen)
            game.draw_score(screen)
            game.manage_game(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if game.state == GameState.SHOW_GAME and (0 < mouse_pos[0] < WIDTH) and (0 < mouse_pos[1] < HEIGHT - 175):
                    game.total_shots += 1
                if game.target_position and pygame.Rect(game.target_position[0][0], game.target_position[0][1], 100, 100).collidepoint(event.pos):
                    game.score += 1
                    game.spawn_targets()
                    if game.level == 1:
                        game.sounds["shot1"].play()
                    elif game.level == 2:
                        game.sounds["shot2"].play()
                    else:
                        game.sounds["shot3"].play()

        pygame.display.flip()

if __name__ == "__main__":
    main()
