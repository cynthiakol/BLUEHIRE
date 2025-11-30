from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.conf import settings

class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        """Run developer superuser creation (in DEBUG) and auto document sync after migrations."""
        # --- DEV SUPERUSER CREATION (keep your existing logic) ---
        if getattr(settings, "DEBUG", False):
            try:
                from django.contrib.auth import get_user_model
                from django.db.utils import OperationalError, ProgrammingError
                import os

                User = get_user_model()
                if not User.objects.filter(is_superuser=True).exists():
                    default_username = os.environ.get("DEV_ADMIN_USER", "admin")
                    default_email = os.environ.get("DEV_ADMIN_EMAIL", "admin@example.com")
                    default_password = os.environ.get("DEV_ADMIN_PASS", "bluehire123!")
                    User.objects.create_superuser(
                        username=default_username,
                        email=default_email,
                        password=default_password,
                    )
            except (OperationalError, ProgrammingError):
                pass
            except Exception:
                pass

        # --- AUTO SYNC DOCUMENT STATUSES ---
        try:
            from accounts.models import JobSeeker, Employer, DocumentVerification

            def auto_sync_docs(sender, **kwargs):
                """Automatically align document verification statuses with approvals."""
                # ✅ Only run for accounts app
                if sender.name != 'accounts':
                    return
                
                try:
                    from django.db import connection
                    
                    # ✅ Check if tables exist
                    existing_tables = connection.introspection.table_names()
                    required_tables = ['accounts_jobseeker', 'accounts_employer', 'accounts_documentverification', 'accounts_users']
                    
                    if not all(table in existing_tables for table in required_tables):
                        return  # Skip if tables don't exist yet
                    
                    # ✅ JobSeekers - with safe user access
                    for seeker in JobSeeker.objects.select_related('user').all():
                        try:
                            # Check if user relationship exists
                            if not hasattr(seeker, 'user') or seeker.user is None:
                                continue
                            
                            user = seeker.user
                            
                            if seeker.approval_status == "Approved":
                                DocumentVerification.objects.filter(user=user).update(status="Verified")
                            elif seeker.approval_status == "Rejected":
                                DocumentVerification.objects.filter(user=user).update(status="Rejected")
                            elif seeker.approval_status == "Re-upload Required":
                                DocumentVerification.objects.filter(user=user).update(status="Pending")
                        except Exception as e:
                            # Skip this seeker if there's any error
                            print(f"⚠️ Skipping seeker {seeker.seeker_id}: {e}")
                            continue

                    # ✅ Employers - with safe user access
                    for emp in Employer.objects.select_related('user').all():
                        try:
                            # Check if user relationship exists
                            if not hasattr(emp, 'user') or emp.user is None:
                                continue
                            
                            user = emp.user
                            
                            if emp.approval_status == "Approved" or emp.is_verified:
                                DocumentVerification.objects.filter(user=user).update(status="Verified")
                            elif emp.approval_status == "Rejected":
                                DocumentVerification.objects.filter(user=user).update(status="Rejected")
                            elif emp.approval_status == "Re-upload Required":
                                DocumentVerification.objects.filter(user=user).update(status="Pending")
                        except Exception as e:
                            # Skip this employer if there's any error
                            print(f"⚠️ Skipping employer {emp.employer_id}: {e}")
                            continue

                    print("✅ [AutoSync] Document verification statuses refreshed.")
                
                except Exception as e:
                    # Don't break migrations if auto-sync fails
                    print(f"⚠️ [AutoSync] Failed: {e}")

            post_migrate.connect(auto_sync_docs, sender=self)
        except Exception as e:
            print("⚠️ AutoSync setup skipped:", e)