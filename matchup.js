// Player database
let playersData = [];

// Current matchup player IDs
let currentPlayer1Id = null;
let currentPlayer2Id = null;

// Lazy audio loading - only load sounds when first needed
let cachedFanfareSound = null;
let cachedFaceoffSound = null;

function getFanfareSound() {
    if (!cachedFanfareSound) {
        cachedFanfareSound = new Audio('sounds/fanfare.wav');
    }
    return cachedFanfareSound;
}

function getFaceoffSound() {
    if (!cachedFaceoffSound) {
        cachedFaceoffSound = new Audio('sounds/faceoff.wav');
    }
    return cachedFaceoffSound;
}

// Load player data from JSON file
async function loadPlayerData() {
    console.log('🔄 Loading player data...');
    try {
        const response = await fetch('players.json?t=' + Date.now());
        console.log('✅ Players.json fetched');
        playersData = await response.json();
        console.log(`📊 Loaded ${playersData.length} players`);
        
        // Check for tournament match parameters
        const urlParams = new URLSearchParams(window.location.search);
        const isTournament = urlParams.get('tournament');
        const p1Id = parseInt(urlParams.get('p1'));
        const p2Id = parseInt(urlParams.get('p2'));
        
        console.log('🏆 Tournament check:', { isTournament, p1Id, p2Id });
        
        if (isTournament && p1Id && p2Id) {
            // Set tournament players
            currentPlayer1Id = p1Id;
            currentPlayer2Id = p2Id;
            console.log('🎯 Setting tournament players:', { p1Id, p2Id });
            
            updateMatchup();
            
            // Start balls breaking and play faceoff sound together after short delay
            setTimeout(() => {
                // Trigger ball break
                if (window.startBallBreak) {
                    window.startBallBreak();
                }
                
                // Play faceoff sound
                const faceoff = getFaceoffSound();
                if (faceoff) {
                    faceoff.currentTime = 0;
                    faceoff.play().catch(e => console.log('Audio play failed:', e));
                    console.log('🎵 Playing faceoff sound with ball break');
                }
            }, 300);
            
            console.log('✅ Tournament match loaded:', { p1Id, p2Id });
        } else {
            // Default to first two players if available
            if (playersData.length >= 2) {
                currentPlayer1Id = playersData[0].id;
                currentPlayer2Id = playersData[1].id;
                console.log('📍 Loading default matchup');
                updateMatchup();
            }
        }
    } catch (error) {
        console.error('❌ Error loading player data:', error);
        const errorElement = document.getElementById('errorMessage');
        if (errorElement) {
            errorElement.textContent = 'Error loading player data!';
        }
    }
}

// Find player by ID
function getPlayerById(id) {
    return playersData.find(player => player.id === parseInt(id));
}

// Adjust font size based on name length
function adjustNameFontSize(nameElement) {
    const name = nameElement.textContent;
    const length = name.length;
    
    if (length <= 12) {
        nameElement.style.fontSize = '48px';
    } else if (length <= 16) {
        nameElement.style.fontSize = '40px';
    } else if (length <= 20) {
        nameElement.style.fontSize = '32px';
    } else if (length <= 25) {
        nameElement.style.fontSize = '28px';
    } else {
        nameElement.style.fontSize = '24px';
    }
}

// Update the matchup display
function updateMatchup() {
    const errorMessage = document.getElementById('errorMessage');
    
    // Check if we have player IDs set
    if (!currentPlayer1Id || !currentPlayer2Id) {
        if (errorMessage) errorMessage.textContent = 'No players selected';
        return;
    }
    
    if (errorMessage) errorMessage.textContent = '';

    const player1 = getPlayerById(currentPlayer1Id);
    const player2 = getPlayerById(currentPlayer2Id);

    if (!player1) {
        if (errorMessage) errorMessage.textContent = `Player ${currentPlayer1Id} not found!`;
        return;
    }

    if (!player2) {
        if (errorMessage) errorMessage.textContent = `Player ${currentPlayer2Id} not found!`;
        return;
    }

    if (currentPlayer1Id === currentPlayer2Id) {
        if (errorMessage) errorMessage.textContent = 'Players must be different!';
        return;
    }

    // Update Player 1
    const player1NameElement = document.getElementById('player1Name');
    player1NameElement.textContent = player1.name;
    adjustNameFontSize(player1NameElement);
    const player1Img = document.getElementById('player1Image');
    player1Img.src = player1.image || 'https://via.placeholder.com/280';
    player1Img.alt = player1.name;

    // Update Player 2
    const player2NameElement = document.getElementById('player2Name');
    player2NameElement.textContent = player2.name;
    adjustNameFontSize(player2NameElement);
    const player2Img = document.getElementById('player2Image');
    player2Img.src = player2.image || 'https://via.placeholder.com/280';
    player2Img.alt = player2.name;

    // Trigger animation
    document.getElementById('matchupDisplay').style.animation = 'none';
    setTimeout(() => {
        document.getElementById('matchupDisplay').style.animation = '';
    }, 10);
}

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPlayerData();
    initBallPhysics();
});

