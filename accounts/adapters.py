"""
Custom allauth adapter for BlueHire social login
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from accounts.models import Users, JobSeeker, Employer
import random


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle social login behavior
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before social login is completed
        """
        print(f"\n{'='*60}")
        print(f"🔍 PRE_SOCIAL_LOGIN CALLED")
        print(f"Provider: {sociallogin.account.provider}")
        print(f"Is existing: {sociallogin.is_existing}")
        print(f"User authenticated: {request.user.is_authenticated}")
        
        try:
            # ✅ FIX: Check for orphaned social accounts
            if sociallogin.is_existing:
                print(f"Checking existing social account...")
                try:
                    # Try to access the user - this will raise DoesNotExist if orphaned
                    user = sociallogin.account.user
                    print(f"✅ Social account linked to user: {user.email}")
                except Users.DoesNotExist:
                    # Delete the orphaned social account and treat as new login
                    print(f"⚠️ ORPHANED SOCIAL ACCOUNT FOUND - Deleting ID: {sociallogin.account.id}")
                    sociallogin.account.delete()
                    sociallogin.account = None
                    print(f"✅ Orphaned account deleted - continuing as new signup")
                    print(f"{'='*60}\n")
                    # Let the flow continue as a new signup
                    return
            
            if request.user.is_authenticated:
                print(f"User already authenticated - connecting social account")
                sociallogin.connect(request, request.user)
                print(f"{'='*60}\n")
                return
            
            if sociallogin.email_addresses:
                email = sociallogin.email_addresses[0].email
                print(f"Email from social login: {email}")
                
                try:
                    user = Users.objects.get(email=email)
                    print(f"✅ Found existing user with email: {email}")
                    
                    extra_data = sociallogin.account.extra_data
                    new_username = email.split('@')[0]
                    
                    if user.pk:
                        if Users.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                            new_username = f"{new_username}{random.randint(100, 999)}"
                    else:
                        if Users.objects.filter(username=new_username).exists():
                            new_username = f"{new_username}{random.randint(100, 999)}"
                    
                    user.username = new_username
                    
                    if sociallogin.account.provider == 'google':
                        user.first_name = extra_data.get('given_name', user.first_name)
                        user.last_name = extra_data.get('family_name', user.last_name)
                    elif sociallogin.account.provider == 'facebook':
                        user.first_name = extra_data.get('first_name', user.first_name)
                        user.last_name = extra_data.get('last_name', user.last_name)
                    
                    user.is_verified = True
                    user.save()
                    
                    print(f"✅ Updated user info and connecting social account")
                    sociallogin.connect(request, user)
                    
                except Users.DoesNotExist:
                    print(f"No existing user found - will create new user")
                    pass
            
            print(f"{'='*60}\n")
                    
        except Exception as e:
            print(f"\n❌ ERROR in pre_social_login: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            # Don't raise - let it continue
            pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Auto-creates user WITHOUT showing signup form
        """
        print(f"\n{'='*60}")
        print(f"💾 SAVE_USER CALLED")
        print(f"Provider: {sociallogin.account.provider}")
        
        try:
            user = super().save_user(request, sociallogin, form)
            print(f"✅ User created by parent class: {user.email}")
            
            extra_data = sociallogin.account.extra_data
            
            if sociallogin.account.provider == 'google':
                user.first_name = extra_data.get('given_name', '')
                user.last_name = extra_data.get('family_name', '')
                
                if user.email:
                    email_username = user.email.split('@')[0]
                    
                    if Users.objects.filter(username=email_username).exists():
                        email_username = f"{email_username}{random.randint(100, 999)}"
                    
                    if not user.username or user.username == user.email or '@' in user.username:
                        user.username = email_username
            
            elif sociallogin.account.provider == 'facebook':
                user.first_name = extra_data.get('first_name', '')
                user.last_name = extra_data.get('last_name', '')
                
                if user.email:
                    email_username = user.email.split('@')[0]
                    
                    if Users.objects.filter(username=email_username).exists():
                        email_username = f"{email_username}{random.randint(100, 999)}"
                    
                    if not user.username or user.username == user.email or '@' in user.username:
                        user.username = email_username
            
            user.role = None  # Will be set in select_role view
            user.is_verified = True
            user.save()
            
            print(f"✅ User saved: {user.username} ({user.email})")
            print(f"   - First name: {user.first_name}")
            print(f"   - Last name: {user.last_name}")
            print(f"   - Role: {user.role}")
            print(f"{'='*60}\n")
            
            # ✅ NEW: Don't create profile here - let select_role view do it
            # This prevents creating profiles with wrong status
            
            return user
            
        except Exception as e:
            print(f"❌ ERROR in save_user: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"{'='*60}\n")
            raise
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Return True to auto-create account
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user data without asking
        """
        user = super().populate_user(request, sociallogin, data)
        
        if user.email:
            email_username = user.email.split('@')[0]
            if not user.username or user.username == user.email or '@' in user.username:
                user.username = email_username
        
        return user
    
    def get_login_redirect_url(self, request):
        """
        Redirect after social login based on role
        """
        user = request.user
        
        if user.is_superuser or user.is_staff or user.role == 'Admin':
            return '/system-admin/dashboard/'
        
        if not user.role:
            return '/select-role/'
        
        if user.role == 'JobSeeker':
            return '/accounts/jobseeker/dashboard/'
        elif user.role == 'Employer':
            return '/accounts/employer/dashboard/'
        
        return '/select-role/'