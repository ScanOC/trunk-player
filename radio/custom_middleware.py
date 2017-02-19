from datetime import timedelta

from django.utils import timezone


EXTENDED_SESSION_DAYS = 60
class ExtendUserSession(object):
    """
    Extend authenticated user's sessions so they don't have to log back in
    every 2 weeks (set by Django's default `SESSION_COOKIE_AGE` setting). 
    """
    def process_request(self, request):
        # Only extend the session for auth'd users
        if request.user.is_authenticated():
            now = timezone.now()

            # Extend the session every day
            if request.session.get_expiry_date() < now + timedelta(days=( EXTENDED_SESSION_DAYS - 1)):
                request.session.set_expiry(EXTENDED_SESSION_DAYS * 86400) 
