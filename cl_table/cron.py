from cl_app.utils import general_error_response
from .models import(Employee, Fmspw)
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

# log start
# import logging
# logging.basicConfig(filename='tokcron.log',level=logging.INFO)

# def token_create_job():
#     try:
#         print("kkk")
#         token = Token.objects.filter().delete()
#         fmspw_ids = Fmspw.objects.filter(pw_isactive=True,user__is_active=True)
#         for f in fmspw_ids:
#             if f.user:
#                 token_cr = Token.objects.create(user = f.user)

#         result = {'status': status.HTTP_200_OK,"message":"Token Cron Successful",'error': False} 
#         return Response(result,status=status.HTTP_200_OK)        
#     except Exception as e:
#         invalid_message = str(e)
#         return general_error_response(invalid_message)

    
    
   
  