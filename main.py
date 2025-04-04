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

# Game
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

        # Game parameters
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

    # Saving scores in a file
    def save_scores(self):
        with open(RESULTS_FILE, "w") as f:
            for level, data in self.best_scores.items():
                f.write(f"{level} {data['score']} {data['shots']}\n")

    # Updating the best score if necessary
    def update_best_score(self):
        if (self.score > self.best_scores[self.level]["score"] or
            (self.score == self.best_scores[self.level]["score"] and
             self.total_shots < self.best_scores[self.level]["shots"])):
            self.best_scores[self.level] = {"score": self.score, "shots": self.total_shots}
            self.save_scores()

    # Spawning targets in random positions
    def spawn_targets(self):
        spawn_intervals = [1.5, 1.0, 0.5]
        self.target_position = [(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 300))]
        self.target_spawn_time = time.time()
        self.next_spawn_time = spawn_intervals[self.level - 1] * SPEED_MULTIPLIER

    # Drawing a gun and animating its movement
    def draw_gun(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        gun_location = (WIDTH / 2, HEIGHT - 175)
        clicks = pygame.mouse.get_pressed()
        slope = (mouse_pos[1] - gun_location[1]) / (mouse_pos[0] - gun_location[0]) if mouse_pos[0] != gun_location[0] else -100000
        angle = math.degrees(math.atan(slope))
        gun = pygame.transform.flip(self.guns[self.level - 1], mouse_pos[0] < WIDTH / 2, False)
        rotated_gun = pygame.transform.rotate(gun, 90 - angle if mouse_pos[0] < WIDTH / 2 else 270 - angle)
        screen.blit(rotated_gun, (WIDTH / 2 - 90 if mouse_pos[0] < WIDTH / 2 else WIDTH / 2 - 30, HEIGHT - 225))
        if clicks[0]:
            pygame.draw.circle(screen, COLORS[self.level - 1], mouse_pos, 5)

    # Drawing targets
    def draw_targets(self, screen):
        for pos in self.target_position:
            screen.blit(self.targets[self.level - 1], pos)

    # Drawing score
    def draw_score(self, screen):
        score_text = self.font.render(f'{self.score}', True, COLORS[self.level - 1])
        screen.blit(score_text, (402, 600))

    # Drawing timer
    def draw_timer(self, screen):
        remaining_time = max(0, GAME_TIME - int(time.time() - self.start_time - self.paused_duration))
        timer_text = self.font.render(f'{remaining_time}', True, COLORS[self.level - 1])
        screen.blit(timer_text, (938, 600))
        return remaining_time

    # Game behavior - ending, pausing, restarting
    def manage_game(self, screen):
        remaining_time = self.draw_timer(screen)

        if remaining_time == 0:
            self.state = GameState.GAME_OVER
            self.sounds["gameover"].play()

        if pygame.Rect((1115, 651), (100, 100)).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.score = 0
            self.start_time = time.time()
            self.paused_duration = 0
            self.sounds["click"].play()

        if pygame.Rect((1241, 651), (100, 100)).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.state = GameState.PAUSE
            self.pause_start_time = time.time()
            self.sounds["click"].play()

    # Drawing entry screen
    def draw_entry(self, screen):
        screen.blit(pygame.image.load(os.path.join(MENU_PATH, 'entry.png')), (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()
        if pygame.Rect((974, 537), (317, 113)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.LEVEL_CHOOSE
            self.sounds["click"].play()
        if pygame.Rect((974, 660), (317, 40)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.SCOREBOARD
            self.sounds["click"].play()

    # Drawing pause screen
    def draw_pause(self, screen):
        screen.blit(pygame.image.load(os.path.join(MENU_PATH, 'pause.png')), (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()
        if pygame.Rect((524, 442), (317, 113)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.SHOW_GAME
            self.paused_duration += time.time() - self.pause_start_time
            self.sounds["click"].play()
        if pygame.Rect((524, 580), (317, 113)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.LEVEL_CHOOSE
            self.sounds["click"].play()

    # Drawing levels with an option to choose one
    def draw_levels(self, screen):
        level_pics = [os.path.join(MENU_PATH, f'level{i}.png') for i in range(1, 4)]
        screen.blit(pygame.image.load(level_pics[self.level - 1]), (0, 0))
        mouse_pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()
        if pygame.Rect((1241, 334), (50, 100)).collidepoint(mouse_pos) and clicks[0]:
            self.level = 1 if self.level == 3 else self.level + 1
            self.sounds["click"].play()
        if pygame.Rect((75, 334), (50, 100)).collidepoint(mouse_pos) and clicks[0]:
            self.level = 3 if self.level == 1 else self.level - 1
            self.sounds["click"].play()
        if pygame.Rect((1124, 25), (150, 100)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.SHOW_GAME
            self.total_shots = 0
            self.score = 0
            self.start_time = time.time()
            self.paused_duration = 0
            self.sounds["click"].play()
        if pygame.Rect((93, 48), (199, 54)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.ENTRY
            self.sounds["click"].play()

    # Drawing gameover screen
    def draw_gameover(self, screen):
        self.update_best_score()
        screen.blit(pygame.image.load(os.path.join(MENU_PATH, 'gameover.png')), (0, 0))
        score_text = self.font.render(f'{self.score}', True, '#C4C4C4')
        shot_text = self.font.render(f'{self.total_shots}', True, '#C4C4C4')
        screen.blit(score_text, (548, 220))
        screen.blit(shot_text, (924, 220))
        mouse_pos = pygame.mouse.get_pos()
        clicks = pygame.mouse.get_pressed()
        if pygame.Rect((524, 467), (317, 113)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.SHOW_GAME
            self.score = 0
            self.total_shots = 0
            self.start_time = time.time()
            self.sounds["click"].play()
        if pygame.Rect((524, 605), (317, 113)).collidepoint(mouse_pos) and clicks[0]:
            self.state = GameState.LEVEL_CHOOSE
            self.sounds["click"].play()

    # Drawing the scoreboard
    def draw_scoreboard(self, screen):
        screen.blit(pygame.image.load(os.path.join(MENU_PATH, 'scoreboard.png')), (0, 0))
        for i in range(1, 4):
            score_text = self.subfont.render(f'LEVEL {i}: SCORE: {self.best_scores[i]["score"]}, SHOTS: {self.best_scores[i]["shots"]}', True, COLORS[i - 1])
            screen.blit(score_text, (50, 158 + (i - 1) * 145))
        if pygame.Rect((50, 40), (199, 54)).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
            self.state = GameState.ENTRY
            self.sounds["click"].play()

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