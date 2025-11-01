from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Optional


def read_json(path: Path) -> Optional[Any]:
	try:
		if not path.exists():
			return None
		with path.open("r", encoding="utf-8") as f:
			return json.load(f)
	except Exception:
		return None


def write_json(path: Path, data: Any) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
