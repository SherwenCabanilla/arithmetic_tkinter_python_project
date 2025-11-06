from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.core.window import Window
from ..ui.widgets.buttons import IconRoundButton
from ..ui import theme
from ..utils.assets import first_existing_image


class HomeScreen(Screen):
	def __init__(self, name: str, navigator, **kwargs):
		super().__init__(name=name, **kwargs)
		self.navigator = navigator
		self._build_ui()

	def _build_ui(self) -> None:
		Window.size = (360, 720)
		root = BoxLayout(orientation="vertical", padding=[16, 24, 16, 24], spacing=18)

		# Flexible top spacer to push content toward center
		root.add_widget(Widget(size_hint_y=1))

		# Logo block
		logo_block = BoxLayout(size_hint=(1, None), height=220)
		logo_path = first_existing_image("logo.png", "learn_bright_logo.png", "learnbright.png")
		if logo_path:
			logo = Image(source=logo_path, allow_stretch=True, keep_ratio=True)
			logo_block.add_widget(logo)
		else:
			logo_block.add_widget(Widget())
		root.add_widget(logo_block)

		# Spacer between logo and buttons
		root.add_widget(Widget(size_hint_y=None, height=20))

		# Buttons
		root.add_widget(IconRoundButton(text="Learn and Watch", icon_name="play.png", on_release=lambda _i: self._go_learn()))
		root.add_widget(IconRoundButton(text="Start Quiz", icon_name="brain.png", on_release=lambda _i: self._go_quiz()))
		root.add_widget(IconRoundButton(text="View High Score", icon_name="chart.png", on_release=lambda _i: self._go_scores()))
		root.add_widget(IconRoundButton(text="Exit", icon_name="exit.png", on_release=lambda _i: self._exit_app()))

		# Flexible bottom spacer to keep the group centered
		root.add_widget(Widget(size_hint_y=1))

		self.add_widget(root)

	def _go_learn(self) -> None:
		from .learn import LearnScreen  # type: ignore
		self.navigator.register_screen("learn", LearnScreen)
		self.navigator.show("learn")

	def _go_quiz(self) -> None:
		from .quiz import QuizScreen  # type: ignore
		self.navigator.register_screen("quiz", QuizScreen)
		self.navigator.show("quiz")

	def _go_scores(self) -> None:
		from .high_scores import HighScoresScreen  # type: ignore
		self.navigator.register_screen("scores", HighScoresScreen)
		self.navigator.show("scores")

	def _exit_app(self) -> None:
		from kivy.app import App
		App.get_running_app().stop()
