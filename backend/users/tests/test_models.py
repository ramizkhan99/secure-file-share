from django.test import TestCase
from django.contrib.auth import get_user_model
from users.role import UserRole

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        self.assertEqual(self.user.username, self.user_data['username'])
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertTrue(self.user.check_password(self.user_data['password']))
        self.assertEqual(self.user.role, UserRole.GUEST)
        self.assertFalse(self.user.mfa_enabled)

    def test_user_roles(self):
        self.user.role = UserRole.ADMIN
        self.user.save()
        self.assertTrue(self.user.is_admin)
        self.assertFalse(self.user.is_regular_user)
        self.assertFalse(self.user.is_guest)

    def test_mfa_functionality(self):
        self.user.generate_totp_secret()
        self.assertIsNotNone(self.user.totp_secret)
        
        uri = self.user.get_totp_uri()
        self.assertIn('SecureFileShare', uri)
        self.assertIn(self.user.username, uri) 