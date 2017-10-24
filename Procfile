web: gunicorn config.wsgi:application
worker: celery worker --app=tenkobo.taskapp --loglevel=info
