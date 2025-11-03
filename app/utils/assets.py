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


def load_icon_max_width(filename: str, max_width: int) -> Optional[tk.PhotoImage]:
	"""Load PNG and scale it down (integer subsample) if wider than max_width.

	This avoids requiring Pillow, using Tk's built-in subsample. The result keeps
	its own reference just like load_icon.
	"""
	img = load_icon(filename)
	if img is None:
		return None
	try:
		w = img.width()
		if w > max_width and max_width > 0:
			# Ceil division to compute integer downscale factor
			factor = (w + max_width - 1) // max_width
			img = img.subsample(factor, factor)
		return img
	except Exception:
		return img