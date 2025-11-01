# Learn Bright (Python Tkinter)

A minimal, mobile-style arithmetic learning app scaffold built with Python and Tkinter. Includes screens for Learn and Watch, Start Quiz, View High Score, and Exit. High scores are stored in a local JSON file.

## Quick Start

```bash
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python -m app
```

## Project Structure

```
app/
  __init__.py
  main.py                 # Entrypoint (python -m app)
  config/
    __init__.py
    paths.py              # App paths, data locations
  core/
    __init__.py
    navigation.py         # Simple screen navigator/controller
  models/
    __init__.py
    high_score.py         # Data model(s)
  screens/
    __init__.py
    home.py               # Home with 4 buttons
    learn.py
    quiz.py
    high_scores.py
  services/
    __init__.py
    high_score_service.py # JSON-backed storage
  ui/
    __init__.py
    theme.py              # Colors, sizing, typography
    widgets/
      __init__.py
      buttons.py          # Reusable primary button
      containers.py       # Frame helpers, scroll container
  utils/
    __init__.py
    json_store.py         # JSON read/write helpers (atomic-ish)
assets/
  images/                 # Logos/icons (optional)
  fonts/                  # Optional custom fonts
data/
  highscores.json         # JSON store (created/seeded on first run)
requirements.txt
README.md
```

## Notes

- This scaffold prefers simple modules over frameworks for clarity.
- The window is sized to resemble a mobile phone (portrait) for desktop.
- JSON storage is local-only and not concurrency-safe across processes.

## Next Steps

- Implement actual learning content and quiz logic.
- Replace placeholder UI with your designs and assets.
- Extend `high_score_service.py` to keep top-N, timestamps, player names, etc.
