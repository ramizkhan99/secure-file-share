from django.test import TestCase
from common.apiresponse import ApiResponse
from rest_framework.test import APIRequestFactory

class ApiResponseTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    def test_success_response(self):
        response = ApiResponse(
            success=True,
            message='Success message',
            data={'key': 'value'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], 'Success message')
        self.assertEqual(response.data['data'], {'key': 'value'})

    def test_error_response(self):
        response = ApiResponse(
            success=False,
            message='Error message',
            status_code=400,
            code='INVALID_REQUEST'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['success'], False)
        self.assertEqual(response.data['message'], 'Error message')
        self.assertEqual(response.data['code'], 'INVALID_REQUEST')

    def test_minimal_response(self):
        response = ApiResponse()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['success'], True)
        self.assertEqual(response.data['message'], '')
        self.assertNotIn('data', response.data) 