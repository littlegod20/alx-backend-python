#!/usr/bin/env python3
"""Middleware for logging user requests and restricting access by time.

"""
from datetime import datetime
from django.http import HttpResponseForbidden


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
        