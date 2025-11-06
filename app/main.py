from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window

try:
	from .core.navigation import Navigator
	from .screens.home import HomeScreen
except ImportError:
	# Allow running this file directly: python app/main.py
	import sys
	from pathlib import Path
	sys.path.append(str(Path(__file__).resolve().parents[1]))
	from app.core.navigation import Navigator
	from app.screens.home import HomeScreen


class LearnBrightApp(App):
	def build(self):
		self.title = "Learn Bright"
		self.icon = "assets/images/learnbright.png"
		Window.clearcolor = (1, 1, 1, 1)
		sm = ScreenManager()
		self.navigator = Navigator(sm)
		self.navigator.register_screen("home", HomeScreen)
		self.navigator.show("home")
		return sm


def main() -> None:
	LearnBrightApp().run()


if __name__ == "__main__":
	main()
