"""
WSGI config for itassets project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import confy
import os
from pathlib import Path

# These lines are required for interoperability between local and container environments.
d = Path(__file__).resolve().parents[1]
dot_env = os.path.join(str(d), '.env')
if os.path.exists(dot_env):
    confy.read_environment_file(dot_env)  # Must precede dj_static imports.

from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itassets.settings')
application = Cling(MediaCling(get_wsgi_application()))
