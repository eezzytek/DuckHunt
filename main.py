import pygame
import math
import random
import time
import os
import argparse
from enum import Enum  class Game: 	 # Saving scores in a file
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

    # Drawing targets
    def draw_targets(self, screen):
        for pos in self.target_position:
            screen.blit(self.targets[self.level - 1], pos)

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
