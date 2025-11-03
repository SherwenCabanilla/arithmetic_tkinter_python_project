import tkinter as tk
from tkinter import messagebox
import sys
import os
import webbrowser
from pathlib import Path

from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import BackCircleButton
from ..ui import theme
from ..config.paths import get_assets_dir, get_project_root


class LessonScreen(MobileFrame):
	"""Topic detail screen with embedded video and playback controls."""

	def __init__(self, master: tk.Misc, navigator) -> None:
		super().__init__(master)
		self.navigator = navigator
		self.topic: str = ""
		self.title_label = None
		self._vlc = None
		self._vlc_instance = None
		self._vlc_player = None
		self._tkvideo_player = None  # fallback player

		BackCircleButton(self, command=self._go_back).pack(anchor=tk.W, padx=16, pady=(16, 8))

		# Friendly, kid-focused title
		self.title_label = tk.Label(self, text="", bg=theme.BG, fg="#FF6F00", font=theme.TITLE_FONT)
		self.title_label.pack(pady=(0, 8))
		subtitle = tk.Label(self, text="Let's learn with a short video!", bg=theme.BG, fg="#8D6E63", font=theme.SUBTITLE_FONT)
		subtitle.pack(pady=(0, 8))

		# Rounded video frame (colorful border)
		frame_canvas = tk.Canvas(self, width=312, height=192, bg=theme.BG, highlightthickness=0)
		frame_canvas.pack(pady=(0, 12))
		# draw rounded rect border
		def rounded_rect(c, x1, y1, x2, y2, r, color):
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
			return c.create_polygon(points, smooth=True, fill=color, outline="")
		radius = 18
		rounded_rect(frame_canvas, 2, 2, 310, 190, radius, "#FFA726")  # orange border

		# Actual video area sits inside with small margin
		self.video_canvas = tk.Canvas(frame_canvas, width=300, height=180, bg="#000000", highlightthickness=0)
		self.video_canvas.place(x=6, y=6)

		# Big colorful controls
		controls = tk.Frame(self, bg=theme.BG)
		controls.pack(pady=(0, 16))
		self.play_pause_btn = tk.Button(controls, text="▶ Play", command=self._toggle_play, bd=0, bg="#17B3E6", fg="#FFFFFF", font=theme.BUTTON_FONT, padx=22, pady=10)
		self.play_pause_btn.pack(side=tk.LEFT, padx=8)
		self.stop_btn = tk.Button(controls, text="⏹ Stop", command=self._stop, bd=0, bg="#FF5252", fg="#FFFFFF", font=theme.BUTTON_FONT, padx=22, pady=10)
		self.stop_btn.pack(side=tk.LEFT, padx=8)

		# Kid-friendly short summary container (below controls)
		self.summary_outer = tk.Frame(self, bg=theme.BG, highlightbackground="#8E66E3", highlightthickness=2)
		self.summary_outer.pack(padx=12, pady=(0, 16), fill=tk.X)
		self.summary_inner = tk.Frame(self.summary_outer, bg="#FFFFFF")
		self.summary_inner.pack(padx=10, pady=10, fill=tk.X)
		self.summary_title = tk.Label(self.summary_inner, text="Short Summary:", bg="#FFFFFF", fg=theme.TEXT, font=("Segoe UI", 11, "bold"), anchor=tk.W)
		self.summary_title.pack(anchor=tk.W)
		self.summary_text = tk.Label(self.summary_inner, text="", bg="#FFFFFF", fg=theme.TEXT, font=("Segoe UI", 10), justify=tk.LEFT, wraplength=280)
		self.summary_text.pack(anchor=tk.W, pady=(4, 0))


		self._prepare_vlc()
		self._prepare_tkvideo_fallback()

	def apply_context(self, topic: str) -> None:
		self.topic = topic
		titles = {
			"addition": "ADDITION",
			"subtraction": "SUBTRACTION",
			"multiplication": "MULTIPLICATION",
			"division": "DIVISION",
		}
		if self.title_label is not None:
			self.title_label.config(text=titles.get(topic, topic).upper())
		self._load_video_for_topic()
		self._load_summary_for_topic()

	def _load_summary_for_topic(self) -> None:
		bullets = {
			"addition": (
				"Adding puts numbers together to make a bigger number.\n"
				"• Example: 3 + 2 = 5\n"
				"• The order doesn’t matter: 2 + 3 = 3 + 2\n"
				"• The answer is called the sum"
			),
			"subtraction": (
				"Subtraction takes away to make a smaller number.\n"
				"• Example: 7 − 4 = 3\n"
				"• Think of ‘how many are left?’\n"
				"• The answer is called the difference"
			),
			"multiplication": (
				"Multiplication is fast repeated addition.\n"
				"• Example: 3 × 4 = 12 (that’s 3 + 3 + 3 + 3)\n"
				"• ‘×’ means groups of\n"
				"• The answer is called the product"
			),
			"division": (
				"Division shares or splits into equal groups.\n"
				"• Example: 12 ÷ 3 = 4 (3 equal groups of 4)\n"
				"• ‘÷’ means share equally\n"
				"• The answer is called the quotient"
			),
		}
		text = bullets.get(self.topic, "")
		self.summary_text.config(text=text)

	def _bind_window(self) -> None:
		if self._vlc_player is None:
			return
		wid = self.video_canvas.winfo_id()
		try:
			if sys.platform.startswith("win"):
				self._vlc_player.set_hwnd(wid)
			elif sys.platform == "darwin":
				self._vlc_player.set_nsobject(wid)
			else:
				self._vlc_player.set_xwindow(wid)
		except Exception:
			pass

	def _load_video_for_topic(self) -> None:
		if self._vlc_player is None and self._tkvideo_player is None:
			# No embedded backend; open externally so user can still watch
			messagebox.showwarning("Video", "Embedded player not available. Opening with system player.")
			self._open_external(path)
			return
		videos = {
			"addition": "Basic_Addition.mp4",
			"subtraction": "Basic_Subtraction.mp4",
			"multiplication": "Basic_Multiplication.mp4",
			"division": "Basic_Division.mp4",
		}
		asset = videos.get(self.topic)
		if not asset:
			messagebox.showerror("Video", f"No video mapped for topic: {self.topic}")
			return
		path: Path = get_assets_dir() / "video" / asset
		if not path.exists():
			messagebox.showerror("Video", f"Video file not found:\n{path}")
			return
		if self._vlc_player is not None:
			media = self._vlc_instance.media_new_path(str(path))  # type: ignore[union-attr]
			self._vlc_player.set_media(media)
			self._bind_window()
			self._vlc_player.stop()
			self.play_pause_btn.config(text="▶ Play")
		elif self._tkvideo_player is not None:
			# Configure tkVideoPlayer
			self._tkvideo_player.load(str(path))
			self.play_pause_btn.config(text="▶ Play")

	def _toggle_play(self) -> None:
		if self._vlc_player is None and self._tkvideo_player is None:
			return
		if self._vlc_player is not None:
			state = self._vlc_player.get_state()
			if self._vlc is not None and state in (self._vlc.State.Playing, self._vlc.State.Buffering):  # type: ignore[union-attr]
				self._vlc_player.pause()
				self.play_pause_btn.config(text="▶ Play")
			else:
				self._vlc_player.play()
				self.play_pause_btn.config(text="⏸ Pause")
		elif self._tkvideo_player is not None:
			if self._tkvideo_player.is_paused():
				self._tkvideo_player.play()
				self.play_pause_btn.config(text="⏸ Pause")
			else:
				self._tkvideo_player.pause()
				self.play_pause_btn.config(text="▶ Play")

	def _stop(self) -> None:
		if self._vlc_player is not None:
			self._vlc_player.stop()
		if self._tkvideo_player is not None:
			self._tkvideo_player.stop()
		self.play_pause_btn.config(text="▶ Play")

	def _go_back(self) -> None:
		self._stop()
		self.navigator.show("learn")

	def _prepare_vlc(self) -> None:
		"""Try to import VLC and configure DLL search on Windows automatically."""
		# If already prepared, skip
		if self._vlc_player is not None or self._vlc is not None:
			return

		# On Windows, add VLC install dir to DLL search path if it exists
		if sys.platform.startswith("win"):
			# 0) Project-local override via vlc_dir.txt (put install path inside)
			try:
				path_file = get_project_root() / "vlc_dir.txt"
				if path_file.exists():
					custom = path_file.read_text(encoding="utf-8").strip().strip('"')
					if custom and os.path.isdir(custom):
						try:
							os.add_dll_directory(custom)
							os.environ.setdefault("PYTHON_VLC_MODULE_PATH", custom)
						except Exception:
							pass
			except Exception:
				pass
			# 1) Manual override via environment variable (recommended if custom install)
			manual = os.environ.get("VLC_DIR") or os.environ.get("LIBVLC_PATH") or os.environ.get("PYTHON_VLC_MODULE_PATH")
			if manual and os.path.isdir(manual):
				try:
					os.add_dll_directory(manual)
					os.environ.setdefault("PYTHON_VLC_MODULE_PATH", manual)
				except Exception:
					pass
			common_paths = [
				r"C:\\Program Files\\VideoLAN\\VLC",
				r"C:\\Program Files (x86)\\VideoLAN\\VLC",
			]
			for path in common_paths:
				if os.path.isdir(path):
					try:
						os.add_dll_directory(path)  # Python 3.8+
						os.environ.setdefault("PYTHON_VLC_MODULE_PATH", path)
					except Exception:
						pass
			# Try Windows Registry for VLC InstallDir
			try:
				import winreg  # type: ignore
				for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
					for subkey in (
						"SOFTWARE\\VideoLAN\\VLC",
						"SOFTWARE\\WOW6432Node\\VideoLAN\\VLC",
					):
						try:
							k = winreg.OpenKey(hive, subkey)
							install_dir, _ = winreg.QueryValueEx(k, "InstallDir")
							if os.path.isdir(install_dir):
								try:
									os.add_dll_directory(install_dir)
									os.environ.setdefault("PYTHON_VLC_MODULE_PATH", install_dir)
								except Exception:
									pass
						finally:
							try:
								winreg.CloseKey(k)  # type: ignore
							except Exception:
								pass
			except Exception:
				pass

		# Lazy import python-vlc
		try:
			import importlib
			self._vlc = importlib.import_module("vlc")
		except Exception:
			self._vlc = None
			return

		try:
			self._vlc_instance = self._vlc.Instance()
			self._vlc_player = self._vlc_instance.media_player_new()
			self.after(100, self._bind_window)
		except Exception:
			self._vlc_instance = None
			self._vlc_player = None

	def _prepare_tkvideo_fallback(self) -> None:
		"""Prepare tkVideoPlayer as a pure-Python fallback if available."""
		try:
			from tkVideoPlayer import TkinterVideo  # type: ignore
			self._tkvideo_player = TkinterVideo(master=self, scaled=True, background="#000000")
			# Place it exactly where the canvas sits
			self._tkvideo_player.place(in_=self.video_canvas, x=0, y=0, width=self.video_canvas.winfo_reqwidth(), height=self.video_canvas.winfo_reqheight())
		except Exception:
			self._tkvideo_player = None

	def _open_external(self, path: Path) -> None:
		try:
			if hasattr(os, "startfile"):
				os.startfile(str(path))  # type: ignore[attr-defined]
			else:
				webbrowser.open(path.as_uri())
		except Exception:
			pass


