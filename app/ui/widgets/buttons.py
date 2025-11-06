from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ListProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Ellipse
from ...utils.assets import resolve_image_path
from .. import theme


class IconRoundButton(ButtonBehavior, BoxLayout):
	text = StringProperty("")
	icon_name = StringProperty("")
	radius = NumericProperty(16)
	bg_color = ListProperty([0, 0, 0, 1])
	hover_color = ListProperty([0, 0, 0, 1])
	text_color = ListProperty([1, 1, 1, 1])
	height_dp = NumericProperty(56)
	with_icon = BooleanProperty(True)

	def __init__(self, text: str, icon_name: str = "", bg_color=None, hover_color=None, text_color=None, **kwargs):
		super().__init__(orientation="horizontal", padding=[12, 0, 12, 0], spacing=12, size_hint=(0.8, None), height=self.height_dp, pos_hint={'center_x': 0.5}, **kwargs)
		self.text = text
		self.icon_name = icon_name
		self.bg_color = self._hex_to_rgba(theme.PRIMARY) if bg_color is None else bg_color
		self.hover_color = self._hex_to_rgba("#00B7EA") if hover_color is None else hover_color
		self.text_color = self._hex_to_rgba(theme.PRIMARY_TEXT) if text_color is None else text_color
		self._bg_rect = None
		self._draw_background(self.bg_color)
		self._build_content()

	def _build_content(self):
		self.clear_widgets()
		if self.icon_name:
			icon_path = resolve_image_path(self.icon_name)
			if icon_path:
				# Wrap icon in a centered container
				from kivy.uix.anchorlayout import AnchorLayout
				icon_container = AnchorLayout(size_hint=(None, 1), width=28, anchor_x='center', anchor_y='center')
				icon_container.add_widget(Image(source=icon_path, size_hint=(None, None), size=(28, 28), allow_stretch=True, keep_ratio=True))
				self.add_widget(icon_container)
		label = Label(text=self.text, color=self.text_color, font_size='20sp', bold=True)
		self.add_widget(label)

	def _draw_background(self, rgba):
		self.canvas.before.clear()
		with self.canvas.before:
			Color(*rgba)
			self._bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
		self.bind(pos=self._update_rect, size=self._update_rect)

	def _update_rect(self, *_):
		if self._bg_rect is not None:
			self._bg_rect.pos = self.pos
			self._bg_rect.size = self.size

	def on_press(self):
		self._draw_background(self.hover_color)

	def on_release(self):
		self._draw_background(self.bg_color)

	def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0):
		hex_color = hex_color.lstrip('#')
		lv = len(hex_color)
		rgb = tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
		return [*rgb, alpha]


class BackCircleButton(ButtonBehavior, FloatLayout):
	diameter = NumericProperty(40)
	bg_color = ListProperty([1, 1, 1, 1])
	hover_color = ListProperty([0.94, 0.94, 0.94, 1])
	icon_name = StringProperty("back_white.png")

	def __init__(self, diameter: int = 30, icon_name: str = "back_white.png", **kwargs):
		super().__init__(size_hint=(None, None), size=(diameter, diameter), **kwargs)
		self.diameter = diameter
		self.icon_name = icon_name
		self._circle = None
		self._icon_widget = None
		self._draw(self.bg_color)

	def _draw(self, fill_rgba):
		self.canvas.before.clear()
		with self.canvas.before:
			Color(*fill_rgba)
			self._circle = Ellipse(pos=self.pos, size=self.size)
		self.bind(pos=self._update_graphics, size=self._update_graphics)
		self._set_icon()

	def _set_icon(self):
		if self._icon_widget is not None:
			self.remove_widget(self._icon_widget)
		path = resolve_image_path(self.icon_name)
		if path:
			self._icon_widget = Image(source=path, size_hint=(None, None), size=(int(self.diameter*0.6), int(self.diameter*0.6)), pos_hint={"center_x": 0.5, "center_y": 0.5})
			self.add_widget(self._icon_widget)

	def _update_graphics(self, *_):
		if self._circle is not None:
			self._circle.pos = self.pos
			self._circle.size = self.size

	def on_press(self):
		self._draw(self.hover_color)

	def on_release(self):
		self._draw(self.bg_color)

	def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0):
		hex_color = hex_color.lstrip('#')
		lv = len(hex_color)
		rgb = tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
		return [*rgb, alpha]
