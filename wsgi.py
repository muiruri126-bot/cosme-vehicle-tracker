"""
WSGI entry point for PythonAnywhere deployment.
PythonAnywhere will import `application` from this module.
"""

from app import app as application  # noqa: F401
