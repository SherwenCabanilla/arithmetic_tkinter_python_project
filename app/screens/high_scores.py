import tkinter as tk
from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import IconRoundButton, BackCircleButton
from ..ui import theme
from ..services.high_score_service import HighScoreService


class HighScoresScreen(MobileFrame):
	def __init__(self, master: tk.Misc, navigator) -> None:
		super().__init__(master)
		self.navigator = navigator
		self.service = HighScoreService()

		BackCircleButton(self, command=lambda: self.navigator.show("home")).pack(anchor=tk.W, padx=16, pady=(16, 8))

		title = tk.Label(self, text="High Score History", bg=theme.BG, fg="#E65100", font=("Segoe UI", 20, "bold"))
		title.pack(pady=(0, 12))

		self._container = tk.Frame(self, bg=theme.BG)
		self._container.pack(fill=tk.BOTH, expand=True)

		self._render_modes()

	def tkraise(self):
		"""Override to refresh when screen is shown."""
		super().tkraise()
		self._render_modes()

	def _render_modes(self) -> None:
		for child in list(self._container.children.values()):
			child.destroy()
		modes = self.service.get_overview()
		for mode, info in modes.items():
			best = info.get("best")
			label = f"{mode.title()} — {best['score']}/{best['total']}" if best else f"{mode.title()} — None"
			IconRoundButton(self._container, text=label, bg_color="#11B3D9", hover_color="#1AC2EA", command=lambda m=mode: self._open_mode(m)).pack(pady=8)

	def _open_mode(self, mode: str) -> None:
		from .mode_logs import ModeLogsScreen
		screen_name = f"mode_logs_{mode}"
		# Destroy old instance if it exists to reset state
		if screen_name in self.navigator._screens:
			self.navigator._screens[screen_name].destroy()
			del self.navigator._screens[screen_name]
		self.navigator.register_screen(screen_name, lambda master, nav: ModeLogsScreen(master, nav, mode))
		self.navigator.show(screen_name)
