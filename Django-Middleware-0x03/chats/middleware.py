#!/usr/bin/env python3
"""Middleware for logging user requests.

"""
from datetime import datetime


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

