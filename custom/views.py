from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import (EmpLevelSerializer, RoomSerializer, ComboServicesSerializer, CategorySerializer, TypeSerializer,
itemCartSerializer,VoucherRecordSerializer,EmployeeDropSerializer, itemCartListSerializer,PaymentRemarksSerializer,
HolditemSetupSerializer,PosPackagedepositSerializer,PosPackagedepositpostSerializer,ExchangeProductSerializer,
CartItemStatusSerializer,CartDiscountSerializer,CartStaffsSerializer,CartServiceCourseSerializer,
SmtpSettingsSerializer,CourseTmpSerializer)
from .models import (EmpLevel, Room, Combo_Services, ItemCart,VoucherRecord,RoundPoint, RoundSales,
PaymentRemarks, HolditemSetup,PosPackagedeposit,SmtpSettings,MultiPricePolicy)
from cl_table.models import(Treatment, Employee, Fmspw, Stock, ItemClass, ItemRange, Appointment,Customer,Treatment_Master,
GstSetting,PosTaud,PosDaud,PosHaud,ControlNo,EmpSitelist,ItemStatus, TmpItemHelper, FocReason, PosDisc,
TreatmentAccount, PosDaud, ItemDept, DepositAccount, PrepaidAccount, ItemDiv, Systemsetup, Title,
PackageHdr,PackageDtl,Paytable,Multistaff,ItemBatch,Stktrn,ItemUomprice,Holditemdetail,CreditNote,
CustomerClass,ItemClass,Tmpmultistaff,Tmptreatment,ExchangeDtl)
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
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives, get_connection
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
from custom.services import GeneratePDF, round_calc, receipt_calculation, customeraccount
from cl_app.permissions import authenticated_only
from django.core.exceptions import PermissionDenied
from rest_framework import exceptions
from cl_app.utils import general_error_response
from Cl_beautesoft.settings import BASE_DIR
from django.db.models import Q
import string
import re
from dateutil.relativedelta import relativedelta
from rest_framework.decorators import api_view

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
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Content 17",'error': False, 
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
    else:
        result = {'status': state, "message": message, 'error': error, 'data': data}
     
    return result



class CategoryViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
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
        serializer_class = CategorySerializer
        queryset = self.filter_queryset(self.get_queryset())

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 1",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   
    def create(self, request):
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

    def get_object(self, pk):
        try:
            return ItemClass.objects.get(pk=pk,itm_isactive=True)
        except ItemClass.DoesNotExist:
            raise Http404

   
    def retrieve(self, request, pk=None):
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
                
    
    def update(self, request, pk=None):
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
    

    def destroy(self, request, pk=None):
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

        message = "No Content 2"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)  
    

    def perform_destroy(self, instance):
        instance.itm_desc = False
        treat = Stock.objects.filter(Item_Classid=instance).update(Item_Classid=None)
        instance.save()  



class TypeViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
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
            result = {'status': status.HTTP_200_OK,"message":"No Content 3",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   

    def create(self, request):
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

   
    def get_object(self, pk):
        try:
            return ItemRange.objects.get(pk=pk)
        except ItemRange.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
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
        

    def update(self, request, pk=None):
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

    
    def destroy(self, request, pk=None):
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

        message = "No Content 4"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)    

    def perform_destroy(self, instance):
        treat = Stock.objects.filter(Item_Rangeid=instance).update(Item_Rangeid=None)
        instance.save()  


class JobTitleViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
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
        serializer_class = EmpLevelSerializer
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 5",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   

    def create(self, request):
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

   
    def get_object(self, pk):
        try:
            return EmpLevel.objects.get(pk=pk,level_isactive=True)
        except EmpLevel.DoesNotExist:
            raise Http404

   
    def retrieve(self, request, pk=None):
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
                   
    def update(self, request, pk=None):
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
    
    
    def destroy(self, request, pk=None):
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

        message = "No Content 6"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)  

    def perform_destroy(self, instance):
        instance.level_isactive = False
        emp = Employee.objects.filter(EMP_TYPEid=instance).update(EMP_TYPEid=None)
        instance.save()                


class RoomViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Room.objects.filter(isactive=True).order_by('-id')
    serializer_class = RoomSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)

        site = fmspw[0].loginsite
        if not site:
            result = {'status': state,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)
       
        queryset = Room.objects.filter(isactive=True).order_by('-id')
        # queryset = Room.objects.filter(isactive=True,Site_Codeid=site).order_by('-id')
        # if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
        #     queryset = Room.objects.filter(isactive=True).order_by('-id')
        # elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [27,31]:
        #     queryset = Room.objects.filter(isactive=True,Site_Codeid=site).order_by('-id')

        
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        # appt = self.request.GET.get('Appointment_id',None)
        # app_obj = Appointment.objects.filter(pk=self.request.GET.get('Appointment_id',None)).first()
        # if not app_obj:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
        #     raise serializers.ValidationError(result)
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
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 7",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   

    def create(self, request):
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

    def get_object(self, pk):
        try:
            return Room.objects.get(pk=pk,isactive=True)
        except Room.DoesNotExist:
            raise Http404

   
    def retrieve(self, request, pk=None):
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
                
    
    def update(self, request, pk=None):
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
    

    def destroy(self, request, pk=None):
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

        message = "No Content 8"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)  
    

    def perform_destroy(self, instance):
        instance.isactive = False
        # treat = Stock.objects.filter(category=instance).update(category=None)
        instance.save()  

class ComboServicesViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Combo_Services.objects.filter(Isactive=True).order_by('-id')
    serializer_class = ComboServicesSerializer

    def get_queryset(self):
        user = self.request.user
        fmspw = Fmspw.objects.filter(user=user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].Emp_Codeid.Site_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = Combo_Services.objects.filter(Isactive=True).order_by('-id')
       
        q = self.request.GET.get('search',None)

        if q is not None:
            queryset = Combo_Services.objects.filter(Isactive=True,services__item_desc__icontains=q).order_by('-id')
        
        return queryset

    def list(self, request):
        serializer_class = ComboServicesSerializer
        queryset = self.filter_queryset(self.get_queryset())
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)         
    
    def create(self, request):
        state = status.HTTP_400_BAD_REQUEST
        user = request.user
        fmspw = Fmspw.objects.filter(user=user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': state,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': state,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)

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

   
    def get_object(self, pk):
        try:
            return Combo_Services.objects.get(pk=pk,Isactive=True)
        except Combo_Services.DoesNotExist:
            raise Http404

    
    def retrieve(self, request, pk=None):
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
    
    def update(self, request, pk=None):
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

    
    def destroy(self, request, pk=None):
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

        message = "No Content 9"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)    

    def perform_destroy(self, instance):
        instance.Isactive = False
        instance.save() 

