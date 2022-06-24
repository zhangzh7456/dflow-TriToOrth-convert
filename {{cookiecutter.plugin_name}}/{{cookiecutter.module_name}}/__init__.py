"""
{{cookiecutter.module_name}}
{{cookiecutter.short_description}}
"""
import sys
if sys.version_info < (3, 10):
    from importlib_metadata import version
else:
    from importlib.metadata import version
from .hello import Hello

__version__ = version("{{cookiecutter.module_name}}")
