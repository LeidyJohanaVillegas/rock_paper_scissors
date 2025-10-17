import random
import os
import json
from datetime import datetime

class RockPaperScissors:
    def __init__(self):
        self.choices = ["rock", "paper", "scissors"]
        self.score_player1 = 0
        self.score_player2 = 0
        self.draws = 0
        self.player_history = []
        self.records_file = "game_records.json"
        self.load_records()
    
    def load_records(self):
        """Load game records from file"""
        try:
            with open(self.records_file, 'r') as f:
                self.records = json.load(f)
        except FileNotFoundError:
            self.records = {
                "player_vs_player": {},
                "player_vs_cpu": {},
                "tournament_winners": []
            }
    
    def save_records(self):
        """Save game records to file"""
        with open(self.records_file, 'w') as f:
            json.dump(self.records, f, indent=2)
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_welcome(self):
        """Display welcome message and game rules"""
        print("🎮 Welcome to Rock, Paper, Scissors - ENHANCED!")
        print("=" * 50)
        print("Game Rules:")
        print("• Rock beats Scissors")
        print("• Scissors beats Paper")
        print("• Paper beats Rock")
        print("• Same choice = Draw")
        print("=" * 50)
        print("\nGame Modes:")
        print("1. Player vs Player")
        print("2. Player vs CPU (Easy)")
        print("3. Player vs CPU (Hard - AI learns your patterns!)")
        print("4. CPU vs CPU (Simulation)")
        print("5. Tournament Mode (4 players)")
        print("6. View Records & Statistics")
        print("=" * 50)
    
    def get_player_choice(self, player_name, show_emoji=True):
        """Get choice from a human player"""
        while True:
            self.clear_screen()
            print(f"\n{player_name}, choose your weapon:")
            if show_emoji:
                print("1. Rock 🪨")
                print("2. Paper 📄")
                print("3. Scissors ✂️")
            else:
                print("1. Rock")
                print("2. Paper")
                print("3. Scissors")
            
            choice = input("Enter 1, 2, or 3: ").strip()
            self.clear_screen()
            
            if choice in ['1', '2', '3']:
                choice_text = self.choices[int(choice) - 1]
                # Store player choice for AI learning
                if player_name != "CPU":
                    self.player_history.append(choice_text)
                return choice_text
            else:
                print("❌ Invalid choice! Please enter 1, 2, or 3.")
    
    def get_cpu_choice_easy(self):
        """Generate random choice for CPU (Easy mode)"""
        return random.choice(self.choices)
    
    def get_cpu_choice_hard(self, player_name):
        """CPU that learns from player patterns (Hard mode)"""
        if len(self.player_history) >= 3:
            # Analyze player's most common choice in last 5 moves
            recent_moves = self.player_history[-5:]
            most_common = max(set(recent_moves), key=recent_moves.count)
            # Counter that choice 70% of the time
            if random.random() < 0.7:
                counters = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
                return counters[most_common]
        
        # 30% of the time or if not enough data, choose randomly
        return random.choice(self.choices)
    
    def get_cpu_choice_smart(self, difficulty="medium"):
        """Advanced CPU with different difficulty levels"""
        if difficulty == "easy":
            return random.choice(self.choices)
        elif difficulty == "medium":
            # Slightly weighted towards rock (common beginner choice)
            return random.choices(self.choices, weights=[40, 30, 30])[0]
        else:  # hard
            # Uses pattern recognition
            return self.get_cpu_choice_hard("Player")
    
    def determine_winner(self, choice1, choice2, player1_name, player2_name):
        """Determine the winner of a round"""
        print(f"\n{player1_name} chose: {choice1.upper()} {self.get_emoji(choice1)}")
        print(f"{player2_name} chose: {choice2.upper()} {self.get_emoji(choice2)}")
        
        if choice1 == choice2:
            print("🤝 It's a DRAW!")
            self.draws += 1
            return "draw"
        
        # Winning conditions
        winning_combinations = {
            ('rock', 'scissors'): player1_name,
            ('scissors', 'paper'): player1_name,
            ('paper', 'rock'): player1_name
        }
        
        if (choice1, choice2) in winning_combinations:
            winner = player1_name
            print(f"🎉 {player1_name} WINS this round! {self.get_victory_message(choice1, choice2)}")
            self.score_player1 += 1
        else:
            winner = player2_name
            print(f"🎉 {player2_name} WINS this round! {self.get_victory_message(choice2, choice1)}")
            self.score_player2 += 1
        
        return winner
    
    def get_emoji(self, choice):
        """Get emoji for choice"""
        emojis = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
        return emojis.get(choice, '')
    
    def get_victory_message(self, winner_choice, loser_choice):
        """Get fun victory message"""
        messages = {
            ('rock', 'scissors'): "Rock crushes Scissors! 💥",
            ('scissors', 'paper'): "Scissors cut Paper! ✂️📄",
            ('paper', 'rock'): "Paper covers Rock! 📄🪨"
        }
        return messages.get((winner_choice, loser_choice), "")
    
    def display_score(self, player1_name, player2_name):
        """Display current score with visual indicators"""
        total_rounds = self.score_player1 + self.score_player2 + self.draws
        self.clear_screen()
        print("\n" + "=" * 40)
        print("📊 CURRENT SCORE:")
        print(f"{player1_name}: {self.score_player1} {'⭐' * min(self.score_player1, 3)}")
        print(f"{player2_name}: {self.score_player2} {'⭐' * min(self.score_player2, 3)}")
        print(f"Draws: {self.draws}")
        print(f"Total Rounds: {total_rounds}")
        
        # Show who's winning
        if self.score_player1 > self.score_player2:
            print(f"🏆 {player1_name} is leading!")
        elif self.score_player2 > self.score_player1:
            print(f"🏆 {player2_name} is leading!")
        else:
            print("🏅 It's a tie game!")
        print("=" * 40)
    
    def player_vs_player(self):
        """Mode: Player 1 vs Player 2"""
        player1_name = input("\nEnter Player 1 name: ").strip() or "Player 1"
        player2_name = input("Enter Player 2 name: ").strip() or "Player 2"
        
        self.play_game_loop(player1_name, player2_name, "human", "human")
        
        # Save record
        winner = self.get_winner_name(player1_name, player2_name)
        if winner != "tie":
            self.update_records("player_vs_player", winner, f"{player1_name} vs {player2_name}")
    
    def player_vs_cpu_easy(self):
        self.clear_screen()
        """Mode: Player vs CPU (Easy)"""
        player_name = input("\nEnter your name: ").strip() or "Player"
        cpu_name = "CPU (Easy)"
        
        print(f"\n🤖 Difficulty: EASY")
        print("CPU will choose randomly")
        
        self.play_game_loop(player_name, cpu_name, "human", "cpu_easy")
    
    def player_vs_cpu_hard(self):
        self.clear_screen()
        """Mode: Player vs CPU (Hard)"""
        player_name = input("\nEnter your name: ").strip() or "Player"
        cpu_name = "CPU (Hard)"
        
        print(f"\n🤖 Difficulty: HARD")
        print("⚠️  Warning: CPU learns from your patterns!")
        print("Try to be unpredictable!")
        
        self.play_game_loop(player_name, cpu_name, "human", "cpu_hard")
    
    def cpu_vs_cpu(self):
        """Mode: CPU vs CPU (simulation)"""
        self.clear_screen()
        cpu1_name = "CPU Alpha"
        cpu2_name = "CPU Beta"
        
        print(f"\n🤖 {cpu1_name} vs {cpu2_name} - Simulation Mode")
        print("Watching AI battle...")
        
        rounds = int(input("How many rounds to simulate? (1-20): ") or "5")
        self.play_game_loop(cpu1_name, cpu2_name, "cpu", "cpu", rounds, False)
    
    def tournament_mode(self):
        """Tournament mode with 4 players"""
        self.clear_screen()
        print("\n🏆 TOURNAMENT MODE")
        print("4 players will compete in a knockout tournament!")
        
        players = []
        for i in range(4):
            name = input(f"Enter Player {i+1} name: ").strip() or f"Player {i+1}"
            players.append(name)
        
        print(f"\nTournament Bracket:")
        print(f"Semifinal 1: {players[0]} vs {players[1]}")
        print(f"Semifinal 2: {players[2]} vs {players[3]}")
        
        # Semifinals
        input("\nPress Enter to start Semifinals...")
        winners = []
        
        # Semifinal 1
        print(f"\n--- SEMIFINAL 1: {players[0]} vs {players[1]} ---")
        self.reset_scores()
        self.play_game_loop(players[0], players[1], "human", "human", 3, False)
        winner1 = self.get_winner_name(players[0], players[1])
        winners.append(winner1)
        
        # Semifinal 2
        self.clear_screen()
        print(f"\n--- SEMIFINAL 2: {players[2]} vs {players[3]} ---")
        self.reset_scores()
        self.play_game_loop(players[2], players[3], "human", "human", 3, False)
        winner2 = self.get_winner_name(players[2], players[3])
        winners.append(winner2)
        
        # Final
        self.clear_screen()
        print(f"\n--- FINAL: {winner1} vs {winner2} ---")
        self.reset_scores()
        self.play_game_loop(winner1, winner2, "human", "human", 5, False)
        champion = self.get_winner_name(winner1, winner2)
        self.clear_screen()
        print(f"\n🎊 TOURNAMENT CHAMPION: {champion} 🎊")
        self.records["tournament_winners"].append({
            "champion": champion,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "participants": players
        })
        self.save_records()
    
    def view_records(self):
        """Display game records and statistics"""
        self.clear_screen()
        print("📊 GAME RECORDS & STATISTICS")
        print("=" * 50)
        
        # Player vs Player records
        self.clear_screen()
        print("\n🏆 Player vs Player Records:")
        if self.records["player_vs_player"]:
            for match, winner in list(self.records["player_vs_player"].items())[-5:]:
                print(f"  {match} → Winner: {winner}")
        else:
            print("  No records yet")
        
        # Tournament winners
        self.clear_screen()
        print("\n🏅 Tournament Champions:")
        if self.records["tournament_winners"]:
            for winner in self.records["tournament_winners"][-3:]:
                print(f"  {winner['champion']} - {winner['date']}")
        else:
            print("  No tournament records yet")
        
        # Personal statistics
        self.clear_screen()
        print("\n📈 Your Game Patterns:")
        if self.player_history:
            total_games = len(self.player_history)
            rock_count = self.player_history.count('rock')
            paper_count = self.player_history.count('paper')
            scissors_count = self.player_history.count('scissors')
            
            print(f"  Total moves: {total_games}")
            print(f"  Rock: {rock_count} ({rock_count/total_games*100:.1f}%)")
            print(f"  Paper: {paper_count} ({paper_count/total_games*100:.1f}%)")
            print(f"  Scissors: {scissors_count} ({scissors_count/total_games*100:.1f}%)")
            
            # Most common choice
            most_common = max(set(self.player_history), key=self.player_history.count)
            print(f"  Favorite move: {most_common.upper()}")
        
        input("\nPress Enter to return to main menu...")
    
    def play_game_loop(self, player1_name, player2_name, type1, type2, max_rounds=5, interactive=True):
        """Main game loop for any mode"""
        rounds = 0
        
        while rounds < max_rounds:
            rounds += 1
            print(f"\n--- Round {rounds} ---")
            
            # Get choices based on player types
            if type1 == "human":
                choice1 = self.get_player_choice(player1_name)
            elif type1 == "cpu_hard":
                choice1 = self.get_cpu_choice_hard(player1_name)
            else:
                choice1 = self.get_cpu_choice_easy()
                if interactive:
                    print(f"{player1_name} is choosing...")
            
            if type2 == "human":
                choice2 = self.get_player_choice(player2_name)
            elif type2 == "cpu_hard":
                choice2 = self.get_cpu_choice_hard(player2_name)
            else:
                choice2 = self.get_cpu_choice_easy()
                if interactive:
                    print(f"{player2_name} is choosing...")
            
            # Small delay for CPU vs CPU to make it watchable
            if type1 != "human" and type2 != "human" and interactive:
                import time
                time.sleep(1)
            
            # Determine winner
            self.determine_winner(choice1, choice2, player1_name, player2_name)
            
            # Display current score
            self.display_score(player1_name, player2_name)
            
            # Ask to continue if interactive
            if interactive and (type1 == "human" or type2 == "human"):
                if rounds < max_rounds:
                    continue_game = input("\nContinue to next round? (y/n): ").lower()
                    if continue_game != 'y':
                        break
        
        self.display_final_results(player1_name, player2_name)
    
    def get_winner_name(self, player1_name, player2_name):
        """Get the winner name or 'tie'"""
        if self.score_player1 > self.score_player2:
            return player1_name
        elif self.score_player2 > self.score_player1:
            return player2_name
        else:
            return "tie"
    
    def update_records(self, record_type, winner, match_info):
        """Update game records"""
        if record_type == "player_vs_player":
            self.records["player_vs_player"][match_info] = winner
        self.save_records()
    
    def display_final_results(self, player1_name, player2_name):
        """Display final results and winner"""
        self.clear_screen()
        print("\n" + "=" * 50)
        print("🏆 FINAL RESULTS:")
        print("=" * 50)
        print(f"{player1_name}: {self.score_player1} wins")
        print(f"{player2_name}: {self.score_player2} wins")
        print(f"Draws: {self.draws}")
        
        if self.score_player1 > self.score_player2:
            print(f"🎊 {player1_name} is the CHAMPION! 🎊")
            print("Congratulations! 🥳")
        elif self.score_player2 > self.score_player1:
            print(f"🎊 {player2_name} is the CHAMPION! 🎊")
            print("Congratulations! 🥳")
        else:
            print("🏅 The game ended in a TIE!")
            print("What an intense match! 🤝")
        print("=" * 50)
    
    def reset_scores(self):
        """Reset all scores for a new game"""
        self.score_player1 = 0
        self.score_player2 = 0
        self.draws = 0
    
    def main_menu(self):
        """Main menu to select game mode"""
        while True:
            self.clear_screen()
            self.display_welcome()
            
            try:
                choice = input("\nSelect game mode (1-6) or 'q' to quit: ").strip()
                
                if choice == 'q':
                    print("Thanks for playing! Goodbye! 👋")
                    self.save_records()
                    break
                elif choice == '1':
                    self.clear_screen()
                    print("🎮 Player vs Player Mode")
                    self.player_vs_player()
                elif choice == '2':
                    self.clear_screen()
                    print("🎮 Player vs CPU - EASY Mode")
                    self.player_vs_cpu_easy()
                elif choice == '3':
                    self.clear_screen()
                    print("🎮 Player vs CPU - HARD Mode")
                    self.player_vs_cpu_hard()
                elif choice == '4':
                    self.clear_screen()
                    print("🎮 CPU vs CPU Mode")
                    self.cpu_vs_cpu()
                elif choice == '5':
                    self.clear_screen()
                    self.tournament_mode()
                elif choice == '6':
                    self.view_records()
                    continue
                else:
                    print("❌ Invalid choice! Please try again.")
                    input("Press Enter to continue...")
                    continue
                
                # Ask to play again
                play_again = input("\nWould you like to play again? (y/n): ").lower()
                if play_again == 'y':
                    self.reset_scores()
                else:
                    print("Thanks for playing! Goodbye! 👋")
                    self.save_records()
                    break
                    
            except KeyboardInterrupt:
                print("\n\nGame interrupted. Thanks for playing! 👋")
                self.save_records()
                break

# Start the game
if __name__ == "__main__":
    game = RockPaperScissors()
    game.main_menu()