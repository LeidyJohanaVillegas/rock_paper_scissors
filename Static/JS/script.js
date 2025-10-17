// API Functions
async function apiCall(endpoint, data = null) {
    try {
        const options = {
            method: data ? 'POST' : 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`/api/${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        return { error: 'Network error' };
    }
}

// Game State Management
let currentGameState = null;

// Screen Management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function showMainMenu() {
    showScreen('main-menu');
    apiCall('reset_game');
}

// Setup Screens
function showSetup(mode) {
    const setupContent = document.getElementById('setup-content');
    const titles = {
        'player_vs_player': '👥 Player vs Player',
        'player_vs_cpu_easy': '🤖 Player vs CPU (Easy)',
        'player_vs_cpu_hard': '🧠 Player vs CPU (Hard)',
        'cpu_vs_cpu': '🤖 CPU vs CPU'
    };
    
    document.getElementById('setup-title').textContent = titles[mode] || 'Game Setup';
    
    setupContent.innerHTML = `
        <div class="setup-form">
            ${getSetupForm(mode)}
            <button class="start-btn" onclick="startGame('${mode}')">Start Game</button>
        </div>
    `;
    
    showScreen('setup-screen');
}

function getSetupForm(mode) {
    const forms = {
        'player_vs_player': `
            <div class="form-group">
                <label for="player1-name">Player 1 Name:</label>
                <input type="text" id="player1-name" value="Player 1">
            </div>
            <div class="form-group">
                <label for="player2-name">Player 2 Name:</label>
                <input type="text" id="player2-name" value="Player 2">
            </div>
            <div class="form-group">
                <label for="max-rounds">Number of Rounds:</label>
                <select id="max-rounds">
                    <option value="3">3 Rounds</option>
                    <option value="5" selected>5 Rounds</option>
                    <option value="7">7 Rounds</option>
                    <option value="10">10 Rounds</option>
                </select>
            </div>
        `,
        'player_vs_cpu_easy': `
            <div class="form-group">
                <label for="player1-name">Your Name:</label>
                <input type="text" id="player1-name" value="Player">
            </div>
            <div class="form-group">
                <label for="max-rounds">Number of Rounds:</label>
                <select id="max-rounds">
                    <option value="3">3 Rounds</option>
                    <option value="5" selected>5 Rounds</option>
                    <option value="7">7 Rounds</option>
                </select>
            </div>
        `,
        'player_vs_cpu_hard': `
            <div class="form-group">
                <label for="player1-name">Your Name:</label>
                <input type="text" id="player1-name" value="Player">
            </div>
            <div class="form-group">
                <label for="max-rounds">Number of Rounds:</label>
                <select id="max-rounds">
                    <option value="3">3 Rounds</option>
                    <option value="5" selected>5 Rounds</option>
                    <option value="7">7 Rounds</option>
                </select>
            </div>
            <p style="color: #FFA726; text-align: center; margin: 15px 0;">
                ⚠️ Warning: CPU learns from your patterns! Try to be unpredictable!
            </p>
        `,
        'cpu_vs_cpu': `
            <div class="form-group">
                <label for="max-rounds">Number of Rounds:</label>
                <select id="max-rounds">
                    <option value="5">5 Rounds</option>
                    <option value="10" selected>10 Rounds</option>
                    <option value="15">15 Rounds</option>
                    <option value="20">20 Rounds</option>
                </select>
            </div>
        `
    };
    
    return forms[mode] || '';
}

// Game Functions
async function startGame(gameMode) {
    const player1Name = document.getElementById('player1-name')?.value || 'Player 1';
    const player2Name = document.getElementById('player2-name')?.value || 'CPU';
    const maxRounds = parseInt(document.getElementById('max-rounds').value);
    
    const result = await apiCall('start_game', {
        game_mode: gameMode,
        player1_name: player1Name,
        player2_name: player2Name,
        max_rounds: maxRounds
    });
    
    if (!result.error) {
        currentGameState = result;
        updateGameDisplay();
        showScreen('game-screen');
        
        // Auto-play for CPU vs CPU
        if (gameMode === 'cpu_vs_cpu') {
            setTimeout(playCPURound, 1000);
        }
    }
}

async function makeChoice(choice, playerNumber) {
    const result = await apiCall('play_round', {
        player_choice: choice,
        player_number: playerNumber
    });
    
    if (!result.error) {
        if (result.status === 'waiting') {
            currentGameState = result.game_state;
            updateChoiceDisplay(playerNumber, choice);
        } else {
            currentGameState = result.game_state;
            showRoundResult(result);
        }
    }
}

async function playCPURound() {
    if (!currentGameState.game_active) return;
    
    // Player 1 CPU choice
    if (!currentGameState.player1.is_human && !currentGameState.player1.choice) {
        await makeChoice('', 1);
    }
    
    // Player 2 CPU choice
    if (!currentGameState.player2.is_human && !currentGameState.player2.choice) {
        setTimeout(async () => {
            await makeChoice('', 2);
        }, 1000);
    }
}

function updateGameDisplay() {
    if (!currentGameState) return;
    
    document.getElementById('game-title').textContent = 
        `${currentGameState.player1.name} vs ${currentGameState.player2.name}`;
    document.getElementById('round-counter').textContent = 
        `Round ${currentGameState.current_round} of ${currentGameState.max_rounds}`;
    
    document.getElementById('player1-name').textContent = currentGameState.player1.name;
    document.getElementById('player2-name').textContent = currentGameState.player2.name;
    
    document.getElementById('score-player1').textContent = currentGameState.player1.score;
    document.getElementById('score-player2').textContent = currentGameState.player2.score;
    document.getElementById('score-draws').textContent = currentGameState.draws;
    
    document.getElementById('score-player1-name').textContent = currentGameState.player1.name;
    document.getElementById('score-player2-name').textContent = currentGameState.player2.name;
    
    // Show/hide buttons based on player type
    document.getElementById('player1-buttons').style.display = 
        currentGameState.player1.is_human ? 'block' : 'none';
    document.getElementById('player2-buttons').style.display = 
        currentGameState.player2.is_human ? 'block' : 'none';
    
    resetChoiceDisplays();
}

function updateChoiceDisplay(playerNumber, choice) {
    const emojis = { rock: '🪨', paper: '📄', scissors: '✂️' };
    const names = { rock: 'ROCK', paper: 'PAPER', scissors: 'SCISSORS' };
    
    const display = document.getElementById(`player${playerNumber}-choice`);
    display.innerHTML = `
        <div class="choice-emoji">${emojis[choice]}</div>
        <div class="choice-text">${names[choice]}</div>
    `;
}

function showRoundResult(result) {
    updateChoiceDisplay(1, currentGameState.player1.choice);
    updateChoiceDisplay(2, currentGameState.player2.choice);
    
    document.getElementById('round-result').textContent = result.message;
    document.getElementById('victory-message').textContent = result.victory_message || '';
    document.getElementById('result-area').classList.remove('hidden');
    
    // Update scores
    document.getElementById('score-player1').textContent = currentGameState.player1.score;
    document.getElementById('score-player2').textContent = currentGameState.player2.score;
    document.getElementById('score-draws').textContent = currentGameState.draws;
    
    if (result.game_complete) {
        document.querySelector('.next-round-btn').textContent = 'View Final Results';
        document.querySelector('.next-round-btn').onclick = showFinalResults;
    }
}

function resetChoiceDisplays() {
    document.getElementById('player1-choice').innerHTML = '<div class="choice-emoji">❓</div><div class="choice-text">Waiting...</div>';
    document.getElementById('player2-choice').innerHTML = '<div class="choice-emoji">❓</div><div class="choice-text">Waiting...</div>';
    document.getElementById('result-area').classList.add('hidden');
}

async function nextRound() {
    if (currentGameState && currentGameState.game_active) {
        updateGameDisplay();
    }
}

function showFinalResults() {
    if (!currentGameState) return;
    
    let championMessage;
    if (currentGameState.player1.score > currentGameState.player2.score) {
        championMessage = `🎊 ${currentGameState.player1.name} is the CHAMPION! 🎊`;
    } else if (currentGameState.player2.score > currentGameState.player1.score) {
        championMessage = `🎊 ${currentGameState.player2.name} is the CHAMPION! 🎊`;
    } else {
        championMessage = "🏅 The game ended in a TIE!";
    }
    
    alert(championMessage);
    showMainMenu();
}

function endGame() {
    if (confirm('Are you sure you want to end the current game?')) {
        showMainMenu();
    }
}

// Records Functions
async function showRecords() {
    const records = await apiCall('get_records');
    if (!records.error) {
        displayRecords(records);
        showScreen('records-screen');
    }
}

function displayRecords(records) {
    // Display PvP records
    const pvpList = document.getElementById('pvp-records-list');
    if (records.player_vs_player.length > 0) {
        pvpList.innerHTML = records.player_vs_player.map(record => `
            <div class="record-item">
                <strong>${record.match}</strong><br>
                Winner: ${record.winner}<br>
                <small>${new Date(record.date).toLocaleDateString()}</small>
            </div>
        `).join('');
    } else {
        pvpList.innerHTML = '<p>No player vs player records yet.</p>';
    }
    
    // Display tournament records
    const tournamentList = document.getElementById('tournament-records-list');
    if (records.tournament_winners.length > 0) {
        tournamentList.innerHTML = records.tournament_winners.map(record => `
            <div class="record-item">
                <strong>${record.champion}</strong><br>
                <small>${new Date(record.date).toLocaleDateString()}</small>
            </div>
        `).join('');
    } else {
        tournamentList.innerHTML = '<p>No tournament records yet.</p>';
    }
    
    // Display statistics
    const statsContent = document.getElementById('stats-content');
    if (currentGameState && currentGameState.player_history.length > 0) {
        const history = currentGameState.player_history;
        const total = history.length;
        const rockCount = history.filter(c => c === 'rock').length;
        const paperCount = history.filter(c => c === 'paper').length;
        const scissorsCount = history.filter(c => c === 'scissors').length;
        
        const mostCommon = [...new Set(history)].reduce((a, b) => 
            history.filter(v => v === a).length > history.filter(v => v === b).length ? a : b
        );
        
        statsContent.innerHTML = `
            <div class="stats-grid">
                <div class="stat-item">
                    <h4>Total Moves</h4>
                    <span class="stat-number">${total}</span>
                </div>
                <div class="stat-item">
                    <h4>Rock</h4>
                    <span class="stat-number">${rockCount} (${((rockCount/total)*100).toFixed(1)}%)</span>
                </div>
                <div class="stat-item">
                    <h4>Paper</h4>
                    <span class="stat-number">${paperCount} (${((paperCount/total)*100).toFixed(1)}%)</span>
                </div>
                <div class="stat-item">
                    <h4>Scissors</h4>
                    <span class="stat-number">${scissorsCount} (${((scissorsCount/total)*100).toFixed(1)}%)</span>
                </div>
                <div class="stat-item favorite-move">
                    <h4>Favorite Move</h4>
                    <span class="stat-number">${mostCommon.toUpperCase()}</span>
                </div>
            </div>
        `;
    } else {
        statsContent.innerHTML = '<p>No game statistics yet. Play some games first!</p>';
    }
}

function showTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    showMainMenu();
});