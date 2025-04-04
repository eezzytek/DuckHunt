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

