import os,sys

sys.path.append('/var/www/one_month')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "one_month.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
