import tkinter as tk
try:
	from .core.navigation import Navigator
	from .screens.home import HomeScreen
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

	navigator = Navigator(root)
	navigator.register_screen("home", HomeScreen)
	navigator.show("home")

	root.mainloop()


if __name__ == "__main__":
	main()
