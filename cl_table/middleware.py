import django.utils.timezone
from pytz import timezone
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from cl_app.models import LoggedInUser
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login , logout, get_user_model
from cl_app.utils import general_error_response
from rest_framework.response import Response
from re import sub
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Customer
from django.conf import settings
from django.contrib.sessions.middleware import SessionMiddleware
from importlib import import_module

# class OneSessionPerUserMiddleware(object):
#     # Called only once when the web server starts
#     def __init__(self, get_response):
#         self.get_response = get_response

#     # Called once per request
#     def __call__(self, request):
#         # This codition is required because anonymous users
#         # dont have access to 'logged_in_user'
#         header_token = request.META.get('HTTP_AUTHORIZATION', None)
#         print(header_token,type(header_token),"header_token")
       
#         if header_token is not None:
#             #try:
#             token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
#             # print(token,type(token),"token")
#             spl = token.split(" ")
#             # print(spl,"spl")
#             token_ids = Token.objects.filter(key=spl[1])
#             # print(token_ids,"token_ids")
#             if token_ids:
#                 token_obj = token_ids[0]
#                 # print(token_obj,"token_obj")
#                 request.user = token_obj.user
#                 print(request.user,"request.user")
#                 #This is now the correct user

#                 print(request.session.session_key,"request.session.session_key 111")


#                 if request.user.is_authenticated:
#                     # Gets the user's session_key from the database
#                     # print(request.user,"request.user")
                
#                     if request.user.logged_in_user:
#                         print(request.session,"request.session")
#                         print(request.user.logged_in_user,request.user.logged_in_user.pk,"lll")
#                         current_session_key = request.user.logged_in_user.session_key
#                         print(current_session_key,"current_session_key")
#                         print(request.session.session_key,"request.session.session_key")
#                         # If the session_key exists in the db and it is different from the browser's session
#                         if current_session_key and current_session_key != request.session.session_key:
#                             print("iff")
#                             sess_ids = Session.objects.filter(session_key=current_session_key)
#                             if sess_ids:
#                                 print(Session.objects.filter(session_key=current_session_key),"hhh")
#                                 Session.objects.filter(session_key=current_session_key).delete()

#                         # Update the user's session_key in the db
#                         request.user.logged_in_user.session_key = request.session.session_key
#                         request.user.logged_in_user.save()

#             # except Exception as e:
#             #     invalid_message = str(e)
#             #     return general_error_response(invalid_message)         
      
        
#         response = self.get_response(request)
#         return response


# def tokencheck(self, request):
#     header_token = request.META.get('HTTP_AUTHORIZATION', None)
#     print(header_token,type(header_token),"header_token")
#     if header_token is not None:
#         token = sub('Token ', '', request.META.get('HTTP_AUTHORIZATION', None))
#         print(token,type(token),"token")
#         # token = "32a2bc0d1ea083abd1b6ece2fb3121bf7079f0da"
#         token_ids = Token.objects.filter(key = token)
#         print(token_ids,"token_ids")
#     return True