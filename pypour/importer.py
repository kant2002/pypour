import importlib.abc
import importlib.machinery
import importlib.util
import sys
import os
from .transpiler import transpile


class PpourFinder(importlib.abc.MetaPathFinder):
    """Finds .ppour files on sys.path so they can be imported as modules."""

    def find_spec(self, fullname, path, target=None):
        parts = fullname.split(".")
        filename = parts[-1] + ".ppour"

        search_dirs = path if path else sys.path
        for d in search_dirs:
            ppour_path = os.path.join(d, filename)
            if os.path.isfile(ppour_path):
                return importlib.util.spec_from_loader(
                    fullname,
                    PpourLoader(ppour_path),
                    origin=ppour_path,
                )
        return None


class PpourLoader(importlib.abc.Loader):
    """Transpiles and loads a .ppour file as a Python module."""

    def __init__(self, path):
        self.path = path

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        with open(self.path, "r", encoding="utf-8") as f:
            source = f.read()
        python_source = transpile(source)
        module.__file__ = self.path
        # Add the directory to sys.path so nested imports work
        module_dir = os.path.dirname(os.path.abspath(self.path))
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
        code = compile(python_source, self.path, "exec")
        exec(code, module.__dict__)


def install():
    """Install the .ppour import hook if not already installed."""
    for finder in sys.meta_path:
        if isinstance(finder, PpourFinder):
            return
    sys.meta_path.append(PpourFinder())
