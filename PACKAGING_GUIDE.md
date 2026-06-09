# Pool Tournament App - Packaging Instructions

## Creating a Standalone .exe File

Follow these steps to create a single executable file that anyone can run without installing Python.

### Prerequisites

1. Make sure Python is installed on your computer
2. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

### Step 1: Test the Launcher

Before packaging, test that the launcher works:

```
python launch_pool_tournament.py
```

This should:
- Start the web server
- Open your default browser to the Pool Tournament app
- Press Ctrl+C to stop when done testing

### Step 2: Create the Executable

Run this command in the `pool` folder:

```
pyinstaller --onefile --noconsole --icon=NONE --name="Pool Tournament" launch_pool_tournament.py
```

**Command breakdown:**
- `--onefile` - Creates a single .exe file (not a folder)
- `--noconsole` - No black command window (cleaner)
- `--name="Pool Tournament"` - Names the .exe file
- If you have an icon file (.ico), replace `NONE` with the path to it

**Alternative (with console window for debugging):**
```
pyinstaller --onefile --name="Pool Tournament" launch_pool_tournament.py
```

### Step 3: Package Everything

After PyInstaller finishes, you'll have:
- `dist/Pool Tournament.exe` - Your executable file

**To distribute to others, create a folder with:**
```
Pool Tournament/
├── Pool Tournament.exe
├── index.html
├── matchup.html
├── register.html
├── players.html
├── matchup.js
├── register.js
├── players.json
└── images/
    ├── table.jpg
    └── (all pool ball images)
```

**Important:** The .exe must be in the same folder as the HTML/JS files!

### Step 4: Share

Zip the entire "Pool Tournament" folder and share it. Users just:
1. Extract the zip file
2. Double-click `Pool Tournament.exe`
3. App opens in their browser automatically!

### Troubleshooting

**If PyInstaller is not installed:**
```
pip install pyinstaller
```

**If the .exe doesn't work:**
- Try the version WITH console window to see error messages
- Make sure all HTML/JS/image files are in the same folder as the .exe
- Check that port 8000 isn't already in use

**If you get a Windows Defender warning:**
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- To avoid this, you'd need to sign the executable (costs money)

### File Size

The final .exe will be approximately:
- **10-20 MB** (includes Python runtime)
- Plus your HTML/JS/image files (~5-10 MB)
- **Total package: ~15-30 MB**

---

## Alternative: Simple Batch File (No .exe needed)

If you don't want to create an .exe, you can create a simple batch file:

**run_pool_tournament.bat:**
```batch
@echo off
echo Starting Pool Tournament App...
start http://localhost:8000/index.html
python launch_pool_tournament.py
```

Users need Python installed, but it's simpler and no packaging required.
