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
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.core.window import Window
from kivy.clock import Clock
from ..config.paths import get_assets_dir
from ..ui.widgets.buttons import BackCircleButton
from ..utils.assets import resolve_image_path


class VideoSeekBar(Widget):
	"""Seekable progress bar with draggable thumb - like YouTube!"""
	def __init__(self, video_widget, **kwargs):
		super().__init__(**kwargs)
		self.video_widget = video_widget
		self.progress = 0.0  # 0.0 to 1.0
		self.is_dragging = False
		
		# Colors - kid-friendly!
		self.bg_color = (0.85, 0.85, 0.85, 1)  # Light gray
		self.progress_color = (0.96, 0.26, 0.21, 1)  # Red like YouTube #F54336
		self.thumb_color = (0.96, 0.26, 0.21, 1)  # Red thumb
		
		with self.canvas.before:
			# Background bar
			Color(*self.bg_color)
			self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[3])
			
			# Progress bar (filled part)
			Color(*self.progress_color)
			self.progress_rect = RoundedRectangle(pos=self.pos, size=(0, self.height), radius=[3])
			
			# Draggable thumb (circle)
			Color(*self.thumb_color)
			self.thumb = Ellipse(pos=(0, 0), size=(16, 16))
		
		self.bind(pos=self._update_graphics, size=self._update_graphics)
	
	def _update_graphics(self, *args):
		"""Update bar and thumb graphics"""
		# Background bar
		self.bg_rect.pos = self.pos
		self.bg_rect.size = self.size
		
		# Progress bar
		progress_width = self.width * self.progress
		self.progress_rect.pos = self.pos
		self.progress_rect.size = (progress_width, self.height)
		
		# Thumb position (centered on progress)
		thumb_x = self.x + progress_width - 8  # Center the 16px thumb
		thumb_y = self.y + (self.height / 2) - 8
		self.thumb.pos = (thumb_x, thumb_y)
	
	def update_progress(self, progress):
		"""Update progress (0.0 to 1.0)"""
		if not self.is_dragging:  # Don't update if user is dragging
			self.progress = max(0.0, min(1.0, progress))
			self._update_graphics()
	
	def _seek_to_position(self, x):
		"""Seek video to position based on x coordinate"""
		print(f"\n=== SEEK DEBUG START ===")
		print(f"Touch X: {x}, Bar X: {self.x}, Bar Width: {self.width}")
		
		if not self.video_widget:
			print("ERROR: No video widget!")
			return
		
		if self.video_widget.duration <= 0:
			print(f"ERROR: Duration not ready: {self.video_widget.duration}")
			return
		
		print(f"Video state: {self.video_widget.state}")
		print(f"Current position: {self.video_widget.position:.2f}")
		print(f"Duration: {self.video_widget.duration:.2f}")
		
		# Calculate percentage
		relative_x = x - self.x
		percentage = max(0.0, min(1.0, relative_x / self.width))
		print(f"Calculated percentage: {percentage*100:.1f}%")
		
		# Strict limit: don't allow seeking past 99.5% to prevent crash
		percentage = min(percentage, 0.995)
		print(f"After 99.5% cap: {percentage*100:.1f}%")
		
		# Update progress immediately for visual feedback
		self.progress = percentage
		self._update_graphics()
		
		# Seek video with multiple safety checks
		try:
			duration = self.video_widget.duration
			seek_position = percentage * duration
			print(f"Target seek position: {seek_position:.2f}s")
			
			# Safety: cap at 99.5% of duration
			max_safe_position = duration * 0.995
			seek_position = min(seek_position, max_safe_position)
			print(f"After 99.5% duration cap: {seek_position:.2f}s")
			
			# Additional safety: don't seek within 0.2 seconds of end
			seek_position = min(seek_position, duration - 0.2)
			print(f"After 0.2s buffer: {seek_position:.2f}s")
			
			print(f"CALLING seek method with PERCENTAGE (Kivy Video uses 0-1 range)")
			
			# Kivy Video.seek() expects a value between 0 and 1 (percentage of duration)
			# NOT seconds!
			seek_percent = seek_position / duration
			print(f"Seek percent: {seek_percent:.4f} ({seek_percent*100:.1f}%)")
			
			self.video_widget.seek(seek_percent)
			
			print(f"Called seek({seek_percent:.4f})")
			
			# Force position update
			from kivy.clock import Clock
			def check_position(dt):
				print(f"Position after seek: {self.video_widget.position:.2f}s")
			Clock.schedule_once(check_position, 0.2)
			
			print(f"=== SEEK DEBUG END ===\n")
			
		except Exception as e:
			print(f"ERROR during seek: {e}")
			print(f"=== SEEK DEBUG END ===\n")
	
	def on_touch_down(self, touch):
		"""Start dragging or seeking"""
		if self.collide_point(*touch.pos):
			# Allow seeking if video is loaded (any state except initial empty)
			if self.video_widget and self.video_widget.duration > 0:
				self.is_dragging = True
				self._seek_to_position(touch.x)
				touch.grab(self)
				return True
		return super().on_touch_down(touch)
	
	def on_touch_move(self, touch):
		"""Continue dragging"""
		if touch.grab_current is self:
			self._seek_to_position(touch.x)
			return True
		return super().on_touch_move(touch)
	
	def on_touch_up(self, touch):
		"""Stop dragging"""
		if touch.grab_current is self:
			self.is_dragging = False
			touch.ungrab(self)
			return True
		return super().on_touch_up(touch)


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
		self.seek_bar = None
		self.time_label = None
		self.update_event = None
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
		self.video_widget = Video(
			source="", 
			state="stop", 
			options={"eos": "stop"},  # Stop at end, don't loop
			allow_stretch=True
		)
		self.video_widget.fit_mode = "contain"
		self.video_widget.size_hint = (1, 1)
		self.video_widget.pos_hint = {"x": 0, "y": 0}
		self.video_widget.opacity = 0
		self.video_widget.allow_stretch = False
		self.video_widget.keep_ratio = True
		self.video_widget.bind(state=self._on_video_state_change)
		self.video_widget.bind(eos=self._on_video_end)
		inner.add_widget(self.video_widget)

		root.add_widget(video_frame)

		# Seekable progress bar with draggable thumb
		self.seek_bar = VideoSeekBar(self.video_widget, size_hint=(1, None), height=6)
		root.add_widget(self.seek_bar)
		
		# Small spacing
		root.add_widget(Widget(size_hint=(1, None), height=5))

		# Time label (current / total)
		self.time_label = Label(
			text="0:00 / 0:00",
			size_hint=(1, None),
			height=25,
			font_size=15,
			color=(0.4, 0.4, 0.4, 1)
		)
		root.add_widget(self.time_label)

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
			# Reset seek bar
			self.seek_bar.update_progress(0)
			# Update time label with video duration (after a brief delay for video to load)
			Clock.schedule_once(self._update_initial_time, 0.5)
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

	def _format_time(self, seconds):
		"""Format seconds to MM:SS"""
		if seconds < 0:
			return "0:00"
		mins = int(seconds // 60)
		secs = int(seconds % 60)
		return f"{mins}:{secs:02d}"
	
	def _update_initial_time(self, dt):
		"""Update time label with video duration after loading"""
		if self.video_widget and self.video_widget.duration > 0:
			total_time = self._format_time(self.video_widget.duration)
			self.time_label.text = f"0:00 / {total_time}"
	
	def _update_progress(self, dt):
		"""Update progress bar and time label while playing"""
		if not self.video_widget or not self._is_playing:
			return
		
		try:
			position = self.video_widget.position
			duration = self.video_widget.duration
			
			if duration > 0 and position >= 0:
				progress = position / duration
				
				# IMPORTANT: Only check for end if video is actually loaded and playing
				# duration > 10 means video is real (not the initial 1.0 placeholder)
				if duration > 10:
					# Safety check: stop very close to the end (at 99.5%)
					# Only 0.2 seconds before the actual end
					if (progress >= 0.995 or 
					    position >= (duration - 0.2) or 
					    (duration - position) < 0.2):
						print(f"Near end detected: position={position:.2f}, duration={duration:.2f}, progress={progress*100:.1f}%")
						self._on_video_end(self.video_widget)
						return
				
				# Update seek bar (cap at 99.5% for safety)
				safe_progress = min(progress, 0.995)
				self.seek_bar.update_progress(safe_progress)
				
				# Update time label
				current_time = self._format_time(position)
				total_time = self._format_time(duration)
				self.time_label.text = f"{current_time} / {total_time}"
		except Exception as e:
			print(f"Error in update_progress: {e}")
			# If there's any error, stop safely
			if self._is_playing:
				self._stop_video()
	
	def _on_video_end(self, instance):
		"""Called when video reaches the end - prevent looping and crashes"""
		print("Video ended - resetting for replay")
		
		# Stop update timer FIRST
		if self.update_event:
			self.update_event.cancel()
			self.update_event = None
		
		self._is_playing = False
		
		# Stop and reset video completely
		if self.video_widget:
			try:
				# First, unbind to prevent recursive calls
				self.video_widget.unbind(eos=self._on_video_end)
				self.video_widget.unbind(state=self._on_video_state_change)
				
				# Stop the video
				self.video_widget.state = "stop"
				
				# Wait a tiny bit, then seek to start
				def reset_video(dt):
					if self.video_widget:
						self.video_widget.seek(0)
						self.video_widget.position = 0
						# Rebind events
						self.video_widget.bind(eos=self._on_video_end)
						self.video_widget.bind(state=self._on_video_state_change)
						print("Video reset complete - ready to play again")
				
				Clock.schedule_once(reset_video, 0.1)
				
			except Exception as e:
				print(f"Error resetting video: {e}")
		
		# Restore poster
		self.poster.opacity = 1
		if self.video_widget:
			self.video_widget.opacity = 0
		
		# Reset seek bar to start
		self.seek_bar.update_progress(0)
		
		# Update time to show it's ready
		if self.video_widget and self.video_widget.duration > 0:
			total = self._format_time(self.video_widget.duration)
			self.time_label.text = f"0:00 / {total}"
		
		self._render_controls()
	
	def _on_video_state_change(self, instance, value):
		"""Handle video state changes (especially when video ends)"""
		if value == "stop":
			self._is_playing = False
			# Restore poster when video ends
			self.poster.opacity = 1
			self.video_widget.opacity = 0
			self.seek_bar.update_progress(0)
			self.time_label.text = "0:00 / 0:00"
			# Stop update timer
			if self.update_event:
				self.update_event.cancel()
				self.update_event = None
			self._render_controls()

	def _toggle_play(self) -> None:
		if self.video_widget is None:
			return
		if self.video_widget.state == "play":
			self.video_widget.state = "pause"
			self._is_playing = False
			# Stop progress updates when paused
			if self.update_event:
				self.update_event.cancel()
				self.update_event = None
		else:
			self.video_widget.state = "play"
			self._is_playing = True
			# Hide poster when playing
			self.poster.opacity = 0
			self.video_widget.opacity = 1
			# Start progress updates (30 FPS)
			if not self.update_event:
				self.update_event = Clock.schedule_interval(self._update_progress, 1/30)
		self._render_controls()

	def _stop_video(self) -> None:
		if self.video_widget is None:
			return
		self.video_widget.state = "stop"
		self._is_playing = False
		# Restore poster when stopped
		self.poster.opacity = 1
		self.video_widget.opacity = 0
		self.seek_bar.update_progress(0)
		self.time_label.text = "0:00 / 0:00"
		# Stop update timer
		if self.update_event:
			self.update_event.cancel()
			self.update_event = None
		self._render_controls()

	def on_pre_leave(self, *_):
		self._stop_video()

	def _back_to_learn(self) -> None:
		self._stop_video()
		self.navigator.show("learn")


