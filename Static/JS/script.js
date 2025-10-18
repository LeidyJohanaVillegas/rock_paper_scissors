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
    // Ensure server route expects POST — send an empty object so apiCall uses POST
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
    
    // If user previously selected rounds, preselect that value
    const savedRounds = localStorage.getItem('rps_max_rounds');
    if (savedRounds) {
        const select = document.getElementById('setup-max-rounds');
        if (select) select.value = savedRounds;
    }

    showScreen('setup-screen');
}

function getSetupForm(mode) {
    const forms = {
        'player_vs_player': `
                <div class="form-group">
                    <label for="setup-player1-name">Player 1 Name:</label>
                    <input type="text" id="setup-player1-name" value="Player 1">
                </div>
                <div class="form-group">
                    <label for="setup-player2-name">Player 2 Name:</label>
                    <input type="text" id="setup-player2-name" value="Player 2">
                </div>
                <div class="form-group">
                    <label for="setup-max-rounds">Number of Rounds:</label>
                    <select id="setup-max-rounds">
                        <option value="3">3 Rounds</option>
                        <option value="5">5 Rounds</option>
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
                <label for="setup-player1-name">Your Name:</label>
                <input type="text" id="setup-player1-name" value="Player">
            </div>
            <div class="form-group">
                <label for="setup-max-rounds">Number of Rounds:</label>
                <select id="setup-max-rounds">
                    <option value="3">3 Rounds</option>
                    <option value="5">5 Rounds</option>
                    <option value="7">7 Rounds</option>
                    <option value="10">10 Rounds</option>
                </select>
            </div>
        `,
        'player_vs_cpu_hard': `
            <div class="form-group">
                <label for="setup-player1-name">Your Name:</label>
                <input type="text" id="setup-player1-name" value="Player">
            </div>
            <div class="form-group">
                <label for="setup-max-rounds">Number of Rounds:</label>
                <select id="setup-max-rounds">
                    <option value="3">3 Rounds</option>
                    <option value="5">5 Rounds</option>
                    <option value="7">7 Rounds</option>
                    <option value="10">10 Rounds</option>
                </select>
            </div>
            <p style="color: #FFA726; text-align: center; margin: 15px 0;">
                ⚠️ Warning: CPU learns from your patterns! Try to be unpredictable!
            </p>
        `,
        'cpu_vs_cpu': `
            <div class="form-group">
                <label for="setup-max-rounds">Number of Rounds:</label>
                <select id="setup-max-rounds">
                    <option value="3">3 Rounds</option>
                    <option value="5">5 Rounds</option>
                    <option value="7">7 Rounds</option>
                    <option value="10">10 Rounds</option>
                </select>
            </div>
        `
    };
    
    return forms[mode] || '';
}

