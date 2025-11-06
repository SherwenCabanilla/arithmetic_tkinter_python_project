import tkinter as tk
from tkinter import messagebox
import sys
import os
import webbrowser
from pathlib import Path

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.video import Video
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.core.window import Window
from ..config.paths import get_assets_dir
from ..ui.widgets.buttons import BackCircleButton
from ..utils.assets import resolve_image_path


class LessonScreen(Screen):
	def __init__(self, name: str, navigator, **kwargs):
		super().__init__(name=name, **kwargs)
		self.navigator = navigator
		self.topic = ""
		self.video_widget = None
		self.title_label = None
		self.summary_label = None
		self._is_playing = False
		self.controls_bar = None
		self._build()

	def _build(self) -> None:
		Window.size = (360, 720)
		root = BoxLayout(orientation="vertical", padding=[16, 16, 16, 16], spacing=12)

		# Header: back and small logo
		header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=52)
		header.add_widget(BackCircleButton(diameter=40, icon_name="back_white.png", on_release=lambda _i: self._back_to_learn()))
		header.add_widget(Widget())
		logo_path = str(get_assets_dir() / "images" / "logo.png")
		header.add_widget(Image(source=logo_path, size_hint=(None, None), size=(140, 60)))
		root.add_widget(header)


		# Add spacing between header and title
		root.add_widget(Widget(size_hint=(1, None), height=20))

		# Title
		self.title_label = Label(text="", markup=True, font_size=32, bold=True, size_hint_y=None, height=50)
		root.add_widget(self.title_label)

		# Video container (no border)
		video_frame = FloatLayout(size_hint=(1, None), height=200)

		# Inner padded area
		inner = FloatLayout(size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
		video_frame.add_widget(inner)


		# Poster thumbnail (shown until playback)
		self.poster = Image(source="", allow_stretch=True, keep_ratio=True, size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
		inner.add_widget(self.poster)

		# Video widget (fit inside container)
		self.video_widget = Video(source="", state="stop", options={"eos": "pause"})
		self.video_widget.fit_mode = "contain"
		self.video_widget.size_hint = (1, 1)
		self.video_widget.pos_hint = {"x": 0, "y": 0}
		self.video_widget.opacity = 0
		inner.add_widget(self.video_widget)

		root.add_widget(video_frame)

		# Controls below the video, centered
		self.controls_bar = BoxLayout(orientation="horizontal", size_hint=(1, None), height=56)
		self._render_controls()
		root.add_widget(self.controls_bar)

		# Summary card (white background + subtle gray border)
		summary_outer = BoxLayout(orientation="vertical", size_hint=(1, None), height=260, padding=[0, 0, 0, 0])
		with summary_outer.canvas.before:
			Color(0.82, 0.84, 0.87, 1)  # light gray border
			self._summary_border = RoundedRectangle(radius=[12])
		summary_outer.bind(pos=self._update_summary_border, size=self._update_summary_border)

		summary_inner = BoxLayout(orientation="vertical", padding=[12, 12, 12, 12])
		with summary_inner.canvas.before:
			Color(1, 1, 1, 1)
			self._summary_bg = RoundedRectangle(radius=[12])
		summary_inner.bind(pos=lambda inst, *_: self._update_summary_bg(inst), size=lambda inst, *_: self._update_summary_bg(inst))

		summary_title = Label(text="Short Summary:", bold=True, color=(0.149, 0.196, 0.22, 1), size_hint=(1, None), height=24, halign="left", valign="middle")
		summary_title.bind(size=lambda inst, _: setattr(inst, 'text_size', inst.size))
		summary_inner.add_widget(summary_title)

		self.summary_label = Label(text="", halign="left", valign="top", color=(0.149, 0.196, 0.22, 1))
		self.summary_label.bind(size=lambda inst, _: setattr(inst, 'text_size', inst.size))
		summary_inner.add_widget(self.summary_label)

		summary_outer.add_widget(summary_inner)
		root.add_widget(summary_outer)

		root.add_widget(Widget())
		self.add_widget(root)

	def _render_controls(self):
		self.controls_bar.clear_widgets()
		left = Widget()
		center = BoxLayout(orientation="horizontal", size_hint=(None, None), height=56, width=120, spacing=14)
		right = Widget()
		play_icon = "pause_white.png" if self._is_playing else "play_white.png"
		play_btn = BackCircleButton(diameter=55, icon_name=play_icon)
		play_btn.bind(on_release=lambda _i: self._toggle_play())
		stop_btn = BackCircleButton(diameter=55, icon_name="stop_white.png")
		stop_btn.bind(on_release=lambda _i: self._stop_video())
		center.add_widget(play_btn)
		center.add_widget(stop_btn)
		self.controls_bar.add_widget(left)
		self.controls_bar.add_widget(center)
		self.controls_bar.add_widget(right)

	def _update_video_border(self, *_):
		# No border currently; keep as no-op to avoid callback errors
		return

	def _update_summary_border(self, instance, *_):
		self._summary_border.pos = instance.pos
		self._summary_border.size = instance.size

	def _update_summary_bg(self, instance):
		self._summary_bg.pos = instance.pos
		self._summary_bg.size = instance.size

	def apply_context(self, topic: str) -> None:
		self.topic = topic
		titles = {
			"addition": "[color=FF6F00][b]ADDITION[/b][/color]",
			"subtraction": "[color=FF6F00][b]SUBTRACTION[/b][/color]",
			"multiplication": "[color=FF6F00][b]MULTIPLICATION[/b][/color]",
			"division": "[color=FF6F00][b]DIVISION[/b][/color]",
		}
		self.title_label.text = titles.get(topic, topic.upper())
		self._load_video_and_summary()

	def _load_video_and_summary(self) -> None:
		videos = {
			"addition": "Basic_Addition.mp4",
			"subtraction": "Basic_Subtraction.mp4",
			"multiplication": "Basic_Multiplication.mp4",
			"division": "Basic_Division.mp4",
		}
		asset = videos.get(self.topic)
		if asset:
			self.video_widget.source = str(get_assets_dir() / "video" / asset)
			self.video_widget.state = "stop"
			self._is_playing = False
			# Set poster image for the topic
			poster_map = {
				"addition": "addition_thumb.png",
				"subtraction": "subtraction_thumb.png",
				"multiplication": "multiplication_thumb.png",
				"division": "division_thumb.png",
			}
			poster_name = poster_map.get(self.topic, "")
			poster_path = resolve_image_path(poster_name) if poster_name else None
			self.poster.source = poster_path or ""
			self.poster.opacity = 1
			self.video_widget.opacity = 0
			self._render_controls()

		bullets = {
			"addition": (
				"Addition is the math operation where you combine two or more numbers to find out how many there are in total.\nFor example:\n\n"
				"• If you have 2 apples and you get 3 more apples, you add them: 2 + 3 = 5 apples.\n"
				"• It’s often shown with the ‘+’ symbol.\n"
				"• It’s one of the first operations children learn, because it’s the building block for lots of other things (like subtraction, multiplication, etc)."
			),
			"subtraction": (
				"Subtraction takes away to make a smaller number.\n"
				"• Example: 7 − 4 = 3.\n"
				"• Think of ‘how many are left?’.\n"
				"• The answer is called the difference."
			),
			"multiplication": (
				"Multiplication is fast repeated addition.\n"
				"• Example: 3 × 4 = 12 (3 + 3 + 3 + 3).\n"
				"• ‘×’ means groups of.\n"
				"• The answer is called the product."
			),
			"division": (
				"Division shares or splits into equal groups.\n"
				"• Example: 12 ÷ 3 = 4.\n"
				"• ‘÷’ means share equally.\n"
				"• The answer is called the quotient."
			),
		}
		self.summary_label.text = bullets.get(self.topic, "")

	def _toggle_play(self) -> None:
		if self.video_widget is None:
			return
		if self.video_widget.state == "play":
			self.video_widget.state = "pause"
			self._is_playing = False
		else:
			self.video_widget.state = "play"
			self._is_playing = True
			# Hide poster when playing
			self.poster.opacity = 0
			self.video_widget.opacity = 1
		self._render_controls()

	def _stop_video(self) -> None:
		if self.video_widget is None:
			return
		self.video_widget.state = "stop"
		self._is_playing = False
		# Restore poster when stopped
		self.poster.opacity = 1
		self.video_widget.opacity = 0
		self._render_controls()

	def on_pre_leave(self, *_):
		self._stop_video()

	def _back_to_learn(self) -> None:
		self._stop_video()
		self.navigator.show("learn")


