from rest_framework.throttling import AnonRateThrottle

class AuthenticationThrottle(AnonRateThrottle):
    scope = "auth"