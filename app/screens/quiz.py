from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from ..ui import theme
from ..ui.widgets.buttons import IconRoundButton, BackCircleButton
from ..utils.assets import resolve_image_path


class QuizScreen(Screen):
    def __init__(self, name: str, navigator, **kwargs):
        super().__init__(name=name, **kwargs)
        self.navigator = navigator
        root = BoxLayout(orientation="vertical", padding=[16, 16, 16, 16], spacing=12)

        # Header row: back + small logo
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=52)
        header.add_widget(BackCircleButton(diameter=40, icon_name="back_white.png", on_release=lambda _i: self.navigator.show("home")))
        header.add_widget(Widget())
        logo_small = resolve_image_path("learnbright.png") or resolve_image_path("logo.png")
        if logo_small:
            header.add_widget(Image(source=logo_small, size_hint=(None, None), size=(140, 60)))
        root.add_widget(header)
        
        # Add spacing between header and title
        root.add_widget(Widget(size_hint=(1, None), height=20))

        # Title - Quiz Games image
        from kivy.uix.anchorlayout import AnchorLayout
        title_img = resolve_image_path("quiz_games.png")
        if title_img:
            title_container = AnchorLayout(size_hint=(1, None), height=160, anchor_x='center', anchor_y='center', padding=[0, 15, 0, 15])
            title_container.add_widget(Image(source=title_img, size_hint=(None, None), size=(500, 230), allow_stretch=True, keep_ratio=True))
            root.add_widget(title_container)
        else:
            root.add_widget(Label(text="[color=FF6F61][b]QUIZ\nGAMES[/b][/color]", markup=True, font_size=26))

        # Mode buttons
        root.add_widget(IconRoundButton(text="Addition", icon_name="addition.png", bg_color=self._hex_to_rgba("#76C043"), hover_color=self._hex_to_rgba("#7FD04A"), on_release=lambda _i: self._start_mode("addition")))
        root.add_widget(IconRoundButton(text="Subtraction", icon_name="minus.png", bg_color=self._hex_to_rgba("#8E66E3"), hover_color=self._hex_to_rgba("#9A74EE"), on_release=lambda _i: self._start_mode("subtraction")))
        root.add_widget(IconRoundButton(text="Multiplication", icon_name="times.png", bg_color=self._hex_to_rgba("#11B3D9"), hover_color=self._hex_to_rgba("#1AC2EA"), on_release=lambda _i: self._start_mode("multiplication")))
        root.add_widget(IconRoundButton(text="Division", icon_name="divide.png", bg_color=self._hex_to_rgba("#F2AB0C"), hover_color=self._hex_to_rgba("#FFC326"), on_release=lambda _i: self._start_mode("division")))
        root.add_widget(IconRoundButton(text="Mix", icon_name="mix.png", bg_color=self._hex_to_rgba("#F25549"), hover_color=self._hex_to_rgba("#FF6A5E"), on_release=lambda _i: self._start_mode("mix")))

        root.add_widget(Widget())
        self.add_widget(root)

    def _start_mode(self, mode: str) -> None:
        from .quiz_play import QuizPlayScreen  # type: ignore
        screen_name = f"quiz_play_{mode}"
        # If an old instance exists, remove it to start fresh at Question 1
        if screen_name in getattr(self.navigator, "_screens", {}):
            try:
                old = self.navigator._screens.pop(screen_name)
                self.navigator.screen_manager.remove_widget(old)
            except Exception:
                pass
        self.navigator.register_screen(screen_name, lambda name, navigator: QuizPlayScreen(name=name, navigator=navigator, mode=mode))
        self.navigator.show(screen_name)

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0):
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        rgb = tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
        return (*rgb, alpha)
