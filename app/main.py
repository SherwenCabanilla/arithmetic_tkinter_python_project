import tkinter as tk
try:
	from .core.navigation import Navigator
	from .screens.home import HomeScreen
	from .utils.assets import load_icon
except ImportError:
	# Allow running this file directly: python app/main.py
	import sys
	from pathlib import Path
	sys.path.append(str(Path(__file__).resolve().parents[1]))
	from app.core.navigation import Navigator
	from app.screens.home import HomeScreen


def main() -> None:
	root = tk.Tk()
	root.title("Learn Bright")
	# Mobile-like portrait dimensions
	root.geometry("360x720")
	root.resizable(False, False)

	# Set window icon if logo exists
	try:
		# Window icon: keep small for titlebar
		icon = load_icon("logo.png") or load_icon("learn_bright_logo.png") or load_icon("learnbright.png")
		if icon is not None:
			# If very large, subsample to around 64px width
			if icon.width() > 64:
				factor = (icon.width() + 63) // 64
				icon = icon.subsample(factor, factor)
			root.iconphoto(True, icon)
	except Exception:
		pass

	navigator = Navigator(root)
	navigator.register_screen("home", HomeScreen)
	navigator.show("home")

	root.mainloop()


if __name__ == "__main__":
	main()
