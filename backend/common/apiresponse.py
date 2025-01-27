from http import HTTPStatus
from rest_framework.response import Response

class ApiResponse(Response):
    def __init__(self, success=True, message='', status_code=200, code=None, data=None, **kwargs):
        response_data = {
            'success': success,
            'message': message,
        }
        if code is not None:
            response_data['code'] = code
        if data is not None:
            response_data['data'] = data

        super().__init__(data=response_data, status=status_code, **kwargs)