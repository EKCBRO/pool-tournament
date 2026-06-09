#!/usr/bin/env python3
"""
Pool Tournament Launcher
Starts the local web server and opens the app in the default browser
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import threading
import time
import subprocess
import json
import base64
import urllib.parse
from pathlib import Path
from datetime import datetime

PORT = 8000
MAX_PORT_ATTEMPTS = 10

# Set up logging to file
log_file = open('server_log.txt', 'w', encoding='utf-8')

def log(message):
    """Print to console and write to log file"""
    print(message)
    log_file.write(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} - {message}\n")
    log_file.flush()

class PoolTournamentHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler for API endpoints and static files"""
    
    def log_message(self, format, *args):
        pass  # Suppress log messages
    
    def end_headers(self):
        # Add cache control headers to prevent caching
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_POST(self):
        """Handle POST requests for API endpoints"""
        log(f"📨 POST request: {self.path}")
        try:
            if self.path == '/api/register':
                self.handle_register()
            elif self.path == '/api/delete-player':
                self.handle_delete_player()
            elif self.path == '/api/update-stats':
                self.handle_update_stats()
            elif self.path == '/api/import-players':
                self.handle_import_players()
            elif self.path == '/api/create-tournament':
                self.handle_create_tournament()
            elif self.path == '/api/update-tournament':
                self.handle_update_tournament()
            else:
                self.send_error(404, "Endpoint not found")
        except (ConnectionAbortedError, BrokenPipeError):
            # Browser closed connection before we could respond - this is normal, ignore it
            pass
        except Exception as e:
            # Log unexpected errors but don't crash the server
            log(f"⚠️  POST request error (server still running): {e}")
            try:
                self.send_error(500, "Internal server error")
            except:
                pass  # Ignore if we can't send error response
    
    def do_GET(self):
        """Handle GET requests with connection abort protection and streaming for large files"""
        # Log ALL requests to debug crashes
        log(f"📄 GET request: {self.path}")
        try:
            # Call parent class's do_GET to serve static files
            super().do_GET()
        except (ConnectionAbortedError, BrokenPipeError):
            # Browser closed connection - normal, ignore it
            pass
        except Exception as e:
            # Log unexpected errors but don't crash the server
            log(f"⚠️  GET request error (server still running): {e}")
            try:
                self.send_error(500, "Internal server error")
            except:
                pass  # Ignore if we can't send error response
    
    def copyfile(self, source, outputfile):
        """Override copyfile to stream large files in chunks instead of loading into memory"""
        try:
            # Stream in 64KB chunks to handle large audio files
            chunk_size = 65536  # 64KB
            while True:
                chunk = source.read(chunk_size)
                if not chunk:
                    break
                try:
                    outputfile.write(chunk)
                except (ConnectionAbortedError, BrokenPipeError):
                    # Browser closed connection mid-stream - stop sending
                    log(f"⚠️  Connection closed during file streaming")
                    break
        except Exception as e:
            log(f"⚠️  File streaming error: {e}")
            raise
    
    def handle_register(self):
        """Register a new player with photo"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Load existing players
            players = self.load_players()
            
            # Find next ID
            max_id = max([p['id'] for p in players], default=0)
            new_id = max_id + 1
            
            # Save photo if provided
            photo_path = ''
            if data.get('photo'):
                # Create players directory if it doesn't exist
                players_dir = Path('images/players')
                players_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate filename from name
                safe_name = data['name'].lower().replace(' ', '-')
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '-')
                photo_filename = f"{safe_name}-{new_id}.jpg"
                photo_path = f"images/players/{photo_filename}"
                
                # Decode base64 and save
                photo_data = data['photo'].split(',')[1]  # Remove data:image/jpeg;base64,
                photo_bytes = base64.b64decode(photo_data)
                
                with open(photo_path, 'wb') as f:
                    f.write(photo_bytes)
            
            # Create player object
            new_player = {
                'id': new_id,
                'name': data['name'],
                'image': photo_path if photo_path else 'https://via.placeholder.com/280',
                'wins': 0,
                'losses': 0
            }
            
            # Add to players list
            players.append(new_player)
            
            # Save to JSON
            self.save_players(players)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'player': new_player}).encode())
            
        except Exception as e:
            self.send_error(500, f"Registration failed: {str(e)}")
    
    def handle_delete_player(self):
        """Delete a player from the roster"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            player_id = data.get('id')
            
            # Load players
            players = self.load_players()
            
            # Find and remove player
            updated_players = [p for p in players if p['id'] != player_id]
            
            # Save updated list
            self.save_players(updated_players)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True}).encode())
            
        except Exception as e:
            self.send_error(500, f"Delete failed: {str(e)}")
    
    def handle_update_stats(self):
        """Update player win/loss stats"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            winner_id = data.get('winnerId')
            loser_id = data.get('loserId')
            
            log(f"📊 Updating stats: winner={winner_id}, loser={loser_id}")
            
            # Load players
            players = self.load_players()
            
            # Update stats
            for player in players:
                if player['id'] == winner_id:
                    player['wins'] = player.get('wins', 0) + 1
                    log(f"   ✓ Winner {player['name']} now has {player['wins']} wins")
                elif player['id'] == loser_id:
                    player['losses'] = player.get('losses', 0) + 1
                    log(f"   ✓ Loser {player['name']} now has {player['losses']} losses")
            
            # Save updated list
            self.save_players(players)
            log(f"💾 Stats saved successfully")
            
            # Send success response (may fail if browser closed connection)
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
                log(f"✅ Response sent to browser")
            except (ConnectionAbortedError, BrokenPipeError):
                # Browser closed connection - stats are already saved, so this is fine
                log(f"⚠️  Browser closed connection (stats already saved)")
            
        except (ConnectionAbortedError, BrokenPipeError):
            # Browser closed connection before we could even read the request
            log(f"⚠️  Browser closed connection during request")
        except Exception as e:
            log(f"❌ Stats update error: {str(e)}")
            try:
                self.send_error(500, f"Stats update failed: {str(e)}")
            except (ConnectionAbortedError, BrokenPipeError):
                # Can't send error because connection is closed
                pass
    
    def handle_import_players(self):
        """Handle player import from CSV file"""
        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            players = json.loads(post_data.decode('utf-8'))
            
            log(f"📥 Importing {len(players)} players")
            
            # Validate data
            if not isinstance(players, list):
                raise ValueError("Invalid data format")
            
            for player in players:
                if not all(key in player for key in ['id', 'name', 'wins', 'losses', 'image']):
                    raise ValueError("Missing required player fields")
            
            # Save to file
            self.save_players(players)
            log(f"✅ Successfully imported {len(players)} players")
            
            # Send response
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            except (ConnectionAbortedError, BrokenPipeError):
                log(f"⚠️  Browser closed connection (import already saved)")
                
        except (ConnectionAbortedError, BrokenPipeError):
            log(f"⚠️  Browser closed connection during import")
        except Exception as e:
            log(f"❌ Import error: {str(e)}")
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
            except (ConnectionAbortedError, BrokenPipeError):
                pass
    
    def handle_create_tournament(self):
        """Create a new tournament bracket with group stage"""
        try:
            import math
            
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            players = data.get('players', [])
            
            log(f"🏆 Creating tournament with {len(players)} players")
            
            if len(players) < 4:
                raise ValueError("Need at least 4 players for group stage")
            
            # Shuffle players for random seeding
            import random
            random.shuffle(players)
            
            # Create tournament structure
            tournament = {
                'rounds': [],
                'groups': [],
                'champion': None,
                'created': str(datetime.now())
            }
            
            # Divide into groups of 4 (or 3 if needed)
            group_size = 4
            num_groups = max(2, (len(players) + group_size - 1) // group_size)
            
            match_id = 1
            
            # Create groups and round-robin matches
            for group_num in range(num_groups):
                group_start = group_num * group_size
                group_end = min(group_start + group_size, len(players))
                group_players = players[group_start:group_end]
                
                group_matches = []
                
                # Round-robin: each player plays every other player
                for i in range(len(group_players)):
                    for j in range(i + 1, len(group_players)):
                        group_matches.append({
                            'id': match_id,
                            'player1': group_players[i],
                            'player2': group_players[j],
                            'winner': None,
                            'groupNum': group_num
                        })
                        match_id += 1
                
                tournament['groups'].append({
                    'name': f'Group {chr(65 + group_num)}',  # A, B, C, etc.
                    'players': group_players,
                    'matches': group_matches,
                    'standings': []  # Will be calculated as matches complete
                })
            
            # Create knockout rounds (semi-finals and finals)
            # Semi-finals: Top 2 from each of 2 groups (4 players total)
            tournament['rounds'].append({
                'name': 'Semi-Finals',
                'matches': [
                    {'id': match_id, 'player1': None, 'player2': None, 'winner': None},
                    {'id': match_id + 1, 'player1': None, 'player2': None, 'winner': None}
                ]
            })
            match_id += 2
            
            # Finals
            tournament['rounds'].append({
                'name': 'Finals',
                'matches': [
                    {'id': match_id, 'player1': None, 'player2': None, 'winner': None}
                ]
            })
            
            
            # Save tournament
            with open('tournament.json', 'w') as f:
                json.dump(tournament, f, indent=2)
            
            log(f"✅ Tournament created with {num_groups} groups + knockout rounds")
            
            # Send response
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            except (ConnectionAbortedError, BrokenPipeError):
                log(f"⚠️  Browser closed connection (tournament already saved)")
                
        except (ConnectionAbortedError, BrokenPipeError):
            log(f"⚠️  Browser closed connection during tournament creation")
        except Exception as e:
            log(f"❌ Tournament creation error: {str(e)}")
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
            except (ConnectionAbortedError, BrokenPipeError):
                pass
    
    def handle_update_tournament(self):
        """Update tournament with match result"""
        try:
            # Read request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            match_id = data['matchId']
            winner_id = data['winnerId']
            
            log(f"🏆 Updating tournament: Match ID {match_id}, Winner ID {winner_id}")
            
            # Load tournament
            with open('tournament.json', 'r') as f:
                tournament = json.load(f)
            
            # Find the match (could be in groups or knockout rounds)
            match_found = False
            is_group_match = False
            group_index = -1
            
            # Check groups first
            for g_idx, group in enumerate(tournament.get('groups', [])):
                for match in group['matches']:
                    if match['id'] == match_id:
                        # Log before update
                        log(f"   📝 Before update - Match {match_id}: winner={match.get('winner')}")
                        match['winner'] = winner_id
                        match_found = True
                        is_group_match = True
                        group_index = g_idx
                        winner = match['player1'] if match['player1']['id'] == winner_id else match['player2']
                        loser = match['player2'] if match['player1']['id'] == winner_id else match['player1']
                        log(f"   ✓ Group {chr(65 + g_idx)} match {match_id}: {winner['name']} (ID={winner_id}) defeated {loser['name']}")
                        log(f"   📝 After update - Match {match_id}: winner={match['winner']}")
                        break
                if match_found:
                    break
            
            # Check knockout rounds if not found in groups
            if not match_found:
                for round_index, rnd in enumerate(tournament['rounds']):
                    for match in rnd['matches']:
                        if match['id'] == match_id:
                            match['winner'] = winner_id
                            match_found = True
                            winner = match['player1'] if match['player1']['id'] == winner_id else match['player2']
                            
                            # Advance winner to next round
                            if round_index < len(tournament['rounds']) - 1:
                                # Find which match in current round this is
                                match_index = rnd['matches'].index(match)
                                next_round = tournament['rounds'][round_index + 1]
                                next_match_index = match_index // 2
                                next_match = next_round['matches'][next_match_index]
                                
                                # Determine if winner goes to player1 or player2 slot
                                if match_index % 2 == 0:
                                    next_match['player1'] = winner
                                else:
                                    next_match['player2'] = winner
                                    
                                log(f"   ✓ {rnd['name']}: {winner['name']} advanced to {next_round['name']}")
                            else:
                                # Tournament complete!
                                tournament['champion'] = winner
                                log(f"   🏆 CHAMPION: {winner['name']}")
                            break
                    if match_found:
                        break
            
            # If group match, update group standings
            if is_group_match:
                self.update_group_standings(tournament, group_index)
                # Check if group stage is complete and populate semi-finals
                if self.is_group_stage_complete(tournament):
                    self.populate_knockout_from_groups(tournament)
            
            if not match_found:
                raise ValueError(f"Match ID {match_id} not found")
            
            # Save tournament
            with open('tournament.json', 'w') as f:
                json.dump(tournament, f, indent=2)
            
            log(f"✅ Tournament updated")
            
            # Send response
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            except (ConnectionAbortedError, BrokenPipeError):
                log(f"⚠️  Browser closed connection (tournament already updated)")
                
        except (ConnectionAbortedError, BrokenPipeError):
            log(f"⚠️  Browser closed connection during tournament update")
        except Exception as e:
            log(f"❌ Tournament update error: {str(e)}")
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
            except (ConnectionAbortedError, BrokenPipeError):
                pass
    
    def update_group_standings(self, tournament, group_index):
        """Calculate and update standings for a group"""
        group = tournament['groups'][group_index]
        
        # Count wins for each player
        player_records = {}
        for player in group['players']:
            player_records[player['id']] = {'player': player, 'wins': 0, 'losses': 0}
        
        # Tally up results
        for match in group['matches']:
            if match['winner'] is not None:
                winner_id = match['winner']
                loser_id = match['player1']['id'] if match['player2']['id'] == winner_id else match['player2']['id']
                player_records[winner_id]['wins'] += 1
                player_records[loser_id]['losses'] += 1
        
        # Sort by wins (descending)
        standings = sorted(player_records.values(), key=lambda x: x['wins'], reverse=True)
        group['standings'] = standings
        
        log(f"   📊 Group {chr(65 + group_index)} standings updated: " + 
            ', '.join([f"{s['player']['name']} ({s['wins']}-{s['losses']})" for s in standings]))
    
    def is_group_stage_complete(self, tournament):
        """Check if all group stage matches are complete"""
        for group in tournament.get('groups', []):
            for match in group['matches']:
                if match['winner'] is None:
                    return False
        return True
    
    def populate_knockout_from_groups(self, tournament):
        """Move top 2 from each group to semi-finals"""
        if len(tournament.get('groups', [])) < 2:
            return
        
        # Get top 2 from each group
        group_a_top = tournament['groups'][0]['standings'][:2]
        group_b_top = tournament['groups'][1]['standings'][:2]
        
        # Semi-finals: A1 vs B2, B1 vs A2
        semi_finals = tournament['rounds'][0]
        semi_finals['matches'][0]['player1'] = group_a_top[0]['player']
        semi_finals['matches'][0]['player2'] = group_b_top[1]['player']
        semi_finals['matches'][1]['player1'] = group_b_top[0]['player']
        semi_finals['matches'][1]['player2'] = group_a_top[1]['player']
        
        log(f"   🎯 Knockout bracket populated from group standings")
        log(f"      SF1: {group_a_top[0]['player']['name']} vs {group_b_top[1]['player']['name']}")
        log(f"      SF2: {group_b_top[0]['player']['name']} vs {group_a_top[1]['player']['name']}")
    
    def load_players(self):
        """Load players from JSON file"""
        try:
            with open('players.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_players(self, players):
        """Save players to JSON file"""
        with open('players.json', 'w') as f:
            json.dump(players, f, indent=2)

def get_app_directory():
    """Get the directory where the app files are located"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return os.path.dirname(sys.executable)
    else:
        # Running as script
        return os.path.dirname(os.path.abspath(__file__))

