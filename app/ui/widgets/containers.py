import tkinter as tk
from .. import theme


class MobileFrame(tk.Frame):
	def __init__(self, master: tk.Misc):
		super().__init__(master, bg=theme.BG)
