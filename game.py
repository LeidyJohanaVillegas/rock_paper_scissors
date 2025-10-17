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

    def player_vs_player(self):
        """Mode: Player 1 vs Player 2"""
        player1_name = input("\nEnter Player 1 name: ").strip() or "Player 1"
        player2_name = input("Enter Player 2 name: ").strip() or "Player 2"
        
        self.play_game_loop(player1_name, player2_name, "human", "human")

    def player_vs_cpu(self):
        """Mode: Player vs CPU"""
        player_name = input("\nEnter your name: ").strip() or "Player"
        cpu_name = "CPU"
        
        self.play_game_loop(player_name, cpu_name, "human", "cpu")
    
    def cpu_vs_cpu(self):
        """Mode: CPU vs CPU (simulation)"""
        cpu1_name = "CPU 1"
        cpu2_name = "CPU 2"
        
        print(f"\n🤖 {cpu1_name} vs {cpu2_name} - Simulation Mode")
        print("Watching AI battle...")
        
        self.play_game_loop(cpu1_name, cpu2_name, "cpu", "cpu")

    def play_game_loop(self, player1_name, player2_name, type1, type2):
        """Main game loop for any mode"""
        rounds = 0
        max_rounds = 5  # You can change this
        
        while rounds < max_rounds:
            rounds += 1
            print(f"\n--- Round {rounds} ---")
            
            # Get choices based on player types
            if type1 == "human":
                choice1 = self.get_player_choice(player1_name)
            else:
                choice1 = self.get_cpu_choice()
                print(f"{player1_name} is choosing...")
            
            if type2 == "human":
                choice2 = self.get_player_choice(player2_name)
            else:
                choice2 = self.get_cpu_choice()
                print(f"{player2_name} is choosing...")
            
            # Determine winner
            self.determine_winner(choice1, choice2, player1_name, player2_name)
            
            # Display current score
            self.display_score(player1_name, player2_name)
            
            # Ask to continue if not CPU vs CPU
            if type1 == "human" or type2 == "human":
                if rounds < max_rounds:
                    continue_game = input("\nContinue to next round? (y/n): ").lower()
                    if continue_game != 'y':
                        break
        
        self.display_final_results(player1_name, player2_name)

    def display_final_results(self, player1_name, player2_name):
        """Display final results and winner"""
        print("\n" + "=" * 40)
        print("🏆 FINAL RESULTS:")
        print("=" * 40)
        print(f"{player1_name}: {self.score_player1} wins")
        print(f"{player2_name}: {self.score_player2} wins")
        print(f"Draws: {self.draws}")
        
        if self.score_player1 > self.score_player2:
            print(f"🎊 {player1_name} is the CHAMPION! 🎊")
        elif self.score_player2 > self.score_player1:
            print(f"🎊 {player2_name} is the CHAMPION! 🎊")
        else:
            print("🏅 The game ended in a TIE!")
        print("=" * 40)