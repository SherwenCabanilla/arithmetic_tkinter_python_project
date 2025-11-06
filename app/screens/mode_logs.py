from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.lang import Builder
from ..ui.widgets.buttons import BackCircleButton
from ..services.high_score_service import HighScoreService
from ..utils.assets import resolve_image_path
import os

# Load the KV file
kv_path = os.path.join(os.path.dirname(__file__), 'mode_logs.kv')
Builder.load_file(kv_path)


class QuestionCard(BoxLayout):
	"""A single question card showing the question, answers, and result."""
	
	# Properties that will be used in the KV file
	index = NumericProperty(0)
	question_text = StringProperty('')
	your_answer = StringProperty('')
	correct_answer = StringProperty('')
	status_text = StringProperty('')
	top_icon = StringProperty('')  # Star or lightbulb at top
	status_icon = StringProperty('')  # Party or sad at bottom
	border_color = ListProperty([0, 0, 0, 1])
	your_box_color = ListProperty([0, 0, 0, 1])
	
	def __init__(self, question_data, index, is_correct, icons, **kwargs):
		# Set properties before calling super().__init__
		self.index = index
		self.question_text = question_data.get('problem', '')
		self.your_answer = str(question_data.get('user', ''))
		self.correct_answer = str(question_data.get('answer', ''))
		
		# Set colors and icons
		if is_correct:
			self.border_color = [0.13, 0.70, 0.00, 1]
			self.your_box_color = [0.13, 0.70, 0.00, 1]
			self.status_text = '[b]CORRECT![/b]'
			self.top_icon = icons['star'] or ''  # Star at top
			self.status_icon = icons['party'] or ''  # Party at bottom
		else:
			self.border_color = [0.90, 0.20, 0.20, 1]
			self.your_box_color = [0.90, 0.20, 0.20, 1]
			self.status_text = '[b]WRONG[/b]'
			self.top_icon = icons['bulb'] or ''  # Lightbulb at top
			self.status_icon = icons['sad'] or ''  # Sad at bottom
		
		super().__init__(**kwargs)


class ModeLogsScreen(Screen):
	def __init__(self, name: str, navigator, mode: str, **kwargs):
		super().__init__(name=name, **kwargs)
		self.navigator = navigator
		self.mode = mode
		self.service = HighScoreService()

		root = BoxLayout(orientation="vertical", padding=[16, 16, 16, 16], spacing=12)
		root.add_widget(BackCircleButton(diameter=40, icon_name="back_white.png", on_release=lambda _i: self.navigator.show("scores")))

		best = self.service.get_best(mode)
		
		# Date/time stamp in blue
		from datetime import datetime, timedelta
		if best and best.get("timestamp"):
			try:
				# Handle both old UTC timestamps (with Z) and new local timestamps
				timestamp_str = best["timestamp"]
				if timestamp_str.endswith("Z"):
					# Old UTC timestamp - convert to local time (Philippines is UTC+8)
					dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
					# Convert to Philippines time (UTC+8)
					dt = dt.replace(tzinfo=None) + timedelta(hours=8)
				else:
					# New local timestamp
					dt = datetime.fromisoformat(timestamp_str)
				date_str = dt.strftime("%b %d, %I:%M %p").upper()
				root.add_widget(Label(text=f"[color=10B6DF]{date_str}[/color]", markup=True, font_size=14, size_hint_y=None, height=20))
			except:
				pass
		
		# Score display
		if best:
			score = best.get('score', 0)
			total = best.get('total', 0)
			score_text = f"[b]{score} out of {total}[/b]"
			root.add_widget(Label(text=score_text, markup=True, font_size=30, size_hint_y=None, height=45, color=(0.2, 0.2, 0.2, 1)))

		scroll = ScrollView(size_hint=(1, 1))
		grid = GridLayout(cols=1, size_hint_y=None, spacing=15, padding=[0, 10, 0, 8])
		grid.bind(minimum_height=grid.setter('height'))

		if best and best.get("questions"):
			# Preload icon paths
			icons = {
				'star': resolve_image_path("star.png"),
				'bulb': resolve_image_path("lightbulb.png"),
				'party': resolve_image_path("party.png"),
				'sad': resolve_image_path("sad.png")
			}
			
			for idx, q in enumerate(best.get("questions", []), start=1):
				is_correct = bool(q.get("correct"))
				card = QuestionCard(q, idx, is_correct, icons)
				grid.add_widget(card)
		else:
			grid.add_widget(Label(text="No results yet for this mode.", size_hint_y=None, height=40))

		scroll.add_widget(grid)
		root.add_widget(scroll)
		self.add_widget(root)