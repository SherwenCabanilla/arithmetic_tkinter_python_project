import tkinter as tk
from typing import Optional
from .. import theme


class PrimaryButton(tk.Button):
	def __init__(self, master: tk.Misc, text: str, command=None):
		super().__init__(
			master,
			text=text,
			command=command,
			bg=theme.PRIMARY,
			fg=theme.PRIMARY_TEXT,
			activebackground=theme.PRIMARY,
			activeforeground=theme.PRIMARY_TEXT,
			bd=0,
			padx=16,
			pady=12,
			font=("Segoe UI", 12, "bold"),
		)


class IconRoundButton(tk.Canvas):
	"""Rounded rectangle button with optional left icon.

	Drawn using a Canvas so we can have rounded corners without external deps.
	"""

	def __init__(self, master: tk.Misc, text: str, command=None, icon: Optional[tk.PhotoImage] = None,
				width: int = 280, height: int = 56, radius: int = 16,
				bg_color: str = None, hover_color: str = None):
		self.width = width
		self.height = height
		self.radius = radius
		self.command = command
		self.icon_image = icon
		self.bg_color = bg_color or theme.PRIMARY
		self.hover_color = hover_color or "#00B7EA"
		self.disabled_color = "#BDBDBD"
		self.enabled = True
		super().__init__(master, width=width, height=height, highlightthickness=0, bg=theme.BG)
		self._draw(text)
		self._bind_events()

	def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
		points = [
			x1+r, y1,
			x2-r, y1,
			x2, y1,
			x2, y1+r,
			x2, y2-r,
			x2, y2,
			x2-r, y2,
			x1+r, y2,
			x1, y2,
			x1, y2-r,
			x1, y1+r,
			x1, y1,
		]
		return self.create_polygon(points, smooth=True, **kwargs)

	def _draw(self, text: str) -> None:
		self.bg_id = self._rounded_rect(2, 2, self.width-2, self.height-2, self.radius, fill=self.bg_color, outline="")
		padding_left = 18
		if self.icon_image is not None:
			self.create_image(18, self.height//2, image=self.icon_image, anchor=tk.W)
			padding_left = 18 + self.icon_image.width() + 10
		self.text_id = self.create_text(padding_left, self.height//2, text=text, fill=theme.PRIMARY_TEXT, anchor=tk.W, font=("Segoe UI", 13, "bold"))

	def _bind_events(self) -> None:
		self.bind("<Button-1>", self._on_click)
		self.bind("<Enter>", self._on_enter)
		self.bind("<Leave>", self._on_leave)

	def _on_enter(self, _e):
		if self.enabled:
			self.itemconfig(self.bg_id, fill=self.hover_color)

	def _on_leave(self, _e):
		self.itemconfig(self.bg_id, fill=self.bg_color if self.enabled else self.disabled_color)

	def _on_click(self, _event) -> None:
		if self.enabled and callable(self.command):
			self.command()

	def set_enabled(self, enabled: bool) -> None:
		self.enabled = enabled
		self.itemconfig(self.bg_id, fill=self.bg_color if enabled else self.disabled_color)
