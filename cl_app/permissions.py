from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status
from .models import (Fmspw)
from django.contrib import messages
from rest_framework import exceptions
from django.utils.translation import ugettext as _

# Create your Permissions here .

class authenticated_only(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            msg = {'status': status.HTTP_400_BAD_REQUEST,"message":"User account is disabled.",'error': True} 
            raise exceptions.AuthenticationFailed(msg)

        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        if not fmspw:
            msg = {'status': status.HTTP_400_BAD_REQUEST,"message":"User account is not activated in FMSPW.",'error': True} 
            raise exceptions.AuthenticationFailed(msg)
            
        if not request.GET.get('sitecodeid',None) is None:
            site = ItemSitelist.objects.filter(id=request.GET.get('sitecodeid',None),itemsite_isactive=True).first()
            if not site:
                msg = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Site ID does not exist.",'error': True} 
                raise exceptions.AuthenticationFailed(msg)
        else:
            site = fmspw[0].loginsite
        if not site:
            msg = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise exceptions.AuthenticationFailed(msg)

        if not fmspw[0].LEVEL_ItmIDid.pk:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee has no security level",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
  
        return request.method 
