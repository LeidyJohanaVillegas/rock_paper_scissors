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
let currentPlayer = 1; // Track which player is currently playing

// Screen Management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function showMainMenu() {
    showScreen('main-menu');
    // send an empty object so apiCall uses POST (server expects POST for /api/reset_game)
    apiCall('reset_game', {});
    currentPlayer = 1;
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
            <div class="privacy-notice">
                <p>🔒 <strong>Privacy Feature:</strong> Players won't see each other's choices until both have selected!</p>
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
        currentPlayer = 1; // Reset to player 1
        updateGameDisplay();
        showScreen('game-screen');
        
        // Auto-play for CPU vs CPU
        if (gameMode === 'cpu_vs_cpu') {
            setTimeout(playCPURound, 1000);
        }
    }
}

async function makeChoice(choice, playerNumber) {
    // Only allow the current player to make a choice
    if (playerNumber !== currentPlayer) {
        alert(`It's ${currentGameState['player' + currentPlayer].name}'s turn!`);
        return;
    }
    
    const result = await apiCall('play_round', {
        player_choice: choice,
        player_number: playerNumber
    });
    
    if (!result.error) {
        if (result.status === 'waiting') {
            currentGameState = result.game_state;
            updateChoiceDisplay(playerNumber, choice, true); // true = hide actual choice
            disablePlayerButtons(playerNumber);
            
            // Switch to next player if it's PvP
            if (currentGameState.game_mode === 'player_vs_player') {
                currentPlayer = currentPlayer === 1 ? 2 : 1;
                showPlayerTurnMessage();
            }
            
        } else {
            currentGameState = result.game_state;
            // Show both choices when both players have chosen
            updateChoiceDisplay(1, currentGameState.player1.choice_display, false);
            updateChoiceDisplay(2, currentGameState.player2.choice_display, false);
            showRoundResult(result);
            
            // Reset for next round
            currentPlayer = 1;
        }
    }
}

function showPlayerTurnMessage() {
    const playerName = currentGameState['player' + currentPlayer].name;
    const messageArea = document.getElementById('turn-message') || createTurnMessageArea();
    messageArea.textContent = `🎮 ${playerName}'s turn!`;
    messageArea.style.display = 'block';
}

function createTurnMessageArea() {
    const gameArea = document.querySelector('.game-area');
    const messageDiv = document.createElement('div');
    messageDiv.id = 'turn-message';
    messageDiv.className = 'turn-message';
    gameArea.insertBefore(messageDiv, gameArea.firstChild);
    return messageDiv;
}

function disablePlayerButtons(playerNumber) {
    const buttons = document.getElementById(`player${playerNumber}-buttons`);
    if (buttons) {
        buttons.querySelectorAll('.choice-btn').forEach(btn => {
            btn.disabled = true;
            btn.style.opacity = '0.6';
        });
    }
}

function enableAllButtons() {
    [1, 2].forEach(playerNumber => {
        const buttons = document.getElementById(`player${playerNumber}-buttons`);
        if (buttons) {
            buttons.querySelectorAll('.choice-btn').forEach(btn => {
                btn.disabled = false;
                btn.style.opacity = '1';
            });
        }
    });
}

async function playCPURound() {
    if (!currentGameState.game_active) return;
    
    // Player 1 CPU choice
    if (!currentGameState.player1.is_human && !currentGameState.player1.choice_made) {
        await makeChoice('', 1);
    }
    
    // Player 2 CPU choice
    if (!currentGameState.player2.is_human && !currentGameState.player2.choice_made) {
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
    
    // Show/hide buttons based on player type and game state
    updatePlayerInterfaces();
    
    resetChoiceDisplays();
    
    // Show turn message if it's PvP
    if (currentGameState.game_mode === 'player_vs_player') {
        showPlayerTurnMessage();
    }
}

function updatePlayerInterfaces() {
    // Player 1 interface
    const player1Buttons = document.getElementById('player1-buttons');
    if (player1Buttons) {
        player1Buttons.style.display = currentGameState.player1.is_human ? 'block' : 'none';
        if (currentGameState.player1.is_human) {
            const buttons = player1Buttons.querySelectorAll('.choice-btn');
            buttons.forEach(btn => {
                btn.disabled = currentPlayer !== 1 || currentGameState.player1.choice_made;
                btn.style.opacity = currentPlayer !== 1 || currentGameState.player1.choice_made ? '0.6' : '1';
            });
        }
    }
    
    // Player 2 interface
    const player2Buttons = document.getElementById('player2-buttons');
    if (player2Buttons) {
        player2Buttons.style.display = currentGameState.player2.is_human ? 'block' : 'none';
        if (currentGameState.player2.is_human) {
            const buttons = player2Buttons.querySelectorAll('.choice-btn');
            buttons.forEach(btn => {
                btn.disabled = currentPlayer !== 2 || currentGameState.player2.choice_made;
                btn.style.opacity = currentPlayer !== 2 || currentGameState.player2.choice_made ? '0.6' : '1';
            });
        }
    }
}

function updateChoiceDisplay(playerNumber, choice, hideActualChoice = true) {
    const display = document.getElementById(`player${playerNumber}-choice`);
    
    if (hideActualChoice && !currentGameState.both_choices_made) {
        // Show ready status instead of actual choice
        const emojis = { '✅ Ready!': '✅', '❓ Waiting...': '❓' };
        const displayText = typeof choice === 'string' ? choice : '❓ Waiting...';
        
        display.innerHTML = `
            <div class="choice-emoji">${emojis[displayText] || '❓'}</div>
            <div class="choice-text">${displayText}</div>
        `;
    } else {
        // Show actual choice
        const emojis = { rock: '🪨', paper: '📄', scissors: '✂️' };
        const names = { rock: 'ROCK', paper: 'PAPER', scissors: 'SCISSORS' };
        
        display.innerHTML = `
            <div class="choice-emoji">${emojis[choice] || '❓'}</div>
            <div class="choice-text">${names[choice] || choice}</div>
        `;
    }
}

function showRoundResult(result) {
    // Enable all buttons for next round
    enableAllButtons();
    
    // Hide turn message
    const messageArea = document.getElementById('turn-message');
    if (messageArea) {
        messageArea.style.display = 'none';
    }
    
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
        // Reset choice flags for new round
        currentGameState.player1.choice_made = false;
        currentGameState.player2.choice_made = false;
        currentGameState.both_choices_made = false;
        
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

// Records Functions (mantener igual que antes)
async function showRecords() {
    const records = await apiCall('get_records');
    if (!records.error) {
        displayRecords(records);
        showScreen('records-screen');
    }
}

function displayRecords(records) {
    // ... (mantener el código de records igual)
}

function showTab(tabId) {
    // ... (mantener el código de tabs igual)
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    showMainMenu();
});