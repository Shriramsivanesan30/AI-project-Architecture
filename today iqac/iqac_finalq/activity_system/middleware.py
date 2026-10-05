import secrets
from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class NoCacheMiddleware:
    """
    Middleware to prevent browser caching. This ensures that users cannot
    use the 'Back' button to view secure pages after they have logged out.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Generate a nonce for CSP
        request.csp_nonce = secrets.token_urlsafe(16)
        
        response = self.get_response(request)
        if 'text/html' in response.get('Content-Type', ''):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response


class SecurityHeadersMiddleware:
    """
    Injects critical security headers to achieve an A Grade:
    - Content-Security-Policy (CSP)
    - Strict-Transport-Security (HSTS)
    - Permissions-Policy
    - X-Content-Type-Options
    - X-Frame-Options
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Determine if local early to avoid NameError and ensure consistency
        host = request.get_host().split(':')[0].lower()
        is_local = host in ['127.0.0.1', 'localhost', 'testserver'] or \
                   host.startswith('192.168.') or \
                   host.startswith('10.') or \
                   host.startswith('172.')

        # 0. Redirection Logic (Mozilla Observatory Grade A+ Compliance)
        if not request.is_secure():
            if not is_local:
                # We stay on the EXACT same host (no stripping www or changing domains yet)
                # This satisfies the "Same Host HTTPS First" requirement
                url = f"https://{request.get_host()}{request.get_full_path()}"
                return HttpResponsePermanentRedirect(url)

        response = self.get_response(request)
        
        # 1. Content Security Policy (CSP)
        nonce = getattr(request, 'csp_nonce', '')
        
        if is_local:
            # Relaxed CSP for local development and institutional local network
            csp = (
                "default-src 'self' * data: blob:; "
                f"script-src 'self' 'nonce-{nonce}' 'unsafe-inline' 'unsafe-eval' *; "
                "style-src 'self' 'unsafe-inline' *; "
                "font-src 'self' data: *; "
                "img-src 'self' data: *; "
                "connect-src 'self' *; "
                "frame-ancestors 'none'; "
                "form-action 'self'; "
            )
        else:
            # Strict Mozilla Observatory Grade A+ CSP for Public Production
            upgrade_insecure = "upgrade-insecure-requests;"
            csp = (
                f"default-src 'self'; "
                f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic' https: http:; "
                f"style-src 'self' 'unsafe-inline' cdnjs.cloudflare.com fonts.googleapis.com; "
                f"font-src 'self' cdnjs.cloudflare.com fonts.gstatic.com data:; "
                f"img-src 'self' data: *; "
                f"connect-src 'self'; "
                f"frame-ancestors 'none'; "
                f"form-action 'self'; "
                f"base-uri 'self'; "
                f"object-src 'none'; "
                f"{upgrade_insecure}"
            )
        response['Content-Security-Policy'] = csp
        
        # 2. Strict-Transport-Security (HSTS)
        if not is_local:
            response['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'

        # 3. Permissions Policy
        response['Permissions-Policy'] = "geolocation=(), camera=(), microphone=(), payment=(), usb=()"

        # 4. Browser Hardening
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # 5. Cross-Origin Lockdown
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        
        return response
