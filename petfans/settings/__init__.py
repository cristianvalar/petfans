# Import settings from the appropriate environment
import os

# Default to local settings
environment = os.environ.get('DJANGO_ENVIRONMENT', 'local')

if environment == 'production':
    from .prod import *
else:
    from .local import *
