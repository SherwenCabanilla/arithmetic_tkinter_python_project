from typing import Dict, Type
from kivy.uix.screenmanager import ScreenManager, Screen


class Navigator:
	"""Simple navigator backed by a Kivy ScreenManager."""

	def __init__(self, screen_manager: ScreenManager) -> None:
		self.screen_manager = screen_manager
		self._screens: Dict[str, Screen] = {}
		self._registry: Dict[str, Type[Screen]] = {}

	def register_screen(self, name: str, screen_cls: Type[Screen]) -> None:
		self._registry[name] = screen_cls

	def show(self, name: str) -> None:
		if name not in self._screens:
			if name not in self._registry:
				raise KeyError(f"Screen '{name}' is not registered")
			instance = self._registry[name](name=name, navigator=self)
			self._screens[name] = instance
			self.screen_manager.add_widget(instance)
		self.screen_manager.current = name

	def show_with_context(self, name: str, **context) -> None:
		self.show(name)
		screen = self._screens.get(name)
		if screen is not None and hasattr(screen, "apply_context"):
			try:
				getattr(screen, "apply_context")(**context)  # type: ignore[misc]
			except Exception:
				pass