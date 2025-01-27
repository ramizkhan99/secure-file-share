from django.test import TestCase
from django.contrib.auth import get_user_model
from common.jwt import (
    generate_jwt_tokens,
    decode_jwt_token,
    generate_temp_token,
    generate_access_token_from_refresh_token
)
import time

User = get_user_model()

class JWTTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_token_generation_and_decoding(self):
        access_token, refresh_token = generate_jwt_tokens(self.user)
        
        # Test access token
        access_payload = decode_jwt_token(access_token)
        self.assertIsNotNone(access_payload)
        self.assertEqual(access_payload['user_id'], self.user.id)
        self.assertTrue(access_payload['mfa'])
        self.assertEqual(access_payload['type'], 'access')
        
        # Test refresh token
        refresh_payload = decode_jwt_token(refresh_token)
        self.assertIsNotNone(refresh_payload)
        self.assertEqual(refresh_payload['user_id'], self.user.id)
        self.assertTrue(refresh_payload['mfa'])
        self.assertEqual(refresh_payload['type'], 'refresh')
        self.assertIn('jti', refresh_payload)

    def test_temp_token_generation(self):
        temp_token = generate_temp_token(self.user)
        payload = decode_jwt_token(temp_token)
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.user.id)
        self.assertFalse(payload['mfa'])
        self.assertEqual(payload['type'], 'temp')
        self.assertTrue(payload['exp'] - time.time() <= 300)  # 5 minutes

    def test_refresh_token_generation(self):
        _, refresh_token = generate_jwt_tokens(self.user)
        new_access_token = generate_access_token_from_refresh_token(refresh_token)
        
        self.assertIsNotNone(new_access_token)
        payload = decode_jwt_token(new_access_token)
        self.assertEqual(payload['user_id'], self.user.id)
        self.assertTrue(payload['mfa'])
        self.assertEqual(payload['type'], 'access')

    def test_expired_token(self):
        # Create a token that's already expired
        payload = {
            'user_id': self.user.id,
            'exp': int(time.time()) - 3600,  # 1 hour ago
            'iat': int(time.time()) - 7200,  # 2 hours ago
            'mfa': True,
            'type': 'access'
        }
        import jwt
        from django.conf import settings
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        decoded_payload = decode_jwt_token(expired_token)
        self.assertIsNone(decoded_payload)

    def test_invalid_token(self):
        invalid_token = "invalid.token.string"
        decoded_payload = decode_jwt_token(invalid_token)
        self.assertIsNone(decoded_payload)

    def test_refresh_with_invalid_token(self):
        new_access_token = generate_access_token_from_refresh_token("invalid.token")
        self.assertIsNone(new_access_token)

    def test_refresh_with_non_refresh_token(self):
        access_token, _ = generate_jwt_tokens(self.user)
        new_access_token = generate_access_token_from_refresh_token(access_token)
        self.assertIsNone(new_access_token) 