// Reload player data when page becomes visible (e.g., after deleting players)
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        loadPlayerData();
    }
});

// Reload player data when navigating back to this page
window.addEventListener('pageshow', (event) => {
    if (event.persisted) {
        loadPlayerData();
    }
});

// Update player stats (wins and losses)
async function updatePlayerStats(winnerId, loserId) {
    // Find winner and loser in playersData
    const winner = playersData.find(p => p.id === winnerId);
    const loser = playersData.find(p => p.id === loserId);
    
    if (!winner || !loser) {
        console.error('Could not find players to update stats');
        return;
    }
    
    // Increment stats locally for immediate UI update
    winner.wins = (winner.wins || 0) + 1;
    loser.losses = (loser.losses || 0) + 1;
    
    console.log(`Updated stats: ${winner.name} now has ${winner.wins} wins, ${loser.name} now has ${loser.losses} losses`);
    
    // Send update to server
    try {
        const response = await fetch('/api/update-stats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                winnerId: winnerId,
                loserId: loserId
            })
        });
        
        if (!response.ok) {
            console.error('Failed to update stats on server');
        } else {
            console.log('✅ Stats saved to server');
        }
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Toggle winner display
let statsUpdateInProgress = false;

window.toggleWinner = function(playerNum) {
    console.log('toggleWinner called for player', playerNum);
    const body = document.body;
    const vsText = document.getElementById('vsText');
    const player1Div = document.getElementById('player1');
    const player2Div = document.getElementById('player2');
    const winnerText = document.getElementById('winnerText');
    const sparkles = document.querySelectorAll('.sparkle');
    
    console.log('Winner text element:', winnerText);
    console.log('Current body classes:', body.className);
    console.log('Has winner-mode:', body.classList.contains('winner-mode'));
    
    if (body.classList.contains('winner-mode')) {
        // Prevent reset if stats update is in progress
        if (statsUpdateInProgress) {
            console.log('⏳ Waiting for stats to save...');
            return;
        }
        
        // Stop all audio before resetting
        if (cachedFanfareSound) {
            cachedFanfareSound.pause();
            cachedFanfareSound.currentTime = 0;
        }
        if (cachedFaceoffSound) {
            cachedFaceoffSound.pause();
            cachedFaceoffSound.currentTime = 0;
        }
        
        // Reset to normal mode
        console.log('Resetting to normal mode');
        body.classList.remove('winner-mode');
        player1Div.classList.remove('hidden');
        player2Div.classList.remove('hidden');
        player1Div.style.display = '';
        player2Div.style.display = '';
        vsText.style.display = 'block';
        winnerText.style.display = 'none';
    } else if (playerNum === 1 || playerNum === 2) {
        // Show winner and update stats - only if valid player number
        console.log('Showing player', playerNum, 'as winner');
        
        // Play fanfare sound (only if not already playing)
        const fanfare = getFanfareSound();
        if (fanfare && fanfare.paused) {
            fanfare.currentTime = 0;
            fanfare.play().catch(e => console.log('Audio play failed:', e));
        }
        
        // Get current player IDs from our stored variables
        const winnerId = playerNum === 1 ? currentPlayer1Id : currentPlayer2Id;
        const loserId = playerNum === 1 ? currentPlayer2Id : currentPlayer1Id;
        
        // Mark stats update in progress
        statsUpdateInProgress = true;
        
        // Failsafe: ALWAYS clear the flag after 10 seconds max (even if something goes wrong)
        // Needs to be longer than stats + tournament update + fanfare wait time
        const failsafeTimer = setTimeout(() => {
            if (statsUpdateInProgress) {
                console.warn('⚠️ Failsafe: Clearing stats lock after timeout');
                statsUpdateInProgress = false;
            }
        }, 10000);
        
        // Update wins and losses (fire and forget - has timeout protection)
        updatePlayerStats(winnerId, loserId)
            .catch(err => {
                console.error('Stats update error:', err);
            })
            .finally(() => {
                // Check if this is a tournament match
                const tournamentMatch = sessionStorage.getItem('tournamentMatch');
                
                if (tournamentMatch) {
                    const matchData = JSON.parse(tournamentMatch);
                    console.log('🏆 Tournament match - updating bracket');
                    
                    // Update tournament bracket
                    fetch('/api/update-tournament', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            matchId: matchData.matchId,
                            winnerId: winnerId
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        clearTimeout(failsafeTimer);
                        
                        if (data.success) {
                            // Clear tournament match data
                            sessionStorage.removeItem('tournamentMatch');
                            
                            // Get fanfare info for logging
                            const fanfare = getFanfareSound();
                            console.log('🎺 Fanfare info:', {
                                duration: fanfare.duration,
                                currentTime: fanfare.currentTime,
                                paused: fanfare.paused
                            });
                            
                            // Wait 8 seconds for fanfare to finish completely before redirecting
                            console.log('⏰ Waiting 8 seconds for fanfare to complete...');
                            setTimeout(() => {
                                statsUpdateInProgress = false; // Clear flag right before redirect
                                console.log('🔄 Redirecting to tournament page');
                                // Use location.replace to prevent caching and force reload
                                window.location.replace('tournament.html?refresh=' + Date.now());
                            }, 8000);
                        } else {
                            statsUpdateInProgress = false;
                            console.error('Tournament update failed:', data.error);
                            alert('Error updating tournament bracket');
                        }
                    })
                    .catch(error => {
                        statsUpdateInProgress = false;
                        clearTimeout(failsafeTimer);
                        console.error('Tournament update error:', error);
                        alert('Error updating tournament bracket');
                    });
                } else {
                    // Not a tournament match - normal behavior
                    setTimeout(() => {
                        statsUpdateInProgress = false;
                        clearTimeout(failsafeTimer); // Cancel failsafe since we completed normally
                        console.log('✅ Stats update complete, ready for next match');
                    }, 500);
                }
            });
        
        body.classList.add('winner-mode');
        if (playerNum === 1) {
            player2Div.classList.add('hidden');
            player2Div.style.display = 'none';
            player1Div.classList.remove('hidden');
            player1Div.style.display = 'flex';
            console.log('Hiding player 2, showing player 1');
        } else {
            player1Div.classList.add('hidden');
            player1Div.style.display = 'none';
            player2Div.classList.remove('hidden');
            player2Div.style.display = 'flex';
            console.log('Hiding player 1, showing player 2');
        }
        vsText.style.display = 'none';
        winnerText.style.display = 'block';
    } else {
        // Invalid playerNum - just log and ignore
        console.warn('toggleWinner called with invalid playerNum:', playerNum);
        return;
    }
    
    console.log('After toggle - body classes:', body.className);
    console.log('Player1 classes:', player1Div.className, 'display:', player1Div.style.display);
    console.log('Player2 classes:', player2Div.className, 'display:', player2Div.style.display);
    console.log('Winner text display:', winnerText.style.display);
};

