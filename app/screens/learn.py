import tkinter as tk
from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import IconRoundButton
from ..ui import theme
from ..utils.assets import load_icon


class LearnScreen(MobileFrame):
	def __init__(self, master: tk.Misc, navigator) -> None:
		super().__init__(master)
		self.navigator = navigator

		self._icons = {
			"add": load_icon("plus.png"),
			"sub": load_icon("minus.png"),
			"mul": load_icon("times.png"),
			"div": load_icon("divide.png"),
			"back": load_icon("back.png"),
		}

		# Header
		back_btn = tk.Button(self, text="⬅", command=lambda: self.navigator.show("home"), bd=0, bg=theme.BG, fg=theme.TEXT, font=("Segoe UI", 14, "bold"))
		back_btn.pack(anchor=tk.W, padx=16, pady=(16, 8))

		title = tk.Label(self, text="Watch Video\nTutorial", bg=theme.BG, fg="#E65100", font=("Segoe UI", 24, "bold"), justify=tk.CENTER)
		title.pack(pady=(4, 24))

		IconRoundButton(self, text="Addition", icon=self._icons["add"], bg_color="#76C043", hover_color="#7FD04A", command=lambda: self._open_topic("addition")).pack(pady=10)
		IconRoundButton(self, text="Subtraction", icon=self._icons["sub"], bg_color="#8E66E3", hover_color="#9A74EE", command=lambda: self._open_topic("subtraction")).pack(pady=10)
		IconRoundButton(self, text="Multiplication", icon=self._icons["mul"], bg_color="#11B3D9", hover_color="#1AC2EA", command=lambda: self._open_topic("multiplication")).pack(pady=10)
		IconRoundButton(self, text="Division", icon=self._icons["div"], bg_color="#F2AB0C", hover_color="#FFC326", command=lambda: self._open_topic("division")).pack(pady=10)

	def _open_topic(self, topic: str) -> None:
		# Placeholder: open video/resource for the topic
		# You can integrate webbrowser.open(url) mapped per topic
		print(f"Open tutorial for {topic}")
