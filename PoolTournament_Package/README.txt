# Pool Tournament App

🎱 **A simple, elegant pool tournament tracker**

## Features
- Track player matchups
- Register new players with photo upload (camera or file)
- Automatic win/loss tracking
- Player roster with statistics
- Beautiful animated pool table interface

## How to Use

### Starting the App - METHOD 1 (Recommended)
1. **Double-click `START_HERE.bat`**
2. A command window will appear showing the server URL
3. Your browser should open automatically
4. If it doesn't, manually open your browser and go to: http://localhost:8000/index.html

### Starting the App - METHOD 2 (Direct exe)
1. **Double-click `PoolTournament.exe`**
2. A command window will appear
3. Copy the URL (http://localhost:8000/index.html) and paste it in your browser if it doesn't open automatically

### IMPORTANT
- **Only run ONE instance at a time** - if you see a port conflict error, close any other running instances
- The app will automatically try ports 8000-8010 if the default port is in use
- Keep the command window open while using the app
- Press Ctrl+C in the command window to stop the server

### Using the App
- **Play** - Select two players for a match, click the winner's photo
- **Register** - Add new players with their photos
- **List Players** - View all players and their win/loss records

### Stopping the App
- Press **Ctrl+C** in the terminal window, or just close it

## Data Storage

✅ **OneDrive Compatible!** All data is stored as files that sync automatically.

**What's Saved:**
- Player roster → players.json (can be edited manually)
- Player photos → images/players/ folder
- Win/loss statistics → saved in players.json

**How OneDrive Sync Works:**
1. Put this folder in OneDrive
2. Run the app on Computer A, register players, track games
3. Close the app (Ctrl+C)
4. Open it on Computer B - everything is there!

**No browser localStorage** - everything is in files that sync via OneDrive/USB/network drives.

**Manual Editing:**
- You can edit players.json with any text editor
- Add player photos to images/players/ as .jpg files
- Reference them like: "image": "images/players/john.jpg"

## System Requirements
- Windows 7 or later
- Any modern web browser (Chrome, Firefox, Edge, etc.)
- No installation required!

## Troubleshooting

**App won't start?**
- Make sure port 8000 isn't being used by another program
- Try restarting your computer

**Can't see images?**
- Make sure the `images` folder is in the same location as the .exe

**Lost your data?**
- Don't clear your browser's cache/localStorage
- Use the Export feature regularly to backup

---

**Made with ❤️ for pool enthusiasts**
