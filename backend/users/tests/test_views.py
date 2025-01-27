from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from users.role import UserRole
import pyotp

User = get_user_model()

class AuthViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.verify_mfa_url = reverse('verify_mfa')
        self.enable_mfa_url = reverse('enable_mfa')
        self.mfa_qr_code_url = reverse('mfa_qr_code')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_login_without_mfa(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertTrue('Authorization' in response.cookies)
        self.assertTrue('Refresh' in response.cookies)

    def test_user_login_with_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('Authorization' in response.cookies)
        self.assertFalse('Refresh' in response.cookies)

    def test_user_login_with_mfa(self):
        # Enable MFA for user
        self.client.force_authenticate(user=self.user)
        self.client.post(self.enable_mfa_url)
        self.client.logout()

        # Try to login
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data['code'], 'MFA_REQUIRED')
        self.assertTrue('Authorization' in response.cookies)
        self.assertFalse('Refresh' in response.cookies)

    def test_verify_mfa(self):
        # Enable MFA and get TOTP secret
        self.client.force_authenticate(user=self.user)
        self.client.post(self.enable_mfa_url)
        totp = pyotp.TOTP(self.user.totp_secret)
        self.client.logout()

        # Login to get temporary token
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Verify MFA
        response = self.client.post(self.verify_mfa_url, {
            'token': totp.now()
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'MFA verified successfully')
        self.assertTrue('Authorization' in response.cookies)
        self.assertTrue('Refresh' in response.cookies)

    def test_verify_mfa_without_login(self):
        response = self.client.post(self.verify_mfa_url, {
            'token': '123456'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_mfa_invalid_token(self):
        # Enable MFA
        self.client.force_authenticate(user=self.user)
        self.client.post(self.enable_mfa_url)
        self.client.logout()

        # Login to get temporary token
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Try to verify with invalid token
        response = self.client.post(self.verify_mfa_url, {
            'token': '123456'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'INVALID_MFA_TOKEN')

    def test_enable_mfa(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.enable_mfa_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 'MFA_ENABLED')
        
        # Verify temporary token cookie is set
        self.assertTrue('Authorization' in response.cookies)
        self.assertFalse('Refresh' in response.cookies)
        
        # Verify user has MFA enabled
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.mfa_enabled)
        self.assertIsNotNone(user.totp_secret)

    def test_enable_mfa_without_auth(self):
        response = self.client.post(self.enable_mfa_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mfa_qr_code_access(self):
        # Enable MFA and login
        self.client.force_authenticate(user=self.user)
        self.client.post(self.enable_mfa_url)
        self.client.logout()
        
        # Login to get temporary token
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Get QR code
        response = self.client.get(self.mfa_qr_code_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'image/png')

    def test_mfa_qr_code_without_temp_token(self):
        response = self.client.get(self.mfa_qr_code_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'MISSING_TOKEN')

class UserViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role=UserRole.ADMIN
        )

    def test_user_list_admin_access(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_list_unauthorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 