class EmployeeCartAPI(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
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
            # if self.request.GET.get('sales_staff',None) == "1":
            #     queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,show_in_sales=True).order_by('display_name')
            
            # elif self.request.GET.get('sales_staff',None) == "0":
            #     queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,show_in_trmt=True).order_by('display_name')

            # elif self.request.GET.get('sales_staff',None) == "2":
            #     queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True).filter(
            #         Q(show_in_trmt=True) | Q(show_in_sales=True)).order_by('display_name')
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
    return True                   
    sacontrol_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
    if not sacontrol_obj:
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
        raise serializers.ValidationError(result)
            
    # print(site.pk,"site")
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
        # sa_id = int(slst[0]) + 1
        sa_id = int(slst[0][-6:]) + 1
        
        sacontrol_obj.control_no = str(sa_id)
        sacontrol_obj.save() 
    return True                   

class itemCartViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ItemCart.objects.filter(isactive=True).order_by('-id')
    serializer_class = itemCartSerializer

    @action(detail=False, methods=['get'], name='Check')
    def Check(self, request):
        if str(self.request.GET.get('cust_noid',None)) == "undefined":
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select customer!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST)         

        global type_ex
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        cart_date = timezone.now().date()

        empl = fmspw[0].Emp_Codeid
       
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

        queryset = ItemCart.objects.filter(cust_noid=cust_obj,cart_date=cart_date,
        cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')    
        lst = list(set([e.cart_id for e in queryset if e.cart_id]))
        if len(lst) > 1:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Customer will have more than one Cart ID in Inprogress status,Please check and delete Unwanted Cart ID!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
        if not control_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
            raise serializers.ValidationError(result)
        # print(site,"site")
        cartre = ItemCart.objects.filter(sitecode=site).order_by('cart_id')
        final = list(set([r.cart_id for r in cartre]))
        code_site = site.itemsite_code
        print(code_site,"code_site")
        prefix = control_obj.control_prefix

        clst = []
        if final != []:
            for f in final:
                newstr = f.replace(prefix,"")
                new_str = newstr.replace(code_site, "")
                clst.append(new_str)
                clst.sort(reverse=True)

            cart_id = int(clst[0][-6:]) + 1
            #cart_id = int(control_obj.control_no) + 1  
            print(cart_id,"clst")
           
            control_obj.control_no = str(cart_id)
            control_obj.save()

        savalue = sa_transacno_update(self, site, fmspw) 
        if queryset:
            # serializer = self.get_serializer(queryset, many=True)
            #'data':  serializer.data
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': {'cart_id':lst[0]},'cart_id':lst[0]}
        else:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Listed Succesfully",'error': False, 
            'data': [],'cart_id': ""}
        return Response(data=result, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        global type_ex
        request = self.request
        # cart_date = timezone.now().date()
        cart_date = request.GET.get('cart_date',None)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        # print(self.request.user,"here")
        site = fmspw[0].loginsite
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
        cart_id = request.GET.get('cart_id',None)

        if fmspw[0].flgsales == True:
            queryset = ItemCart.objects.filter(isactive=True,sitecode=site).order_by('id')
            # print(cart_id,"id")
            # print(cart_date,"date")
            # print(cust_obj,"cust_obj")
            queryset = queryset.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
            cart_status="Inprogress",isactive=True,is_payment=False).exclude(type__in=type_ex).order_by('lineno')  
            # if cust_obj:
            #    print(self.request.user,"here")
        else:
            queryset = ItemCart.objects.none()
        return queryset

    def list(self, request):
        global type_ex
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        empl = fmspw[0].Emp_Codeid
        cart_date = timezone.now().date()

        if self.request.GET.get('cart_date',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give cart_date",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
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
        # print(site,"site")
        cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
        cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)  
        # print(cartc_ids,"cartc_ids")
        if cartc_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 10",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)

        exchange = False
        if queryset.filter(type='Exchange'):
            exchange = True

        # gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False; subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0;
        trans_amt=0.0 ;deposit_amt =0.0; billable_amount=0.0;balance=0.0 
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            lst = []
            for d in data:
                dict_v = dict(d)
                cartobj = ItemCart.objects.filter(id=dict_v['id'],isactive=True,sitecode=site.itemsite_code).exclude(type__in=type_ex).first()  
                #stockobj = Stock.objects.filter(item_code=cartobj.itemcode,item_isactive=True).first()
                stockobj = Stock.objects.filter(item_code=cartobj.itemcode).first()
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
                # else:
                #    dict_v['quantity'] = 0.0
                
                if cartobj.type == 'Deposit' and stockobj.item_div == '3':
                    tmp_ids = TmpItemHelper.objects.filter(itemcart=cartobj,site_code=site.itemsite_code)
                    
                    # for emp in tmp_ids:
                    #    appt = Appointment.objects.filter(cust_noid=cartobj.cust_noid,appt_date=date.today(),
                    #    ItemSite_Codeid=fmspw[0].loginsite,emp_no=emp.helper_code) 
                    #    if not appt:
                    #        tmpids = TmpItemHelper.objects.filter(itemcart=cartobj,helper_code=emp.helper_code,
                    #        site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                    #        if tmpids:
                    #            emp.delete()

                    #    if emp.appt_fr_time and emp.appt_to_time:         
                    #        appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
                    #        itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
                    #        if appt_ids:
                    #            emp.delete()

                    for existing in cartobj.helper_ids.all():
                        cartobj.helper_ids.remove(existing) 

                    for exist in cartobj.service_staff.all():
                        cartobj.service_staff.remove(exist)     

                    for t in TmpItemHelper.objects.filter(itemcart=cartobj,site_code=site.itemsite_code):
                        helper_obj = Employee.objects.filter(emp_isactive=True,emp_code=t.helper_code).first()
                        cartobj.helper_ids.add(t) 
                        cartobj.service_staff.add(helper_obj.pk) 

                if 1==1:
                    if cartobj.type == 'Sales' and stockobj.item_div == '3':
                        trtmp_ids = TmpItemHelper.objects.filter(treatment=cartobj.treatment,site_code=site.itemsite_code)
                        for existing in cartobj.helper_ids.all():
                            cartobj.helper_ids.remove(existing) 

                        for exis in cartobj.treatment.helper_ids.all():
                            cartobj.treatment.helper_ids.remove(exis) 
    
                        for exist in cartobj.service_staff.all():
                            cartobj.service_staff.remove(exist)     

                        for t in TmpItemHelper.objects.filter(treatment=cartobj.treatment,site_code=site.itemsite_code):
                            helper_obj = Employee.objects.filter(emp_isactive=True,pk=t.helper_id.pk).first()
                            cartobj.helper_ids.add(t) 
                            cartobj.treatment.helper_ids.add(t) 
                            cartobj.service_staff.add(helper_obj.pk) 

                if 1==1:
                    if cartobj.type in ['Deposit','Top Up','Exchange']:
                        tmpmul_ids = Tmpmultistaff.objects.filter(itemcart=cartobj)
                        for existings in cartobj.multistaff_ids.all():
                            cartobj.multistaff_ids.remove(existings) 

                        for exists in cartobj.sales_staff.all():
                            cartobj.sales_staff.remove(exists)     

                        for tm in Tmpmultistaff.objects.filter(itemcart=cartobj):
                            emp_obj = Employee.objects.filter(emp_isactive=True,
                            pk=tm.emp_id.pk).first()
                            cartobj.multistaff_ids.add(tm) 
                            cartobj.sales_staff.add(emp_obj.pk) 
       
                tot_disc = dict_v['discount_amt'] + dict_v['additional_discountamt']
                #stock_obj = Stock.objects.filter(pk=dict_v['itemcodeid'],item_isactive=True)[0]
                stock_obj = Stock.objects.filter(pk=dict_v['itemcodeid'])[0]
                total_disc = dict_v['discount_amt'] + dict_v['additional_discountamt']
                dict_v['price'] = "{:.2f}".format(float(dict_v['price']))
                dict_v['total_price'] = "{:.2f}".format(float(dict_v['total_price']))
                dict_v['discount_price'] = "{:.2f}".format(float(dict_v['discount_price']))
                dict_v['item_class'] = stock_obj.Item_Classid.itm_desc
                dict_v['sales_staff'] =   ','.join([v.emp_name for v in cartobj.sales_staff.all() if v])
                dict_v['service_staff'] = ','.join([v.emp_name for v in cartobj.service_staff.all() if v])
                # dict_v['tax'] = "{:.2f}".format(float(dict_v['tax']))
                #discount keyword for other disc + trasc discei
                dict_v['discount'] = "{:.2f}".format(float(tot_disc))
                # dict_v['discount_amt'] = "{:.2f}".format(float(dict_v['discount_amt']))
                dict_v['trans_amt'] = "{:.2f}".format(float(dict_v['trans_amt']))
                dict_v['deposit'] = "{:.2f}".format(float(dict_v['deposit']))
                # dict_v['additional_discount'] = "{:.2f}".format(float(dict_v['additional_discount']))
                # dict_v['additional_discountamt'] = "{:.2f}".format(float(dict_v['additional_discountamt']))
                dict_v['total_disc'] = "{:.2f}".format(float(total_disc))
                dict_v['treatment_name'] = dict_v['itemdesc']+" "+" "+"("+str(dict_v['quantity'])+")"
                dict_v['item_name'] = stock_obj.item_name
                dict_v['item_div'] = int(stockobj.item_div)

                if dict_v['type'] != "Exchange":
                    subtotal += float(dict_v['total_price'])
                    # discount_amt += float(dict_v['discount_amt']) * int(dict_v['quantity'])
                    if 1==1:
                        if cartobj.free_sessions:
                            val = int(dict_v['quantity']) - int(cartobj.free_sessions)
                            discount_amt += float(dict_v['discount_amt']) * val
                        else:
                            discount_amt += float(dict_v['discount_amt']) * int(dict_v['quantity'])

                    additional_discountamt += float(dict_v['additional_discountamt'])
                    # print(additional_discountamt,"additional_discountamt")
                    trans_amt += float(dict_v['trans_amt'])
                    deposit_amt += float(dict_v['deposit'])
                    # tax += float(dict_v['tax'])

                balance += float(dict_v['deposit'])
                # print(balance,"balance")
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


            # sub_total = "{:.2f}".format(float(subtotal))
            # billable_amount = "{:.2f}".format(deposit_amt + float(round_calc(deposit_amt))) # round()
            # total_disc = discount_amt + additional_discountamt
            # result = {'status': state,"message":message,'error': error, 'data':  lst,'subtotal':"{:.2f}".format(float(sub_total)),
            # 'discount': "{:.2f}".format(float(total_disc)),'trans_amt': "{:.2f}".format(float(trans_amt)),'deposit_amt':"{:.2f}".format(float(deposit_amt)),
            # 'billable_amount': "{:.2f}".format(fldoat(billable_amount))}
            # print(balance,"balance")
            sub_total = "{:.2f}".format(float(subtotal))
            # billable_amount = "{:.2f}".format(deposit_amt + float(round_calc(deposit_amt))) # round()
            billable_amount = "{:.2f}".format(balance + float(round_calc(balance))) # round()
            # print(billable_amount,"billable_amount")
            total_disc = discount_amt + additional_discountamt
            result = {'status': state,"message":message,'error': error, 'data':  lst,'subtotal':"{:.2f}".format(float(sub_total)),
            'discount': "{:.2f}".format(float(total_disc)),'trans_amt': "{:.2f}".format(float(trans_amt)),'deposit_amt':"{:.2f}".format(float(balance)),
            'billable_amount': "{:.2f}".format(float(billable_amount)),'balance':"{:.2f}".format(float(balance)),
            'exchange': exchange}
        else:
            serializer = self.get_serializer()
            result = {'status': state,"message":message,'error': error, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)

    def create(self, request):
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

            # stock_obj = Stock.objects.filter(pk=req['itemcodeid'],item_isactive=True).first()
            stock_obj = Stock.objects.filter(pk=req['itemcodeid']).first()
            if not stock_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
        
            cart_lst = [];subtotal = 0.0; discount=0.0; billable_amount=0.0;trans_amt=0.0;deposit_amt = 0.0
            recorddetail="Service"
            cart_id = request.GET.get('cart_id',None)
            if cart_id:
                cartchids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex)  
                if not cartchids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is not there for this cutomer,Give Without cart_id in parms!!",'error': True} 
                    raise serializers.ValidationError(result)

                check = "Old"
                # print(site,"site")
                #cust_noid=cust_obj,
                cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)  
                if cartc_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                    raise serializers.ValidationError(result)
            else:
                cartcids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex)  
                if cartcids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is there for this cutomer!!",'error': True} 
                    raise serializers.ValidationError(result)

                check = "New"
                control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
              
                # cart_rec = ItemCart.objects.all().count()
                # print(cart_rec,"cart_rec")
                cartre = ItemCart.objects.filter(sitecode=site).order_by('cart_id')
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
                    # c_no = int(lst[0]) + 1
                    c_no = int(lst[0][-6:]) + 1
                    cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(c_no)
                else:
                    cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                
                # print(site,"site")
                #cust_noid=cust_obj,
                cartcc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)  
                if cartcc_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                    raise serializers.ValidationError(result)
            
                #same customer
                cartcu_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cart_date,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,check="New").exclude(type__in=type_ex)     
                if len(cartcu_ids) == 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                    raise serializers.ValidationError(result)

                #Different customer
                cartcut_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,check="New").exclude(type__in=type_ex)     
                if len(cartcut_ids) == 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                    raise serializers.ValidationError(result)
            
            cag_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
            cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex)  
            if cag_ids:
                lst = list(set([e.cust_noid.pk for e in cag_ids if e.cust_noid]))
                if len(lst) > 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Each Item Cart ID should have one customer not multiple",'error': True} 
                    raise serializers.ValidationError(result)

                if lst[0] != (cust_obj.pk):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item Cart ID already one customer id is there",'error': True} 
                    raise serializers.ValidationError(result)
            # print(req,"req")
            if serializer.is_valid():
                # if int(stock_obj.Item_Divid.itm_code) == 1 and stock_obj.Item_Divid.itm_desc == 'RETAIL PRODUCT' and stock_obj.Item_Divid.itm_isactive == True:
                # carttype = False
                # if str(req['type']) == 'Deposit': 
                #     carttype = 'Deposit'
                quantity = 1.0
                holdreason=None
                holditemqty=0
                focreason=None
                # print(req,"req")
                # if 'quantity' in request.data and not req['quantity'] is None:
                if not req['quantity'] is None:
                    quantity = req['quantity']
                if int(stock_obj.item_div) == 1:
                    # print(request.data,"reqdata")
                    if req['item_uom'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Retail Product item uom should not be empty",'error': True} 
                        raise serializers.ValidationError(result)

                    # if 'holdreason' in request.data and not request.data['holdreason'] is None:
                    if not req['holdreason'] is None:
                        #if itemcart.is_foc == True:
                        if req['holdreason'] != '':
                            # if not req['is_foc'] is None:
                            #    if req['is_foc'] == True:
                            #        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give holdreason.",'error': True} 
                            #        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            holdobj = HolditemSetup.objects.filter(pk=req['holdreason']).first()
                            if not holdobj:
                                result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"HoldReason ID does not exist!!",'error': True} 
                                raise serializers.ValidationError(result)
                            if int(req['holditemqty']) == 0:
                                result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Please enter Hold item Qty~!",'error': True} 
                                raise serializers.ValidationError(result)
                            holdreason=holdobj
                            # ItemCart.objects.filter(id=itemcart.id).update(holdreason=holdobj)  
                    print(holdreason,"holdreason")
                    # if 'holditemqty' in request.data and not request.data['holditemqty'] is None:
                    if not req['holditemqty'] is None:
                    # if not self.request.data['holditemqty'] is None and request.data['holditemqty'] != 0:
                        if req['holditemqty'] != 0:
                        # if self.request.data['holditemqty']:
                            #if itemcart.is_foc == True:
                            # if req['is_foc'] is None:
                            #    if req['is_foc'] == True:
                            #        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give holditemqty.",'error': True} 
                            #        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            holditemqty=req['holditemqty']
                    print(holditemqty,"holditemqty")

                # if 'focreason' in request.data and not request.data['focreason'] is None:
                if not req['focreason'] is None:
                    if req['focreason'] != '':
                        if int(stock_obj.item_div) == 5:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid not allow Foc Reason!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        focobj = FocReason.objects.filter(pk=req['focreason'],foc_reason_isactive=True).first()
                        if not focobj:
                            result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"FocReason ID does not exist!!",'error': True} 
                            raise serializers.ValidationError(result)
                        focreason=focobj                  
                # print(focreason,"focreason")
                
                #print(quantity,"qty1")
                
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

                if int(stock_obj.item_div) == 1:
                    recorddetail="Product"
                if int(stock_obj.item_div) == 4:
                    recorddetail="Voucher"
                if int(stock_obj.item_div) == 5:
                    recorddetail="Prepaid"

                itemtype=stock_obj.item_type

                tax_value = 0.0
                if stock_obj.is_have_tax == True:
                    tax_value = gst.item_value

                cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cart_date,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex).order_by('lineno')     
                if not cartcuids:
                    lineno = 1
                else:
                    rec = cartcuids.last()
                    lineno = float(rec.lineno) + 1  

                # is_allow_foc = request.GET.get('is_foc',None)
                if not self.request.GET.get('is_foc',None) is None and int(self.request.GET.get('is_foc',None)) == 1:
                    if not stock_obj.is_allow_foc == True:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Product doesn't have FOC",'error': True} 
                        raise serializers.ValidationError(result)
                    print(quantity,"qty0")

                    # if carttype in ['Top Up','Sales']:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC not allow for Top Up / Reedem",'error': True} 
                    #     raise serializers.ValidationError(result)
                    cart = serializer.save(cart_date=cart_date,phonenumber=cust_obj.cust_phone2,
                    customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                    itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc +" "+ "(FOC)",
                    quantity=quantity,price="{:.2f}".format(float(req['price'])),
                    sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                    tax="{:.2f}".format(tax_value),check=check,ratio=100.00,auto=False,is_foc=True,
                    discount_price=0.0,discount=0.0,discount_amt="{:.2f}".format(float(req['price'])),itemtype=itemtype,
                    total_price=float(req['price']) * quantity,trans_amt=0.0,deposit=0.0,type="Deposit",recorddetail=recorddetail,
                    holditemqty=holditemqty,holdreason=holdreason,focreason=focreason)
                else:  
                    # depositamt = float(req['price']) * 1.0
                    # if str(req['type']) == 'Sales':
                    #     depositamt = 0.00
                    # print(quantity,"qty2")

                    cart = serializer.save(cart_date=cart_date,phonenumber=cust_obj.cust_phone2,
                    customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                    itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                    quantity=quantity,price="{:.2f}".format(float(req['price'])),
                    sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                    tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                    # discount_price=float(req['price']) * 1.0,
                    # total_price=float(req['price']) * int(req['qty']) if req['qty'] else float(req['price']) * 1.0,
                    # trans_amt=float(req['price']) * int(req['qty']) if req['qty'] else float(req['price']) * 1.0,
                    # deposit=float(req['price']) * int(req['qty']) if req['qty'] else float(req['price']) * 1.0,
                    discount_price=float(req['price']) * 1.0,total_price=float(req['price']) * float(quantity),itemtype=itemtype,
                    trans_amt=float(req['price']) * float(quantity),deposit=float(req['price']) * float(quantity),
                    type="Deposit",recorddetail=recorddetail,holditemqty=holditemqty,holdreason=holdreason)

                    if 1==1:
                        cls_ids = CustomerClass.objects.filter(class_code=cust_obj.cust_class,class_isactive=True).first()
                        itmcls_ids = ItemClass.objects.filter(itm_code=stock_obj.item_class,itm_isactive=True).first()

                        if stock_obj.autocustdisc == True and cls_ids and itmcls_ids:
                            muti_ids = MultiPricePolicy.objects.filter(item_class_code=stock_obj.item_class,
                            cust_class_code=cust_obj.cust_class).order_by('pk').first()
                            if muti_ids and muti_ids.disc_percent_limit > 0:
                                discper = muti_ids.disc_percent_limit
                                discamt = (float(req['price']) * discper) / 100

                                value = float(req['price']) - discamt
                                amount = value * int(req['qty'])

                                cart.discount = discper
                                cart.discount_amt = discamt
                                cart.discount_price = value
                                cart.deposit = amount
                                cart.trans_amt = amount
                                cart.save()

                                posdisc = PosDisc(sa_transacno=None,dt_itemno=stock_obj.item_code+"0000",
                                disc_amt=discamt,disc_percent=discper,
                                dt_lineno=cart.lineno,remark='Member',site_code=site.itemsite_code,
                                dt_status="New",dt_auto=1,line_no=1,disc_user=fmspw[0].emp_code,lnow=1,dt_price=None,
                                istransdisc=False)
                                posdisc.save()
                                # print(posdisc.id,"posdisc")  
                                cart.pos_disc.add(posdisc.id) 

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
                    if 1==1:
                        ratio = 0.0; salescommpoints = 0.0
                        if cart.sales_staff.all().count() > 0:
                            count = cart.sales_staff.all().count()
                            ratio = float(cart.ratio) / float(count)
                            salesamt = float(cart.trans_amt) / float(count)
                            if stock_obj.salescommpoints and float(stock_obj.salescommpoints) > 0.0:
                                salescommpoints = float(stock_obj.salescommpoints) / float(count)

                        mul_ids = Tmpmultistaff.objects.filter(emp_id__pk=logstaff.pk,
                        itemcart__pk=cart.pk)
                        if not mul_ids:
                            tmpmulti = Tmpmultistaff(item_code=stock_obj.item_code,
                            emp_code=logstaff.emp_code,ratio=ratio,
                            salesamt="{:.2f}".format(float(salesamt)),type=None,isdelete=False,role=1,
                            dt_lineno=cart.lineno,itemcart=cart,emp_id=logstaff,salescommpoints=salescommpoints)
                            tmpmulti.save()
                            cart.multistaff_ids.add(tmpmulti.pk)

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
                #     raise serializers.ValidationError(result)

                # amt = subtotal - discamt
                # taxamt = amt * (tax/100)
                # if gst.is_exclusive == True:
                #     billable_amount = "{:.2f}".format(amt + taxamt)
                # else:
                #     billable_amount = "{:.2f}".format(amt)
            else:
                print("Invalid Input","Invalid Input") 
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


    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def TopUpCartCreate(self, request):
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
                cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex)
                if not cartchids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is not there for this cutomer,Give Without cart_id in parms!!",'error': True} 
                    raise serializers.ValidationError(result)

                check = "Old"
                # print(site,"site")
                #cust_noid=cust_obj,
                cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
                if cartc_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                    raise serializers.ValidationError(result)
            else:
                cartcids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex)
                if cartcids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is there for this cutomer!!",'error': True} 
                    raise serializers.ValidationError(result)

                check = "New"
                control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
                    
                cartre = ItemCart.objects.filter(sitecode=site).order_by('cart_id')
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
                    # c_no = int(lst[0]) + 1
                    c_no = int(lst[0][-6:]) + 1
                    cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(c_no)
                else:
                    cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                
                # print(site,"site")
                #cust_noid=cust_obj,
                cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
                if cartc_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                    raise serializers.ValidationError(result)
            
                #same customer
                cartcu_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,check="New").exclude(type__in=type_ex)   
                if len(cartcu_ids) == 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                    raise serializers.ValidationError(result)

                #Different customer
                cartcut_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,check="New").exclude(type__in=type_ex)   
                if len(cartcut_ids) == 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                    raise serializers.ValidationError(result)
            
            cag_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
            cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex)
            if cag_ids:
                lst = list(set([e.cust_noid.pk for e in cag_ids if e.cust_noid]))
                if len(lst) > 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Each Item Cart ID should have one customer not multiple",'error': True} 
                    raise serializers.ValidationError(result)

                if lst[0] != (cust_obj.pk):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item Cart ID already one customer id is there",'error': True} 
                    raise serializers.ValidationError(result)

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

            # stock_obj = Stock.objects.filter(pk=req['itemcodeid'],item_isactive=True).first()
            stock_obj = Stock.objects.filter(pk=req['itemcodeid']).first()
            recorddetail="TP Service"
            if not stock_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            itemtype=stock_obj.item_type
            item_div = ItemDiv.objects.filter(pk=stock_obj.Item_Divid.pk).first()
            item_dept = ItemDept.objects.filter(pk=stock_obj.Item_Deptid.pk,itm_status=True).first()

            if item_div.itm_code == '3' and item_dept.is_service == True:
                # acc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account'],site_code=site.itemsite_code).first()
                acc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account']).first()
                if not acc_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Account ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                carttp_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,
                treatment_account__pk=req['treatment_account'],type='Top Up').exclude(type__in=type_ex).order_by('lineno')

            elif item_div.itm_code == '1' and item_dept.is_retailproduct == True:
                #acc_obj = DepositAccount.objects.filter(pk=req['deposit_account'],site_code=site.itemsite_code).order_by('id').first()
                acc_obj = DepositAccount.objects.filter(pk=req['deposit_account']).order_by('id').first()
                if not acc_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit Account ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                carttp_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,
                deposit_account__pk=req['deposit_account'],type='Top Up').exclude(type__in=type_ex).order_by('lineno')   
                recorddetail="TP Product"
        
            elif item_div.itm_code == '5' and item_dept.is_prepaid == True:
                # acc_obj = PrepaidAccount.objects.filter(pk=req['prepaid_account'],site_code=site.itemsite_code).order_by('id').first() 
                acc_obj = PrepaidAccount.objects.filter(pk=req['prepaid_account']).order_by('id').first() 
                if not acc_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid Account ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                carttp_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,
                prepaid_account__pk=req['prepaid_account'],type='Top Up').exclude(type__in=type_ex).order_by('lineno')   
                recorddetail="TP Prepaid"
            
            else:
                acc_obj = None
                if acc_obj is None:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Account ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                carttp_ids = None    
          
            gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
        
            print(req,"req")
            
            if serializer.is_valid():
                tax_value = 0.0
                if stock_obj.is_have_tax == True:
                    tax_value = gst.item_value

                cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex).order_by('lineno')   
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
                            raise serializers.ValidationError(result)

                        if not stock_obj.is_allow_foc == True:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Product doesn't have FOC",'error': True} 
                            raise serializers.ValidationError(result)

                        cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                        customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                        itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                        quantity=1,price="{:.2f}".format(float(req['price'])),
                        sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                        tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                        discount_price=0.0,discount=0.0,discount_amt="{:.2f}".format(float(req['price'])),itemtype=itemtype,
                        total_price=float(req['price']) * 1.0,trans_amt=0.0,deposit=0.0,type="Top Up",recorddetail=recorddetail)
                    else:    
                        cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                        customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                        itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                        quantity=1,price="{:.2f}".format(float(req['price'])),
                        sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                        tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                        discount_price=float(req['price']) * 1.0,total_price=float(req['price']) * 1.0,itemtype=itemtype,
                        trans_amt=float(req['price']) * 1.0,deposit=float(req['price']) * 1.0,type="Top Up",recorddetail=recorddetail)

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
                    #     raise serializers.ValidationError(result)

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

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def TrmtDoneCartCreate(self, request):
        global type_ex
        cartdate = timezone.now().date()
        for idx, req in enumerate(request.data, start=1):
            cust_obj = Customer.objects.filter(pk=req['cust_noid'],cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
        
        cart_lst = [];subtotal = 0.0; discount=0.0; billable_amount=0.0;trans_amt=0.0;deposit_amt = 0.0;cart_id = 0
        for idx, req in enumerate(request.data, start=1):
            # print(request.data,"requstdata")
            if cart_id==0:
                cart_id = request.GET.get('cart_id',None)
            if cart_id:
                cartchids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex)
                if not cartchids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is not there for this cutomer,Give Without cart_id in parms!!",'error': True} 
                    raise serializers.ValidationError(result)

                # print(site,"site")
                check = "Old"
                #cust_noid=cust_obj,
                cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
                if cartc_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                    raise serializers.ValidationError(result)
            else:
                cartcids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cust_noid=cust_obj,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex)
                if cartcids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Inprogress record is there for this cutomer!!",'error': True} 
                    raise serializers.ValidationError(result)

                check = "New"

                control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
                    
                cartre = ItemCart.objects.filter(sitecode=site).order_by('cart_id')
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
                    c_no = int(lst[0][-6:]) + 1
                    cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(c_no)
                else:
                   cart_id = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                
                # print(site,"site")
                #cust_noid=cust_obj,
                cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
                if cartc_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                    raise serializers.ValidationError(result)
            
                #same customer
                cartcu_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,check="New").exclude(type__in=type_ex)   
                if len(cartcu_ids) == 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                    raise serializers.ValidationError(result)

                #Different customer
                cartcut_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,check="New").exclude(type__in=type_ex)   
                if len(cartcut_ids) == 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id!!",'error': True} 
                    raise serializers.ValidationError(result)
            
            cag_ids = ItemCart.objects.filter(isactive=True,cart_date=cartdate,
            cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex)
            if cag_ids:
                lst = list(set([e.cust_noid.pk for e in cag_ids if e.cust_noid]))
                if len(lst) > 1:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Each Item Cart ID should have one customer not multiple",'error': True} 
                    raise serializers.ValidationError(result)

                if lst[0] != (cust_obj.pk):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Item Cart ID already one customer id is there",'error': True} 
                    raise serializers.ValidationError(result)

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

            #stock_obj = Stock.objects.filter(pk=req['itemcodeid'],item_isactive=True).first()
            stock_obj = Stock.objects.filter(pk=req['itemcodeid']).first()
            if not stock_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            recorddetail="TD"
            itemtype=stock_obj.item_type
            # trmtacc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account'],site_code=site.itemsite_code).first()
            # print(req['treatment'],"treatmentid")
            # arrtreatmentid = req['treatment'].split(',')
            firstid = 0
            qtyid = 1
            if isinstance(req['treatment'], list):
                for tt in req['treatment']:
                     # print(tt,"tt")
                     if firstid == 0:
                         firstid = tt
                     else:
                         qtyid+=1           
            else:
                firstid = req['treatment']
         
            # print(firstid,"firstid")
            trmtacc_obj = TreatmentAccount.objects.filter(pk=req['treatment_account']).first()
            # trmtacc_obj = TreatmentAccount.objects.filter(pk=firstid).first()
            if not trmtacc_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Account ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # trmt_obj = Treatment.objects.filter(pk=req['treatment'],site_code=site.itemsite_code).first()
            # print(req['treatment'],"treatmentid")
            # trmt_obj = Treatment.objects.filter(pk=req['treatment']).first()
            trmt_obj = Treatment.objects.filter(pk=firstid).first()
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

            if 1==1:
                if req['ori_stockid']:

                    ori_stockobj = Stock.objects.filter(pk=req['ori_stockid'],item_isactive=True).first()

                    excontrol_obj = ControlNo.objects.filter(control_description__iexact="EXCHANGE NO",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                    if not excontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"EXCHANGE NO Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                            
                    controlno = str(excontrol_obj.Site_Codeid.itemsite_code)+str(excontrol_obj.control_no)
                    
                    ex = ExchangeDtl(exchange_no=controlno,staff_code=fmspw[0].Emp_Codeid.emp_code,
                    staff_name=fmspw[0].Emp_Codeid.emp_name,original_item_code=ori_stockobj.item_code+"0000",
                    original_item_name=ori_stockobj.item_name,exchange_item_code=stock_obj.item_code+"0000",
                    exchange_item_name=stock_obj.item_name,trmt_code=trmt_obj.treatment_parentcode,
                    trmt_full_code=trmt_obj.treatment_code,treatment_time=trmt_obj.times,sa_transacno=trmt_obj.sa_transacno,
                    status=False,site_code=site.itemsite_code,cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name)
                    ex.save()
            
            # Yoonus
            req['treatment'] = firstid
            if serializer.is_valid():
                tax_value = 0.0
                if stock_obj.is_have_tax == True:
                    tax_value = gst.item_value

                cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site).exclude(type__in=type_ex).order_by('lineno')   
                if not cartcuids:
                    lineno = 1
                else:
                    rec = cartcuids.last()
                    lineno = float(rec.lineno) + 1  

                # staffsno = str(trmtacc_obj.sa_staffno).split(',')
                # empids = Employee.objects.filter(emp_code__in=staffsno,emp_isactive=True)

                # is_allow_foc = request.GET.get('is_foc',None)

                carttr_ids = ItemCart.objects.filter(isactive=True,cust_noid=cust_obj,cart_date=cartdate,
                cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecode=site,
                treatment_account__pk=trmtacc_obj.pk,treatment__pk=trmt_obj.pk,type='Sales').exclude(type__in=type_ex).order_by('lineno')   
                # print(lineno,"lineno")
                if not carttr_ids:
                    # print(cart_id,"cart_id")
                    if not self.request.GET.get('is_foc',None) is None and int(self.request.GET.get('is_foc',None)) == 1:
                        if self.request.GET.get('is_foc',None):
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sales will not have FOC!!",'error': True} 
                            raise serializers.ValidationError(result)

                        if not stock_obj.is_allow_foc == True:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Product doesn't have FOC",'error': True} 
                            raise serializers.ValidationError(result)

                        # quantity=1,price="{:.2f}".format(float(req['price'])),
                        # total_price=float(req['price']) * 1.0,trans_amt=0.0,deposit=0.0,type="Sales",recorddetail=recorddetail)
                        cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                        customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                        itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                        quantity=qtyid,price="{:.2f}".format(float(req['price'])),
                        sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                        tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                        discount_price=0.0,discount=0.0,discount_amt="{:.2f}".format(float(req['price'])),itemtype=itemtype,
                        total_price=float(req['price']) * qtyid,trans_amt=0.0,deposit=0.0,type="Sales",recorddetail=recorddetail)
                    else:    
                        cart = serializer.save(cart_date=cartdate,phonenumber=cust_obj.cust_phone2,
                        customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                        itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                        quantity=qtyid,price="{:.2f}".format(float(req['price'])),
                        sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                        tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                        discount_price=float(req['price']) * 1.0,total_price=float(req['price']) * 1.0,itemtype=itemtype,
                        trans_amt=float(req['price']) * qtyid,deposit=0.0,type="Sales",recorddetail=recorddetail)

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
                    #     raise serializers.ValidationError(result)

                    # amt = subtotal - discamt
                    # taxamt = amt * (tax/100)
                    # if gst.is_exclusive == True:
                    #     billable_amount = "{:.2f}".format(amt + taxamt)
                    # else:
                    #     billable_amount = "{:.2f}".format(amt)
                    # print(message,"message")
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
        
        print(cart_lst,"cart_lst")
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
            result = {'status': status.HTTP_201_CREATED,"message":"Already Cart Created",'error': False}
            return Response(result, status=status.HTTP_201_CREATED)

    
        message = "Invalid Input"
        error = True
        data = []
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":message,'error': error, 'data': data}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
       
        
    def get_object(self, pk):
        # try:
            return ItemCart.objects.get(pk=pk,isactive=True)
        #except ItemCart.DoesNotExist:
        #    raise Http404

    def retrieve(self, request, pk=None):
        global type_ex
        cart = self.get_object(pk)
        if cart.type in ['Top Up','Sales','Exchange']:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales/Exchange Cart Edit is not applicable!!",'error': True} 
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
        
    def update(self, request, pk=None):
        itemcart = self.get_object(pk)
        cust_obj = itemcart.cust_noid
        cart_id = itemcart.cart_id
        cart_date = itemcart.cart_date
        trans_amt = itemcart.trans_amt

        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
       
        empl = fmspw.Emp_Codeid

        if itemcart.type in ['Top Up','Sales','Exchange']:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales/Exchange Cart Edit is not applicable!!",'error': True} 
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
            if 1==1:
                itemcart.pos_disc.all().filter().delete()

                tmp_treat_ids = Tmptreatment.objects.filter(itemcart=itemcart).order_by('pk') 
                if tmp_treat_ids:
                    if int(self.request.GET.get('auto',None)) == 0:
                        number = Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk').count()
                        price = itemcart.price * number

                        Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk'
                        ).update(price="{:.2f}".format(float(price)),unit_amount="{:.2f}".format(float(itemcart.price)),trmt_is_auto_proportion=False)

                        Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True).order_by('pk'
                        ).update(price=0,unit_amount=0.00,trmt_is_auto_proportion=False)

                    elif int(self.request.GET.get('auto',None)) == 1: 
                        no = Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk').count()
                        price = itemcart.price * no
                        # print(price, type(price),"kk")
                        number = Tmptreatment.objects.filter(itemcart=itemcart).order_by('pk').count()
                        
                        d_price = price / number

                        Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk'
                        ).update(price="{:.2f}".format(float(price)),unit_amount="{:.2f}".format(float(d_price)),trmt_is_auto_proportion=True)
                        
                        l_ids = Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True).order_by('pk').last()

                        Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True).order_by('pk'
                        ).exclude(pk=l_ids.pk).update(price=0,unit_amount="{:.2f}".format(float(d_price)),trmt_is_auto_proportion=True)
                        
                        amt = "{:.2f}".format(float(d_price))   
                        lval = float(price) - (float(amt) * (number -1))

                        Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True,pk=l_ids.pk).order_by('pk'
                        ).update(price=0,unit_amount="{:.2f}".format(float(lval)),trmt_is_auto_proportion=True)


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
                    raise serializers.ValidationError(result)
                else:
                    if 'discount' in request.data and 'discount_amt' in request.data:
                        if not float(request.data['discount']) >= 0 and float(request.data['discount_amt']) >= 0:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give either Discount / Discount Amount,Both should not be zero!!",'error': True} 
                            raise serializers.ValidationError(result)

                if disclimit == 0.0:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Discount is not allowed for this product !!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                
                if 'discount' in request.data and float(request.data['discount']) != 0.0:
                    
                    if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher / Prepaid / Package not allow Discount!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
              
                    if float(request.data['discount']) > disclimit:
                        result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Discount is not greater than stock discount!!",'error': True} 
                        raise serializers.ValidationError(result)

                    if float(request.data['discount']) > float(itemcart.price):
                        msg = "Discount is > {0} !".format(itemcart.price)
                        result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":msg,'error': True} 
                        raise serializers.ValidationError(result)
                    
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
                            result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Discount is not greater than stock discount!!",'error': True} 
                            raise serializers.ValidationError(result)
                        
                        if float(request.data['discount_amt']) > itemcart.price:
                            msg = "Discount is > {0} !".format(itemcart.price)
                            result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":msg,'error': True} 
                            raise serializers.ValidationError(result)
                        
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
                        result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Disc Reason ID does not exist!!",'error': True} 
                        raise serializers.ValidationError(result)
                    
                    if discobj.r_code == '100006' and discobj.r_desc == 'OTHERS':
                        if request.data['discreason_txt'] is None:
                            result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Please Enter Disc Reason Text!!",'error': True} 
                            raise serializers.ValidationError(result)
                        if 'discreason_txt' not in request.data:
                            result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Please Enter Disc Reason Text and add key!!",'error': True} 
                            raise serializers.ValidationError(result)

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
                
                if 1==1:
                    tmptreat_ids = Tmptreatment.objects.filter(itemcart=itemcart).order_by('pk') 
                    if tmptreat_ids:
                        disamt = itemcart.pos_disc.all().filter(istransdisc=False).aggregate(Sum('disc_amt'))

                        if disamt['disc_amt__sum']:
                            dprice = float(itemcart.price) - disamt['disc_amt__sum']
                            if int(self.request.GET.get('auto',None)) == 0:
                                number = Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk').count()
                                price = dprice * number

                                Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk'
                                ).update(price="{:.2f}".format(float(price)),unit_amount="{:.2f}".format(float(dprice)),trmt_is_auto_proportion=False)

                                Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True).order_by('pk'
                                ).update(price=0,unit_amount=0.00,trmt_is_auto_proportion=False)

                            elif int(self.request.GET.get('auto',None)) == 1: 
                                no = Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk').count()
                                price = dprice * no
                                number = Tmptreatment.objects.filter(itemcart=itemcart).order_by('pk').count()
                                
                                d_price = price / number

                                l_ids = Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True).order_by('pk').last()

                                Tmptreatment.objects.filter(itemcart=itemcart,isfoc=False).order_by('pk'
                                ).exclude(pk=l_ids.pk).update(price="{:.2f}".format(float(price)),unit_amount="{:.2f}".format(float(d_price)),trmt_is_auto_proportion=True)

                                Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True).order_by('pk'
                                ).update(price=0,unit_amount="{:.2f}".format(float(d_price)),trmt_is_auto_proportion=True)
                                
                                amt = "{:.2f}".format(float(d_price))   
                                lval = price - (float(amt) * (number -1))

                                Tmptreatment.objects.filter(itemcart=itemcart,isfoc=True,pk=l_ids.pk).order_by('pk'
                                ).update(price=0,unit_amount="{:.2f}".format(float(lval)),trmt_is_auto_proportion=True)
            
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
                if not int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
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
            #             raise serializers.ValidationError(result)

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
                        raise serializers.ValidationError(result)

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
            #             raise serializers.ValidationError(result)

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
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"ItemStatus ID does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

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
                if not int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE': 
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
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Deposit should not be greater than transaction amount!!",'error': True} 
                    raise serializers.ValidationError(result)

                if itemcart.is_foc == True:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give Deposit.",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    

                if float(self.request.GET.get('deposit',None)) == 0.0:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Deposit should not be Zero!!",'error': True} 
                    raise serializers.ValidationError(result)

                if int(itemcart.itemcodeid.item_div) != 4:
                    ItemCart.objects.filter(id=itemcart.id).update(deposit=self.request.GET.get('deposit',None))                    

            if 'remark' in request.data and not request.data['remark'] is None:
                ItemCart.objects.filter(id=itemcart.id).update(remark=request.data['remark'])    

            if 'focreason' in request.data and not request.data['focreason'] is None:
               
                if int(itemcart.itemcodeid.item_div) == 5:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid not allow Foc Reason!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
               
                focobj = FocReason.objects.filter(pk=request.data['focreason'],foc_reason_isactive=True).first()
                if not focobj:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"FocReason ID does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

                if itemcart.itemcodeid.is_allow_foc == None or itemcart.itemcodeid.is_allow_foc == False:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"This Item will not have is allow foc true!!",'error': True} 
                    raise serializers.ValidationError(result)
                
                if disclimit != 100.00:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"This Item will not have 100% disclimit!!",'error': True} 
                    raise serializers.ValidationError(result)
                
                ItemCart.objects.filter(id=itemcart.id).update(focreason=focobj)                    
            
            if 'holdreason' in request.data and not request.data['holdreason'] is None:
                if itemcart.is_foc == True:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give holdreason.",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
  
                holdobj = HolditemSetup.objects.filter(pk=request.data['holdreason']).first()
                if not holdobj:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"HoldReason ID does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

                if int(self.request.data['holditemqty']) == 0:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Please enter Hold item Qty~!",'error': True} 
                    raise serializers.ValidationError(result)
    
                ItemCart.objects.filter(id=itemcart.id).update(holdreason=holdobj)  
                                  
            
            if not self.request.data['holditemqty'] is None and request.data['holditemqty'] != 0:
                if self.request.data['holditemqty']:
                    if itemcart.is_foc == True:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give holditemqty.",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
                    if int(self.request.data['holditemqty']) > int(itemcart.quantity):
                        result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Please Enter valid Hold Item Qty,Cart Qty {0}!".format(itemcart.quantity),
                        'error': True} 
                        raise serializers.ValidationError(result)

                    ItemCart.objects.filter(id=itemcart.id).update(holditemqty=request.data['holditemqty'])  

            if not self.request.data['ratio'] is None and request.data['ratio'] != 0.0:
                ItemCart.objects.filter(id=itemcart.id).update(ratio=request.data['ratio'])  

            if 1==1:
                # print(itemcart.sales_staff.all(),"itemcart.sales_staff.all()")
                ratio = 0.0; salescommpoints = 0
                if itemcart.sales_staff.all().count() > 0:
                    count = itemcart.sales_staff.all().count()
                    ratio = float(itemcart.ratio) / float(count)
                    salesamt = float(trans_amt) / float(count)
                    if float(itemcart.itemcodeid.salescommpoints) > 0.0:
                        salescommpoints = float(itemcart.itemcodeid.salescommpoints) / float(count)


                for i in itemcart.sales_staff.all():
                    mul_ids = Tmpmultistaff.objects.filter(emp_id__pk=i.pk,
                    itemcart__pk=itemcart.pk)
                    if not mul_ids:
                        tmpmulti = Tmpmultistaff(item_code=itemcart.itemcodeid.item_code,
                        emp_code=i.emp_code,ratio=ratio,
                        salesamt="{:.2f}".format(float(salesamt)),type=None,isdelete=False,role=1,
                        dt_lineno=itemcart.lineno,itemcart=itemcart,emp_id=i,salescommpoints=salescommpoints)
                        tmpmulti.save()
                        itemcart.multistaff_ids.add(tmpmulti.pk)
                    else:
                        mul_ids[0].ratio = ratio
                        mul_ids[0].salesamt = "{:.2f}".format(float(salesamt))
                        mul_ids[0].salescommpoints = salescommpoints
                        mul_ids[0].save()

                del_ids = Tmpmultistaff.objects.filter(itemcart__pk=itemcart.pk).exclude(emp_id__in=sales_staff).delete()
     
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

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def SetAdditionalDiscList(self, request): 
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
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 12",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        
        cart_ids = queryset.filter(itemcodeid__item_div__in=[1,3],itemcodeid__item_type='SINGLE').exclude(is_foc=True)
        if not cart_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"There is no cart based on this Cart ID so create cart then add addtional discount/Not Allowable!!",'error': True} 
            raise serializers.ValidationError(result)
        
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
             

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def SetAdditionalDisc(self, request): 
       
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
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 13",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)

        cart_ids = queryset
        if not cart_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"There is not cart based on this Cart ID so create cart then add addtional discount!!",'error': True} 
            raise serializers.ValidationError(result)
        
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
                result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Disc Reason ID does not exist!!",'error': True} 
                raise serializers.ValidationError(result)

            if discobj.r_code == '100006' and discobj.r_desc == 'OTHERS':
                if self.request.GET.get('discreason_txt',None) is None:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Please Enter Disc Reason Text!!",'error': True} 
                    raise serializers.ValidationError(result)
                if 'discreason_txt' not in self.request.GET:
                    result = {'status': status.HTTP_406_NOT_ACCEPTABLE,"message":"Please Enter Disc Reason Text and add key!!",'error': True} 
                    raise serializers.ValidationError(result)

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


    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication],name='qtyupdate')
    def qtyupdate(self, request, pk=None):

        itemcart = self.get_object(pk)
        if itemcart.type in ['Top Up','Sales','Exchange']:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales/Exchange Cart Edit is not applicable!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
        #client told to change quantity
        # if itemcart.is_foc == True:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give qty.",'error': True} 
        #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
  
        check = self.request.GET.get('check',None)
        if not check:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give check for Plus/Minus",'error': True}
            return Response(data=result, status=status.HTTP_200_OK)
        
        if int(itemcart.itemcodeid.item_div) in [4,5] or itemcart.itemcodeid.item_type== 'PACKAGE':
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

    def partial_update(self, request, pk=None):
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
        Tmpmultistaff.objects.filter(itemcart=instance).delete()
        Tmptreatment.objects.filter(itemcart=instance).delete()
        instance.delete() 

class VoucherRecordViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = VoucherRecord.objects.filter(isvalid=True).order_by('-id')
    serializer_class = VoucherRecordSerializer

    def list(self, request):
        # appt_ids = Appointment.objects.filter(pk=request.GET.get('Appointment_id',None),appt_isactive=True)
        # if not appt_ids:
        #    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
        #    raise serializers.ValidationError(result)
        # app_obj = Appointment.objects.filter(pk=request.GET.get('Appointment_id',None))[0]
        cust_obj = Customer.objects.filter(pk=self.request.GET.get('cust_id',None),cust_isactive=True).first()
        if not cust_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('voucher_no',None):
            queryset = VoucherRecord.objects.filter(isvalid=True,cust_codeid=cust_obj.cust_no,voucher_no=request.GET.get('voucher_no',None)).order_by('-pk')
        else:
            queryset = VoucherRecord.objects.filter(isvalid=True,cust_codeid=cust_obj.cust_no).order_by('-pk')

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
            result = {'status': state,"message":message,'error': error, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)              
    
def receipt_calculation(request, daud):
    # cart_ids = ItemCart.objects.filter(isactive=True,Appointment=app_obj,is_payment=True)
    gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
    subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0; 
    trans_amt=0.0 ;deposit_amt =0.0; tax_amt = 0.0; billable_amount=0.0;total_balance = 0.0;total_qty = 0
    for ct in daud:
        c = ct.itemcart
        # total = "{:.2f}".format(float(c.price) * int(c.quantity))
        subtotal += float(c.total_price)
        discount_amt += float(c.discount_amt)
        additional_discountamt += float(c.additional_discountamt)
        trans_amt += float(c.trans_amt)
        deposit_amt += float(c.deposit)
        balance = float(c.trans_amt) - float(c.deposit)
        total_balance += float(balance)
        total_qty += int(c.quantity)

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
    
    print(request.user,"1 request.user")
    fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
    site = fmspw.loginsite 
    calcgst = 0
    if gst:
        calcgst = gst.item_value
    if calcgst > 0:
        sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
        if sitegst:
            if sitegst.site_is_gst == False:
                calcgst = 0

    if calcgst > 0:
        if gst.is_exclusive == True:
            tax_amt = deposit_amt * (calcgst / 100)
            billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
        else:
            billable_amount = "{:.2f}".format(deposit_amt)
            tax_amt = deposit_amt * calcgst / (100+calcgst)
    else:
        billable_amount = "{:.2f}".format(deposit_amt)

    sub_total = "{:.2f}".format(float(subtotal))
    round_val = float(round_calc(billable_amount)) # round()
    billable_amount = float(billable_amount) + round_val 
    sa_Round = round_val
    discount = discount_amt + additional_discountamt
    itemvalue = "{:.2f}".format(float(gst.item_value))

    value = {'subtotal':sub_total,'discount': "{:.2f}".format(float(discount)),'trans_amt': "{:.2f}".format(float(trans_amt)),
    'deposit_amt': "{:.2f}".format(float(deposit_amt)),'tax_amt':"{:.2f}".format(float(tax_amt)),
    'tax_lable': "Tax Amount"+"("+str(itemvalue)+" "+"%"+")",'sa_Round': "{:.2f}".format(float(sa_Round)),
    'billable_amount': "{:.2f}".format(float(billable_amount)),'balance': "{:.2f}".format(float(balance)),
    'total_balance': "{:.2f}".format(float(total_balance)),'total_qty':total_qty}
    return value


