from __future__ import annotations
from pathlib import Path
from typing import Optional
import tkinter as tk
try:
	from ..config.paths import get_assets_dir
except ImportError:
	# Allow running this module directly
	import sys
	from pathlib import Path as _P
	sys.path.append(str(_P(__file__).resolve().parents[2]))
	from app.config.paths import get_assets_dir


def load_icon(filename: str) -> Optional[tk.PhotoImage]:
	"""Load PNG from assets/images, return None on failure.
	Keeps a reference by returning the PhotoImage to caller.
	"""
	try:
		path = get_assets_dir() / "images" / filename
		if not path.exists():
			return None
		return tk.PhotoImage(file=str(path))
	except Exception:
		return None
