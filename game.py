import os
import random

class RockPaperScissors:
    def __init__(self):
        self.choices = ['rock', 'paper', 'scissors']
        self.score = {player1:0, player2:0}
        self.draws = 0

    def clearscreen(self):
        """Clears the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_welcome(self):
        """Display the welcome message and game rules."""
        print("🎮 Welcome to Rock, Paper, Scissors!")
        print("=" * 40)
        print("Game Rules:")
        print("• Rock beats Scissors")
        print("• Scissors beats Paper")
        print("• Paper beats Rock")
        print("• Same choice = Draw")
        print("=" * 40)
        print("\nGame Modes:")
        print("1. Player vs Player")
        print("2. Player vs CPU")
        print("3. CPU vs CPU (Simulation)")
        print("=" * 40)