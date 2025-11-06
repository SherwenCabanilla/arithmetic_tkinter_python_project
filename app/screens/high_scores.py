from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from ..ui import theme
from ..ui.widgets.buttons import IconRoundButton, BackCircleButton
from ..services.high_score_service import HighScoreService
from ..utils.assets import resolve_image_path


class HighScoresScreen(Screen):
    def __init__(self, name: str, navigator, **kwargs):
        super().__init__(name=name, **kwargs)
        self.navigator = navigator
        self.service = HighScoreService()
        self.root_layout = None
        self._build_ui()

    def on_pre_enter(self):
        """Refresh the UI every time the screen is shown"""
        self._build_ui()

    def _build_ui(self):
        """Build or rebuild the UI with fresh data"""
        # Clear existing widgets
        self.clear_widgets()
        
        root = BoxLayout(orientation="vertical", padding=[16, 16, 16, 16], spacing=12)

        # Header row: back + small logo
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=52, padding=[0, 0, 0, 0])
        header.add_widget(BackCircleButton(diameter=40, icon_name="back_white.png", on_release=lambda _i: self.navigator.show("home")))
        header.add_widget(Widget())
        logo_small = resolve_image_path("learnbright.png") or resolve_image_path("logo.png")
        if logo_small:
            header.add_widget(Image(source=logo_small, size_hint=(None, None), size=(140, 60)))
        root.add_widget(header)
        
        # Add spacing between header and title
        root.add_widget(Widget(size_hint=(1, None), height=20))

        # Title - High Score image
        from kivy.uix.anchorlayout import AnchorLayout
        title_img = resolve_image_path("highscore.png")
        if title_img:
            title_container = AnchorLayout(size_hint=(1, None), height=160, anchor_x='center', anchor_y='center', padding=[0, 15, 0, 30])
            title_container.add_widget(Image(source=title_img, size_hint=(None, None), size=(500, 230), allow_stretch=True, keep_ratio=True))
            root.add_widget(title_container)
        else:
            root.add_widget(Label(text="[color=10B6DF][b]High Score History[/b][/color]", markup=True, font_size=22))

        # Mode buttons with best score summary - refresh data each time
        overview = self.service.get_overview()
        mode_config = {
            "addition": {"icon": "addition.png", "bg": "#76C043", "hover": "#7FD04A"},
            "subtraction": {"icon": "minus.png", "bg": "#8E66E3", "hover": "#9A74EE"},
            "multiplication": {"icon": "times.png", "bg": "#11B3D9", "hover": "#1AC2EA"},
            "division": {"icon": "divide.png", "bg": "#F2AB0C", "hover": "#FFC326"},
            "mix": {"icon": "mix.png", "bg": "#F25549", "hover": "#FF6A5E"}
        }
        
        for mode in ["addition", "subtraction", "multiplication", "division", "mix"]:
            info = overview.get(mode, {})
            best = info.get("best")
            label = f"{mode.title()} — {best['score']}/{best['total']}" if best else f"{mode.title()} — None"
            config = mode_config[mode]
            root.add_widget(IconRoundButton(
                text=label, 
                icon_name=config["icon"],
                bg_color=self._hex_to_rgba(config["bg"]), 
                hover_color=self._hex_to_rgba(config["hover"]), 
                on_release=lambda _i, m=mode: self._open_mode(m)
            ))

        root.add_widget(Widget())
        self.add_widget(root)
        self.root_layout = root

    def _open_mode(self, mode: str) -> None:
        from .mode_logs import ModeLogsScreen  # type: ignore
        screen_name = f"mode_logs_{mode}"
        # Replace old instance to refresh
        if screen_name in getattr(self.navigator, "_screens", {}):
            try:
                old = self.navigator._screens.pop(screen_name)
                self.navigator.screen_manager.remove_widget(old)
            except Exception:
                pass
        self.navigator.register_screen(screen_name, lambda name, navigator: ModeLogsScreen(name=name, navigator=navigator, mode=mode))
        self.navigator.show(screen_name)

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0):
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        rgb = tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
        return (*rgb, alpha)
