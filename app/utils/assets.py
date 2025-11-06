from __future__ import annotations
from pathlib import Path
from typing import Optional
try:
	from ..config.paths import get_assets_dir
except ImportError:
	# Allow running this module directly
	import sys
	from pathlib import Path as _P
	sys.path.append(str(_P(__file__).resolve().parents[2]))
	from app.config.paths import get_assets_dir


def resolve_image_path(filename: str) -> Optional[str]:
	"""Return full path to an image file under assets/images if it exists."""
	path = get_assets_dir() / "images" / filename
	return str(path) if path.exists() else None


def first_existing_image(*filenames: str) -> Optional[str]:
	"""Return the first existing image path from provided filenames."""
	for name in filenames:
		p = resolve_image_path(name)
		if p:
			return p
	return None