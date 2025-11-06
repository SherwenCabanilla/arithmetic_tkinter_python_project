# Building LearnBright Math to EXE

## Quick Start

### 1. Install Required Packages
```bash
pip install pyinstaller pillow
```

### 2. Create the Icon (One Time Only)
Convert your logo to ICO format:
```bash
python convert_icon.py
```
This creates `assets/images/logo.ico` which will be your EXE icon.

**Alternative:** If you prefer, use an online converter:
- Go to https://convertio.co/png-ico/
- Upload `assets/images/logo.png`
- Download as `logo.ico` and save to `assets/images/`

### 3. Build the EXE
From your project root (`D:\python_app`), run:
```bash
pyinstaller learnbright.spec
```

### 3. Find Your EXE
Your executable will be created at:
```
dist/LearnBright Math.exe
```

## What Gets Included:
- ✅ All Python code
- ✅ All images in `assets/`
- ✅ Initial `highscores.json` file
- ✅ All `.kv` layout files

## How Data Works:
- The JSON file (`highscores.json`) will be saved in the same directory as the EXE
- When users play quizzes, their scores are saved to this JSON file
- Data persists between sessions - just don't delete the JSON file!

## Distribution:
You can share the entire `dist/` folder with users, or just the EXE file (it's a single standalone executable).

## Notes:
- First build takes a few minutes
- The EXE is ~50-100MB (includes Python + Kivy)
- No Python installation needed on user's computer
- Works on Windows 7, 8, 10, 11

## Troubleshooting:
If the build fails, try:
```bash
# Clean previous builds
rmdir /s /q build dist
del /f LearnBright*.spec

# Rebuild
pyinstaller learnbright.spec
```

## Testing:
After building, test the EXE by:
1. Running `dist/LearnBright Math.exe`
2. Playing a quiz and checking if scores save
3. Closing and reopening to verify data persists

