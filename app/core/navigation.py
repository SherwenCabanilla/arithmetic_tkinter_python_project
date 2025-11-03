import tkinter as tk
from typing import Dict, Type


class Navigator:
	"""Simple navigator that swaps Tkinter Frames by name."""

	def __init__(self, root: tk.Tk) -> None:
		self.root = root
		self.container = tk.Frame(root)
		self.container.pack(fill=tk.BOTH, expand=True)
		self._screens: Dict[str, tk.Frame] = {}
		self._registry: Dict[str, Type[tk.Frame]] = {}

	def register_screen(self, name: str, screen_cls: Type[tk.Frame]) -> None:
		self._registry[name] = screen_cls

	def show(self, name: str) -> None:
		if name not in self._screens:
			if name not in self._registry:
				raise KeyError(f"Screen '{name}' is not registered")
			self._screens[name] = self._registry[name](self.container, self)
		# Hide others
		for screen_name, frame in self._screens.items():
			if screen_name == name:
				frame.pack(fill=tk.BOTH, expand=True)
				frame.tkraise()
			else:
				frame.pack_forget()

	def show_with_context(self, name: str, **context) -> None:
		"""Show a screen and pass context via an optional apply_context method.

		If the target screen implements apply_context(**kwargs), it will be
		called after the screen is shown.
		"""
		self.show(name)
		frame = self._screens.get(name)
		if frame is not None and hasattr(frame, "apply_context"):
			try:
				getattr(frame, "apply_context")(**context)  # type: ignore[misc]
			except Exception:
				pass