import pyotp
from django.db import models
from django.contrib.auth.models import AbstractUser

from users.role import UserRole

class User(AbstractUser):
    mfa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=255, blank=True, null=True)  # For TOTP
    email = models.EmailField(unique=True)  # Make email required and unique
    role = models.CharField(
        max_length=128,
        choices=UserRole.CHOICES,
        default=UserRole.GUEST
    )

    def generate_totp_secret(self):
        """Generates a new TOTP secret."""
        self.totp_secret = pyotp.random_base32()

    def get_totp_uri(self):
        """Generates the TOTP provisioning URI."""
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.username, issuer_name="SecureFileShare"
        )

    def verify_totp(self, token):
        """Verifies a TOTP token."""
        totp = pyotp.totp.TOTP(self.totp_secret)
        return totp.verify(token)
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    @property
    def is_regular_user(self):
        return self.role == UserRole.USER

    @property
    def is_guest(self):
        return self.role == UserRole.GUEST
