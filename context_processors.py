"""Site-wide context processors."""
from django.conf import settings

def static_media(request):
    """Just add the STATIC URL to context."""
    return {
        'STATIC_URL': getattr(settings, 'STATIC_URL', None)
    }
