from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import (EmpLevelSerializer, RoomSerializer, ComboServicesSerializer, CategorySerializer, TypeSerializer,
itemCartSerializer,VoucherRecordSerializer,EmployeeDropSerializer, itemCartListSerializer,PaymentRemarksSerializer,
HolditemSetupSerializer,PosPackagedepositSerializer,PosPackagedepositpostSerializer)
from .models import (EmpLevel, Room, Combo_Services, ItemCart,VoucherRecord,RoundPoint, RoundSales,
PaymentRemarks, HolditemSetup,PosPackagedeposit)
from cl_table.models import(Treatment, Employee, Fmspw, Stock, ItemClass, ItemRange, Appointment,Customer,Treatment_Master,
GstSetting,PosTaud,PosDaud,PosHaud,ControlNo,EmpSitelist,ItemStatus, TmpItemHelper, FocReason, PosDisc,
TreatmentAccount, PosDaud, ItemDept, DepositAccount, PrepaidAccount, ItemDiv, Systemsetup, Title,
PackageHdr,PackageDtl)
from cl_app.models import ItemSitelist, SiteGroup
from cl_table.serializers import PostaudSerializer,StaffsAvailableSerializer,PosdaudSerializer
import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
import math
from rest_framework import serializers
from rest_framework.views import APIView
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from Cl_beautesoft.settings import EMAIL_HOST_USER, PDF_ROOT
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives
from io import BytesIO
from rest_framework.decorators import action
from django.utils.html import strip_tags
from django.template.loader import get_template
import pdfkit
from rest_framework import generics
from pyvirtualdisplay import Display
from reportlab.pdfgen import canvas
from django.core.files.storage import default_storage
from Cl_beautesoft import settings
import os
import os.path
import tempfile
from datetime import date
from django.db.models import Sum
from django.db.models import Count
from custom.services import GeneratePDF, round_calc
from cl_app.permissions import authenticated_only
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions
from cl_app.utils import general_error_response
from Cl_beautesoft.settings import BASE_DIR
from django.db.models import Q
import string
from cl_table.authentication import ExpiringTokenAuthentication

type_ex = ['VT-Deposit','VT-Top Up','VT-Sales']

# Create your views here.

def get_client_ip(request):
    # url = request.build_absolute_uri()
    # ip = url.split('api')
    # string = ""
    # for idx, val in enumerate(ip[0]):
    #     if idx != 21:
    #         string += val
    ip_str = str("http://"+request.META['HTTP_HOST'])
    return ip_str


def response(self,request, queryset,total,  state, message, error, serializer_class, data, action): 
    ip = get_client_ip(request)
    if action == 'list':
        page= request.GET.get('page',1)
        if self.__class__.__name__ == 'EmployeeCartAPI':
            limit = request.GET.get('limit',6)
        else:
            limit = request.GET.get('limit',12)
     
        paginator = Paginator(queryset, limit)
        total_page = math.ceil(len(queryset)/int(limit))
        if queryset:
            if int(page) > total_page:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Content",'error': False, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
                'dataList': []}}
                return result
            try:
                queryset = paginator.page(page)
            except PageNotAnInteger:
                queryset = paginator.page(1)
                page= 1    

            serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
            if self.__class__.__name__ == 'ComboServicesViewset':
                dat = serializer.data
                final =[]
                for d in dat:
                    lst =[]; dit = {}
                    dictval = dict(d)
                    for key, value in dictval.items(): 
                        if key == 'services':
                            for v in value:
                                obj = Stock.objects.get(pk=v)
                                img = obj.images_set.all().order_by('-id')
                                if obj.Item_Classid:
                                    Category = obj.Item_Classid.itm_desc
                                else:
                                    Category = None

                                if img:
                                    images = str(ip)+str(img[0].image.url)
                                else:
                                    images = None        

                                val = {'service_name':obj.item_desc,'category':Category,'image':images,'price':obj.item_price}
                                lst.append(val)
                       
                        if key == 'Price':
                            price = value  
                        if key == 'id':
                            id_val = value   

                    dit = {'id':id_val ,'Combolist':lst, 'Price':price}    
                    final.append(dit)
                result = {'status': state,"message":message,'error': error, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
                'dataList': final}}
            elif self.__class__.__name__ == 'ServicesViewset':
                datval = serializer.data
                listval = []
                for d in datval:
                    dictt = dict(d)

                    for key, value in dictt.items(): 
                        if key == "id":
                            obj = Stock.objects.get(pk=value)
                            imagee = obj.images_set.all().order_by('-id')
                            if imagee:
                                image = str(ip)+str(imagee[0].image.url)
                            else:
                                image = None
                            dictt['images'] = image    
                            
                    listval.append(dictt) 

                result = {'status': state,"message":message,'error': error, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
                'dataList': listval}}             
            else:
                result = {'status': state,"message":message,'error': error, 
                'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
                'dataList': serializer.data}}
            
        else:  
            serializer = self.get_serializer()
            result = {'status': state,"message":message,'error': error, 
            'data': {'meta': {'pagination': {"per_page":limit,"current_page":page,"total":total,"total_pages":total_page}}, 
            'dataList': []}} 
            
    elif action in ['create','retrieve','update','partial_update']: 
        if self.__class__.__name__ == 'ComboServicesViewset':
            result = {'status': state,"message":message,'error': error, 'data': data} 
            d = result.get('data')
            if 'services' in d:
                s = d['services']
                lst = []
                for v in s:
                    obj = Stock.objects.get(pk=v)
                    img = obj.images_set.all().order_by('-id')
                    if obj.Item_Classid:
                        Category = obj.Item_Classid.itm_desc
                    else:
                        Category = None

                    if img:
                        images = str(ip)+str(img[0].image.url)
                    else:
                        images = None        

                    val = {'service_name':obj.item_desc,'category':Category,'image':images,'price':obj.item_price}
                    lst.append(val)

                d['Combolist'] = lst
            else:
                result = {'status': state,"message":message,'error': error, 'data': data} 
        else:    
            result = {'status': state,"message":message,'error': error, 'data': data} 
    elif action == 'destroy':
        result = {'status': state,"message":message,'error': error} 
     
    return result



class CategoryViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ItemClass.objects.filter(itm_isactive=True).order_by('-pk')
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = ItemClass.objects.filter(itm_isactive=True).order_by('-pk')
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = ItemClass.objects.filter(itm_isactive=True,itm_desc__icontains=q).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'itm_desc':
                    queryset = ItemClass.objects.filter(itm_isactive=True).order_by('itm_desc')
            elif value == "desc":
                if key == 'itm_desc':
                    queryset = ItemClass.objects.filter(itm_isactive=True).order_by('-itm_desc')

        return queryset

    def list(self, request):
        try:
            serializer_class = CategorySerializer
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)             
    
    def create(self, request):
        try:
            queryset = None
            serializer_class = None
            total = None
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                serializer.save()
                state = status.HTTP_201_CREATED
                message = "Created Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_201_CREATED)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def get_object(self, pk):
        try:
            return ItemClass.objects.get(pk=pk,itm_isactive=True)
        except ItemClass.DoesNotExist:
            raise Http404

   
    def retrieve(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            category = self.get_object(pk)
            serializer = CategorySerializer(category)
            data = serializer.data
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
                
    
    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            category = self.get_object(pk)
            serializer = CategorySerializer(category, data=request.data)
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        

    def destroy(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            data = None
            state = status.HTTP_204_NO_CONTENT
            try:
                instance = self.get_object(pk)
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result,status=status.HTTP_200_OK)    
            except Http404:
                pass

            message = "No Content"
            error = True
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       
        

    def perform_destroy(self, instance):
        instance.itm_desc = False
        treat = Stock.objects.filter(Item_Classid=instance).update(Item_Classid=None)
        instance.save()  



class TypeViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ItemRange.objects.filter().order_by('-pk')
    serializer_class = TypeSerializer

    def get_queryset(self):
        queryset = ItemRange.objects.filter().order_by('-pk')
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = ItemRange.objects.filter(itm_desc__icontains=q).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'itm_desc':
                    queryset = ItemRange.objects.filter().order_by('itm_desc')
            elif value == "desc":
                if key == 'itm_desc':
                    queryset = ItemRange.objects.filter().order_by('-itm_desc')

        return queryset

    def list(self, request):
        try:
            serializer_class = TypeSerializer
            queryset = self.filter_queryset(self.get_queryset())
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)            
    

    def create(self, request):
        try:
            queryset = None
            serializer_class = None
            total = None
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                serializer.save()
                state = status.HTTP_201_CREATED
                message = "Created Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_201_CREATED)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

   
    def get_object(self, pk):
        try:
            return ItemRange.objects.get(pk=pk)
        except ItemRange.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            Type = self.get_object(pk)
            serializer = TypeSerializer(Type)
            data = serializer.data
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
            

    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            Type = self.get_object(pk)
            serializer = TypeSerializer(Type, data=request.data)
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    
    def destroy(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            data = None
            state = status.HTTP_204_NO_CONTENT
            try:
                instance = self.get_object(pk)
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result,status=status.HTTP_200_OK)    
            except Http404:
                pass

            message = "No Content"
            error = True
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        

    def perform_destroy(self, instance):
        treat = Stock.objects.filter(Item_Rangeid=instance).update(Item_Rangeid=None)
        instance.save()  


class JobTitleViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = EmpLevel.objects.filter(level_isactive=True).order_by('-pk')
    serializer_class = EmpLevelSerializer

    def get_queryset(self):
        queryset = EmpLevel.objects.filter(level_isactive=True).order_by('-pk')
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = EmpLevel.objects.filter(level_isactive=True,level_desc__icontains=q).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'level_desc':
                    queryset = EmpLevel.objects.filter(level_isactive=True).order_by('level_desc')
            elif value == "desc":
                if key == 'level_desc':
                    queryset = EmpLevel.objects.filter(level_isactive=True).order_by('-level_desc')

        return queryset

    def list(self, request):
        try:
            serializer_class = EmpLevelSerializer
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          
    

    def create(self, request):
        try:
            queryset = None
            serializer_class = None
            total = None
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                serializer.save()
                state = status.HTTP_201_CREATED
                message = "Created Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_201_CREATED)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

   
    def get_object(self, pk):
        try:
            return EmpLevel.objects.get(pk=pk,level_isactive=True)
        except EmpLevel.DoesNotExist:
            raise Http404

   
    def retrieve(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            jobtitle = self.get_object(pk)
            serializer = EmpLevelSerializer(jobtitle)
            data = serializer.data
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
                    
    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            jobtitle = self.get_object(pk)
            serializer = EmpLevelSerializer(jobtitle, data=request.data)
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        
    
    def destroy(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            data = None
            state = status.HTTP_204_NO_CONTENT
            try:
                instance = self.get_object(pk)
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result,status=status.HTTP_200_OK)    
            except Http404:
                pass

            message = "No Content"
            error = True
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       

    def perform_destroy(self, instance):
        instance.level_isactive = False
        emp = Employee.objects.filter(EMP_TYPEid=instance).update(EMP_TYPEid=None)
        instance.save()                


class RoomViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Room.objects.filter(isactive=True).order_by('-id')
    serializer_class = RoomSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

        site = fmspw[0].loginsite
        if not site:
            result = {'status': state,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
       
        queryset = Room.objects.filter(isactive=True,Site_Codeid=site).order_by('-id')
        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Room.objects.filter(isactive=True).order_by('-id')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [27,31]:
            queryset = Room.objects.filter(isactive=True,Site_Codeid=site).order_by('-id')

        
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        # appt = self.request.GET.get('Appointment_id',None)
        # app_obj = Appointment.objects.filter(pk=self.request.GET.get('Appointment_id',None)).first()
        # if not app_obj:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

        outlet = self.request.GET.get('Outlet',None)

        if q is not None:
            queryset = queryset.filter(displayname=q).order_by('-id')
        elif value and key is not None:
            if value == "asc":
                if key == 'displayname':
                    queryset = queryset.order_by('displayname')
            elif value == "desc":
                if key == 'displayname':
                    queryset = queryset.order_by('-displayname')
                    
        elif outlet is not None:
            queryset = Room.objects.filter(isactive=True,Site_Codeid__id=outlet).order_by('-id')
        # elif appt is not None:
        #     app_obj = Appointment.objects.filter(pk=appt).first()
        #     rooms=[]
        #     app = Appointment.objects.filter(appt_date=app_obj.appt_date,appt_status="confirmed",ItemSite_Codeid=app_obj.ItemSite_Codeid)
        #     for a in app:
        #         trt = Treatment_Master.objects.filter(Appointment=a)
        #         rooms = list(set([t.Trmt_Room_Code.id for t in trt if t.Trmt_Room_Code]))

        #     queryset = Room.objects.filter(isactive=True,Site_Codeid=app_obj.ItemSite_Codeid).exclude(id__in=rooms).order_by('-id')

        return queryset

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
                data = serializer.data
                lst = []
                for v in data:
                    data_v = dict(v)
                    data_v['room_img'] = str(get_client_ip(request))+str(data_v['room_img'])
                    lst.append(data_v)

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  lst}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)             
    

    def create(self, request):
        try:
            queryset = None
            serializer_class = None
            total = None
            serializer = self.get_serializer(data=request.data, context={'request': self.request})
            if serializer.is_valid():
                self.perform_create(serializer)
                user = request.user
                fmspw = Fmspw.objects.filter(user=user,pw_isactive=True)
                site = fmspw[0].loginsite
                serializer.save(Site_Codeid=site,site_code=site.itemsite_code,Room_PIC=request.data['Room_PIC'])
                state = status.HTTP_201_CREATED
                message = "Created Succesfully"
                error = False
                data = serializer.data
                ip = get_client_ip(request)
                if 'room_img' in data and data['room_img'] is not None:
                    data['room_img'] = str(ip)+str(data['room_img'])
            
                result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_201_CREATED)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk,isactive=True)
        except Room.DoesNotExist:
            raise Http404

   
    def retrieve(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            room = self.get_object(pk)
            serializer = RoomSerializer(room, context={'request': self.request})
            data = serializer.data
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
                
    
    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            room = self.get_object(pk)
            serializer = RoomSerializer(room, data=request.data, context={'request': self.request})
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        

    def destroy(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            data = None
            state = status.HTTP_204_NO_CONTENT
            try:
                instance = self.get_object(pk)
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result,status=status.HTTP_200_OK)    
            except Http404:
                pass

            message = "No Content"
            error = True
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        

    def perform_destroy(self, instance):
        instance.isactive = False
        # treat = Stock.objects.filter(category=instance).update(category=None)
        instance.save()  

class ComboServicesViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Combo_Services.objects.filter(Isactive=True).order_by('-id')
    serializer_class = ComboServicesSerializer

    def get_queryset(self):
        user = self.request.user
        fmspw = Fmspw.objects.filter(user=user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        site = fmspw[0].Emp_Codeid.Site_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

        queryset = Combo_Services.objects.filter(Isactive=True).order_by('-id')
       
        q = self.request.GET.get('search',None)

        if q is not None:
            queryset = Combo_Services.objects.filter(Isactive=True,services__item_desc__icontains=q).order_by('-id')
        
        return queryset

    def list(self, request):
        try:
            serializer_class = ComboServicesSerializer
            queryset = self.filter_queryset(self.get_queryset())
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)           
        
    def create(self, request):
        try:
            state = status.HTTP_400_BAD_REQUEST
            user = request.user
            fmspw = Fmspw.objects.filter(user=user,pw_isactive=True)
            if not self.request.user.is_authenticated:
                result = {'status': state,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            if not fmspw:
                result = {'status': state,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            queryset = None
            serializer_class = None
            total = None
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                site = fmspw[0].Emp_Codeid.Site_Codeid
                s = serializer.save()
                s.Site_Code = site
                s.save()
                state = status.HTTP_201_CREATED
                message = "Created Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)  
                return Response(result, status=status.HTTP_201_CREATED)

            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

   
    def get_object(self, pk):
        try:
            return Combo_Services.objects.get(pk=pk,Isactive=True)
        except Combo_Services.DoesNotExist:
            raise Http404

    
    def retrieve(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            combo = self.get_object(pk)
            serializer = ComboServicesSerializer(combo)
            data = serializer.data
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        
    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            combo = self.get_object(pk)
            serializer = ComboServicesSerializer(combo, data=request.data)
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    
    def destroy(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            data = None
            state = status.HTTP_204_NO_CONTENT
            try:
                instance = self.get_object(pk)
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result,status=status.HTTP_200_OK)    
            except Http404:
                pass

            message = "No Content"
            error = True
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        

    def perform_destroy(self, instance):
        instance.Isactive = False
        instance.save() 

class EmployeeCartAPI(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
    serializer_class = EmployeeDropSerializer

    def list(self, request):
        try:
            if self.request.GET.get('sales_staff',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sales_staff in parms!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            if not self.request.user.is_authenticated:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not self.request.GET.get('sitecodeid',None) is None:
                site = ItemSitelist.objects.filter(pk=self.request.GET.get('sitecodeid',None),itemsite_isactive=True).first()
                if not site:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Site ID does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            else:
                site = fmspw[0].loginsite
            branch = ItemSitelist.objects.filter(pk=site.pk,itemsite_isactive=True).first() 
            if not branch:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Outlet Id does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            emp_siteids = EmpSitelist.objects.filter(Site_Codeid__pk=branch.pk,isactive=True)
            staffs = list(set([e.Emp_Codeid.pk for e in emp_siteids if e.Emp_Codeid and e.Emp_Codeid.emp_isactive == True]))
            if self.request.GET.get('sales_staff',None) == "1":
                queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,show_in_sales=True).order_by('emp_seq_webappt')
            
            elif self.request.GET.get('sales_staff',None) == "0":
                queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,show_in_trmt=True).order_by('emp_seq_webappt')

            elif self.request.GET.get('sales_staff',None) == "2":
                queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True).filter(
                    Q(show_in_trmt=True) | Q(show_in_sales=True)).order_by('emp_seq_webappt')
    

            
            serializer_class = EmployeeDropSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result = response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            v = result.get('data')
            d = v.get("dataList")
            for dat in d:
                emp_obj = Employee.objects.filter(pk=dat['id']).first()
                dat['emp_name'] = emp_obj.display_name
    
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)             
        
       
def round_calc(value):
    val = "{:.2f}".format(float(value))
    fractional = math.modf(float(val))
    data = "{:.2f}".format(float(fractional[0]))
    split_d = str(data).split('.')
    con = "0.0"+split_d[1][-1]
    round_ids = RoundSales.objects.filter(sales=float(con)).first()
    rounded = 0.0
    if type(val) == 'str':
        if '-' in str(round_ids.roundvalue):
            split_value = str(round_ids.roundvalue).split('-')
            rounded = str(val) - split_value[1]
        elif '+' in str(round_ids.roundvalue):
            split = str(round_ids.roundvalue).split('+')
            rounded = str(val) + split_value[1]
    elif type(val) == 'float': 
        if '-' in str(round_ids.roundvalue):
            split_value = str(round_ids.roundvalue).split('-')
            rounded = float(val) - float(split_value[1])
        elif '+' in str(round_ids.roundvalue):
            split = str(round_ids.roundvalue).split('+')
            rounded = float(val) + float(split_value[1])        
    return rounded    



def get_in_val(self, time):
    if time:
        split = str(time).split(':')
        split.pop()
        for idx, val in enumerate(split):
            if idx == 0:
                hr = val 
            elif idx == 1:
                mins = val
        in_time = str(hr)+":"+str(mins)
        return str(in_time)
    else:
        return None 

def sa_transacno_update(self, site, fmspw):
    sacontrol_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
    if not sacontrol_obj:
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
    haudre = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('sa_transacno')
    haudfinal = list(set([r.sa_transacno for r in haudre]))
    code_site = site.itemsite_code
    prefix_s = sacontrol_obj.control_prefix

    slst = []
    if haudfinal != []:
        for fh in haudfinal:
            fhstr = fh.replace(prefix_s,"")
            fhnew_str = fhstr.replace(code_site, "")
            slst.append(fhnew_str)
            slst.sort(reverse=True)

        # print(slst,"slst")
        sa_id = int(slst[0]) + 1
        
        sacontrol_obj.control_no = str(sa_id)
        sacontrol_obj.save() 
    return True                   

class itemCartViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ItemCart.objects.filter(isactive=True).order_by('-id')
    serializer_class = itemCartSerializer

    @action(detail=False, methods=['get'], name='Check')
    def Check(self, request):
        try:
            if str(self.request.GET.get('cust_noid',None)) == "undefined":
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select customer!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)         

            global type_ex
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            cart_date = timezone.now().date()

            empl = fmspw[0].Emp_Codeid
        
           
            if self.request.GET.get('cust_noid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            cust_obj = Customer.objects.filter(pk=self.request.GET.get('cust_noid',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        
            control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
            final = list(set([r.cart_id for r in cartre]))
            code_site = site.itemsite_code
            prefix = control_obj.control_prefix

            clst = []
            if final != []:
                for f in final:
                    newstr = f.replace(prefix,"")
                    new_str = newstr.replace(code_site, "")
                    clst.append(new_str)
                    clst.sort(reverse=True)

                # print(clst,"clst")
                cart_id = int(clst[0]) + 1
                
                control_obj.control_no = str(cart_id)
                control_obj.save()

            savalue = sa_transacno_update(self, site, fmspw) 

            queryset = ItemCart.objects.filter(cust_noid=cust_obj,cart_date=cart_date,
            cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')    
            lst = list(set([e.cart_id for e in queryset if e.cart_id]))
            if len(lst) > 1:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Customer will have more than one Cart ID in Inprogress status,Please check and delete Unwanted Cart ID!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if queryset:
                # serializer = self.get_serializer(queryset, many=True)
                #'data':  serializer.data
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': {'cart_id':lst[0]},'cart_id':lst[0]}
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"Listed Succesfully",'error': False, 
                'data': [],'cart_id': ""}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        
    def get_queryset(self):
        global type_ex
        request = self.request
        cart_date = timezone.now().date()
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
       
        site = fmspw[0].loginsite
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
        cart_id = request.GET.get('cart_id',None)

        if fmspw[0].flgsales == True:
            if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
                queryset = ItemCart.objects.filter(isactive=True).order_by('id')
            elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [31,27]:
                queryset = ItemCart.objects.filter(isactive=True,sitecodeid=site).order_by('id')

            queryset = queryset.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
            cart_status="Inprogress",isactive=True,is_payment=False).exclude(type__in=type_ex).order_by('lineno')  
        else:
            queryset = ItemCart.objects.none()
        return queryset

    def list(self, request):
        try:
            global type_ex
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            empl = fmspw[0].Emp_Codeid
            cart_date = timezone.now().date()

           
            if self.request.GET.get('cust_noid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            today = datetime.datetime.now().strftime('%Y-%m-%d')
            # print(date.today(),"today")
            # print(self.request.GET.get('cart_date',None),date.today())
            # if str(self.request.GET.get('cart_date',None)) != str(date.today()):
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Date must be today date",'error': True}
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            cust_obj = Customer.objects.filter(pk=self.request.GET.get('cust_noid',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            cart_id = self.request.GET.get('cart_id',None)
            if not cart_id:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content cart_id is not given",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)

            cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
            cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site).exclude(type__in=type_ex)  
            # print(cartc_ids,"cartc_ids")
            if cartc_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            
            queryset = self.filter_queryset(self.get_queryset())
            if not queryset:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)

            # gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False; subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0;
            trans_amt=0.0 ;deposit_amt =0.0; billable_amount=0.0
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
                lst = []
                for d in data:
                    dict_v = dict(d)
                    cartobj = ItemCart.objects.filter(id=dict_v['id'],isactive=True,sitecode=site.itemsite_code).exclude(type__in=type_ex).first()  
                    stockobj = Stock.objects.filter(item_code=cartobj.itemcode,item_isactive=True).first()
                    if not stockobj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock Id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


                    # if float(dict_v['price']) <= 0.0:
                    #     msg = "Price should not be Zero for %s Treatment".format(stockobj.item_desc)
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                    #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
                    
                    if dict_v['quantity'] is None:
                        dict_v['quantity'] = 0.0

                    if float(dict_v['quantity']) > 0.0 and dict_v['quantity'] is not None:
                        dict_v['quantity'] = dict_v['quantity']
                    else:
                        dict_v['quantity'] = 0.0
                    
                    if cartobj.type == 'Deposit' and stockobj.item_div == '3':
                        tmp_ids = TmpItemHelper.objects.filter(itemcart=cartobj,site_code=site.itemsite_code)
                        
                        for emp in tmp_ids:
                            appt = Appointment.objects.filter(cust_noid=cartobj.cust_noid,appt_date=date.today(),
                            ItemSite_Codeid=fmspw[0].loginsite,emp_no=emp.helper_code) 
                            if not appt:
                                tmpids = TmpItemHelper.objects.filter(itemcart=cartobj,helper_code=emp.helper_code,
                                site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                                if tmpids:
                                    emp.delete()

                            if emp.appt_fr_time and emp.appt_to_time:         
                                appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
                                itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
                                if appt_ids:
                                    emp.delete()

                        for existing in cartobj.helper_ids.all():
                            cartobj.helper_ids.remove(existing) 

                        for exist in cartobj.service_staff.all():
                            cartobj.service_staff.remove(exist)     

                        for t in TmpItemHelper.objects.filter(itemcart=cartobj,site_code=site.itemsite_code):
                            helper_obj = Employee.objects.filter(emp_isactive=True,emp_code=t.helper_code).first()
                            cartobj.helper_ids.add(t) 
                            cartobj.service_staff.add(helper_obj.pk) 
        
                
                    tot_disc = dict_v['discount_amt'] + dict_v['additional_discountamt']
                    stock_obj = Stock.objects.filter(pk=dict_v['itemcodeid'],item_isactive=True)[0]
                    total_disc = dict_v['discount_amt'] + dict_v['additional_discountamt']
                    dict_v['price'] = "{:.2f}".format(float(dict_v['price']))
                    dict_v['total_price'] = "{:.2f}".format(float(dict_v['total_price']))
                    dict_v['discount_price'] = "{:.2f}".format(float(dict_v['discount_price']))
                    dict_v['item_class'] = stock_obj.Item_Classid.itm_desc
                    dict_v['sales_staff'] =   ','.join([v.display_name for v in cartobj.sales_staff.all() if v])
                    dict_v['service_staff'] = ','.join([v.display_name for v in cartobj.service_staff.all() if v])
                    # dict_v['tax'] = "{:.2f}".format(float(dict_v['tax']))
                    #discount keyword for other disc + trasc disc
                    dict_v['discount'] = "{:.2f}".format(float(tot_disc))
                    # dict_v['discount_amt'] = "{:.2f}".format(float(dict_v['discount_amt']))
                    dict_v['trans_amt'] = "{:.2f}".format(float(dict_v['trans_amt']))
                    dict_v['deposit'] = "{:.2f}".format(float(dict_v['deposit']))
                    # dict_v['additional_discount'] = "{:.2f}".format(float(dict_v['additional_discount']))
                    # dict_v['additional_discountamt'] = "{:.2f}".format(float(dict_v['additional_discountamt']))
                    dict_v['total_disc'] = "{:.2f}".format(float(total_disc))
                    dict_v['treatment_name'] = dict_v['itemdesc']+" "+" "+"("+str(dict_v['quantity'])+")"
                    dict_v['item_name'] = stock_obj.item_name

                    subtotal += float(dict_v['total_price'])
                    discount_amt += float(dict_v['discount_amt']) * int(dict_v['quantity'])
                    additional_discountamt += float(dict_v['additional_discountamt'])
                    # print(additional_discountamt,"additional_discountamt")
                    trans_amt += float(dict_v['trans_amt'])
                    deposit_amt += float(dict_v['deposit'])
                    # tax += float(dict_v['tax'])

                    lst.append(dict_v)

                # disc_percent = 0.0
                # if discount_amt > 0.0:
                #     disc_percent = (float(discount_amt) * 100) / float(net_deposit)
                #     after_line_disc = net_deposit
                # else:
                #     after_line_disc = net_deposit

                # add_percent = 0.0
                # if additional_discountamt > 0.0:
                #     # print(additional_discountamt,"additional_discountamt")
                #     add_percent = (float(additional_discountamt) * 100) / float(net_deposit)
                #     after_add_disc = after_line_disc 
                # else:
                #     after_add_disc = after_line_disc   

                
                # taxamt = 0.0
                # if gst.is_exclusive == True:
                #     taxamt = after_add_disc * (tax/100)
                #     billable_amount = "{:.2f}".format(after_add_disc + taxamt)
                # else:
                #     billable_amount = "{:.2f}".format(after_add_disc)


                sub_total = "{:.2f}".format(float(subtotal))
                billable_amount = "{:.2f}".format(deposit_amt + float(round_calc(deposit_amt))) # round()
                total_disc = discount_amt + additional_discountamt
                result = {'status': state,"message":message,'error': error, 'data':  lst,'subtotal':"{:.2f}".format(float(sub_total)),
                'discount': "{:.2f}".format(float(total_disc)),'trans_amt': "{:.2f}".format(float(trans_amt)),'deposit_amt':"{:.2f}".format(float(deposit_amt)),
                'billable_amount': "{:.2f}".format(float(billable_amount))}
            else:
                serializer = self.get_serializer()
                result = {'status': state,"message":message,'error': error, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def create(self, request):
        try:
            global type_ex
            for idx, req in enumerate(request.data, start=1):
                serializer = self.get_serializer(data=req)
                cart_date = timezone.now().date()

                if not 'cart_date' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart date",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if req['cart_date'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart date",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                if not 'cust_noid' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if req['cust_noid'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not 'itemcodeid' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item code ",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if 'itemcodeid' in req and req['itemcodeid'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item code ",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not 'price' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item price ",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if 'price' in req and req['price'] is 0.0:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item price ",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                # if not 'type' in req:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Type ",'error': False}
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                # else:
                #     if 'type' in req and not req['type']:
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Type",'error': False}
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

                # if str(req['cart_date']) != str(date.today()):
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Date must be today date",'error': True}
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)

                logstaff = Employee.objects.filter(emp_code=fmspw[0].emp_code,emp_isactive=True).first()
                if not logstaff:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Login user, employee is inactive",'error': True}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


                site = fmspw[0].loginsite

                cust_obj = Customer.objects.filter(pk=req['cust_noid'],cust_isactive=True).first()
                if not cust_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                stock_obj = Stock.objects.filter(pk=req['itemcodeid'],item_isactive=True).first()
                if not stock_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
            
                cart_lst = [];subtotal = 0.0; discount=0.0; billable_amount=0.0;trans_amt=0.0;deposit_amt = 0.0

                cart_id = request.GET.get('cart_id',None)
                if cart_id:
                    cartchids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                    cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex)  
                    if not cartchids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is not there for this cutomer,Give Without cart_id in parms!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    check = "Old"
                    #cust_noid=cust_obj,
                    cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                    cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site).exclude(type__in=type_ex)  
                    if cartc_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    cartcids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                    cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex)  
                    if cartcids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is there for this cutomer!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    check = "New"
                    control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                    if not control_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                    # cart_rec = ItemCart.objects.all().count()
                    # print(cart_rec,"cart_rec")
                    cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
                    final = list(set([r.cart_id for r in cartre]))
                    # print(final,len(final),"final")
                    code_site = site.itemsite_code
                    prefix = control_obj.control_prefix

                    lst = []
                    if final != []:
                        for f in final:
                            newstr = f.replace(prefix,"")
                            new_str = newstr.replace(code_site, "")
                            lst.append(new_str)
                            lst.sort(reverse=True)

                        # print(lst,"lst")
                        c_no = int(lst[0]) + 1
                        cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(c_no)
                    else:
                        cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                    
                    #cust_noid=cust_obj,
                    cartcc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                    cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site).exclude(type__in=type_ex)  
                    if cartcc_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                    #same customer
                    cartcu_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cart_date,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,check="New").exclude(type__in=type_ex)     
                    if len(cartcu_ids) == 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    #Different customer
                    cartcut_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,check="New").exclude(type__in=type_ex)     
                    if len(cartcut_ids) == 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                cag_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex)  
                if cag_ids:
                    lst = list(set([e.cust_noid.pk for e in cag_ids if e.cust_noid]))
                    if len(lst) > 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Each Item Cart ID should have one customer not multiple",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if lst[0] != (cust_obj.pk):
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item Cart ID already one customer id is there",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                if serializer.is_valid():
                    # if int(stock_obj.Item_Divid.itm_code) == 1 and stock_obj.Item_Divid.itm_desc == 'RETAIL PRODUCT' and stock_obj.Item_Divid.itm_isactive == True:
                    # carttype = False
                    # if str(req['type']) == 'Deposit': 
                    #     carttype = 'Deposit'
                    if int(stock_obj.item_div) == 1:
                        if req['item_uom'] is None:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Retail Product item uom should not be empty",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        quantity = 1
                        if int(quantity) > int(stock_obj.onhand_qty):
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Retail Product cart qty should not be greater than onhand qty ",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    # elif str(req['type']) == 'Top Up': 
                    #     carttype = 'Top Up'
                    #     item_div = ItemDiv.objects.filter(itm_code=stock_obj.item_div).first()
                    #     item_dept = ItemDept.objects.filter(itm_code=stock_obj.item_dept,itm_status=True).first()

                    #     if item_div.itm_code == '3' and item_dept.is_service == True:
                    #         acc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account']).first()
                    #         if not acc_obj:
                    #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Account ID does not exist!!",'error': True} 
                    #             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    #     elif item_div.itm_code == '1' and item_dept.is_retailproduct == True:
                    #         acc_obj = DepositAccount.objects.filter(pk=req['deposit_account']).order_by('id').first()
                    #         if not acc_obj:
                    #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit Account ID does not exist!!",'error': True} 
                    #             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    #     elif item_div.itm_code == '5' and item_dept.is_prepaid == True:
                    #         acc_obj = PrepaidAccount.objects.filter(pk=req['prepaid_account']).order_by('id').first() 
                    #         if not acc_obj:
                    #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid Account ID does not exist!!",'error': True} 
                    #             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    #     else:
                    #         acc_obj = None
                    #         if acc_obj is None:
                    #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Account ID does not exist!!",'error': True} 
                    #             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    #     if item_div.itm_code == '5' and item_dept.is_prepaid == True:
                    #         staffsno = str(acc_obj.staff_no).split(',')
                    #     else:
                    #         staffsno = str(acc_obj.sa_staffno).split(',')
                    #     empids = Employee.objects.filter(emp_code__in=staffsno,emp_isactive=True)
                        
                    # elif str(req['type']) == 'Sales': 
                    #     carttype = 'Sales' 
                    #     trmtacc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account']).first()
                    #     if not trmtacc_obj:
                    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Account ID does not exist!!",'error': True} 
                    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    #     trmt_obj = Treatment.objects.filter(pk=req['treatment']).first()
                    #     # print(trmt_obj,"trmt_obj")
                    #     # print(trmt_obj.helper_ids.all(),"helper_ids.all()")
                    #     if not trmt_obj:
                    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    #     if not trmt_obj.helper_ids.all():
                    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Service Staffs Treatment Done!!",'error': True} 
                    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        
                    #     if float(req['price']) < float(trmt_obj.unit_amount):
                    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Insufficent Amount in Treatment Account. Please Top Up!!",'error': True} 
                    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    tax_value = 0.0
                    if stock_obj.is_have_tax == True:
                        tax_value = gst.ITEM_VALUE

                    cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cart_date,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex).order_by('lineno')     
                    if not cartcuids:
                        lineno = 1
                    else:
                        rec = cartcuids.last()
                        lineno = float(rec.lineno) + 1  

                    # is_allow_foc = request.GET.get('is_foc',None)
                    if not self.request.GET.get('is_foc',None) is None and int(self.request.GET.get('is_foc',None)) == 1:
                        if not stock_obj.is_allow_foc == True:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Product doesn't have FOC",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        # if carttype in ['Top Up','Sales']:
                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC not allow for Top Up / Reedem",'error': True} 
                        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 


                        cart = serializer.save(cart_date=cart_date,phonenumber=cust_obj.cust_phone2,
                        customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                        itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc +" "+ "(FOC)",
                        quantity=1,price="{:.2f}".format(float(req['price'])),
                        sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                        tax="{:.2f}".format(tax_value),check=check,ratio=100.00,auto=False,is_foc=True,
                        discount_price=0.0,discount=0.0,discount_amt="{:.2f}".format(float(req['price'])),
                        total_price=float(req['price']) * 1.0,trans_amt=0.0,deposit=0.0,type="Deposit")
                    else:  
                        # depositamt = float(req['price']) * 1.0
                        # if str(req['type']) == 'Sales':
                        #     depositamt = 0.00

                        cart = serializer.save(cart_date=cart_date,phonenumber=cust_obj.cust_phone2,
                        customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                        itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                        quantity=1,price="{:.2f}".format(float(req['price'])),
                        sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                        tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                        discount_price=float(req['price']) * 1.0,total_price=float(req['price']) * 1.0,
                        trans_amt=float(req['price']) * 1.0,deposit=float(req['price']) * 1.0,type="Deposit")
                    
                    if int(stock_obj.item_div) == 3 and stock_obj.item_type == 'PACKAGE':
                        packhdr_ids = PackageHdr.objects.filter(code=stock_obj.item_code).first()
                        if packhdr_ids:
                            packdtl_ids = PackageDtl.objects.filter(package_code=packhdr_ids.code,isactive=True)
                            if packdtl_ids:
                                for padtl in packdtl_ids:
                                    padtl_deposit = padtl.price * padtl.qty
                                    PosPackagedeposit(code=padtl.code,description=padtl.description,price=padtl.price,
                                    discount=padtl.discount,package_code=padtl.package_code,package_description=packhdr_ids.description,
                                    qty=padtl.qty,unit_price=padtl.unit_price,ttl_uprice=padtl.ttl_uprice,site_code=site.itemsite_code,
                                    dt_lineno=cart.lineno,status="PENDING",deposit_amt=padtl_deposit,deposit_lineno=padtl.line_no,
                                    itemcart=cart).save()

    
                    # if str(req['type']) == 'Top Up':
                    #     for s in empids: 
                    #         cart.sales_staff.add(s) 

                    # elif str(req['type']) == 'Sales': 
                    #     for s in trmt_obj.helper_ids.all(): 
                    #         cart.service_staff.add(s.helper_id)

                    #     sa = trmt_obj.helper_ids.all().first()
                    #     cart.sales_staff.add(sa.helper_id)
                    if logstaff:
                        cart.sales_staff.add(logstaff.pk)
                    message = "Created Succesfully"
                    val = serializer.data
                    # if cart.id and check == "New":
                    #     control_obj.control_no = int(control_obj.control_no) + 1
                    #     control_obj.save()
                    
                    val['price'] = "{:.2f}".format(float(val['price']))
                    val['total_price'] = "{:.2f}".format(float(val['total_price']))
                    val['discount_price'] = "{:.2f}".format(float(val['discount_price']))
                    val['item_class'] = stock_obj.Item_Classid.itm_desc
                    val['sales_staff'] = ''
                    val['service_staff'] = ''
                    # val['tax'] = "{:.2f}".format(float(val['tax']))
                    val['deposit'] = "{:.2f}".format(float(val['deposit']))
                    val['trans_amt'] = "{:.2f}".format(float(val['trans_amt']))
                    val['treatment_name'] = val['itemdesc']+" "+" "+"("+str(val['quantity'])+")"
                    val['discount'] = "{:.2f}".format(float(val['discount']))
                    val['discount_amt'] = "{:.2f}".format(float(val['discount_amt']))
                    val['additional_discount'] = "{:.2f}".format(float(val['additional_discount']))
                    val['additional_discountamt'] = "{:.2f}".format(float(val['additional_discountamt']))

                    subtotal +=float(val['total_price'])
                    # tax += float(val['tax'])
                    discount += float(val['discount'])
                    trans_amt += float(val['trans_amt'])
                    deposit_amt += float(val['deposit'])

                    cart_lst.append({'cartid':cart.cart_id})

                    sub_total = "{:.2f}".format(float(subtotal))
                    # tax_amt = "{:.2f}".format(float(tax))
                    # discamt = subtotal * (discount/100)
                    # disc_amt = "{:.2f}".format(float(discamt))
                    # if subtotal < discamt:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Subtotal Must be greater than Discount Amount!!",'error': True} 
                    #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 


                    # amt = subtotal - discamt
                    # taxamt = amt * (tax/100)
                    # if gst.is_exclusive == True:
                    #     billable_amount = "{:.2f}".format(amt + taxamt)
                    # else:
                    #     billable_amount = "{:.2f}".format(amt)
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 'data': serializer.errors}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            if cart_lst != []:
                state= status.HTTP_201_CREATED
                error = False
                # result = {'status': state,"message":message,'error': error, 'data': cart_lst,'subtotal':sub_total,
                # 'discount':"{:.2f}".format(float(discount)),'trans_amt':"{:.2f}".format(float(trans_amt)),
                # 'deposit_amt':"{:.2f}".format(float(deposit_amt)),'billable_amount':sub_total}
                result = {'status': state,"message":message,'error': error, 'data': cart_lst}
                return Response(result, status=status.HTTP_201_CREATED)
        
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,'error': error, 'data': data}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def TopUpCartCreate(self, request):
        try:
            global type_ex
            cartdate = timezone.now().date()
            if not request.data:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please enter a valid pay amount!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
            for idx, req in enumerate(request.data, start=1):
                cust_obj = Customer.objects.filter(pk=req['cust_noid'],cust_isactive=True).first()
                if not cust_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite

            cart_lst = [];subtotal = 0.0; discount=0.0; billable_amount=0.0;trans_amt=0.0;deposit_amt = 0.0
            for idx, req in enumerate(request.data, start=1):
                cart_id = request.GET.get('cart_id',None)
                if cart_id:
                    cartchids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex)
                    if not cartchids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is not there for this cutomer,Give Without cart_id in parms!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    check = "Old"
                    #cust_noid=cust_obj,
                    cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site).exclude(type__in=type_ex)
                    if cartc_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    cartcids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex)
                    if cartcids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is there for this cutomer!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    check = "New"
                    control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                    if not control_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                        
                    cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
                    final = list(set([r.cart_id for r in cartre]))
                    code_site = site.itemsite_code
                    prefix = control_obj.control_prefix

                    lst = []
                    if final != []:
                        for f in final:
                            newstr = f.replace(prefix,"")
                            new_str = newstr.replace(code_site, "")
                            lst.append(new_str)
                            lst.sort(reverse=True)

                        print(lst,"lst")
                        c_no = int(lst[0]) + 1
                        cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(c_no)
                    else:
                        cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                    
                    #cust_noid=cust_obj,
                    cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site).exclude(type__in=type_ex)
                    if cartc_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                    #same customer
                    cartcu_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,check="New").exclude(type__in=type_ex)   
                    if len(cartcu_ids) == 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    #Different customer
                    cartcut_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,check="New").exclude(type__in=type_ex)   
                    if len(cartcut_ids) == 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                cag_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex)
                if cag_ids:
                    lst = list(set([e.cust_noid.pk for e in cag_ids if e.cust_noid]))
                    if len(lst) > 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Each Item Cart ID should have one customer not multiple",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if lst[0] != (cust_obj.pk):
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item Cart ID already one customer id is there",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                # if idx == 1:
                #     check = "New"
                # else:
                #     check = "Old"

                serializer = self.get_serializer(data=req)

                if not 'cart_date' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart date",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if req['cart_date'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart date",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                if not 'cust_noid' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if req['cust_noid'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not 'itemcodeid' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item code ",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if 'itemcodeid' in req and req['itemcodeid'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item code ",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not 'price' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item price ",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if req['price'] == 0.0 or not req['price']:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item price ",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                # if str(req['cart_date']) != str(date.today()):
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Date must be today date",'error': True}
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite

                
                cust_obj = Customer.objects.filter(pk=req['cust_noid'],cust_isactive=True).first()
                if not cust_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                stock_obj = Stock.objects.filter(pk=req['itemcodeid'],item_isactive=True).first()

                if not stock_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                item_div = ItemDiv.objects.filter(pk=stock_obj.Item_Divid.pk).first()
                item_dept = ItemDept.objects.filter(pk=stock_obj.Item_Deptid.pk,itm_status=True).first()

                if item_div.itm_code == '3' and item_dept.is_service == True:
                    acc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account'],site_code=site.itemsite_code).first()
                    if not acc_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Account ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
                    carttp_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,
                    treatment_account__pk=req['treatment_account'],type='Top Up').exclude(type__in=type_ex).order_by('lineno')

                elif item_div.itm_code == '1' and item_dept.is_retailproduct == True:
                    acc_obj = DepositAccount.objects.filter(pk=req['deposit_account'],site_code=site.itemsite_code).order_by('id').first()
                    if not acc_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit Account ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    carttp_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,
                    deposit_account__pk=req['deposit_account'],type='Top Up').exclude(type__in=type_ex).order_by('lineno')   
            
                elif item_div.itm_code == '5' and item_dept.is_prepaid == True:
                    acc_obj = PrepaidAccount.objects.filter(pk=req['prepaid_account'],site_code=site.itemsite_code).order_by('id').first() 
                    if not acc_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid Account ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    carttp_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,
                    prepaid_account__pk=req['prepaid_account'],type='Top Up').exclude(type__in=type_ex).order_by('lineno')   
                
                else:
                    acc_obj = None
                    if acc_obj is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Account ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    carttp_ids = None    
            
                gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
            
                
                if serializer.is_valid():
                    tax_value = 0.0
                    if stock_obj.is_have_tax == True:
                        tax_value = gst.ITEM_VALUE

                    cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex).order_by('lineno')   
                    if not cartcuids:
                        lineno = 1
                    else:
                        rec = cartcuids.last()
                        lineno = float(rec.lineno) + 1  

                    if item_div.itm_code == '5' and item_dept.is_prepaid == True:
                        staffsno = str(acc_obj.staff_no).split(',')
                    else:
                        staffsno = str(acc_obj.sa_staffno).split(',')
                    empids = Employee.objects.filter(emp_code__in=staffsno,emp_isactive=True)

                    
                    if not carttp_ids: 
                        # is_allow_foc = request.GET.get('is_foc',None)
                        if not self.request.GET.get('is_foc',None) is None and int(self.request.GET.get('is_foc',None)) == 1:
                            if self.request.GET.get('is_foc',None):
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Top Up will not have FOC!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            if not stock_obj.is_allow_foc == True:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Product doesn't have FOC",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                            customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                            itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                            quantity=1,price="{:.2f}".format(float(req['price'])),
                            sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                            tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                            discount_price=0.0,discount=0.0,discount_amt="{:.2f}".format(float(req['price'])),
                            total_price=float(req['price']) * 1.0,trans_amt=0.0,deposit=0.0,type="Top Up")
                        else:    
                            cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                            customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                            itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                            quantity=1,price="{:.2f}".format(float(req['price'])),
                            sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                            tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                            discount_price=float(req['price']) * 1.0,total_price=float(req['price']) * 1.0,
                            trans_amt=float(req['price']) * 1.0,deposit=float(req['price']) * 1.0,type="Top Up")

                        for s in empids: 
                            cart.sales_staff.add(s)

                        message = "Created Succesfully"
                        val = serializer.data
                    
                        val['price'] = "{:.2f}".format(float(val['price']))
                        val['total_price'] = "{:.2f}".format(float(val['total_price']))
                        val['discount_price'] = "{:.2f}".format(float(val['discount_price']))
                        val['item_class'] = stock_obj.Item_Classid.itm_desc
                        val['sales_staff'] = ''
                        val['service_staff'] = ''
                        # val['tax'] = "{:.2f}".format(float(val['tax']))
                        val['deposit'] = "{:.2f}".format(float(val['deposit']))
                        val['trans_amt'] = "{:.2f}".format(float(val['trans_amt']))
                        val['treatment_name'] = val['itemdesc']+" "+" "+"("+str(val['quantity'])+")"
                        val['discount'] = "{:.2f}".format(float(val['discount']))
                        val['discount_amt'] = "{:.2f}".format(float(val['discount_amt']))
                        val['additional_discount'] = "{:.2f}".format(float(val['additional_discount']))
                        val['additional_discountamt'] = "{:.2f}".format(float(val['additional_discountamt']))

                        subtotal +=float(val['total_price'])
                        # tax += float(val['tax'])
                        discount += float(val['discount'])
                        trans_amt += float(val['trans_amt'])
                        deposit_amt += float(val['deposit'])

                        cart_lst.append(cart.cart_id)
                        sub_total = "{:.2f}".format(float(subtotal))
                        # tax_amt = "{:.2f}".format(float(tax))
                        # discamt = subtotal * (discount/100)
                        # disc_amt = "{:.2f}".format(float(discamt))
                        # if subtotal < discamt:
                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Subtotal Must be greater than Discount Amount!!",'error': True} 
                        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 


                        # amt = subtotal - discamt
                        # taxamt = amt * (tax/100)
                        # if gst.is_exclusive == True:
                        #     billable_amount = "{:.2f}".format(amt + taxamt)
                        # else:
                        #     billable_amount = "{:.2f}".format(amt)
                    else:
                        if carttp_ids:
                            if len(carttp_ids) > 1:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID for Topup len must be one !!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            
                            al_ids = carttp_ids.first() 
                            ItemCart.objects.filter(pk=al_ids.pk).update(price="{:.2f}".format(float(req['price'])),discount_price=float(req['price']) * 1.0,
                            total_price=float(req['price']) * 1.0,trans_amt=float(req['price']) * 1.0,deposit=float(req['price']) * 1.0)
                            al_ids.save()
                            cart_lst.append(al_ids.cart_id)
                            message = "Updated Succesfully"
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 'data': serializer.errors}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            if cart_lst != []:
                cart_lst = list(set(cart_lst)) 
                if len(cart_lst) > 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID for TopUp should be one!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                # if check == 'New':
                #     control_obj.control_no = int(control_obj.control_no) + 1
                #     control_obj.save()

                state= status.HTTP_201_CREATED
                error = False
                # result = {'status': state,"message":message,'error': error, 'data': cart_lst,'subtotal':sub_total,
                # 'discount':"{:.2f}".format(float(discount)),'trans_amt':"{:.2f}".format(float(trans_amt)),
                # 'deposit_amt':"{:.2f}".format(float(deposit_amt)),'billable_amount':sub_total}
                result = {'status': state,"message":message,'error': error, 'data': {'cart_id': cart_lst[0]}}
                return Response(result, status=status.HTTP_201_CREATED)
        
            message = "Invalid Input"
            error = True
            data = []
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,'error': error, 'data': data}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def TrmtDoneCartCreate(self, request):
        try:
            global type_ex
            cartdate = timezone.now().date()
            for idx, req in enumerate(request.data, start=1):
                cust_obj = Customer.objects.filter(pk=req['cust_noid'],cust_isactive=True).first()
                if not cust_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            
                site = fmspw[0].loginsite
                
            
            cart_lst = [];subtotal = 0.0; discount=0.0; billable_amount=0.0;trans_amt=0.0;deposit_amt = 0.0
            for idx, req in enumerate(request.data, start=1):
                cart_id = request.GET.get('cart_id',None)
                if cart_id:
                    cartchids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex)
                    if not cartchids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is not there for this cutomer,Give Without cart_id in parms!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    check = "Old"
                    #cust_noid=cust_obj,
                    cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site).exclude(type__in=type_ex)
                    if cartc_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    cartcids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex)
                    if cartcids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is there for this cutomer!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    check = "New"

                    control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                    if not control_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                        
                    cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
                    final = list(set([r.cart_id for r in cartre]))
                    code_site = site.itemsite_code
                    prefix = control_obj.control_prefix

                    lst = []
                    if final != []:
                        for f in final:
                            newstr = f.replace(prefix,"")
                            new_str = newstr.replace(code_site, "")
                            lst.append(new_str)
                            lst.sort(reverse=True)

                        # print(lst,"lst")
                        c_no = int(lst[0]) + 1
                        cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(c_no)
                    else:
                        cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                    
                    #cust_noid=cust_obj,
                    cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site).exclude(type__in=type_ex)
                    if cartc_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                    #same customer
                    cartcu_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,check="New").exclude(type__in=type_ex)   
                    if len(cartcu_ids) == 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    #Different customer
                    cartcut_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,check="New").exclude(type__in=type_ex)   
                    if len(cartcut_ids) == 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                cag_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex)
                if cag_ids:
                    lst = list(set([e.cust_noid.pk for e in cag_ids if e.cust_noid]))
                    if len(lst) > 1:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Each Item Cart ID should have one customer not multiple",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if lst[0] != (cust_obj.pk):
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item Cart ID already one customer id is there",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                # if idx == 1:
                #     check = "New"
                # else:
                #     check = "Old"

                serializer = self.get_serializer(data=req)

                if not 'cart_date' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart date",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if req['cart_date'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart date",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                if not 'cust_noid' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if req['cust_noid'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not 'itemcodeid' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item code ",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if 'itemcodeid' in req and req['itemcodeid'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item code ",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not 'price' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item price ",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if 'price' in req and req['price'] is 0.0:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Item price ",'error': False}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                # if str(req['cart_date']) != str(date.today()):
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Date must be today date",'error': True}
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite

            
                cust_obj = Customer.objects.filter(pk=req['cust_noid'],cust_isactive=True).first()
                if not cust_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                stock_obj = Stock.objects.filter(pk=req['itemcodeid'],item_isactive=True).first()
                if not stock_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                trmtacc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account'],site_code=site.itemsite_code).first()
                if not trmtacc_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Account ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                trmt_obj = Treatment.objects.filter(pk=req['treatment'],site_code=site.itemsite_code).first()
                # print(trmt_obj,"trmt_obj")
                # print(trmt_obj.helper_ids.all(),"helper_ids.all()")
                if not trmt_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
                
                if not trmt_obj.helper_ids.all():
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Service Staffs Treatment Done!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                if float(req['price']) < float(trmt_obj.unit_amount):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Insufficent Amount in Treatment Account. Please Top Up!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                

                if serializer.is_valid():
                    tax_value = 0.0
                    if stock_obj.is_have_tax == True:
                        tax_value = gst.ITEM_VALUE

                    cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex).order_by('lineno')   
                    if not cartcuids:
                        lineno = 1
                    else:
                        rec = cartcuids.last()
                        lineno = float(rec.lineno) + 1  

                    # staffsno = str(trmtacc_obj.sa_staffno).split(',')
                    # empids = Employee.objects.filter(emp_code__in=staffsno,emp_isactive=True)

                    # is_allow_foc = request.GET.get('is_foc',None)

                    carttr_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                    cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site,
                    treatment_account__pk=trmtacc_obj.pk,treatment__pk=trmt_obj.pk,type='Sales').exclude(type__in=type_ex).order_by('lineno')   

                    if not carttr_ids:
                        if not self.request.GET.get('is_foc',None) is None and int(self.request.GET.get('is_foc',None)) == 1:
                            if self.request.GET.get('is_foc',None):
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sales will not have FOC!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            if not stock_obj.is_allow_foc == True:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Product doesn't have FOC",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                            customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                            itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                            quantity=1,price="{:.2f}".format(float(req['price'])),
                            sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                            tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                            discount_price=0.0,discount=0.0,discount_amt="{:.2f}".format(float(req['price'])),
                            total_price=float(req['price']) * 1.0,trans_amt=0.0,deposit=0.0,type="Sales")
                        else:    
                            cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                            customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                            itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                            quantity=1,price="{:.2f}".format(float(req['price'])),
                            sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                            tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                            discount_price=float(req['price']) * 1.0,total_price=float(req['price']) * 1.0,
                            trans_amt=float(req['price']) * 1.0,deposit=0.0,type="Sales")

                    
                        for s in trmt_obj.helper_ids.all(): 
                            cart.service_staff.add(s.helper_id)

                        sa = trmt_obj.helper_ids.all().first()
                        cart.sales_staff.add(sa.helper_id)
            
                        message = "Created Succesfully"
                        val = serializer.data
                    
                        val['price'] = "{:.2f}".format(float(val['price']))
                        val['total_price'] = "{:.2f}".format(float(val['total_price']))
                        val['discount_price'] = "{:.2f}".format(float(val['discount_price']))
                        val['item_class'] = stock_obj.Item_Classid.itm_desc
                        val['sales_staff'] = ''
                        val['service_staff'] = ''
                        # val['tax'] = "{:.2f}".format(float(val['tax']))
                        # val['deposit'] = "{:.2f}".format(float(val['deposit']))
                        val['trans_amt'] = "{:.2f}".format(float(val['trans_amt']))
                        val['treatment_name'] = val['itemdesc']+" "+" "+"("+str(val['quantity'])+")"
                        val['discount'] = "{:.2f}".format(float(val['discount']))
                        val['discount_amt'] = "{:.2f}".format(float(val['discount_amt']))
                        val['additional_discount'] = "{:.2f}".format(float(val['additional_discount']))
                        val['additional_discountamt'] = "{:.2f}".format(float(val['additional_discountamt']))

                        subtotal +=float(val['total_price'])
                        # tax += float(val['tax'])
                        discount += float(val['discount'])
                        trans_amt += float(val['trans_amt'])
                        # deposit_amt += float(val['deposit'])

                        cart_lst.append(cart.cart_id)
                        sub_total = "{:.2f}".format(float(subtotal))
                        # tax_amt = "{:.2f}".format(float(tax))
                        # discamt = subtotal * (discount/100)
                        # disc_amt = "{:.2f}".format(float(discamt))
                        # if subtotal < discamt:
                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Subtotal Must be greater than Discount Amount!!",'error': True} 
                        #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 


                        # amt = subtotal - discamt
                        # taxamt = amt * (tax/100)
                        # if gst.is_exclusive == True:
                        #     billable_amount = "{:.2f}".format(amt + taxamt)
                        # else:
                        #     billable_amount = "{:.2f}".format(amt)
                    else:
                        if carttr_ids:
                            if len(carttr_ids) > 1:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID for TD len must be one !!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            
                            message = "Already Cart Added"
                            first = carttr_ids.first()    
                            cart_lst.append(first.cart_id)
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 'data': serializer.errors}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            if cart_lst != []:
                cart_lst = list(set(cart_lst)) 
                if len(cart_lst) > 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID for TD should be one!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                # if check == 'New':
                #     control_obj.control_no = int(control_obj.control_no) + 1
                #     control_obj.save()

                state= status.HTTP_201_CREATED
                error = False
                # result = {'status': state,"message":message,'error': error, 'data': cart_lst,'subtotal':sub_total,
                # 'discount':"{:.2f}".format(float(discount)),'trans_amt':"{:.2f}".format(float(trans_amt)),
                # 'deposit_amt':0.0,'billable_amount':0.0}
                result = {'status': state,"message":message,'error': error, 'data': {'cart_id':cart_lst[0]}}
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                if carttr_ids:
                    result = {'status': status.HTTP_201_CREATED,"message":"Already Cart Created",'error': False}
                    return Response(result, status=status.HTTP_201_CREATED)
                else:
                    result = {'status': status.HTTP_201_CREATED,"message":"Invalid Input",'error': False}
                    return Response(result, status=status.HTTP_201_CREATED)

            message = "Invalid Input"
            error = True
            data = []
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,'error': error, 'data': data}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
            
       
        
    def get_object(self, pk):
        try:
            return ItemCart.objects.get(pk=pk,isactive=True)
        except ItemCart.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            global type_ex
            cart = self.get_object(pk)
            if cart.type in ['Top Up','Sales']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

            # print(cart.helper_ids.all())
            # print(cart.helper_ids.all().filter(times="01").values('times').annotate(Count('id')).order_by().filter(id__count__gt=1))
            sales_lst = []
            for v in cart.sales_staff.all():
                val = {'id':v.pk,'emp_name':v.emp_name}
                sales_lst.append(val)
            
            serializer = itemCartListSerializer(cart)
            data = serializer.data
            if cart.itemcodeid.Stock_PIC:
                data['stock_pic'] = "http://"+request.META['HTTP_HOST']+cart.itemcodeid.Stock_PIC.url
            else:
                data['stock_pic'] = None   
            # data['products_used'] = ""
            data['discount_reason'] = ""
            data['discreason_txt'] = ""
            data['discpercent'] = int(float(round_calc(data['discount'])))
            data['discountamt'] = "{:.2f}".format(float(data['discount_amt']))
            data['total_price'] = "{:.2f}".format(float(data['total_price']))
            data['discount_price'] = "{:.2f}".format(float(data['discount_price']))
            data['trans_amt'] = "{:.2f}".format(float(data['trans_amt']))
            data['deposit'] = "{:.2f}".format(float(data['deposit']))
            data['ratio'] = "{:.2f}".format(float(data['ratio']))
            data['sales_staff'] =   sales_lst
            data['item_div'] = cart.itemcodeid.item_div if cart.itemcodeid.item_div else ""
            # data['products_used'] = ','.join([p.item_desc for p in products_used if p.item_desc])
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
            
    def update(self, request, pk=None):
        try:
            itemcart = self.get_object(pk)
            cust_obj = itemcart.cust_noid
            cart_id = itemcart.cart_id
            cart_date = itemcart.cart_date
            trans_amt = itemcart.trans_amt

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
        
            empl = fmspw.Emp_Codeid

            if itemcart.type in ['Top Up','Sales']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not self.request.GET.get('disc_reset',None) is None and int(self.request.GET.get('disc_reset',None)) == 1 and not self.request.GET.get('disc_add',None) is None and int(self.request.GET.get('disc_add',None)) == 1:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Disc Add and Reset will not be allowed at the same time!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        
            if not self.request.GET.get('disc_reset',None) is None and int(self.request.GET.get('disc_reset',None)) == 1:
            
                if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher / Prepaid / Package not allow Discount Reset!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
                if itemcart.is_foc == True:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give discount.",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        

                trascamt = itemcart.price * itemcart.quantity
                ItemCart.objects.filter(id=itemcart.id).update(discount=0.0,discount_amt=0.0,
                additional_discount=0.0,additional_discountamt=0.0,
                discount_price=itemcart.price,deposit=trascamt,trans_amt=trascamt)
                for existing in itemcart.disc_reason.all():
                    itemcart.disc_reason.remove(existing) 

                itemcart.pos_disc.all().filter(istransdisc=False,dt_status='New').delete()    

                result = {'status': status.HTTP_200_OK,"message":"Reset Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

        
            cart_ids = ItemCart.objects.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
            cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code).order_by('lineno') 
            disclimit = itemcart.itemcodeid.disclimit

            serializer = itemCartSerializer(itemcart, data=request.data, partial=True)
            if serializer.is_valid():
                if not self.request.GET.get('disc_add',None) is None and int(self.request.GET.get('disc_add',None)) == 1:
                    if itemcart.is_foc == True:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give discount.",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
                    if not 'discount' in request.data and not 'discount_amt' in request.data:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give either Discount / Discount Amount,Both should not be zero!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    else:
                        if 'discount' in request.data and 'discount_amt' in request.data:
                            if not float(request.data['discount']) >= 0 and float(request.data['discount_amt']) >= 0:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give either Discount / Discount Amount,Both should not be zero!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if disclimit == 0.0:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Discount is not allowed for this product !!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    
                    if 'discount' in request.data and float(request.data['discount']) != 0.0:
                        
                        if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher / Prepaid / Package not allow Discount!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                        if float(request.data['discount']) > disclimit:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Discount is not greater than stock discount!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        if float(request.data['discount']) > float(itemcart.price):
                            msg = "Discount is > {0} !".format(itemcart.price)
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                        
                        discount = itemcart.discount + float(request.data['discount'])
                        discount_amt = itemcart.discount_amt + float(request.data['discount_amt'])
                        # discount = float(request.data['discount'])
                        # discount_amt = float(request.data['discount_amt'])


                        value = float(itemcart.price) - discount_amt
                        amount = value * itemcart.quantity
                        if float(amount) <= 0.0:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit Should not be negative!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                        ItemCart.objects.filter(id=itemcart.id).update(discount=discount,
                        discount_amt=discount_amt,discount_price=value,deposit=amount,trans_amt=amount)
                    else:
                        if 'discount_amt' in request.data and float(request.data['discount_amt']) != 0.0:
                            
                            if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher / Prepaid / Package not allow Discount!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                            discamt = float(request.data['discount_amt'])
                            dt_discPercent = (float(discamt) * 100) / float(itemcart.price)
                            if dt_discPercent  > disclimit: 
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Discount is not greater than stock discount!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                            
                            if float(request.data['discount_amt']) > itemcart.price:
                                msg = "Discount is > {0} !".format(itemcart.price)
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                            
                            discount = itemcart.discount + float(request.data['discount'])
                            discount_amt = itemcart.discount_amt + float(request.data['discount_amt'])
                            # print(discount_amt,"discount_amt")
                            # discount = float(request.data['discount'])
                            # discount_amt = float(request.data['discount_amt'])

                            value = float(itemcart.price) - discount_amt
                            # print(value,"value")
                            amount = value * itemcart.quantity
                            # print(amount,"amount")
                            if float(amount) <= 0.0:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit Should not be negative!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                            ItemCart.objects.filter(id=itemcart.id).update(discount=discount,
                            discount_amt=discount_amt,discount_price=value,deposit=amount,trans_amt=amount)
                        
                    #disc reason 

                    if 'disc_reason' in request.data and not request.data['disc_reason'] is None and request.data['disc_reason'] != '':
                    
                        if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher / Prepaid / Package not allow Discount Reason!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                        discobj = PaymentRemarks.objects.filter(pk=request.data['disc_reason'],isactive=True).first()
                        if not discobj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Disc Reason ID does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                        
                        if discobj.r_code == '100006' and discobj.r_desc == 'OTHERS':
                            if request.data['discreason_txt'] is None:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Enter Disc Reason Text!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                            if 'discreason_txt' not in request.data:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Enter Disc Reason Text and add key!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            ItemCart.objects.filter(id=itemcart.id).update(discreason_txt=request.data['discreason_txt']) 
                            itemcart.disc_reason.add(discobj.id)
                            reason = request.data['discreason_txt']
                        else:
                            itemcart.disc_reason.add(discobj.id)
                            reason = discobj.r_desc
                            
                        line_ids = itemcart.pos_disc.all().filter(istransdisc=False).order_by('line_no').last() 
                        # print(line_ids,"line_ids")
                        if line_ids != None:
                            line_no = int(line_ids.line_no) + 1
                        else:
                            line_no = 1    

                        posdisc = PosDisc(sa_transacno=None,dt_itemno=itemcart.itemcodeid.item_code+"0000",
                        disc_amt=request.data['discount_amt'],disc_percent=request.data['discount'],
                        dt_lineno=itemcart.lineno,remark=reason,site_code=itemcart.sitecodeid.itemsite_code,
                        dt_status="New",dt_auto=0,line_no=line_no,disc_user=empl.emp_code,lnow=1,dt_price=None,
                        istransdisc=False)
                        posdisc.save()
                        # print(posdisc.id,"posdisc")  
                        itemcart.pos_disc.add(posdisc.id)  
                
                    result = {'status': status.HTTP_200_OK,"message":"Discount added Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)

                total_disc = itemcart.discount_amt + itemcart.additional_discountamt
                if self.request.data['quantity']:
                    if float(self.request.data['quantity']) <= 0.0:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Quantity Should not be negative/Zero!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        
                if not self.request.data['quantity'] is None and request.data['quantity'] != 0.0:
                    #client told not to give 
                    # if itemcart.is_foc == True:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give discount.",'error': True} 
                    #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
                
                    if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
                        if float(itemcart.quantity) != float(self.request.data['quantity']):
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid/Voucher/Package not allow Quantity!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    # float(request.data['discount_amt']))
                    if not int(itemcart.itemcodeid.item_div) in [4,5]: 
                        total_price = float(request.data['price']) * int(request.data['quantity'])
                        after_linedisc = (float(request.data['price']) - float(itemcart.discount_amt)) * int(request.data['quantity'])
                        trans_amt = after_linedisc - float(itemcart.additional_discountamt)
                        deposit = after_linedisc - float(itemcart.additional_discountamt)
                        if itemcart.is_foc == True:
                            ItemCart.objects.filter(id=itemcart.id).update(quantity=request.data['quantity'],
                            total_price=total_price)
                        else:
                            ItemCart.objects.filter(id=itemcart.id).update(quantity=request.data['quantity'],
                            total_price=total_price,trans_amt=trans_amt,deposit=deposit)
                            itemcart.quantity = request.data['quantity']
                            itemcart.save()

                    # print(itemcart.quantity,itemcart.price,itemcart.total_price,itemcart.discount_price,itemcart.trans_amt,itemcart.deposit,"QTY")

                # if not self.request.data['products_used'] is None and request.data['products_used'] != []: 
                #     products_used = self.request.data['products_used']
                #     for salon in products_used:
                #         stock = Stock.objects.filter(id=salon,item_isactive=True,Item_Divid__itm_code=2,
                #         Item_Divid__itm_desc='SALON PRODUCT',Item_Divid__itm_isactive=True)
                #         if not stock:
                #             msg = "Salon Products id %s is not present in Stock!!".format(salon)
                #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                #             return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                #         itemcart.products_used.add(salon) 
                #         itemcart.save()    
                
                if not self.request.data['sales_staff'] is None and request.data['sales_staff'] != []: 
                    sales_staff = self.request.data['sales_staff']
                    for ex in itemcart.sales_staff.all():
                        itemcart.sales_staff.remove(ex) 

                    for sales in sales_staff:
                        emp = Employee.objects.filter(pk=sales,emp_isactive=True)
                        if not emp:
                            msg = "Sales staff id %s is not present in Employee!!".format(sales)
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        # if not self.request.GET.get('sales_all',None) is None and request.GET.get('sales_all',None) == "1":
                        #     for c in cart_ids:
                        #         for existing in c.sales_staff.all():
                        #             c.sales_staff.remove(existing) 
                        #         c.sales_staff.add(sales) 
                        #         c.save()

                        if not self.request.GET.get('sales_all',None) is None and request.GET.get('sales_all',None) == "0":
                            itemcart.sales_staff.add(sales) 
                            itemcart.save()
                
                # if not self.request.data['service_staff'] is None and request.data['service_staff'] != []:
                #     service_staff =  self.request.data['service_staff']
                #     for service in service_staff:
                #         emp_s = Employee.objects.filter(pk=service,emp_isactive=True)
                #         if not emp_s:
                #             msg = "Service staff id %s is not present in Employee!!".format(service)
                #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                #             return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                #         if not self.request.GET.get('service_all',None) is None and request.GET.get('service_all',None) == "1":
                #             for c in cart_ids:
                #                 c.service_staff.add(service) 
                #                 c.save()
                #         if not self.request.GET.get('service_all',None) is None and request.GET.get('service_all',None) == "0":
                #             itemcart.service_staff.add(service) 
                #             itemcart.save()
    
            
                if 'itemstatus' in request.data and not request.data['itemstatus'] is None:
                    statusobj = ItemStatus.objects.filter(pk=request.data['itemstatus'],itm_isactive=True).first()
                    if not statusobj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"ItemStatus ID does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    ItemCart.objects.filter(id=itemcart.id).update(itemstatus=statusobj)   
                
                if self.request.data['price']: 
                    if float(self.request.data['price']) <= 0.0:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Price Should not be negative/Zero!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
                if not self.request.data['price'] is None and request.data['price'] != 0.0:
                
                    if itemcart.is_foc == True:
                        if float(itemcart.price) != float(self.request.data['price']):
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give Price Change.",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                    if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
                        if float(itemcart.price) != float(self.request.data['price']):
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher / Prepaid / Package not allow Price!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                    # float(request.data['discount_amt']))
                    if not int(itemcart.itemcodeid.item_div) in [4,5]: 
                        total_price = float(request.data['price']) * int(request.data['quantity'])
                        discount_price = float(request.data['price']) - total_disc
                        after_linedisc = (float(request.data['price']) - float(itemcart.discount_amt)) * int(request.data['quantity'])
                        trans_amt = after_linedisc - float(itemcart.additional_discountamt)
                        deposit = after_linedisc - float(itemcart.additional_discountamt)

                    
                        if itemcart.is_foc == False:
                            ItemCart.objects.filter(id=itemcart.id).update(price=self.request.data['price'],
                            total_price=total_price,discount_price=discount_price,trans_amt=trans_amt,deposit=deposit)

                        # print(itemcart.quantity,itemcart.price,itemcart.total_price,itemcart.discount_price,itemcart.trans_amt,itemcart.deposit,"price")

                
                #hold reason,hold qty,foc reason
                
                if not self.request.GET.get('deposit',None) is None and float(request.GET.get('deposit',None)) > 0.0:
                    if int(itemcart.itemcodeid.item_div) == 4:
                        if float(itemcart.deposit) != float(self.request.GET.get('deposit',None)):
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit can't be changed for Voucher Product!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                    if int(float(self.request.GET.get('deposit',None))) > int(trans_amt):
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit should not be greater than transaction amount!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if itemcart.is_foc == True:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give Deposit.",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        

                    if float(self.request.GET.get('deposit',None)) == 0.0:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit should not be Zero!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if int(itemcart.itemcodeid.item_div) != 4:
                        ItemCart.objects.filter(id=itemcart.id).update(deposit=self.request.GET.get('deposit',None))                    

                if 'remark' in request.data and not request.data['remark'] is None:
                    ItemCart.objects.filter(id=itemcart.id).update(remark=request.data['remark'])    

                if 'focreason' in request.data and not request.data['focreason'] is None:
                    if 'focreason' in request.data and request.data['focreason']:
                        if not request.data['focreason'] is None:                
                            if int(itemcart.itemcodeid.item_div) == 5:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid not allow Foc Reason!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        
                            focobj = FocReason.objects.filter(pk=request.data['focreason'],foc_reason_isactive=True).first()
                            if not focobj:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FocReason ID does not exist!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            if itemcart.itemcodeid.is_allow_foc == None or itemcart.itemcodeid.is_allow_foc == False:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item will not have is allow foc true!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                            
                            if disclimit != 100.00:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item will not have 100% disclimit!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                            
                            ItemCart.objects.filter(id=itemcart.id).update(focreason=focobj)                    
                    
                if 'holdreason' in request.data and not request.data['holdreason'] is None:
                    if itemcart.is_foc == True:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give holdreason.",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
                    holdobj = HolditemSetup.objects.filter(pk=request.data['holdreason']).first()
                    if not holdobj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"HoldReason ID does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if int(self.request.data['holditemqty']) == 0:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please enter Hold item Qty~!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        
                    ItemCart.objects.filter(id=itemcart.id).update(holdreason=holdobj)  
                                    
                
                if not self.request.data['holditemqty'] is None and request.data['holditemqty'] != 0:
                    if self.request.data['holditemqty']:
                        if itemcart.is_foc == True:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give holditemqty.",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
                        if int(self.request.data['holditemqty']) > int(itemcart.quantity) or int(self.request.data['holditemqty']) <= 0:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Enter valid Hold Item Qty,Cart Qty {0}!".format(itemcart.quantity),
                            'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        ItemCart.objects.filter(id=itemcart.id).update(holditemqty=request.data['holditemqty'])  

                if not self.request.data['ratio'] is None and request.data['ratio'] != 0.0:
                    ItemCart.objects.filter(id=itemcart.id).update(ratio=request.data['ratio'])  
        
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                result = {'status': state,"message":message,'error': error}
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = serializer.errors
            error = True
            result = {'status': state,"message":message,'error': error}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def SetAdditionalDiscList(self, request): 
        try:
            if self.request.GET.get('cart_date',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart_date",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            if self.request.GET.get('cust_noid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            cust_obj = Customer.objects.filter(pk=self.request.GET.get('cust_noid',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            cart_id = self.request.GET.get('cart_id',None)
            if not cart_id:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content cart_id is not given",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)

            queryset = self.filter_queryset(self.get_queryset()).exclude(type__in=('Top Up','Sales'))
            if not queryset:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
            
            cart_ids = queryset.filter(itemcodeid__item_div__in=[1,3],itemcodeid__item_type='SINGLE').exclude(is_foc=True)
            if not cart_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transac Discount not allowable!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            lst = [];total_amount = 0.0;other_disc = 0.0;net_amount=0.0;tran_disc=0.0;deposit_amount=0.0
            for c in cart_ids:
                val = {'id':c.pk,'lineno':c.lineno,'item_code':c.itemcodeid.item_code,'item_desc':c.itemcodeid.item_name,
                'qty':c.quantity,'unit_price':"{:.2f}".format(float(c.price)),'other_disc':"{:.2f}".format(float(c.discount_amt)),
                'tran_disc':"{:.2f}".format(float(c.additional_discountamt)),'net_amount':"{:.2f}".format(float(c.trans_amt)),
                'deposit_amount':"{:.2f}".format(float(c.deposit)),'auto': c.auto}
                lst.append(val)
                if c.auto == True:
                    total_amount += c.total_price
                    other_disc += c.discount_amt * c.quantity
                    tran_disc += c.additional_discountamt
                    net_amount += c.trans_amt
                    deposit_amount += c.deposit

            balance = total_amount - other_disc

            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,
            'data': lst,'total_amount':"{:.2f}".format(float(total_amount)),'other_disc':"{:.2f}".format(float(other_disc)),
            'balance':"{:.2f}".format(float(balance)),'tran_disc':"{:.2f}".format(float(tran_disc)),
            'net_amount':"{:.2f}".format(float(net_amount)),'deposit_amount':"{:.2f}".format(float(deposit_amount))}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
                

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def SetAdditionalDisc(self, request): 
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        
            empl = fmspw.Emp_Codeid

            # if self.request.GET.get('cart_date',None) is None:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart_date",'error': True}
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            if self.request.GET.get('cust_noid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cust_noid",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            cust_obj = Customer.objects.filter(pk=self.request.GET.get('cust_noid',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            cart_id = self.request.GET.get('cart_id',None)
            if not cart_id:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content cart_id is not given",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)

            queryset = self.filter_queryset(self.get_queryset()).filter(itemcodeid__item_div__in=[1,3],itemcodeid__item_type='SINGLE').exclude(type__in=('Top Up','Sales'),is_foc=True)
            if not queryset:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)

            cart_ids = queryset
            if not cart_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"There is not cart based on this Cart ID so create cart then add addtional discount!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            cnt = cart_ids.filter(auto=True).count()
            if cnt == 0:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Any One Cart Line Must Have Auto.",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            for c in cart_ids:
                if c.auto == True:
                    values = float(c.price) - c.discount_amt
                    tra_amount = values * c.quantity
                    ItemCart.objects.filter(id=c.id).update(additional_discount=0.0,additional_discountamt=0.0,
                    discount_price=values,deposit=tra_amount,trans_amt=tra_amount)
                    c.pos_disc.all().filter(istransdisc=True,dt_status='New').delete()  
            
            other_disc = sum([ca.discount_amt * ca.quantity for ca in cart_ids if ca.discount_amt and ca.quantity])
            transamtids = cart_ids.filter(auto=True).aggregate(Sum('trans_amt'),Sum('total_price'))
            totaltrans_amt = float(transamtids['trans_amt__sum'])
            total_amount = float(transamtids['total_price__sum'])

            if not self.request.GET.get('disc_reset',None) is None and int(self.request.GET.get('disc_reset',None)) == 1 and not self.request.GET.get('net_amt',None) is None and int(self.request.GET.get('net_amt',None)) != 0.0:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Disc Reset and Net Amount add will not be allowed at the same time!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            if not self.request.GET.get('disc_reset',None) is None and int(self.request.GET.get('disc_reset',None)) == 1:
                reset_cartids = self.filter_queryset(self.get_queryset()).filter(itemcodeid__item_div__in=[1,3],itemcodeid__item_type='SINGLE').exclude(type__in=('Top Up','Sales'),is_foc=True)
                for cr in reset_cartids:
                    if cr.auto == True:
                        revalue = float(cr.price) - cr.discount_amt
                        reamount = revalue * cr.quantity
                        ItemCart.objects.filter(id=cr.id).update(additional_discount=0.0,additional_discountamt=0.0,
                        discount_price=revalue,deposit=reamount,trans_amt=reamount)
                        cr.pos_disc.all().filter(istransdisc=True,dt_status='New').delete()    
                
                result = {'status': status.HTTP_200_OK,"message":"Reset Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            if not self.request.GET.get('disc_reason',None) is None and request.GET.get('disc_reason',None) != '':
                discobj = PaymentRemarks.objects.filter(pk=self.request.GET.get('disc_reason',None),isactive=True).first()
                if not discobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Disc Reason ID does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                if discobj.r_code == '100006' and discobj.r_desc == 'OTHERS':
                    if self.request.GET.get('discreason_txt',None) is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Enter Disc Reason Text!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    if 'discreason_txt' not in self.request.GET:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Enter Disc Reason Text and add key!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    reason = self.request.GET.get('discreason_txt',None)
                else:
                    reason = discobj.r_desc

            if not self.request.GET.get('net_amt',None) is None and float(self.request.GET.get('net_amt',None)) <= 0.0:        
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit Should not be less than Zero!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # print(not self.request.GET.get('net_amt',None) is None,"self.request.GET.get('net_amt',None) is None")    
            if not self.request.GET.get('net_amt',None) is None and request.GET.get('net_amt',None) != 0.0:
                try:  
                    given_net = float(self.request.GET.get('net_amt',None)) 
                    # print(given_net,"given_net")

                    balance = total_amount - other_disc
                    new_cart_ids = self.filter_queryset(self.get_queryset()).filter(itemcodeid__item_div__in=[1,3],itemcodeid__item_type='SINGLE').exclude(type__in=('Top Up','Sales'),is_foc=True)
                    for ct in new_cart_ids:
                        if ct.auto == True:
                            old_nettrascamt = ct.trans_amt
                            oldpercent = (old_nettrascamt / balance) * 100
                            new_nettrasamt = oldpercent * (given_net / 100)
                            cal_percent = 100 - ( (new_nettrasamt / old_nettrascamt) * 100 )
                            add_disc = (old_nettrascamt / 100) * cal_percent
                            discountprice = ((float(ct.price) - float(ct.discount_amt)) / 100) * cal_percent
                            ItemCart.objects.filter(id=ct.id).update(additional_discount=0.0,additional_discountamt=add_disc,
                            discount_price=discountprice,deposit=new_nettrasamt,trans_amt=new_nettrasamt)

                            posdisc_n = PosDisc(sa_transacno=None,dt_itemno=ct.itemcodeid.item_code+"0000",
                            disc_amt=add_disc,disc_percent=0.0,dt_lineno=ct.lineno,remark=reason,
                            site_code=ct.sitecodeid.itemsite_code,dt_status="New",dt_auto=0,
                            line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=None,
                            istransdisc=True)
                            posdisc_n.save()
                            ct.pos_disc.add(posdisc_n.id)  

                    result = {'status': status.HTTP_200_OK,"message":"Addtional Discount and Net Amount Updated Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)
                except Exception as e:
                    invalid_message = str(e)
                    return general_error_response(invalid_message)
            
                
            # print(request.data,"request.data")
            if request.data['additional_discount'] != None:
                if 'additional_discount' in request.data and (float(request.data['additional_discount']) > 0.0):
                    # add_discamt = subtotal * (float(request.data['additional_discount'])/100)
                    per_cartids = self.filter_queryset(self.get_queryset()).filter(itemcodeid__item_div__in=[1,3],itemcodeid__item_type='SINGLE').exclude(type__in=('Top Up','Sales'),is_foc=True)

                    for cp in per_cartids:
                        if cp.auto == True:
                            pvalue = cp.trans_amt * (float(request.data['additional_discount']) / 100)
                            div_pvalue = pvalue / cp.quantity
                            cp.additional_discountamt = pvalue
                            discprice = cp.discount_price  * cp.quantity
                            cp.discount_price =  cp.discount_price - div_pvalue
                            cp.deposit = discprice - pvalue
                            cp.trans_amt = discprice - pvalue
                            # print(cp.discount_price,cp.deposit,cp.trans_amt,"kk")
                            if cp.discount_price <= 0.0 or cp.deposit <= 0.0 or cp.trans_amt <= 0.0:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Line Deposit should not be negative/Zero",'error': False}
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
                            cp.save()

                            posdisc = PosDisc(sa_transacno=None,dt_itemno=cp.itemcodeid.item_code+"0000",
                            disc_amt=pvalue,disc_percent=0.0,dt_lineno=cp.lineno,remark=reason,
                            site_code=cp.sitecodeid.itemsite_code,dt_status="New",dt_auto=0,
                            line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=None,
                            istransdisc=True)
                            posdisc.save()
                            cp.pos_disc.add(posdisc.id)  
                    
                    result = {'status': status.HTTP_200_OK,"message":"Addtional Discount Updated Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)    
                else:
                    # print(request.data['additional_discountamt'],"request.data['additional_discountamt']")
                    if request.data['additional_discountamt'] != None:
                        if 'additional_discountamt' in request.data and (float(request.data['additional_discountamt']) > 0.0):
                            amt_cartids = self.filter_queryset(self.get_queryset()).filter(itemcodeid__item_div__in=[1,3],itemcodeid__item_type='SINGLE').exclude(type__in=('Top Up','Sales'),is_foc=True)

                            percent = (float(request.data['additional_discountamt']) * 100) / float(totaltrans_amt)
                            for ca in amt_cartids:
                                if ca.auto == True:
                                
                                    amt = ca.trans_amt * (percent / 100)
                                    div_amt = amt / ca.quantity
                                    ca.additional_discountamt = amt
                                    disc_price = ca.discount_price  * ca.quantity
                                    ca.discount_price =  ca.discount_price - div_amt
                                    ca.deposit = disc_price - amt
                                    ca.trans_amt = disc_price - amt
                                    # print(ca.discount_price,ca.deposit,ca.trans_amt,"kk")

                                    if ca.discount_price <= 0.0 or ca.deposit <= 0.0 or ca.trans_amt <= 0.0:
                                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Line Deposit should not be negative/Zero",'error': False}
                                        return Response(result, status=status.HTTP_400_BAD_REQUEST)
                    
                                    ca.save()

                                    posdisc_a = PosDisc(sa_transacno=None,dt_itemno=ca.itemcodeid.item_code+"0000",
                                    disc_amt=amt,disc_percent=0.0,dt_lineno=ca.lineno,remark=reason,
                                    site_code=ca.sitecodeid.itemsite_code,dt_status="New",dt_auto=0,
                                    line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=None,
                                    istransdisc=True)
                                    posdisc_a.save()
                                    ca.pos_disc.add(posdisc_a.id)  

                            result = {'status': status.HTTP_200_OK,"message":"Addtional Discount Updated Succesfully",'error': False}
                            return Response(result, status=status.HTTP_200_OK)
                    

            state = status.HTTP_400_BAD_REQUEST
            message = "Bad Request"
            error = True
            result = {'status': state,"message":message,'error': error}
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)          


    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication],name='qtyupdate')
    def qtyupdate(self, request, pk=None):
        try:
            itemcart = self.get_object(pk)
            if itemcart.type in ['Top Up','Sales']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
            #client told to change quantity
            # if itemcart.is_foc == True:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give qty.",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
            check = self.request.GET.get('check',None)
            if not check:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give check for Plus/Minus",'error': True}
                return Response(data=result, status=status.HTTP_200_OK)
            
            if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type == 'PACKAGE':
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid/Voucher/Package not allow Quantity!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
            serializer = itemCartSerializer(itemcart, data=request.data, partial=True)
            if serializer.is_valid():
                if self.request.GET.get('check',None) == "1":
                    qty = float(itemcart.quantity)+float(request.data['quantity'])
                    message = "Cart Qty Added Succesfully"
                elif self.request.GET.get('check',None) == "0":
                    qty = float(itemcart.quantity)-float(request.data['quantity'])
                    message = "Cart Qty Minus Succesfully"

                if qty <= 0:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Qty should not be less than Zero!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                total_price = float(itemcart.price) * int(qty)
                after_linedisc = (float(itemcart.price) - float(itemcart.discount_amt)) * int(qty)
                trans_amt = after_linedisc - float(itemcart.additional_discountamt)
                deposit = after_linedisc - float(itemcart.additional_discountamt)
                
                if itemcart.is_foc == True:
                    ItemCart.objects.filter(id=itemcart.id).update(quantity=qty,total_price=total_price)
                else:
                    ItemCart.objects.filter(id=itemcart.id).update(quantity=qty,
                    total_price=total_price,trans_amt=trans_amt,deposit=deposit)

                result = {'status': status.HTTP_200_OK,"message":message,'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      

    def partial_update(self, request, pk=None):
        try:
            itemcart = self.get_object(pk)
            if itemcart.type in ['Top Up','Sales']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if itemcart.is_foc == True:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give edit.",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
            serializer = itemCartSerializer(itemcart, data=request.data, partial=True)
            message = "Updated Succesfully"
            if serializer.is_valid():
                if itemcart.auto == True:
                    serializer.save(auto=False)
                    message = "Unselected Succesfully"
                elif itemcart.auto == False:
                    serializer.save(auto=True)  
                    message = "Selected Succesfully"
    
                state = status.HTTP_200_OK
                error = False
                result = {'status': state,"message":message,'error': error}
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_400_BAD_REQUEST
            message = serializer.errors
            error = True
            result = {'status': state,"message":message,'error': error}
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        
        

    def destroy(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            data = None
            state = status.HTTP_204_NO_CONTENT
            try:
                instance = self.get_object(pk)
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                state = status.HTTP_200_OK
                result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
                return Response(result,status=status.HTTP_200_OK)    
            except Http404:
                pass

            message = "No Content"
            error = True
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_204_NO_CONTENT) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        

    def perform_destroy(self, instance):
        instance.isactive = False
        TreatmentAccount.objects.filter(itemcart=instance).update(itemcart=None)
        PosDaud.objects.filter(itemcart=instance).update(itemcart=None)
        TmpItemHelper.objects.filter(itemcart=instance).update(itemcart=None)
        PosPackagedeposit.objects.filter(itemcart=instance).delete()
        instance.delete() 

class VoucherRecordViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = VoucherRecord.objects.filter(isvalid=True).order_by('-id')
    serializer_class = VoucherRecordSerializer

    def list(self, request):
        try:
            appt_ids = Appointment.objects.filter(pk=request.GET.get('Appointment_id',None),appt_isactive=True)
            if not appt_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            app_obj = Appointment.objects.filter(pk=request.GET.get('Appointment_id',None))[0]
            queryset = VoucherRecord.objects.filter(isvalid=True,voucher_no=request.GET.get('voucher_no',None),
            cust_codeid=app_obj.cust_noid).order_by('-pk')
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
                lst = []
                for d in data:
                    dict_d = dict(d)
                    if dict_d['percent']:
                        dict_d['percent'] = str("{:.2f}".format(float(dict_d['percent'])))+" "+"%"
                    else:
                        dict_d['percent'] = "0.0"
                    if dict_d['value']:
                        dict_d['value'] = "{:.2f}".format(float(dict_d['value']))
                    else:
                        dict_d['value'] = "0.0"

                    lst.append(dict_d)

                result = {'status': state,"message":message,'error': error, 'data': lst}
                return Response(data=result, status=status.HTTP_200_OK)              
            else:
                state = status.HTTP_204_NO_CONTENT
                message = "Invaild Voucher Number"
                error = True
                result = {'status': state,"message":message,'error': error}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)                       
        
# def receipt_calculation(request, daud):
#     # cart_ids = ItemCart.objects.filter(isactive=True,Appointment=app_obj,is_payment=True)
#     gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
#     subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0; 
#     trans_amt=0.0 ;deposit_amt =0.0; tax_amt = 0.0; billable_amount=0.0;total_balance = 0.0;total_qty = 0
#     for ct in daud:
#         c = ct.itemcart
#         # total = "{:.2f}".format(float(c.price) * int(c.quantity))
#         subtotal += float(c.total_price)
#         discount_amt += float(c.discount_amt)
#         additional_discountamt += float(c.additional_discountamt)
#         trans_amt += float(c.trans_amt)
#         deposit_amt += float(c.deposit)
#         balance = float(c.trans_amt) - float(c.deposit)
#         total_balance += float(balance)
#         total_qty += int(c.quantity)

#     # disc_percent = 0.0
#     # if discount_amt > 0.0:
#     #     disc_percent = (float(discount_amt) * 100) / float(net_deposit) 
#     #     after_line_disc = net_deposit
#     # else:
#     #     after_line_disc = net_deposit

#     # add_percent = 0.0
#     # if additional_discountamt > 0.0:
#     #     # print(additional_discountamt,"additional_discountamt")
#     #     add_percent = (float(additional_discountamt) * 100) / float(net_deposit) 
#     #     after_add_disc = after_line_disc 
#     # else:
#     #     after_add_disc = after_line_disc   

#     if gst.is_exclusive == True:
#         tax_amt = deposit_amt * (gst.item_value / 100)
#         billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
#     else:
#         billable_amount = "{:.2f}".format(deposit_amt)

#     sub_total = "{:.2f}".format(float(subtotal))
#     round_val = float(round_calc(billable_amount)) # round()
#     billable_amount = float(billable_amount) + round_val 
#     sa_Round = round_val
#     discount = discount_amt + additional_discountamt
#     itemvalue = "{:.2f}".format(float(gst.item_value))

#     value = {'subtotal':sub_total,'discount': "{:.2f}".format(float(discount)),'trans_amt': "{:.2f}".format(float(trans_amt)),
#     'deposit_amt': "{:.2f}".format(float(deposit_amt)),'tax_amt':"{:.2f}".format(float(tax_amt)),
#     'tax_lable': "Tax Amount"+"("+str(itemvalue)+" "+"%"+")",'sa_Round': "{:.2f}".format(float(sa_Round)),
#     'billable_amount': "{:.2f}".format(float(billable_amount)),'balance': "{:.2f}".format(float(balance)),
#     'total_balance': "{:.2f}".format(float(total_balance)),'total_qty':total_qty}
#     return value


class ReceiptPdfGeneration(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request, format=None):
        try:
            if request.GET.get('sa_transacno',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sa_transacno!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite 
            sa_transacno = request.GET.get('sa_transacno',None)
            hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
            ItemSite_Codeid__pk=site.pk).order_by("pk")
            if not hdr:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sa Transacno Does not exist in Poshaud!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            ip_link = GeneratePDF(self, request, sa_transacno)
            if ip_link:
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': ip_link}
                return Response(data=result, status=status.HTTP_200_OK) 
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Data",'error': True}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)               


class ReceiptPdfSend(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def post(self, request, format='json'):
        try:
            if request.GET.get('sa_transacno',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sa_transacno!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite  
            sa_transacno = request.GET.get('sa_transacno',None)
            hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
            ItemSite_Codeid__pk=site.pk).order_by("pk")
            if not hdr:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sa Transacno Does not exist in Poshaud!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            template_path = 'customer_receipt.html'
            gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
            hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
            ItemSite_Codeid__pk=site.pk).order_by("id")[:1]
            daud = PosDaud.objects.filter(sa_transacno=sa_transacno,
            ItemSite_Codeid__pk=site.pk)
            taud = PosTaud.objects.filter(sa_transacno=sa_transacno,
            ItemSIte_Codeid__pk=site.pk)
            if not taud:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"sa_transacno Does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            Pos_daud = PosDaud.objects.filter(sa_transacno=sa_transacno,
            ItemSite_Codeid__pk=site.pk).first()

            tot_qty = 0;tot_trans = 0 ; tot_depo = 0; tot_bal = 0;balance = 0
            dtl_serializer = PosdaudSerializer(daud, many=True)
            dtl_data = dtl_serializer.data
            for dat in dtl_data:
                d = dict(dat)
                d_obj = PosDaud.objects.filter(pk=d['id'],ItemSite_Codeid__pk=site.pk).first()
                package_desc = []; packages = ""
                if d['record_detail_type'] == "PACKAGE":
                    package_dtl = PackageDtl.objects.filter(package_code=d['dt_combocode'],isactive=True)
                    for i in package_dtl:
                        desc = i.description
                        package_desc.append(desc)
                    packages = tuple(package_desc)

                if d['dt_status'] == 'SA' and d['record_detail_type'] == "TD":
                    d['dt_transacamt'] = ""
                    d['dt_deposit'] = ""
                    balance = ""
                    d['balance'] = ""
                else:    
                    d['dt_transacamt'] = "{:.2f}".format(float(d_obj.dt_amt))
                    d['dt_deposit'] = "{:.2f}".format(float(d['dt_deposit']))
                    balance = float(d_obj.dt_amt) - float(d['dt_deposit'])
                    d['balance'] = "{:.2f}".format(float(balance))
                    tot_trans += float(d_obj.dt_amt)
                    tot_depo += float(d['dt_deposit'])
                    tot_bal += float(balance)
                    
                tot_qty += int(d['dt_qty'])

                # app_obj = Appointment.objects.filter(pk=d['Appointment']).first()
                # sales = "";service = ""
                # if 'itemcart' in d:
                #     cartobj = ItemCart.objects.filter(pk=d['itemcart']).first()
                #     if cartobj:
                #         if cartobj.sales_staff.all():
                #             for i in cartobj.sales_staff.all():
                #                 if sales == "":
                #                     sales = sales + i.emp_name
                #                 elif not sales == "":
                #                     sales = sales +","+ i.emp_name
                #         if cartobj.service_staff.all(): 
                #             for s in cartobj.service_staff.all():
                #                 if service == "":
                #                     service = service + s.emp_name
                #                 elif not service == "":
                #                     service = service +","+ s.emp_name 
            
            
                # daud_obj = PosDaud.objects.filter(pk=d['id']).update(staffs=sales +" "+"/"+" "+ service)

                # if d['record_detail_type'] == "TD":
                #     d['staffs'] = "/"+ service
                # else:
                #     d['staffs'] = sales +" "+"/"+" "+ service

            # value = receipt_calculation(request, daud)
        
            # sub_data = {'subtotal': "{:.2f}".format(float(value['subtotal'])),'total_disc':"{:.2f}".format(float(value['discount'])),
            # 'trans_amt':"{:.2f}".format(float(value['trans_amt'])),'deposit_amt':"{:.2f}".format(float(value['deposit_amt'])),
            # 'tax_amt':"{:.2f}".format(float(value['tax_amt'])),'tax_lable': value['tax_lable'],
            # 'billing_amount':"{:.2f}".format(float(value['billable_amount'])),'balance':"{:.2f}".format(float(value['balance'])),
            # 'total_balance':"{:.2f}".format(float(value['total_balance'])),'total_qty': value['total_qty']}
            
            if gst.is_exclusive == True:
                tax_amt = tot_depo * (gst.item_value / 100)
                billable_amount = "{:.2f}".format(tot_depo + tax_amt)
            else:
                billable_amount = "{:.2f}".format(tot_depo)

            sub_data = {'total_qty':str(tot_qty),'trans_amt':str("{:.2f}".format((tot_trans))),
            'deposit_amt':str("{:.2f}".format((tot_depo))),'total_balance':str("{:.2f}".format((tot_bal))),
            'subtotal':str("{:.2f}".format((tot_depo))),'billing_amount':"{:.2f}".format(float(billable_amount))}

            split = str(hdr[0].sa_date).split(" ")
            # date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime('%d.%m.%Y')
            esplit = str(hdr[0].sa_time).split(" ")
            Time = str(esplit[1]).split(":")

            time = Time[0]+":"+Time[1]
            day = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime('%a')
            title = Title.objects.filter(product_license=site.itemsite_code).first()
            path = None
            if title and title.logo_pic:
                path = BASE_DIR + title.logo_pic.url
            
            
            date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d-%b-%Y")

            taud_f = PosTaud.objects.filter(sa_transacno=sa_transacno,
            ItemSIte_Codeid__pk=site.pk).first()

            data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
            'address': title.trans_h2 if title and title.trans_h2 else '', 
            'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
            'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
            'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
            'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
            'hdr': hdr[0], 'daud':daud,'taud_f':taud_f,'postaud':taud,'day':day,'fmspw':fmspw,
            'date':date,'time':time,'percent':int(gst.item_value),'path':path if path else '','title':title if title else None,
            'packages': str(packages)}
            data.update(sub_data)

            html = render_to_string(template_path, data)

            result = BytesIO()
            # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),result)

            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")),result)
            subject = 'Customer Receipt Pdf'
            if Pos_daud.itemcart.cust_noid.cust_email is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer email!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            to = Pos_daud.itemcart.cust_noid.cust_email
            cust_name = Pos_daud.itemcart.cust_noid.cust_name

            template = get_template('customer_receipt.html')
            html = template.render(data)
            display = Display(visible=0, size=(800, 600))
            display.start()
            options = {
                'margin-top': '.25in',
                'margin-right': '.25in',
                'margin-bottom': '.25in',
                'margin-left': '.25in',
                'encoding': "UTF-8",
                'no-outline': None,
                
            }
            p=pdfkit.from_string(html,False,options=options)
            
            html_message = '''Dear {0},\nKindly Find your receipt bill no {1}.\nThank You,'''.format(cust_name,sa_transacno)
            plain_message = strip_tags(html)
            # email = EmailMessage(subject , html_message, EMAIL_HOST_USER, [to])
            # email.attach_file('Customer Receipt Report.pdf',result.getvalue(),'application/pdf')
            # email.send()
            system_setup = Systemsetup.objects.filter(title='Email Setting',value_name='Email CC To').first()
            if system_setup: 
                cc = [system_setup.value_data] if system_setup.value_data else []
            else:
                cc = []  

            msg = EmailMultiAlternatives(subject, html_message, EMAIL_HOST_USER, [to], cc)
            # msg.attach_alternative('Customer Receipt Report.pdf',result.getvalue(),'application/pdf')
            filename  = "customer_receipt_" + str(str(hdr[0].sa_transacno_ref)) + ".pdf"

            msg.attach(filename,p,'application/pdf')
            msg.send()
            response = HttpResponse(p,content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="Customer Receipt Report.pdf"'
            result = {'status': status.HTTP_200_OK,"message":"Email sent succesfully",'error': False}
            display.stop()
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

class PaymentRemarksAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = PaymentRemarks.objects.filter(isactive=True).order_by('id')
    serializer_class = PaymentRemarksSerializer

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      


class HolditemSetupAPIView(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = HolditemSetup.objects.filter().order_by('id')
    serializer_class = HolditemSetupSerializer

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      


class PosPackagedepositViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = PosPackagedeposit.objects.filter().order_by('deposit_lineno')
    serializer_class = PosPackagedepositSerializer

    def get_queryset(self):
        if self.request.GET.get('cartid',None):
            if not self.request.GET.get('cartid',None) is None and str(self.request.GET.get('cartid',None)) != "null":
                cartid = self.request.GET.get('cartid',None)
                queryset = PosPackagedeposit.objects.filter(itemcart__pk=cartid).order_by('deposit_lineno')
            else:
                queryset = None    
        return queryset         
                 

    def list(self, request):
        try:
            if not request.GET.get('cartid',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Cart Record ID",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = [];auto_deposit = 0 ; deposit = 0; net_deposit = 0
                for d in serializer.data:
                    dict_t = dict(d)
                    auto_deposit += dict_t['deposit_amt']
                    deposit += dict_t['deposit_amt']

                    net_deposit += dict_t['net_amt']
                    dict_t['deposit_amt'] = "{:.2f}".format(float(dict_t['deposit_amt']))
                    dict_t['net_amt'] = "{:.2f}".format(float(dict_t['net_amt']))
                    lst.append(dict_t)
                
                if request.GET.get('autoamt', None):
                    if not self.request.GET.get('autoamt',None) is None and request.GET.get('autoamt',None) != 0.0:
                        auto_ids = queryset.filter(auto=True)
                        auto_net = sum([ca.price * ca.qty for ca in auto_ids if ca.price and ca.qty])

                        # print(auto_net,'auto_net')

                        if request.GET.get('clear', None) == "0":
                            raise Exception('Deposit cannot be cleared, while applying Auto Deposit') 

                        if request.GET.get('clear', None) == "1":
                            raise Exception('Auto Deposit Cannot be applied for Full Payment') 

                        if float(request.GET.get('autoamt', None)) > net_deposit:
                            raise Exception('Deposit amount cannot be more than outstanding amount') 

                        if float(request.GET.get('autoamt', None)) > auto_net:
                            raise Exception('Deposit amount cannot be more than outstanding amount') 

                        autoamt = float(self.request.GET.get('autoamt',None))
                        # print(autoamt,"autoamt")

                        percent = (autoamt / auto_net) * 100 
                        auto_deposit = 0 ; deposit = 0;
                        for l in lst:
                            if l['auto'] == True:
                                updateval = (float(l['net_amt']) * float(percent)) / 100
                                # print(updateval,"updateval")
                                l['deposit_amt'] = "{:.2f}".format(float(updateval))
                                auto_deposit += float(l['deposit_amt'])
                                deposit += float(l['deposit_amt'])
                            else:
                                if l['auto'] == False:
                                    l['deposit_amt'] = "0.00"  
                    else:
                        raise Exception('Please give correct float value for Auto Deposit') 


                if request.GET.get('clear', None): 
                    if request.GET.get('clear', None) == "0":
                        for l in lst:
                            l['deposit_amt'] = "0.00"
                            deposit = 0
                    

                result = {'status': status.HTTP_200_OK,"message":"Listed Successfully",'error': False, 
                'data':  lst,'auto_deposit': "{:.2f}".format(float(auto_deposit)),'deposit':"{:.2f}".format(float(deposit)),
                'net_deposit': "{:.2f}".format(float(net_deposit))}
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def get_object(self, pk):
        try:
            return PosPackagedeposit.objects.get(pk=pk)
        except PosPackagedeposit.DoesNotExist:
            raise Http404        

    def partial_update(self, request, pk=None):
        try:
            pos = self.get_object(pk)
            serializer = itemCartSerializer(pos, data=request.data, partial=True)
            if serializer.is_valid():
                if pos.auto == True:
                    serializer.save(auto=False)
                    message = "Unselected Succesfully"
                elif pos.auto == False:
                    serializer.save(auto=True)  
                    message = "Selected Succesfully"
    
                result = {'status': status.HTTP_200_OK,"message":message,'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def confirm(self, request):  
        try:
            if request.data:
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                cart_date = timezone.now().date()
                if not request.GET.get('cartid',None):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Cart Record ID",'error': True}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                cartobj = ItemCart.objects.filter(pk=request.GET.get('cartid',None),cart_date=cart_date,
                cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code).order_by('lineno')    
                if not cartobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID Does not exist",'error': True}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                pos_deposit = 0
                for idx, req in enumerate(request.data, start=1): 
                    serializer = PosPackagedepositpostSerializer(data=req)
                    if serializer.is_valid():
                        pos = PosPackagedeposit.objects.filter(id=req['id']).first()
                        if not pos:
                            raise Exception('PosPackagedeposit id Does not exist') 

                        pos_code = str(pos.code)
                        itm_code = pos_code[:-4]
                        itmstock = Stock.objects.filter(item_code=itm_code,item_isactive=True).first()
                        if int(itmstock.item_div) != 1:
                            if int(req['hold_qty']) != 0.0:
                                msg = "{0} This Product can't hold item".format(str(pos.description))
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        if int(itmstock.item_div) == 1: 
                            if int(req['hold_qty']) > int(pos.qty):
                                print(int(req['hold_qty']) > int(pos.qty),"ll")
                                qtymsg = "{0} This Product hold qty should not be greater than {1}".format(str(pos.description),str(pos.qty))
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message": qtymsg,'error': True}
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                            
                            if int(req['hold_qty']) > 0:
                                pos.hold_qty=req['hold_qty'] 
     
                        pos.deposit_amt=req['deposit_amt'] 
                        pos.save()
                        if pos.auto == True:
                            pos_deposit += float(pos.deposit_amt)

                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                objcart = cartobj.first()
                objcart.deposit =  pos_deposit
                objcart.save()         
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)               
            else:
                raise Exception('Request body data does not exist') 

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     