// Ball physics with collision detection
function initBallPhysics() {
    const balls = document.querySelectorAll('.pool-ball');
    const ballData = [];
    const speed = 2; // Constant speed
    const ballSize = 53; // All balls are same size
    const border = ballSize; // Border width equal to ball size
    let isAnimating = false;
    
    // Triangle rack starting positions (8 balls)
    // Center the rack on screen
    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;
    const spacing = ballSize + 5; // Small gap between balls
    
    // Triangle formation for 8 balls (3 rows: 3, 2, 2, 1)
    const rackPositions = [
        // Row 1 (3 balls)
        { x: centerX - spacing, y: centerY - spacing * 1.5 },
        { x: centerX, y: centerY - spacing * 1.5 },
        { x: centerX + spacing, y: centerY - spacing * 1.5 },
        // Row 2 (2 balls)
        { x: centerX - spacing / 2, y: centerY - spacing * 0.5 },
        { x: centerX + spacing / 2, y: centerY - spacing * 0.5 },
        // Row 3 (2 balls)
        { x: centerX - spacing / 2, y: centerY + spacing * 0.5 },
        { x: centerX + spacing / 2, y: centerY + spacing * 0.5 },
        // Row 4 (1 ball - apex)
        { x: centerX, y: centerY + spacing * 1.5 }
    ];
    
    // Initialize ball positions (velocities added later when break starts)
    balls.forEach((ball, index) => {
        const pos = rackPositions[index] || { x: centerX, y: centerY };
        ballData.push({
            element: ball,
            x: pos.x - ballSize / 2,
            y: pos.y - ballSize / 2,
            vx: 0, // Start stationary
            vy: 0, // Start stationary
            radius: ballSize / 2,
            speed: speed,
            rotation: 0
        });
        
        // Set initial position
        ball.style.left = (pos.x - ballSize / 2) + 'px';
        ball.style.top = (pos.y - ballSize / 2) + 'px';
    });
    
    function animate() {
        if (!isAnimating) return;
        
        ballData.forEach((ball, i) => {
            // Update position
            ball.x += ball.vx;
            ball.y += ball.vy;
            
            // Bounce off walls with border
            if (ball.x <= border || ball.x >= window.innerWidth - ballSize - border) {
                ball.vx *= -1;
                ball.x = ball.x <= border ? border : window.innerWidth - ballSize - border;
            }
            if (ball.y <= border || ball.y >= window.innerHeight - ballSize - border) {
                ball.vy *= -1;
                ball.y = ball.y <= border ? border : window.innerHeight - ballSize - border;
            }
            
            // Check collision with other balls
            for (let j = i + 1; j < ballData.length; j++) {
                const other = ballData[j];
                const dx = other.x - ball.x;
                const dy = other.y - ball.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                const minDist = ball.radius + other.radius;
                
                if (distance < minDist) {
                    // Collision detected! Calculate new velocities
                    const angle = Math.atan2(dy, dx);
                    const sin = Math.sin(angle);
                    const cos = Math.cos(angle);
                    
                    // Rotate velocities
                    const vx1 = ball.vx * cos + ball.vy * sin;
                    const vy1 = ball.vy * cos - ball.vx * sin;
                    const vx2 = other.vx * cos + other.vy * sin;
                    const vy2 = other.vy * cos - other.vx * sin;
                    
                    // Swap velocities (elastic collision)
                    const temp = vx1;
                    ball.vx = vx2 * cos - vy1 * sin;
                    ball.vy = vy1 * cos + vx2 * sin;
                    other.vx = temp * cos - vy2 * sin;
                    other.vy = vy2 * cos + temp * sin;
                    
                    // Separate balls
                    const overlap = minDist - distance;
                    const moveX = overlap * cos * 0.5;
                    const moveY = overlap * sin * 0.5;
                    ball.x -= moveX;
                    ball.y -= moveY;
                    other.x += moveX;
                    other.y += moveY;
                }
            }
            
            // Normalize velocity to maintain constant speed
            const currentSpeed = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
            if (currentSpeed > 0) {
                ball.vx = (ball.vx / currentSpeed) * ball.speed;
                ball.vy = (ball.vy / currentSpeed) * ball.speed;
            }
            
            // Update rotation
            ball.rotation += 2;
            
            // Update DOM
            ball.element.style.left = ball.x + 'px';
            ball.element.style.top = ball.y + 'px';
            ball.element.style.transform = `rotate(${ball.rotation}deg)`;
        });
        
        requestAnimationFrame(animate);
    }
    
    // Function to start the ball break (exposed globally)
    window.startBallBreak = function() {
        if (isAnimating) return; // Already started
        
        // Give each ball a random velocity
        ballData.forEach(ball => {
            const angle = Math.random() * Math.PI * 2;
            ball.vx = Math.cos(angle) * speed;
            ball.vy = Math.sin(angle) * speed;
        });
        
        isAnimating = true;
        animate();
        console.log('🎱 Ball break started!');
    };
    
    // Check if this is a tournament match - if not, start immediately
    const urlParams = new URLSearchParams(window.location.search);
    const isTournament = urlParams.get('tournament');
    
    if (!isTournament) {
        // For non-tournament matches, start immediately
        window.startBallBreak();
    }
}

// Stop all audio when navigating away
document.addEventListener('DOMContentLoaded', function() {
    const homeLinks = document.querySelectorAll('a[href="index.html"]');
    homeLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Stop all audio immediately
            if (cachedFanfareSound) {
                cachedFanfareSound.pause();
                cachedFanfareSound.currentTime = 0;
            }
            if (cachedFaceoffSound) {
                cachedFaceoffSound.pause();
                cachedFaceoffSound.currentTime = 0;
            }
        });
    });
});
