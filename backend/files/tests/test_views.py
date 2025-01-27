from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File, SharedFile

User = get_user_model()

class FileViewsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            b"test content",
            content_type="text/plain"
        )

    def test_upload_file(self):
        response = self.client.post(
            reverse('handle_file_requests'),
            {'file': self.test_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(File.objects.filter(owner=self.user).exists())

    def test_list_files(self):
        File.objects.create(
            owner=self.user,
            file=self.test_file,
            filename='test_file.txt,',
            size=13213,
            mime='application/txt'
        )
        response = self.client.get(reverse('handle_file_requests'))
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_share_file(self):
        file = File.objects.create(
            owner=self.user,
            file=self.test_file,
            filename='test_file.txt'
        )
        response = self.client.get(
            reverse('get_share_link') + '?id=1'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SharedFile.objects.filter(file=file).exists()) 