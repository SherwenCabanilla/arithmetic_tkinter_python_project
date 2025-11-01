import tkinter as tk
from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import IconRoundButton
from ..ui import theme
from ..utils.assets import load_icon
from .quiz_play import QuizPlayScreen


class QuizScreen(MobileFrame):
	def __init__(self, master: tk.Misc, navigator) -> None:
		super().__init__(master)
		self.navigator = navigator

		self._icons = {
			"add": load_icon("plus.png"),
			"sub": load_icon("minus.png"),
			"mul": load_icon("times.png"),
			"div": load_icon("divide.png"),
			"mix": load_icon("mix.png"),
		}

		back_btn = tk.Button(self, text="⬅", command=lambda: self.navigator.show("home"), bd=0, bg=theme.BG, fg=theme.TEXT, font=("Segoe UI", 14, "bold"))
		back_btn.pack(anchor=tk.W, padx=16, pady=(16, 8))

		title = tk.Label(self, text="QUIZ\nGAMES", bg=theme.BG, fg="#FF6F61", font=("Segoe UI", 28, "bold"), justify=tk.CENTER)
		title.pack(pady=(4, 24))

		IconRoundButton(self, text="Addition", icon=self._icons["add"], bg_color="#76C043", hover_color="#7FD04A", command=lambda: self._start_mode("addition")).pack(pady=10)
		IconRoundButton(self, text="Subtraction", icon=self._icons["sub"], bg_color="#8E66E3", hover_color="#9A74EE", command=lambda: self._start_mode("subtraction")).pack(pady=10)
		IconRoundButton(self, text="Multiplication", icon=self._icons["mul"], bg_color="#11B3D9", hover_color="#1AC2EA", command=lambda: self._start_mode("multiplication")).pack(pady=10)
		IconRoundButton(self, text="Division", icon=self._icons["div"], bg_color="#F2AB0C", hover_color="#FFC326", command=lambda: self._start_mode("division")).pack(pady=10)
		IconRoundButton(self, text="Mix", icon=self._icons["mix"], bg_color="#F25549", hover_color="#FF6A5E", command=lambda: self._start_mode("mix")).pack(pady=10)

	def _start_mode(self, mode: str) -> None:
		name = f"quiz_play_{mode}"
		# Destroy old instance if it exists to reset state
		if name in self.navigator._screens:
			self.navigator._screens[name].destroy()
			del self.navigator._screens[name]
		self.navigator.register_screen(name, lambda master, nav: QuizPlayScreen(master, nav, mode))
		self.navigator.show(name)