def start_server():
    """Start the HTTP server"""
    app_dir = get_app_directory()
    os.chdir(app_dir)
    
    # Try to find an available port
    port = PORT
    httpd = None
    
    for attempt in range(MAX_PORT_ATTEMPTS):
        try:
            httpd = socketserver.TCPServer(("", port), PoolTournamentHandler)
            break  # Success! Port is available
        except OSError as e:
            if e.winerror == 10048:  # Port already in use
                log(f"⚠ Port {port} is in use, trying {port + 1}...")
                port += 1
            else:
                raise  # Different error, re-raise it
    
    if httpd is None:
        log(f"\n❌ ERROR: Could not find an available port.")
        log(f"Please close any other instances of Pool Tournament and try again.")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    log(f"🎱 Pool Tournament App")
    log(f"━" * 50)
    log(f"Server running at: http://localhost:{port}")
    log(f"Opening in your default browser...")
    log(f"\nPress Ctrl+C to stop the server and close the app")
    log(f"━" * 50)
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)
        url = f'http://localhost:{port}/index.html'
        
        # Try multiple methods to open browser (in order of reliability)
        success = False
        
        # Method 1: subprocess with cmd /c start (most reliable on Windows)
        try:
            subprocess.Popen(['cmd', '/c', 'start', url], shell=True)
            success = True
            log(f"✓ Browser opened!")
        except:
            pass
        
        # Method 2: Direct os.system as fallback
        if not success:
            try:
                os.system(f'start {url}')
                success = True
                log(f"✓ Browser opened!")
            except:
                pass
        
        # Method 3: webbrowser module as last resort
        if not success:
            try:
                webbrowser.open(url)
                success = True
                log(f"✓ Browser opened!")
            except:
                pass
        
        if not success:
            log(f"⚠ Could not auto-open browser")
            log(f"\nPlease manually open your browser and go to:")
            log(f"{url}")
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        log("🚀 Server ready and listening for requests...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        log("\n\n👋 Shutting down Pool Tournament App...")
        log("Thanks for playing!")
    except Exception as e:
        log(f"\n\n💥 FATAL ERROR: Server crashed!")
        log(f"Error: {e}")
        import traceback
        log(traceback.format_exc())
    finally:
        log_file.close()

if __name__ == "__main__":
    try:
        start_server()
    except Exception as e:
        log(f"\n\n💥 STARTUP FAILED!")
        log(f"Error: {e}")
        import traceback
        log(traceback.format_exc())
        log_file.close()
        input("\nPress Enter to exit...")
        sys.exit(1)

