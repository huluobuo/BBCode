import sys
import os

# Add the script's directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Now import and run BBCode
from bbcode.main_window import main

if __name__ == "__main__":
    main()
