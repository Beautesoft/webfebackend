from rest_framework.response import Response
from rest_framework import status, exceptions
from rest_framework.views import exception_handler

class BeautesoftException(Exception):
    pass

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response:
        error_message = response.data.get('detail', '')

        if error_message:
            response.data = {}
            response.data['success'] = False
            response.data['data'] = None
            response.data['msg'] = error_message
    return response

def response_template(data=None, status=status.HTTP_200_OK, error=True, message=''):
    response_dict = {
        'status': status,
        'error': error,
        'message': message}
    return Response(status=status, data=response_dict)

def general_error_response(message, data=None):
    return response_template(
        data, status.HTTP_400_BAD_REQUEST, True, message)
