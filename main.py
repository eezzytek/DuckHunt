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

