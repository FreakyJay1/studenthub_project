#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studenthub_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Override DATABASES for migrate and makemigrations commands
    if sys.argv[1] in ['migrate', 'makemigrations']:
        from django.conf import settings

        settings.DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',  # Use SQLite in-memory
                'NAME': ':memory:',
            }
        }
        # Configure settings only if they haven't been configured yet
        if not settings.configured:
            settings.configure()

    execute_from_command_line(sys.argv)