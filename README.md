# Learn Bright (Kivy)

This project has been migrated to Kivy for mobile-friendly UI and packaging.

## Requirements
- Python 3.10+
- Kivy

Install Kivy on Windows (PowerShell):

```powershell
python -m pip install --upgrade pip
python -m pip install kivy[base] kivy_examples
```

## Run locally

```powershell
python -m app.main
```

## Assets
Put images under `assets/images/`. The app icon is expected at `assets/images/learnbright.png` (optional).

## Mobile builds
- Android: use Buildozer on WSL/Linux. See Kivy docs: `https://kivy.org/doc/stable/guide/packaging-android.html`.
- iOS: Xcode + kivy-ios. See docs: `https://kivy.org/doc/stable/guide/packaging-ios.html`.
