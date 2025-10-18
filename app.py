from flask import Flask, render_template, request, jsonify
from game_logic import RockPaperScissors
import json
from datetime import datetime

app = Flask(__name__)
game = RockPaperScissors()

@app.route('/')
def index():
    return render_template('index.html')

# API Routes
@app.route('/api/start_game', methods=['POST'])
def start_game():
    data = request.json
    game_mode = data.get('game_mode')
    player1_name = data.get('player1_name', 'Player 1')
    player2_name = data.get('player2_name', 'CPU')
    # Be defensive: ensure max_rounds is an integer
    try:
        max_rounds = int(data.get('max_rounds', 5))
        if max_rounds <= 0:
            max_rounds = 5
    except (TypeError, ValueError):
        max_rounds = 5
    
    result = game.start_game(game_mode, player1_name, player2_name, max_rounds)
    return jsonify(result)

@app.route('/api/play_round', methods=['POST'])
def play_round():
    data = request.json
    player_choice = data.get('player_choice')
    player_number = data.get('player_number', 1)
    
    result = game.play_round(player_choice, player_number)
    return jsonify(result)

@app.route('/api/get_game_state', methods=['GET'])
def get_game_state():
    return jsonify(game.get_game_state())


@app.route('/api/get_challenge', methods=['GET'])
def get_challenge():
    ch = game.get_current_challenge()
    if not ch:
        return jsonify({'challenge': None})
    return jsonify({'challenge': ch, 'for_player': game.challenge_for_player})


@app.route('/api/submit_challenge', methods=['POST'])
def submit_challenge():
    data = request.json
    player_number = data.get('player_number')
    answer = data.get('answer')
    result = game.submit_challenge_answer(player_number, answer)
    return jsonify(result)

@app.route('/api/reset_game', methods=['POST'])
def reset_game():
    game.reset_game()
    return jsonify({'status': 'success'})

@app.route('/api/get_records', methods=['GET'])
def get_records():
    return jsonify(game.get_records())

@app.route('/api/save_record', methods=['POST'])
def save_record():
    data = request.json
    record_type = data.get('record_type')
    data = data.get('data')
    game.save_record(record_type, data)
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Run without debug/reload to avoid restart loops while diagnosing
    app.run(debug=False, port=5000)