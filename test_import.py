import sys
import os

# Add the project directory to sys.path
project_dir = r'd:\akademiya_murojat_bot'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import utils.utils
print(f"File path of utils.utils: {utils.utils.__file__}")
print(f"Attributes of utils.utils: {[a for a in dir(utils.utils) if not a.startswith('__')]}")

try:
    from utils.utils import get_course_code
    print("SUCCESS: get_course_code imported successfully")
except ImportError as e:
    print(f"FAILED to import get_course_code: {e}")
