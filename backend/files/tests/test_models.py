from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from files.models import File, SharedFile

User = get_user_model()

class FileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.test_file = SimpleUploadedFile(
            "test_file.txt",
            b"test content",
            content_type="text/plain"
        )

    def test_create_file(self):
        file = File.objects.create(
            owner=self.user,
            file=self.test_file,
            filename='test_file.txt',
            size=len(b"test content"),
            mime='text/plain'
        )
        self.assertEqual(file.owner, self.user)
        self.assertEqual(file.filename, 'test_file.txt')
        self.assertEqual(file.size, len(b"test content"))
        self.assertEqual(file.mime, 'text/plain')

    def test_create_shared_file(self):
        file = File.objects.create(
            owner=self.user,
            file=self.test_file,
            filename='test_file.txt'
        )
        shared_file = SharedFile.objects.create(
            file=file,
            user=self.user
        )
        self.assertIsNotNone(shared_file.share_hash)
        self.assertEqual(shared_file.file, file)
        self.assertEqual(shared_file.user, self.user) 