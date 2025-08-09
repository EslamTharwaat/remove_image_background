"""
Authentication utilities for API endpoints
"""
from functools import wraps
from flask import request, jsonify, current_app


def require_bearer_token(f):
    """
    Decorator to require Bearer token authentication for API endpoints
    
    Usage:
        @require_bearer_token
        def protected_endpoint():
            return jsonify({"message": "success"})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if authentication is required
        if not current_app.config.get('API_REQUIRE_AUTH', True):
            return f(*args, **kwargs)
        
        # Get the Authorization header
        auth_header = request.headers.get(current_app.config.get('API_TOKEN_HEADER', 'Authorization'))
        
        if not auth_header:
            return jsonify({
                'error': 'Missing Authorization header',
                'message': 'Bearer token is required for API access'
            }), 401
        
        # Check if it's a Bearer token
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Invalid Authorization header format',
                'message': 'Authorization header must be in format: Bearer <token>'
            }), 401
        
        # Extract the token
        token = auth_header.split(' ')[1] if len(auth_header.split(' ')) == 2 else None
        
        if not token:
            return jsonify({
                'error': 'Invalid token format',
                'message': 'Bearer token cannot be empty'
            }), 401
        
        # Validate the token
        expected_token = current_app.config.get('API_BEARER_TOKEN')
        if token != expected_token:
            return jsonify({
                'error': 'Invalid token',
                'message': 'The provided Bearer token is invalid'
            }), 401
        
        # Token is valid, proceed with the request
        return f(*args, **kwargs)
    
    return decorated_function





def get_auth_info():
    """
    Get authentication information for API documentation
    
    Returns:
        dict: Authentication requirements and example
    """
    return {
        'required': current_app.config.get('API_REQUIRE_AUTH', True),
        'type': 'Bearer Token',
        'header': current_app.config.get('API_TOKEN_HEADER', 'Authorization'),
        'format': 'Bearer <token>',
        'example': f"Bearer {current_app.config.get('API_BEARER_TOKEN', 'your-token-here')}"
    }
