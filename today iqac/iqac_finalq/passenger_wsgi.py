import os
import sys
from django.core.wsgi import get_wsgi_application

# Add your project directory to the sys.path
# In cPanel, this should point to your Application root folder (e.g., /home/username/mcet)
script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, script_dir)

# Tell Django where your settings module is
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_activity_system.settings')

# Initialize Django WSGI application
application = get_wsgi_application()
