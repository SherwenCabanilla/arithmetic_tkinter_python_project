import tkinter as tk
from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import PrimaryButton, IconRoundButton
from ..ui import theme
from ..utils.assets import load_icon


class HomeScreen(MobileFrame):
	def __init__(self, master: tk.Misc, navigator) -> None:
		super().__init__(master)
		self.navigator = navigator

		# Keep references to icons to avoid garbage collection
		self._icons = {
			"play": load_icon("play.png"),
			"quiz": load_icon("brain.png"),
			"chart": load_icon("chart.png"),
			"exit": load_icon("exit.png"),
		}

		title = tk.Label(self, text="Learn\nBRIGHT", bg=theme.BG, fg=theme.TEXT, font=("Segoe UI", 28, "bold"))
		title.pack(pady=(40, 24))

		IconRoundButton(self, text="Learn and Watch", icon=self._icons["play"], command=self._go_learn).pack(pady=12)
		IconRoundButton(self, text="Start Quiz", icon=self._icons["quiz"], command=self._go_quiz).pack(pady=12)
		IconRoundButton(self, text="View High Score", icon=self._icons["chart"], command=self._go_scores).pack(pady=12)
		IconRoundButton(self, text="Exit", icon=self._icons["exit"], command=self._exit_app).pack(pady=12)

	def _go_learn(self) -> None:
		from .learn import LearnScreen  # local import to avoid cycles
		self.navigator.register_screen("learn", LearnScreen)
		self.navigator.show("learn")

	def _go_quiz(self) -> None:
		from .quiz import QuizScreen
		self.navigator.register_screen("quiz", QuizScreen)
		self.navigator.show("quiz")

	def _go_scores(self) -> None:
		from .high_scores import HighScoresScreen
		self.navigator.register_screen("scores", HighScoresScreen)
		self.navigator.show("scores")

	def _exit_app(self) -> None:
		self.winfo_toplevel().destroy()
