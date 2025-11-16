# wsgi.py
"""
WSGI entry point for WonderFloyd.

Gunicorn or any other WSGI server will use the `app` object
imported from app.py as the application callable.
"""

from app import app

# Optional: allow local run as `python wsgi.py`
if __name__ == "__main__":
    app.run()
