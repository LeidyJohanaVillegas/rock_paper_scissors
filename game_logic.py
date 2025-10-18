import random
import json
from datetime import datetime
from challenges import get_random_challenge, check_challenge

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
        # Challenge state when a loser must perform an English challenge
        self.current_challenge = None
        self.challenge_for_player = None  # 1 or 2
    
    def load_records(self):
        try:
            with open(self.records_file, 'r') as f:
                self.records = json.load(f)
            # Validate structure: ensure lists for each record category
            for key in ["player_vs_player", "player_vs_cpu", "tournament_winners"]:
                if key not in self.records or not isinstance(self.records[key], list):
                    # If the file has a non-list (e.g. {}), coerce to empty list
                    self.records[key] = []
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
        # Defensive: coerce max_rounds to int and ensure minimum of 1
        try:
            max_rounds = int(max_rounds)
            if max_rounds <= 0:
                max_rounds = 5
        except (TypeError, ValueError):
            max_rounds = 5

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
        
        # Reset choices for next round (but keep the made flags for display)
        self.game_state['player1']['choice_made'] = False
        self.game_state['player2']['choice_made'] = False
        self.game_state['both_choices_made'] = False

        # If someone lost and is human, create a challenge for the loser
        # Determine loser
        if result in ['player1', 'player2']:
            loser = 'player2' if result == 'player1' else 'player1'
            loser_num = 1 if loser == 'player1' else 2
            # Only issue a challenge if the loser is human
            if self.game_state[loser]['is_human']:
                # create a challenge and attach to state
                self.current_challenge = get_random_challenge()
                self.challenge_for_player = loser_num
                round_result['challenge_issued'] = True
                # Do not end the round immediately; caller should fetch challenge

        # Check if game should continue (increment round after handling challenges)
        self.game_state['current_round'] += 1
        if self.game_state['current_round'] > self.game_state['max_rounds']:
            # If a challenge was just issued, postpone finalizing the game until challenge resolution
            if round_result.get('challenge_issued'):
                # Mark that the game should end after the challenge finishes
                self.game_state['end_after_challenge'] = True
                round_result['game_complete'] = False
            else:
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

        return round_result

    # Challenge-related methods
    def get_current_challenge(self):
        if not self.current_challenge:
            return None
        # Return challenge without exposing the correct answer when sending to clients
        ch = self.current_challenge.copy()
        # For server-side checking we keep the 'word' or 'correct_answer' in memory
        # but remove it from the public payload
        if ch.get('type') == 'quiz':
            ch.pop('correct_answer', None)
        elif ch.get('type') == 'word_guess':
            ch.pop('word', None)
        return ch

    def submit_challenge_answer(self, player_number, answer):
        # Only allow the player who was assigned the challenge to submit
        if not self.current_challenge or self.challenge_for_player != player_number:
            return {'error': 'No challenge for this player'}

        passed = check_challenge(self.current_challenge, answer)
        # Clear challenge state
        self.current_challenge = None
        self.challenge_for_player = None

        if not passed:
            # If failed, award point to opponent
            opponent_num = 1 if player_number == 2 else 2
            self.game_state[f'player{opponent_num}']['score'] += 1

        # If we were supposed to end the game after this challenge, finalize now
        if self.game_state.get('end_after_challenge'):
            self.game_state['game_active'] = False
            # mark game complete in the returned payload
            resp = {'passed': passed, 'game_state': self.get_game_state(), 'game_complete': True}

            # Save records for PvP games if applicable
            if self.game_state.get('game_mode') == 'player_vs_player':
                winner = (self.game_state['player1']['name'] 
                         if self.game_state['player1']['score'] > self.game_state['player2']['score'] 
                         else self.game_state['player2']['name'])
                self.save_record('player_vs_player', {
                    'match': f"{self.game_state['player1']['name']} vs {self.game_state['player2']['name']}",
                    'winner': winner,
                    'date': datetime.now().isoformat()
                })

            # Clear the flag
            self.game_state['end_after_challenge'] = False
            return resp

        return {'passed': passed, 'game_state': self.get_game_state()}
    
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

        # Expose minimal challenge info (no answers) so clients can react
        safe_state['challenge_pending'] = bool(self.current_challenge)
        safe_state['challenge_for_player'] = self.challenge_for_player

        return safe_state
        
    
    def get_records(self):
        return self.records
    
    def save_record(self, record_type, data):
        # Be defensive: if the record_type is missing or not a list (file corruption), coerce it
        if record_type not in self.records or not isinstance(self.records.get(record_type), list):
            self.records[record_type] = []

        self.records[record_type].append(data)
        self.save_records()