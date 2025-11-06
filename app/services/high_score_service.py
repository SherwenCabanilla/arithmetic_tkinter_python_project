from __future__ import annotations
from typing import List, Dict, Any
from datetime import datetime
from ..config.paths import get_high_scores_path
from ..utils.json_store import read_json, write_json


DEFAULT_MODES = ["addition", "subtraction", "multiplication", "division", "mix"]


class HighScoreService:
	def __init__(self) -> None:
		self.path = get_high_scores_path()
		data = read_json(self.path)
		if not isinstance(data, dict):
			data = {"modes": {m: {"best": None} for m in DEFAULT_MODES}}
		else:
			# migrate: remove attempts, keep only best
			for m in DEFAULT_MODES:
				mode_obj = data.get("modes", {}).get(m)
				if mode_obj:
					if "attempts" in mode_obj:
						del mode_obj["attempts"]
					if isinstance(mode_obj.get("best"), dict) and "questions" not in mode_obj["best"]:
						mode_obj["best"]["questions"] = []
		write_json(self.path, data)
		self._cache = data

	def _save(self) -> None:
		write_json(self.path, self._cache)

	def record_attempt(self, mode: str, score: int, total: int, questions: List[Dict[str, Any]]) -> bool:
		"""Record a quiz attempt. Returns True if it's a new high score, False otherwise."""
		if mode not in self._cache["modes"]:
			self._cache["modes"][mode] = {"best": None}
		best = self._cache["modes"][mode]["best"]
		# Only save if it's a new high score
		is_new_high_score = best is None or score > best.get("score", 0)
		if is_new_high_score:
			self._cache["modes"][mode]["best"] = {
				"score": int(score),
				"total": int(total),
				"timestamp": datetime.now().isoformat(),
				"questions": questions,
			}
			self._save()
		return is_new_high_score

	def get_best(self, mode: str) -> Dict | None:
		self.refresh()  # Always get fresh data
		return (self._cache.get("modes", {}).get(mode) or {}).get("best")

	def get_attempts(self, mode: str) -> List[Dict]:
		# Keep method for compatibility, but return empty list since we only store best
		return []

	def refresh(self) -> None:
		"""Reload data from disk to get latest scores."""
		data = read_json(self.path)
		if isinstance(data, dict):
			self._cache = data

	def get_overview(self) -> Dict[str, Dict]:
		self.refresh()  # Always get fresh data
		return self._cache.get("modes", {})
