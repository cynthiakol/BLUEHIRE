"""
Custom middleware to bypass allauth's ugly signup page
"""
from django.shortcuts import redirect
from django.urls import reverse


class SocialSignupRedirectMiddleware:
    """
    Intercepts allauth's social signup page and redirects to our custom page
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if '/logout' in request.path.lower():
            response = self.get_response(request)
            return response
        
        if '/signin_register' in request.path.lower() or '/signin-register' in request.path.lower():
            response = self.get_response(request)
            return response
        
        if '/accounts/google/login/callback/' in request.path or \
           '/accounts/facebook/login/callback/' in request.path or \
           'socialaccount/signup' in request.path:
            
            if request.user.is_authenticated:
                if request.user.is_superuser or request.user.is_staff or request.user.role == 'Admin':
                    return redirect('/system-admin/dashboard/')
                
                if request.user.role == 'JobSeeker':
                    return redirect('/accounts/jobseeker/dashboard/')
                elif request.user.role == 'Employer':
                    return redirect('/accounts/employer/dashboard/')
                
                if not request.user.role:
                    return redirect('/select-role/')
        
        response = self.get_response(request)
        return response