class ReceiptPdfGeneration(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request, format=None):
        if request.GET.get('sa_transacno',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sa_transacno!!",'error': True} 
            raise serializers.ValidationError(result)    
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite 
        sa_transacno = request.GET.get('sa_transacno',None)
        hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
        ItemSite_Codeid__pk=site.pk).order_by("pk")
        if not hdr:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sa Transacno Does not exist in Poshaud!!",'error': True} 
            raise serializers.ValidationError(result)    

        ip_link = GeneratePDF(self, request, sa_transacno)
        if ip_link:
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': ip_link}
            return Response(data=result, status=status.HTTP_200_OK) 
        else:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Data",'error': True}
            return Response(data=result, status=status.HTTP_200_OK)      


class ReceiptPdfSend(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def post(self, request, format='json'):
        if request.GET.get('sa_transacno',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sa_transacno!!",'error': True} 
            raise serializers.ValidationError(result) 

        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite  
        sa_transacno = request.GET.get('sa_transacno',None)
        hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
        ItemSite_Codeid__pk=site.pk).order_by("pk")
        if not hdr:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sa Transacno Does not exist in Poshaud!!",'error': True} 
            raise serializers.ValidationError(result)    

        template_path = 'customer_receipt.html'
        # gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
        hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
        ItemSite_Codeid__pk=site.pk).order_by("id")[:1]
        daud = PosDaud.objects.filter(sa_transacno=sa_transacno,
        ItemSite_Codeid__pk=site.pk)
        taud = PosTaud.objects.filter(sa_transacno=sa_transacno,
        ItemSIte_Codeid__pk=site.pk)
        if not taud:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"sa_transacno Does not exist!!",'error': True} 
            raise serializers.ValidationError(result)    

        Pos_daud = PosDaud.objects.filter(sa_transacno=sa_transacno,
        ItemSite_Codeid__pk=site.pk).first()

        tot_qty = 0;tot_trans = 0 ; tot_depo = 0; tot_bal = 0;balance = 0
        tot_amt = 0;tot_disc = 0;
        dtl_serializer = PosdaudSerializer(daud, many=True)
        dtl_data = dtl_serializer.data
        for dat in dtl_data:
            d = dict(dat)
            d_obj = PosDaud.objects.filter(pk=d['id'],ItemSite_Codeid__pk=site.pk).first()

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
                net_amt = d_obj.dt_qty * d_obj.dt_price
                if d_obj.isfoc == False:
                    tot_amt += net_amt
                    discvalue = net_amt - d_obj.dt_amt
                    tot_disc += discvalue
                
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
        
        calcgst = 0
        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
        if gst:
            calcgst = gst.item_value
            if calcgst > 0:
                sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                if sitegst:
                    if sitegst.site_is_gst == False:
                        calcgst = 0

        tax_amt = 0
        billable_amount = "{:.2f}".format(tot_depo)
        if calcgst > 0:
            if gst.is_exclusive == True:
                tax_amt = tot_depo * (calcgst / 100)
                billable_amount = "{:.2f}".format(tot_depo + tax_amt)
            else:
                billable_amount = "{:.2f}".format(tot_depo)
                tax_amt = tot_depo * calcgst / (100+calcgst)
        else:
            billable_amount = "{:.2f}".format(tot_depo)

        # sub_data = {'total_qty':str(tot_qty),'trans_amt':str("{:.2f}".format((tot_trans))),
        # 'deposit_amt':str("{:.2f}".format((tot_depo))),'total_balance':str("{:.2f}".format((tot_bal))),
        # 'subtotal':str("{:.2f}".format((tot_depo))),'billing_amount':"{:.2f}".format(float(billable_amount))}
        sub_data = {'total_qty':str(tot_qty),'trans_amt':str("{:.2f}".format((tot_trans))),
        'deposit_amt':str("{:.2f}".format((tot_depo))),'total_balance':str("{:.2f}".format((tot_bal))),
        'subtotal':str("{:.2f}".format((tot_depo))),'billing_amount':"{:.2f}".format(float(billable_amount)),
        'tot_amt': str("{:.2f}".format((tot_amt))),'tot_disc':str("{:.2f}".format((tot_disc)))}

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
        'date':date,'time':time,'percent':int(gst.item_value),'path':path if path else '','title':title if title else None}
        data.update(sub_data)

        html = render_to_string(template_path, data)

        result = BytesIO()
        # pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")),result)

        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")),result)
        subject = 'Customer Receipt Pdf'
        if Pos_daud.itemcart.cust_noid.cust_email is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer email!!",'error': True} 
            raise serializers.ValidationError(result)

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

class PaymentRemarksAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PaymentRemarks.objects.filter(isactive=True).order_by('id')
    serializer_class = PaymentRemarksSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 15",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 


class HolditemSetupAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = HolditemSetup.objects.filter().order_by('id')
    serializer_class = HolditemSetupSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 16",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 

class CartItemDeleteAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def post(self, request, format='json'):
        cart_id = self.request.GET.get('cart_id', None)
        # print(cart_id,"cart_id")
        try:
            cartids=ItemCart.objects.filter(cart_id=cart_id)
        except:
            return Response({'success' : 'False','message':'No ItemCart object found'},status=400)
        if cartids:
            for i in cartids:
                TreatmentAccount.objects.filter(itemcart=i).update(itemcart=None)
                PosDaud.objects.filter(itemcart=i).update(itemcart=None)
                TmpItemHelper.objects.filter(itemcart=i).update(itemcart=None)
                PosPackagedeposit.objects.filter(itemcart=i).delete()
                Tmpmultistaff.objects.filter(itemcart=i).delete()
                Tmptreatment.objects.filter(itemcart=i).delete()
                i.isactive = False
                i.delete()
            # self.perform_destroy(obj)
            # obj.isactive = False
            # obj.delete()
            # obj.delete()

            return Response({'success' : 'True','message':'ItemCart deleted successfully'},status=200)
        else:
            return Response({'success': 'False','message':'Bad request'},status=400)

    def perform_destroy(self, instance):
        instance.isactive = False
        TreatmentAccount.objects.filter(itemcart=instance).update(itemcart=None)
        PosDaud.objects.filter(itemcart=instance).update(itemcart=None)
        TmpItemHelper.objects.filter(itemcart=instance).update(itemcart=None)
        PosPackagedeposit.objects.filter(itemcart=instance).delete()
        Tmpmultistaff.objects.filter(itemcart=instance).delete()
        Tmptreatment.objects.filter(itemcart=instance).delete()
        instance.delete()

class PosPackagedepositViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
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
        # try:
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
        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)

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
    authentication_classes=[TokenAuthentication])
    def confirm(self, request):  
        # try:
            if request.data:
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite
                cart_date = timezone.now().date()
                if not request.GET.get('cartid',None):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Cart Record ID",'error': True}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                # cartobj = ItemCart.objects.filter(pk=request.GET.get('cartid',None),cart_date=cart_date,
                # cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code).order_by('lineno')    
                cartobj = ItemCart.objects.filter(pk=request.GET.get('cartid',None),cart_date=cart_date,
                cart_status="Inprogress",isactive=True,is_payment=False).order_by('lineno')    
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
                        # Checking for hold item
                        # if int(itmstock.item_div) != 1:
                        #    if int(req['hold_qty']) != 0.0:
                        #        msg = "{0} This Product can't hold item".format(str(pos.description))
                        #        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        #        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        if int(itmstock.item_div) == 1: 
                            if int(req['hold_qty']) > int(pos.qty):
                                # print(int(req['hold_qty']) > int(pos.qty),"ll")
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

        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)     

