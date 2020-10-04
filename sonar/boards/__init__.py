"""
Add all the local board files
"""

import importlib
import os

files = os.listdir(os.path.dirname(__file__))
boards = [x for x in files if x not in ("__init__.py", "__pycache__")]
for board in boards:
    importlib.import_module(f"sonar.boards.{board}")
