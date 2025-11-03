import tkinter as tk
from typing import Optional
from .. import theme
from ...utils.assets import load_icon


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
			font=theme.BUTTON_FONT,
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
		self.text_id = self.create_text(padding_left, self.height//2, text=text, fill=theme.PRIMARY_TEXT, anchor=tk.W, font=theme.BUTTON_FONT)

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


class BackCircleButton(tk.Canvas):
	"""Circular blue back button with optional PNG icon for perfection.

	If an icon named 'back_white.png' (or provided icon_name) exists under
	assets/images, it is used; otherwise a vector arrow is drawn.
	"""

	def __init__(self, master: tk.Misc, command=None, diameter: int = 36, icon_name: Optional[str] = "back_white.png", bg_color: Optional[str] = None, hover_color: Optional[str] = None, show_circle: bool = False):
		self.diameter = diameter
		self.command = command
		super().__init__(master, width=diameter, height=diameter, highlightthickness=0, bg=theme.BG)
		self._show_circle = bool(show_circle)
		self._base_color = bg_color or theme.PRIMARY
		self._hover_color = hover_color or "#10B6DF"
		# Try to load icon
		self._icon = load_icon(icon_name) if icon_name else None
		self._draw()
		self._bind_events()

	def _draw(self) -> None:
		self.circle_id = None
		if self._show_circle:
			self.circle_id = self.create_oval(0, 0, self.diameter, self.diameter, fill=self._base_color, outline="")
		if self._icon is not None:
			# Center the provided icon; keep a reference so it isn't GC'd
			self.create_image(self.diameter//2, self.diameter//2, image=self._icon)
		else:
			# Draw a centered left-pointing arrow (shaft + triangle head)
			d = self.diameter
			pad = int(d * 0.26)
			shaft_h = int(d * 0.18)
			shaft_left = pad + int(d * 0.22)
			shaft_right = d - pad
			center_y = d // 2
			# Shaft rectangle
			self.create_rectangle(shaft_left, center_y - shaft_h//2, shaft_right, center_y + shaft_h//2, fill=theme.PRIMARY_TEXT, outline="")
			# Triangle head pointing left
			head_left = pad
			points = [
				shaft_left, center_y - shaft_h,
				shaft_left, center_y + shaft_h,
				head_left, center_y,
			]
			self.create_polygon(points, fill=theme.PRIMARY_TEXT, outline="")

	def _bind_events(self) -> None:
		self.bind("<Button-1>", self._on_click)
		if self.circle_id is not None:
			self.bind("<Enter>", lambda _e: self.itemconfig(self.circle_id, fill=self._hover_color))
			self.bind("<Leave>", lambda _e: self.itemconfig(self.circle_id, fill=self._base_color))

	def _on_click(self, _e):
		if callable(self.command):
			self.command()
