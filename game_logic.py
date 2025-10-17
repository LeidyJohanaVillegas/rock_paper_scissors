import random
import json
from datetime import datetime

class RockPaperScissors:
    def __init__(self):
        self.choices = ["rock", "paper", "scissors"]
        self.records_file = "game_records.json"
        self.reset_game()
        self.load_records()
    
    def reset_game(self):
        self.game_state = {
            'game_mode': None,
            'player1': {'name': 'Player 1', 'score': 0, 'choice': None, 'is_human': True, 'choice_made': False},
            'player2': {'name': 'CPU', 'score': 0, 'choice': None, 'is_human': False, 'choice_made': False},
            'draws': 0,
            'current_round': 1,
            'max_rounds': 5,
            'player_history': [],
            'game_active': False,
            'both_choices_made': False
        }
    
    def load_records(self):
        try:
            with open(self.records_file, 'r') as f:
                self.records = json.load(f)
        except FileNotFoundError:
            self.records = {
                "player_vs_player": [],
                "player_vs_cpu": [],
                "tournament_winners": []
            }
    
    def save_records(self):
        with open(self.records_file, 'w') as f:
            json.dump(self.records, f, indent=2)
    
    def start_game(self, game_mode, player1_name, player2_name, max_rounds):
        self.reset_game()
        self.game_state.update({
            'game_mode': game_mode,
            'player1': {'name': player1_name, 'score': 0, 'choice': None, 'is_human': True, 'choice_made': False},
            'player2': {'name': player2_name, 'score': 0, 'choice': None, 'is_human': False, 'choice_made': False},
            'max_rounds': max_rounds,
            'game_active': True,
            'both_choices_made': False
        })
        
        # Set player types based on game mode
        if game_mode == 'player_vs_player':
            self.game_state['player2']['is_human'] = True
        elif game_mode in ['player_vs_cpu_easy', 'player_vs_cpu_hard']:
            self.game_state['player2']['is_human'] = False
        elif game_mode == 'cpu_vs_cpu':
            self.game_state['player1']['is_human'] = False
            self.game_state['player2']['is_human'] = False
        
        return self.get_game_state()
    
    def get_cpu_choice(self, difficulty="easy"):
        if difficulty == "easy":
            return random.choice(self.choices)
        else:  # hard
            if len(self.game_state['player_history']) >= 3:
                recent_moves = self.game_state['player_history'][-5:]
                most_common = max(set(recent_moves), key=recent_moves.count)
                if random.random() < 0.7:
                    counters = {'rock': 'paper', 'paper': 'scissors', 'scissors': 'rock'}
                    return counters[most_common]
            return random.choice(self.choices)
    
    def play_round(self, player_choice=None, player_number=1):
        if not self.game_state['game_active']:
            return {'error': 'Game not active'}
        
        # Set player choices
        if player_number == 1:
            self.game_state['player1']['choice'] = player_choice
            self.game_state['player1']['choice_made'] = bool(player_choice)
            if player_choice and self.game_state['player1']['is_human']:
                self.game_state['player_history'].append(player_choice)
        else:
            self.game_state['player2']['choice'] = player_choice
            self.game_state['player2']['choice_made'] = bool(player_choice)
        
        # If CPU needs to make a choice
        if (not self.game_state['player1']['choice'] and 
            not self.game_state['player1']['is_human']):
            difficulty = 'hard' if 'hard' in self.game_state.get('game_mode', '') else 'easy'
            cpu_choice = self.get_cpu_choice(difficulty)
            self.game_state['player1']['choice'] = cpu_choice
            self.game_state['player1']['choice_made'] = True
        
        if (not self.game_state['player2']['choice'] and 
            not self.game_state['player2']['is_human']):
            difficulty = 'hard' if 'hard' in self.game_state.get('game_mode', '') else 'easy'
            cpu_choice = self.get_cpu_choice(difficulty)
            self.game_state['player2']['choice'] = cpu_choice
            self.game_state['player2']['choice_made'] = True
        
        # Check if both choices are made
        both_made = (self.game_state['player1']['choice_made'] and 
                    self.game_state['player2']['choice_made'])
        
        self.game_state['both_choices_made'] = both_made
        
        if both_made:
            return self.determine_winner()
        else:
            return {
                'status': 'waiting', 
                'game_state': self.get_game_state(),
                'player_ready': player_number,
                'both_ready': False
            }
    
    def determine_winner(self):
        choice1 = self.game_state['player1']['choice']
        choice2 = self.game_state['player2']['choice']
        
        if choice1 == choice2:
            result = 'draw'
            self.game_state['draws'] += 1
            message = "It's a DRAW!"
        elif ((choice1 == 'rock' and choice2 == 'scissors') or
              (choice1 == 'scissors' and choice2 == 'paper') or
              (choice1 == 'paper' and choice2 == 'rock')):
            result = 'player1'
            self.game_state['player1']['score'] += 1
            message = f"{self.game_state['player1']['name']} WINS!"
        else:
            result = 'player2'
            self.game_state['player2']['score'] += 1
            message = f"{self.game_state['player2']['name']} WINS!"
        
        # Victory messages
        victory_messages = {
            ('rock', 'scissors'): "Rock crushes Scissors! 💥",
            ('scissors', 'paper'): "Scissors cut Paper! ✂️📄",
            ('paper', 'rock'): "Paper covers Rock! 📄🪨"
        }
        
        victory_message = victory_messages.get((choice1, choice2), "") if result == 'player1' else victory_messages.get((choice2, choice1), "")
        
        round_result = {
            'result': result,
            'message': message,
            'victory_message': victory_message,
            'game_state': self.get_game_state(),
            'both_ready': True
        }
        
        # Check if game should continue
        self.game_state['current_round'] += 1
        if self.game_state['current_round'] > self.game_state['max_rounds']:
            round_result['game_complete'] = True
            self.game_state['game_active'] = False
            
            # Save records for PvP games
            if self.game_state['game_mode'] == 'player_vs_player':
                winner = (self.game_state['player1']['name'] 
                         if self.game_state['player1']['score'] > self.game_state['player2']['score'] 
                         else self.game_state['player2']['name'])
                self.save_record('player_vs_player', {
                    'match': f"{self.game_state['player1']['name']} vs {self.game_state['player2']['name']}",
                    'winner': winner,
                    'date': datetime.now().isoformat()
                })
        
        # Reset choices for next round (but keep the made flags for display)
        self.game_state['player1']['choice_made'] = False
        self.game_state['player2']['choice_made'] = False
        self.game_state['both_choices_made'] = False
        
        return round_result
    
    def get_game_state(self):
        # Return a safe version of game state that hides opponent's choice
        safe_state = self.game_state.copy()
        
        # If both choices aren't made, hide the actual choices from players
        if not safe_state['both_choices_made']:
            # For player 1 - only show if they've made a choice
            if safe_state['player1']['choice_made']:
                safe_state['player1']['choice_display'] = 'ready'
                safe_state['player1']['choice_emoji'] = '✅'
                safe_state['player1']['choice_text'] = 'Ready!'
            else:
                safe_state['player1']['choice_display'] = 'waiting'
                safe_state['player1']['choice_emoji'] = '❓'
                safe_state['player1']['choice_text'] = 'Waiting...'
            
            # For player 2 - only show if they've made a choice
            if safe_state['player2']['choice_made']:
                safe_state['player2']['choice_display'] = 'ready'
                safe_state['player2']['choice_emoji'] = '✅'
                safe_state['player2']['choice_text'] = 'Ready!'
            else:
                safe_state['player2']['choice_display'] = 'waiting'
                safe_state['player2']['choice_emoji'] = '❓'
                safe_state['player2']['choice_text'] = 'Waiting...'
        else:
            # When both are ready, show the actual choices
            emojis = {'rock': '🪨', 'paper': '📄', 'scissors': '✂️'}
            names = {'rock': 'ROCK', 'paper': 'PAPER', 'scissors': 'SCISSORS'}
            
            safe_state['player1']['choice_display'] = 'revealed'
            safe_state['player1']['choice_emoji'] = emojis.get(safe_state['player1']['choice'], '❓')
            safe_state['player1']['choice_text'] = names.get(safe_state['player1']['choice'], 'UNKNOWN')
            
            safe_state['player2']['choice_display'] = 'revealed'
            safe_state['player2']['choice_emoji'] = emojis.get(safe_state['player2']['choice'], '❓')
            safe_state['player2']['choice_text'] = names.get(safe_state['player2']['choice'], 'UNKNOWN')
        
        return safe_state
    
    def get_records(self):
        return self.records
    
    def save_record(self, record_type, data):
        if record_type in self.records:
            self.records[record_type].append(data)
            self.save_records()