class ExchangeProductAPIView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ExchangeProductSerializer
    
    def create(self, request):
        try:
            global type_ex
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            cart_date = timezone.now().date()
            serializer = ExchangeProductSerializer(data=request.data)
            cust_obj = Customer.objects.filter(pk=request.data['cust_id'],cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            queryset = ItemCart.objects.filter(isactive=True,sitecodeid=site,cust_noid=cust_obj,cart_id=request.data['cart_id'],cart_date=cart_date,
            cart_status="Inprogress",is_payment=False).exclude(type__in=type_ex).order_by('lineno')  
            if not queryset:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Selected Customer Cart is Empty!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if queryset.filter(itemcodeid__item_div__in=[2,3,4,5]).exists():
                result = {'status': status.HTTP_400_BAD_REQUEST,
                "message":"Only Retail Products allow to do Exchange!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


            if queryset.filter(type='Exchange').exists():
                result = {'status': status.HTTP_400_BAD_REQUEST,
                "message":"You are not allow to perform twice Exchange product on the same transactions!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if queryset.filter(type__in=['Top Up','Sales']).exists():
                result = {'status': status.HTTP_400_BAD_REQUEST,
                "message":"You are not allow to perform Exchange when Top Up & Sales cart added!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    

            if serializer.is_valid():
                if queryset:
                    for q in queryset:
                        q.quantity = -abs(q.quantity)
                        q.deposit =  -abs(q.deposit)
                        q.type = "Exchange"
                        q.save()   

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)


            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 
            'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                



class ExchangeProductConfirmAPIView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ExchangeProductSerializer
    
    def create(self, request):
        try:
            global type_ex
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            code_site = site.itemsite_code
            cart_date = timezone.now().date()
            serializer = ExchangeProductSerializer(data=request.data)
            cust_obj = Customer.objects.filter(pk=request.data['cust_id'],cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            queryset = ItemCart.objects.filter(isactive=True,sitecodeid=site,cust_noid=cust_obj,cart_id=request.data['cart_id'],cart_date=cart_date,
            cart_status="Inprogress",is_payment=False).exclude(type__in=type_ex).order_by('lineno')  
            if not queryset:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Selected Customer Cart is Empty!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not queryset.filter(type='Deposit'):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Exchange Product!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


            balance = sum([i.deposit for i in queryset])
            # print(balance,"balance")    

            if balance > 0:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please do payment checkout,Customer Need to pay balance amount!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 


            control_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw.loginsite.pk).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        
            haudre = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('sa_transacno')
            final = list(set([r.sa_transacno for r in haudre]))
            # print(final,len(final),"final")
            saprefix = control_obj.control_prefix

            lst = []
            if final != []:
                for f in final:
                    newstr = f.replace(saprefix,"")
                    new_str = newstr.replace(code_site, "")
                    lst.append(new_str)
                    lst.sort(reverse=True)

                # print(lst,"lst")
                sa_no = int(lst[0][-6:]) + 1
                sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(sa_no)
            else:
                sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                
            paytable = Paytable.objects.filter(pay_code="CS",pay_isactive=True).first()
            gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
            calcgst = 0
            if gst:
                calcgst = gst.item_value
            if calcgst > 0:
                sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                if sitegst:
                    if sitegst.site_is_gst == False:
                        calcgst = 0

            decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
            if not decontrolobj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
            if not con_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            if balance == 0.0:
                taud = PosTaud(sa_transacno=sa_transacno,billed_by=fmspw,ItemSIte_Codeid=site,itemsite_code=site.itemsite_code,
                pay_groupid=paytable.pay_groupid,pay_group=paytable.pay_groupid.pay_group_code,pay_typeid=paytable,pay_type=paytable.pay_code,
                pay_desc=paytable.pay_description,pay_tendamt=0,pay_tendrate=1,pay_amt=0,pay_amtrate=1.0,pay_rem1="Refund",pay_status=1,dt_lineno=1,
                pay_actamt=0,subtotal=0,paychange=0,tax=0, discount_amt=0,billable_amount=0,
                pay_gst_amt_collect=0,pay_gst=0,pay_premise=True).save()
                #print(taud,"taud")

                for idx, c in enumerate(queryset, start=1):

                    sales = "";service = ""
                    if c.sales_staff.all():
                        for i in c.sales_staff.all():
                            if sales == "":
                                sales = sales + i.display_name
                            elif not sales == "":
                                sales = sales +","+ i.display_name
                    if c.service_staff.all(): 
                        for s in c.service_staff.all():
                            if service == "":
                                service = service + s.display_name
                            elif not service == "":
                                service = service +","+ s.display_name 

                    if calcgst > 0:
                        if gst.is_exclusive == True:
                            gst_amt_collect = c.deposit * (calcgst / 100)
                            # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
                        else:
                            # billable_amount = "{:.2f}".format(deposit_amt)
                            gst_amt_collect = c.deposit * calcgst / (100+calcgst)
                    else:
                        gst_amt_collect = 0
                        # billable_amount = "{:.2f}".format(deposit_amt)

                    # gst.item_value
                    # gst_amt_collect = c.deposit * (gst.item_value / 100)

                    sales_staff = c.sales_staff.all().first()
                    salesstaff = c.sales_staff.all()
                    dt_status = "SA"
                    dt_remark = ""
                    depo_type = "Deposit"
                    if c.type == "Exchange":
                        dt_status = "EX"
                        depo_type = "Exchange"
                        dt_remark = sa_transacno
                        # gst_amt_collect = c.deposit * (gst.item_value / 100)

                    dtl = PosDaud(sa_transacno=sa_transacno,dt_status=dt_status,dt_itemnoid=c.itemcodeid,
                    dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=c.itemcodeid.item_name,dt_price=c.price,
                    dt_promoprice="{:.2f}".format(float(c.discount_price)),
                    dt_amt=-float("{:.2f}".format(float(c.trans_amt))) if c.type == "Exchange" else "{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                    dt_discamt=0,dt_discpercent=0,dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                    dt_discuser=None,dt_combocode=c.itemcodeid.item_code,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                    dt_transacamt="{:.2f}".format(float(c.trans_amt)),dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,itemcart=c,
                    st_ref_treatmentcode=None,record_detail_type="PRODUCT",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                    topup_outstanding=0,dt_remark=dt_remark,isfoc=0,item_remarks="",
                    dt_uom=c.item_uom.uom_code if c.item_uom else None,first_trmt_done=False,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                    staffs=sales +" "+"/"+" "+ service)

                    dtl.save()
                    # print(dtl.id,"dtl")

                    #multi staff table creation
                    ratio = 0.0
                    if c.sales_staff.all().count() > 0:
                        count = c.sales_staff.all().count()
                        ratio = float(c.ratio) / float(count)

                    for sale in c.sales_staff.all():
                        multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
                        emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
                        dt_lineno=c.lineno)
                        multi.save()
                        # print(multi.id,"multi")

                    if int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                        desc = "Total Product Amount : "+str("{:.2f}".format(float(c.trans_amt)))
                        #Deposit Account creation
                        
                       
                        treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                        
                        if c.is_foc == True:
                            item_descriptionval = c.itemcodeid.item_name+" "+"(FOC)"
                        else:
                            item_descriptionval = c.itemcodeid.item_name
                        

                        depoacc = DepositAccount(cust_code=cust_obj.cust_code,type=depo_type,amount="{:.2f}".format(float(c.deposit)),
                        balance="{:.2f}".format(float(c.deposit)),user_name=fmspw.pw_userlogin,qty=c.quantity,outstanding=0,
                        deposit="{:.2f}".format(float(c.deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                        sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                        deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                        sa_status=dt_status,item_barcode=str(c.itemcodeid.item_code)+"0000",item_description=item_descriptionval,
                        treat_code=treat_code,void_link=None,lpackage=None,package_code=None,
                        dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                        ref_transacno=sa_transacno,ref_productcode=treat_code,Item_Codeid=c.itemcodeid,
                        item_code=c.itemcodeid.item_code)
                        depoacc.save()
                        # print(depoacc.pk,"depoacc")
                        if depoacc.pk:
                            decontrolobj.control_no = int(decontrolobj.control_no) + 1
                            decontrolobj.save()
                        

                        if c.type != "Exchange":
                            # Inventory Control
                            qtytodeduct = c.quantity
                            if c.holditemqty and int(c.holditemqty) > 0:
                                qtytodeduct = c.quantity - int(c.holditemqty)

                            if qtytodeduct > 0:
                                batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(c.itemcodeid.item_code),
                                uom=c.item_uom.uom_code).order_by('pk').last() 
                                #ItemBatch
                                if batchids:
                                    deduct = batchids.qty - qtytodeduct
                                    batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                                else:
                                    batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                                    batch_no="",uom=c.item_uom.uom_code,qty=-qtytodeduct,exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                                    deduct = -qtytodeduct

                                #Stktrn
                                currenttime = timezone.now()
                                currentdate = timezone.now().date()
                        
                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(c.itemcodeid.item_code)+"0000",
                                item_uom=c.item_uom.uom_code).order_by('pk').last() 

                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,trn_date=currentdate,
                                trn_type="EX",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                                trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                line_no=c.lineno,item_uom=c.item_uom.uom_code,item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None).save()

                        elif c.type == "Exchange":
                            #ItemBatch
                            batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                            item_code=c.itemcodeid.item_code,uom=c.item_uom.uom_code).order_by('pk').last()
                            
                            if batch_ids:
                                addamt = batch_ids.qty + abs(c.quantity)
                                batch_ids.qty = addamt
                                batch_ids.updated_at = timezone.now()
                                batch_ids.save() 
                            else:
                                batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                                batch_no="",uom=c.item_uom.uom_code,qty=abs(c.quantity),exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                                addamt = abs(c.quantity)


                            #Stktrn
                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                            itemcode=c.itemcodeid.item_code+"0000",item_uom=c.item_uom.uom_code).last() 
                            # print(stktrn_ids,"stktrn_ids")

                            currenttime = timezone.now()

                            post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                            itemuom_ids = ItemUomprice.objects.filter(item_code=c.itemcodeid.item_code,item_uom=c.item_uom.uom_code).order_by('pk').first()

                            if stktrn_ids:
                                amt_add = stktrn_ids.trn_balqty + abs(c.quantity)

                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                                itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                                tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                                trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                                trn_qty=abs(c.quantity),trn_balqty=amt_add,trn_balcst=0,
                                trn_amt="{:.2f}".format(float(abs(c.deposit))),
                                trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                                hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                                item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None).save()
                            else:
                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                                itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                                tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                                trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                                trn_qty=abs(c.quantity),trn_balqty=addamt,trn_balcst=0,
                                trn_amt="{:.2f}".format(float(abs(c.deposit))),
                                trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                                hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                                item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None).save()
        
                            

                        #[HoldItemDetail]

                        product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                        
                        hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
                        transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
                        hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                        hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=-c.trans_amt if c.type == 'Exchange' else c.trans_amt,
                        hi_qty=c.quantity,hi_discamt=0,hi_discpercent=0,hi_discdesc=None,
                        hi_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                        hi_lineno=c.lineno,hi_uom=c.item_uom.uom_code,hold_item=False,hi_deposit=c.deposit,
                        holditemqty=0,status="Close",sa_custno=cust_obj.cust_code,
                        sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
                        product_issues_no=product_issues_no)
                        hold.save()
                        # print(hold.pk,"hold")
                        if hold.pk:
                            con_obj.control_no = int(con_obj.control_no) + 1
                            con_obj.save()
                            dtl.holditemqty = 0
                            dtl.save()


                sa_totamt = queryset.exclude(type='Exchange').aggregate(Sum('trans_amt'))
                sa_totqty = queryset.exclude(type='Exchange').aggregate(Sum('quantity'))
                alsales_staff = queryset.first().sales_staff.all().first()
                if alsales_staff:
                    Emp_code = alsales_staff.emp_code
                    Emp_name = alsales_staff.emp_name
                else:
                    alsales_staff = None
                    Emp_code = ""  
                    Emp_name = ""

                nscontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Non Sales No",Site_Codeid__pk=fmspw.loginsite.pk).first()
                if not nscontrol_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Non Sales No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                sa_transacno_refval = str(nscontrol_obj.control_prefix)+str(nscontrol_obj.Site_Codeid.itemsite_code)+str(nscontrol_obj.control_no)
                sa_transacno_type = "Non Sales"
                # tax_amt = balance * (gst.item_value / 100)
                tax_amt = 0

                hdr = PosHaud(cas_name=fmspw.pw_userlogin,sa_transacno=sa_transacno,sa_status="SA",
                sa_totamt="{:.2f}".format(float(sa_totamt['trans_amt__sum'])),sa_totqty=sa_totqty['quantity__sum'],sa_totdisc=None,sa_totgst="{:.2f}".format(float(tax_amt)),
                sa_staffnoid=alsales_staff,sa_staffno=Emp_code,sa_staffname=Emp_name,sa_custnoid=cust_obj,sa_custno=cust_obj.cust_code,
                sa_custname=cust_obj.cust_name,sa_discuser=None,sa_discamt=None,sa_disctotal=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                sa_depositamt="{:.2f}".format(float(balance)),sa_transacamt="{:.2f}".format(float(balance)),sa_round=0,total_outstanding=0,
                trans_user_login=fmspw.pw_password,trans_user_loginid=fmspw,sa_transacno_ref=sa_transacno_refval,sa_transacno_type=sa_transacno_type,
                issuestrans_user_login=fmspw.pw_userlogin)
                
                # appt_time=app_obj.appt_fr_time,
                hdr.save()
                if hdr.pk:
                    nscontrol_obj.control_no = int(nscontrol_obj.control_no) + 1
                    nscontrol_obj.save() 

            
            elif balance < 0.0:
                pay_gst = 0
                # pay_gst = (float(balance) / (100+gst.item_value)) * gst.item_value
                if calcgst > 0:
                    if gst.is_exclusive == True:
                        pay_gst = float(balance) * (calcgst / 100)
                        # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
                    else:
                        # billable_amount = "{:.2f}".format(deposit_amt)
                        pay_gst = float(balance) * calcgst / (100+calcgst)

                if request.data['return_type'] == 'Credit':
                    paytable = Paytable.objects.filter(pay_code="CN",pay_isactive=True).first()

                taud = PosTaud(sa_transacno=sa_transacno,billed_by=fmspw,ItemSIte_Codeid=site,itemsite_code=site.itemsite_code,
                pay_groupid=paytable.pay_groupid,pay_group=paytable.pay_groupid.pay_group_code,pay_typeid=paytable,pay_type=paytable.pay_code,
                pay_desc=paytable.pay_description,pay_tendamt=0 if request.data['return_type'] == 'Forfeit' else "{:.2f}".format(float(balance)),
                pay_tendrate=1,pay_amt=0 if request.data['return_type'] == 'Forfeit' else "{:.2f}".format(float(balance)),pay_amtrate=1,
                pay_rem1="Issue CN" if request.data['return_type'] == 'Credit' else "Forfeit" if request.data['return_type'] == 'Forfeit' else "Refund",
                pay_rem3=request.data['remarks'],pay_status=1,dt_lineno=1,
                pay_actamt=0 if request.data['return_type'] == 'Forfeit' else "{:.2f}".format(float(balance)),subtotal=0,paychange=0,tax=0, discount_amt=0,billable_amount=0,
                pay_gst_amt_collect=0 if request.data['return_type'] == 'Forfeit' else "{:.2f}".format(float(pay_gst)),pay_gst=0 if request.data['return_type'] == 'Forfeit' else "{:.2f}".format(float(pay_gst)),
                pay_premise=True if request.data['return_type'] == 'Cash' else False).save()
                #print(taud,"taud")

                for idx, c in enumerate(queryset, start=1):
    
                    sales = "";service = ""
                    if c.sales_staff.all():
                        for i in c.sales_staff.all():
                            if sales == "":
                                sales = sales + i.display_name
                            elif not sales == "":
                                sales = sales +","+ i.display_name
                    if c.service_staff.all(): 
                        for s in c.service_staff.all():
                            if service == "":
                                service = service + s.display_name
                            elif not service == "":
                                service = service +","+ s.display_name 

                    gst_amt_collect = 0
                    # gst_amt_collect = c.deposit * (gst.item_value / 100)
                    if calcgst > 0:
                        if gst.is_exclusive == True:
                            gst_amt_collect = c.deposit * (calcgst / 100)
                            # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
                        else:
                            # billable_amount = "{:.2f}".format(deposit_amt)
                            gst_amt_collect = c.deposit * calcgst / (100+calcgst)
                    # else:
                        # billable_amount = "{:.2f}".format(deposit_amt)

                    sales_staff = c.sales_staff.all().first()
                    salesstaff = c.sales_staff.all()
                    dt_status = "SA"
                    dt_remark = ""
                    depo_type = "Deposit"
                    if c.type == "Exchange":
                        dt_status = "EX"
                        depo_type = "Exchange"
                        dt_remark = sa_transacno
                        # gst_amt_collect = c.deposit * (gst.item_value / 100)

                    dtl = PosDaud(sa_transacno=sa_transacno,dt_status=dt_status,dt_itemnoid=c.itemcodeid,
                    dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=c.itemcodeid.item_name,dt_price=c.price,
                    dt_promoprice="{:.2f}".format(float(c.discount_price)),
                    dt_amt=-float("{:.2f}".format(float(c.trans_amt))) if c.type == "Exchange" else "{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                    dt_discamt=0,dt_discpercent=0,dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                    dt_discuser=None,dt_combocode=c.itemcodeid.item_code,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                    dt_transacamt="{:.2f}".format(float(c.trans_amt)),dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,itemcart=c,
                    st_ref_treatmentcode=None,record_detail_type="PRODUCT",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                    topup_outstanding=0,dt_remark=dt_remark,isfoc=0,item_remarks="",
                    dt_uom=c.item_uom.uom_code if c.item_uom else None,first_trmt_done=False,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                    staffs=sales +" "+"/"+" "+ service)

                    dtl.save()
                    # print(dtl.id,"dtl")

                    #multi staff table creation
                    ratio = 0.0
                    if c.sales_staff.all().count() > 0:
                        count = c.sales_staff.all().count()
                        ratio = float(c.ratio) / float(count)

                    for sale in c.sales_staff.all():
                        multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
                        emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
                        dt_lineno=c.lineno)
                        multi.save()
                        # print(multi.id,"multi")

                    if int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                        desc = "Total Product Amount : "+str("{:.2f}".format(float(c.trans_amt)))
                        #Deposit Account creation
                        
                        decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                        if not decontrolobj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                        
                        if c.is_foc == True:
                            item_descriptionval = c.itemcodeid.item_name+" "+"(FOC)"
                        else:
                            item_descriptionval = c.itemcodeid.item_name
                        

                        depoacc = DepositAccount(cust_code=cust_obj.cust_code,type=depo_type,amount="{:.2f}".format(float(c.deposit)),
                        balance="{:.2f}".format(float(c.deposit)),user_name=fmspw.pw_userlogin,qty=c.quantity,outstanding=0,
                        deposit="{:.2f}".format(float(c.deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                        sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                        deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                        sa_status=dt_status,item_barcode=str(c.itemcodeid.item_code)+"0000",item_description=item_descriptionval,
                        treat_code=treat_code,void_link=None,lpackage=None,package_code=None,
                        dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                        ref_transacno=sa_transacno,ref_productcode=treat_code,Item_Codeid=c.itemcodeid,
                        item_code=c.itemcodeid.item_code)
                        depoacc.save()
                        # print(depoacc.pk,"depoacc")
                        if depoacc.pk:
                            decontrolobj.control_no = int(decontrolobj.control_no) + 1
                            decontrolobj.save()

                        if c.type != "Exchange":
                            # Inventory Control
                            qtytodeduct = c.quantity
                            if c.holditemqty and int(c.holditemqty) > 0:
                                qtytodeduct = c.quantity - int(c.holditemqty)

                            if qtytodeduct > 0:
                                batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(c.itemcodeid.item_code),
                                uom=c.item_uom.uom_code).order_by('pk').last() 
                                #ItemBatch
                                if batchids:
                                    deduct = batchids.qty - qtytodeduct
                                    batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                                else:
                                    batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                                    batch_no="",uom=c.item_uom.uom_code,qty=-qtytodeduct,exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                                    deduct = -qtytodeduct

                                #Stktrn
                                currenttime = timezone.now()
                                currentdate = timezone.now().date()
                        
                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(c.itemcodeid.item_code)+"0000",
                                item_uom=c.item_uom.uom_code).order_by('pk').last() 

                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                                store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,trn_date=currentdate,
                                trn_type="EX",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                                trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                                trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                                trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                                hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                                line_no=c.lineno,item_uom=c.item_uom.uom_code,item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None).save()

                        elif c.type == "Exchange":
                            #ItemBatch
                            batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                            item_code=c.itemcodeid.item_code,uom=c.item_uom.uom_code).order_by('pk').last()
                            
                            if batch_ids:
                                addamt = batch_ids.qty + abs(c.quantity)
                                batch_ids.qty = addamt
                                batch_ids.updated_at = timezone.now()
                                batch_ids.save() 
                            else:
                                batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                                batch_no="",uom=c.item_uom.uom_code,qty=abs(c.quantity),exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                                addamt = abs(c.quantity)                      
                

                            #Stktrn
                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                            itemcode=c.itemcodeid.item_code,item_uom=c.item_uom.uom_code).last() 
                            # print(stktrn_ids,"stktrn_ids")

                            currenttime = timezone.now()

                            post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                            itemuom_ids = ItemUomprice.objects.filter(item_code=c.itemcodeid.item_code,item_uom=c.item_uom.uom_code).order_by('pk').first()

                            if stktrn_ids:
                                amt_add = stktrn_ids.trn_balqty + abs(c.quantity)

                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                                itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                                tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                                trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                                trn_qty=abs(c.quantity),trn_balqty=amt_add,trn_balcst=0,
                                trn_amt="{:.2f}".format(float(abs(c.deposit))),
                                trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                                hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                                item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None).save()
                            else:
                                stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                                itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                                tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                                trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                                trn_qty=abs(c.quantity),trn_balqty=addamt,trn_balcst=0,
                                trn_amt="{:.2f}".format(float(abs(c.deposit))),
                                trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                                hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                                item_batch=None,mov_type=None,item_batch_cost=None,
                                stock_in=None,trans_package_line_no=None).save()
            
     
                        #[HoldItemDetail]

                        product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                        
                        hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
                        transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
                        hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                        hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=-c.trans_amt if c.type == 'Exchange' else c.trans_amt,
                        hi_qty=c.quantity,hi_discamt=0,hi_discpercent=0,hi_discdesc=None,
                        hi_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                        hi_lineno=c.lineno,hi_uom=c.item_uom.uom_code,hold_item=False,hi_deposit=c.deposit,
                        holditemqty=0,status="Close",sa_custno=cust_obj.cust_code,
                        sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
                        product_issues_no=product_issues_no)
                        hold.save()
                        # print(hold.pk,"hold")
                        if hold.pk:
                            con_obj.control_no = int(con_obj.control_no) + 1
                            con_obj.save()
                            dtl.holditemqty = 0
                            dtl.save()

                        
                sa_totamt = queryset.exclude(type='Exchange').aggregate(Sum('trans_amt'))
                sa_totqty = queryset.exclude(type='Exchange').aggregate(Sum('quantity'))
                alsales_staff = queryset.first().sales_staff.all().first()
                if alsales_staff:
                    Emp_code = alsales_staff.emp_code
                    Emp_name = alsales_staff.emp_name
                else:
                    alsales_staff = None
                    Emp_code = ""  
                    Emp_name = ""
                
                if request.data['return_type'] == 'Cash':   

                    rfcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Refund No",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not rfcontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Refund No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                    sa_transacno_refval = str(rfcontrol_obj.control_prefix)+str(rfcontrol_obj.Site_Codeid.itemsite_code)+str(rfcontrol_obj.control_no)
                    sa_transacno_type = "Refund"

                elif request.data['return_type'] == 'Credit':

                    cncontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Credit Note No",Site_Codeid=site).first()
                    if not cncontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Credit Note Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                    sa_transacno_refval = str(cncontrol_obj.control_prefix)+str(cncontrol_obj.Site_Codeid.itemsite_code)+str(cncontrol_obj.control_no)
                    sa_transacno_type = "Credit Note"

                    #creditnote creation  
                    creditnote = CreditNote(treatment_code="",treatment_name="",amount="{:.2f}".format(abs(balance)),
                    treatment_parentcode="",type="Exchange",cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name,
                    sa_transacno=sa_transacno,status="OPEN",credit_code=sa_transacno_refval,balance="{:.2f}".format(abs(balance)),
                    deposit_type=None,site_code=site.itemsite_code,treat_code=None)
                    creditnote.save()

                elif request.data['return_type'] == 'Forfeit':
                    nscontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Non Sales No",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not nscontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Non Sales No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                    sa_transacno_refval = str(nscontrol_obj.control_prefix)+str(nscontrol_obj.Site_Codeid.itemsite_code)+str(nscontrol_obj.control_no)
                    sa_transacno_type = "Non Sales"

                # tax_amt = balance * (gst.item_value / 100)
                tax_amt = 0

                hdr = PosHaud(cas_name=fmspw.pw_userlogin,sa_transacno=sa_transacno,sa_status="SA",
                sa_totamt="{:.2f}".format(float(sa_totamt['trans_amt__sum'])),sa_totqty=sa_totqty['quantity__sum'],sa_totdisc=None,sa_totgst="{:.2f}".format(float(tax_amt)),
                sa_staffnoid=alsales_staff,sa_staffno=Emp_code,sa_staffname=Emp_name,sa_custnoid=cust_obj,sa_custno=cust_obj.cust_code,
                sa_custname=cust_obj.cust_name,sa_discuser=None,sa_discamt=None,sa_disctotal=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                sa_depositamt="{:.2f}".format(float(balance)),sa_transacamt="{:.2f}".format(float(balance)),sa_round=0,total_outstanding=0,
                trans_user_login=fmspw.pw_password,trans_user_loginid=fmspw,sa_transacno_ref=sa_transacno_refval,sa_transacno_type=sa_transacno_type,
                issuestrans_user_login=fmspw.pw_userlogin)
                
                # appt_time=app_obj.appt_fr_time,
                hdr.save()
                if hdr.pk:
                    if request.data['return_type'] == 'Cash':   
                        rfcontrol_obj.control_no = int(rfcontrol_obj.control_no) + 1
                        rfcontrol_obj.save() 

                    elif request.data['return_type'] == 'Credit': 
                        cncontrol_obj.control_no = int(cncontrol_obj.control_no) + 1
                        cncontrol_obj.save() 

                    elif request.data['return_type'] == 'Forfeit':
                        nscontrol_obj.control_no = int(nscontrol_obj.control_no) + 1
                        nscontrol_obj.save() 

            for ci in queryset:
                ci.is_payment = True
                ci.cart_status = "Completed"
                ci.sa_transacno = sa_transacno
                ci.save()    

            # serializer_final.data
            result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",'error': False, 
            'data': {'sa_transacno':sa_transacno}}
            return Response(result, status=status.HTTP_201_CREATED)            
        
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


class SmtpSettingsViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = SmtpSettings.objects.filter().order_by('-pk')
    serializer_class = SmtpSettingsSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = SmtpSettings.objects.none()
        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = SmtpSettings.objects.filter().order_by('-pk')
       
        return queryset

    def list(self, request):
        try:
            serializer_class = SmtpSettingsSerializer
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
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            serializer = SmtpSettingsSerializer(data=request.data)
            if serializer.is_valid():
                siteobj = ItemSitelist.objects.filter(pk=request.data['site_codeid'],itemsite_isactive=True).first()
                serializer.save(site_codeid=siteobj,site_code=siteobj.itemsite_code)
                result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_201_CREATED)
            
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
            'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def get_object(self, pk):
        try:
            return SmtpSettings.objects.get(pk=pk)
        except SmtpSettings.DoesNotExist:
            raise Exception('SmtpSettings Does not Exist') 

    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            smtp = self.get_object(pk)
            serializer = SmtpSettingsSerializer(smtp, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 
    
    
    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            smtp = self.get_object(pk)

            serializer = self.get_serializer(smtp, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_at=timezone.now())

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   


    def destroy(self, request, pk=None):
        smtp = self.get_object(pk)
        smtp.delete()
        result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
        return Response(result, status=status.HTTP_200_OK)

             
class CartPopupViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ItemCart.objects.filter(isactive=True).order_by('-id')
    serializer_class = CartItemStatusSerializer


    def get_serializer_class(self):
        if self.request.GET.get('is_staffs',None) and int(self.request.GET.get('is_staffs',None)) == 1:
            return CartStaffsSerializer
        else:
            return CartItemStatusSerializer    
       
             
    def get_queryset(self):
        type_ex = ['VT-Deposit','VT-Top Up','VT-Sales']
        request = self.request
        cart_date = timezone.now().date()
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
       
        site = fmspw[0].loginsite
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
        cart_id = request.GET.get('cart_id',None)

        # is_product = request.GET.get('is_product',None)
        # print(type(is_product),"is_product")
        
        
        if fmspw[0].flgsales == True:
            if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
                queryset = ItemCart.objects.filter(isactive=True).order_by('id')
            elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [31,27]:
                queryset = ItemCart.objects.filter(isactive=True,sitecodeid=site).order_by('id')
            
           
            if request.GET.get('is_product',None) and int(request.GET.get('is_product',None)) == 1:
                type_ex.extend(['Sales','Exchange','Top Up'])
                queryset = queryset.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
                cart_status="Inprogress",isactive=True,is_payment=False,itemcodeid__item_div=1).exclude(type__in=type_ex).order_by('lineno')  
            if request.GET.get('is_status',None) and int(request.GET.get('is_status',None)) == 1:
                type_ex.extend(['Sales','Exchange'])
                queryset = queryset.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
                cart_status="Inprogress",isactive=True,is_payment=False).exclude(type__in=type_ex).order_by('lineno')  
            if request.GET.get('is_staffs',None) and int(request.GET.get('is_staffs',None)) == 1:
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
            queryset = self.filter_queryset(self.get_queryset())
            if not queryset:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
                
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,
                'data': serializer.data}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   

    
    def create(self, request):
        try:
            if request.data:
                for idx, req in enumerate(request.data, start=1):
                    cartobj = ItemCart.objects.filter(id=req['id']).first()
                    if not cartobj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sent Valid Cart ID",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                    if req['itemstatus']:
                        statusobj = ItemStatus.objects.filter(pk=req['itemstatus'],itm_isactive=True).first()
                        if statusobj:
                            cartobj.itemstatus = statusobj
                            cartobj.save()

                    if req['focreason'] and cartobj.type != 'Top Up' and cartobj.is_foc == True:
                        if cartobj.itemcodeid.item_div != 5 and cartobj.itemcodeid.is_allow_foc == True and cartobj.itemcodeid.disclimit == 100.00:
                            focobj = FocReason.objects.filter(pk=req['focreason'],foc_reason_isactive=True).first()
                            if focobj:
                                cartobj.focreason = focobj
                                cartobj.save()

                result = {'status': status.HTTP_200_OK,"message":"Updated Sucessfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   


    @action(detail=False, methods=['post'], name='product')
    def product(self, request):
        try:  
            if request.data:
                for idx, req in enumerate(request.data, start=1):
                    itemcart = ItemCart.objects.filter(id=req['id']).first()
                    # print(itemcart,"itemcart")
                    if not itemcart:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sent Valid Cart ID",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    trans_amt = itemcart.trans_amt    

                    if req['quantity'] and req['quantity'] != 0.0:
                        # float(request.data['discount_amt']))
                        if not int(itemcart.itemcodeid.item_div) in [4,5]: 
                            total_price = float(req['price']) * int(req['quantity'])
                            after_linedisc = (float(req['price']) - float(itemcart.discount_amt)) * int(req['quantity'])
                            trans_amt = after_linedisc - float(itemcart.additional_discountamt)
                            deposit = after_linedisc - float(itemcart.additional_discountamt)
                            if itemcart.is_foc == True:
                                itemcart.quantity = req['quantity']
                                itemcart.total_price = total_price
                                itemcart.save()
                            else:
                                itemcart.quantity = req['quantity']
                                itemcart.total_price = total_price
                                itemcart.trans_amt = trans_amt
                                itemcart.deposit = deposit
                                itemcart.save()

                   
                    if req['price'] and float(req['price']) > 0.0 and itemcart.is_foc == False:
                        total_disc = itemcart.discount_amt + itemcart.additional_discountamt
                        if not int(itemcart.itemcodeid.item_div) in [4,5]: 
                            total_price = float(req['price']) * int(req['quantity'])
                            discount_price = float(req['price']) - total_disc
                            after_linedisc = (float(req['price']) - float(itemcart.discount_amt)) * int(req['quantity'])
                            trans_amt = after_linedisc - float(itemcart.additional_discountamt)
                            deposit = after_linedisc - float(itemcart.additional_discountamt)

                            itemcart.price = req['price']
                            itemcart.total_price = total_price
                            itemcart.discount_price = discount_price
                            itemcart.trans_amt = trans_amt
                            itemcart.deposit = deposit
                            itemcart.save()


                    if 'deposit' in req and req['deposit'] and float(req['deposit']) > 0.0 and  itemcart.is_foc == False:
                        if int(float(req['deposit'])) < int(trans_amt):
                            if int(itemcart.itemcodeid.item_div) != 4:
                                itemcart.deposit = req['deposit']
                                
                    if req['holdreason'] and req['holditemqty'] > 0:
                        holdobj = HolditemSetup.objects.filter(pk=req['holdreason']).first()
                        itemcart.holdreason = holdobj
                        itemcart.save()
                    
                    if req['holditemqty'] and req['holditemqty'] > 0:
                        if req['holditemqty'] <= req['quantity']: 
                            itemcart.holditemqty = req['holditemqty']
                            itemcart.save()


                result = {'status': status.HTTP_200_OK,"message":"Updated Sucessfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


    def get_object(self, pk):
        try:
            return ItemCart.objects.get(pk=pk)
        except ItemCart.DoesNotExist:
            raise Exception('ItemCart Does not Exist') 


    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            cart = self.get_object(pk)
            if cart.type in ['Top Up','Sales','Exchange']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if int(cart.itemcodeid.item_div) in [4,5] or cart.is_foc == True:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Discount is not applicable",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            serializer = CartDiscountSerializer(cart, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 
              

    def partial_update(self, request, pk=None):
        try:
            itemcart = self.get_object(pk)
            if itemcart.type in ['Top Up','Sales','Exchange']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if itemcart.is_foc == True:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give edit.",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
            if request.data['deposit'] and float(request.data['deposit']) > 0.0:
                if int(itemcart.itemcodeid.item_div) == 4:
                    if float(itemcart.deposit) != float(request.data['deposit']):
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit can't be changed for Voucher Product!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                if float(request.data['deposit']) > itemcart.trans_amt:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit should not be greater than transaction amount!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                if itemcart.is_foc == True:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FOC could not give Deposit.",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
                if int(itemcart.itemcodeid.item_div) != 4:
                    itemcart.deposit = request.data['deposit']
                    itemcart.save()
                    
                result = {'status': status.HTTP_200_OK,"message":"Updated Sucessfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   


    @action(detail=False, methods=['post'], name='staffs')
    def staffs(self, request):
        try:  
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            if request.data:
                for idx, req in enumerate(request.data, start=1):
                    itemcart = ItemCart.objects.filter(id=req['id']).first()
                    # print(itemcart.pk,itemcart.type,"itemcart")
                    if not itemcart:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sent Valid Cart ID",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    for s in req['data']:
                        if s['work'] == True:
                            if s['work_percentage'] == "":
                                raise Exception('Work Percentage Should not be empty') 
                            if s['work_amount'] == "":
                                raise Exception('work Amount Should not be empty') 
                            if s['wp'] == "":
                                raise Exception('wp Should not be empty') 

                        if s['sales'] == True:
                            if s['sales_percentage'] == "":
                                raise Exception('Sales Percentage Should not be empty') 
                            if s['sales_amount'] == "":
                                raise Exception('Sales Amount Should not be empty') 
                            if s['sp'] == "":
                                raise Exception('sp Should not be empty') 


                    if itemcart.type == 'Deposit' and int(itemcart.itemcodeid.item_div) == 3:
                        for i, s in enumerate(req['data'], start=1):
                            if s['work'] == True:
                                if s['tmp_workid']:
                                    TmpItemHelper.objects.filter(id=s['tmp_workid']).update(
                                    percent=s['work_percentage'],work_amt=s['work_amount'],wp1=s['wp'])
                                elif s['tmp_workid'] == None:
                                    helper_obj = Employee.objects.filter(emp_isactive=True,pk=s['emp_id']).first()
                                    
                                    if helper_obj: 
                                        obj_ids = TmpItemHelper.objects.filter(itemcart=itemcart,helper_id__pk=helper_obj.pk)
                                        
                                        if not obj_ids:
                                            # print("if")
                                            temph = TmpItemHelper(item_name=itemcart.itemcodeid.item_desc,helper_id=helper_obj,
                                            helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,
                                            site_code=site.itemsite_code,times=str(itemcart.quantity).zfill(2),
                                            treatment_no=str(itemcart.quantity).zfill(2),wp1=s['wp'],wp2=0.0,wp3=0.0,itemcart=itemcart,
                                            percent=s['work_percentage'],work_amt=s['work_amount']) 
                                            temph.save() 

                            if s['sales'] == True: 
                                if s['tmp_saleid']:
                                    Tmpmultistaff.objects.filter(id=s['tmp_saleid']).update(
                                    ratio=s['sales_percentage'],salesamt=s['sales_amount'],salescommpoints=s['sp'])
                                elif s['tmp_saleid'] == None:
                                    emp_obj = Employee.objects.filter(emp_isactive=True,pk=s['emp_id']).first()
                                    if emp_obj:
                                        objids = Tmpmultistaff.objects.filter(itemcart=itemcart,
                                        emp_id__pk=emp_obj.pk)
                                        
                                        if not objids:
                                            tmpmulti = Tmpmultistaff(item_code=itemcart.itemcodeid.item_code,
                                            emp_code=emp_obj.emp_code,ratio=s['sales_percentage'],
                                            salesamt="{:.2f}".format(float(s['sales_amount'])),type=None,isdelete=False,role=1,
                                            dt_lineno=itemcart.lineno,itemcart=itemcart,emp_id=emp_obj,salescommpoints=s['sp'])
                                            tmpmulti.save()


                        tmpids = TmpItemHelper.objects.filter(itemcart=itemcart).order_by('pk').aggregate(Sum('wp1'))
                        if tmpids['wp1__sum']:
                            value ="{:.2f}".format(float(tmpids['wp1__sum']))
                            tmp_ids = TmpItemHelper.objects.filter(itemcart=itemcart).order_by('pk').update(workcommpoints=value)
            
                        
                    elif itemcart.type == 'Sales' and int(itemcart.itemcodeid.item_div) == 3:
                       
                        for i, s in enumerate(req['data'], start=1):
                            if s['work'] == True:
                                if s['tmp_workid']:
                                    TmpItemHelper.objects.filter(id=s['tmp_workid']).update(
                                    percent=s['work_percentage'],work_amt=s['work_amount'],wp1=s['wp'])
                                elif s['tmp_workid'] == None:
                                    helper_obj = Employee.objects.filter(emp_isactive=True,pk=s['emp_id']).first()
                                    
                                    if helper_obj: 
                                        obj_ids = TmpItemHelper.objects.filter(treatment=itemcart.treatment,
                                        helper_id__pk=helper_obj.pk)
                                        
                                        if not obj_ids:
                                            temph = TmpItemHelper(item_name=itemcart.itemcodeid.item_desc,helper_id=helper_obj,
                                            helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,
                                            site_code=site.itemsite_code,times=itemcart.treatment.times,treatment_no=itemcart.treatment.treatment_no,
                                            wp1=s['wp'],wp2=0.0,wp3=0.0,itemcart=None,treatment=itemcart.treatment,
                                            percent=s['work_percentage'],work_amt=s['work_amount'])
                                            temph.save()

                        tmpids = TmpItemHelper.objects.filter(treatment=itemcart.treatment).order_by('pk').aggregate(Sum('wp1'))
                        if tmpids['wp1__sum']:
                            value ="{:.2f}".format(float(tmpids['wp1__sum']))
                            tmp_ids = TmpItemHelper.objects.filter(treatment=itemcart.treatment).order_by('pk').update(workcommpoints=value)
            

                    elif itemcart.type in ['Deposit','Top Up','Exchange'] and int(itemcart.itemcodeid.item_div) != 3:
                        for i, sa in enumerate(req['data'], start=1):
                            if sa['sales'] == True:
                                if sa['tmp_saleid']:
                                    Tmpmultistaff.objects.filter(id=sa['tmp_saleid']).update(
                                    ratio=sa['sales_percentage'],salesamt=sa['sales_amount'],salescommpoints=sa['sp'])
                                elif sa['tmp_saleid'] == None:
                                    emp_obj = Employee.objects.filter(emp_isactive=True,pk=sa['emp_id']).first()
                                    if emp_obj:
                                        objids = Tmpmultistaff.objects.filter(itemcart=itemcart,
                                        emp_id__pk=emp_obj.pk)
                                        
                                        if not objids:
                                            tmpmulti = Tmpmultistaff(item_code=itemcart.itemcodeid.item_code,
                                            emp_code=emp_obj.emp_code,ratio=sa['sales_percentage'],
                                            salesamt="{:.2f}".format(float(sa['sales_amount'])),type=None,isdelete=False,role=1,
                                            dt_lineno=itemcart.lineno,itemcart=itemcart,emp_id=emp_obj,salescommpoints=sa['sp'])
                                            tmpmulti.save()


                result = {'status': status.HTTP_200_OK,"message":"Updated Sucessfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

             
    @action(detail=False, methods=['post'], name='staffsdelete')
    def staffsdelete(self, request):
        try:  
            if request.data:
                if not request.data['cart_id']:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                cartobj = ItemCart.objects.filter(pk=request.data['cart_id']).first()
                if not cartobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if not request.data['tmp_saleid'] and not request.data['tmp_workid']:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sale or work!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if request.data['sales'] == True and request.data['tmp_saleid']:
                    tids = Tmpmultistaff.objects.filter(id=request.data['tmp_saleid'])
                    if not tids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sales id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    Tmpmultistaff.objects.filter(id=request.data['tmp_saleid']).delete()

                if request.data['work'] == True and request.data['tmp_workid']:
                    t_ids = TmpItemHelper.objects.filter(id=request.data['tmp_workid'])
                    if not t_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Work id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
 
                    TmpItemHelper.objects.filter(id=request.data['tmp_workid']).delete() 
                
                result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
                return Response(data=result, status=status.HTTP_200_OK)
     
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)



class CartServiceCourseViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ItemCart.objects.filter(isactive=True).order_by('-id')
    serializer_class = CartServiceCourseSerializer

    def get_object(self, pk):
        #try:
            return ItemCart.objects.get(pk=pk)
        #except ItemCart.DoesNotExist:
        #    raise Exception('ItemCart Does not Exist') 

    def retrieve(self, request, pk=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            cart = self.get_object(pk)
            if (cart.type == 'Deposit' and int(cart.itemcodeid.item_div) != 3) or (cart.type in ['Top Up','Sales','Exchange']) or (cart.type == 'Deposit' and int(cart.itemcodeid.item_div) == 3 and cart.is_foc == True):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Service Course is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            serializer = CartServiceCourseSerializer(cart, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)

        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message) 


    @action(detail=False, methods=['post'], name='reset')
    def reset(self, request):
        # try:    
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            if not request.data['cart_id']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            cartobj = ItemCart.objects.filter(pk=request.data['cart_id']).first()
            if not cartobj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            if cartobj:
                tmpids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk').delete()

                trascamt = cartobj.price * 1
                ItemCart.objects.filter(id=cartobj.id).update(discount=0.0,discount_amt=0.0,
                additional_discount=0.0,additional_discountamt=0.0,quantity=1,
                discount_price=cartobj.price,deposit=trascamt,trans_amt=trascamt,is_total=False)
                for existing in cartobj.disc_reason.all():
                    cartobj.disc_reason.remove(existing) 

                cartobj.pos_disc.all().filter(istransdisc=False,dt_status='New').delete()
                cartobj.pos_disc.all().filter().delete()


                result = {'status': status.HTTP_200_OK,"message":"Reset Succesfully",'error': False}
                return Response(data=result, status=status.HTTP_200_OK)

        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message) 


    def partial_update(self, request, pk=None):
        # try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            empl = fmspw.Emp_Codeid
            cart = self.get_object(pk)

            if int(request.data['free_sessions']) > int(request.data['quantity']) or int(request.data['free_sessions']) > request.data['treatment_no']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Free Sessions should not greater than quantity/treatment_no ",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(cart, data=request.data, partial=True)
            if serializer.is_valid():
                # total_price = request.data['treatment_no'] * request.data['price']
                trans_amt = request.data['trans_amt']
                if request.data['deposit'] > trans_amt:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Deposit should not greater than transac amount",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_200_OK)  

        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)     
        
        

class CourseTmpAPIView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Tmptreatment.objects.filter().order_by('-pk')
    serializer_class = CourseTmpSerializer


    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            if not request.data['cart_id']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            cartobj = ItemCart.objects.filter(pk=request.data['cart_id']).first()
            if not cartobj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            if cartobj:
                if cartobj.is_foc == True:
                    course_val = cartobj.itemcodeid.item_name +" "+"(FOC)"
                    isfoc_val = True
                else:
                    course_val = cartobj.itemcodeid.item_name 
                    isfoc_val = False

                # print(request.data,"request.data")    
                serializer = CourseTmpSerializer(data=request.data)
                if serializer.is_valid():
                
                    if request.data['treatment_no']:
                        price = request.data['treatment_no'] * cartobj.discount_price

                        checkids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk').first()

                        if checkids:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already created,Reset & Try!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                        check = list(range(1, int(request.data['free_sessions'])+1))
                        treat_val = request.data['treatment_no'] + request.data['free_sessions']

                        date_lst = []
                        cnt = 1
                        while cnt <= treat_val:
                            if date_lst == []:
                                current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d").strftime("%Y-%m-%d")
                                # next_date = current_date + relativedelta(days=7)
                                # nextdate = datetime.datetime.strptime(str(next_date), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                                date_lst.append(current_date)
                            else:
                                date_1 = datetime.datetime.strptime(str(date_lst[-1]), "%Y-%m-%d")
                                end_date = (date_1 + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
                                date_lst.append(end_date)

                            cnt+=1
                        
                        # print(date_lst,"date_lst") 
                        
                        cnt = 0
                        for i in range(treat_val, 0, -1):
                            times = str(i).zfill(2)
                            unit_amount = cartobj.discount_price

                            if i in check:
                                unit_amount = 0.0
                                isfoc_val = True
                                course_val = cartobj.itemcodeid.item_name +" "+"(FOC)"
                                price = 0

                            treatmentid = Tmptreatment(course=course_val,times=times,
                            treatment_no=str(treat_val).zfill(2),price="{:.2f}".format(float(price)),
                            next_appt=date_lst[cnt],cust_code=cartobj.cust_noid.cust_code,
                            cust_name=cartobj.cust_noid.cust_name,
                            unit_amount="{:.2f}".format(float(unit_amount)),
                            status="Open",item_code=str(cartobj.itemcodeid.item_code)+"0000",
                            sa_status="SA",type="N",trmt_is_auto_proportion=False,
                            dt_lineno=cartobj.lineno,site_code=site.itemsite_code,isfoc=isfoc_val,
                            itemcart=cartobj)
                            treatmentid.save()
                            cnt += 1

                        tmpids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk')

                        data = [{'slno': i,'program': c.course,
                        'next_appt': datetime.datetime.strptime(str(c.next_appt), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") ,
                        'unit_amount': "{:.2f}".format(c.unit_amount)} 
                        for i, c in enumerate(tmpids, start=1)]
                    
                        result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                        'error': False,'data': data}

                        return Response(result, status=status.HTTP_201_CREATED)

                    if request.data['total_price']:
                        if request.data['auto'] == False:
                            treatmentno = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk').count()
                            unit_amount = float(request.data['total_price']) / int(treatmentno)


                            tmp_treatids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk'
                            ).update(price="{:.2f}".format(float(request.data['total_price'])),
                            unit_amount="{:.2f}".format(unit_amount),trmt_is_auto_proportion=False)

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk'
                            ).update(price=0,unit_amount=0.00,trmt_is_auto_proportion=False)

                        elif request.data['auto'] == True:
                            treatmentno = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk').count()
                            # print(treatmentno,"treatmentno")
                            unit_amount = float(request.data['total_price']) / int(treatmentno)
                            # print(unit_amount,"unit_amount")

                            tmp_treatids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk'
                            ).update(price="{:.2f}".format(float(request.data['total_price'])),
                            unit_amount="{:.2f}".format(unit_amount),trmt_is_auto_proportion=True)
                            
                            l_ids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk').last()

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk'
                            ).exclude(pk=l_ids.pk).update(price=0,unit_amount="{:.2f}".format(unit_amount),trmt_is_auto_proportion=True)
                             
                            amt = "{:.2f}".format(float(unit_amount)) 
                            # print(amt,"amt")  
                            # print(request.data['total_price'],"hh")
                            lval = float(request.data['total_price']) - (float(amt) * (treatmentno -1))
                            # print(lval,"lval")

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True,pk=l_ids.pk).order_by('pk'
                            ).update(price=0,unit_amount="{:.2f}".format(float(lval)),trmt_is_auto_proportion=True)


                            
                        tmp_ids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk')

                        cartobj.is_total = True
                        cartobj.save()

                        data = [{'slno': i,'program': c.course,
                        'next_appt': datetime.datetime.strptime(str(c.next_appt), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") ,
                        'unit_amount': "{:.2f}".format(c.unit_amount)} 
                        for i, c in enumerate(tmp_ids, start=1)]

                        result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False
                        ,'data': data}
                        return Response(result, status=status.HTTP_200_OK)

                    if request.data['disc_amount'] and request.data['unit_price']:
                        tmpobj = Tmptreatment.objects.filter(itemcart=cartobj).order_by('-pk').first()
                        val = float(request.data['unit_price']) * int(tmpobj.treatment_no)
                        price = val - float(request.data['disc_amount'])
                        unit_amount = float(price) / int(tmpobj.treatment_no)

                        tmp_treatids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk'
                        ).update(price="{:.2f}".format(float(price)),
                        unit_amount=unit_amount)

                        Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk'
                        ).update(price="{:.2f}".format(float(price)))


                        tmp_ids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk')

                        data = [{'slno': i,'program': c.course,
                        'next_appt': datetime.datetime.strptime(str(c.next_appt), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") ,
                        'unit_amount': "{:.2f}".format(c.unit_amount)} 
                        for i, c in enumerate(tmp_ids, start=1)]

                        result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False
                        ,'data': data}
                        return Response(result, status=status.HTTP_200_OK)

                    if request.data['disc_percent'] and request.data['unit_price']:
                        tmpobj = Tmptreatment.objects.filter(itemcart=cartobj).order_by('-pk').first()
                        total_price = float(request.data['unit_price']) * int(tmpobj.treatment_no)
                        value = total_price * (int(request.data['disc_percent']) / 100)
                        price = total_price - float(value)
                        unit_amount = float(price) / int(tmpobj.treatment_no)

                        tmp_treatids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk'
                        ).update(price="{:.2f}".format(float(price)),
                        unit_amount=unit_amount)

                        Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk'
                        ).update(price="{:.2f}".format(float(price)))


                        tmp_ids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk')

                        data = [{'slno': i,'program': c.course,
                        'next_appt': datetime.datetime.strptime(str(c.next_appt), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") ,
                        'unit_amount': "{:.2f}".format(c.unit_amount)} 
                        for i, c in enumerate(tmp_ids, start=1)]

                        result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False
                        ,'data': data}
                        return Response(result, status=status.HTTP_200_OK)

                    if request.data['auto_propation']:
                        # print(type(request.data['auto_propation']),"jj")
                        if request.data['auto_propation'] == "False":
                            # print("False")
                            number = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk').count()
                            tmp_ids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk').last()
                            unit_amount = tmp_ids.price / number

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk'
                            ).update(unit_amount="{:.2f}".format(float(unit_amount)),trmt_is_auto_proportion=False)

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk'
                            ).update(unit_amount=0.0,trmt_is_auto_proportion=False)

                            tmp_ids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk')

                            data = [{'slno': i,'program': c.course,
                            'next_appt': datetime.datetime.strptime(str(c.next_appt), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") ,
                            'unit_amount': "{:.2f}".format(c.unit_amount)} 
                            for i, c in enumerate(tmp_ids, start=1)]

                            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False
                            ,'data': data}
                            return Response(result, status=status.HTTP_200_OK)


                        elif request.data['auto_propation'] == "True": 
                            # print("True")
                            number = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk').count()
                            tmp_ids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk').last()
                            unit_amount = tmp_ids.price / number

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=False).order_by('pk'
                            ).update(unit_amount="{:.2f}".format(float(unit_amount)),trmt_is_auto_proportion=True)

                           
                            l_ids = Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk').last()

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True).order_by('pk'
                            ).exclude(pk=l_ids.pk).update(price=0,unit_amount="{:.2f}".format(float(unit_amount)),trmt_is_auto_proportion=True)

                            amt = "{:.2f}".format(float(unit_amount))  
                            lval = float(tmp_ids.price) - (float(amt) * (number -1))

                            Tmptreatment.objects.filter(itemcart=cartobj,isfoc=True,pk=l_ids.pk).order_by('pk'
                            ).update(price=0,unit_amount="{:.2f}".format(float(lval)),trmt_is_auto_proportion=True)


                            tmp_ids = Tmptreatment.objects.filter(itemcart=cartobj).order_by('pk')

                            data = [{'slno': i,'program': c.course,
                            'next_appt': datetime.datetime.strptime(str(c.next_appt), "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y") ,
                            'unit_amount': "{:.2f}".format(c.unit_amount)} 
                            for i, c in enumerate(tmp_ids, start=1)]

                            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False
                            ,'data': data}
                            return Response(result, status=status.HTTP_200_OK)


                # print(serializer.errors,"serializer.errors")
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
                'error': True, 'data': serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)   

