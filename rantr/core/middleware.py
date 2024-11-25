import time
import logging
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        start_time = time.time()
        
        # Count database queries before request
        queries_before = len(connection.queries)
        
        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called.
        if settings.DEBUG:
            # Calculate request execution time
            execution_time = time.time() - start_time
            
            # Count database queries after request
            queries_after = len(connection.queries)
            queries_count = queries_after - queries_before
            
            # Log performance metrics
            logger.debug(f"""
                Performance Metrics for {request.path}:
                Execution Time: {execution_time:.2f}s
                Database Queries: {queries_count}
                Method: {request.method}
                User: {request.user}
            """)
            
            # Add custom header with performance metrics
            response['X-Page-Execution-Time'] = f"{execution_time:.2f}s"
            response['X-Page-Query-Count'] = str(queries_count)
        
        return response


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] = 'nosniff'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['X-XSS-Protection'] = '1; mode=block'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cache = {}
        self.rate_limit = 100  # requests per minute
        self.window = 60  # seconds

    def __call__(self, request):
        if not settings.DEBUG:
            client_ip = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old entries
            self.clean_old_entries(current_time)
            
            # Check rate limit
            if self.is_rate_limited(client_ip, current_time):
                from django.http import HttpResponseTooManyRequests
                return HttpResponseTooManyRequests("Rate limit exceeded")
            
            # Add request to cache
            self.cache.setdefault(client_ip, []).append(current_time)
        
        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

    def clean_old_entries(self, current_time):
        for ip in list(self.cache.keys()):
            self.cache[ip] = [
                timestamp for timestamp in self.cache[ip]
                if current_time - timestamp < self.window
            ]
            if not self.cache[ip]:
                del self.cache[ip]

    def is_rate_limited(self, client_ip, current_time):
        return (
            client_ip in self.cache and
            len([t for t in self.cache[client_ip] if current_time - t < self.window]) >= self.rate_limit
        )