// Game Functions
async function startGame(gameMode) {
    // Read from setup form inputs (different ids to avoid collision with game display ids)
    const player1Name = document.getElementById('setup-player1-name')?.value || 'Player 1';
    const player2Name = document.getElementById('setup-player2-name')?.value || 'CPU';
    const maxRounds = parseInt(document.getElementById('setup-max-rounds').value);

    // Persist the user's chosen rounds so next time it's preselected
    try {
        if (!isNaN(maxRounds)) localStorage.setItem('rps_max_rounds', String(maxRounds));
    } catch (e) {
        // ignore storage errors
        console.warn('Could not save max rounds to localStorage', e);
    }
    
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
            
            // Start polling for state updates
            updateGameStateFromServer();
            
            // Switch to next player if it's PvP
            if (currentGameState.game_mode === 'player_vs_player') {
                currentPlayer = currentPlayer === 1 ? 2 : 1;
                // Update interfaces so buttons enable/disable according to the new currentPlayer
                updatePlayerInterfaces();
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

function updateGameStateFromServer() {
    // Periodically check game state from server (optional)
    if (currentGameState && currentGameState.game_active && !currentGameState.both_choices_made) {
        setTimeout(async () => {
            const result = await apiCall('get_game_state');
            if (!result.error && result.game_mode === currentGameState.game_mode) {
                // Only update if the game mode is the same
                const previousState = JSON.stringify(currentGameState);
                const newState = JSON.stringify(result);
                
                if (previousState !== newState) {
                    currentGameState = result;
                    updateGameDisplay();
                    
                    // Auto-play for CPU
                    if (!currentGameState.player1.is_human && !currentGameState.player1.choice_made) {
                        setTimeout(() => makeChoice('', 1), 500);
                    }
                    if (!currentGameState.player2.is_human && !currentGameState.player2.choice_made) {
                        setTimeout(() => makeChoice('', 2), 1000);
                    }
                    // If server reports a pending challenge, fetch/show it
                    if (currentGameState.challenge_pending) {
                        // Only fetch if there's a specific player assigned
                        if (currentGameState.challenge_for_player) {
                            fetchAndShowChallenge();
                        }
                    }
                }
            }
        }, 1000);
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
    const playerState = currentGameState['player' + playerNumber];
    
    if (!currentGameState.both_choices_made && hideActualChoice) {
        // Show ready/waiting status instead of actual choice
        const status = playerState.choice_display; // 'waiting' or 'ready'
        const emoji = playerState.choice_emoji; // '❓' or '✅'
        const text = playerState.choice_text; // 'Waiting...' or 'Ready!'
        
        // Update CSS classes for styling
        display.className = `choice-display ${status}`;
        
        display.innerHTML = `
            <div class="choice-emoji">${emoji}</div>
            <div class="choice-text">${text}</div>
        `;
    } else {
        // Show actual choice - both players have chosen
        const emoji = playerState.choice_emoji;
        const text = playerState.choice_text;
        
        // Update CSS classes for styling
        display.className = 'choice-display revealed';
        
        display.innerHTML = `
            <div class="choice-emoji">${emoji}</div>
            <div class="choice-text">${text}</div>
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

    // If server issued a challenge for the loser, fetch and show it
    if (result.challenge_issued) {
        // fetch challenge data from server and show UI
        fetchAndShowChallenge(result);
    }
}

// Challenge handling
let currentChallengeForPlayer = null;
let lastChallengeResponse = null;

async function fetchAndShowChallenge(roundResult) {
    const chResp = await apiCall('get_challenge');
    if (chResp.error) return;
    const challenge = chResp.challenge;
    const forPlayer = chResp.for_player;
    if (!challenge) return;

    currentChallengeForPlayer = forPlayer;
    // Show the challenge area
    document.getElementById('challenge-area').classList.remove('hidden');
    document.getElementById('challenge-result').classList.add('hidden');

    // Indicate which player must answer
    const instr = document.getElementById('challenge-instruction');
    if (instr) {
        const playerName = currentGameState ? currentGameState['player' + forPlayer].name : `Player ${forPlayer}`;
        instr.textContent = `${playerName}, you lost this round. Complete the English Challenge to avoid giving a point to your opponent.`;
    }

    // Hide all challenge content first
    document.getElementById('quiz-challenge').classList.add('hidden');
    document.getElementById('word-challenge').classList.add('hidden');

    if (challenge.type === 'quiz') {
        // Show quiz UI and populate options
        document.getElementById('quiz-challenge').classList.remove('hidden');
        document.getElementById('quiz-question').textContent = challenge.question || '';
        document.getElementById('option-a').textContent = challenge.options?.a || '';
        document.getElementById('option-b').textContent = challenge.options?.b || '';
        document.getElementById('option-c').textContent = challenge.options?.c || '';
        document.getElementById('option-d').textContent = challenge.options?.d || '';
    } else if (challenge.type === 'word_guess') {
        document.getElementById('word-challenge').classList.remove('hidden');
        document.getElementById('word-clue').textContent = challenge.clue || '';
        document.getElementById('hint-text').textContent = challenge.hint || '';
        document.getElementById('word-answer').value = '';
    }
}

async function submitChallengeAnswer(letter) {
    if (!currentChallengeForPlayer) return;
    const resp = await apiCall('submit_challenge', { player_number: currentChallengeForPlayer, answer: letter });
    handleChallengeResponse(resp);
}

async function submitWordChallenge() {
    if (!currentChallengeForPlayer) return;
    const answer = document.getElementById('word-answer').value || '';
    const resp = await apiCall('submit_challenge', { player_number: currentChallengeForPlayer, answer: answer });
    handleChallengeResponse(resp);
}

function handleChallengeResponse(resp) {
    if (!resp) return;
    if (resp.error) {
        document.getElementById('challenge-result-title').textContent = 'Error';
        document.getElementById('challenge-result-message').textContent = resp.error;
        document.getElementById('challenge-result').classList.remove('hidden');
        return;
    }

    lastChallengeResponse = resp;
    // Show result
    const passed = resp.passed;
    document.getElementById('quiz-challenge').classList.add('hidden');
    document.getElementById('word-challenge').classList.add('hidden');
    document.getElementById('challenge-result').classList.remove('hidden');
    if (passed) {
        document.getElementById('challenge-result-title').textContent = 'Well done!';
        document.getElementById('challenge-result-message').textContent = 'You passed the challenge and prevented your opponent from getting the point.';
    } else {
        document.getElementById('challenge-result-title').textContent = 'You failed :(';
        document.getElementById('challenge-result-message').textContent = 'You did not pass the challenge. The point was awarded to your opponent.';
    }

    // Update local game state if provided
    if (resp.game_state) {
        currentGameState = resp.game_state;
        updateGameDisplay();
    }

    // Clear currentChallengeForPlayer so accidental resubmissions are blocked
    currentChallengeForPlayer = null;
}

function continueAfterChallenge() {
    // Hide challenge area and continue
    document.getElementById('challenge-area').classList.add('hidden');
    document.getElementById('challenge-result').classList.add('hidden');
    // If we have latest game state, update display
    if (lastChallengeResponse && lastChallengeResponse.game_state) {
        currentGameState = lastChallengeResponse.game_state;
        updateGameDisplay();
    } else {
        // fallback: fetch game state
        apiCall('get_game_state').then(res => {
            if (!res.error) {
                currentGameState = res;
                updateGameDisplay();
            }
        });
    }
}

function resetChoiceDisplays() {
    document.getElementById('player1-choice').innerHTML = '<div class="choice-emoji">❓</div><div class="choice-text">Waiting...</div>';
    document.getElementById('player2-choice').innerHTML = '<div class="choice-emoji">❓</div><div class="choice-text">Waiting...</div>';
    document.getElementById('result-area').classList.add('hidden');
}

async function nextRound() {
    if (!currentGameState) return;

    // Fetch latest server state to respect server-side round completion
    const serverState = await apiCall('get_game_state');
    if (serverState.error) {
        // fallback to local reset if network issue
        currentGameState.player1.choice_made = false;
        currentGameState.player2.choice_made = false;
        currentGameState.both_choices_made = false;
        updateGameDisplay();
        return;
    }

    currentGameState = serverState;
    // If the server signalled game is no longer active or we've passed max rounds, show final
    if (!currentGameState.game_active) {
        showFinalResults();
        return;
    }

    // Otherwise clear local choice flags and update UI for next round
    currentGameState.player1.choice_made = false;
    currentGameState.player2.choice_made = false;
    currentGameState.both_choices_made = false;
    updateGameDisplay();
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

function showTab(tabId, clickedEl) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    const tab = document.getElementById(tabId);
    if (tab) tab.classList.add('active');

    // Mark the clicked button active if provided
    if (clickedEl && clickedEl.classList) {
        clickedEl.classList.add('active');
    }
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function() {
    showMainMenu();
});