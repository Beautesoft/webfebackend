from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from datetime import timedelta, datetime
from django.utils import timezone
from django.conf import settings
import pytz
from rest_framework import status
import datetime

#this return left time

def expires_in(token):
    # print(timezone.now(),"timezone.now()")
    # print(token.created,"token.created")
    time_elapsed = timezone.now() - token.created
    data1 = token.created
    # print(data1,"data1")
    nextday = timezone.now() + datetime.timedelta(days=1)
    # print(nextday,"nextday")
    data2 = nextday.replace(hour=8, minute=0, second=0, microsecond=0)

    diff = data2 - data1
    # print(diff)

    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds / 3600
    # print(hours,"hours")

    # print(time_elapsed,"time_elapsed")
    # print(timedelta(seconds = 300),"timedelta(seconds = 300)")
    # left_time = timedelta(seconds = settings.TOKEN_EXPIRED_AFTER_HOURS) - time_elapsed
    left_time = timedelta(hours= hours) - time_elapsed
    # print(left_time,"left_time")
    return left_time

def is_token_expired(token):
    # print(timedelta(seconds = 0),"timedelta(seconds = 0)")
    # print(expires_in(token),"expires_in(token)")
    return expires_in(token) < timedelta(seconds = 0)


# if token is expired new token will be established
# If token is expired then it will be removed
# and new one with different key will be created
def token_expire_handler(token):
    is_expired = is_token_expired(token)
    # print(is_expired,"is_expired")
    if is_expired:
        token.delete()
        token = Token.objects.create(user = token.user)
    return is_expired, token

#DEFAULT_AUTHENTICATION_CLASSES
class ExpiringTokenAuthentication(TokenAuthentication):
    """
    If token is expired then it will be removed
    and new one with different key will be created
    """
    def authenticate_credentials(self, key):
        try:
            token = Token.objects.get(key = key)
        except Token.DoesNotExist:
            msg = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Token.",'error': True} 
            raise AuthenticationFailed(msg)
        
        if not token.user.is_active:
            amsg = {'status': status.HTTP_400_BAD_REQUEST,"message":"User is not active.",'error': True} 
            raise AuthenticationFailed(amsg)
        

        is_expired, token = token_expire_handler(token)
        if is_expired:
            tmsg = {'status': status.HTTP_400_BAD_REQUEST,"message":"The Token is expired.",'error': True} 
            raise AuthenticationFailed(tmsg)
        
        return (token.user, token)


def multiple_expire_handler(token):
    token.delete()
    token = Token.objects.create(user = token.user)
    return token