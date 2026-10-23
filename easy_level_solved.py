from easy_level_save import show_winner, config
import time, random, sys, os, pygame, pickle


with open("winner.pkl", "rb") as f:
    genome = pickle.load(f)
    while True:
        show_winner([(1, genome)], config)