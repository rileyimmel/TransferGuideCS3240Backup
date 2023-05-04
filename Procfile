release: python manage.py migrate
web: gunicorn TransferCreditGuide.wsgi
worker: python -u run-worker.py
