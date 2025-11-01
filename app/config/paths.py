from pathlib import Path


def get_project_root() -> Path:
	return Path(__file__).resolve().parents[2]


def get_data_dir() -> Path:
	data = get_project_root() / "data"
	data.mkdir(parents=True, exist_ok=True)
	return data


def get_high_scores_path() -> Path:
	return get_data_dir() / "highscores.json"


def get_assets_dir() -> Path:
	assets = get_project_root() / "assets"
	(assets / "images").mkdir(parents=True, exist_ok=True)
	return assets
