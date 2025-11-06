import random
from typing import Tuple, Dict, Any
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle, Line
from ..ui.widgets.buttons import IconRoundButton, BackCircleButton
from ..ui import theme
from ..services.high_score_service import HighScoreService
from ..utils.assets import resolve_image_path


class QuizPlayScreen(Screen):
    def __init__(self, name: str, navigator, mode: str, **kwargs) -> None:
        super().__init__(name=name, **kwargs)
        self.navigator = navigator
        self.mode = mode
        self.question_index = 0
        self.correct = 0
        self.current_answer = None
        self.current_problem = ""
        self._checked_current = False
        self._logs: list[Dict[str, Any]] = []

        root = BoxLayout(orientation="vertical", padding=[16, 16, 16, 16], spacing=12)

        # Header row: back + small logo
        header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=52)
        header.add_widget(BackCircleButton(diameter=40, icon_name="back_white.png", on_release=lambda _i: self._back()))
        header.add_widget(Widget())
        logo_small = resolve_image_path("learnbright.png") or resolve_image_path("logo.png")
        if logo_small:
            header.add_widget(Image(source=logo_small, size_hint=(None, None), size=(140, 60)))
        root.add_widget(header)

        # Question label
        self.question_label = Label(text="Question 1", color=self._hex_to_rgba(theme.TEXT), font_size=24, bold=True, size_hint_y=None, height=50)
        root.add_widget(self.question_label)

        # Question pill (white border + blue fill) - wrapped in centered container
        from kivy.uix.anchorlayout import AnchorLayout
        question_wrapper = AnchorLayout(size_hint=(1, None), height=70, anchor_x='center', anchor_y='center')
        self.problem_container = BoxLayout(size_hint=(0.8, None), height=70, padding=[0, 0, 0, 0])
        with self.problem_container.canvas.before:
            # Outer white border
            Color(1, 1, 1, 1)
            self._q_outer = RoundedRectangle(radius=[14])
            # Inner blue fill
            Color(*self._hex_to_rgba("#3DD0F2"))
            self._q_inner = RoundedRectangle(radius=[14])
        self.problem_container.bind(pos=lambda *_: self._update_question_bg(), size=lambda *_: self._update_question_bg())
        self.problem_label = Label(text="", font_size=26, bold=True, color=(1, 1, 1, 1))
        self.problem_container.add_widget(self.problem_label)
        question_wrapper.add_widget(self.problem_container)
        root.add_widget(question_wrapper)

        # Answer box (cyan border using two rounded rectangles to avoid line gaps) - wrapped in centered container
        answer_wrapper = AnchorLayout(size_hint=(1, None), height=120, anchor_x='center', anchor_y='center')
        self.answer_container = BoxLayout(size_hint=(0.8, None), height=120, padding=[0, 0, 0, 0])
        with self.answer_container.canvas.before:
            # Outer cyan border rectangle
            Color(*self._hex_to_rgba("#53C7E8"))
            self._a_outer = RoundedRectangle(radius=[14])
            # Inner white fill inset to create the border effect
            Color(1, 1, 1, 1)
            self._a_inner = RoundedRectangle(radius=[14])
        self.answer_container.bind(pos=lambda *_: self._update_answer_bg(), size=lambda *_: self._update_answer_bg())
        self.answer_input = TextInput(
            text="",
            multiline=False,
            halign="center",
            font_size=28,
            size_hint=(1, 1),
            background_color=(1, 1, 1, 0),
            input_filter="int",
        )

        # Use plain color backgrounds (no image skins)
        self.answer_input.background_normal = ""
        self.answer_input.background_active = ""
        self.answer_input.cursor_width = 2

        # Colors
        self.answer_input.foreground_color = self._hex_to_rgba("#10B6DF")
        self.answer_input.cursor_color = self._hex_to_rgba("#10B6DF")
        self.answer_input.selection_color = (*self._hex_to_rgba("#10B6DF", 0.25),)

        # Center the text vertically by adjusting padding dynamically
        self.answer_input.bind(size=lambda *_: self._center_answer_input())
        # Also keep blue after focus changes
        self.answer_input.bind(focus=lambda *_: self._force_input_colors())
        # Initial padding
        self.answer_input.padding = [12, 12, 12, 12]

        self.answer_container.add_widget(self.answer_input)
        answer_wrapper.add_widget(self.answer_container)
        root.add_widget(answer_wrapper)

        self.feedback_label = Label(text="", color=self._hex_to_rgba("#F2AB0C"), size_hint_y=None, height=60, font_size=20, bold=True)
        root.add_widget(self.feedback_label)

        root.add_widget(IconRoundButton(text="Check Answer", bg_color=self._hex_to_rgba("#F25549"), hover_color=self._hex_to_rgba("#FF6A5E"), on_release=lambda _i: self._check()))
        self._btn_next = IconRoundButton(text="Next Question", bg_color=self._hex_to_rgba("#F2AB0C"), hover_color=self._hex_to_rgba("#FFC326"), on_release=lambda _i: self._next_guarded())
        root.add_widget(self._btn_next)
        self._btn_finish = IconRoundButton(text="Finish Quiz", bg_color=self._hex_to_rgba("#76C043"), hover_color=self._hex_to_rgba("#7FD04A"), on_release=lambda _i: self._finish_guarded())
        root.add_widget(self._btn_finish)

        root.add_widget(Widget())
        self.add_widget(root)
        self._next()

    def _hex_to_rgba(self, hex_color: str, alpha: float = 1.0):
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        rgb = tuple(int(hex_color[i:i + lv // 3], 16) / 255.0 for i in range(0, lv, lv // 3))
        return (*rgb, alpha)

    def _set_nav_enabled(self, enabled: bool) -> None:
        self._btn_next.disabled = not enabled
        self._btn_finish.disabled = not enabled

    def _back(self) -> None:
        self.navigator.show("quiz")

    def _gen_question(self) -> Tuple[str, int]:
        mode = self.mode
        if mode == "mix":
            mode = random.choice(["addition", "subtraction", "multiplication", "division"]) 
        if mode == "addition":
            a = random.randint(1, 99)
            b = random.randint(1, 99)
            return f"{a} + {b} = ?", a + b
        if mode == "subtraction":
            a = random.randint(1, 99)
            b = random.randint(1, 99)
            if b > a:
                a, b = b, a
            return f"{a} - {b} = ?", a - b
        if mode == "multiplication":
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            return f"{a} × {b} = ?", a * b
        if mode == "division":
            candidates = [(a, b) for a in range(1, 10) for b in range(1, 10) if a % b == 0]
            a, b = random.choice(candidates)
            return f"{a} ÷ {b} = ?", a // b
        raise ValueError("Unknown mode")

    def _check(self) -> None:
        if self._checked_current:
            return
        text = self.answer_input.text.strip()
        if not text.isdigit():
            self.feedback_label.text = "Enter a Valid Number!"
            self.feedback_label.color = self._hex_to_rgba("#F2AB0C")
            self._checked_current = False
            self._set_nav_enabled(False)
            return
        user = int(text)
        correct_now = user == self.current_answer
        if correct_now:
            self.feedback_label.text = "Correct!"
            self.feedback_label.color = self._hex_to_rgba("#3DAA3C")
            self.correct += 1
        else:
            self.feedback_label.text = f"X Wrong! Correct: {self.current_answer}"
            self.feedback_label.color = self._hex_to_rgba("#E53935")
        self._checked_current = True
        self._set_nav_enabled(True)
        self.answer_input.readonly = True
        self._logs.append({
            "problem": self.current_problem,
            "answer": self.current_answer,
            "user": user,
            "correct": bool(correct_now),
        })

    def _next_guarded(self) -> None:
        if not self._checked_current:
            self.feedback_label.text = "Please check your answer first!"
            self.feedback_label.color = self._hex_to_rgba("#F2AB0C")
            return
        self._next()

    def _next(self) -> None:
        self.question_index += 1
        self.question_label.text = f"Question {self.question_index}"
        problem, answer = self._gen_question()
        self.current_answer = answer
        self.current_problem = problem
        self.problem_label.text = problem
        self.answer_input.readonly = False
        self.answer_input.text = ""
        self.feedback_label.text = ""
        self._checked_current = False
        self._set_nav_enabled(False)
        # Focus the input so the user can type immediately
        self.answer_input.focus = True

    def _finish_guarded(self) -> None:
        if not self._checked_current:
            self.feedback_label.text = "Please check your answer first!"
            self.feedback_label.color = self._hex_to_rgba("#F2AB0C")
            return
        self._finish()

    def _finish(self) -> None:
        service = HighScoreService()
        is_new_high_score = service.record_attempt(self.mode, score=self.correct, total=self.question_index, questions=self._logs)
        
        # Show popup if it's a new high score
        if is_new_high_score:
            self._show_high_score_popup()
        else:
            # Navigate back to the quiz modes screen
            self.navigator.show("quiz")
    
    def _show_high_score_popup(self) -> None:
        """Show a congratulations popup for new high score"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        # Congratulations message
        content.add_widget(Label(
            text=f"[color=FFD700][size=32][b] NEW HIGH SCORE!!! [/b][/size][/color]\n\n[size=24]You scored [b]{self.correct}/{self.question_index}[/b]\nin [b]{self.mode.title()}[/b] mode![/size]",
            markup=True,
            halign='center',
            valign='center'
        ))
        
        # OK button
        ok_button = Button(
            text='OK',
            size_hint=(1, None),
            height=50,
            background_color=self._hex_to_rgba("#76C043"),
            color=(1, 1, 1, 1),
            bold=True,
            font_size=20
        )
        
        popup = Popup(
            title='Congratulations!',
            title_size='20sp',
            title_align='center',
            content=content,
            size_hint=(0.85, None),
            height=300,
            auto_dismiss=False
        )
        
        def close_popup(_):
            popup.dismiss()
            self.navigator.show("quiz")
        
        ok_button.bind(on_release=close_popup)
        content.add_widget(ok_button)
        
        popup.open()

    def _update_question_bg(self):
        # 1px white border by insetting blue rect
        x, y = self.problem_container.pos
        w, h = self.problem_container.size
        self._q_outer.pos = (x, y)
        self._q_outer.size = (w, h)
        inset = 1
        self._q_inner.pos = (x + inset, y + inset)
        self._q_inner.size = (max(0, w - 2 * inset), max(0, h - 2 * inset))

    def _update_answer_bg(self):
        x, y = self.answer_container.pos
        w, h = self.answer_container.size
        # Outer cyan
        self._a_outer.pos = (x, y)
        self._a_outer.size = (w, h)
        # Inner white inset (creates visible border without line seams)
        inset = 3
        self._a_inner.pos = (x + inset, y + inset)
        self._a_inner.size = (max(0, w - 2 * inset), max(0, h - 2 * inset))

    def _center_answer_input(self):
        # Use a safe, fixed vertical padding to avoid over-centering glitches
        try:
            pad_y = 40
            self.answer_input.padding = [12, pad_y, 12, pad_y]
        except Exception:
            pass

    def _force_input_colors(self):
        try:
            self.answer_input.foreground_color = self._hex_to_rgba("#10B6DF")
            self.answer_input.cursor_color = self._hex_to_rgba("#10B6DF")
        except Exception:
            pass