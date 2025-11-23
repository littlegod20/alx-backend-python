#!/usr/bin/env python3
"""Middleware for logging user requests and restricting access by time.

"""
from datetime import datetime, timedelta
from django.http import HttpResponseForbidden, HttpResponseTooManyRequests
import threading


class RequestLoggingMiddleware:
    """Middleware to log user requests to a file.

    """
    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response
        self.log_file = 'requests.log'

    def __call__(self, request):
        """Process the request and log user information."""
        # Get user information
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = str(request.user)
        else:
            user = 'Anonymous'
        
        # Format log message
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        
        # Write to log file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)
        
        # Process the request
        response = self.get_response(request)
        
        return response


class RestrictAccessByTimeMiddleware:
    """Middleware to restrict access outside business hours (9AM-6PM).

    """
    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response
        self.start_hour = 9  # 9 AM
        self.end_hour = 18   # 6 PM

    def __call__(self, request):
        """Check current time and deny access if outside allowed hours."""
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Check if current hour is outside 9AM (9) and 6PM (18)
        if current_hour < self.start_hour or current_hour >= self.end_hour:
            return HttpResponseForbidden(
                "Access denied. The messaging app is only available between "
                "9:00 AM and 6:00 PM."
            )
        
        # Process the request if within allowed hours
        response = self.get_response(request)
        
        return response


class OffensiveLanguageMiddleware:
    """Middleware to limit message sending rate per IP address.

    """
    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response
        self.max_messages = 5  # Maximum messages allowed
        self.time_window = timedelta(minutes=1)  # Time window (1 minute)
        self.ip_requests = {}  # Dictionary to store IP addresses and timestamps
        self.lock = threading.Lock()  # Lock for thread-safe access

    def _get_client_ip(self, request):
        """Get the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _clean_old_requests(self, ip, current_time):
        """Remove timestamps older than the time window."""
        if ip in self.ip_requests:
            cutoff_time = current_time - self.time_window
            self.ip_requests[ip] = [
                timestamp for timestamp in self.ip_requests[ip]
                if timestamp > cutoff_time
            ]
            # Remove IP if no requests remain
            if not self.ip_requests[ip]:
                del self.ip_requests[ip]

    def __call__(self, request):
        """Check message rate limit for POST requests to message endpoints."""
        # Only check POST requests to message endpoints
        if request.method == 'POST' and '/messages' in request.path:
            current_time = datetime.now()
            client_ip = self._get_client_ip(request)
            
            # Thread-safe access to ip_requests dictionary
            with self.lock:
                # Clean old requests for this IP
                self._clean_old_requests(client_ip, current_time)
                
                # Check if IP exists in dictionary
                if client_ip not in self.ip_requests:
                    self.ip_requests[client_ip] = []
                
                # Check if limit is exceeded
                if len(self.ip_requests[client_ip]) >= self.max_messages:
                    return HttpResponseTooManyRequests(
                        "Rate limit exceeded. You can only send "
                        f"{self.max_messages} messages per minute."
                    )
                
                # Add current request timestamp
                self.ip_requests[client_ip].append(current_time)
            
            # Process the request if within limit
            response = self.get_response(request)
            return response
        
        # For non-POST requests or non-message endpoints, process normally
        response = self.get_response(request)
        return response


class RolePermissionMiddleware:
    """Middleware to check user role permissions.

    """
    def __init__(self, get_response):
        """Initialize the middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Check user role and deny access if not admin or moderator."""
        # Check if user is authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Get user role
            user_role = getattr(request.user, 'role', None)
            
            # Check if user is admin or moderator
            # Allow access only if user has admin or moderator role
            if user_role not in ['admin', 'moderator']:
                return HttpResponseForbidden(
                    "Access denied. Only administrators or moderators can access "
                    "this resource."
                )
        
        # Process the request if user is admin/moderator or not authenticated
        # (unauthenticated users will be handled by authentication middleware)
        response = self.get_response(request)
        
        return response
        