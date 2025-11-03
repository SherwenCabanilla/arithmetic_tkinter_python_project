import tkinter as tk
from datetime import datetime
from typing import Optional, Dict
from ..ui.widgets.containers import MobileFrame
from ..ui.widgets.buttons import BackCircleButton
from ..ui import theme
from ..services.high_score_service import HighScoreService
from ..utils.assets import load_icon


class ModeLogsScreen(MobileFrame):
	"""Screen showing detailed logs for a specific quiz mode."""

	def __init__(self, master: tk.Misc, navigator, mode: str) -> None:
		super().__init__(master)
		self.navigator = navigator
		self.mode = mode
		self.service = HighScoreService()

		# Load status icons (with fallback to emojis) - try both lowercase and uppercase
		self._icons = {
			"star": load_icon("star.png") or load_icon("STAR.png"),  # For correct answers
			"lightbulb": load_icon("lightbulb.png"),  # For incorrect answers
			"party": load_icon("party.png") or load_icon("PARTY.png"),  # For correct result badge
			"sad": load_icon("sad.png"),  # For wrong result badge
		}

		# Back button
		BackCircleButton(self, command=lambda: self.navigator.show("scores")).pack(anchor=tk.W, padx=16, pady=(16, 8))

		# Container for content (below back button)
		self._content_frame = tk.Frame(self, bg=theme.BG)
		self._content_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

		# Canvas for drawing
		self.canvas = tk.Canvas(self._content_frame, bg="#FFFFFF", highlightthickness=0)
		self.canvas.pack(fill=tk.BOTH, expand=True)

		self._render_content()

	def tkraise(self):
		"""Override to refresh when screen is shown."""
		super().tkraise()
		self.service.refresh()
		self._render_content()

	def _render_content(self) -> None:
		"""Render the mode logs content."""
		# Clear previous widgets
		if hasattr(self, '_logs_frame'):
			self._logs_frame.destroy()
		self.canvas.delete("all")

		best = self.service.get_best(self.mode)
		# Wait for canvas to be rendered
		self.update_idletasks()
		w = self.canvas.winfo_width()
		h = self.canvas.winfo_height()
		if w <= 1 or h <= 1:  # Not yet rendered, use defaults
			w = 336
			h = 600

		def _draw_rr(px1, py1, px2, py2, r, fill):
			x1, y1, x2, y2, r = map(int, (px1, py1, px2, py2, r))
			self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=fill, outline="")
			self.canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=fill, outline="")
			self.canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, fill=fill, outline="")
			self.canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, fill=fill, outline="")
			self.canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, fill=fill, outline="")
			self.canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, fill=fill, outline="")

		# Content panel
		panel_x1 = 0
		panel_y1 = 0
		panel_x2 = w
		panel_y2 = h
		self._rr(self.canvas, panel_x1, panel_y1, panel_x2, panel_y2, 18, fill="#FFFFFF", outline="", width=0)

		# Compute logs geometry
		logs_x1 = panel_x1 + 16
		logs_w = (panel_x2 - panel_x1) - 32
		
		# Operation name at the top - clear and catchy for kids
		operation_name = self.mode.title()  # e.g., "Addition", "Subtraction", etc.
		operation_y = 20  # Position at top with enough space
		header_x1 = logs_x1
		header_x2 = logs_x1 + logs_w
		self.canvas.create_text((header_x1 + header_x2) // 2, operation_y,
								text=operation_name, fill="#10B6DF", font=("Segoe UI", 22, "bold"),
								anchor=tk.CENTER)
		
		# Header: blue rounded rectangle (with space below operation name)
		header_y2 = 110  # More space below "Subtraction" text before the blue box
		header_y1 = header_y2 - 56
		logs_y1 = 56 + 36 + 70  # Adjusted to account for operation name and spacing
		logs_h = (panel_y2 - panel_y1) - logs_y1 - 20
		
		_draw_rr(header_x1, header_y1, header_x2, header_y2, 14, fill="#10B6DF")
		score_text = "None"
		if best:
			score_text = f"{best['score']}/{best['total']}"
		self.canvas.create_text((header_x1 + header_x2) // 2, (header_y1 + header_y2) // 2,
								text=score_text, fill="#FFFFFF", font=("Segoe UI", 16, "bold"))

		# Timestamp (blue text)
		ts = ""
		if best and best.get("timestamp"):
			try:
				d = datetime.fromisoformat(best["timestamp"].replace("Z", ""))
				ts = d.strftime("%b %d, %I:%M %p")
			except Exception:
				ts = best.get("timestamp", "")
		self.canvas.create_text((header_x1 + header_x2) // 2, header_y2 + 18,
								text=ts, fill="#10B6DF", font=("Segoe UI", 12, "bold"))

		# Scrollable frame for question cards
		logs_frame = tk.Frame(self.canvas, bg="#FFFFFF")
		scrollable = tk.Canvas(logs_frame, bg="#FFFFFF", highlightthickness=0)
		sb = tk.Scrollbar(logs_frame, orient=tk.VERTICAL, command=scrollable.yview)
		scrollable.configure(yscrollcommand=sb.set)
		
		# Inner frame for content
		inner_frame = tk.Frame(scrollable, bg="#FFFFFF")
		scroll_window = scrollable.create_window((0, 0), window=inner_frame, anchor=tk.NW)
		
		# Update scroll region when inner frame changes size
		def configure_scroll_region(event=None):
			# Update the scroll region to encompass all items
			scrollable.configure(scrollregion=scrollable.bbox("all"))
			# Keep inner frame width equal to scrollable canvas width
			canvas_width = scrollable.winfo_width()
			if canvas_width > 1:
				scrollable.itemconfig(scroll_window, width=canvas_width)
		
		def configure_scrollable_size(event):
			canvas_width = scrollable.winfo_width()
			if canvas_width > 1:
				scrollable.itemconfig(scroll_window, width=canvas_width)
			configure_scroll_region()
		
		# Enable mousewheel scrolling - define before binding
		def on_mousewheel(event):
			try:
				bbox = scrollable.bbox("all")
				if bbox and len(bbox) > 3:
					content_height = bbox[3]
					canvas_height = scrollable.winfo_height()
					if content_height > canvas_height:
						scrollable.yview_scroll(int(-1 * (event.delta / 120)), "units")
			except:
				pass
			return "break"
		
		inner_frame.bind("<Configure>", configure_scroll_region)
		scrollable.bind("<Configure>", configure_scrollable_size)
		
		# Bind mousewheel to all relevant widgets
		scrollable.bind("<MouseWheel>", on_mousewheel)
		logs_frame.bind("<MouseWheel>", on_mousewheel)
		inner_frame.bind("<MouseWheel>", on_mousewheel)
		
		scrollable.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		sb.pack(side=tk.RIGHT, fill=tk.Y)
		
		self.canvas.create_window(logs_x1, logs_y1, window=logs_frame, anchor=tk.NW, width=logs_w, height=logs_h)
		
		# Draw individual question cards
		if best and best.get("questions"):
			y_pos = 12
			card_width = logs_w - 24
			
			for idx, q in enumerate(best.get("questions", []), start=1):
				is_correct = q.get("correct", False)
				card_bg = "#E8F5E9" if is_correct else "#FFEBEE"  # Light green or light red
				border_color = "#3DAA3C" if is_correct else "#E53935"
				
				# Create card frame
				card = tk.Frame(inner_frame, bg=card_bg, relief=tk.FLAT)
				card.pack(fill=tk.X, padx=12, pady=8)
				
				# Card canvas for rounded corners and decoration
				card_canvas = tk.Canvas(card, bg=card_bg, highlightthickness=2, 
										highlightbackground=border_color, height=175, width=card_width)
				card_canvas.pack(fill=tk.BOTH, expand=True)
				
				# Get canvas dimensions after packing
				card.update_idletasks()
				cw = card_canvas.winfo_width()
				if cw <= 1 or cw > card_width:
					cw = card_width
				card_canvas.config(width=cw)
				
				# Question number badge (circular)
				badge_bg = "#3DAA3C" if is_correct else "#E53935"
				card_canvas.create_oval(10, 10, 40, 40, fill=badge_bg, outline="")
				card_canvas.create_text(25, 25, text=str(idx), fill="#FFFFFF", 
										font=("Segoe UI", 14, "bold"))
				
				# Status icon (right side) - use PNG if available, otherwise emoji
				if is_correct:
					icon_img = self._icons.get("star")
					if icon_img:
						icon_size = 28
						card_canvas.create_image(cw - 20, 25, image=icon_img, anchor=tk.CENTER)
					else:
						card_canvas.create_text(cw - 20, 25, text="⭐", 
												font=("Segoe UI", 24), fill="#FFD700")
				else:
					icon_img = self._icons.get("lightbulb")
					if icon_img:
						icon_size = 28
						card_canvas.create_image(cw - 20, 25, image=icon_img, anchor=tk.CENTER)
					else:
						card_canvas.create_text(cw - 20, 25, text="💡", 
												font=("Segoe UI", 24), fill="#FF9800")
				
				# Question text (centered, large and bold)
				problem_text = q['problem']
				center_x = cw // 2
				card_canvas.create_text(center_x, 38, text=problem_text, anchor=tk.CENTER,
										font=("Segoe UI", 20, "bold"), fill="#10B6DF")
				
				# Your answer section with box
				card_canvas.create_text(12, 70, text="Your", anchor=tk.W,
										font=("Segoe UI", 12, "bold"), fill="#666666")
				card_canvas.create_text(12, 85, text="Answer:", anchor=tk.W,
										font=("Segoe UI", 12, "bold"), fill="#666666")
				your_ans_bg = "#FFFFFF"
				box_x1 = 75
				box_x2 = 135
				card_canvas.create_rectangle(box_x1, 65, box_x2, 90, fill=your_ans_bg, 
											outline=border_color, width=3)
				card_canvas.create_text((box_x1 + box_x2) // 2, 77.5, text=str(q['user']), 
										font=("Segoe UI", 18, "bold"), 
										fill="#E53935" if not is_correct else "#3DAA3C")
				
				# Correct answer section with box
				card_canvas.create_text(12, 102, text="Correct", anchor=tk.W,
										font=("Segoe UI", 12, "bold"), fill="#666666")
				card_canvas.create_text(12, 117, text="Answer:", anchor=tk.W,
										font=("Segoe UI", 12, "bold"), fill="#666666")
				card_canvas.create_rectangle(box_x1, 97, box_x2, 122, fill="#E8F5E9", 
											outline="#3DAA3C", width=3)
				card_canvas.create_text((box_x1 + box_x2) // 2, 109.5, text=str(q['answer']), 
										font=("Segoe UI", 18, "bold"), fill="#3DAA3C")
				
				# Result badge at bottom right - text first, then icon (both right-aligned)
				# Position with more vertical padding from bottom
				result_y = 150  # Moved up a bit from bottom (card height is 175)
				result_color = "#3DAA3C" if is_correct else "#E53935"
				if is_correct:
					result_icon = self._icons.get("party")
					if result_icon:
						# Icon positioned further from right edge to avoid clipping
						icon_width = result_icon.width() if result_icon else 24
						icon_x = cw - 20 - icon_width // 6  # Move left to avoid clipping at right edge
						text_x = icon_x - icon_width // 2 - 10  # Position text to left of icon with spacing
						card_canvas.create_text(text_x, result_y, text="CORRECT!", anchor=tk.E,
												font=("Segoe UI", 14, "bold"), fill=result_color)
						card_canvas.create_image(icon_x, result_y, image=result_icon, anchor=tk.CENTER)
					else:
						card_canvas.create_text(cw - 15, result_y, text="CORRECT! 🎉", anchor=tk.E,
												font=("Segoe UI", 14, "bold"), fill=result_color)
				else:
					result_icon = self._icons.get("sad")
					if result_icon:
						# Icon positioned further from right edge to avoid clipping
						icon_width = result_icon.width() if result_icon else 24
						icon_x = cw - 20 - icon_width // 6  # Move left to avoid clipping at right edge
						text_x = icon_x - icon_width // 2 - 10  # Position text to left of icon with spacing
						card_canvas.create_text(text_x, result_y, text="WRONG", anchor=tk.E,
												font=("Segoe UI", 14, "bold"), fill=result_color)
						card_canvas.create_image(icon_x, result_y, image=result_icon, anchor=tk.CENTER)
					else:
						card_canvas.create_text(cw - 15, result_y, text="WRONG ☹️", anchor=tk.E,
												font=("Segoe UI", 14, "bold"), fill=result_color)
				
				y_pos += 183  # Updated to match new card height (175 + 8 padding)
		else:
			# Empty state
			empty_card = tk.Frame(inner_frame, bg="#FFFFFF")
			empty_card.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
			
			empty_canvas = tk.Canvas(empty_card, bg="#FFFFFF", highlightthickness=0, height=200)
			empty_canvas.pack(fill=tk.BOTH, expand=True)
			
			# Get actual canvas width
			empty_card.update_idletasks()
			canvas_w = empty_canvas.winfo_width()
			if canvas_w <= 1:
				canvas_w = logs_w
			
			empty_canvas.create_text(canvas_w // 2, 60, text="🎮", font=("Segoe UI", 48))
			empty_canvas.create_text(canvas_w // 2, 130, text="No Quiz Results Yet!",
									font=("Segoe UI", 18, "bold"), fill="#10B6DF", width=canvas_w - 40)
			empty_canvas.create_text(canvas_w // 2, 160, text="Play a quiz to see your\namazing results here!",
									font=("Segoe UI", 14), fill="#666666", width=canvas_w - 40, justify=tk.CENTER)
		
		# Update scroll region after all content is added
		inner_frame.update_idletasks()
		scrollable.update_idletasks()
		logs_frame.update_idletasks()
		
		# Force update of scroll region
		def finalize_scroll():
			bbox = scrollable.bbox("all")
			if bbox:
				scrollable.config(scrollregion=bbox)
			# Bind mousewheel to all cards
			for card in inner_frame.winfo_children():
				try:
					card.bind("<MouseWheel>", on_mousewheel)
					for subchild in card.winfo_children():
						try:
							subchild.bind("<MouseWheel>", on_mousewheel)
						except:
							pass
				except:
					pass
		
		finalize_scroll()
		# Also update after a short delay to ensure everything is rendered
		scrollable.after(100, finalize_scroll)
		
		# Store references
		self._logs_frame = logs_frame
		self._scrollable = scrollable
		self._inner_frame = inner_frame
		self._scrollbar = sb
		self._on_mousewheel = on_mousewheel  # Store reference for card bindings

	def _rr(self, canvas: tk.Canvas, x1, y1, x2, y2, r, **kwargs):
		pts = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
		return canvas.create_polygon(pts, smooth=True, **kwargs)

