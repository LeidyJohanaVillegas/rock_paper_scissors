import os
import random

class RockPaperScissors:
    def __init__(self):
        self.choices = ['rock', 'paper', 'scissors']
        self.score_player1 = 0
        self.score_player2 = 0
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
    
    def get_player_choice(self, player_name):
        """Get choice from a human player"""
        while True:
            print(f"\n{player_name}, choose your weapon:")
            print("1. Rock 🪨")
            print("2. Paper 📄")
            print("3. Scissors ✂️")
            
            choice = input("Enter 1, 2, or 3: ").strip()
            
            if choice in ['1', '2', '3']:
                return self.choices[int(choice) - 1]
            else:
                print("❌ Invalid choice! Please enter 1, 2, or 3.")

    def get_cpu_choice(self):
        """Generate random choice for CPU"""
        return random.choice(self.choices)
    
    def determine_winner(self, choice1, choice2, player1_name, player2_name):
        """Determine the winner of a round"""
        print(f"\n{player1_name} chose: {choice1.upper()}")
        print(f"{player2_name} chose: {choice2.upper()}")
        
        if choice1 == choice2:
            print("🤝 It's a DRAW!")
            self.draws += 1
            return "draw"
        
        # Winning conditions
        winning_combinations = {
            ('rock', 'scissors'): player1_name,
            ('scissors', 'paper'): player1_name,
            ('paper', 'rock'): player1_name,
            ('scissors', 'rock'): player2_name,
            ('paper', 'scissors'): player2_name,
            ('rock', 'paper'): player2_name
        }

        winner = winning_combinations.get((choice1, choice2))

        if winner == player1_name:
            print(f"🏆 {player1_name} WINS this round!")
            self.score_player1 += 1
        else:
            print(f"🏆 {player2_name} WINS this round!")
            self.score_player2 += 1
        
        return winner
    
    def display_scores(self, player1_name, player2_name):
        """Display current score"""
        print("\n" + "=" * 30)
        print("📊 CURRENT SCORE:")
        print(f"{player1_name}: {self.score_player1}")
        print(f"{player2_name}: {self.score_player2}")
        print(f"Draws: {self.draws}")
        print("=" * 30)