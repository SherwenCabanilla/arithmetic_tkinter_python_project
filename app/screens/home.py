import tkinter as tk
from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import PrimaryButton, IconRoundButton
from ..ui import theme
from ..utils.assets import load_icon, load_icon_max_width


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

		# Center all content vertically by using an inner container with expand=True
		content = tk.Frame(self, bg=theme.BG)
		content.pack(fill=tk.BOTH, expand=True)

		# Top spacer (adds 24px margin from the top)
		spacer = tk.Frame(content, bg=theme.BG, height=80)
		spacer.pack(fill=tk.X)

		# Try to show app logo if available
		# Load and constrain logo width for consistent layout
		self._logo = (
			load_icon_max_width("logo.png", 300)
			or load_icon_max_width("learn_bright_logo.png", 300)
			or load_icon_max_width("learnbright.png", 300)
		)
		if self._logo is not None:
			logo_label = tk.Label(content, image=self._logo, bg=theme.BG)
			logo_label.pack(pady=(12, 18))
		else:
			title = tk.Label(content, text="Learn\nBRIGHT", bg=theme.BG, fg=theme.TEXT, font=theme.TITLE_FONT)
			title.pack(pady=(40, 24))

		IconRoundButton(content, text="Learn and Watch", icon=self._icons["play"], command=self._go_learn).pack(pady=14)
		IconRoundButton(content, text="Start Quiz", icon=self._icons["quiz"], command=self._go_quiz).pack(pady=14)
		IconRoundButton(content, text="View High Score", icon=self._icons["chart"], command=self._go_scores).pack(pady=14)
		IconRoundButton(content, text="Exit", icon=self._icons["exit"], command=self._exit_app).pack(pady=14)

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
