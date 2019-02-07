"""
This copy of manage.py explicitly sets the minimum settings required to be
able to manage migrations for the request_token app, and no more. It is not
designed to be used to run a site.

"""
import os
import sys

if __name__ == "__main__":

    from django.conf import settings
    from django.core.management import execute_from_command_line

    settings.configure(
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "auto_scale"}
        },
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "rq_worker_auto_scale",
        ),
        SECRET_KEY="secret",
    )

    execute_from_command_line(sys.argv)
