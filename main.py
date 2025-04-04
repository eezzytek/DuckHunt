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
