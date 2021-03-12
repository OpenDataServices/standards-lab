web: env DEBUG=False sh -c 'cd /code/standards_lab && gunicorn --bind 0.0.0.0:80 wsgi:application'
worker: env DEBUG=False sh -c 'cd /code/standards_lab && python manage.py rqworker default'
