import os
import importlib

files = os.listdir(os.path.dirname(__file__))
boards = [x for x in files if x != "__init__.py" and x != "__pycache__"]
for board in boards:
    importlib.import_module(f"sonar.boards.{board}")
