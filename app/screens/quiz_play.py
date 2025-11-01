import tkinter as tk
import random
from typing import Tuple, Dict, Any
from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import IconRoundButton
from ..ui import theme
from ..services.high_score_service import HighScoreService


class QuizPlayScreen(MobileFrame):
	def __init__(self, master: tk.Misc, navigator, mode: str) -> None:
		super().__init__(master)
		self.navigator = navigator
		self.mode = mode  # 'addition'|'subtraction'|'multiplication'|'division'|'mix'
		self.question_index = 0
		self.correct = 0
		self.current_answer = None
		self.current_problem = ""
		self._checked_current = False
		self._logs: list[Dict[str, Any]] = []

		back_btn = tk.Button(self, text="⬅", command=self._back, bd=0, bg=theme.BG, fg=theme.TEXT, font=("Segoe UI", 14, "bold"))
		back_btn.pack(anchor=tk.W, padx=16, pady=(16, 8))

		self.question_label = tk.Label(self, text="Question 1", bg=theme.BG, fg=theme.TEXT, font=("Segoe UI", 12, "bold"))
		self.question_label.pack(pady=(0, 8))

		# Problem container (rounded)
		self.problem_canvas = tk.Canvas(self, width=280, height=56, bg=theme.BG, highlightthickness=0)
		self.problem_canvas.pack(pady=(0, 16))
		self._draw_problem_container(self.problem_canvas)
		self.problem_text = self.problem_canvas.create_text(140, 28, text="", fill="#FFFFFF", font=("Segoe UI", 18, "bold"))

		# Answer container (large rounded with Entry centered)
		self.answer_canvas = tk.Canvas(self, width=260, height=120, bg=theme.BG, highlightthickness=0)
		self.answer_canvas.pack(pady=(0, 12))
		self._draw_answer_container(self.answer_canvas)
		self.answer_entry = tk.Entry(self, justify=tk.CENTER, font=("Segoe UI", 18, "bold"), fg="#10B6DF", bd=0, relief=tk.FLAT)
		# place centered over the canvas area
		self.answer_entry.place(in_=self.answer_canvas, x=130, y=60, anchor=tk.CENTER, width=150)

		self.feedback_label = tk.Label(self, text="", bg=theme.BG, fg="#F2AB0C", font=("Segoe UI", 12, "bold"))
		self.feedback_label.pack(pady=(8, 8))

		IconRoundButton(self, text="Check Answer", bg_color="#F25549", hover_color="#FF6A5E", command=self._check).pack(pady=10)
		self._btn_next = IconRoundButton(self, text="Next Question", bg_color="#F2AB0C", hover_color="#FFC326", command=self._next_guarded)
		self._btn_next.pack(pady=10)
		self._btn_finish = IconRoundButton(self, text="Finish Quiz", bg_color="#76C043", hover_color="#7FD04A", command=self._finish_guarded)
		self._btn_finish.pack(pady=10)

		self._next()

	def _rounded_rect(self, canvas: tk.Canvas, x1, y1, x2, y2, r, **kwargs):
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
		return canvas.create_polygon(points, smooth=True, **kwargs)

	def _draw_problem_container(self, canvas: tk.Canvas) -> None:
		self._rounded_rect(canvas, 2, 2, 278, 54, 14, fill="#3DD0F2", outline="white", width=4)

	def _draw_answer_container(self, canvas: tk.Canvas) -> None:
		self._rounded_rect(canvas, 2, 2, 258, 118, 14, fill="#FFFFFF", outline="#53C7E8", width=4)

	def _set_nav_enabled(self, enabled: bool) -> None:
		self._btn_next.set_enabled(enabled)
		self._btn_finish.set_enabled(enabled)

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
			# Single-digit dividend and divisor (1..9), exact division; allow divisor 1
			candidates = [(a, b) for a in range(1, 10) for b in range(1, 10) if a % b == 0]
			a, b = random.choice(candidates)
			return f"{a} ÷ {b} = ?", a // b
		raise ValueError("Unknown mode")

	def _check(self) -> None:
		# Prevent multiple checks for the same question
		if self._checked_current:
			return
		text = self.answer_entry.get().strip()
		if not text.isdigit():
			self.feedback_label.configure(text="Enter a Valid Number!", fg="#F2AB0C")
			self._checked_current = False
			self._set_nav_enabled(False)
			return
		user = int(text)
		correct_now = user == self.current_answer
		if correct_now:
			self.feedback_label.configure(text="Correct!", fg="#3DAA3C")
			self.correct += 1
		else:
			self.feedback_label.configure(text=f"X Wrong! Correct: {self.current_answer}", fg="#E53935")
		self._checked_current = True
		self._set_nav_enabled(True)
		# Disable answer entry after checking
		self.answer_entry.configure(state=tk.DISABLED)
		# Record this question log (only once per question)
		self._logs.append({
			"problem": self.current_problem,
			"answer": self.current_answer,
			"user": user,
			"correct": bool(correct_now),
		})

	def _next_guarded(self) -> None:
		if not self._checked_current:
			self.feedback_label.configure(text="Please check your answer first!", fg="#F2AB0C")
			return
		self._next()

	def _next(self) -> None:
		self.question_index += 1
		self.question_label.configure(text=f"Question {self.question_index}")
		problem, answer = self._gen_question()
		self.current_answer = answer
		self.current_problem = problem
		self.problem_canvas.itemconfig(self.problem_text, text=problem)
		# Re-enable answer entry for new question
		self.answer_entry.configure(state=tk.NORMAL)
		self.answer_entry.delete(0, tk.END)
		self.feedback_label.configure(text="")
		self.answer_entry.focus_set()
		self._checked_current = False
		self._set_nav_enabled(False)

	def _finish_guarded(self) -> None:
		if not self._checked_current:
			self.feedback_label.configure(text="Please check your answer first!", fg="#F2AB0C")
			return
		self._finish()

	def _finish(self) -> None:
		service = HighScoreService()
		service.record_attempt(self.mode, score=self.correct, total=self.question_index, questions=self._logs)
		self.navigator.show("home")
