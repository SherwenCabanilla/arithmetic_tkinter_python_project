from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from ..ui import theme


class HighScoresScreen(Screen):
	def __init__(self, name: str, navigator, **kwargs):
		super().__init__(name=name, **kwargs)
		self.navigator = navigator
		root = BoxLayout(orientation="vertical", padding=16, spacing=12)
		root.add_widget(Button(text="← Back", size_hint=(1, None), height=44, background_normal="", background_color=self._hex_to_rgba(theme.PRIMARY), color=self._hex_to_rgba(theme.PRIMARY_TEXT), on_press=lambda _i: self.navigator.show("home")))
		root.add_widget(Label(text="High scores (coming soon)", color=self._hex_to_rgba(theme.TEXT)))
		self.add_widget(root)

	def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0):
		hex_color = hex_color.lstrip('#')
		lv = len(hex_color)
		rgb = tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
		return (*rgb, alpha)
