from pathlib import Path
import sys
import os


def get_project_root() -> Path:
	"""Get the project root directory, works for both dev and frozen (EXE) mode"""
	if getattr(sys, 'frozen', False):
		# Running as compiled EXE - use the EXE's directory
		return Path(sys.executable).parent
	else:
		# Running in development - use the project root
		return Path(__file__).resolve().parents[2]


def get_data_dir() -> Path:
	"""Get data directory - creates it next to EXE if it doesn't exist"""
	data = get_project_root() / "data"
	data.mkdir(parents=True, exist_ok=True)
	return data


def get_high_scores_path() -> Path:
	return get_data_dir() / "highscores.json"


def get_assets_dir() -> Path:
	"""Get assets directory - for frozen apps, use bundled resources"""
	if getattr(sys, 'frozen', False):
		# Running as EXE - use the bundled assets
		# PyInstaller extracts to sys._MEIPASS
		if hasattr(sys, '_MEIPASS'):
			return Path(sys._MEIPASS) / "assets"
	# Running in development or fallback
	assets = get_project_root() / "assets"
	(assets / "images").mkdir(parents=True, exist_ok=True)
	return assets
