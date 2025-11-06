"""
Simple script to convert logo.png to logo.ico for the EXE icon
"""
from PIL import Image

try:
    # Open the logo
    img = Image.open('assets/images/logo.png')
    
    # Convert to ICO with multiple sizes (for better quality at different resolutions)
    img.save('assets/images/logo.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    
    print("✅ Icon created successfully: assets/images/logo.ico")
    print("You can now build the EXE with: pyinstaller learnbright.spec")
    
except FileNotFoundError:
    print("❌ Error: logo.png not found in assets/images/")
    print("Make sure you have a logo.png file in the assets/images folder")
    
except ImportError:
    print("❌ Error: Pillow not installed")
    print("Install it with: pip install pillow")
    
except Exception as e:
    print(f"❌ Error: {e}")

