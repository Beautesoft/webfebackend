from django.core.exceptions import FieldError
from django.db import transaction, connection
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import status,viewsets
from rest_framework.response import Response

from .configuration import DYNAMIC_FIELD_CHOICES
from .models import (Gender, Employee, Fmspw, Attendance2, Customer, Images, Treatment, Stock, Systemloginlog,
                     EmpSitelist, Appointment, ItemDept, ControlNo, Treatment_Master, ItemClass, Paytable, PosTaud,
                     PayGroup,
                     PosDaud, PosHaud, GstSetting, PayGroup, TreatmentAccount, ItemStatus, Source, Securities,
                     Systemlog, ScheduleHour, ScheduleMonth,
                     ApptType, ItemHelper, Multistaff, DepositType, TmpItemHelper, PosDisc, FocReason, Holditemdetail,
                     DepositAccount, PrepaidAccount, PrepaidAccountCondition, VoucherCondition, ItemUom, Title,
                     CreditNote, Systemsetup,
                     PackageDtl, Language, Country, State, PackageHdr, BlockReason, AppointmentLog, AppointmentStatus,
                     CustomerClass, Tmpmultistaff,
                     Skillstaff, ItemType, CustomerFormControl, RewardPolicy, RedeemPolicy, Diagnosis, DiagnosisCompare,
                     Securitylevellist, DailysalesdataSummary, DailysalesdataDetail, Multilanguage, Workschedule,
                     Religious, Nationality, Races)
from cl_app.models import ItemSitelist, SiteGroup, LoggedInUser
from custom.models import Room,ItemCart,VoucherRecord,EmpLevel
from .serializers import (EmployeeSerializer, FMSPWSerializer, UserLoginSerializer, Attendance2Serializer,
                          CustomerallSerializer, CustomerSerializer, ServicesSerializer, ItemSiteListSerializer,
                          AppointmentSerializer,
                          Item_DeptSerializer, StockListSerializer, TreatmentMasterSerializer,
                          ItemSiteListAPISerializer,
                          StockListTreatmentSerializer, StaffsAvailableSerializer, PaytableSerializer,
                          PostaudSerializer,
                          PoshaudSerializer, PosdaudSerializer, PayGroupSerializer, PostaudprintSerializer,
                          StateSerializer,
                          ItemStatusSerializer, SourceSerializer, AppointmentPopupSerializer,
                          AppointmentCalendarSerializer,
                          SecuritiesSerializer, CustTransferSerializer, EmpTransferPerSerializer,
                          EmpTransferTempSerializer,
                          EmpSitelistSerializer, ScheduleHourSerializer, CustApptSerializer, ApptTypeSerializer,
                          CountrySerializer,
                          TmpItemHelperSerializer, FocReasonSerializer, CustomerUpdateSerializer, LanguageSerializer,
                          TreatmentApptSerializer,
                          AppointmentResourcesSerializer, AppointmentSortSerializer, ApptTreatmentDoneHistorySerializer,
                          UpcomingAppointmentSerializer, AppointmentBlockSerializer, BlockReasonSerializer,
                          EmployeeBranchSerializer,
                          AppointmentLogSerializer, AppointmentRecurrSerializer, RoomAppointmentSerializer,
                          DeptAppointmentSerializer,
                          TitleSerializer, CustApptUpcomingSerializer, AttendanceStaffsSerializer,
                          CustomerFormControlSerializer,
                          StaffPlusSerializer, EmpInfoSerializer, EmpWorkScheduleSerializer,
                          CustomerPlusSerializer, RewardPolicySerializer, RedeemPolicySerializer, SkillSerializer,
                          DiagnosisSerializer, DiagnosisCompareSerializer, SecuritylevellistSerializer,
                          AppointmentEditSerializer, DailysalesdataSummarySerializer, DailysalesdataDetailSerializer)
from datetime import date, timedelta, datetime
import datetime
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import Http404
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework import generics
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login , logout, get_user_model
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator, InvalidPage
import math
from custom.views import response, get_client_ip, round_calc
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from django.db.models import Q
from rest_framework import serializers
from rest_framework.views import APIView
import base64 
from rest_framework.decorators import action, permission_classes
import pandas as pd 
from dateutil import parser, rrule
from .authentication import token_expire_handler, expires_in, multiple_expire_handler
from django.conf import settings
from rest_framework.decorators import api_view
from Cl_beautesoft.settings import SMS_ACCOUNT_SID, SMS_AUTH_TOKEN, SMS_SENDER
from django.core.mail import EmailMessage
from Cl_beautesoft.settings import EMAIL_HOST_USER
from django.template.loader import get_template
from django.template import Context, Template
from cl_app.permissions import authenticated_only
from twilio.rest import Client
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from time import sleep 
from cl_app.utils import general_error_response
from Cl_beautesoft.settings import TIME_ZONE
from .services import invoice_deposit,invoice_topup,invoice_sales,invoice_exchange
from collections import Counter
from cl_table.authentication import ExpiringTokenAuthentication
from pyvirtualdisplay import Display
import pdfkit
from fpdf import FPDF 
import os
from Cl_beautesoft.settings import BASE_DIR
import io
# import xlsxwriter # todo: uncomment this
from django.db.models import Count
from django.db.models import F    
from django.utils.html import strip_tags
from django.core.mail import EmailMessage, send_mail, EmailMultiAlternatives

type_ex = ['VT-Deposit','VT-Top Up','VT-Sales']

# Create your views here .

# @api_view(["GET"])
# def user_info(request):
#     return Response({
#         'user': request.user.username,
#         'expires_in': expires_in(request.auth)
#     }, status=HTTP_200_OK)   
# 

# class ChangeApplicationStatus(APIView):
#     permission_classes = [IsAdminUser, ]

#     def post(self, request):
#         ser = StatusChangeSerializer(data=request.data)
#         ser.is_valid(raise_exception=True)
#         ret_data = {'status': 'ok'}
#         try:
#             process_application_status_change(**dict(ser.data))
#         except JuloInvalidStatusChange as e:
#             ret_data = {'status': 'error', 'errors': e.message}
#         return Response(status=HTTP_200_OK, data=ret_data)
     

class UserLoginAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            user = serializer.user
            fmspw_ids = Fmspw.objects.filter(user=user,pw_isactive=True)
            if not fmspw_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":'User account is disabled.','error': True, 'data': 'User account is not activated.'} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            fmspw = Fmspw.objects.filter(user=user,pw_isactive=True)[0]

            msg = "FE - Login Successful : "+" "+str(user.username)
            Systemloginlog(log_type="PROCESSLOG",log_datetime=timezone.now(),log_user=fmspw.pw_userlogin,
            log_process="System Login",log_message=msg).save()
            login(request, user)
            # if fmspw.loginsite:
            #    fmspw.loginsite = None
            #    fmspw.save()
            branch = ""
            salon = ""
            if request.data['salon'] != 0:
                siteid = ItemSitelist.objects.filter(pk=request.data['salon'],itemsite_isactive=True)[0]
                if siteid:
                    fmspw.loginsite = siteid
                    fmspw.save()
                    branch = siteid.itemsite_code
                    salon = siteid.Site_Groupid.description
            
            empcode=fmspw.emp_code
            # siteids = EmpSitelist.objects.filter(emp_code=empcode,isactive=True).only('site_code')
            sites =[]
            # if siteids:
            #    for d in siteids:
            #       sites.append(d.site_code)

            # emp_ids = EmpSitelist.objects.filter(Site_Codeid__pk=site.pk,isactive=True)
            # emp_lst = list(set([e.Emp_Codeid.pk for e in emp_ids if e.Emp_Codeid]))
            # queryset = Employee.objects.filter(pk__in=emp_lst,emp_isactive=True).order_by('-pk')
            emp_ids = EmpSitelist.objects.filter(emp_code=empcode,isactive=True)
            # print(emp_ids,"empids")
            emp_lst = list(set([e.Site_Codeid.pk for e in emp_ids if e.Site_Codeid]))
            # print(emp_lst,"emp_lst")

            itemsites = ItemSitelist.objects.filter(pk__in=emp_lst,itemsite_isactive=True).order_by('pk')
            # itemsites = ItemSitelist.objects.filter(itemsite_isactive=True,itemsite_code__inpk=site.pk).order_by('-pk')
            if itemsites:
                for d in itemsites:
                   val = {'id': d.itemsite_id, 'itemsite_code': d.itemsite_code, 'itemsite_desc': d.itemsite_desc}
                   sites.append(val)
                   if branch == "":
                       branch = d.itemsite_code
                   if salon == "":
                       salon = d.Site_Groupid.description

            # salon = siteid.Site_Groupid.description
            webbe = fmspw.flgallcom
            system_setup = Systemsetup.objects.filter(title='CID',value_name='Currency Code').first()
            if system_setup.value_data:
                currency = system_setup.value_data
            else:
                currency = "$"
            foc = 1
            system_setup = Systemsetup.objects.filter(title='SYSTEM SETTING',value_name='Allow FOC Login').first()
            if system_setup.value_data:
                if system_setup.value_data == "FALSE":
                    foc = 0

            tokens, _ = Token.objects.get_or_create(user = user)
            if tokens:
                token = multiple_expire_handler(tokens)

            # is_expired, token = token_expire_handler(token) 
            data["token"] = token.key
            data['salon'] = salon
            data['branch'] = branch
            data['backendauthorization'] = webbe
            data['foc'] = foc
            data['currency'] = currency
            data['role']:fmspw.LEVEL_ItmIDid.level_name
            data['sites'] = sites
            # data['expires_in']= expires_in(token)
            pw_data = data.pop('password')
            
            # print(request.session,"request.session")
            # print(request.session.session_key,"request.session.session_key")
            # request.session['key'] = request.session.session_key 
            # request.session['uid'] = user.id
            
            session_id = request.session.session_key
            data['session_id'] = session_id
            # print(request.session['key'],"dd")
            # print(request.session['uid'],"uid")

            result = {'status': status.HTTP_200_OK,"message":"Login Successful",'error': False, 'data': data} 
            return Response(result,status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutAPIView(GenericAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)[0]
        # if fmspw.loginsite:
        #    fmspw.loginsite = None
        #    fmspw.save()
        logout(request)
        result = {'status': status.HTTP_200_OK,"message":"Sucessfully logged out",'error': False} 
        return Response(result, status=status.HTTP_200_OK) 

        
#dev with api integration

class CustomerViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')
    serializer_class = CustomerSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
       
        queryset = Customer.objects.filter(cust_isactive=True).only('cust_isactive').order_by('-pk')

        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = queryset.filter(Q(cust_name__icontains=q) | 
            Q(cust_email__icontains=q) | Q(cust_code__icontains=q) | Q(cust_phone2__icontains=q) | Q(cust_phone1__icontains=q) |
            Q(cust_nric__icontains=q)  | Q(cust_refer__icontains=q) )[:20]
        elif value and key is not None:
            if value == "asc":
                if key == 'cust_name':
                    queryset = queryset.order_by('cust_name')
                elif key == 'cust_address':
                    queryset = queryset.order_by('cust_address')
            elif value == "desc":
                if key == 'cust_name':
                    queryset = queryset.order_by('-cust_name')
                elif key == 'cust_address':
                    queryset = queryset.order_by('-cust_address')

        return queryset


    def list(self, request):
        serializer_class = CustomerSerializer
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
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data, context={'request': self.request})
        if serializer.is_valid():
            self.perform_create(serializer)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Employee Site_Codeid is not mapped!!",'error': True} 
                raise serializers.ValidationError(result)

            control_obj = ControlNo.objects.filter(control_description__iexact="VIP CODE").first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
                
            # cus_code = "000000"+str(control_obj.control_no)+str(site.itemsite_code)
            # cus_code = cus_code[-8:]
            # cus_code = "000000"+str(control_obj.control_no)+str(site.itemsite_code)
            # cus_code = cus_code[-8:]
            cus_code = str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
            # print(request.data['Cust_refer'],"refer")
            # print(request.data['cust_phone2'],"phone")
            # print(request.data['reference'],"reference")
            # gender = Gender.objects.filter(pk=request.data['Cust_sexesid'],itm_isactive=True).first()
            # k = serializer.save(site_code=site.itemsite_code,cust_code=cus_code,cust_sexes=gender.itm_code,cust_joindate=timezone.now())
            gender = False
            if request.data['Cust_sexesid']:
                gender = Gender.objects.filter(pk=request.data['Cust_sexesid'],itm_isactive=True).first()

            # k = serializer.save(site_code=site.itemsite_code,cust_code=cus_code,cust_joindate=timezone.now(),join_status=True,
            # cust_phone2=request.data['cust_phone2'],cust_isactive=True,or_key=site.itemsite_code)
            classobj = CustomerClass.objects.filter(class_code='100001',class_isactive=True).first()
            #if 'Site_Codeid' in request.data: 
            #    #site_obj = ItemSitelist.objects.filter(pk=request.data['Site_Codeid']).first()    
            #    k = serializer.save(site_code=site_obj.itemsite_code,cust_code=cus_code,
            #    cust_sexes=gender.itm_code if gender else None, cust_joindate=timezone.now(),
            #    join_status=True,cust_class=classobj.class_code if classobj and classobj.class_code else None,
            #    Cust_Classid=classobj,cust_phone2=request.data['cust_phone2'],cust_isactive=True,or_key=site.itemsite_code)
            #else:
            k = serializer.save(site_code=site.itemsite_code,Site_Codeid=site,cust_code=cus_code,
            cust_sexes=gender.itm_code if gender else None, cust_joindate=timezone.now(),
            join_status=True,cust_class=classobj.class_code if classobj and classobj.class_code else None,
            Cust_Classid=classobj,cust_phone2=request.data['cust_phone2'],cust_isactive=True,or_key=site.itemsite_code)

            if k.pk:
                control_obj.control_no = int(control_obj.control_no) + 1
                control_obj.save()
            state = status.HTTP_201_CREATED
            message = "Created Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_201_CREATED)

        error = True
        # print(serializer.errors,"serializer.errors")
        data = serializer.errors
        print(data,"data")
        if 'non_field_errors' in data:
            message = data['non_field_errors'][0]
        else:
            message = "Invalid Input"
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    

    def get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk,cust_isactive=True)
        except Customer.DoesNotExist:
            raise Http404

   
    def retrieve(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        customer = self.get_object(pk)
        serializer = CustomerSerializer(customer)
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
        customer = self.get_object(pk)
        serializer = CustomerUpdateSerializer(customer, data=request.data, context={'request': self.request})
        if serializer.is_valid():
            gender = False
            if request.data['Cust_sexesid']:
                gender = Gender.objects.filter(pk=request.data['Cust_sexesid'],itm_isactive=True).first()
                
            serializer.save(cust_sexes=gender.itm_code if gender else None)
            # serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        data = serializer.errors
        message = data['non_field_errors'][0]
        state = status.HTTP_204_NO_CONTENT
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        customer = self.get_object(pk)
        serializer = CustomerUpdateSerializer(customer, data=request.data, partial=True, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
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
        instance = self.get_object(pk)
        if instance:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"You are not allowed to delete customer!!",'error': True} 
            raise serializers.ValidationError(result)

        try:
            self.perform_destroy(instance)
            message = "Deleted Succesfully"
            error = False
            result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK)    
        except Exception as e:
            pass

        message = "No Content 16"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)    

    def perform_destroy(self, instance):
        instance.cust_isactive = False
        instance.save()    

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def CustTransfer(self, request, pk=None):
        customer = self.get_object(pk)  
        serializer = CustTransferSerializer(customer, data=request.data, partial=True, context={'request': self.request})
        if serializer.is_valid():
            if 'site_id' in request.data and not request.data['site_id'] is None:
                siteobj = ItemSitelist.objects.filter(pk=request.data['site_id'],itemsite_isactive=True).first() 
                serializer.save(Site_Codeid=siteobj,site_code=siteobj.itemsite_code)

            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
            return Response(result, status=status.HTTP_200_OK)

        data = serializer.errors
        result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
        return Response(result, status=status.HTTP_400_BAD_REQUEST)



# class CustomerListView(generics.ListAPIView):
#     authentication_classes = []
#     permission_classes = []
#     queryset = Customer.objects.filter(cust_isactive=True).order_by('-id')
#     serializer_class = CustomerSerializer
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['cust_name', 'cust_address','last_visit','upcoming_appointments','Cust_DOB','cust_phone2','cust_email','cust_isactive','created_at','Sync_LstUpd']

class CustomerListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')
    serializer_class = CustomerallSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')

        return queryset

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            lst =[]
            for c in serializer.data:
                data_dict = dict(c)
                val = {'value': c['id'] ,'label': c['cust_name']}
                lst.append(val)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  lst}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 17",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   

class ServicesListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')
    serializer_class = ServicesSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)
        queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')
        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [27,31]:
            queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')

        return queryset

    def list(self, request):
        serializer_class = ServicesSerializer
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 18",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   


class ServicesViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')
    serializer_class = ServicesSerializer
    
    def get_serializer_context(self):
        return {'request': self.request,'view': self}

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)


        queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')
        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [27,31]:
            queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')

        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = Stock.objects.filter(item_isactive=True).filter(Q(item_desc__icontains=q) | Q(Item_Classid__itm_desc__icontains=q) 
            | Q(Item_Rangeid__itm_desc__icontains=q)).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'item_desc':
                    queryset = Stock.objects.filter(item_isactive=True).order_by('item_desc')
               
            elif value == "desc":
                if key == 'item_desc':
                    queryset = Stock.objects.filter(item_isactive=True).order_by('-item_desc')

        return queryset

    def list(self, request):
        serializer_class = ServicesSerializer
        queryset = self.filter_queryset(self.get_queryset())
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        for dat in d:
            dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
            if dat['tax'] is not None:
                dat["tax"] = "{:.2f}".format(float(dat['tax']))
            else:
                dat["tax"] = None   
            if dat['itm_disc'] is not None:
                dat["itm_disc"] = "{:.2f}".format(float(dat['itm_disc']))
            else:
                dat["itm_disc"] = None    

        return Response(result, status=status.HTTP_200_OK)         
    
    def create(self, request):
        state = status.HTTP_400_BAD_REQUEST
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': state,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': state,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data, context={'view': self, 'request': self.request})
        if serializer.is_valid():
            classobj = ItemClass.objects.filter(pk=request.data['Item_Classid'],itm_isactive=True).first()
            self.perform_create(serializer)
            site = fmspw[0].Emp_Codeid.Site_Codeid
            s = serializer.save(item_class=classobj.itm_code,item_createuserid=fmspw[0],item_createuser=fmspw[0].pw_userlogin)
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
            return Stock.objects.get(pk=pk,item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    
    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        queryset = None
        total = None
        serializer_class = None
        stock = self.get_object(pk)
        serializer = ServicesSerializer(stock)
        data = serializer.data
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        images = v['images']
        lst = []
        for i in images:
            im = dict(i)
            if im['image']:
                images = str(ip)+str(im['image'])
                val = {'id':im['id'],'image':images}
                lst.append(val)
        v['images'] = lst 
        return Response(result, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        stock = self.get_object(pk)
        serializer = ServicesSerializer(stock, data=request.data,  context={'view': self, 'request': self.request})
        if serializer.is_valid():
            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)

    
    def destroy(self, request, pk=None):
        image_id = self.request.GET.get('image_id',None)
        services_id = self.request.GET.get('services_id',None)
        queryset = None
        total = None
        serializer_class = None
        data = None
        state = status.HTTP_204_NO_CONTENT
        try:
            instance = self.get_object(pk)
            self.perform_destroy(instance)
            if image_id and services_id:
                message = "Image Deleted Succesfully"
            else:
                message = "Deleted Succesfully"
            error = False
            result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK)    
        except Http404:
            pass

        message = "No Content 19"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)    

    def perform_destroy(self, instance):
        image_id = self.request.GET.get('image_id',None)
        services_id = self.request.GET.get('services_id',None)
        if image_id and services_id:
            img = Images.objects.filter(id=image_id,services=services_id).delete()
        else:
            instance.item_isactive = False
            instance.save() 

class ItemSiteListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ItemSitelist.objects.filter(itemsite_isactive=True).order_by('-pk')
    serializer_class = ItemSiteListAPISerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = ItemSitelist.objects.filter(itemsite_isactive=True,pk=site.pk).order_by('-pk')

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = ItemSitelist.objects.filter(itemsite_isactive=True).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [27,31]:
            queryset = ItemSitelist.objects.filter(itemsite_isactive=True,pk=site.pk).order_by('-pk')
                
        return queryset
    

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 20",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 

class ItemSiteListAPIViewLogin(generics.ListAPIView):
    authentication_classes = []
    permission_classes = []
    queryset = ItemSitelist.objects.filter(itemsite_isactive=True).order_by('pk')
    serializer_class = ItemSiteListAPISerializer

    def get_queryset(self):
        queryset = ItemSitelist.objects.filter(itemsite_isactive=True).order_by('pk')
        return queryset

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 21",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)                              

class ItemSiteListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ItemSitelist.objects.filter(itemsite_isactive=True).order_by('-pk')
    serializer_class = ItemSiteListSerializer

    def get_serializer_context(self):
        return {'request': self.request,'view': self}

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = ItemSitelist.objects.filter(itemsite_isactive=True,pk=site.pk).order_by('-pk')

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = ItemSitelist.objects.filter(itemsite_isactive=True).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [27,31]:
            queryset = ItemSitelist.objects.filter(itemsite_isactive=True,pk=site.pk).order_by('-pk')
        print(self.request,"request")
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)
        if q is not None:
            queryset = queryset.filter(Q(itemsite_desc__icontains=q) | Q(Site_Groupid__description__icontains=q) | 
            Q(services__item_desc__icontains=q)).order_by('-pk') 
        elif value and key is not None:
            if value == "asc":
                if key == 'itemsite_desc':
                    queryset = queryset.order_by('itemsite_desc')
                elif key == 'Site_Groupid':
                    queryset = queryset.order_by('Site_Groupid')
                elif key == 'services':
                    queryset = queryset.order_by('services')   
               
            elif value == "desc":
                if key == 'itemsite_desc':
                    queryset = queryset.order_by('-itemsite_desc')
                elif key == 'Site_Groupid':
                    queryset = queryset.order_by('-Site_Groupid')
                elif key == 'services':
                    queryset = queryset.order_by('-services')   
                   
        return queryset
    
    def list(self, request):
        serializer_class = ItemSiteListSerializer
        queryset = self.filter_queryset(self.get_queryset())
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)         
           
    
    def create(self, request):
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)[0]
        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data, context={'request': self.request})
        if serializer.is_valid():
            self.perform_create(serializer)
            siteobj= SiteGroup.objects.filter(id=request.data['Site_Groupid'],is_active=True).first()
            serializer.save(ItemSite_Userid=fmspw,itemsite_user=fmspw.pw_userlogin,site_group=siteobj.code)
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
            return ItemSitelist.objects.get(pk=pk,itemsite_isactive=True)
        except ItemSitelist.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        queryset = None
        total = None
        serializer_class = None
        site = self.get_object(pk)
        serializer = ItemSiteListSerializer(site)
        data = serializer.data
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        images = v['images']
        lst = []
        for i in images:
            im = dict(i)
            if im['image']:
                images = str(ip)+str(im['image'])
                val = {'id':im['id'],'image':images}
                lst.append(val)
        v['images'] = lst       
        return Response(result, status=status.HTTP_200_OK)
        
    def update(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        site = self.get_object(pk)
        serializer = ItemSiteListSerializer(site, data=request.data,  context={'view': self, 'request': self.request})
        if serializer.is_valid():
            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        site = self.get_object(pk)
        serializer = ItemSiteListSerializer(site, data=request.data,  context={'view': self,'request': self.request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        image_id = self.request.GET.get('image_id',None)
        item_sitelist_id = self.request.GET.get('item_sitelist_id',None)
        queryset = None
        total = None
        serializer_class = None
        data = None
        state = status.HTTP_204_NO_CONTENT
        try:
            instance = self.get_object(pk)
            self.perform_destroy(instance)
            if image_id and item_sitelist_id:
                message = "Image Deleted Succesfully"
            else:
                message = "Deleted Succesfully"
            error = False
            result=response(self,request, queryset, total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result,status=status.HTTP_200_OK)    
        except Http404:
            pass

        message = "No Content 22"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)    

    def perform_destroy(self, instance):
        image_id = self.request.GET.get('image_id',None)
        item_sitelist_id = self.request.GET.get('item_sitelist_id',None)
        if image_id and item_sitelist_id:
            img = Images.objects.filter(id=image_id,item_sitelist=item_sitelist_id).delete()
        else:    
            instance.itemsite_isactive = False      
            instance.save()      

class EmployeeViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        empl = fmspw[0].Emp_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)
        emp_ids = EmpSitelist.objects.filter(Site_Codeid__pk=site.pk,isactive=True)


        queryset = Employee.objects.none()

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 31:
            emp_lst = list(set([e.Emp_Codeid.pk for e in emp_ids if e.Emp_Codeid]))
            queryset = Employee.objects.filter(pk__in=emp_lst,emp_isactive=True).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 27:
            emp_lst = list(set([e.Emp_Codeid.pk for e in emp_ids if e.Emp_Codeid.pk == empl.pk]))
            queryset = Employee.objects.filter(pk__in=emp_lst,emp_isactive=True).order_by('-pk')
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = queryset.filter(Q(emp_name__icontains=q) | Q(emp_code__icontains=q) | 
            Q(skills__item_desc__icontains=q) | Q(Site_Codeid__itemsite_desc__icontains=q) |
            Q(defaultSiteCodeid__itemsite_desc__icontains=q)).order_by('-pk') 
        elif value and key is not None:
            if value == "asc":
                if key == 'emp_name':
                    queryset = queryset.order_by('emp_name')
                elif key == 'emp_code':
                    queryset = queryset.order_by('emp_code')
                elif key == 'skills':
                    queryset = queryset.order_by('skills') 
                elif key == 'Site_Codeid':
                    queryset = queryset.order_by('Site_Codeid')
                elif key == 'defaultSiteCodeid':
                    queryset = queryset.order_by('defaultSiteCodeid')    
            elif value == "desc":
                if key == 'emp_name':
                    queryset = queryset.order_by('-emp_name')
                elif key == 'emp_code':
                    queryset = queryset.order_by('-emp_code')
                elif key == 'skills':
                    queryset = queryset.order_by('-skills') 
                elif key == 'Site_Codeid':
                    queryset = queryset.order_by('-Site_Codeid')
                elif key == 'defaultSiteCodeid':
                    queryset = queryset.order_by('defaultSiteCodeid')        
                   
        return queryset


    def list(self, request):
        serializer_class = EmployeeSerializer
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
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        Site_Codeid = fmspw[0].loginsite
        if not self.request.user.is_authenticated:
            result = {'status': state,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': state,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        if not Site_Codeid:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data, context={'request': self.request})

        if int(fmspw[0].level_itmid) not in [24,31]:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Staffs / other login user not allow to create staff!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            control_obj = ControlNo.objects.filter(control_description__iexact="EMP CODE",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
            emp_code = str(control_obj.control_prefix)+str(control_obj.control_no)
            defaultobj = ItemSitelist.objects.filter(pk=request.data['defaultSiteCodeid'],itemsite_isactive=True).first()

            site_unique = EmpSitelist.objects.filter(emp_code=emp_code,site_code=defaultobj.itemsite_code,isactive=True)
            if site_unique:
                result = {'status': state,"message":"Unique Constrain for emp_code and site_code!!",'error': True} 
                raise serializers.ValidationError(result)
            user_obj = User.objects.filter(username=request.data['emp_name'])
            if user_obj:
                result = {'status': state,"message":"Username already exist!!",'error': True} 
                raise serializers.ValidationError(result)
            emp_obj = Employee.objects.filter(emp_name=request.data['emp_name'])
            if emp_obj:
                result = {'status': state,"message":"Employee already exist!!",'error': True} 
                raise serializers.ValidationError(result)
            fmspw_obj = Fmspw.objects.filter(pw_userlogin=request.data['emp_name'])
            if fmspw_obj:
                result = {'status': state,"message":"Fmspw already exist!!",'error': True} 
                raise serializers.ValidationError(result)

            token_obj = Fmspw.objects.filter(user__username=request.data['emp_name'])
            if token_obj:
                result = {'status': state,"message":"Token for this employee user is already exist!!",'error': True} 
                raise serializers.ValidationError(result)


            jobtitle = EmpLevel.objects.filter(id=request.data['EMP_TYPEid'],level_isactive=True).first()
            gender = Gender.objects.filter(pk=request.data['Emp_sexesid'],itm_isactive=True).first()
            self.perform_create(serializer)
            s = serializer.save(emp_code=emp_code,emp_type=jobtitle.level_code,emp_sexes=gender.itm_code,
            defaultsitecode=defaultobj.itemsite_code,site_code=Site_Codeid.itemsite_code)
            s.emp_code = emp_code
            s.save()
            token = False
            if s.is_login == True:
                if not 'pw_password' in request.data:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"pw_password Field is required.",'error': True} 
                    raise serializers.ValidationError(result)
                else:
                    if request.data['pw_password'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"pw_password Field is required.",'error': True} 
                        raise serializers.ValidationError(result)
                if not 'LEVEL_ItmIDid' in request.data:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"LEVEL_ItmIDid Field is required.",'error': True} 
                    raise serializers.ValidationError(result)
                else:
                    if request.data['LEVEL_ItmIDid'] is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"LEVEL_ItmIDid Field is required.",'error': True} 
                        raise serializers.ValidationError(result)
                
                EmpSitelist(Emp_Codeid=s,emp_code=emp_code,Site_Codeid=s.defaultSiteCodeid,site_code=s.defaultSiteCodeid.itemsite_code).save()
                user = User.objects.create_user(username=s.emp_name,email=s.emp_email,password=request.data['pw_password'])    
                levelobj = Securities.objects.filter(pk=request.data['LEVEL_ItmIDid'],level_isactive=True).first()             
                Fmspw(pw_userlogin=s.emp_name,pw_password=request.data['pw_password'],
                LEVEL_ItmIDid=levelobj,level_itmid=levelobj.level_code,level_desc=levelobj.level_description,
                Emp_Codeid=s,emp_code=emp_code,user=user,loginsite=None).save()
                s.pw_userlogin = s.emp_name
                s.pw_password = request.data['pw_password']
                s.LEVEL_ItmIDid = levelobj
                s.save()
                token = Token.objects.create(user=user)
            if s.pk:
                control_obj.control_no = int(control_obj.control_no) + 1
                control_obj.save()
            state = status.HTTP_201_CREATED
            message = "Created Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            v = result.get('data')
            if token:
                v["token"] = token.key
                    
            return Response(result, status=status.HTTP_201_CREATED)

        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

   
    def get_object(self, pk):
        try:
            return Employee.objects.get(pk=pk,emp_isactive=True)
        except Employee.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        queryset = None
        total = None
        serializer_class = None
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee)
        data = serializer.data
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        if v['emp_pic']:
            images = str(ip)+str(v['emp_pic'])
            v['emp_pic'] = images
        return Response(result, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data, context={'request': self.request})
        if serializer.is_valid():
            if 'emp_name' in request.data and not request.data['emp_name'] is None:
                serializer.save()
                fmspw_obj = Fmspw.objects.filter(Emp_Codeid=employee,pw_isactive=True).first()
                if fmspw_obj:
                    fmspw_obj.pw_userlogin = request.data['emp_name']
                    fmspw_obj.save()
                    if fmspw_obj.user:
                        fmspw_obj.user.username =  request.data['emp_name']
                        fmspw_obj.user.save() 
                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"FMSPW User is not Present.Please map",'error': True} 
                        raise serializers.ValidationError(result)

            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        employee = self.get_object(pk)
        serializer = EmployeeSerializer(employee, data=request.data, partial=True, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
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

        message = "No Content 23"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)    

    def perform_destroy(self, instance):
        instance.emp_isactive = False
        instance.save()    

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def EmpTransferList(self, request, pk=None):
        employee = self.get_object(pk)  
        serializer = EmpTransferPerSerializer(employee, context={'request': self.request})
        sitelist_ids = EmpSitelist.objects.filter(Emp_Codeid=employee,isactive=True)
        if sitelist_ids:
            serializer_empsite = EmpSitelistSerializer(sitelist_ids, many=True)
            data = serializer_empsite.data
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,'data':data}
            return Response(result, status=status.HTTP_200_OK)

        result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 24",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def EmpTransfer(self, request, pk=None):
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        Site_Codeid = fmspw[0].loginsite
        employee = self.get_object(pk) 
        if 'site_id' in request.data and not request.data['site_id'] is None:
            siteobj = ItemSitelist.objects.filter(pk=request.data['site_id'],itemsite_isactive=True).first() 
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"site_id Field is required!!",'error': True} 
            raise serializers.ValidationError(result)
     
                       
        if self.request.GET.get('permanent',None) == "1":
            serializer = EmpTransferPerSerializer(employee, data=request.data, partial=True, context={'request': self.request})
            if serializer.is_valid():
                site_unique = EmpSitelist.objects.filter(emp_code=employee.emp_code,site_code=siteobj,isactive=True)
                if site_unique:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unique Constrain for emp_code and site_code!!",'error': True} 
                    raise serializers.ValidationError(result)

                if self.request.GET.get('check',None) == "No":
                    EmpSitelist(Emp_Codeid=employee,emp_code=employee.emp_code,Site_Codeid=siteobj,site_code=siteobj.itemsite_code).save()
                    result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    if self.request.GET.get('check',None) == "Yes":
                        sitelist_ids = EmpSitelist.objects.filter(Emp_Codeid=employee,isactive=True).delete()
                        EmpSitelist(Emp_Codeid=employee,emp_code=employee.emp_code,Site_Codeid=siteobj,
                        site_code=siteobj.itemsite_code).save()
                        result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                        return Response(result, status=status.HTTP_200_OK)

                data = serializer.errors
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 'data': serializer.errors} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                    
        else:
            if self.request.GET.get('permanent',None) == "0":
                if not 'hour_id' in request.data:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"hour_id Field is required!!",'error': True} 
                    raise serializers.ValidationError(result)
     
                serializer = EmpTransferTempSerializer(employee, data=request.data, partial=True, context={'request': self.request})
                if serializer.is_valid():
                    msg = "Temporary Transfer Site"+" "+str(siteobj.itemsite_code)
                    Systemlog(log_type="PROCESSLOG",log_datetime=timezone.now(),log_user=fmspw[0].pw_userlogin,
                    log_process="System Login",log_message=msg,log_site_code=siteobj.itemsite_code).save()
                    date1 = request.data['start_date']
                    date2 = request.data['end_date']
                    hourobj = ScheduleHour.objects.filter(id=request.data['hour_id'],itm_isactive=True).first()
                    start_date = datetime.datetime.strptime(str(date1), "%Y-%m-%d").date()
                    end_date = datetime.datetime.strptime(str(date2), "%Y-%m-%d").date()
                    day_count = (end_date - start_date).days + 1
                    for single_date in [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]:
                        date = single_date.strftime('%Y-%m-%d')
                        sche_ids = ScheduleMonth.objects.filter(emp_code=employee.emp_code,itm_date=date,
                        itm_type=hourobj.itm_code,user_name=fmspw[0].pw_userlogin,site_code=siteobj.itemsite_code).order_by('id')
                        
                        if not sche_ids:
                            ScheduleMonth(Emp_Codeid=employee,emp_code=employee.emp_code,itm_date=date,
                            itm_Typeid=hourobj,itm_type=hourobj.itm_code,ledit=True,
                            ledittype=hourobj.itm_code,User_Nameid=fmspw[0],user_name=fmspw[0].pw_userlogin,
                            datetime=timezone.now(),Site_Codeid=siteobj,site_code=siteobj.itemsite_code,comments=None).save()

                    result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                    return Response(result, status=status.HTTP_200_OK)

                data = serializer.errors
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 'data': serializer.errors} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Parms permanent",'error': True} 
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
class ScheduleHourAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ScheduleHour.objects.filter(itm_isactive=True).order_by('-id')
    serializer_class = ScheduleHourSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 
       

class ShiftListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Attendance2.objects.filter().order_by('-pk')
    serializer_class = Attendance2Serializer

    def get_queryset(self):
        q = self.request.GET.get('employee',None)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = Attendance2.objects.filter(created_at=date.today(),Attn_Emp_codeid=q).order_by('-pk')

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Attendance2.objects.filter(created_at=date.today()).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 31:
            queryset = Attendance2.objects.filter(Attn_Site_Codeid=site,created_at=date.today()).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 27:
            queryset = Attendance2.objects.filter(Attn_Site_Codeid=site,Attn_Emp_codeid=q,created_at=date.today()).order_by('-pk')

        return queryset

    def list(self, request):
        serializer_class = Attendance2Serializer
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 25",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   



class ShiftViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Attendance2.objects.filter().order_by('-pk')
    serializer_class = Attendance2Serializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        empl = fmspw[0].Emp_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = Attendance2.objects.filter(Attn_Site_Codeid=site,Attn_Emp_codeid__pk=empl.pk).order_by('-pk')

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Attendance2.objects.filter().order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 31:
            queryset = Attendance2.objects.filter(Attn_Site_Codeid=site).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 27:
            queryset = Attendance2.objects.filter(Attn_Site_Codeid=site,Attn_Emp_codeid__pk=empl.pk).order_by('-pk')
       
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = queryset.filter(Q(Attn_Emp_codeid__emp_name__icontains=q)).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'Attn_Emp_codeid':
                    queryset = queryset.order_by('Attn_Emp_codeid')
            elif value == "desc":
                if key == 'Attn_Emp_codeid':
                    queryset = queryset.order_by('-Attn_Emp_codeid')

        return queryset

    def list(self, request):
        serializer_class = Attendance2Serializer
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 26",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   
    def create(self, request):
        state = status.HTTP_400_BAD_REQUEST
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)[0]
        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data, context={'request': self.request})
        if serializer.is_valid():
            self.perform_create(serializer)
            emp = Employee.objects.filter(pk=request.data['Attn_Emp_codeid'],emp_isactive=True).first()
            if not fmspw[0].loginsite:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"loginsite is null please login again!!",'error': True} 
                raise serializers.ValidationError(result)
     
            # site = ItemSitelist.objects.filter(pk=data['Attn_Site_Codeid'],itemsite_isactive=True).first()
            site = fmspw.loginsite
            serializer.save(attn_emp_code=emp.emp_code,Attn_Site_Codeid=site,attn_site_code=site.itemsite_code)
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
            return Attendance2.objects.get(pk=pk)
        except Attendance2.DoesNotExist:
            raise Http404


    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        queryset = None
        total = None
        serializer_class = None
        shift = self.get_object(pk)
        serializer = Attendance2Serializer(shift)
        data = serializer.data
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        if v['emp_img']:
            images = str(ip)+str(v['emp_img'])
            v['emp_img'] = images
        return Response(result, status=status.HTTP_200_OK)
        

    def update(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        shift = self.get_object(pk)
        serializer = Attendance2Serializer(shift, data=request.data, context={'request': self.request})
        if serializer.is_valid():
            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
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

        message = "No Content 27"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)  

    def perform_destroy(self, instance):
        instance.Attn_isactive = False
        instance.save()  
                      
def days_cur_month():
    m = datetime.datetime.now().month
    y = datetime.datetime.now().year
    if m == 12:
        m = 1
    ndays = (date(y, m+1, 1) - date(y, m, 1)).days
    d1 = date(y, m, 1)
    d2 = date(y, m, ndays)
    delta = d2 - d1

    return [(d1 + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]


class ShiftDateWiseViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Attendance2.objects.filter().order_by('created_at')
    serializer_class = Attendance2Serializer

    def get_queryset(self):
        datelst = days_cur_month()
        sdate = datelst[0]
        edate = datelst[-1]
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)
        empl = fmspw[0].Emp_Codeid
        queryset = Attendance2.objects.filter(created_at__gte=sdate,created_at__lte=edate,Attn_Emp_codeid__pk=empl.pk,Attn_Site_Codeid=site).order_by('created_at')

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Attendance2.objects.filter(created_at__gte=sdate,created_at__lte=edate).order_by('created_at')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 31:
            queryset = Attendance2.objects.filter(created_at__gte=sdate,created_at__lte=edate,Attn_Site_Codeid__pk=site.id).order_by('created_at')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 27:
            empl = fmspw[0].Emp_Codeid
            queryset = Attendance2.objects.filter(created_at__gte=sdate,created_at__lte=edate,Attn_Emp_codeid__pk=empl.pk,Attn_Site_Codeid=site).order_by('-pk')

        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = queryset.filter(Q(Attn_Emp_codeid__emp_name__icontains=q)).order_by('created_at')
        elif value and key is not None:
            if value == "asc":
                if key == 'Attn_Emp_code':
                    queryset = queryset.order_by('Attn_Emp_codeid')
            elif value == "desc":
                if key == 'Attn_Emp_code':
                    queryset = queryset.order_by('-Attn_Emp_codeid')
        return queryset
    
    def list(self, request):
        serializer_class = Attendance2Serializer
        queryset = self.filter_queryset(self.get_queryset())
        total  = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        datelst = days_cur_month()
        v = result.get('data')
        d = v.get('dataList')
        final = []; dit = {}
        for dt in datelst:
            for i in d:
                for key, value in i.items(): 
                    if key == 'created_at' and value == dt:
                        if dt not in dit:
                            dit[dt] = [i]
                        else:
                            dit[dt].append(i)

        v['dataList'] = [dit]
        return Response(data=result, status=status.HTTP_200_OK)         
   

class FMSPWViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Fmspw.objects.filter(pw_isactive=True).order_by('-pk')
    serializer_class = FMSPWSerializer

    def get_queryset(self):
        queryset = Fmspw.objects.filter(pw_isactive=True).order_by('-pk')
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = Fmspw.objects.filter(pw_isactive=True,pw_userlogin=q).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'pw_userlogin':
                    queryset = Fmspw.objects.filter(pw_isactive=True,pw_userlogin=q).order_by('pw_userlogin')
            elif value == "desc":
                if key == 'pw_userlogin':
                    queryset = Fmspw.objects.filter(pw_isactive=True,pw_userlogin=q).order_by('-pw_userlogin')

        return queryset
    
    def list(self, request):
        serializer_class = FMSPWSerializer
        queryset = self.filter_queryset(self.get_queryset())
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(data=result, status=status.HTTP_200_OK)         
    
    def create(self, request):
        if User.objects.filter(username=request.data['pw_userlogin']).exists():
            return Response({"Status":status.HTTP_400_BAD_REQUEST,"error":True,"message":"username already exist"},
            status=status.HTTP_400_BAD_REQUEST)
        
        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            role = Securities.objects.filter(pk=request.data['LEVEL_ItmIDid'],level_isactive=True).first()
            emp = Employee.objects.filter(pk=request.data['Emp_Codeid'],emp_isactive=True).first()
            serializer.save(level_itmid=role.level_code,emp_code=emp.emp_code)
            state = status.HTTP_201_CREATED
            message = "Created Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            user = serializer.data['user']
            user_obj = User.objects.filter(id=user)[0]
            token = Token.objects.create(user=user_obj)
            v = result.get('data')
            v["token"] = token.key
            return Response(result, status=status.HTTP_201_CREATED)

        state = status.HTTP_400_BAD_REQUEST
        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


    def perform_create(self, serializer):
        if 'LEVEL_ItmIDid' in serializer.validated_data:
            if serializer.validated_data['LEVEL_ItmIDid'] is not None:
                level = serializer.validated_data['LEVEL_ItmIDid']
                desc = level.level_description
            else:
                desc = None    
        employee = serializer.validated_data['Emp_Codeid']
        user = User.objects.create_user(username=serializer.validated_data['pw_userlogin'],email=employee.emp_email,
        password=serializer.validated_data['pw_password'])
        serializer.save(user=user,level_desc=desc) 

    def get_object(self, pk):
        try:
            return FMSPW.objects.get(pk=pk,pw_isactive=True)
        except FMSPW.DoesNotExist:
            raise Http404


    def retrieve(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        fmspw = self.get_object(pk)
        serializer = FMSPWSerializer(fmspw)
        data = serializer.data
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        if User.objects.filter(username=request.data['pw_userlogin']).exists() and request.data['pw_userlogin'] == request.user.username:
            return Response({"Status":status.HTTP_400_BAD_REQUEST,"error":True,"message":"username already exist"},
            status=status.HTTP_400_BAD_REQUEST)
        
        queryset = None
        total = None
        serializer_class = None
        fmspw = self.get_object(pk)
        serializer = FMSPWSerializer(fmspw, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer, pk)
            serializer.save()
            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)


    def perform_update(self, serializer, pk=None):
        instance = self.get_object(pk)
        if 'pw_userlogin' in serializer.validated_data:
            instance.user.username = serializer.validated_data['pw_userlogin']
        if 'pw_password' in serializer.validated_data:
            instance.user.set_password(serializer.validated_data['pw_password'])
        # if 'group' in serializer.validated_data:
        #     for existing in instance.user.groups.all():
        #         instance.user.groups.remove(existing) 

        #     instance.user.groups.add(serializer.validated_data['group'])


        instance.user.save()
        # serializer.save(group=serializer.validated_data['group'])

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

        message = "No Content 28"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)  

    def perform_destroy(self, instance):
        instance.pw_isactive = False
        instance.save()
        instance.user.is_active = False
        instance.user.save()


class EmployeeList(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)

        site = fmspw[0].loginsite
        empl = fmspw[0].Emp_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)

        queryset = Employee.objects.filter(emp_isactive=True,defaultSiteCodeid__pk=site.pk,pk=empl.pk).order_by('-pk')

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 31:
            queryset = Employee.objects.filter(emp_isactive=True,defaultSiteCodeid__pk=site.pk).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 27:
            queryset = Employee.objects.filter(emp_isactive=True,defaultSiteCodeid__pk=site.pk,pk=empl.pk).order_by('-pk')

        # q = self.request.GET.get('outlet',None)
        # if q is not None:
        #     if ItemSitelist.objects.filter(pk=q):
        #         site = ItemSitelist.objects.filter(pk=q)[0]
        #         queryset = Employee.objects.filter(emp_isactive=True,Site_Codeid__pk=site.pk).order_by('-pk') 

        return queryset

    def list(self, request):
        serializer_class = EmployeeSerializer
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data} 
        else:  
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 29",'error': False, 'data': []}
        return Response(result, status=status.HTTP_200_OK)  

def get_in_val(self, time):
    if time:
        value = str(time).split(':')
        hr = value[0]
        mins = value[1]
        in_time = str(hr)+":"+str(mins)
        return str(in_time)
    else:
        return None 

class SourceAPI(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Source.objects.filter(source_isactive=True).order_by('-id')
    serializer_class = SourceSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content 30",'error': False,  'data': []}
        return Response(data=result, status=status.HTTP_200_OK)                              

class LanguageAPI(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Language.objects.filter(itm_isactive=True).order_by('-itm_id')
    serializer_class = LanguageSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content 31",'error': False,  'data': []}
        return Response(data=result, status=status.HTTP_200_OK)                              

class StateAPI(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = State.objects.filter(itm_isactive=True).order_by('-itm_id')
    serializer_class = StateSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content 32",'error': False,  'data': []}
        return Response(data=result, status=status.HTTP_200_OK)                              

class CountryAPI(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Country.objects.filter(itm_isactive=True).order_by('-itm_id')
    serializer_class = CountrySerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content 33",'error': False,  'data': []}
        return Response(data=result, status=status.HTTP_200_OK)                              
    
class AppointmentViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('pk')
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

        site = fmspw[0].loginsite
        empl = fmspw[0].Emp_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        if fmspw[0].flgappt == True:
            if empl.show_in_appt == True:
                queryset = Appointment.objects.filter(appt_date=self.request.GET.get('Appt_date'),appt_isactive=True,ItemSite_Codeid=site,emp_noid=empl).order_by('pk')
            else:
                if empl.show_in_appt == False:
                    queryset = Appointment.objects.filter(appt_date=self.request.GET.get('Appt_date'),appt_isactive=True,ItemSite_Codeid=site).order_by('pk')
        else:
            queryset = Appointment.objects.none()
        return queryset


    def list(self, request):
        try:
            ip = get_client_ip(request)
            queryset = self.filter_queryset(self.get_queryset()).order_by('-pk')
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                data = serializer.data
                lst = []
                for d in data:
                    dict_v = dict(d)
                    dict_v['appt_fr_time'] = get_in_val(self, dict_v['appt_fr_time'])
                    dict_v['appt_to_time'] = get_in_val(self, dict_v['appt_to_time'])
                    treat = Treatment_Master.objects.filter(Appointment__pk=dict_v['id'])
                    treat_serializer = TreatmentMasterSerializer(treat, many=True ,context={'request': self.request})
                    treat_data = treat_serializer.data
                    t_lst = []
                    for dt in treat_data:
                        dict_t = dict(dt)
                        # dict_t['appt_time'] = get_in_val(self, dict_t['appt_time'])
                        dict_t['start_time'] = get_in_val(self, dict_t['start_time'])
                        dict_t['end_time'] = get_in_val(self, dict_t['end_time'])
                        dict_t['add_duration'] = get_in_val(self, dict_t['add_duration'])
                        dict_t['price'] = "{:.2f}".format(float(dict_t['price']))
                        dict_t['PIC'] = str(dict_t['PIC'])
                        if 'room_img' in dict_t and dict_t['room_img'] is not None:
                            dict_t['room_img'] = str(ip)+str(dict_t['room_img'])
                        t_lst.append(dict_t)
        
                    val = {'Appointment': dict_v, 'Treatment': t_lst}
                    lst.append(val)

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def create(self, request):
        try:
            state = status.HTTP_400_BAD_REQUEST
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            queryset = None
            serializer_class = None
            total = None
            treatment = request.data.get('Treatment')
            if treatment == []:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Details!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            link_flag = False
            if len(treatment) > 1:
                link_flag = True

            Appt = request.data.get('Appointment')
            if not Appt['appt_date']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Appointment Date!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if not Appt['cust_noid']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Customer!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if not Appt['appt_status']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Appointment Booking Status!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)     

            todaydate = timezone.now().date() 
            appt_date = datetime.datetime.strptime(str(Appt['appt_date']), "%Y-%m-%d").date()
            

            if appt_date < todaydate:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cant Book Appointments for Past days!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            if not Appt['cust_noid']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Customer!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            if 'Appt_typeid' in Appt and Appt['Appt_typeid']:
                channel = ApptType.objects.filter(pk=Appt['Appt_typeid'],appt_type_isactive=True).first()
                if not channel:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            else:
                channel = False  

            #customer = Customer.objects.filter(pk=Appt['cust_noid'],cust_isactive=True,
            #site_code=site.itemsite_code).first()
            customer = Customer.objects.filter(pk=Appt['cust_noid'],cust_isactive=True).first()
            # print(customer,'customer')
            if not customer:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            cust_obj = customer

            cust_email = cust_obj.cust_email
            # if not cust_email or cust_email is None:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Email id is not given!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 


            if 'Source_Codeid' in Appt and Appt['Source_Codeid']:
                source = Source.objects.filter(pk=Appt['Source_Codeid'],source_isactive=True).first()
                if not source:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Source Code does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                Source_Code = source.source_code 
            else:    
                Source_Code = False
            
            if 'Room_Codeid' in Appt and Appt['Room_Codeid']:
                room_ids = Room.objects.filter(id=Appt['Room_Codeid'],site_code=site.itemsite_code,isactive=True)
                if not room_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            else:
                room_ids = False

        
            apptsite = fmspw[0].loginsite
           
            for idx, reqt in enumerate(treatment):
               
                empobj = Employee.objects.filter(pk=reqt['emp_no'],emp_isactive=True).first()
                if not empobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                stockobj = Stock.objects.filter(pk=reqt['Item_Codeid'],item_isactive=True).first()
                if not stockobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item code is not avaliable!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                #customer will have multiple appt in one outlet in different time only not same time
                #customer having an appointment for the same day on another branch
                custprev_appts = Appointment.objects.filter(appt_date=Appt['appt_date'],
                cust_no=customer.cust_code).order_by('-pk').exclude(itemsite_code=site.itemsite_code)
                if custprev_appts:
                    msg = "This Customer Will have appointment on this day other outlet"
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                custprevtime_appts = Appointment.objects.filter(appt_date=Appt['appt_date'],
                cust_no=customer.cust_code).filter(Q(appt_to_time__gte=reqt['start_time']) & Q(appt_fr_time__lte=reqt['end_time'])).order_by('-pk')
                if custprevtime_appts:
                    msg = "This Customer Will have appointment on this day with same time"
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
    

                #staff having shift/appointment on other branch for the same time
                prev_appts = Appointment.objects.filter(appt_date=Appt['appt_date'],
                emp_no=empobj.emp_code).order_by('-pk')
                # print(prev_appts,"prev_appts")
                
                if prev_appts:
                    check_ids = Appointment.objects.filter(appt_date=Appt['appt_date'],emp_no=empobj.emp_code,
                    ).filter(Q(appt_to_time__gt=reqt['start_time']) & Q(appt_fr_time__lt=reqt['end_time']))
                    # print(check_ids,"check_ids")

                    if check_ids:
                        msg = "StartTime {0} EndTime {1} Service {2}, Employee {3} Already have appointment for this time".format(str(reqt['start_time']),str(reqt['end_time']),str(stockobj.item_name),str(empobj.display_name))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 


            trt_lst = []; apt_lst = []
            for idx, req in enumerate(treatment): 
                control_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=apptsite.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                appt_code = str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_prefix)+str(control_obj.control_no)
                
                if apt_lst == []:
                    linkcode = str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_prefix)+str(control_obj.control_no)
                else:
                    app_obj = Appointment.objects.filter(pk=apt_lst[0]).order_by('pk').first()
                    linkcode = app_obj.linkcode


                datelst = []
                if req['recur_qty']:
                    count = 1
                    while count <= int(req['recur_qty'])-1:
                        if datelst == []:
                            date_1 = datetime.datetime.strptime(str(Appt['appt_date']), "%Y-%m-%d")
                        else:
                            date_1 = datetime.datetime.strptime(str(datelst[-1]), "%Y-%m-%d")

                        end_date = (date_1 + datetime.timedelta(days=int(req['recur_days']))).strftime("%Y-%m-%d")
                        datelst.append(end_date)
                        count+=1
                
                # print(datelst,"datelst")

                    
                if not 'emp_no' in req:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Employee ID!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                if req['emp_no'] is None or req['emp_no'] == []:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select the treatment staff!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                res = []; emp_lst = []
                if ',' in str(req['emp_no']):
                    res = str(req['emp_no']).split(',')
                else:
                    res = str(req['emp_no']).split(' ')
                
                if res != []:
                    for e in res:
                        emp_obj = Employee.objects.filter(pk=e,emp_isactive=True).first()
                        if not emp_obj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                        if e not in emp_lst:
                            emp_lst.append(e)

                stock_obj = Stock.objects.filter(pk=req['Item_Codeid'],item_isactive=True).first()
                if not stock_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item code is not avaliable!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                
                # if req['start_time'] and req['end_time']:         
                #     apptt_ids = Appointment.objects.filter(appt_date=appt_date,emp_no=emp_obj.emp_code,
                #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=req['start_time']) & Q(appt_fr_time__lte=req['end_time']))
                #     print(apptt_ids,"apptt_ids")
                #     if apptt_ids:
                #         msg = "In These timing already Appointment is booked for employee {0} so allocate other duration".format(emp_obj.emp_code)
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


                # appt_ids = Appointment.objects.filter(appt_date=Appt['appt_date'],
                # emp_noid=emp_obj,itemsite_code=apptsite.itemsite_code).filter(Q(appt_to_time__gte=req['start_time']) & Q(appt_fr_time__lte=req['end_time']))
                # if appt_ids:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"In These timing already Appointment is booked!!",'error': True} 
                #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 

    
                #treatment_master creation  
                req['emp_no'] = emp_lst
                serializer_t = TreatmentMasterSerializer(data=req,context={'request': self.request})
                class_obj = stock_obj.Item_Classid
                if serializer_t.is_valid():
                    start_time =  get_in_val(self, req['start_time'])
                    starttime = datetime.datetime.strptime(start_time, "%H:%M")
                    # if dict_v['srv_duration'] is None or dict_v['srv_duration'] == 0.0:
        
                    if  stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
                        stk_duration = 60
                    else:
                        stk_duration = int(stock_obj.srv_duration)

                    stkduration = int(stk_duration) + 30
                    # print(stkduration,"stkduration")

                    hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                    
                    end_time = starttime + datetime.timedelta(minutes = stkduration)
                    endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                    duration = hrs
                
                    # print(start_time,endtime,duration,"duration")
                    k=serializer_t.save(course=stock_obj.item_desc,price=stock_obj.item_price,PIC=stock_obj.Stock_PIC,
                    Site_Codeid=site,site_code=site.itemsite_code,times="01",treatment_no="01",
                    status="Open",cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,cust_name=cust_obj.cust_name,
                    Item_Codeid=stock_obj,item_code=stock_obj.item_code,Item_Class=class_obj,type="N",
                    start_time=start_time,end_time=req['end_time'],add_duration=req['add_duration'],
                    duration=stkduration,trmt_room_code=room_ids[0].room_code if room_ids and room_ids[0].room_code else None,
                    Trmt_Room_Codeid=room_ids[0] if room_ids else None)
                    # treatment_code=treatment_code,treatment_parentcode=treatment_code
                
                    if k:
                        trt_lst.append(k.pk)
                        k.emp_no.add(emp_obj.pk) 
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 'data': serializer_t.errors}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                serializer = self.get_serializer(data=request.data.get('Appointment'))
                if serializer.is_valid():

                    if req['requesttherapist'] == True:
                        requesttherapist = True
                    else:
                        requesttherapist = False    

                    obj=serializer.save(cust_no=customer.cust_code,cust_name=customer.cust_name,appt_phone=customer.cust_phone2,
                    cust_refer=customer.cust_refer,Appt_Created_Byid=fmspw[0],appt_created_by=fmspw[0].pw_userlogin,
                    itemsite_code=site.itemsite_code,ItemSite_Codeid=site,source_code=Source_Code if Source_Code else None,appt_code=appt_code,new_remark=Appt['new_remark'],
                    emp_noid=emp_obj,emp_no=emp_obj.emp_code,emp_name=emp_obj.emp_name,Room_Codeid=room_ids[0] if room_ids else None,
                    room_code=room_ids[0].room_code if room_ids and room_ids[0].room_code else None,
                    Appt_typeid=channel if channel else None,appt_type=channel.appt_type_code if channel and channel.appt_type_code else None,requesttherapist=requesttherapist,
                    appt_fr_time=start_time,appt_to_time=req['end_time'],item_code=stock_obj.item_code,appt_remark=req['item_text'] if req['item_text'] else stock_obj.item_desc,
                    linkcode=linkcode,link_flag=link_flag)
                    
                    if obj.pk:
                        k.Appointment = obj
                        k.appt_time=str(obj.appt_date)
                        k.save()

                        apptlog = AppointmentLog(appt_id=obj,userid=fmspw[0].Emp_Codeid,
                        username=fmspw[0].Emp_Codeid.display_name,appt_date=Appt['appt_date'],
                        appt_fr_time=start_time,appt_to_time=req['end_time'],emp_code=emp_obj.emp_code,
                        appt_status=Appt['appt_status'],sec_status=Appt['sec_status'],appt_remark=req['item_text'] if req['item_text'] else stock_obj.item_desc,
                        item_code=stock_obj.item_code,requesttherapist=requesttherapist,add_duration=req['add_duration'],
                        new_remark=Appt['new_remark']).save()

                        control_obj.control_no = int(control_obj.control_no) + 1
                        control_obj.save()
                        # print(control_obj.control_no,"control_obj.control_no")
                        apt_lst.append(obj.pk)
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 'data': serializer.errors}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                if datelst != []:
                    linkcode = "RLC-"+str(obj.appt_code)
                    obj.recur_linkcode = linkcode
                    obj.recurring_qty = req['recur_qty']
                    obj.recurring_days = req['recur_days']
                    obj.save()

                    for e in datelst: 
                        recontrol_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=apptsite.pk).first()
                        reappt_code = str(recontrol_obj.Site_Codeid.itemsite_code)+str(recontrol_obj.control_prefix)+str(recontrol_obj.control_no)
             
                        appt_re = Appointment(appt_date=e,cust_noid=customer,cust_no=customer.cust_code,cust_name=customer.cust_name,appt_phone=customer.cust_phone2,
                        cust_refer=customer.cust_refer,Appt_Created_Byid=fmspw[0],appt_created_by=fmspw[0].pw_userlogin,
                        itemsite_code=site.itemsite_code,ItemSite_Codeid=site,source_code=Source_Code if Source_Code else None,appt_code=reappt_code,new_remark=Appt['new_remark'],
                        emp_noid=emp_obj,emp_no=emp_obj.emp_code,emp_name=emp_obj.emp_name,Room_Codeid=room_ids[0] if room_ids else None,
                        room_code=room_ids[0].room_code if room_ids and room_ids[0].room_code else None,Source_Codeid=source if Appt['Source_Codeid'] else None,
                        Appt_typeid=channel if channel else None,appt_type=channel.appt_type_code if channel and channel.appt_type_code else None,requesttherapist=requesttherapist,
                        appt_fr_time=start_time,appt_to_time=req['end_time'],item_code=stock_obj.item_code,appt_remark=req['item_text'] if req['item_text'] else stock_obj.item_desc,
                        appt_status=Appt['appt_status'],sec_status=Appt['sec_status'],recur_linkcode=linkcode,
                        recurring_qty=req['recur_qty'],recurring_days=req['recur_days'])
                        appt_re.save()

                        if appt_re.pk:
                            recontrol_obj.control_no = int(recontrol_obj.control_no) + 1
                            recontrol_obj.save() 

                        appt_log = AppointmentLog(appt_id=appt_re,userid=fmspw[0].Emp_Codeid,
                        username=fmspw[0].Emp_Codeid.display_name,appt_date=e,
                        appt_fr_time=start_time,appt_to_time=req['end_time'],emp_code=emp_obj.emp_code,
                        appt_status=Appt['appt_status'],sec_status=Appt['sec_status'],appt_remark=req['item_text'] if req['item_text'] else stock_obj.item_desc,
                        item_code=stock_obj.item_code,requesttherapist=requesttherapist,add_duration=req['add_duration'],
                        new_remark=Appt['new_remark'])
                        appt_log.save()


                        trt_re = Treatment_Master(course=stock_obj.item_desc,price=stock_obj.item_price,PIC=stock_obj.Stock_PIC,
                        Site_Codeid=site,site_code=site.itemsite_code,times="01",treatment_no="01",appt_time=e,
                        status="Open",cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,cust_name=cust_obj.cust_name,
                        Item_Codeid=stock_obj,item_code=stock_obj.item_code,Item_Class=class_obj,type="N",
                        start_time=start_time,end_time=req['end_time'],add_duration=req['add_duration'],
                        duration=stkduration,trmt_room_code=room_ids[0].room_code if room_ids and room_ids[0].room_code else None,
                        Trmt_Room_Codeid=room_ids[0] if room_ids else None,requesttherapist=requesttherapist,Appointment=appt_re)
                        trt_re.save()
                        trt_re.emp_no.add(emp_obj.pk)     

                    
            
            ip = get_client_ip(request)
            state = status.HTTP_201_CREATED
            error = False
            treat_t = Treatment_Master.objects.filter(id__in=trt_lst)
            serializer_final = TreatmentMasterSerializer(treat_t, many=True,context={'request': self.request})
            data_d = serializer_final.data
            appt_t = Appointment.objects.filter(pk__in=apt_lst)
            serializer_apt = AppointmentSerializer(appt_t, many=True,context={'request': self.request})
            data_a = serializer_apt.data
            final_data = {'Appointment':data_a,'Treatment':data_d}
            
            allowsms = False; allowemail = False
            allow_sms = cust_obj.custallowsendsms
            cust_name = cust_obj.cust_name
            date = Appt['appt_date']
            if allow_sms:
                receiver = cust_obj.cust_phone2
                if not receiver:
                    result = {'status': status.HTTP_200_OK,"message":"Mobile number is not given!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
                try:
                    client = Client(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
                    message = client.messages.create(
                            body='''Dear {0},\nYour Appointment dated on {1} is created successfully in Booking Status.\nThank You,'''.format(cust_name,date),
                            from_=SMS_SENDER,
                            to=receiver)
                    allowsms = True     
                except:
                    allowsms = False       

            allow_email = cust_obj.cust_maillist
            if allow_email and cust_obj.cust_email:
                to = cust_obj.cust_email
                
                subject = "Beautesoft Appointment"
                sender = EMAIL_HOST_USER
                system_setup = Systemsetup.objects.filter(title='Email Setting',value_name='Email CC To').first()
                if system_setup.value_data:
                    cc = [system_setup.value_data]
                else:
                    cc = []    
                email_msg = "Your Appointment is booked successfully."
                ctx = {
                    'name': cust_name,
                    'textmessage': email_msg,
                }
                try:
                    message = get_template('app_email.html').render(ctx)
                    msg = EmailMessage(subject, message, to=[to], from_email=sender, cc=cc)
                    msg.content_subtype = 'html'
                    msg.send()
                    allowemail = True 
                except:
                    allowemail = False

            if allowsms == True and allowemail == True:
                message = "Created Succesfully and Email and SMS sent Succesfully"
            elif allowsms == True:
                message = "Created Succesfully and SMS sent Succesfully"
            elif allowemail == True:
                message = "Created Succesfully and Email sent Succesfully"
            else:
                message = "Created Succesfully"

            result=response(self,request, queryset, total, state, message, error, serializer_class, final_data, action=self.action)
            d = result.get('data')
            app = d.get('Appointment');tre = d.get('Treatment')
            if apt_lst != [] and trt_lst != []:

                for appt in app:
                    appt['appt_fr_time'] = get_in_val(self, appt['appt_fr_time'])
                    appt['appt_to_time'] = get_in_val(self, appt['appt_to_time'])

                for treat in tre:
                    treat['price'] = "{:.2f}".format(float(treat['price']))
                    treat['start_time'] = get_in_val(self, treat['start_time'])
                    treat['end_time'] = get_in_val(self, treat['end_time'])
                    treat['add_duration'] = get_in_val(self, treat['add_duration'])
                    treat['PIC'] = str(treat['PIC'])
                    if 'room_img' in treat and treat['room_img']:
                        treat['room_img'] = str(ip)+str(treat['room_img'])

                return Response(result, status=status.HTTP_201_CREATED)
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Not Created",'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)               



       
    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk,appt_isactive=True)
        except Appointment.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite 
            app = self.get_object(pk)
            appt = Appointment.objects.filter(pk=app.pk).first()
            if not appt:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)        

            serializer = AppointmentSerializer(app)
            d = serializer.data
            apptdate = datetime.datetime.strptime(str(d['appt_date']), "%Y-%m-%d").strftime("%d-%m-%Y")
            time = get_in_val(self, d['appt_fr_time'])        
            # Booking_details = {"Booking_details":{"Booked_by":d['appt_created_by'],
            # "Source": app.Source_Codeid.source_desc if app.Source_Codeid else "",
            # "Appointment_channel": d['site_name']}}
            # appointment_details = {"Appointment_details":{"Date":d['appt_date'],"Time":time,"Outlet":d['site_name'],
            # "Booking_status":d['appt_status'],"Secondary_Status": d['sec_status']}}
            master = Treatment_Master.objects.filter(Appointment=app).order_by('id')
            treat_lst = []; pay = ""
            for m in master:
                if m.Item_Codeid.srv_duration == 0.0 or m.Item_Codeid.srv_duration == None:
                    srvduration = 60
                else:
                    srvduration = m.Item_Codeid.srv_duration

                stkduration = int(srvduration) + 30

                treat_ids = Treatment.objects.filter(sa_transacno=app.sa_transacno,
                treatment_parentcode=m.treatment_parentcode,Item_Codeid=m.Item_Codeid,
                Site_Codeid=app.ItemSite_Codeid,status="Open").order_by('pk').last()
                # print(treat_ids,treat_ids.pk,"treat_ids")  
                if treat_ids:
                    payment_ids = PosTaud.objects.filter(sa_transacno=treat_ids.sa_transacno,
                    ItemSIte_Codeid__pk=site.pk)
                    if payment_ids:
                        pay = ','.join([p.pay_groupid.pay_group_code for p in payment_ids if p.pay_groupid])

                    value = str(m.course)+"("+str(stkduration)+"Mins)"+str(treat_ids.treatment_parentcode)
                    Status = treat_ids.status
                else:
                    value = str(m.course)+"("+str(stkduration)+"Mins)"  
                    pay = ""
                    Status = m.status

                string = ""
                if m.emp_no:
                    for i in m.emp_no.all():
                        emp_obj = Employee.objects.filter(pk=i.pk,emp_isactive=True).first()
                        if not emp_obj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                        if string == "":
                            string = string + i.emp_name +"["+str(i.emp_code)+"]"
                        elif not string == "":
                            string = string +","+ i.emp_name +"["+str(i.emp_code)+"]"

                val = {"id": m.id,"Start_Time": get_in_val(self, m.start_time),"End_Time": get_in_val(self, m.end_time),
                "Treatment": value,"Duration": get_in_val(self, m.add_duration),"emp_id":emp_obj.pk,"Therapist": string if m.emp_no else "", 
                "Room": m.Trmt_Room_Codeid.displayname if m.Trmt_Room_Codeid else "","Status": Status}

                # treat_lst.append(val)
                # Customer_Request = {"Customer_Request" : app.requesttherapist}
                # Payment = {"Payment" : pay}
                # Remark = {"Remark": {"New_Remark" : app.new_remark, "Remark_Points": app.remark_pts}}
            
            ip = get_client_ip(request)
            customer = appt.cust_noid.pk
            cust = Customer.objects.filter(pk=customer,cust_isactive=True).first()

            if not Customer.objects.filter(pk=customer,cust_isactive=True).exists():
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)        

            queryset = Customer.objects.filter(pk=customer).values('cust_name','cust_code','cust_joindate',
            'cust_pic','cust_dob','Cust_sexesid__itm_name','cust_phone2','cust_email','cust_address',
            'Cust_Classid__class_desc')
            for c in queryset:
                
                if c['cust_joindate']:
                    splt = str(c['cust_joindate']).split(" ") 
                    cust_joindate = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                
                if c['cust_dob']:
                    cust_dob = datetime.datetime.strptime(str(c['cust_dob']), "%Y-%m-%d").strftime("%d-%m-%Y")
                
                custval = {"cust_name":c['cust_name'],"cust_code":c['cust_code'],"cust_joindate":cust_joindate,
                "cust_pic":str(ip)+str(cust.cust_pic.url) if cust.cust_pic else "",
                "cust_dob":cust_dob if c['cust_dob'] else "","cust_sex": c['Cust_sexesid__itm_name'] if c['Cust_sexesid__itm_name'] else "",
                "cust_phone2": c['cust_phone2'] if c['cust_phone2'] else "","cust_email":c['cust_email'] if c['cust_email'] else "",
                "cust_address": c['cust_address'] if c['cust_address'] else "","member_type": c['Cust_Classid__class_desc'] if c['Cust_Classid__class_desc'] else ""}


            # treatment = {"Treatment":treat_lst}
            # data = [Booking_details,appointment_details,Customer_Request,Payment,treatment,Remark]
            data = {"Booking_details":{"Booked_by":d['appt_created_by'] if d['appt_created_by'] else "",
            "Source": app.Source_Codeid.source_desc if app.Source_Codeid else "",
            "Appointment_channel":app.appt_type if app.appt_type else ""},"Appointment_details":{"Date":apptdate if apptdate else "",
            "Time":time,"Outlet":d['site_name'] if d['site_name'] else "",
            "Booking_status":d['appt_status'] if d['appt_status'] else "","Secondary_Status": d['sec_status'] if d['sec_status'] else ""},
            "Customer_Request" : app.requesttherapist if app.requesttherapist else False,"Payment" : pay if pay else "","Treatment":val,
            "Remark": {"New_Remark" : app.new_remark if app.new_remark else "", "Remark_Points": app.remark_pts if app.remark_pts else ""},
            "customer_detail": custval}

            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully ",'error': False, 'data': data}
            return Response(result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def UpdateDetail(self, request, pk=None):
        try:
            app = self.get_object(pk)
            appt = Appointment.objects.filter(pk=app.pk).first()
            if not appt:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)        

            serializer = self.get_serializer(app, data=request.data, partial=True)
            if serializer.is_valid():
                if app.treatmentcode:
                    trmtt_ids = Treatment.objects.filter(treatment_code=app.treatmentcode).first()
                else:   
                    trmtt_ids = None 

                if 'appt_date' in request.data and not request.data['appt_date'] is None:
                    app.appt_date = request.data['appt_date']
                    app.save()
                # if 'appt_fr_time' in request.data and not request.data['appt_fr_time'] is None:
                #     app.appt_fr_time = request.data['appt_fr_time']
                # if 'appt_to_time' in request.data and not request.data['appt_to_time'] is None:
                #     app.appt_to_time = request.data['appt_to_time'] 

                if 'appt_status' in request.data and request.data['appt_status'] == 'Cancelled':
                    if app.appt_status == 'Done':
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Completed Appointment cannot move cancelled!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                    if app.appt_status == 'Cancelled':
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Appointment is cancelled only!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                if 'appt_status' in request.data and request.data['appt_status'] == 'Done':
                    if not app.treatmentcode:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment is not created yet so cannot move Done!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                    if trmtt_ids:
                        if not trmtt_ids.status == "Done":
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Cannot move done because treatment is not in done!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                        if not trmtt_ids.status == "Cancel":
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Cannot move done because treatment is in Cancel!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)        


                treat_data = request.data.pop('Treatment')
                if treat_data:
                    t = treat_data
                    trmt = Treatment_Master.objects.filter(Appointment=appt.pk).first()

                    emp_obj = Employee.objects.filter(pk=t['emp_no'],emp_isactive=True).first()
                    if not emp_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                    for existing in trmt.emp_no.all():
                        trmt.emp_no.remove(existing) 

                    trmt.emp_no.add(emp_obj)

                    if not trmt:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Master does not exist",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                    if request.data['appt_status'] == 'Cancelled':
                        if trmtt_ids:
                            if trmtt_ids.status == "Done":
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Completed Treatment cannot move cancelled!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                            if trmtt_ids.status == "Cancel":
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Treatment is cancelled only!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)        


                    treat_id = Treatment_Master.objects.filter(Appointment=appt.pk).first()
                    if 'add_duration' in t and t['add_duration']:
                        t1 = datetime.datetime.strptime(str(t['add_duration']), '%H:%M')
                        t2 = datetime.datetime(1900,1,1)
                        addduration = (t1-t2).total_seconds() / 60.0

                    if 'start_time' in t and t['start_time']:
                        start_time =  get_in_val(self, t['start_time'])
                        starttime = datetime.datetime.strptime(start_time, "%H:%M")
                        end_time = starttime + datetime.timedelta(minutes = addduration)
                        endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                        treat_id.start_time = t['start_time']
                        treat_id.end_time = endtime
                        treat_id.add_duration = t1
                        app.appt_fr_time = t['start_time']
                        app.appt_to_time = endtime

                    if request.data['appt_status'] == 'Cancelled':
                        treat_id.status = "Cancel"

                    treat_id.save()
                    
                    app.appt_status = request.data['appt_status']
                    app.sec_status = request.data['sec_status']
                    app.emp_noid = emp_obj
                    app.emp_no = emp_obj.emp_code
                    app.emp_name = emp_obj.emp_name
                    app.save()

                if request.data['sec_status'] == "Rescheduled":
                    serializer.save(sec_status="Rescheduled")
                data = serializer.data
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully ",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Invalid Input",'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       
        

    def partial_update(self, request, pk=None):
        try:
            app = self.get_object(pk)
            serializer = self.get_serializer(app, data=request.data, partial=True)
            if serializer.is_valid():
                if 'appt_status' in request.data and request.data['appt_status'] == 'Cancelled':
                    if app.appt_status == 'Done':
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Completed Appointmet cannot move cancelled!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                serializer.save()
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
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
        instance.appt_isactive = False
        instance.appt_status = "Cancelled"
        instance.save()      

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def GetCustomer(self, request): 
        try:
            ip = get_client_ip(request)
            appt = Appointment.objects.filter(pk=request.GET.get('appt_id')).first()
            if not appt:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)        
            customer = appt.cust_noid.pk
            cust = Customer.objects.filter(pk=customer).first()
            if not Customer.objects.filter(pk=customer).exists():
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)        
            queryset = Customer.objects.filter(pk=customer).values('cust_name','cust_code','cust_joindate',
            'cust_pic','cust_dob','Cust_sexesid__itm_name','cust_phone2','cust_email','cust_address',
            'Cust_Classid__class_desc')
            for c in queryset:
                if c['cust_phone2']:
                    c['cust_phone1'] = c['cust_phone2']
                    c.pop('cust_phone2')
                if c['cust_pic']:
                    c['cust_pic'] = str(ip)+str(cust.cust_pic.url)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully ",'error': False, 'data': queryset}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


    @action(detail=False, methods=['get'], name='Staffs', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def Staffs(self, request):
        try:
            # outlet = request.GET.get('Outlet',None)
            # if outlet is None or outlet is '':
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give outlet in parms",'error': True} 
            #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 


            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            outlet = fmspw.loginsite
            emp = fmspw.Emp_Codeid


            site = ItemSitelist.objects.filter(pk=outlet.pk,itemsite_isactive=True).first()
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Site ID does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            if not outlet is None:
              
                date = request.GET.get('date',None)
                if not date:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give appointment date",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                date = parser.parse(date)
                # dt = datetime.datetime.combine(date, datetime.datetime.min.time())
                if fmspw.flgappt == True:
                    emp_siteids = EmpSitelist.objects.filter(Site_Codeid__pk=outlet.pk,isactive=True)
                    staffs = list(set([e.Emp_Codeid.pk for e in emp_siteids if e.Emp_Codeid and e.Emp_Codeid.emp_isactive == True]))
                    emp_queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,
                    show_in_appt=True,show_in_trmt=True) 
                    staffs_f = list(set([e.pk for e in emp_queryset if e.pk and e.emp_isactive == True]))
                    # print(staffs_f,"staffs_f") 
                    month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid__pk__in=staffs_f,
                    site_code=outlet.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007'))
                    final = list(set([e.Emp_Codeid.pk for e in month if e.Emp_Codeid]))
                    queryset = Employee.objects.filter(pk__in=final,emp_isactive=True,show_in_appt=True,
                    show_in_trmt=True).order_by('emp_seq_webappt') 
                    serializer = StaffsAvailableSerializer(queryset, many=True, context={'request': self.request})
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
                    return Response(result, status=status.HTTP_200_OK)
                else:
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': []}
                    return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         

class AppointmentPopup(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')
    serializer_class = AppointmentPopupSerializer

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk,appt_isactive=True)
        except Appointment.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            appointment = self.get_object(pk)
            appt = Appointment.objects.filter(pk=appointment.pk).first()
            if not appt:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            serializer = AppointmentPopupSerializer(appointment)
            data = serializer.data
            master_ids = Treatment_Master.objects.filter(Appointment=appointment).order_by('id').first()
            # print(master_ids,master_ids.pk,"master_ids")
            treat_ids = Treatment.objects.filter(sa_transacno=appointment.sa_transacno,
            treatment_parentcode=master_ids.treatment_parentcode,Item_Codeid=master_ids.Item_Codeid,
            Site_Codeid=appointment.ItemSite_Codeid,status="Open",cust_code=appointment.cust_no).order_by('pk').last()
            # print(treat_ids,treat_ids.pk,"treat_ids")
            if treat_ids:
                treatment = treat_ids.course+" "+"["+str(treat_ids.times)+"]"
                acc_ids = TreatmentAccount.objects.filter(ref_transacno=treat_ids.sa_transacno,
                treatment_parentcode=treat_ids.treatment_parentcode,Site_Codeid=appointment.ItemSite_Codeid,
                type__in=('Deposit', 'Top Up')).order_by('id').last()
                # print(acc_ids.id,acc_ids.balance,acc_ids.outstanding,"acc_ids")
                data['treatment'] = treatment
                data['balance_available'] = "{:.2f}".format(float(acc_ids.balance))
                data['outstanding'] = "{:.2f}".format(float(acc_ids.outstanding))
                data['payment_amount'] = "{:.2f}".format(float(acc_ids.deposit))
            else:
                data['treatment'] = ""
                data['balance_available'] = 0.0
                data['outstanding'] = 0.0
                data['payment_amount'] = 0.0 

            data['appt_fr_time'] = get_in_val(self, data['appt_fr_time']) 
            data['appt_to_time'] = get_in_val(self, data['appt_to_time'])        
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully ",'error': False, 'data': data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def partial_update(self, request, pk=None):
        try:
            appobj = self.get_object(pk)
            serializer = self.get_serializer(appobj, data=request.data, partial=True)
            if serializer.is_valid():
                if 'appt_remark' in request.data and not request.data['appt_remark'] is None:
                    serializer.appt_remark = request.data['appt_remark']
                if 'requesttherapist' in request.data and not request.data['requesttherapist'] is None:
                    serializer.requesttherapist =  request.data['requesttherapist']
                if 'appt_status' in request.data and not request.data['appt_status'] is None:
                    if 'appt_status' in request.data and request.data['appt_status'] == 'Cancelled':
                        if app.appt_status == 'Done':
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Completed Appointmet cannot move cancelled!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    serializer.appt_status = request.data['appt_status']
        
                serializer.save()
            
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully ",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Invalid Input",'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

class AppointmentRecurViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')
    serializer_class = AppointmentRecurrSerializer

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk,appt_isactive=True)
        except Appointment.DoesNotExist:
            raise Exception('Appointment Does not Exist') 

    
    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            appobj = self.get_object(pk)
            master_ids = Treatment_Master.objects.filter(Appointment=appobj,site_code=site.itemsite_code).order_by('id').first()
            if not master_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Master does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

                        
            if appobj.appt_date < date.today():
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Past Date Appointment Update is not Allowed !",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)   

            if appobj.appt_status == "Block":
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Blocked Appointment Update is not Allowed !",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if not appobj.recur_linkcode:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Recurring Appointment Update is not Allowed !",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if 'Room_Codeid' in request.data and request.data['Room_Codeid']:
                if not request.data['Room_Codeid'] is None:
                    room_ids = Room.objects.filter(id=request.data['Room_Codeid'],site_code=site.itemsite_code,isactive=True).first()
                    if not room_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if 'add_duration' in request.data and request.data['add_duration']:
                if not request.data['add_duration'] is None:  
                    t1 = datetime.datetime.strptime(str(request.data['add_duration']), '%H:%M')
                    t2 = datetime.datetime(1900,1,1)
                    addduration = (t1-t2).total_seconds() / 60.0

            if 'start_time' in request.data and request.data['start_time']:
                if not request.data['start_time'] is None: 
                    start_time =  get_in_val(self, request.data['start_time'])
                    starttime = datetime.datetime.strptime(start_time, "%H:%M")
                    end_time = starttime + datetime.timedelta(minutes = addduration)
                    endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                    master_ids.start_time = request.data['start_time']
                    master_ids.end_time = endtime
                    master_ids.add_duration = t1
                    appobj.appt_fr_time = request.data['start_time']
                    appobj.appt_to_time = endtime
            
            if request.data['item_id']:
                stockobj = Stock.objects.filter(pk=request.data['item_id'],item_isactive=True).first()
                if not stockobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock Id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # if request.data['emp_id']:   
            #     emp_obj = Employee.objects.filter(pk=request.data['emp_id'],emp_isactive=True).first()
            #     if not emp_obj:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
            #         return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            #     prev_appts = Appointment.objects.filter(appt_date=request.data['appt_date'],
            #     emp_no=emp_obj.emp_code).order_by('-pk').exclude(pk=appobj.pk)
            #     if prev_appts:
            #         check_ids = Appointment.objects.filter(appt_date=request.data['appt_date'],emp_no=emp_obj.emp_code,
            #         ).filter(Q(appt_to_time__gt=request.data['start_time']) & Q(appt_fr_time__lt=request.data['end_time'])).exclude(pk=appobj.pk)
            #         # print(check_ids,"check_ids")
            #         if check_ids:
            #             msg = "StartTime {0} EndTime {1} Service {2}, Employee {3} Already have appointment for this time".format(str(request.data['start_time']),str(request.data['end_time']),str(stockobj.item_name),str(emp_obj.display_name))
            #             result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
            #             return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
        
             
            if self.request.GET.get('type',None) == "all":
                apptl_ids = Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code,appt_isactive=True
                ).exclude(appt_status__in=['Done','Cancelled']).order_by('-appt_date')
                # print(apptl_ids,"apptl_ids")
            else:
                if not request.data['recur_ids'] or request.data['recur_ids'] == []:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Recurring Appointment!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
                request.data['recur_ids'].append(appobj.pk)

                apptl_ids = Appointment.objects.filter(pk__in=request.data['recur_ids'],appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code,appt_isactive=True
                ).exclude(appt_status__in=['Done','Cancelled']).order_by('-appt_date')
                # print(apptl_ids,"apptl_ids")   

               
            if apptl_ids:
                for i in apptl_ids:
                    appt = Appointment.objects.filter(pk=i.pk).update(appt_status=request.data['appt_status'] if request.data['appt_status'] else i.appt_status,
                    Room_Codeid=room_ids if request.data['Room_Codeid'] and room_ids else i.Room_Codeid,
                    room_code=room_ids.room_code if request.data['Room_Codeid'] and room_ids else i.room_code, 
                    sec_status=request.data['sec_status'] if request.data['sec_status'] else i.sec_status,
                    appt_fr_time=request.data['start_time'] if request.data['start_time'] else i.appt_fr_time,
                    appt_to_time=endtime if request.data['end_time'] else i.appt_to_time,
                    item_code=stockobj.item_code if request.data['item_id'] else i.item_code,
                    appt_remark=request.data['item_text'] if request.data['item_text'] else stockobj.item_desc,
                    # emp_noid=emp_obj if request.data['emp_id'] else i.emp_noid,
                    # emp_no=emp_obj.emp_code if request.data['emp_id'] else i.emp_no,
                    # emp_name=emp_obj.emp_name if request.data['emp_id'] else i.emp_name,
                    requesttherapist=request.data['requesttherapist'] if request.data['requesttherapist'] else i.requesttherapist,
                    )
                    
                    m_id = Treatment_Master.objects.filter(Appointment__pk=i.pk).first()   
                    master = Treatment_Master.objects.filter(Appointment__pk=i.pk).update(
                    Trmt_Room_Codeid=room_ids if request.data['Room_Codeid'] and room_ids else m_id.Trmt_Room_Codeid,
                    trmt_room_code=room_ids.room_code if request.data['Room_Codeid'] and room_ids else m_id.trmt_room_code,
                    start_time=request.data['start_time'] if request.data['start_time'] else m_id.start_time,
                    end_time=endtime if request.data['end_time'] else m_id.end_time,
                    add_duration=t1 if request.data['add_duration'] else m_id.add_duration,
                    Item_Codeid=stockobj if request.data['item_id'] else m_id.Item_Codeid, 
                    item_code=stockobj.item_code if request.data['item_id'] else m_id.item_code,
                    course=stockobj.item_desc if request.data['item_id'] else m_id.course,
                    requesttherapist=request.data['requesttherapist'] if request.data['requesttherapist'] else m_id.requesttherapist,
                    )
                    # if 'emp_id' in request.data and request.data['emp_id']:
                    #     if not request.data['emp_id'] is None:  
                    #         for existing in m_id.emp_no.all():
                    #             m_id.emp_no.remove(existing) 
                    #         m_id.emp_no.add(emp_obj)
    

                
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully ",'error': False}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

class AppointmentResourcesViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')
    serializer_class = AppointmentResourcesSerializer

    def get_object(self, pk):
        try:
            return Appointment.objects.get(pk=pk,appt_isactive=True)
        except Appointment.DoesNotExist:
            raise Exception('Appointment Does not Exist') 

    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            appointment = self.get_object(pk)
            appt = Appointment.objects.filter(pk=appointment.pk,appt_isactive=True,itemsite_code=site.itemsite_code).first()
            if not appt:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            serializer = AppointmentResourcesSerializer(appointment, context={'request': self.request})
            data = serializer.data
            master_ids = Treatment_Master.objects.filter(Appointment=appointment,site_code=site.itemsite_code).order_by('id').first()
            
            start_time = get_in_val(self, master_ids.start_time) 
            end_time = get_in_val(self, master_ids.end_time) 
            add_duration = get_in_val(self, master_ids.add_duration) 
            # print(appointment.recur_linkcode,"appointment.recur_linkcode")
            recur_lst = []
            if appointment.recur_linkcode:
                apptl_ids = Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appointment.recur_linkcode,
                cust_noid=appointment.cust_noid,itemsite_code=site.itemsite_code,appt_isactive=True
                ).exclude(pk=appointment.pk).order_by('-appt_date')
                # print(apptl_ids,"apptl_ids")
                recur_lst = [
                    {  
                        'id':i.pk,
                        'date': datetime.datetime.strptime(str(i.appt_date), "%Y-%m-%d").strftime("%d/%m/%Y"),
                        'appt_status': i.appt_status,
                        'sec_status' : i.sec_status if i.sec_status else "", 
                        'room': i.Room_Codeid.displayname if i.Room_Codeid and i.Room_Codeid.displayname else "",
                        'room_id':i.Room_Codeid.pk if i.Room_Codeid and i.Room_Codeid.pk else "",
                        'start_time': get_in_val(self, i.appt_fr_time),
                        'end_time': get_in_val(self, i.appt_to_time),
                        'item_name': i.appt_remark,
                        'emp_name':i.emp_noid.display_name,
                        'emp_id':i.emp_noid.pk,
                        'requesttherapist':i.requesttherapist,'recur_days': i.recurring_days if i.recurring_days else "",
                        'recur_qty': i.recurring_qty if i.recurring_qty else "",
                    } 
                    for i in apptl_ids
                    ]

            for i in recur_lst:
                masterids = Treatment_Master.objects.filter(Appointment__pk=i['id'],
                site_code=site.itemsite_code).order_by('id').first()
                # print(masterids.Item_Codeid.pk,"masterids.Item_Codeid.pk")
                i['Item_Codeid'] = masterids.Item_Codeid.pk if masterids.Item_Codeid else "",
                i['add_duration'] = get_in_val(self, masterids.add_duration)
                # print(i,"ii")

            sys_obj = Systemsetup.objects.filter(title='Appointment Remark').first()    
            value = ""
            if sys_obj.value_data == 'APPEND ONLY':
                value = True
            elif sys_obj.value_data == 'FULL EDIT':
                value = False     
 

            trt_lst = []
            if master_ids and appointment:
                appt_date = datetime.datetime.strptime(str(data['appt_date']), "%Y-%m-%d").strftime("%d/%m/%Y")
                appt_data = {'appt_date':appt_date,
                'cust_name':data['cust_name'] if 'cust_name' in data and data['cust_name'] else "",
                'cust_id':data['cust_noid'] if 'cust_noid' in data and data['cust_noid'] else "",
                'booking_status':data['appt_status'],
                'channel': appointment.Appt_typeid.appt_type_desc if appointment.Appt_typeid and appointment.Appt_typeid.appt_type_desc else "",
                'channel_id': appointment.Appt_typeid.pk if appointment.Appt_typeid and appointment.Appt_typeid.pk else "",
                'ori_remark':data['new_remark'],'edit_remark':"",
                'source':appointment.Source_Codeid.source_desc if appointment.Source_Codeid and appointment.Source_Codeid.source_desc else "",
                'source_id':appointment.Source_Codeid.pk if appointment.Source_Codeid and appointment.Source_Codeid.pk else "",
                'room':appointment.Room_Codeid.displayname if appointment.Room_Codeid and appointment.Room_Codeid.displayname else "",
                'room_id':appointment.Room_Codeid.pk if appointment.Room_Codeid and appointment.Room_Codeid.pk else "",
                'secondary_status': data['sec_status'],'start_time':start_time,'end_time':end_time,
                'item_name':appointment.appt_remark,'Item_Codeid': master_ids.Item_Codeid.pk if master_ids.Item_Codeid else "",'add_duration':add_duration,
                'emp_name':appointment.emp_noid.display_name,'emp_id':appointment.emp_noid.pk,
                'requesttherapist':appointment.requesttherapist,'recur_days': appointment.recurring_days if appointment.recurring_days else "",
                'recur_qty': appointment.recurring_qty if appointment.recurring_qty else "",
                'checktype' : master_ids.checktype,'treat_parentcode': master_ids.treat_parentcode,
                'recur_lst':recur_lst ,
                'remark_setting' : value
                } 
                
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully ",'error': False, 
                'data': appt_data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message) 

    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            appobj = self.get_object(pk)
            apptstatus = appobj.appt_status
            if request.data['recur_qty'] == 0 or request.data['recur_days'] == 0:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Recurring Days / Recurring Qty should not be 0",
                'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            master_ids = Treatment_Master.objects.filter(Appointment=appobj,site_code=site.itemsite_code).order_by('id').first()
            if not master_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Master does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

                        
            if appobj.appt_date < date.today():
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Past Date Appointment Update is not Allowed !",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)   

            if appobj.appt_status == "Block":
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Blocked Appointment Update is not Allowed !",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)   

          
            emp_obj = Employee.objects.filter(pk=request.data['emp_id'],emp_isactive=True).first()
            if not emp_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)        

            stockobj = Stock.objects.filter(pk=request.data['item_id'],item_isactive=True).first()
            if not stockobj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock Id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            #customer Validation
            custprev_appts = Appointment.objects.filter(appt_date=request.data['appt_date'],
            cust_no=appobj.cust_noid.cust_code).order_by('-pk').exclude(itemsite_code=site.itemsite_code)
            if custprev_appts:
                msg = "This Customer Will have appointment on this day other outlet"
                result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            custprevtime_appts = Appointment.objects.filter(appt_date=request.data['appt_date'],
            cust_no=appobj.cust_noid.cust_code).filter(Q(appt_to_time__gte=request.data['start_time']) & Q(appt_fr_time__lte=request.data['end_time'])).exclude(pk=appobj.pk).order_by('-pk')
            if custprevtime_appts:
                msg = "This Customer Will have appointment on this day with same time"
                result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        

            #staff having shift/appointment on other branch for the same time
            prev_appts = Appointment.objects.filter(appt_date=request.data['appt_date'],
            emp_no=emp_obj.emp_code).order_by('-pk').exclude(pk=appobj.pk)
            # print(prev_appts,"prev_appts")
            if prev_appts:
                check_ids = Appointment.objects.filter(appt_date=request.data['appt_date'],emp_no=emp_obj.emp_code,
                ).filter(Q(appt_to_time__gt=request.data['start_time']) & Q(appt_fr_time__lt=request.data['end_time'])).exclude(pk=appobj.pk)
                # print(check_ids,"check_ids")
                if check_ids:
                    msg = "StartTime {0} EndTime {1} Service {2}, Employee {3} Already have appointment for this time".format(str(request.data['start_time']),str(request.data['end_time']),str(stockobj.item_name),str(emp_obj.display_name))
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
    

            serializer = self.get_serializer(appobj, data=request.data, partial=True)
            if serializer.is_valid():
                trmtt_ids = False
                if appobj.treatmentcode and appobj.sa_transacno:
                    trmtt_ids = Treatment.objects.filter(treatment_code=app.treatmentcode,
                    sa_transacno=appobj.sa_transacno,site_code=site.itemsite_code).first()
                 
                if 'appt_date' in request.data and request.data['appt_date']:
                    if not request.data['appt_date'] is None:
                        appobj.appt_date = request.data['appt_date']
                        master_ids.treatment_date = request.data['appt_date']

                if 'appt_status' in request.data and request.data['appt_status']:
                    if not request.data['appt_status'] is None:
                        if request.data['appt_status'] in ['Done','Cancelled']:
                            if not appobj.treatmentcode:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment treatmentcode not mapped!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)        


                        if request.data['appt_status'] == 'Cancelled':
                            if appobj.appt_status == 'Done':
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Completed Appointment cannot move cancelled!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                            if appobj.appt_status == 'Cancelled':
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cancelled Appointment cannot move Cancelled again!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)

                            if not trmtt_ids:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cannot move done because treatmentcode,sa_transacno does not exist!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                            if trmtt_ids.status == "Done":
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Cannot move Cancelled because treatment is in Done!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)    

                            if trmtt_ids.status == "Cancel":
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Treatment is cancelled only!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)

                            master_ids.status = "Cancel"
            
    
                        if request.data['appt_status'] == 'Done':
                            if appobj.appt_status == 'Done':
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Done Appointment cannot move Done again!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                            if appobj.appt_status == 'Cancelled':
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cancelled Appointment cannot move Done!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                 
                            
                            if trmtt_ids:
                                if not trmtt_ids.status == "Done":
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Cannot move done because treatment is not in done!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                if trmtt_ids.status == "Done":
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Treatment is Done only!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST)        
    
                            else:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cannot move done because treatmentcode,sa_transacno does not exist!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST) 


                        appobj.appt_status = request.data['appt_status']

                if 'sec_status' in request.data and request.data['sec_status']:
                    if not request.data['sec_status'] is None:
                        appobj.sec_status = request.data['sec_status']   

                if 'Room_Codeid' in request.data and request.data['Room_Codeid']:
                    if not request.data['Room_Codeid'] is None:
                        room_ids = Room.objects.filter(id=request.data['Room_Codeid'],site_code=site.itemsite_code,isactive=True).first()
                        if not room_ids:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)

                        appobj.Room_Codeid = room_ids
                        appobj.room_code = room_ids.room_code  
                        master_ids.Trmt_Room_Codeid = room_ids
                        master_ids.trmt_room_code = room_ids.room_code

                if 'edit_remark' in request.data and request.data['edit_remark']:
                    if not request.data['edit_remark'] is None: 
                        val = appobj.new_remark
                        if str(request.data['edit_remark']) not in val:
                            val += " "+str(request.data['edit_remark'])
                            appobj.new_remark = val

                if 'ori_remark' in request.data and request.data['ori_remark']:
                    if not request.data['ori_remark'] is None:
                        appobj.new_remark = request.data['ori_remark']

                if 'requesttherapist' in request.data and not request.data['requesttherapist'] is None:
                    appobj.requesttherapist =  request.data['requesttherapist']
                    master_ids.requesttherapist = request.data['requesttherapist']
                    # master_ids.save()

                
                if 'emp_id' in request.data and request.data['emp_id']:
                    if not request.data['emp_id'] is None:  
                        for existing in master_ids.emp_no.all():
                            master_ids.emp_no.remove(existing) 

                        appobj.emp_noid = emp_obj
                        appobj.emp_no = emp_obj.emp_code
                        appobj.emp_name = emp_obj.emp_name
                        appobj.save()
                        master_ids.emp_no.add(emp_obj)
                       

                if 'add_duration' in request.data and request.data['add_duration']:
                    if not request.data['add_duration'] is None:  
                        t1 = datetime.datetime.strptime(str(request.data['add_duration']), '%H:%M')
                        t2 = datetime.datetime(1900,1,1)
                        addduration = (t1-t2).total_seconds() / 60.0

                if 'start_time' in request.data and request.data['start_time']:
                    if not request.data['start_time'] is None: 
                        start_time =  get_in_val(self, request.data['start_time'])
                        starttime = datetime.datetime.strptime(start_time, "%H:%M")
                        end_time = starttime + datetime.timedelta(minutes = addduration)
                        endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                        master_ids.start_time = request.data['start_time']
                        master_ids.end_time = endtime
                        master_ids.add_duration = t1
                        appobj.appt_fr_time = request.data['start_time']
                        appobj.appt_to_time = endtime

                        # master_ids.save()
                        
                        # appobj.appt_status = request.data['appt_status']
                        # appobj.sec_status = request.data['sec_status']

                if 'item_id' in request.data and request.data['item_id']:
                    if not request.data['item_id'] is None:
                       
                        appobj.item_code = stockobj.item_code
                        appobj.appt_remark = stockobj.item_desc
                        # appobj.save()
                        master_ids.Item_Codeid = stockobj
                        master_ids.item_code = stockobj.item_code
                        master_ids.course = stockobj.item_desc
                        # master_ids.save()

                if 'item_text' in request.data and request.data['item_text']:
                    if not request.data['item_text'] is None:
                        appobj.appt_remark = request.data['item_text']
                            
        
                # serializer.save()
                master_ids.updated_at = timezone.now()
                appobj.updated_at = timezone.now()

                appobj.save()
                master_ids.save()

                apptlog = AppointmentLog(appt_id=appobj,userid=fmspw.Emp_Codeid,
                username=fmspw.Emp_Codeid.display_name,appt_date=request.data['appt_date'],
                appt_fr_time=request.data['start_time'],appt_to_time=request.data['end_time'],emp_code=emp_obj.emp_code,
                appt_status=request.data['appt_status'],sec_status=request.data['sec_status'],appt_remark=stockobj.item_desc,
                item_code=stockobj.item_code,requesttherapist=request.data['requesttherapist'],
                add_duration=request.data['add_duration'],new_remark=request.data['edit_remark']).save()

                
                if appobj.recurring_qty and request.data['recur_qty']:
                    # print("iff")
                    if appobj.recurring_qty != request.data['recur_qty']:
                        if appobj.recurring_qty > request.data['recur_qty']:
                            # print("iff")
                            r = appobj.recurring_qty - request.data['recur_qty']
                            apptl_ids = Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                            cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code,appt_isactive=True).order_by('-appt_date')[:r].values_list('pk', flat=True)
                            # print(apptl_ids,"apptl_ids")
                            queryapp = Appointment.objects.filter(pk__in=apptl_ids).update(appt_isactive=False)
                            # print(queryapp,"queryapp")

                            Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                            cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code).order_by('appt_date').update(recurring_qty=request.data['recur_qty'])
                            appobj.recurring_qty = request.data['recur_qty']
                            appobj.save()

                        elif appobj.recurring_qty < request.data['recur_qty']:
                            apptlids = Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                            cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code,appt_isactive=True).order_by('appt_date').last()
                            # print(apptlids,"apptl_ids")
                            rem = request.data['recur_qty'] - appobj.recurring_qty
                            datelst = []
                            if request.data['recur_qty']:
                                count = 1
                                while count <= int(rem):
                                    if datelst == []:
                                        date_1 = datetime.datetime.strptime(str(apptlids.appt_date), "%Y-%m-%d")
                                    else:
                                        date_1 = datetime.datetime.strptime(str(datelst[-1]), "%Y-%m-%d")

                                    end_date = (date_1 + datetime.timedelta(days=int(appobj.recurring_days))).strftime("%Y-%m-%d")
                                    datelst.append(end_date)
                                    count+=1
                            
                            # print(datelst,"datelst")
                            if datelst != []:   
                                for e in datelst: 
                                    search_ids = Appointment.objects.filter(appt_date=e,recur_linkcode=appobj.recur_linkcode,
                                    cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code).order_by('appt_date')

                                    if search_ids:
                                        search_ids.update(appt_isactive=True)
                                    else:
                                        recontrol_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=site.pk).first()
                                        reappt_code = str(recontrol_obj.Site_Codeid.itemsite_code)+str(recontrol_obj.control_prefix)+str(recontrol_obj.control_no)
                            
                                        appt_re = Appointment(appt_date=e,cust_noid=appobj.cust_noid,cust_no=appobj.cust_noid.cust_code,cust_name=appobj.cust_noid.cust_name,appt_phone=appobj.cust_noid.cust_phone2,
                                        cust_refer=appobj.cust_noid.cust_refer,Appt_Created_Byid=fmspw,appt_created_by=fmspw.pw_userlogin,
                                        itemsite_code=site.itemsite_code,ItemSite_Codeid=site,source_code=appobj.source_code ,appt_code=reappt_code,new_remark=appobj.new_remark,
                                        emp_noid=appobj.emp_noid,emp_no=appobj.emp_no,emp_name=appobj.emp_name,Room_Codeid=appobj.Room_Codeid,
                                        room_code=appobj.room_code,Source_Codeid=appobj.Source_Codeid,
                                        Appt_typeid=appobj.Appt_typeid,appt_type=appobj.appt_type,requesttherapist=appobj.requesttherapist,
                                        appt_fr_time=appobj.appt_fr_time,appt_to_time=appobj.appt_to_time,item_code=appobj.item_code,appt_remark=appobj.appt_remark,
                                        appt_status="Booking",sec_status=None,recur_linkcode=appobj.recur_linkcode,
                                        recurring_qty=appobj.recurring_qty,recurring_days=appobj.recurring_days)
                                        appt_re.save()

                                        if appt_re.pk:
                                            recontrol_obj.control_no = int(recontrol_obj.control_no) + 1
                                            recontrol_obj.save() 

                                        appt_log = AppointmentLog(appt_id=appt_re,userid=fmspw.Emp_Codeid,
                                        username=fmspw.Emp_Codeid.display_name,appt_date=e,
                                        appt_fr_time=appobj.appt_fr_time,appt_to_time=appobj.appt_to_time,emp_code=appobj.emp_no,
                                        appt_status="Booking",sec_status=None,appt_remark=appobj.appt_remark,
                                        item_code=appobj.item_code,requesttherapist=appobj.requesttherapist,add_duration=master_ids.add_duration,
                                        new_remark=appobj.new_remark)
                                        appt_log.save()


                                        trt_re = Treatment_Master(course=appobj.appt_remark,
                                        Site_Codeid=site,site_code=site.itemsite_code,times="01",treatment_no="01",appt_time=e,
                                        status="Open",cust_code=appobj.cust_noid.cust_code,Cust_Codeid=appobj.cust_noid,cust_name=appobj.cust_noid.cust_name,
                                        Item_Codeid=master_ids.Item_Codeid,item_code=master_ids.Item_Codeid.item_code,Item_Class=master_ids.Item_Class,type="N",
                                        start_time=appobj.appt_fr_time,end_time=appobj.appt_to_time,add_duration=master_ids.add_duration,
                                        duration=master_ids.duration,trmt_room_code=master_ids.trmt_room_code,
                                        Trmt_Room_Codeid=master_ids.Trmt_Room_Codeid,requesttherapist=appobj.requesttherapist,Appointment=appt_re)
                                        trt_re.save()
                                        trt_re.emp_no.add(appobj.emp_noid.pk)     
                                
                                Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                                cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code).order_by('appt_date').update(recurring_qty=request.data['recur_qty'])
                                appobj.recurring_qty = request.data['recur_qty']
                                appobj.save()


                if appobj.recurring_days and request.data['recur_days']:
                    if appobj.recurring_days != request.data['recur_days']:
                        lkids = Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                        cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code,appt_isactive=True).order_by('appt_date')
                        # print(lkids,"lkids")
                        date_lst = []
                        if request.data['recur_days']:
                            cnt = 1
                            while cnt <= len(lkids):
                                if date_lst == []:
                                    date_1 = datetime.datetime.strptime(str(lkids[0].appt_date), "%Y-%m-%d")
                                else:
                                    date_1 = datetime.datetime.strptime(str(date_lst[-1]), "%Y-%m-%d")

                                end_date = (date_1 + datetime.timedelta(days=int(request.data['recur_days']))).strftime("%Y-%m-%d")
                                date_lst.append(end_date)
                                cnt+=1
                        
                        # print(date_lst,"date_lst")
                        if date_lst != []:
                            for idx,req in enumerate(lkids,start=0):
                                req.appt_date = date_lst[idx]
                                req.save()
                        
                            Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appobj.recur_linkcode,
                            cust_noid=appobj.cust_noid,itemsite_code=site.itemsite_code).update(recurring_days=request.data['recur_days'])


                # print(appobj.appt_date,"appobj.appt_date")
                # print(date.today(),"date.today()")

                if 'appt_status' in request.data and request.data['appt_status'] and not request.data['appt_status'] is None:
                    if request.data['appt_status'] == "Arrived":
                        if apptstatus == "Arrived":
                            print(appobj.appt_status,"iff")
                            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully ",'error': False}
                            return Response(result, status=status.HTTP_200_OK)


                        global type_ex
                        cart_date = timezone.now().date()
                        cartex = ItemCart.objects.filter(cust_noid=appobj.cust_noid,cart_date=cart_date,
                        cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')    
                        olst = list(set([e.cart_id for e in cartex if e.cart_id]))
                        if olst != []:
                            cart_id = olst[0]
                            check = "Old"
                        else:
                            check = "New"
                            control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw.loginsite.pk).first()
                            
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
                        
                        cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=appobj.cust_noid,cart_date=cart_date,
                        cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex).order_by('lineno')   
                        if not cartcuids:
                            lineno = 1
                        else:
                            rec = cartcuids.last()
                            lineno = float(rec.lineno) + 1  

                        gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
                        tax_value = 0.0
                        if stockobj.is_have_tax == True:
                            tax_value = gst.item_value

                        
                        if master_ids.checktype == "package":
                            trmt_obj = Treatment.objects.filter(cust_code=appobj.cust_noid.cust_code,site_code=site.itemsite_code,
                            treatment_parentcode=master_ids.treat_parentcode,status='Open').order_by('pk').last()
                            # print(trmt_obj,"trmt_obj")

                            if trmt_obj:

                                check_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,cust_noid=appobj.cust_noid,
                                type="Sales",treatment=trmt_obj,Appointment=appobj)
                                if check_ids:
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Already Exist!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

                            
                                cart = ItemCart(cart_date=cart_date,phonenumber=appobj.cust_noid.cust_phone2,
                                customercode=appobj.cust_noid.cust_code,cust_noid=appobj.cust_noid,lineno=lineno,
                                itemcodeid=stockobj,itemcode=stockobj.item_code,itemdesc=stockobj.item_desc+" "+trmt_obj.treatment_code,
                                quantity=1,price="{:.2f}".format(float(trmt_obj.unit_amount)),
                                sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                                tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                                discount_price=float(trmt_obj.unit_amount) * 1.0,total_price=float(trmt_obj.unit_amount) * 1.0,
                                trans_amt=float(trmt_obj.unit_amount) * 1.0,deposit=0.0,type="Sales",treatment_account=trmt_obj.treatment_account,
                                treatment=trmt_obj,Appointment=appobj)
                                cart.save()

                                tmpcids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_id=appobj.emp_noid)

                                if not tmpcids:
                                    temph = TmpItemHelper(item_name=stockobj.item_desc,helper_id=appobj.emp_noid,
                                    helper_name=appobj.emp_noid.display_name,helper_code=appobj.emp_noid.emp_code,Room_Codeid=appobj.Room_Codeid,
                                    site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
                                    wp1=stockobj.workcommpoints if stockobj.workcommpoints else 0,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,Source_Codeid=appobj.Source_Codeid,
                                    new_remark=appobj.new_remark,workcommpoints=stockobj.workcommpoints)
                                    temph.save()

                                    trmt_obj.helper_ids.add(temph)

                                for s in trmt_obj.helper_ids.all(): 
                                    cart.service_staff.add(s.helper_id)

                                sa = trmt_obj.helper_ids.all().first()
                                cart.sales_staff.add(sa.helper_id)

                                result = {'status': status.HTTP_201_CREATED,"message":"Cart Created Succesfully ",'error': False,
                                'data': cart.cart_id}
                                return Response(result, status=status.HTTP_201_CREATED)

                            else:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Package Parent Code Does not Exist",'error': True}
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)


                        elif master_ids.checktype == "service":

                            check_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,cust_noid=appobj.cust_noid,
                            type="Deposit",Appointment=appobj)
                            if check_ids:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Already Exist!!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)

                            cart = ItemCart(cart_date=cart_date,phonenumber=appobj.cust_noid.cust_phone2,
                            customercode=appobj.cust_noid.cust_code,cust_noid=appobj.cust_noid,lineno=lineno,
                            itemcodeid=stockobj,itemcode=stockobj.item_code,itemdesc=stockobj.item_desc,
                            quantity=1,price="{:.2f}".format(float(stockobj.item_price)),
                            sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                            tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                            discount_price=float(stockobj.item_price) * 1.0,
                            total_price=float(stockobj.item_price) * 1.0,
                            trans_amt=float(stockobj.item_price) * 1.0,
                            deposit=float(stockobj.item_price) * 1.0,
                            type="Deposit",Appointment=appobj)
                            cart.save()

                            tmpcids = TmpItemHelper.objects.filter(itemcart=cart,helper_id=appobj.emp_noid)

                            if not tmpcids:
                                temph = TmpItemHelper(item_name=stockobj.item_desc,helper_id=appobj.emp_noid,
                                helper_name=appobj.emp_noid.display_name,helper_code=appobj.emp_noid.emp_code,Room_Codeid=appobj.Room_Codeid,
                                site_code=site.itemsite_code,times="01",
                                treatment_no="01",wp1=stockobj.workcommpoints if stockobj.workcommpoints else 0,wp2=0.0,wp3=0.0,itemcart=cart,Source_Codeid=appobj.Source_Codeid,
                                new_remark=appobj.new_remark,
                                workcommpoints=stockobj.workcommpoints)

                                temph.save()

                                cart.helper_ids.add(temph)

                            for s in cart.helper_ids.all(): 
                                cart.service_staff.add(s.helper_id)

                            logstaff = Employee.objects.filter(emp_code=fmspw.emp_code,emp_isactive=True).first()

                            if logstaff:
                                mul_ids = Tmpmultistaff.objects.filter(emp_id__pk=logstaff.pk,
                                itemcart__pk=cart.pk)
                                if not mul_ids:
                                    cart.sales_staff.add(logstaff.pk)
                                    ratio = 0.0; salescommpoints = 0.0
                                    if cart.sales_staff.all().count() > 0:
                                        count = cart.sales_staff.all().count()
                                        ratio = float(cart.ratio) / float(count)
                                        salesamt = float(cart.trans_amt) / float(count)
                                        if stockobj.salescommpoints and float(stockobj.salescommpoints) > 0.0:
                                            salescommpoints = float(stockobj.salescommpoints) / float(count)


                                    tmpmulti = Tmpmultistaff(item_code=stockobj.item_code,
                                    emp_code=logstaff.emp_code,ratio=ratio,
                                    salesamt="{:.2f}".format(float(salesamt)),type=None,isdelete=False,role=1,
                                    dt_lineno=cart.lineno,itemcart=cart,emp_id=logstaff,salescommpoints=salescommpoints)
                                    tmpmulti.save()
                                    cart.multistaff_ids.add(tmpmulti.pk)   

                                result = {'status': status.HTTP_201_CREATED,"message":"Cart Created Succesfully ",'error': False,
                                'data': cart.cart_id}
                                return Response(result, status=status.HTTP_201_CREATED)
            
                
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully ",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Invalid Input",'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

class AppointmentEditViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')
    serializer_class = AppointmentEditSerializer

    def get_object(self, pk):
        #try:
            return Appointment.objects.get(pk=pk,appt_isactive=True)
        #except Appointment.DoesNotExist:
        #    raise Exception('Appointment Does not Exist') 

    def retrieve(self, request, pk=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            app = self.get_object(pk)
            appt = Appointment.objects.filter(pk=app.pk,appt_isactive=True,itemsite_code=site.itemsite_code).first()
            if not appt:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            sys_obj = Systemsetup.objects.filter(title='Appointment Remark').first()    
            value = ""
            if sys_obj.value_data == 'APPEND ONLY':
                value = True
            elif sys_obj.value_data == 'FULL EDIT':
                value = False         

            if app.linkcode:
                link_ids = Appointment.objects.filter(appt_date=app.appt_date,linkcode=app.linkcode,cust_noid__pk=app.cust_noid.pk,
                appt_isactive=True,itemsite_code=site.itemsite_code).order_by('appt_fr_time')  
                
                treatlst = []
                for i in link_ids:
                    master_ids = Treatment_Master.objects.filter(Appointment=i,site_code=site.itemsite_code).order_by('id').first()
                    if master_ids:
                        start_time = get_in_val(self, master_ids.start_time) 
                        end_time = get_in_val(self, master_ids.end_time) 
                        add_duration = get_in_val(self, master_ids.add_duration) 

                        treat = {'appt_id': i.pk,'start_time':start_time,'end_time':end_time,'add_duration':add_duration,
                        'item_name': i.appt_remark,'item_id': master_ids.Item_Codeid.pk if master_ids.Item_Codeid else "",
                        'item_text' : None,
                        'emp_name': i.emp_noid.display_name,'emp_id':i.emp_noid.pk,
                        'requesttherapist': i.requesttherapist,
                        'recur_qty': i.recurring_qty if i.recurring_qty else "",
                        'recur_days': i.recurring_days if i.recurring_days else "",
                        'checktype' : master_ids.checktype if master_ids.checktype else "",
                        'treat_parentcode': master_ids.treat_parentcode if master_ids.treat_parentcode else "",
                        }
                        treatlst.append(treat)

                apoint = {'appt_date':app.appt_date,
                    'cust_id': app.cust_noid.pk,'cust_name': app.cust_noid.cust_name, 
                    'appt_status': app.appt_status,
                    'channel_id': app.Appt_typeid.pk if app.Appt_typeid else "",
                    'ori_remark': appt.new_remark,'edit_remark': "",
                    'source_id': appt.Source_Codeid.pk if appt.Source_Codeid else "",
                    'Room_Codeid':appt.Room_Codeid.pk if appt.Room_Codeid  else "",
                    'sec_status': appt.sec_status if appt.sec_status else "",
                    'remark_setting' : value
                    }
                data = {'appointment': apoint,'treatment': treatlst}   

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully ",'error': False, 
                'data': data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)


            # serializer = AppointmentResourcesSerializer(appointment, context={'request': self.request})
            # data = serializer.data
            # master_ids = Treatment_Master.objects.filter(Appointment=appointment,site_code=site.itemsite_code).order_by('id').first()
            
            # start_time = get_in_val(self, master_ids.start_time) 
            # end_time = get_in_val(self, master_ids.end_time) 
            # add_duration = get_in_val(self, master_ids.add_duration) 
            # # print(appointment.recur_linkcode,"appointment.recur_linkcode")
            # recur_lst = []
            # if appointment.recur_linkcode:
            #     apptl_ids = Appointment.objects.filter(appt_date__gte=date.today(),recur_linkcode=appointment.recur_linkcode,
            #     cust_noid=appointment.cust_noid,itemsite_code=site.itemsite_code,appt_isactive=True
            #     ).exclude(pk=appointment.pk).order_by('-appt_date')
            #     # print(apptl_ids,"apptl_ids")
            #     recur_lst = [
            #         {  
            #             'id':i.pk,
            #             'date': datetime.datetime.strptime(str(i.appt_date), "%Y-%m-%d").strftime("%d/%m/%Y"),
            #             'appt_status': i.appt_status,
            #             'sec_status' : i.sec_status if i.sec_status else "", 
            #             'room': i.Room_Codeid.displayname if i.Room_Codeid and i.Room_Codeid.displayname else "",
            #             'room_id':i.Room_Codeid.pk if i.Room_Codeid and i.Room_Codeid.pk else "",
            #             'start_time': get_in_val(self, i.appt_fr_time),
            #             'end_time': get_in_val(self, i.appt_to_time),
            #             'item_name': i.appt_remark,
            #             'emp_name':i.emp_noid.display_name,
            #             'emp_id':i.emp_noid.pk,
            #             'requesttherapist':i.requesttherapist,'recur_days': i.recurring_days if i.recurring_days else "",
            #             'recur_qty': i.recurring_qty if i.recurring_qty else "",
            #         } 
            #         for i in apptl_ids
            #         ]

            # for i in recur_lst:
            #     masterids = Treatment_Master.objects.filter(Appointment__pk=i['id'],
            #     site_code=site.itemsite_code).order_by('id').first()
            #     # print(masterids.Item_Codeid.pk,"masterids.Item_Codeid.pk")
            #     i['Item_Codeid'] = masterids.Item_Codeid.pk if masterids.Item_Codeid else "",
            #     i['add_duration'] = get_in_val(self, masterids.add_duration)
            #     # print(i,"ii")

            # trt_lst = []
            # if master_ids and appointment:
            #     appt_date = datetime.datetime.strptime(str(data['appt_date']), "%Y-%m-%d").strftime("%d/%m/%Y")
            #     appt_data = {'appt_date':appt_date,
            #     'cust_name':data['cust_name'] if 'cust_name' in data and data['cust_name'] else "",
            #     'cust_id':data['cust_noid'] if 'cust_noid' in data and data['cust_noid'] else "",
            #     'booking_status':data['appt_status'],
            #     'channel': appointment.Appt_typeid.appt_type_desc if appointment.Appt_typeid and appointment.Appt_typeid.appt_type_desc else "",
            #     'channel_id': appointment.Appt_typeid.pk if appointment.Appt_typeid and appointment.Appt_typeid.pk else "",
            #     'ori_remark':data['new_remark'],'edit_remark':"",
            #     'source':appointment.Source_Codeid.source_desc if appointment.Source_Codeid and appointment.Source_Codeid.source_desc else "",
            #     'source_id':appointment.Source_Codeid.pk if appointment.Source_Codeid and appointment.Source_Codeid.pk else "",
            #     'room':appointment.Room_Codeid.displayname if appointment.Room_Codeid and appointment.Room_Codeid.displayname else "",
            #     'room_id':appointment.Room_Codeid.pk if appointment.Room_Codeid and appointment.Room_Codeid.pk else "",
            #     'secondary_status': data['sec_status'],'start_time':start_time,'end_time':end_time,
            #     'item_name':appointment.appt_remark,'Item_Codeid': master_ids.Item_Codeid.pk if master_ids.Item_Codeid else "",'add_duration':add_duration,
            #     'emp_name':appointment.emp_noid.display_name,'emp_id':appointment.emp_noid.pk,
            #     'requesttherapist':appointment.requesttherapist,'recur_days': appointment.recurring_days if appointment.recurring_days else "",
            #     'recur_qty': appointment.recurring_qty if appointment.recurring_qty else "",
            #     'checktype' : master_ids.checktype,'treat_parentcode': master_ids.treat_parentcode,
            #     'recur_lst':recur_lst ,
            #     'remark_setting' : value
            #     } 
                
            #     result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully ",'error': False, 
            #     'data': appt_data}
            #     return Response(data=result, status=status.HTTP_200_OK)
            # else:
            #     result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            #     return Response(data=result, status=status.HTTP_200_OK)

        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message) 


    def partial_update(self, request, pk=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            appobj = self.get_object(pk)
            

            if appobj.appt_date < date.today():
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Past Date Appointment Update is not Allowed !",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)   

            if appobj.appt_status == "Block":
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Blocked Appointment Update is not Allowed !",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)   

            # if request.data['recur_qty'] == 0 or request.data['recur_days'] == 0:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Recurring Days / Recurring Qty should not be 0",
            #     'error': False}
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # print(request.data,"request.data")
            appt = request.data.get('appointment')
            treat = request.data.get('treatment')

            for i in treat:
                # print(i['appt_id'],"ytt")

                emp_obj = Employee.objects.filter(pk=i['emp_id'],emp_isactive=True).first()
                if not emp_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)        

                stockobj = Stock.objects.filter(pk=i['item_id'],item_isactive=True).first()
                if not stockobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock Id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                custprev_appts = Appointment.objects.filter(appt_date=appt['appt_date'],
                cust_no=appobj.cust_noid.cust_code).order_by('-pk').exclude(itemsite_code=site.itemsite_code)
                if custprev_appts:
                    msg = "This Customer Will have appointment on this day other outlet"
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 


                if i['appt_id']:
                    app_obj = Appointment.objects.filter(pk=i['appt_id'],appt_isactive=True,itemsite_code=site.itemsite_code).first() 

                    appt_status = app_obj.appt_status 

                    mast_ids = Treatment_Master.objects.filter(Appointment=app_obj,site_code=site.itemsite_code).order_by('id').first()
                    if not mast_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Master does not exist",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                    if appt['appt_status'] == "Arrived" and appt_status != "Arrived": 
                        if str(appobj.appt_date) != str(date.today()):

                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Arrived Appointment date must be today date to move cart",'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)

                        if mast_ids.checktype == "package":  
                            trmt_obj = Treatment.objects.filter(cust_code=appobj.cust_noid.cust_code,site_code=site.itemsite_code,
                            treatment_parentcode=mast_ids.treat_parentcode,status='Open').order_by('pk').last()
                            # print(trmt_obj,"trmt_obj")
                            if not trmt_obj:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Package Parent Code Does not Exist !!",'error': True} 
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)    


                    custprevtime_appts = Appointment.objects.filter(appt_date=appt['appt_date'],
                    cust_no=appobj.cust_noid.cust_code).filter(Q(appt_to_time__gt=i['start_time']) & Q(appt_fr_time__lt=i['end_time'])).exclude(pk=i['appt_id']).order_by('-pk')
                    # print(custprevtime_appts,"custprevtime_appts")
                    if custprevtime_appts:
                        msg = "This Customer Will have appointment on this day with same time"
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        
                    #staff having shift/appointment on other branch for the same time
                    prev_appts = Appointment.objects.filter(appt_date=appt['appt_date'],
                    emp_no=emp_obj.emp_code).order_by('-pk')
                    # print(prev_appts,"prev_appts")
                    
                    if prev_appts:
                        check_ids = Appointment.objects.filter(appt_date=appt['appt_date'],emp_no=emp_obj.emp_code,
                        ).filter(Q(appt_to_time__gt=i['start_time']) & Q(appt_fr_time__lt=i['end_time'])).exclude(pk=i['appt_id'])
                        # print(check_ids,"check_ids")

                        if check_ids:
                            msg = "StartTime {0} EndTime {1} Service {2}, Employee {3} Already have appointment for this time".format(str(i['start_time']),str(i['end_time']),str(stockobj.item_name),str(emp_obj.display_name))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                else:
                    custprevtime_appts = Appointment.objects.filter(appt_date=appt['appt_date'],
                    cust_no=appobj.cust_noid.cust_code).filter(Q(appt_to_time__gt=i['start_time']) & Q(appt_fr_time__lt=i['end_time'])).order_by('-pk')
                    if custprevtime_appts:
                        msg = "This Customer Will have appointment on this day with same time"
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
        
                    #staff having shift/appointment on other branch for the same time
                    prev_appts = Appointment.objects.filter(appt_date=appt['appt_date'],
                    emp_no=emp_obj.emp_code).order_by('-pk')
                    # print(prev_appts,"prev_appts")
                    
                    if prev_appts:
                        check_ids = Appointment.objects.filter(appt_date=appt['appt_date'],emp_no=emp_obj.emp_code,
                        ).filter(Q(appt_to_time__gt=i['start_time']) & Q(appt_fr_time__lt=i['end_time']))
                        # print(check_ids,"check_ids")

                        if check_ids:
                            msg = "StartTime {0} EndTime {1} Service {2}, Employee {3} Already have appointment for this time".format(str(i['start_time']),str(i['end_time']),str(stockobj.item_name),str(emp_obj.display_name))
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                   

            new_remark = None
            if 'edit_remark' in appt and appt['edit_remark']:
                if not appt['edit_remark'] is None: 
                    new_remark = appobj.new_remark
                    if str(appt['edit_remark']) not in val:
                        new_remark += " "+str(appt['edit_remark'])

            if 'ori_remark' in appt and appt['ori_remark']:
                if not appt['ori_remark'] is None:
                    new_remark = appt['ori_remark']


            cartlst = []
            for j in treat: 
                source_ids = False;room_ids = False ; channel_ids = False 

                # print(j['appt_id'],"j['appt_id']")
                emp_obj = Employee.objects.filter(pk=j['emp_id'],emp_isactive=True).first()

                stockobj = Stock.objects.filter(pk=j['item_id'],item_isactive=True).first()

                if not appt['source_id'] is None:
                    source_ids = Source.objects.filter(id=appt['source_id'],source_isactive=True).first()

                if not appt['Room_Codeid'] is None:
                    room_ids = Room.objects.filter(id=appt['Room_Codeid'],site_code=site.itemsite_code,isactive=True).first()

                if not appt['channel_id'] is None:
                    channel_ids = ApptType.objects.filter(pk=appt['channel_id'],appt_type_isactive=True).first()
                        
   
                if j['appt_id']:
                    appt_obj = Appointment.objects.filter(pk=j['appt_id'],appt_isactive=True,itemsite_code=site.itemsite_code).first() 
                    
                    apptstatus = appt_obj.appt_status

                    master_ids = Treatment_Master.objects.filter(Appointment=appt_obj,site_code=site.itemsite_code).order_by('id').first()
                    if not master_ids:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Master does not exist",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                    

                    trmtt_ids = False
                    if appt_obj.treatmentcode and appt_obj.sa_transacno:
                        trmtt_ids = Treatment.objects.filter(treatment_code=app.treatmentcode,
                        sa_transacno=appt_obj.sa_transacno,site_code=site.itemsite_code).first()
                    
                    if 'appt_date' in appt and appt['appt_date']:
                        if not appt['appt_date'] is None:
                            appt_obj.appt_date = appt['appt_date']
                            master_ids.treatment_date = appt['appt_date']

                    if 'appt_status' in appt and appt['appt_status']:
                        if not appt['appt_status'] is None:
                            if appt['appt_status'] in ['Done','Cancelled']:
                                if not appt_obj.treatmentcode:
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment treatmentcode not mapped!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST)        


                            if appt['appt_status'] == 'Cancelled':
                                if appt_obj.appt_status == 'Done':
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Completed Appointment cannot move cancelled!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                if appt_obj.appt_status == 'Cancelled':
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cancelled Appointment cannot move Cancelled again!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

                                if not trmtt_ids:
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cannot move done because treatmentcode,sa_transacno does not exist!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                if trmtt_ids.status == "Done":
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Cannot move Cancelled because treatment is in Done!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST)    

                                if trmtt_ids.status == "Cancel":
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Treatment is cancelled only!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

                                master_ids.status = "Cancel"
                

                            if appt['appt_status'] == 'Done':
                                if appt_obj.appt_status == 'Done':
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Done Appointment cannot move Done again!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                                if appt_obj.appt_status == 'Cancelled':
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cancelled Appointment cannot move Done!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
                                
                                if trmtt_ids:
                                    if not trmtt_ids.status == "Done":
                                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Cannot move done because treatment is not in done!!",'error': True} 
                                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                    if trmtt_ids.status == "Done":
                                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Treatment is Done only!!",'error': True} 
                                        return Response(result, status=status.HTTP_400_BAD_REQUEST)        
        
                                else:
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cannot move done because treatmentcode,sa_transacno does not exist!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 


                            appt_obj.appt_status = appt['appt_status']

                    if 'sec_status' in appt and appt['sec_status']:
                        if not appt['sec_status'] is None:
                            appt_obj.sec_status = appt['sec_status']   

                    if 'Room_Codeid' in appt and appt['Room_Codeid']:
                        if not appt['Room_Codeid'] is None and room_ids:
                            appt_obj.Room_Codeid = room_ids
                            appt_obj.room_code = room_ids.room_code  
                            master_ids.Trmt_Room_Codeid = room_ids
                            master_ids.trmt_room_code = room_ids.room_code

                    if 'source_id' in appt and appt['source_id']:
                        if not appt['source_id'] is None and source_ids:
                            appt_obj.Source_Codeid = source_ids
                            appt_obj.source_code = source_ids.source_code

                    if 'channel_id' in appt and appt['channel_id']:
                        if not appt['channel_id'] is None and channel_ids:
                            appt_obj.Appt_typeid = channel_ids
                            appt_obj.appt_type = channel_ids.appt_type_code
                                
                            
                    if 'edit_remark' in appt and appt['edit_remark']:
                        if not appt['edit_remark'] is None: 
                            val = appt_obj.new_remark
                            if str(appt['edit_remark']) not in val:
                                val += " "+str(appt['edit_remark'])
                                appt_obj.new_remark = val

                    if 'ori_remark' in appt and appt['ori_remark']:
                        if not appt['ori_remark'] is None:
                            appt_obj.new_remark = appt['ori_remark']

                    appt_obj.requesttherapist =  j['requesttherapist']
                    master_ids.requesttherapist = j['requesttherapist']

                    if 'emp_id' in j and j['emp_id']:
                        if not j['emp_id'] is None:  
                            for existing in master_ids.emp_no.all():
                                master_ids.emp_no.remove(existing) 

                            appt_obj.emp_noid = emp_obj
                            appt_obj.emp_no = emp_obj.emp_code
                            appt_obj.emp_name = emp_obj.emp_name
                            master_ids.emp_no.add(emp_obj)
                        

                    if 'add_duration' in j and j['add_duration']:
                        if not j['add_duration'] is None:  
                            t1 = datetime.datetime.strptime(str(j['add_duration']), '%H:%M')
                            t2 = datetime.datetime(1900,1,1)
                            addduration = (t1-t2).total_seconds() / 60.0

                    if 'start_time' in j and j['start_time']:
                        if not j['start_time'] is None: 
                            start_time =  get_in_val(self, j['start_time'])
                            starttime = datetime.datetime.strptime(start_time, "%H:%M")
                            end_time = starttime + datetime.timedelta(minutes = addduration)
                            endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                            master_ids.start_time = j['start_time']
                            master_ids.end_time = endtime
                            master_ids.add_duration = t1
                            appt_obj.appt_fr_time = j['start_time']
                            appt_obj.appt_to_time = endtime

                            
                        
                    if 'item_id' in j and j['item_id']:
                        if not j['item_id'] is None:

                            appt_obj.item_code = stockobj.item_code
                            appt_obj.appt_remark = stockobj.item_desc
                            master_ids.Item_Codeid = stockobj
                            master_ids.item_code = stockobj.item_code
                            master_ids.course = stockobj.item_desc

                    if 'item_text' in j and j['item_text']:
                        if not j['item_text'] is None:
                            appt_obj.appt_remark = j['item_text']

                    if 'checktype' in j and j['checktype']:
                        if not j['checktype'] is None:
                            master_ids.checktype = j['checktype']

                    master_ids.treat_parentcode = j['treat_parentcode']
                        
                    master_ids.updated_at = timezone.now()
                    appt_obj.updated_at = timezone.now()

                else:
                    recontrol_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=site.pk).first()
                    reappt_code = str(recontrol_obj.Site_Codeid.itemsite_code)+str(recontrol_obj.control_prefix)+str(recontrol_obj.control_no)
                            
                            
                    app_nobj = Appointment(appt_date=appt['appt_date'],cust_noid=appobj.cust_noid,cust_no=appobj.cust_noid.cust_code,
                    cust_name=appobj.cust_noid.cust_name,appt_phone=appobj.cust_noid.cust_phone2,
                    cust_refer=appobj.cust_noid.cust_refer,Appt_Created_Byid=fmspw,appt_created_by=fmspw.pw_userlogin,
                    itemsite_code=site.itemsite_code,ItemSite_Codeid=site,source_code=source_ids.source_code if source_ids else None,
                    appt_code=reappt_code,new_remark=new_remark,
                    emp_noid=emp_obj,emp_no=emp_obj.emp_code,emp_name=emp_obj.emp_name,Room_Codeid=room_ids if room_ids else None,
                    room_code=room_ids.room_code if room_ids and room_ids.room_code else None,Source_Codeid=source_ids if source_ids else None,
                    Appt_typeid=channel_ids if channel_ids else None,appt_type=channel_ids.appt_type_code if channel_ids and channel_ids.appt_type_code else None,requesttherapist=j['requesttherapist'],
                    appt_fr_time=j['start_time'],appt_to_time=j['end_time'],item_code=stockobj.item_code,appt_remark=j['item_text'] if j['item_text'] else stockobj.item_desc,
                    appt_status=appt['appt_status'],sec_status=appt['sec_status'],linkcode=appobj.linkcode,link_flag=True)
                    app_nobj.save()

                    if app_nobj.pk:
                        recontrol_obj.control_no = int(recontrol_obj.control_no) + 1
                        recontrol_obj.save() 

                        link_ids = Appointment.objects.filter(linkcode=appobj.linkcode,cust_noid__pk=appobj.cust_noid.pk,
                        appt_isactive=True,itemsite_code=site.itemsite_code).update(link_flag=True)  
                    

                    trt_re = Treatment_Master(course=stockobj.item_desc,price=stockobj.item_price,PIC=stockobj.Stock_PIC,
                    Site_Codeid=site,site_code=site.itemsite_code,times="01",treatment_no="01",appt_time=appt['appt_date'],
                    status="Open",cust_code=appobj.cust_noid.cust_code,Cust_Codeid=appobj.cust_noid,cust_name=appobj.cust_noid.cust_name,
                    Item_Codeid=stockobj,item_code=stockobj.item_code,type="N",
                    start_time=j['start_time'],end_time=j['end_time'],add_duration=j['add_duration'],
                    trmt_room_code=room_ids.room_code if room_ids and room_ids.room_code else None,
                    Trmt_Room_Codeid=room_ids if room_ids else None,requesttherapist=j['requesttherapist'],Appointment=app_nobj,
                    checktype=j['checktype'],treat_parentcode=j['treat_parentcode'])
                    trt_re.save()
                    trt_re.emp_no.add(emp_obj.pk)     


                
                if 'appt_status' in appt and appt['appt_status'] and not appt['appt_status'] is None:
                    # print(appt['appt_status'],appobj.appt_status,"kk")
                    if appt['appt_status'] == "Arrived":
                        # print("IFFF")

                        # if apptstatus == "Arrived":
                        #     result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully ",'error': False}
                        #     return Response(result, status=status.HTTP_200_OK)

                        # print(type(appobj.appt_date), type(date.today()),"date.today()")
                        # print(appobj.appt_date, date.today())

                       
                        global type_ex
                        cart_date = timezone.now().date()
                        cartex = ItemCart.objects.filter(cust_noid=appobj.cust_noid,cart_date=cart_date,
                        cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')    
                        olst = list(set([e.cart_id for e in cartex if e.cart_id]))
                        # print(olst,"olst")

                        if olst != []:
                            cart_id = olst[0]
                            check = "Old"
                        else:
                            check = "New"
                            control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw.loginsite.pk).first()
                            
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
                        
                        cartcuids = ItemCart.objects.filter(isactive=True,cust_noid=appobj.cust_noid,cart_date=cart_date,
                        cart_id=cart_id,cart_status="Inprogress",is_payment=False,sitecodeid=site).exclude(type__in=type_ex).order_by('lineno')   
                        if not cartcuids:
                            lineno = 1
                        else:
                            rec = cartcuids.last()
                            lineno = float(rec.lineno) + 1  

                        gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()
                        tax_value = 0.0
                        if stockobj.is_have_tax == True:
                            tax_value = gst.item_value

                        print(j['appt_id'],"j['appt_id']")

                        if j['appt_id']:
                            # print("iff")
                            treat_type = master_ids
                            # print(treat_type.checktype,"treat_type.checktype")
                            appment = appt_obj
                            # print(appment.pk,"appment")
                        else:
                            # print("else")
                            appment = app_nobj
                            treat_type = Treatment_Master.objects.filter(Appointment=app_nobj,site_code=site.itemsite_code).order_by('id').first()
                            # print(treat_type.checktype,"kk")
                            # print(appment.pk,"appment")

                        
                        if treat_type.checktype == "package":
                            # print("iff package")
                            trmt_obj = Treatment.objects.filter(cust_code=appobj.cust_noid.cust_code,site_code=site.itemsite_code,
                            treatment_parentcode=treat_type.treat_parentcode,status='Open').order_by('pk').last()
                            print(trmt_obj,"trmt_obj")

                            if trmt_obj:
                                # print(trmt_obj,"jkkk")

                                check_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,cust_noid=appobj.cust_noid,
                                type="Sales",treatment=trmt_obj,Appointment=appment)
                                # if check_ids:
                                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Already Exist!!",'error': True} 
                                #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

                                if not check_ids: 
                                    cart = ItemCart(cart_date=cart_date,phonenumber=appobj.cust_noid.cust_phone2,
                                    customercode=appobj.cust_noid.cust_code,cust_noid=appobj.cust_noid,lineno=lineno,
                                    itemcodeid=stockobj,itemcode=stockobj.item_code,itemdesc=stockobj.item_desc+" "+trmt_obj.treatment_code,
                                    quantity=1,price="{:.2f}".format(float(trmt_obj.unit_amount)),
                                    sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                                    tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                                    discount_price=float(trmt_obj.unit_amount) * 1.0,total_price=float(trmt_obj.unit_amount) * 1.0,
                                    trans_amt=float(trmt_obj.unit_amount) * 1.0,deposit=0.0,type="Sales",treatment_account=trmt_obj.treatment_account,
                                    treatment=trmt_obj,Appointment=appment)
                                    cart.save()

                                    # print(cart.pk,"cart pk")

                                    tmpcids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_id=appobj.emp_noid)

                                    if not tmpcids:
                                        temph = TmpItemHelper(item_name=stockobj.item_desc,helper_id=appobj.emp_noid,
                                        helper_name=appobj.emp_noid.display_name,helper_code=appobj.emp_noid.emp_code,Room_Codeid=appobj.Room_Codeid,
                                        site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
                                        wp1=stockobj.workcommpoints if stockobj.workcommpoints else 0,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,Source_Codeid=appobj.Source_Codeid,
                                        new_remark=appobj.new_remark,workcommpoints=stockobj.workcommpoints)
                                        temph.save()

                                        trmt_obj.helper_ids.add(temph)

                                    for s in trmt_obj.helper_ids.all(): 
                                        cart.service_staff.add(s.helper_id)

                                    sa = trmt_obj.helper_ids.all().first()
                                    cart.sales_staff.add(sa.helper_id)

                                    if cart.pk not in cartlst:
                                        cartlst.append(cart.pk)
                                

                        elif treat_type.checktype == "service":
                            # print(appobj.pk,master_ids.checktype,"jjj")

                            check_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,cust_noid=appobj.cust_noid,
                            type="Deposit",Appointment=appment)
                            # if check_ids:
                            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart Already Exist!!",'error': True} 
                            #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

                            if not check_ids: 
                                cart = ItemCart(cart_date=cart_date,phonenumber=appobj.cust_noid.cust_phone2,
                                customercode=appobj.cust_noid.cust_code,cust_noid=appobj.cust_noid,lineno=lineno,
                                itemcodeid=stockobj,itemcode=stockobj.item_code,itemdesc=stockobj.item_desc,
                                quantity=1,price="{:.2f}".format(float(stockobj.item_price)),
                                sitecodeid=site,sitecode=site.itemsite_code,cart_status="Inprogress",cart_id=cart_id,
                                tax="{:.2f}".format(tax_value),check=check,ratio=100.00,
                                discount_price=float(stockobj.item_price) * 1.0,
                                total_price=float(stockobj.item_price) * 1.0,
                                trans_amt=float(stockobj.item_price) * 1.0,
                                deposit=float(stockobj.item_price) * 1.0,
                                type="Deposit",Appointment=appment)
                                cart.save()

                                # print(cart.pk,"cart pk")

                                if cart.pk not in cartlst:
                                    cartlst.append(cart.pk)

                                tmpcids = TmpItemHelper.objects.filter(itemcart=cart,helper_id=appobj.emp_noid)

                                if not tmpcids:
                                    temph = TmpItemHelper(item_name=stockobj.item_desc,helper_id=appobj.emp_noid,
                                    helper_name=appobj.emp_noid.display_name,helper_code=appobj.emp_noid.emp_code,Room_Codeid=appobj.Room_Codeid,
                                    site_code=site.itemsite_code,times="01",
                                    treatment_no="01",wp1=stockobj.workcommpoints if stockobj.workcommpoints else 0,wp2=0.0,wp3=0.0,itemcart=cart,Source_Codeid=appobj.Source_Codeid,
                                    new_remark=appobj.new_remark,
                                    workcommpoints=stockobj.workcommpoints)

                                    temph.save()

                                    cart.helper_ids.add(temph)

                                for s in cart.helper_ids.all(): 
                                    cart.service_staff.add(s.helper_id)

                                logstaff = Employee.objects.filter(emp_code=fmspw.emp_code,emp_isactive=True).first()

                                if logstaff:
                                    mul_ids = Tmpmultistaff.objects.filter(emp_id__pk=logstaff.pk,
                                    itemcart__pk=cart.pk)
                                    if not mul_ids:
                                        cart.sales_staff.add(logstaff.pk)
                                        ratio = 0.0; salescommpoints = 0.0
                                        if cart.sales_staff.all().count() > 0:
                                            count = cart.sales_staff.all().count()
                                            ratio = float(cart.ratio) / float(count)
                                            salesamt = float(cart.trans_amt) / float(count)
                                            if stockobj.salescommpoints and float(stockobj.salescommpoints) > 0.0:
                                                salescommpoints = float(stockobj.salescommpoints) / float(count)


                                        tmpmulti = Tmpmultistaff(item_code=stockobj.item_code,
                                        emp_code=logstaff.emp_code,ratio=ratio,
                                        salesamt="{:.2f}".format(float(salesamt)),type=None,isdelete=False,role=1,
                                        dt_lineno=cart.lineno,itemcart=cart,emp_id=logstaff,salescommpoints=salescommpoints)
                                        tmpmulti.save()
                                        cart.multistaff_ids.add(tmpmulti.pk) 
                    
                if j['appt_id']:
                    appt_obj.save()
                    master_ids.save()
                else:
                    app_nobj.save()
                    trt_re.save()


                apptlog = AppointmentLog(appt_id=appobj,userid=fmspw.Emp_Codeid,
                username=fmspw.Emp_Codeid.display_name,appt_date=appt['appt_date'],
                appt_fr_time=j['start_time'],appt_to_time=j['end_time'],emp_code=emp_obj.emp_code,
                appt_status=appt['appt_status'],sec_status=appt['sec_status'],appt_remark=appobj.appt_remark,
                item_code=stockobj.item_code,requesttherapist=j['requesttherapist'],
                add_duration=j['add_duration'],new_remark=appobj.new_remark).save()

            # print(cartlst,"cartlst") 
            if cartlst != []:
                cart_ids = ItemCart.objects.filter(pk__in=cartlst)
                cartdata = list(set([i.cart_id for i in cart_ids]))
                # print(cartdata,"cartdata")

                result = {'status': status.HTTP_201_CREATED,"message":"Cart Created Succesfully ",'error': False,
                'data': cartdata[0]}
                return Response(result, status=status.HTTP_201_CREATED)

                
            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully ",'error': False}
            return Response(result, status=status.HTTP_200_OK)

        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)     
    
class AppointmentSortAPIView(generics.ListCreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
    serializer_class = AppointmentSortSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        queryset = Employee.objects.none()
        emp = fmspw[0].Emp_Codeid
        site = fmspw[0].loginsite   
    
        if self.request.GET.get('date',None) and not self.request.GET.get('date',None) is None:
            date = self.request.GET.get('date',None)
            date = parser.parse(date)
        else:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            date = parser.parse(date)
    
        if not date:
            raise Exception('Please Select date in calendar view')
        
        if fmspw[0].flgappt == True: 
            #Therapist
            if emp.show_in_appt == True:
                site_list = EmpSitelist.objects.filter(Emp_Codeid=emp,Site_Codeid__pk=site.pk,isactive=True)
                if site_list:
                    month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid=emp,
                    site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()

                    if month:
                        emp_id = month.Emp_Codeid
                        queryset = Employee.objects.filter(pk=emp_id.pk,emp_isactive=True,
                        show_in_appt=True).order_by('emp_seq_webappt')
                        # print(queryset,"queryset")
                        
            #manager -> Therapist,Consultant staffs as Resources
            elif emp.show_in_appt == False:
                emp_siteids = EmpSitelist.objects.filter(Site_Codeid__pk=site.pk,isactive=True)
                staffs = list(set([e.Emp_Codeid.pk for e in emp_siteids if e.Emp_Codeid and e.Emp_Codeid.emp_isactive == True]))
                emp_queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,
                show_in_appt=True) 
                staffs_f = list(set([e.pk for e in emp_queryset if e.pk and e.emp_isactive == True]))
                month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid__pk__in=staffs_f,
                site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007'))
                final = list(set([e.Emp_Codeid.pk for e in month if e.Emp_Codeid]))
                queryset = Employee.objects.filter(pk__in=final,emp_isactive=True,
                show_in_appt=True).order_by('emp_seq_webappt')
        
        return queryset
   
    def list(self, request):
        #try:        
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)     

    def create(self, request):
        #try:
            if not request.data['emp_ids'] or request.data['emp_ids'] == [] or request.data['emp_ids'] is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Employee!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
            queryset = self.filter_queryset(self.get_queryset())
            update_ids = queryset.update(emp_seq_webappt=None)

            serializer = AppointmentSortSerializer(data=request.data)
            if serializer.is_valid():
                emp_ids = request.data['emp_ids']
                # print(emp_ids,"emp_ids")
                if emp_ids:
                    for idx, reqt in enumerate(emp_ids, start=1): 
                        # print(idx,reqt,"reqt")
                        empobj = Employee.objects.filter(pk=reqt,emp_isactive=True,
                        show_in_appt=True).order_by('emp_seq_webappt').first()
                        if not empobj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        empobj.emp_seq_webappt = idx  
                        empobj.save() 

                    result = {'status': status.HTTP_201_CREATED,"message":"Updated Succesfully",
                    'error': False}
                    return Response(result, status=status.HTTP_201_CREATED)
                
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
            'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)     

class ItemDeptViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ItemDept.objects.filter().order_by('-pk')
    serializer_class = Item_DeptSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 36",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)

  
    
class StockListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Stock.objects.filter(item_isactive=True).order_by('-pk')
    serializer_class = StockListSerializer

    def list(self, request):
            # now = time()
            # now = timezone.now()
            # # print(now,"Start")
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
            # sleep(2) 
            queryset = Stock.objects.filter(item_isactive=True, item_div="3").only('item_isactive', 'item_div').order_by('-pk')
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_dept = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None),is_service=True,itm_status=True,itm_showonsales=True).first()
                    if not item_dept:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True,item_div="3",item_dept=item_dept.itm_code).only('item_isactive', 'item_dept','item_div').order_by('-pk')
            
            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(
                        Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None))).order_by('-pk')

            # print(queryset,"queryset")
            if queryset:
                serializer_class = StockListSerializer
                total = len(queryset)
                state = status.HTTP_200_OK
                message = "Listed Succesfully"
                error = False
                data = None
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                v = result.get('data')
                d = v.get('dataList')
                lst = []
                for dat in d:
                    dict_v = dict(dat)
                    stock_obj = Stock.objects.filter(pk=dict_v['id'],item_isactive=True).first()
                    if dict_v['srv_duration'] is None or dict_v['srv_duration'] == 0.0:
                        srvduration = 60
                    else:
                        srvduration = dict_v['srv_duration']     

                    dict_v['name'] = str(dict_v['item_desc'])+" "+"["+str(int(srvduration))+" "+"Mins"+""+"]"
                    dict_v['item_price'] = "{:.2f}".format(float(dict_v['item_price']))

                    # if int(dict_v['srv_duration']) == 0.0 or dict_v['srv_duration'] is None:
                    #     stk_duration = 60
                    # else:
                    #     stk_duration = int(stock_obj.srv_duration)

                    stkduration = int(srvduration) + 30
                    # print(stkduration,"stkduration")

                    hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                    dict_v['add_duration'] = hrs
                    dict_v['srv_duration'] = str(srvduration)+" "+"Mins"
                    lst.append(dict_v)

                # now1 = time()
                # now1 = timezone.now()
                # # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
                # # print(now,"End")
                # total = now1.second - now.second
                # print(total,"total")
                # sleep(2) 
                # print(len(lst),"lst length") 
                v['dataList'] =  lst  
                return Response(result, status=status.HTTP_200_OK)   
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)

class TreatmentApptAPI(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Treatment.objects.filter().order_by('-pk')
    serializer_class = TreatmentApptSerializer

    def list(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            cust_id = self.request.GET.get('cust_id',None)
            serializer_class = TreatmentApptSerializer

            #cust_obj = Customer.objects.filter(pk=cust_id,
            #cust_isactive=True,site_code=site.itemsite_code).first()
            cust_obj = Customer.objects.filter(pk=cust_id,cust_isactive=True,).first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  
            
            queryset_t = Treatment.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code,
            status='Open').order_by('-pk')
            # print(queryset_t,"queryset_t")
            par_lst = list(set([e.treatment_parentcode for e in queryset_t if e.treatment_parentcode]))
            # print(par_lst,"par_lst")

            if par_lst == []:
                result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,  'data': []}
                return Response(data=result, status=status.HTTP_200_OK) 

            lst = [];querylst = []
            if par_lst:
                for p in par_lst:
                    #queryid = Treatment.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code,
                    #treatment_parentcode=p,status='Open').order_by('pk').first()
                    queryid = Treatment.objects.filter(cust_code=cust_obj.cust_code,
                    treatment_parentcode=p,status='Open').order_by('pk').first()
                    if queryid.pk not in querylst:
                        querylst.append(queryid.pk)

                if querylst == []:
                    result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,  'data': []}
                    return Response(data=result, status=status.HTTP_200_OK) 
        
                
                if querylst !=[]:
                    #queryset = Treatment.objects.filter(pk__in=querylst,cust_code=cust_obj.cust_code,site_code=site.itemsite_code).order_by('-pk')
                    queryset = Treatment.objects.filter(pk__in=querylst,cust_code=cust_obj.cust_code).order_by('-pk')
                    total = len(queryset)
                    state = status.HTTP_200_OK
                    message = "Listed Succesfully"
                    error = False
                    data = None
                    result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action='list')
                    v = result.get('data')
                    d = v.get('dataList')
                    # print(d,"DD")

                    lst = []
                    for dat in d:
                        dict_d = dict(dat)
                        if dict_d['id']:
                            query = Treatment.objects.filter(pk=dict_d['id']).order_by('pk').first()
                            # print(query,"query")
                            #open_ids = Treatment.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code,
                            #treatment_parentcode=query.treatment_parentcode,status='Open').order_by('pk').count()
                            open_ids = Treatment.objects.filter(cust_code=cust_obj.cust_code,
                            treatment_parentcode=query.treatment_parentcode,status='Open').order_by('pk').count()
                            if query.item_code:
                                stock = Stock.objects.filter(item_code=query.item_code[:-4],item_isactive=True).first()

                                if stock:
                                    if stock.srv_duration is None or stock.srv_duration == 0.0:
                                        srvduration = 60
                                    else:
                                        srvduration = stock.srv_duration   
                                    
                                    expiry = ""
                                    if query.expiry:
                                        split = str(query.expiry).split(" ")
                                        expiry = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d/%m/%Y")

                                    # stkduration = int(srvduration) + 30
                                    # print(stkduration,"stkduration")

                                    hrs = '{:02d}:{:02d}'.format(*divmod(srvduration, 60))
                                    # dict_v['srv_duration'] = str(srvduration)+" "+"Mins"
                                        
                                    # name = str(stock.item_name)+" "+"["+"("+str(int(srvduration))+")"+"]"+" "+str(query.treatment_parentcode)
                                    name = str(stock.item_name)+" "+str(query.treatment_parentcode)
                                    val = {'item_name':name,'tr_open':open_ids,'tr_done':query.treatment_no,
                                    'price':"{:.2f}".format(float(query.unit_amount)),'expiry':expiry,'add_duration':hrs,
                                    'stock_id':stock.pk,'treatment_parentcode': query.treatment_parentcode}
                                    lst.append(val)  
                           

                    if lst != []:
                        v['dataList'] =  lst  
                        return Response(result, status=status.HTTP_200_OK) 
                    else:
                        result = {'status':status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,  'data': []}
                        return Response(data=result, status=status.HTTP_200_OK)  
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)                                 


class ApptTreatmentDoneHistoryAPI(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ApptTreatmentDoneHistorySerializer
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')

    def list(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            cust_id = self.request.GET.get('cust_id',None)         
            cust_obj = Customer.objects.filter(pk=cust_id,
            cust_isactive=True,site_code=site.itemsite_code).first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 

            serializer_class = ApptTreatmentDoneHistorySerializer
            treat_lst = [];appt_lst = []

            appt_ids = Appointment.objects.filter(appt_date__lte=date.today(),cust_no=cust_obj.cust_code).order_by('-pk')
            # print(appt_ids,len(appt_ids),"appt_ids")
               
            serializer_class = ApptTreatmentDoneHistorySerializer
            total = len(appt_ids)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, appt_ids,total,  state, message, error, serializer_class, data, action='list')
            v = result.get('data')
            d = v.get('dataList')
            for dat in d:
                dict_d = dict(dat)
                a = Appointment.objects.filter(pk=dict_d['id'],appt_isactive=True).first()
                apptdate = datetime.datetime.strptime(str(a.appt_date), "%Y-%m-%d").strftime("%d/%m/%Y")
                appt_fr_time = get_in_val(self, a.appt_fr_time) 
                # print(a.pk,"appt ID")
                treat_ids = Treatment.objects.filter(treatment_date__date=a.appt_date,
                cust_code=cust_obj.cust_code,site_code=a.itemsite_code,status='Done',
                ).order_by('-pk')
                # print(treat_ids,len(treat_ids),"treat_ids")
                if treat_ids:
                    # print("tret iff")
                    for t in treat_ids:
                        # print(t.pk,"t ID")
                        # print(treat_lst,"treat_lst")
                        if not any(d['treat_id'] == t.pk for d in treat_lst):
                            # print("if not")
                            tmphelper_ids = TmpItemHelper.objects.filter(treatment__pk=t.pk).order_by('-pk')
                            # print(tmphelper_ids,"tmphelper_ids iff")
                            service_staffs = ','.join([v.helper_name for v in tmphelper_ids if v.helper_name])                                                
                        
                            val = {'treat_id':t.pk,'date':apptdate,'appt_fr_time':appt_fr_time,'description':a.appt_remark,'staff':a.emp_name,
                            'itemsite_code':a.itemsite_code,'course':t.course,
                            'service_staff':service_staffs,'helper_transacno':tmphelper_ids[0].sa_transacno if tmphelper_ids else ""}
                            if a.pk not in appt_lst:
                                treat_lst.append(val)
                                appt_lst.append(a.pk)
                        else:
                            # print("else")
                            val = {'treat_id':"",'date':apptdate,'appt_fr_time':appt_fr_time,'description':a.appt_remark,'staff':a.emp_name,
                            'itemsite_code':a.itemsite_code,'course':"",
                            'service_staff':"",'helper_transacno':"",}
                            if a.pk not in appt_lst:
                                treat_lst.append(val) 
                                appt_lst.append(a.pk)
                else:
                    # print("treat else")
                    val = {'treat_id':"",'date':apptdate,'appt_fr_time':appt_fr_time,'description':a.appt_remark,'staff':a.emp_name,
                    'itemsite_code':a.itemsite_code,'course':"",
                    'service_staff':"",'helper_transacno':"",}
                    if a.pk not in appt_lst:
                        treat_lst.append(val)
                        appt_lst.append(a.pk)


            # print(treat_lst,len(treat_lst),"treat_lst")
            # print(appt_lst,len(appt_lst),len(d),"appt_lst")
            v['dataList'] =  treat_lst  
            return Response(result, status=status.HTTP_200_OK) 
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)                                 

class UpcomingAppointmentAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = UpcomingAppointmentSerializer
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')

    def list(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            cust_id = self.request.GET.get('cust_id',None)
            # cust_obj = Customer.objects.filter(pk=cust_id,
            # cust_isactive=True,site_code=site.itemsite_code).first()
            cust_obj = Customer.objects.filter(pk=cust_id,cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 
                
            queryset = Appointment.objects.filter(appt_isactive=True,cust_no=cust_obj.cust_code,
            appt_date__gte=date.today()).order_by('-appt_date')
            serializer_class = UpcomingAppointmentSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action='list')
            v = result.get('data')
            d = v.get('dataList')
            lst = []
            for dat in d:
                dict_d = dict(dat)
                if dict_d['appt_date']:
                    dict_d['appt_date'] = datetime.datetime.strptime(str(dict_d['appt_date']), "%Y-%m-%d").strftime("%d/%m/%Y")
                if dict_d['appt_fr_time']:
                    dict_d['appt_fr_time'] = get_in_val(self, dict_d['appt_fr_time']) 
                if dict_d['sec_status'] is None:
                    dict_d['sec_status'] = ""

                lst.append(dict_d)
            v['dataList'] =  lst  
         
            return Response(result, status=status.HTTP_200_OK) 
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)                                 


# Course,Price,Treatment_Date,cust_name,cust_code,Status,Item_Code,appt_time,Site_Code,Item_Class,treatment_details
#     procedure,Appointment

class TreatmentdetailsViewset(viewsets.ModelViewSet): 
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Treatment_Master.objects.filter().order_by('id')
    serializer_class = TreatmentMasterSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)

        site = fmspw[0].loginsite
        empl = fmspw[0].Emp_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)
        if fmspw[0].flgappt == True:
            if empl.show_in_trmt == True:
                queryset = Appointment.objects.filter(pk=self.request.GET.get('appt_id',None),appt_isactive=True,ItemSite_Codeid=site,emp_noid=empl).order_by('pk')
            else:
                if empl.show_in_trmt == False:
                    queryset = Appointment.objects.filter(pk=self.request.GET.get('appt_id',None),appt_isactive=True,ItemSite_Codeid=site).order_by('pk')
        else:
            queryset = Appointment.objects.none()
        return queryset

    def list(self, request):
        ip = get_client_ip(request)
        appt_ids = Appointment.objects.filter(pk=request.GET.get('appt_id',None),appt_isactive=True)
        if not appt_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

        appt_id = self.filter_queryset(self.get_queryset()).first()
        queryset = Treatment_Master.objects.filter(Appointment__pk=appt_id.pk,is_payment=False).order_by('id')
        if queryset:
            serializer = self.get_serializer(queryset, many=True, context={'request': self.request})
            data = serializer.data
            lst = []
            for d in data:
                dict_v = dict(d)
                treatobj = Treatment_Master.objects.filter(id= dict_v['id']).first()
                dict_v['treatment_no'] = treatobj.treatment_no
                # dict_v['appt_time'] = get_in_val(self, dict_v['appt_time'])
                dict_v['start_time'] = get_in_val(self, dict_v['start_time'])
                dict_v['end_time'] = get_in_val(self, dict_v['end_time'])
                dict_v['add_duration'] = get_in_val(self, dict_v['add_duration'])
                dict_v['price'] = "{:.2f}".format(float(dict_v['price']))

                if 'room_img' in d and d['room_img'] is not None:
                    dict_v['room_img'] = str(ip)+str(dict_v['room_img'])
               
                if 'treatment_no' in dict_v and dict_v['treatment_no'] is not None:
                    if '0' in dict_v['treatment_no']:
                        no = str(dict_v['treatment_no']).split('0')
                        if no[0] == '':
                            number = no[1]
                        else:
                            number = request.data['treatment_no'] if 'treatment_no' in request.data else 0    
                    else:
                        number = request.data['treatment_no'] if 'treatment_no' in request.data else 0    

                    dict_v['treatment_no'] = number  
                    dict_v['total'] = "{:.2f}".format(float(dict_v['price']) * int(number))
           
                lst.append(dict_v)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  lst}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 38",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)

    def create(self, request):
        ip = get_client_ip(request)
        state = status.HTTP_400_BAD_REQUEST
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data,context={'request': self.request})
        appt_ids = Appointment.objects.filter(pk=request.data['Appointment'],appt_isactive=True)
        if not appt_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

        app_obj = Appointment.objects.filter(pk=request.data['Appointment']).first()
        stock_obj = Stock.objects.filter(pk=request.data['Item_Codeid'],item_isactive=True).first()
        if not stock_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item code is not avaliable!!",'error': True} 
            raise serializers.ValidationError(result)

        cust_obj = Customer.objects.filter(pk=app_obj.cust_noid.pk,cust_isactive=True).first()
        class_obj = stock_obj.Item_Classid
        site = fmspw[0].Emp_Codeid.Site_Codeid
      
        if serializer.is_valid():
            if int(stock_obj.srv_duration) == 0.0:
                stk_duration = 60
            else:
                stk_duration = int(stock_obj.srv_duration)

            stkduration = int(stk_duration) + 30
            # print(stkduration,"stkduration")

            hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
            # print(hrs,"hrs")
            treat = Treatment_Master.objects.filter(Appointment=app_obj).order_by('id')
            if not treat:
                start_time =  get_in_val(self, app_obj.appt_fr_time)
                starttime = datetime.datetime.strptime(start_time, "%H:%M")
                end_time = starttime + datetime.timedelta(minutes = stkduration)
                endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                duration = hrs
            else:
                start_time = None
                endtime = None
                duration = hrs

            # print(start_time,endtime,duration,"duration")
            serializer.save(course=stock_obj.item_desc,price=stock_obj.item_price,PIC=stock_obj.Stock_PIC,Site_Codeid=app_obj.ItemSite_Codeid,site_code=app_obj.ItemSite_Codeid.itemsite_code,
            status="Open",cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,cust_name=cust_obj.cust_name,Item_Codeid=stock_obj,
            item_code=stock_obj.item_code,Item_Class=class_obj,treatment_details=stock_obj.treatment_details,procedure=stock_obj.procedure,Appointment=app_obj,
            start_time=start_time,end_time=endtime,add_duration=duration,appt_time=str(app_obj.appt_date))
            # treatment_code=treatment_code,treatment_parentcode=treatment_code
            
        
            state = status.HTTP_201_CREATED
            message = "Created Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            d = result.get('data')
            # d['appt_time'] = get_in_val(self, d['appt_time'])
            d['price'] = "{:.2f}".format(float(d['price']))
            return Response(result, status=status.HTTP_201_CREATED)

        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, pk):
        #try:
            return Treatment_Master.objects.get(pk=pk)
        #except Treatment_Master.DoesNotExist:
        #    raise Http404


    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        queryset = None
        total = None
        serializer_class = None
        treat = self.get_object(pk)
        serializer = TreatmentMasterSerializer(treat, context={'request': self.request})
        data = serializer.data
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        d = result.get('data')
        d['price'] = "{:.2f}".format(float(d['price']))
        d['start_time'] = get_in_val(self, d['start_time'])
        d['end_time'] = get_in_val(self, d['end_time'])
        d['add_duration'] = get_in_val(self, d['add_duration'])
        d['PIC'] = str(d['PIC'])
        if 'room_img' in d and d['room_img'] is not None:
            d['room_img'] = str(ip)+str(d['room_img'])
       
        return Response(result, status=status.HTTP_200_OK)

   
def checkvalidate(self, request):
    if not 'treatment_no' in request.data:
        raise serializers.ValidationError("treatment_no Field is required.")
    else:
        if request.data['treatment_no'] is None:
            raise serializers.ValidationError("treatment_no Field is required.")
    if not 'emp_no' in request.data: 
        raise serializers.ValidationError("emp_no Field is required.")
    else:
        if request.data['emp_no'] is None:
            raise serializers.ValidationError("emp_no Field is required.")

    if not 'Trmt_Room_Codeid' in request.data:
        raise serializers.ValidationError("Trmt_Room_Code Field is required.")  
    else:
        if request.data['Trmt_Room_Codeid'] is None:
            raise serializers.ValidationError("Trmt_Room_Code Field is required.")  

    if not 'cus_requests' in request.data:
        raise serializers.ValidationError("cus_requests Field is required.") 
    else:
        if request.data['cus_requests'] is None:
            raise serializers.ValidationError("cus_requests Field is required.") 


           
class TreatmentMasterViewset(viewsets.ModelViewSet): 
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Treatment_Master.objects.filter().order_by('id')
    serializer_class = TreatmentMasterSerializer

    def get_object(self, pk):
        #try:
            return Treatment_Master.objects.get(pk=pk)
        #except Treatment_Master.DoesNotExist:
        #    raise Http404

    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        queryset = None
        total = None
        serializer_class = None
        treat = self.get_object(pk)
        serializer = TreatmentMasterSerializer(treat,context={'request': self.request})
        data = serializer.data
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        d = result.get('data')
        d['price'] = "{:.2f}".format(float(d['price']))
        # d['appt_time'] = get_in_val(self, d['appt_time'])
        d['start_time'] = get_in_val(self, d['start_time'])
        d['end_time'] = get_in_val(self, d['end_time'])
        d['add_duration'] = get_in_val(self, d['add_duration'])
        d['PIC'] = str(d['PIC'])
        if 'room_img' in d and d['room_img'] is not None:
            d['room_img'] = str(ip)+str(d['room_img'])
       
        return Response(result, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        ip = get_client_ip(request)
        checkvalidate(self,request)
        queryset = None
        total = None
        serializer_class = None
        treat_master = self.get_object(pk)
       
        empno = Employee.objects.filter(pk__in=request.data['emp_no'],emp_isactive=True)
        if not empno:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

        room_ids = Room.objects.filter(id=request.data['Trmt_Room_Codeid'],isactive=True)
        if not room_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

       
        serializer = TreatmentMasterSerializer(treat_master, data=request.data, context={'request': self.request}, partial=True)
        if not 'treatment_no' in request.data: 
            msg = "Cart Cannot Proceed without Treatment Qty for %s Treatment!!".format(treat_master.course)
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
            raise serializers.ValidationError(result)
        else:
            if int(request.data['treatment_no']) <= 0:
                msg = "Cart Cannot Proceed without Treatment Qty for %s Treatment!!".format(treat_master.course)
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                raise serializers.ValidationError(result)
            elif request.data['treatment_no'] is None: 
                msg = "Cart Cannot Proceed without Treatment Qty for %s Treatment!!".format(treat_master.course)
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                raise serializers.ValidationError(result)


        if serializer.is_valid():
            if int(request.data['treatment_no']) < 10:
                treatment_no = str(request.data['treatment_no']).zfill(2)
            else:
                treatment_no = request.data['treatment_no']
            # for EmpNo in request.data['emp_no']:
            #     treat_master.emp_no.add(EmpNo)
            #     treat_master.save()
            k = serializer.save(treatment_no=treatment_no,trmt_room_code=room_ids[0].room_code)
            for emp in request.data['emp_no']:
                k.emp_no.add(emp)
           

            state = status.HTTP_200_OK
            message = "Updated Succesfully"
            error = False
            data = serializer.data
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            d = result.get('data')
            d['price'] = "{:.2f}".format(float(d['price']))
            # d['appt_time'] = get_in_val(self, d['appt_time'])
            d['start_time'] = get_in_val(self, d['start_time'])
            d['end_time'] = get_in_val(self, d['end_time'])
            d['add_duration'] = get_in_val(self, d['add_duration'])
            d['PIC'] = str(d['PIC'])
            if d['room_img']:
                d['room_img'] = str(ip)+str(d['room_img'])
            
            return Response(result, status=status.HTTP_200_OK)

        state = status.HTTP_204_NO_CONTENT
        message = "Invalid Input"
        error = True
        data = serializer.errors
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result, status=status.HTTP_200_OK)

    
    # @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated],
    # authentication_classes=[TokenAuthentication])
    # def update_master(self, request, pk=None):
    #     treat_master = self.get_object(pk)
    #     serializer = TreatmentMasterSerializer(treat_master, data=request.data, partial=True, context={'request': self.request})
    #     if 'add_duration' in request.data and not request.data['add_duration'] is None:
    #         app_obj = treat_master.Appointment
    #         master = Treatment_Master.objects.filter(Appointment=app_obj).order_by('id').first()
    #         if serializer.is_valid():
    #             if master.id == treat_master.id:
    #                 t1 = datetime.datetime.strptime(str(request.data['add_duration']), '%H:%M')
    #                 t2 = datetime.datetime(1900,1,1)
    #                 addduration = (t1-t2).total_seconds() / 60.0
    #                 start_time =  get_in_val(self, treat_master.start_time)
    #                 starttime = datetime.datetime.strptime(start_time, "%H:%M")
    #                 end_time = starttime + datetime.timedelta(minutes = addduration)
    #                 endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
    #                 serializer.save(end_time=endtime,add_duration=request.data['add_duration'])
    #                 result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
    #                 return Response(result, status=status.HTTP_200_OK)
    #             else:
    #                 result = {'status': status.HTTP_200_OK,"message":"Please go to reschedule screen to update duration!",'error': False}
    #                 return Response(result, status=status.HTTP_200_OK)

    #             # ids = [m.id for m in master if m]
    #             # last = master.last().id
    #             # flst = []
    #             # start = int(pk)
    #             # # print(pk,type(pk),last,type(last))
    #             # for i in range(start,last+1):
    #             #     flst.append(i)

    #             # vals = Treatment_Master.objects.filter(Appointment=app_obj,id__in=flst).order_by('id').exclude(id=pk)
    #             # for v in vals:
    #             #     if int(v.Item_Codeid.srv_duration) == 0.0:
    #             #         stk_duration = 60
    #             #     else:
    #             #         stk_duration = int(v.Item_Codeid.srv_duration)

    #             #     stkduration = int(stk_duration) + 30
    #             #     hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
    #             #     vstart_time =  get_in_val(self, v.start_time)
    #             #     vstarttime = datetime.datetime.strptime(vstart_time, "%H:%M")
    #             #     vend_time = vstarttime + datetime.timedelta(minutes = stkduration)
    #             #     vendtime = datetime.datetime.strptime(str(vend_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
    #             #     duration = hrs
    #             #     v.start_time = endtime
    #             #     v.end_time = vendtime
    #             #     v.save()

    #             result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
    #             return Response(result, status=status.HTTP_200_OK)


    #     if 'times' in request.data and not request.data['times'] is None:
    #         if 'status' in request.data and not request.data['status'] is None: 
    #             if int(request.data['times']) < 10:
    #                 times = str(request.data['times']).zfill(2)
    #             else:
    #                 times = request.data['times']
    #             treat_all = Treatment.objects.filter(Appointment=treat_master.Appointment,
    #                 treatment_master=treat_master)
    #             if request.data['status'] == "Cancel":
    #                 treat_ids = Treatment.objects.filter(Appointment=treat_master.Appointment,
    #                 treatment_master=treat_master,times=times).first() 
    #                 if not treat_ids:
    #                     result = {'status': status.HTTP_204_NO_CONTENT,"message": "Payment is not not done so cant move treatment done",'error': True, 'data':serializer.errors}
    #                     return Response(result, status=status.HTTP_200_OK)
            
    #                 if treat_ids.status == "Done":
    #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment is in Done Status cant move cancel",'error': True} 
    #                     raise serializers.ValidationError(result)

    #                 if treat_ids.status == "Cancel":
    #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment is in Cancel Status cant move cancel",'error': True} 
    #                     raise serializers.ValidationError(result)

    #                 treat_ids.status = "Cancel" 
    #                 treat_ids.save() 
                    
    #                 length = [t.status for t in treat_all if t.status == 'Cancel']
    #                 if all([t.status for t in treat_all if t.status == 'Cancel']) == 'Cancel' and len(length) == treat_all.count():
    #                     treat_master.status = "Cancel"
    #                     treat_master.save()
    
    #             elif request.data['status'] == "Done":
    #                 app_obj = treat_master.Appointment
    #                 site = app_obj.ItemSite_Codeid

    #                 treat_time = Treatment.objects.filter(Appointment=treat_master.Appointment,
    #                 treatment_master=treat_master,times=times).first()
    #                 cart = ItemCart.objects.filter(Appointment=treat_master.Appointment,treatment=treat_master,itemcodeid=treat_master.Item_Codeid).first() 

    #                 sales_staff = cart.sales_staff.all().first()
    #                 salesstaff = cart.sales_staff.all()

    #                 control_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=site.pk).first()
    #                 if not control_obj:
    #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
    #                     raise serializers.ValidationError(result)
                    
    #                 sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                    
    #                 refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Redeem Service No",Site_Codeid__pk=site.pk).first()
    #                 if not refcontrol_obj:
    #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Redeem Service Control No does not exist!!",'error': True} 
    #                     raise serializers.ValidationError(result)
                    
    #                 sa_transacno_ref =  str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
    #                 fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
                    

    #                 #header creation
    #                 if sales_staff:
    #                     Emp_code = sales_staff.emp_code
    #                     Emp_name = sales_staff.emp_name
    #                 else:
    #                     sales_staff = None
    #                     Emp_code = ""  
    #                     Emp_name = ""
                        
                    
    #                 hdr = PosHaud(cas_name=fmspw.pw_userlogin,sa_transacno=sa_transacno,sa_status="SA",
    #                 sa_totamt=treat_time.unit_amount,sa_totqty=1,sa_totdisc=0.0,sa_totgst=0.0,
    #                 sa_staffnoid=sales_staff,sa_staffno=Emp_code,sa_staffname=Emp_name,sa_custnoid=treat_master.Appointment.cust_noid,sa_custno=treat_master.Appointment.cust_noid.cust_code,
    #                 sa_custname=treat_master.Appointment.cust_noid.cust_name,sa_discuser=None,sa_disctotal=0.0,ItemSite_Codeid=treat_master.Appointment.ItemSite_Codeid,itemsite_code=treat_master.Appointment.ItemSite_Codeid.itemsite_code,
    #                 sa_depositamt=0.0,sa_transacamt=0.0,appt_time=app_obj.appt_fr_time,sa_round=0.0,total_outstanding=0.0,
    #                 trans_user_login=fmspw.pw_password,trans_user_loginid=fmspw,sa_transacno_ref=sa_transacno_ref,Appointment=app_obj,sa_transacno_type="Redeem Service")
    #                 hdr.save()
    #                 # print(hdr.id,"hdr")

    #                 dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=cart.itemcodeid,dt_itemno=cart.itemcodeid.item_code,dt_itemdesc=cart.itemcodeid.item_desc,dt_price=treat_time.unit_amount,
    #                 dt_promoprice=treat_time.unit_amount,dt_amt=treat_time.unit_amount,dt_qty=1.0,dt_discamt=0.0,dt_discpercent=0.0,
    #                 dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),dt_discuser=0.0,
    #                 ItemSite_Codeid=app_obj.ItemSite_Codeid,itemsite_code=app_obj.ItemSite_Codeid.itemsite_code,
    #                 dt_transacamt=0.0,dt_deposit=0.0,dt_lineno=1,appt_time=app_obj.appt_fr_time,Appointment=app_obj,
    #                 st_ref_treatmentcode=treat_time.treatment_code,record_detail_type="TD",gst_amt_collect=0.0)
    #                 dtl.save()
    #                 # print(dtl.id,"dtl")

    #                 desc = str(treat_master.course)
    #                 acc_ids = TreatmentAccount.objects.filter(ref_transacno=treat_time.sa_transacno,treatment_parentcode=treat_time.treatment_parentcode).order_by('id').last()
    #                 balance = acc_ids.balance - treat_time.unit_amount
    #                 if acc_ids.balance < treat_time.unit_amount:
    #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Deposit Amount is not enough to do this service,Kindly do top up",'error': True} 
    #                     raise serializers.ValidationError(result)
    
    #                 #treatment Account creation
    #                 treatacc = TreatmentAccount(Cust_Codeid=app_obj.cust_noid,cust_code=app_obj.cust_noid.cust_code,ref_no=treat_time.treatment_code,description=desc,type='sales',
    #                 amount=-treat_time.unit_amount,balance=balance,User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=treat_time.sa_transacno,
    #                 sa_transacno=sa_transacno,qty=1,outstanding=acc_ids.outstanding,deposit=0.0,treatment_parentcode=treat_time.treatment_parentcode,treatment_code="",
    #                 sa_status="SA",cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
    #                 dt_lineno=1,Site_Codeid=site,site_code=site.itemsite_code,treat_code=treat_time.treatment_parentcode,treatment_master=treat_master)
    #                 treatacc.save()
    #                 # print(treatacc.id,"treatacc")

    #                 treat_time.status = "Done"
    #                 treat_time.save()
    #                 length = [t.status for t in treat_all if t.status == 'Done']
    #                 if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
    #                     treat_master.status = "Done"
    #                     treat_master.save()
    #                 if hdr:
    #                     control_obj.control_no = int(control_obj.control_no) + 1
    #                     control_obj.save()

    #                 result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
    #                 return Response(result, status=status.HTTP_200_OK)

    #     result = {'status': status.HTTP_204_NO_CONTENT,"message":message,'error': True, 'data':serializer.errors}
    #     return Response(result, status=status.HTTP_200_OK)
            

    @action(detail=True, methods=['get'], name='Times', permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def Times(self, request, pk=None):
        treat = self.get_object(pk)
        times_lst = []
        for i in range(1,int(treat.treatment_no)+1):
            times = str(i).zfill(2)
            times_lst.append(times)
        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': times_lst}
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], name='Duration')
    def Duration(self, request): 
        lst = []
        for i in range(0,13):
            for j in range(0, 60, 5):
                hr = str(i).zfill(2)
                mins = str(j).zfill(2)
                output = hr+":"+mins
                lst.append(output)
        res = lst[: len(lst) - 10] 
        res.pop()
        # res[len(res)-1] = "12:00"
        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': res}
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], name='Outlet', permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def Outlet(self, request):
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        emp_siteids = EmpSitelist.objects.filter(Emp_Codeid=fmspw.Emp_Codeid.pk,isactive=True)
        sites = list(set([e.Site_Codeid.pk for e in emp_siteids if e.Site_Codeid and e.Site_Codeid.itemsite_isactive == True]))
        queryset = ItemSitelist.objects.filter(pk__in=sites,itemsite_isactive=True)        
        serializer = ItemSiteListAPISerializer(queryset, many=True)
        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], name='Staffs', permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def Staffs(self, request):
        app_obj = Appointment.objects.filter(pk=self.request.GET.get('Appointment_id',None)).first()
        if not app_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)
        outlet = app_obj.ItemSite_Codeid
        branch = ItemSitelist.objects.filter(pk=outlet.pk,itemsite_isactive=True).first() 
        if not branch:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Outlet Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

        emp_siteids = EmpSitelist.objects.filter(Site_Codeid__pk=branch.pk,isactive=True)
        staffs = list(set([e.Emp_Codeid.pk for e in emp_siteids if e.Emp_Codeid and e.Emp_Codeid.emp_isactive == True]))
        queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,show_in_trmt=True) 
        serializer = StaffsAvailableSerializer(queryset, many=True, context={'request': self.request})
        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
        return Response(result, status=status.HTTP_200_OK)
    
       
    
class AppointmentBookingStatusList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    
    def get(self, request, format=None):
        #try:
            sta_ids = AppointmentStatus.objects.filter(isactive=True,is_secstatus=False)
            primary_lst = [[i.value, i.lable, i.color] for i in sta_ids]

            # primary_lst = [
            #     ('Booking', 'Booking','#f0b5ec'),
            #     ('Waiting', 'Waiting List','#c928f3'),
            #     ('Confirmed', 'Confirmed','#ebef8b'),
            #     ('Cancelled', 'Cancelled','#ff531a'),
            #     ('Arrived', 'Arrived','#42e2c7'),
            #     ('Done', 'Completed','#80c4f8'),
            #     ('LastMinCancel', 'Cancelled Last Minute','#e1920b'),
            #     ('Late', 'Late', '#66d9ff'),
            #     ('No Show', 'No Show','#c56903'),
            # ]

            sec_ids = AppointmentStatus.objects.filter(isactive=True,is_secstatus=True)
            secondary_lst = [[i.value, i.lable, i.color] for i in sec_ids]
            
            # secondary_lst = [
            #     ("Rescheduled", "Rescheduled" ,'#ff80bf'),
            #     ("Notified Once", "Notified Once", '#6600ff'),
            #     ("Notified Twice", "Notified Twice", '#669900')
            # ]
            final = []
            for i in primary_lst:
                val = {'value': i[0] ,'label': i[1], 'color': i[2]}
                final.append(val)
            sec = []
            for s in secondary_lst:
                value = {'value': s[0] ,'label': s[1], 'color': s[2]}
                sec.append(value)    
            treat = [ 
                ('Open', 'Open'),
                ('Done', 'Done'),
                ('Cancel','Cancel'),
            ]   
            treatlst = []
            for t in treat:
                val = {'value': t[0] ,'label': t[1]}
                treatlst.append(val) 

            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,
            'data':  final,'sec_data': sec, 'treat_data':  treatlst}
            return Response(result)
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)     


class StockDetail(APIView):
   
    def get_object(self, pk):
        #try:
            return Stock.objects.get(pk=pk,item_isactive=True)
        #except Stock.DoesNotExist:
        #    raise Http404

    def get(self, request, pk, format=None):
        ip = "http://"+request.META['HTTP_HOST']
        Stock = self.get_object(pk)
        serializer = StockListTreatmentSerializer(Stock)

        appt_ids = Appointment.objects.filter(pk=request.GET.get('Appointment_id',None),appt_isactive=True)
        if not appt_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

        app_obj = Appointment.objects.filter(pk=request.GET.get('Appointment_id',None)).first()
        staffs = [];rooms=[]
        app = Appointment.objects.filter(appt_date=app_obj.appt_date,appt_status="confirmed",ItemSite_Codeid=app_obj.ItemSite_Codeid)
        for a in app:
            trt = Treatment_Master.objects.filter(Appointment=a)
            if trt:
                staffs = list(set([t.emp_no.pk for t in trt if t.emp_no]))
                rooms = list(set([t.Trmt_Room_Codeid.id for t in trt if t.Trmt_Room_Codeid]))
        
        emppic =None; roompic =None
        emp = Employee.objects.filter(skills__in=[pk])
        if emp:
            sel = list(set([e.pk for e in emp if e.pk not in staffs]))
            if sel != []:
                empobj = Employee.objects.filter(pk=sel[0]).first()
                emppic = empobj.emp_pic.url
            else:
                emppic = emp[0].emp_pic.url

        rooms = Room.objects.filter(Site_Codeid=app_obj.ItemSite_Codeid)
        if rooms:
            sel_room = list(set([r.id for r in rooms if r.id not in rooms]))
            if sel_room != []:
                roomobj = Room.objects.filter(id=sel_room[0]).first()
                roompic = roomobj.Room_PIC.url
            else:
                roompic = rooms[0].Room_PIC.url

        data = serializer.data
        if emppic:
            data['staff_image'] = str(ip)+str(emppic)
        if roompic:
            data['room_image'] = str(ip)+str(roompic)
        data['Stock_PIC'] = str(ip)+str(data['Stock_PIC'])
        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': data}
        return Response(result, status=status.HTTP_200_OK)    


class StaffsAvailable(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
    serializer_class = StaffsAvailableSerializer

    def get_queryset(self,queryset):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            raise serializers.ValidationError(result)
        query = queryset

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = query
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 31:
            # queryset = query.filter(defaultSiteCodeid__pk=site.pk).order_by('-pk')
            queryset = query.filter(SiteCodeid__pk=site.pk).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 27:
            empl = fmspw[0].Emp_Codeid
            # queryset = query.filter(defaultSiteCodeid__pk=site.pk,pk=empl.pk).order_by('-pk')
            queryset = query.filter(SiteCodeid__pk=site.pk,pk=empl.pk).order_by('-pk')
        return queryset

    def list(self, request):
        appt_ids = Appointment.objects.filter(appt_date=request.GET.get('Appt_date',None),appt_isactive=True)
        # if not appt_ids:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment date record does not exist!!",'error': True} 
        #     raise serializers.ValidationError(result)

        
        appt_date = self.request.GET.get('Appt_date',None)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
       
        app_ids = Appointment.objects.filter(appt_date=appt_date,ItemSite_Codeid=site).order_by('appt_date')
        emp_lst = []
        for a in app_ids:
            treat_ids = Treatment_Master.objects.filter(Appointment=a).order_by('id')
            for t in treat_ids:
                for i in t.emp_no.all():
                    if i.pk not in emp_lst:
                        emp_lst.append(i.pk)
            
        queryset1 = Employee.objects.filter(pk__in=emp_lst,emp_isactive=True).order_by('-pk')
        sitelist_ids = EmpSitelist.objects.filter(Site_Codeid=site.pk,isactive=True)
        emplist = list(set([r.Emp_Codeid.pk for r in sitelist_ids if r.Emp_Codeid]))
        queryset2 = Employee.objects.filter(pk__in=emplist,emp_isactive=True).order_by('-pk')

        queryset = queryset1 | queryset2
        new_queryset = self.filter_queryset(self.get_queryset(queryset))
        # new_queryset = queryset2
        # print(new_queryset,"new_queryset")

        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        if new_queryset:
            serializer = self.get_serializer(new_queryset, many=True, context={'request': self.request})
            data = serializer.data
            for d in data:
                lst = []
                treat_ids = Treatment_Master.objects.filter(emp_no=d['id'],Appointment__appt_date=appt_date).order_by('pk')
                app_lst = list(set([t.Appointment.pk for t in treat_ids if t.Appointment]))
                value = str(len(app_lst))+" "+"Appointments Today"
                if len(app_lst)==0:
                    value = "1 Appointments Today"
                d['value'] = value
                for app in Appointment.objects.filter(pk__in=app_lst,ItemSite_Codeid=site).order_by('appt_date'):
                    time = get_in_val(self, app.appt_fr_time)
                    totime = get_in_val(self, app.appt_to_time)
                    val = {'time': str(time)+" "+"-"+" "+str(totime),'cust_name':app.cust_noid.cust_name}
                    lst.append(val)
                d['appointment'] = lst   
            # print(data,"data")
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': data}
        else:
            serializer = self.get_serializer(context={'request': self.request})
            result = {'status': status.HTTP_204_NO_CONTENT,"message":message,'error': False,'data': []}
        return Response(data=result, status=status.HTTP_200_OK)

class UsersList(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request, format=None):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        system_setup = Systemsetup.objects.filter(title='CID',value_name='Currency Code').first()
        if system_setup.value_data:
            currency = system_setup.value_data
        else:
            currency = "$"
        
        foc = 1
        system_setup = Systemsetup.objects.filter(title='SYSTEM SETTING',value_name='Allow FOC Login').first()
        if system_setup.value_data:
            if system_setup.value_data == "FALSE":
                foc = 0

        token = Token.objects.filter(user=self.request.user).first()
        data = {'username':self.request.user.username,'currency':currency,'foc':foc,'token':token.key,
        'role':fmspw.LEVEL_ItmIDid.level_name,'branch': fmspw.loginsite.itemsite_desc if fmspw.loginsite else "",
        'service_sel': fmspw.loginsite.service_sel, 'service_text': fmspw.loginsite.service_text}
        result = {'status': status.HTTP_200_OK,"message":"Listed Sucessfully",'error': False,'data':data}
        return Response(result, status=status.HTTP_200_OK)

class PaytableListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Paytable.objects.filter(pay_isactive=True).order_by('-pk')
    serializer_class = PaytableSerializer

    def list(self, request):
        queryset = Paytable.objects.filter(pay_isactive=True,pay_groupid__pk=request.GET.get('pay_groupid',None)).order_by('-pk')
        print(queryset,"request")
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":message,'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)

def postaud_calculation(self, request, queryset):
    fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
    if not self.request.GET.get('sitecodeid',None) is None:
        site = ItemSitelist.objects.filter(pk=self.request.GET.get('sitecodeid',None),itemsite_isactive=True).first()
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Site ID does not exist!!",'error': True} 
            raise serializers.ValidationError(result)
    else:
        site = fmspw.loginsite

    cart_ids = queryset
    gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
    subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0; 
    trans_amt=0.0 ;deposit_amt =0.0; tax_amt = 0.0; billable_amount=0.0;balance=0.0
    for c in cart_ids:
        balance += float(c.deposit)
        print(balance,"balance")
        if c.type != "Exchange":
            # total = "{:.2f}".format(float(c.price) * int(c.quantity))
            subtotal += float(c.total_price)
            discount_amt += float(c.discount_amt) * int(c.quantity)
            additional_discountamt += float(c.additional_discountamt)
            trans_amt += float(c.trans_amt)
            deposit_amt += float(c.deposit)

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

    calcgst = 0
    if gst:
        calcgst = gst.item_value
    if calcgst > 0:
        sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
        if sitegst:
            if sitegst.site_is_gst == False:
                calcgst = 0
    # print(calcgst,"0 calcgst")

    if calcgst > 0:
        if gst.is_exclusive == True:
            # tax_amt = deposit_amt * (gst.item_value / 100)
            # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
            tax_amt = balance * (calcgst / 100)
            billable_amount = "{:.2f}".format(balance + tax_amt)
        else:
            billable_amount = "{:.2f}".format(balance)
            # tax_amt = deposit_amt * gst.item_value / (100+gst.item_value)
            tax_amt = balance * calcgst / (100+calcgst)
        itemvalue = "{:.2f}".format(float(calcgst))
    else:
        # billable_amount = "{:.2f}".format(deposit_amt)
        billable_amount = "{:.2f}".format(balance)
        tax_amt = 0
        itemvalue = 0

    # print(request.data,"request_data")
    totaltax=0
    linetax=0
    if request.data is not None:
        for rgt in request.data:
            paytablegt = Paytable.objects.filter(pk=rgt['pay_typeid'],pay_isactive=True).first()
            stringgt = paytablegt.gt_group
            st_newgt= "".join(stringgt.split())
            linetax=0
            if st_newgt == 'GT1': 
                if calcgst > 0:
                    if gst.is_exclusive == True:
                        linetax = rgt['pay_amt'] * (calcgst/ 100)
                    else:
                        linetax = rgt['pay_amt'] * calcgst / (100+calcgst)
            totaltax+=linetax

    # print(totaltax,"totaltax")
    if totaltax>0:
        tax_amt = totaltax
    sub_total = "{:.2f}".format(float(subtotal))
    round_val = float(round_calc(billable_amount)) # round()
    billable_amount = float(billable_amount) + round_val 
    sa_Round = round_val

    discount = discount_amt + additional_discountamt

    now = date.today()
    time = datetime.datetime.now().strftime('%H:%M')  #  Time like '23:12:05'
   
    sa_transacno = cart_ids.first().sa_transacno

    value = {'date':now,'time':time,'billed_by':fmspw.pw_userlogin,'bill_no':sa_transacno,
    'subtotal':sub_total,'discount': "{:.2f}".format(float(discount)),'trans_amt': "{:.2f}".format(float(trans_amt)),
    'deposit_amt': "{:.2f}".format(float(balance)),'tax_amt':"{:.2f}".format(float(tax_amt)),
    'tax_lable': "Tax Amount"+"("+str(itemvalue)+" "+"%"+")",'sa_Round': "{:.2f}".format(float(sa_Round)),
    'billable_amount': "{:.2f}".format(float(billable_amount)),'tot_deposit':"{:.2f}".format(float(deposit_amt))}
    return value
    
    
class postaudViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = PosTaud.objects.filter().order_by('-pk')
    serializer_class = PostaudSerializer

    def get_queryset(self):
        global type_ex
        cart_date = timezone.now().date()

        request = self.request
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
      
        site = fmspw[0].loginsite

        empl = fmspw[0].Emp_Codeid

        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
        cart_id = request.GET.get('cart_id',None)

        if fmspw[0].flgsales == True:
            queryset = ItemCart.objects.filter(isactive=True).order_by('id')
            # if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            #    queryset = ItemCart.objects.filter(isactive=True).order_by('id')
            # elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [31,27]:
            #    queryset = ItemCart.objects.filter(isactive=True,sitecode=site).order_by('id')

            queryset = queryset.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
            cart_status="Inprogress",isactive=True,is_payment=False).exclude(type__in=type_ex).order_by('id')
        else:
            queryset = ItemCart.objects.none()

        return queryset

    def list(self, request):
        global type_ex
        cart_date = timezone.now().date()
        if request.GET.get('cart_date',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give cart date",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('cust_noid',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Customer ID",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
        if not cust_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        cart_id = request.GET.get('cart_id',None)
        if cart_id is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content cart_id is not given",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        request = self.request
       
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
       
        site = fmspw[0].loginsite

        empl = fmspw[0].Emp_Codeid
        
        cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
        cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
        # print(cartc_ids,"cartc_ids")
        if cartc_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 1",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        balance=0
        exchange_ids = queryset.filter(type='Exchange')
        if exchange_ids:  
            balance = sum([i.deposit for i in queryset])   
            # print(balance,"balance")
            if balance <= 0.0:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Payment checkout is not possible",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
        value = postaud_calculation(self, request, queryset)
        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':value}
        return Response(data=result, status=status.HTTP_200_OK)


    def create(self, request):
        # try:
            cart_date = timezone.now().date()
            global type_ex
            request = self.request
            if request.GET.get('cart_date',None) is None:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give cart date",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if request.GET.get('cust_noid',None) is None:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Customer ID",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            cart_id = request.GET.get('cart_id',None)
            if cart_id is None:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content cart_id is not given",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            
            site = fmspw.loginsite
            code_site = site.itemsite_code

            empl = fmspw.Emp_Codeid
        
            cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
            cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
            if cartc_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # New
            cartnew_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
            cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid=site,
            customercode=cust_obj.cust_code).exclude(type__in=type_ex)
            if cartnew_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done for this Customer!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            # New

            gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
            calcgst = 0
            if gst:
                calcgst = gst.item_value
            if calcgst > 0:
                sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                if sitegst:
                    if sitegst.site_is_gst == False:
                        calcgst = 0
            # print(calcgst,"calcgst")

            queryset = self.filter_queryset(self.get_queryset())
            if not queryset:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 2",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
            
            cart_ids = queryset
            value = postaud_calculation(self, request, queryset)
            
            control_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw.loginsite.pk).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
            
            # print(site.pk,"site.pk")
            haudre = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('sa_transacno')
            final = list(set([r.sa_transacno for r in haudre]))
            # print(final,len(final),"final")
            saprefix = control_obj.control_prefix

            lst = []
            # if final != []:
            #    for f in final:
            #        newstr = f.replace(saprefix,"")
            #        new_str = newstr.replace(code_site, "")
            #        lst.append(new_str)
            #        lst.sort(reverse=True)

            #    # print(lst,"lst")
            #    print(lst[0],"lst")
            #    # sa_no = int(lst[0]) + 1
            #    sa_no = int(lst[0][-6:]) + 1
            #    sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(sa_no)
            # else:
            sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)

            # print(cart_ids,"cart_ids")
            depotop_ids = cart_ids.filter(type__in=['Deposit','Top Up'])
            # print(depotop_ids,"depotop_ids")
            depo_ids = cart_ids.filter(type='Deposit')
            topup_ids = cart_ids.filter(type='Top Up')
            sales_ids = cart_ids.filter(type='Sales') 
            exchange_ids = cart_ids.filter(type='Exchange') 
            # print(sales_ids,"sales_ids")
            # print(depotop_ids,"depotop_ids")

            checkgt=[]
            # print(request.data,"request.data")
            for rgt in request.data:
                paytablegt = Paytable.objects.filter(pk=rgt['pay_typeid'],pay_isactive=True).first()
                stringgt = paytablegt.gt_group
                st_newgt= "".join(stringgt.split())
                if st_newgt == 'GT1': 
                    checkgt.append("GT1") 
                if st_newgt == 'GT2': 
                    checkgt.append("GT2") 

            # print(checkgt,"checkgt")
            if depotop_ids:
                if "GT1" in checkgt:
                    refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Receipt No",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not refcontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Receipt Control No does not exist!!",'error': True} 
                        raise serializers.ValidationError(result)
                else:
                    refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Non Sales No",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not refcontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Non Sales Control No does not exist!!",'error': True} 
                        raise serializers.ValidationError(result)
                    

                # haudre_ref = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('sa_transacno_ref')
                # final_ref = list(set([r.sa_transacno_ref for r in haudre_ref]))
                # # print(final,len(final),"final")
                # sa_ref_prefix = refcontrol_obj.control_prefix


                # ref_lst = []
                # if final_ref != []:
                #     for fr in final_ref:
                #         new_ref = fr.replace(sa_ref_prefix,"")
                #         new_str_ref = new_ref.replace(code_site, "")
                #         ref_lst.append(new_str_ref)
                #         ref_lst.sort(reverse=True)

                #     # print(lst,"lst")
                #     sa_ref_no = int(ref_lst[0]) + 1
                #     sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(sa_ref_no)
                # else:
                #     sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
                
                sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
            else:
                if sales_ids:
                    refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Redeem Service No",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not refcontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Redeem Service Control No does not exist!!",'error': True} 
                        raise serializers.ValidationError(result)
                    
                    sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)

            for ca in cart_ids.filter(type='Deposit'):
                if ca.itemcodeid.Item_Divid.itm_code == '1':
                    uom = ItemUom.objects.filter(pk=ca.item_uom.pk,uom_isactive=True).first()
                    if not uom:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"ItemUom ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if int(ca.itemcodeid.item_div) == 3 and ca.itemcodeid.item_type == 'PACKAGE' and ca.is_foc == False:
                    if float(ca.deposit) == 0.0:
                        pamsg = "{0} Package Product can not be 0.00".format(str(ca.itemcodeid.item_name))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":pamsg,'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            poshaud_ids = PosHaud.objects.filter(sa_transacno=sa_transacno,sa_custno=cust_obj.cust_code,
            ItemSite_Codeid__pk=site.pk,sa_transacno_ref=sa_transacno_ref)
            if poshaud_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Already Created!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            pos_haud_ids = PosHaud.objects.filter(sa_transacno=sa_transacno,sa_custno=cust_obj.cust_code,
            ItemSite_Codeid__pk=site.pk)
            if pos_haud_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Already Created!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            for ctl in cartc_ids:
                #,itemcart__pk=ctl.pk
                pos_daud_ids = PosDaud.objects.filter(sa_transacno=sa_transacno,dt_itemnoid=ctl.itemcodeid,
                ItemSite_Codeid__pk=site.pk,dt_lineno=ctl.lineno)
                if pos_daud_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosDaud Already Created!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
              
              
            pay_amt = 0.0  ; taud_ids = []; check=[]
            # satransacno = request.GET.get('satransacno',None)
            for r in request.data:
                paytable = Paytable.objects.filter(pk=r['pay_typeid'],pay_isactive=True).first()
                pay_amt += float(r['pay_amt'])
                string = paytable.pay_groupid.pay_group_code
                st_new= "".join(string.split())
                print(st_new,"st_new")
                if st_new == 'CASH':
                    if "CASH" not in check:
                        check.append("CASH")
                    else:    
                        if "CASH" in check: 
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Double Cash Pay Not Allowed!!",'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                if st_new == 'CARD': 
                    check.append("CARD") 
                if str(st_new) == 'Credit': 
                    check.append("CREDIT")
                if str(st_new) == 'Credit Note': 
                    check.append("CREDIT")
                if str(st_new) == 'CreditNote': 
                    check.append("CREDIT")
                if str(st_new) == 'PREPAID':
                    check.append("PREPAID")
                if str(st_new) == 'OLD BILL':
                    check.append("OLD BILL")
                if str(st_new) == 'E-WALLET':
                    check.append("E-WALLET")
                if str(st_new) == 'VOUCHER':
                    check.append("VOUCHER")

            # print(check,"check")
            id_itm = dict(Counter(check))
            # print(id_itm,"id_itm")

            # print(len(request.data),"Length")
            # print(pay_amt,value['billable_amount']) 
            tcheck = list(set(check)) 
            #prepaid will not add gst 7%

            # if pay_amt < float(value['billable_amount']) or pay_amt > float(value['billable_amount']):
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Pay amount should be equal to billable amount!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            add = 0.0
            value['tax_amt'] = 0
            for idx, req in enumerate(request.data, start=1): 
                # print(idx,"idx")
                paytable = Paytable.objects.filter(pk=req['pay_typeid'],pay_isactive=True).first()
                # stringgetgt = paytablegt.gt_group
                pay_ids = Paytable.objects.filter(pk=req['pay_typeid'],pay_isactive=True)
                if not pay_ids:
                    msg = "Paytable ID %s is does not exist!!".format(req['pay_typeid'])
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                    raise serializers.ValidationError(result)

                serializer_one = self.get_serializer(data=req)
                #pos_taud creation
                if serializer_one.is_valid():
                    # pay_gst = (float(req['pay_amt']) / (100+gst.item_value)) * gst.item_value
                    pay_gst = 0
                    # stnewgetgt= "".join(stringgetgt.split())
                    # print(paytable.gt_group,"paytable.gt_group")
                    # if stnewgetgt == 'GT1':
                    amount = float(req['pay_amt'])
                    if paytable.gt_group == 'GT1': 
                        if calcgst > 0:
                            if gst.is_exclusive == True:
                                pay_gst = float(req['pay_amt']) * (gst.item_value / 100)
                            else:
                                pay_gst = (float(req['pay_amt']) * gst.item_value ) / (100+gst.item_value)
                            amount = float(req['pay_amt']) - pay_gst
                            value['tax_amt'] += pay_gst
                    print(value['tax_amt'],"tax1")

                    card_no = False
                    if depotop_ids:
                        # ids_taud = PosTaud.objects.filter(sa_transacno=sa_transacno,dt_lineno=idx,
                        # ItemSIte_Codeid__pk=site.pk)
                        ids_taud = PosTaud.objects.filter(sa_transacno=sa_transacno,dt_lineno=idx,
                        ItemSIte_Codeid__pk=site.pk).first()
                        print(ids_taud,"ids_taud")
                        if ids_taud:
                            ids_taud.delete()
                            # result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosTaud Already Created!!",'error': True} 
                            # return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                        taud = serializer_one.save(sa_transacno=sa_transacno,billed_by=fmspw,ItemSIte_Codeid=site,itemsite_code=site.itemsite_code,
                        pay_groupid=paytable.pay_groupid,pay_group=paytable.pay_groupid.pay_group_code,pay_typeid=paytable,pay_type=paytable.pay_code,
                        pay_desc=paytable.pay_description,pay_tendamt=req['pay_amt'],pay_tendrate=1.0,pay_amt=req['pay_amt'],pay_amtrate=1.0,pay_status=1,dt_lineno=idx,
                        pay_actamt=req['pay_amt'],subtotal="{:.2f}".format(float(value['subtotal'])) if value['subtotal'] else 0.0,paychange=0.0,
                        tax="{:.2f}".format(float(value['tax_amt'])) if value['tax_amt'] else 0.0, discount_amt="{:.2f}".format(float(value['discount'])) if value['discount'] else 0.0,
                        billable_amount="{:.2f}".format(float(value['billable_amount'])) if value['billable_amount'] else 0.0,
                        pay_gst_amt_collect="{:.2f}".format(float(pay_gst)),pay_gst="{:.2f}".format(float(pay_gst)))
                        # print(check,"check")
                        # print(taud.pay_premise,taud.credit_debit)

                        if req['prepaid'] == True:
                            # print(req['prepaid'],"ok")
                            # amount = float(req['pay_amt'])
                            splt = str(req['pay_rem1']).split("-")
                            pp_no = splt[0]
                            line_no = splt[1]
                            open_ids = PrepaidAccountCondition.objects.filter(pp_no=pp_no,
                            pos_daud_lineno=line_no).only('pp_no','pos_daud_lineno').first()
                            pac_ids = PrepaidAccount.objects.filter(pp_no=pp_no,line_no=line_no,
                            cust_code=cust_obj.cust_code,status=True).only('pp_no','line_no','site_code','cust_code','status').order_by('pk').last()
                            if pac_ids:
                                if float(req['pay_amt']) > float(pac_ids.remain):
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid pay amt should not be greater than selected prepaid remain!!",'error': True} 
                                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                                remain = float(pac_ids.remain) - float(req['pay_amt'])
                                PrepaidAccount.objects.filter(pk=pac_ids.pk).update(status=False)
                                acc = PrepaidAccountCondition.objects.filter(pk=open_ids.pk).update(use_amt=float(req['pay_amt']),
                                remain=remain)
                                vstatus = True
                                if remain == 0:
                                    vstatus = False
                                prepacc = PrepaidAccount(pp_no=pac_ids.pp_no,pp_type=pac_ids.pp_type,
                                pp_desc=pac_ids.pp_desc,exp_date=pac_ids.exp_date,cust_code=pac_ids.cust_code,
                                cust_name=pac_ids.cust_name,pp_amt=pac_ids.pp_amt,pp_total=pac_ids.pp_total,
                                pp_bonus=pac_ids.pp_bonus,transac_no=sa_transacno,item_no="",use_amt=float(req['pay_amt']),
                                remain=remain,ref1=pac_ids.ref1,ref2=pac_ids.ref2,status=vstatus,site_code=site.itemsite_code,sa_status="SA",exp_status=pac_ids.exp_status,
                                voucher_no=pac_ids.voucher_no,isvoucher=pac_ids.isvoucher,has_deposit=pac_ids.has_deposit,topup_amt=0,
                                outstanding=pac_ids.outstanding,active_deposit_bonus=pac_ids.active_deposit_bonus,topup_no="",topup_date=None,
                                line_no=pac_ids.line_no,staff_name=None,staff_no=None,
                                pp_type2=open_ids.conditiontype2,condition_type1=open_ids.conditiontype1,pos_daud_lineno=pac_ids.line_no,Cust_Codeid=cust_obj,Site_Codeid=site,
                                Item_Codeid=pac_ids.Item_Codeid,item_code=pac_ids.item_code)
                                prepacc.save()

                            check.remove("PREPAID")
                        elif req['pay_typeid'] == 17:
                            # amount = float(req['pay_amt'])
                            # print(req,"req")
                            card_no = req['pay_rem1']
                            # crdobj = CreditNote.objects.filter(credit_code=req['pay_rem1'],cust_code=cust_obj.cust_code,site_code=site.itemsite_code).first()
                            crdobj = CreditNote.objects.filter(credit_code=req['pay_rem1'],cust_code=cust_obj.cust_code).first()
                            # print(card_no,"card_no")
                            if crdobj:
                                # crbalance = float(crdobj.amount) - float(req['pay_amt'])
                                crbalance = float(crdobj.balance) - float(req['pay_amt'])
                                # print(crbalance,"crbalance")
                                if crbalance == 0.0:
                                    crstatus = "CLOSE"
                                elif crbalance < 0.0:
                                    crstatus = "CLOSE" 
                                    crbalance = 0.0   
                                elif crbalance > 0.0:
                                    crstatus = "OPEN"    
                                CreditNote.objects.filter(pk=crdobj.pk).update(balance=crbalance,status=crstatus)

                            check.remove("CREDIT")
                        elif req['pay_typeid'] == 9:
                            card_no = req['pay_rem1']
                            # crdobj = CreditNote.objects.filter(credit_code=req['pay_rem1'],cust_code=cust_obj.cust_code,site_code=site.itemsite_code).first()
                            # crdobj = CreditNote.objects.filter(credit_code=req['pay_rem1'],cust_code=cust_obj.cust_code).first()
                            crdobj = VoucherRecord.objects.filter(voucher_no=req['pay_rem1'],cust_code=cust_obj.cust_code).first()
                            # print(card_no,"card_no")
                            if crdobj:
                                VoucherRecord.objects.filter(pk=crdobj.pk).update(isvalid=False,used=True)

                            check.remove("VOUCHER")
                        elif req['pay_typeid'] == 2:
                        # elif "CASH" in check:

                            # if len(request.data) == 1:
                            #    amount = float(req['pay_amt']) - float(value['tax_amt'])
                            # elif len(request.data) == 2:
                            #    if paytable.pay_groupid.pay_group_code == 'CASH': 
                            #        amount = float(req['pay_amt'])
                            #    elif paytable.pay_groupid.pay_group_code != 'CASH': 
                            #        amount = float(req['pay_amt']) - float(value['tax_amt'])  
                            #        if amount <= 0:
                            #            amount = 0
                            # elif len(request.data) == 3: 
                            #    add += pay_gst
                            #    if paytable.pay_groupid.pay_group_code == 'CASH': 
                            #        amount = float(req['pay_amt']) 
                            #    elif paytable.pay_groupid.pay_group_code != 'CASH': 
                            #        amount = float(req['pay_amt']) - add
                            #        if amount <= 0:
                            #            amount = 0
                            #        add = 0.0

                            check.remove("CASH")

                        else:
                            if "CARD" in check: 
                                check.remove("CARD")
                            if "OLD BILL" in check: 
                                check.remove("OLD BILL")
                            if "E-WALLET" in check: 
                                check.remove("E-WALLET")
                            if "E-WALLET" in check: 
                                check.remove("PREPAID")
                            if "E-WALLET" in check: 
                                 check.remove("CREDIT")
                        
                        # else:
                        # elif "CASH" not in check:
                            # amount = float(req['pay_amt']) - pay_gst
                            if "CARD" in check: 
                                amount = float(req['pay_amt']) - pay_gst
                                check.remove("CARD")
                            if "OLD BILL" in check: 
                                # amount = float(req['pay_amt']) - pay_gst
                                amount = float(req['pay_amt'])
                                check.remove("OLD BILL")
                            if "E-WALLET" in check: 
                                amount = float(req['pay_amt']) - pay_gst
                                check.remove("E-WALLET")
                            if "PREPAID" in check: 
                                 # print(req['prepaid'],"SHOULD NOT")
                                 amount = float(req['pay_amt'])
                                 # card_no = req['pay_rem1']
                                 if req['prepaid'] == True:
                                     splt = str(req['pay_rem1']).split("-")
                                     pp_no = splt[0]
                                     line_no = splt[1]
                                     open_ids = PrepaidAccountCondition.objects.filter(pp_no=pp_no,
                                     pos_daud_lineno=line_no).only('pp_no','pos_daud_lineno').first()
                                     pac_ids = PrepaidAccount.objects.filter(pp_no=pp_no,line_no=line_no,
                                     cust_code=cust_obj.cust_code,status=True).only('pp_no','line_no','site_code','cust_code','status').order_by('pk').last()
                                     if pac_ids:
                                         if float(req['pay_amt']) > float(pac_ids.remain):
                                             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid pay amt should not be greater than selected prepaid remain!!",'error': True} 
                                             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                                         remain = float(pac_ids.remain) - float(req['pay_amt'])
                                         PrepaidAccount.objects.filter(pk=pac_ids.pk).update(status=False)
                                         acc = PrepaidAccountCondition.objects.filter(pk=open_ids.pk).update(use_amt=float(req['pay_amt']),
                                         remain=remain)
                                         # print(pac_ids.Item_Codeid,"pac_ids")
                                         # print(remain,"remain")
                                         vstatus = True
                                         if remain == 0:
                                             vstatus = False
                                         prepacc = PrepaidAccount(pp_no=pac_ids.pp_no,pp_type=pac_ids.pp_type,
                                         pp_desc=pac_ids.pp_desc,exp_date=pac_ids.exp_date,cust_code=pac_ids.cust_code,
                                         cust_name=pac_ids.cust_name,pp_amt=pac_ids.pp_amt,pp_total=pac_ids.pp_total,
                                         pp_bonus=pac_ids.pp_bonus,transac_no=sa_transacno,item_no="",use_amt=float(req['pay_amt']),
                                         remain=remain,ref1=pac_ids.ref1,ref2=pac_ids.ref2,status=vstatus,site_code=site.itemsite_code,sa_status="SA",exp_status=pac_ids.exp_status,
                                         voucher_no=pac_ids.voucher_no,isvoucher=pac_ids.isvoucher,has_deposit=pac_ids.has_deposit,topup_amt=0,
                                         outstanding=pac_ids.outstanding,active_deposit_bonus=pac_ids.active_deposit_bonus,topup_no="",topup_date=None,
                                         line_no=pac_ids.line_no,staff_name=None,staff_no=None,
                                         pp_type2=open_ids.conditiontype2,condition_type1=open_ids.conditiontype1,pos_daud_lineno=pac_ids.line_no,Cust_Codeid=cust_obj,Site_Codeid=site,
                                         Item_Codeid=pac_ids.Item_Codeid,item_code=pac_ids.item_code)
                                         prepacc.save()

                                     check.remove("PREPAID")
                            # if "CREDIT" in check: 
                            #     amount = float(req['pay_amt'])
                            #    
                            #     card_no = req['pay_rem1']
                            #     # crdobj = CreditNote.objects.filter(credit_code=req['pay_rem1'],cust_code=cust_obj.cust_code,site_code=site.itemsite_code).first()
                            #     crdobj = CreditNote.objects.filter(credit_code=req['pay_rem1'],cust_code=cust_obj.cust_code).first()
                            #     print(card_no,"card_no")
                            #     if crdobj:
                            #         # crbalance = float(crdobj.amount) - float(req['pay_amt'])
                            #         crbalance = float(crdobj.balance) - float(req['pay_amt'])
                            #         print(crbalance,"crbalance")
                            #         if crbalance == 0.0:
                            #             crstatus = "CLOSE"
                            #         elif crbalance < 0.0:
                            #             crstatus = "CLOSE" 
                            #             crbalance = 0.0   
                            #         elif crbalance > 0.0:
                            #             crstatus = "OPEN"    
                            #         CreditNote.objects.filter(pk=crdobj.pk).update(balance=crbalance,status=crstatus)

                            #     check.remove("CREDIT")


                            # elif "Credit" in check: 
                            #     amount = float(req['pay_amt']) - pay_gst
                                
                            #     card_no = req['pay_rem1']
                            #     crdobj = CreditNote.objects.filter(credit_code=req['pay_rem1'],
                            # cust_code=cust_obj.cust_code,site_code=site.itemsite_code).first()
                            #     if crdobj:
                            #         crbalance = float(crdobj.amount) - float(req['pay_amt'])
                            #         if crbalance == 0.0:
                            #             crstatus = "CLOSE"
                            #         elif crbalance < 0.0:
                            #             crstatus = "CLOSE" 
                            #             crbalance = 0.0   
                            #         elif crbalance > 0.0:
                            #             crstatus = "OPEN"    
                            #         CreditNote.objects.filter(pk=crdobj.pk).update(balance=crbalance,status=crstatus)

                            #     check.remove("Credit")
                            # elif "PREPAID" in check: 
                            #     amount = float(req['pay_amt'])
                            #     card_no = req['pay_rem1']
                            #     splt = str(req['pay_amt']).split("-")
                            #     print(splt,"splt")
                            #     pp_no = splt[0]
                            #     line_no = splt[1]
                            #     open_ids = PrepaidAccountCondition.objects.filter(pp_no=pp_no,
                            #     pos_daud_lineno=line_no).only('pp_no','pos_daud_lineno').first()
                            #     pac_ids = PrepaidAccount.objects.filter(pp_no=pp_no,line_no=line_no,
                            #     site_code=site.itemsite_code,cust_code=cust_obj.cust_code,status=True).only('pp_no','line_no','site_code','cust_code','status').order_by('pk').last()
                            #     if pac_ids:
                            #         if float(req['pay_amt']) > float(pac_ids.remain):
                            #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Prepaid pay amt should not be greater than selected prepaid remain!!",'error': True} 
                            #             return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                            #         remain = float(pac_ids.remain) - float(req['pay_amt'])
                            #         PrepaidAccount.objects.filter(pk=pac_ids.pk).update(status=False)
                            #         acc = PrepaidAccountCondition.objects.filter(pk=open_ids.pk).update(use_amt=float(req['pay_amt']),
                            #         remain=remain)

                            #         prepacc = PrepaidAccount(pp_no=pac_ids.pp_no,pp_type=pac_ids.pp_type,
                            #         pp_desc=pac_ids.pp_desc,exp_date=pac_ids.exp_date,cust_code=pac_ids.cust_code,
                            #         cust_name=pac_ids.cust_name,pp_amt=pac_ids.pp_amt,pp_total=pac_ids.pp_total,
                            #         pp_bonus=pac_ids.pp_bonus,transac_no=sa_transacno,item_no="",use_amt=float(req['pay_amt']),
                            #         remain=remain,ref1=pac_ids.ref1,ref2=pac_ids.ref2,status=True,site_code=site.itemsite_code,sa_status="SA",exp_status=pac_ids.exp_status,
                            #         voucher_no=pac_ids.voucher_no,isvoucher=pac_ids.isvoucher,has_deposit=pac_ids.has_deposit,topup_amt=0,
                            #         outstanding=pac_ids.outstanding,active_deposit_bonus=pac_ids.active_deposit_bonus,topup_no="",topup_date=None,
                            #         line_no=pac_ids.line_no,staff_name=None,staff_no=None,
                            #         pp_type2=open_ids.conditiontype2,condition_type1=open_ids.conditiontype1,pos_daud_lineno=pac_ids.line_no,Cust_Codeid=cust_obj,Site_Codeid=site,
                            #         Item_Codeid=pac_ids.itemcodeid,item_code=pac_ids.itemcodeid.item_code)
                            #         prepacc.save()

                            #     check.remove("PREPAID")

    
                        depo_type = DepositType(sa_transacno=sa_transacno,pay_group=paytable.pay_groupid.pay_group_code,
                        pay_type=paytable.pay_code,amount="{:.2f}".format(float(amount)),card_no=card_no,pay_desc=paytable.pay_description,
                        pay_tendcurr=None,pay_tendrate=1.0,site_code=site.itemsite_code,pos_taud_lineno=idx) 
                        # print(depo_type.id,"depo_type") 
                           
                        if taud:
                            depo_type.save()
                            taud_ids.append(taud.pk)
                    else:
                        if sales_ids:
                            idstaud = PosTaud.objects.filter(sa_transacno=sa_transacno,
                            dt_lineno=idx,ItemSIte_Codeid__pk=site.pk)
                            if idstaud:
                                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosTaud Already Created!!",'error': True} 
                                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                            taud = serializer_one.save(sa_transacno=sa_transacno,billed_by=fmspw,ItemSIte_Codeid=site,itemsite_code=site.itemsite_code,
                            pay_groupid=paytable.pay_groupid,pay_group=paytable.pay_groupid.pay_group_code,pay_typeid=paytable,pay_type=paytable.pay_code,
                            pay_desc=paytable.pay_description,pay_tendamt=req['pay_amt'],pay_tendrate=1.0,pay_amt=req['pay_amt'],pay_amtrate=1.0,pay_status=1,dt_lineno=idx,
                            pay_actamt=0.0,subtotal="{:.2f}".format(float(value['subtotal'])) if value['subtotal'] else 0.0,paychange=0.0,
                            tax=0.0, discount_amt="{:.2f}".format(float(value['discount'])) if value['discount'] else 0.0,
                            billable_amount=0.0,pay_gst_amt_collect=0.0,pay_gst=0.0)
                            #print(taud,"taud")
                            # print(taud.pay_premise,taud.credit_debit)
                            if taud:
                                taud_ids.append(taud.pk)

            if cart_ids.filter(type='Exchange').exists():
                sum_ex_depo = sum([i.deposit for i in cart_ids.filter(type='Exchange')])
                outstanding = (float(value['trans_amt']) - float(value['deposit_amt'])) - abs(sum_ex_depo)
            else:
                outstanding =  float(value['trans_amt']) - float(value['deposit_amt'])

            #detail creation
            id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
            outstanding_new = 0.0

            if depo_ids:
                depo = invoice_deposit(self, request, depo_ids, sa_transacno, cust_obj, outstanding)
                for dep in depo:
                    if dep not in id_lst:
                        id_lst.append(dep) 
            if topup_ids:
                topup = invoice_topup(self, request, topup_ids, sa_transacno, cust_obj, outstanding)
                for toup in topup:
                    if toup not in id_lst:
                        id_lst.append(toup) 

            if sales_ids:
                salev = invoice_sales(self, request, sales_ids, sa_transacno, cust_obj, outstanding)
                for sal in salev:
                    if sal not in id_lst:
                        id_lst.append(sal) 
            
            if exchange_ids:
                exproduct = invoice_exchange(self, request, exchange_ids, sa_transacno, cust_obj, outstanding)
                for ex in exproduct:
                    if ex not in id_lst:
                        id_lst.append(ex) 

            alsales_staff = cart_ids.first().sales_staff.all().first()


            # for idx, c in enumerate(cart_ids, start=1):
            #     if idx == 1:
            #         alsales_staff = c.sales_staff.all().first()

            #     # print(c,"cc")
            #     outstanding_acc =  float(c.trans_amt) - float(c.deposit)
            #     controlobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #     if not controlobj:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
            #         raise serializers.ValidationError(result)
            #     treatment_parentcode = "TRM"+str(controlobj.control_prefix)+str(controlobj.Site_Codeid.itemsite_code)+str(controlobj.control_no)
                
            #     sales_staff = c.sales_staff.all().first()
            #     salesstaff = c.sales_staff.all()

            #     # total = c.price * c.quantity
            #     totQty += c.quantity
            #     # discount_amt += float(c.discount_amt)
            #     # additional_discountamt += float(c.additional_discountamt)
            #     total_disc += c.discount_amt + c.additional_discountamt
            #     totaldisc = c.discount_amt + c.additional_discountamt
            #     # dt_discPercent = (float(total_disc) * 100) / float(value['subtotal'])
            #     dt_discPercent = c.discount + c.additional_discount

            #     if c.is_foc == True:
            #         isfoc = True
            #         item_remarks = c.focreason.foc_reason_ldesc
            #     else:
            #         isfoc = False  
            #         item_remarks = None   
                
                
            #     dt_uom = None; dt_discuser = None ; lpackage = False; package_code = None
                
            #     if c.itemcodeid.Item_Divid.itm_code == '3':
            #         record_detail_type = "SERVICE"
            #         # elif c.itemcodeid.item_type == 'COURSE':  
            #         #     record_detail_type = "PACKAGE"
            #         #     lpackage = True
            #         #     packobj = PackageDtl.objects.filter(code=str(c.itemcodeid.item_code)+"0000",isactive=True)
            #         #     if packobj:
            #         #         package_code = packobj[0].package_code

            #         dt_discuser = fmspw.pw_userlogin
            #     elif c.itemcodeid.Item_Divid.itm_code == '1':
            #         dt_uom = c.item_uom.uom_desc
            #         record_detail_type = "PRODUCT"
            #         dt_discuser = fmspw.pw_userlogin
            #     elif c.itemcodeid.Item_Divid.itm_code == '5':
            #         record_detail_type = "PREPAID" 
            #         dt_discuser = None   
            #     elif c.itemcodeid.Item_Divid.itm_code == '4':
            #         record_detail_type = "VOUCHER" 
            #         dt_discuser = None      

            #     gst_amt_collect = c.deposit * (gst.item_value / 100)

            #     dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
            #     dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=c.itemcodeid.item_name,dt_price=c.price,
            #     dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
            #     dt_discamt="{:.2f}".format(float(totaldisc)),
            #     dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #     dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #     dt_discuser=dt_discuser,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            #     dt_transacamt="{:.2f}".format(float(c.trans_amt)),dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,itemcart=c,
            #     st_ref_treatmentcode=None,record_detail_type=record_detail_type,gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
            #     topup_outstanding=outstanding_acc,dt_remark=c.remark,isfoc=isfoc,item_remarks=item_remarks,
            #     dt_uom=dt_uom,,item_status_code=c.itemstatus.status_desc if c.itemstatus and c.itemstatus.status_desc else None)
            #     #appt_time=app_obj.appt_fr_time,                
            #     #st_ref_treatmentcode=treatment_parentcode,

            #     dtl.save()
            #     # print(dtl.id,"dtl")
            #     if dtl.pk not in id_lst:
            #         id_lst.append(c.pk)


            #     #multi staff table creation
            #     ratio = 0.0
            #     if c.sales_staff.all().count() > 0:
            #         count = c.sales_staff.all().count()
            #         ratio = float(c.ratio) / float(count)

            #     for sale in c.sales_staff.all():
            #         multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
            #         emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
            #         dt_lineno=c.lineno)
            #         multi.save()
            #         # print(multi.id,"multi")


                
            #     if int(c.itemcodeid.Item_Divid.itm_code) == 3 and c.itemcodeid.Item_Divid.itm_desc == 'SERVICES' and c.itemcodeid.Item_Divid.itm_isactive == True:
            #         desc = "Total Service Amount : "+str("{:.2f}".format(float(c.trans_amt)))

            #         #treatment Account creation
            #         treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
            #         description=desc,type="Deposit",amount="{:.2f}".format(float(c.deposit)),
            #         balance="{:.2f}".format(float(c.deposit)),User_Nameid=fmspw,
            #         user_name=fmspw.pw_userlogin,ref_transacno=sa_transacno,sa_transacno=sa_transacno,
            #         qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)),deposit="{:.2f}".format(float(c.deposit)),
            #         lpackage=lpackage,treatment_parentcode=treatment_parentcode,treatment_code="",sa_status="SA",
            #         cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #         sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),dt_lineno=c.lineno,
            #         Site_Codeid=site,site_code=site.itemsite_code,treat_code=treatment_parentcode,itemcart=c,
            #         focreason=item_remarks,package_code=package_code)
            #         treatacc.save()
            #         # print(treatacc.id,"treatacc")
            #     elif int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
            #         desc = "Total Product Amount : "+str("{:.2f}".format(float(c.trans_amt)))
            #         #Deposit Account creation
                    
            #         decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #         if not decontrolobj:
            #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
            #             raise serializers.ValidationError(result)

            #         treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)

            #         depoacc = DepositAccount(cust_code=cust_obj.cust_code,type="Deposit",amount="{:.2f}".format(float(c.deposit)),
            #         balance="{:.2f}".format(float(c.deposit)),user_name=fmspw.pw_userlogin,qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)),
            #         deposit="{:.2f}".format(float(c.deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #         sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #         deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
            #         sa_status="SA",item_barcode=str(c.itemcodeid.item_code)+"0000",item_description=c.itemcodeid.item_desc,
            #         treat_code=treat_code,void_link=None,lpackage=None,package_code=None,
            #         dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
            #         ref_transacno=sa_transacno,ref_productcode=treat_code,Item_Codeid=c.itemcodeid,
            #         item_code=c.itemcodeid.item_code)
            #         depoacc.save()
            #         # print(depoacc.pk,"depoacc")
            #         if depoacc.pk:
            #             decontrolobj.control_no = int(decontrolobj.control_no) + 1
            #             decontrolobj.save()

            #     elif int(c.itemcodeid.Item_Divid.itm_code) == 5 and c.itemcodeid.Item_Divid.itm_desc == 'PREPAID' and c.itemcodeid.Item_Divid.itm_isactive == True:
            #         #Prepaid Account creation
            #         #exp_date need to map
            #         prepaid_valid_period = date.today() + timedelta(int(c.itemcodeid.prepaid_valid_period))
            #         pp_bonus = c.itemcodeid.prepaid_value - c.itemcodeid.prepaid_sell_amt

            #         prepacc = PrepaidAccount(pp_no=sa_transacno,pp_type=c.itemcodeid.item_range,
            #         pp_desc=c.itemcodeid.item_name,exp_date=prepaid_valid_period,cust_code=cust_obj.cust_code,
            #         cust_name=cust_obj.cust_name,pp_amt=c.itemcodeid.prepaid_sell_amt,pp_total=c.itemcodeid.prepaid_value,
            #         pp_bonus=pp_bonus,transac_no="",item_no="",use_amt=0,remain=c.itemcodeid.prepaid_value,ref1="",
            #         ref2="",status=True,site_code=site.itemsite_code,sa_status="DEPOSIT",exp_status=True,
            #         voucher_no=None,isvoucher=None,has_deposit=True,topup_amt=c.deposit,
            #         outstanding=outstanding_acc,active_deposit_bonus=False,topup_no="",topup_date=None,
            #         line_no=c.lineno,staff_name=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #         staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #         pp_type2=None,condition_type1=None,pos_daud_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,
            #         Item_Codeid=c.itemcodeid,item_code=c.itemcodeid.item_code)
            #         prepacc.save()
            #         print(prepacc.pk,"prepacc")

            #         vo_obj = VoucherCondition.objects.filter(item_code=c.itemcodeid.item_code)
            #         #PrepaidAccountCondition Creation
            
            #         pp_acc = PrepaidAccountCondition(pp_no=sa_transacno,pp_type=c.itemcodeid.item_range,
            #         pp_desc=c.itemcodeid.item_name,p_itemtype=','.join([v.p_itemtype for v in vo_obj if v.p_itemtype]),
            #         item_code=c.itemcodeid.item_code,conditiontype1=','.join([v.conditiontype1 for v in vo_obj if v.conditiontype1]),
            #         conditiontype2=','.join([v.conditiontype2 for v in vo_obj if v.conditiontype2]),
            #         amount=vo_obj.first().amount,rate=vo_obj.first().rate,use_amt=0,remain=vo_obj.first().amount,
            #         pos_daud_lineno=c.lineno)
            #         pp_acc.save()
            #         # print(pp_acc.pk,"pp_acc")
            #         PrepaidAccount.objects.filter(pk=prepacc.pk).update(pp_type2=pp_acc.pp_type,
            #         condition_type1=pp_acc.conditiontype1)

            #     elif int(c.itemcodeid.Item_Divid.itm_code) == 4 and c.itemcodeid.Item_Divid.itm_desc == 'VOUCHER' and c.itemcodeid.Item_Divid.itm_isactive == True:
            #         vorecontrolobj = ControlNo.objects.filter(control_description__iexact="Public Voucher",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #         if not vorecontrolobj:
            #             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher Record Control No does not exist!!",'error': True} 
            #             raise serializers.ValidationError(result)

            #         voucher_code = str(vorecontrolobj.control_prefix)+str(vorecontrolobj.Site_Codeid.itemsite_code)+str(vorecontrolobj.control_no)
                    
            #         if c.itemcodeid.voucher_value_is_amount == True:
            #             vo_percent = 0
            #         else:
            #             if c.itemcodeid.voucher_value_is_amount == False:
            #                 vo_percent = c.itemcodeid.voucher_value
                    
            #         if c.itemcodeid.voucher_valid_period:
            #             date_1 = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
            #             print(date_1,"date_1")
            #             end_date = date_1 + datetime.timedelta(days=int(c.itemcodeid.voucher_valid_period))
            #             print(end_date,"end_date")
            #             # tod_now = datetime.now(pytz.timezone(TIME_ZONE))
            #             # print(tod_now,"tod_now")
            #             # voexpiry = tod_now + datetime.timedelta(days=c.itemcodeid.voucher_valid_period)
            #             # print(voexpiry,"voexpiry")
            #             # expiry = datetime.datetime.combine(end_date, datetime.datetime.min.time())

            #             # expiry = end_date.strftime("%d-%m-%Y")
            #             # print(expiry,"expiry") 

            #         vo_rec = VoucherRecord(sa_transacno=sa_transacno,voucher_name=c.itemcodeid.item_name,
            #         voucher_no=voucher_code,value=c.price,cust_codeid=cust_obj,cust_code=cust_obj.cust_code,
            #         cust_name=cust_obj.cust_name,percent=vo_percent,site_codeid=site,site_code=site.itemsite_code,
            #         issued_expiry_date=end_date if end_date else None,issued_staff=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #         onhold=0,paymenttype=None,remark=None,type_code=vorecontrolobj.control_prefix,used=0,
            #         ref_fullvoucherno=None,ref_rangefrom=None,ref_rangeto=None,site_allocate=None,dt_lineno=c.lineno,)
            #         vo_rec.save()
            #         if vo_rec.pk:
            #             vorecontrolobj.control_no = int(vorecontrolobj.control_no) + 1
            #             vorecontrolobj.save()

            #     totaldisc = c.discount_amt + c.additional_discountamt
            #     totalpercent = c.discount + c.additional_discount

            #     # if c.discount_amt != 0.0 and c.additional_discountamt != 0.0:
            #     #     totaldisc = c.discount_amt + c.additional_discountamt
            #     #     totalpercent = c.discount + c.additional_discount
            #     #     istransdisc = True
            #     # elif c.discount_amt != 0.0:
            #     #     totaldisc = c.discount_amt
            #     #     totalpercent = c.discount
            #     #     istransdisc = False
            #     # elif c.additional_discountamt != 0.0:
            #     #     totaldisc = c.additional_discountamt
            #     #     totalpercent = c.additional_discount
            #     #     istransdisc = True    
            #     # else:
            #     #     totaldisc = 0.0
            #     #     totalpercent = 0.0
            #     #     istransdisc = False

            #     #PosDisc Creation for each cart line with or without line disc (disc per/amt = line disc + trasac disc)
            #     # if transc disc for whole cart is applied that time need to create one record in PosDisc (disc per/amt = trasac disc).
            #     discreason = None
            #     if int(c.itemcodeid.item_div) in [1,3] and c.itemcodeid.item_type == 'SINGLE':
            #         if c.pos_disc.all().exists():
            #             # for d in c.disc_reason.all():
            #             #     if d.r_code == '100006' and d.r_desc == 'Others':
            #             #         discreason = c.discreason_txt
            #             #     elif d.r_desc:
            #             #         discreason = d.r_desc  
                            
            #             for po in c.pos_disc.all():
            #                 po.sa_transacno = sa_transacno
            #                 po.dt_status = "SA"
            #                 po.dt_price = c.price
            #                 po.save()
            #         else:
            #             if totaldisc == 0.0 or totalpercent == 0.0 and len(c.pos_disc.all()) == 0:
            #                 posdisc = PosDisc(sa_transacno=sa_transacno,dt_itemno=c.itemcodeid.item_code+"0000",disc_amt=totaldisc,
            #                 disc_percent=totalpercent,dt_lineno=c.lineno,remark=discreason,site_code=site.itemsite_code,
            #                 dt_status="SA",dt_auto=0,line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=c.price,istransdisc=False)
            #                 posdisc.save()
            #                 # print(posdisc.pk,"posdisc")

                    
            #     #HoldItemDetail creation for retail products
            #     if c.itemcodeid.Item_Divid.itm_code == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
            #         if c.holditemqty > 0:
            #             con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #             if not con_obj:
            #                 result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
            #                 raise serializers.ValidationError(result)

            #             product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                        
            #             hold = HoldItemDetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
            #             transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
            #             hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #             hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=c.trans_amt,hi_qty=c.holditemqty,
            #             hi_discamt=totaldisc,hi_discpercent=totalpercent,hi_discdesc=None,
            #             hi_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #             hi_lineno=c.lineno,hi_uom=c.item_uom.uom_desc,hold_item=True,hi_deposit=c.deposit,
            #             holditemqty=c.holditemqty,status="OPEN",sa_custno=cust_obj.cust_code,
            #             sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
            #             product_issues_no=product_issues_no)
            #             hold.save()
            #             # print(hold.pk,"hold")
            #             if hold.pk:
            #                 con_obj.control_no = int(con_obj.control_no) + 1
            #                 con_obj.save()

            #     if '0' in str(c.quantity):
            #         no = str(c.quantity).split('0')
            #         if no[0] == '':
            #             number = no[1]
            #         else:
            #             number = c.quantity
            #     else:
            #         number = c.quantity

            #     dtl_st_ref_treatmentcode = "";dtl_first_trmt_done = False
            #     if c.itemcodeid.Item_Divid.itm_code == '3':
            #         for i in range(1,int(number)+1):
            #             treat = c
            #             Price = c.trans_amt
            #             Unit_Amount = Price / c.quantity
            #             times = str(i).zfill(2)
            #             treatment_no = str(c.quantity).zfill(2)
            #             treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #             treatment_parentcode=treatment_parentcode,course=treat.itemcodeid.item_name,times=times,
            #             treatment_no=treatment_no,price="{:.2f}".format(float(Price)),unit_amount="{:.2f}".format(float(Unit_Amount)),Cust_Codeid=treat.cust_noid,
            #             cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
            #             status="Open",item_code=str(treat.itemcodeid.item_code)+"0000",Item_Codeid=treat.itemcodeid,
            #             sa_transacno=sa_transacno,sa_status="SA",type="N",trmt_is_auto_proportion=False,
            #             dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,
            #             treatment_account=treatacc,service_itembarcode=str(treat.itemcodeid.item_code)+"0000")

            #             #and str(treatmentid.treatment_code) == str(treatment_parentcode)+"-"+"01"
            #             if c.helper_ids.exists():
            #                 for h in c.helper_ids.all().filter(times=times):
                            
            #                     # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                                
            #                     treatmentid.status = "Done"
            #                     treatmentid.trmt_room_code = h.Room_Codeid.room_code if h.Room_Codeid else None
            #                     treatmentid.save()

            #                     wp1 = h.workcommpoints / float(c.helper_ids.all().filter(times=times).count())
            #                     share_amt = float(treatmentid.unit_amount) / float(c.helper_ids.all().filter(times=times).count())

            #                     TmpItemHelper.objects.filter(id=h.id).update(item_code=treatment_parentcode+"-"+str(times),
            #                     item_name=c.itemcodeid.item_name,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
            #                     amount=treatmentid.unit_amount,sa_date=dtl.sa_date,site_code=site.itemsite_code,
            #                     wp1=wp1,wp2=0.0,wp3=0.0)

            #                     # Item helper create
            #                     helper = ItemHelper(item_code=treatment_parentcode+"-"+str(times),item_name=c.itemcodeid.item_desc,
            #                     line_no=dtl.dt_lineno,sa_transacno=sa_transacno,amount="{:.2f}".format(float(treatmentid.unit_amount)),
            #                     helper_name=h.helper_name if h.helper_name else None,helper_code=h.helper_code if h.helper_code else None,sa_date=dtl.sa_date,
            #                     site_code=site.itemsite_code,share_amt=share_amt,helper_transacno=sa_transacno,
            #                     wp1=wp1,wp2=0.0,wp3=0.0)
            #                     helper.save()
            #                     # print(helper.id,"helper")

            #                     #appointment treatment creation
            #                     if h.appt_fr_time and h.appt_to_time != False and h.add_duration != False:
            #                         stock_obj = c.itemcodeid

            #                         if stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
            #                             stk_duration = 60
            #                         else:
            #                             stk_duration = int(stock_obj.srv_duration)

            #                         stkduration = int(stk_duration) + 30
            #                         # print(stkduration,"stkduration")

            #                         hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
            #                         start_time =  get_in_val(self, h.appt_fr_time)
            #                         starttime = datetime.datetime.strptime(start_time, "%H:%M")

            #                         end_time = starttime + datetime.timedelta(minutes = stkduration)
            #                         endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            #                         duration = hrs

            #                         treat_all = Treatment.objects.filter(sa_transacno=sa_transacno,treatment_parentcode=treatment_parentcode)
            #                         length = [t.status for t in treat_all if t.status == 'Done']
            #                         if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
            #                             master_status = "Done"
            #                         else:
            #                             master_status = "Open"
        
            #                         master = Treatment_Master(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #                         treatment_parentcode=treatment_parentcode,sa_transacno=sa_transacno,
            #                         course=stock_obj.item_desc,times=times,treatment_no=treatment_no,
            #                         price=stock_obj.item_price,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
            #                         cust_name=cust_obj.cust_name,status=master_status,unit_amount=stock_obj.item_price,
            #                         Item_Codeid=stock_obj,item_code=stock_obj.item_code,
            #                         sa_status="SA",dt_lineno=dtl.dt_lineno,type="N",duration=stkduration,
            #                         Site_Codeid=site,site_code=site.itemsite_code,
            #                         trmt_room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,Trmt_Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,
            #                         Item_Class=stock_obj.Item_Classid if stock_obj.Item_Classid else None,PIC=stock_obj.Stock_PIC if stock_obj.Stock_PIC else None,
            #                         start_time=h.appt_fr_time if h.appt_fr_time else None,end_time=h.appt_to_time if h.appt_to_time else None,add_duration=h.add_duration if h.add_duration else None,
            #                         appt_remark=stock_obj.item_desc if stock_obj.item_desc else None,requesttherapist=False)

            #                         master.save()
            #                         master.emp_no.add(h.helper_id.pk)
            #                         # print(master.id,"master")

            #                         ctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #                         if not ctrl_obj:
            #                             result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
            #                             raise serializers.ValidationError(result)
                                    
            #                         appt_code = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                                    
            #                         channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()
            #                         # if not channel:
            #                         #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
            #                         #     raise serializers.ValidationError(result)

            #                         appt = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=date.today(),
            #                         appt_fr_time=h.appt_fr_time if h.appt_fr_time else None,Appt_typeid=channel if channel else None,appt_type=channel.appt_type_desc if channel.appt_type_desc else None,
            #                         appt_phone=cust_obj.cust_phone2,appt_remark=stock_obj.item_desc,
            #                         emp_noid=h.helper_id if h.helper_id else None,emp_no=h.helper_id.emp_code if h.helper_id.emp_code else None,emp_name=h.helper_id.emp_name if h.helper_id.emp_name else None,
            #                         cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
            #                         appt_to_time=h.appt_to_time if h.appt_to_time else None,Appt_Created_Byid=fmspw,
            #                         appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            #                         Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,
            #                         Source_Codeid=h.Source_Codeid if h.Source_Codeid else None,source_code=h.Source_Codeid.source_code if h.Source_Codeid else None,
            #                         cust_refer=cust_obj.cust_refer,requesttherapist=False,new_remark=h.new_remark,
            #                         item_code=stock_obj.item_code,sa_transacno=sa_transacno,treatmentcode=str(treatment_parentcode)+"-"+str(times))
            #                         appt.save()

            #                         if appt.pk:
            #                             master.Appointment = appt
            #                             master.appt_time = timezone.now()
            #                             master.save()
            #                             ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
            #                             ctrl_obj.save()
                                    
            #                 #treatment Account creation for done treatment 01
            #                 if c.helper_ids.all().filter(times=times).first():
            #                     acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,
            #                     treatment_parentcode=treatment_parentcode,Site_Codeid=site).order_by('id').last()

            #                     td_desc = str(times)+"/"+str(c.quantity)+" "+str(stock_obj.item_name)
            #                     balance = acc_ids.balance - float(treatmentid.unit_amount)

            #                     treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
            #                     cust_code=cust_obj.cust_code,ref_no=treatmentid.treatment_code,
            #                     description=td_desc,type='Sales',amount=-float("{:.2f}".format(float(treatmentid.unit_amount))) if treatmentid.unit_amount else 0.0,
            #                     balance="{:.2f}".format(float(balance)) if balance else 0.0,User_Nameid=fmspw,user_name=fmspw.pw_userlogin,
            #                     ref_transacno=treatmentid.sa_transacno,
            #                     sa_transacno=sa_transacno,qty=1,outstanding="{:.2f}".format(float(acc_ids.outstanding)),
            #                     deposit=None,treatment_parentcode=treatmentid.treatment_parentcode,treatment_code="",
            #                     sa_status="SA",cas_name=fmspw.pw_userlogin,
            #                     sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #                     sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #                     dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
            #                     treat_code=treatmentid.treatment_parentcode,itemcart=c)
            #                     treatacc_td.save()
            #                     # print(treatacc_td.id,"treatacc_td")
            #                     dtl_first_trmt_done = True
            #                     if dtl_st_ref_treatmentcode == "":
            #                         dtl_st_ref_treatmentcode = str(treatment_parentcode)+"-"+str(times)
            #                     elif not dtl_st_ref_treatmentcode == "":
            #                         dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)

                        
            #             treatmentid.save()
            #             # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
            #             # print(treatmentid.id,"treatment_id")

            #         if treatacc and treatmentid:
            #             controlobj.control_no = int(controlobj.control_no) + 1
            #             controlobj.save()

            #         # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
            #         dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
            #         dtl.first_trmt_done = dtl_first_trmt_done
            #         dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
            #         dtl.first_trmt_done_staff_name = ','.join([v.helper_id.emp_name for v in c.helper_ids.all() if v.helper_id.emp_name])
            #         dtl.save()

            # sumqty = cart_ids.filter().aggregate(Sum('quantity'))
            # totQty = int(sumqty['quantity__sum'])
            # total_disc = sum([ca.discount_amt + ca.additional_discountamt for ca in cart_ids if ca.discount_amt and ca.additional_discountamt])
            sumqty = cart_ids.exclude(type='Exchange').aggregate(Sum('quantity'))
            totQty = int(sumqty['quantity__sum'])
            ex_cart_ids = cart_ids.exclude(type='Exchange')
            total_disc = sum([ca.discount_amt + ca.additional_discountamt for ca in ex_cart_ids if ca.discount_amt and ca.additional_discountamt])
            
            if depotop_ids:
                #header creation
                if alsales_staff:
                    Emp_code = alsales_staff.emp_code
                    Emp_name = alsales_staff.emp_name
                else:
                    alsales_staff = None
                    Emp_code = ""  
                    Emp_name = ""

                focnot_ids = cart_ids.filter(is_foc=False) 
                if focnot_ids:
                    print(focnot_ids,"focnot_ids")
                    sa_transacno_refval = sa_transacno_ref
                    sa_transacno_type = "Receipt"
                else:
                    nscontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Non Sales No",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not nscontrol_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Non Sales No does not exist!!",'error': True} 
                        raise serializers.ValidationError(result)
                    
                    sa_transacno_refval = str(nscontrol_obj.control_prefix)+str(nscontrol_obj.Site_Codeid.itemsite_code)+str(nscontrol_obj.control_no)
                    sa_transacno_type = "Non Sales"

                print(value['tax_amt'],"tax2")
                hdr = PosHaud(cas_name=fmspw.pw_userlogin,sa_transacno=sa_transacno,sa_status="SA",
                sa_totamt="{:.2f}".format(float(value['deposit_amt'])),sa_totqty=totQty,sa_totdisc="{:.2f}".format(float(total_disc)),sa_totgst="{:.2f}".format(float(value['tax_amt'])),
                sa_staffnoid=alsales_staff,sa_staffno=Emp_code,sa_staffname=Emp_name,sa_custnoid=cust_obj,sa_custno=cust_obj.cust_code,
                sa_custname=cust_obj.cust_name,sa_discuser=fmspw.pw_userlogin,sa_discamt="{:.2f}".format(float(total_disc)),sa_disctotal="{:.2f}".format(float(total_disc)),ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                sa_depositamt="{:.2f}".format(float(value['deposit_amt'])),sa_transacamt="{:.2f}".format(float(value['trans_amt'])),sa_round="{:.2f}".format(float(value['sa_Round'])),total_outstanding="{:.2f}".format(float(outstanding)),
                trans_user_login=fmspw.pw_password,trans_user_loginid=fmspw,sa_transacno_ref=sa_transacno_refval,sa_transacno_type=sa_transacno_type,
                issuestrans_user_login=fmspw.pw_userlogin)
                
                # appt_time=app_obj.appt_fr_time,
                hdr.save()
                # print(hdr.id,"hdr")
                if hdr.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()
                    if focnot_ids:
                        refcontrol_obj.control_no = int(refcontrol_obj.control_no) + 1
                        refcontrol_obj.save()
                    else:
                        nscontrol_obj.control_no = int(nscontrol_obj.control_no) + 1
                        nscontrol_obj.save()   
            else:
                if sales_ids:
                    #header creation
                    alservice_staff = alsales_staff
                    if alservice_staff:
                        Emp_code = alservice_staff.emp_code
                        Emp_name = alservice_staff.emp_name
                    else:
                        alservice_staff = None
                        Emp_code = ""  
                        Emp_name = ""

                    hdr = PosHaud(cas_name=fmspw.pw_userlogin,sa_transacno=sa_transacno,sa_status="SA",
                    sa_totamt=0.0,sa_totqty=0.0,sa_totdisc=0.0,sa_totgst=None,
                    sa_staffnoid=alservice_staff,sa_staffno=Emp_code,sa_staffname=Emp_name,sa_custnoid=cust_obj,sa_custno=cust_obj.cust_code,
                    sa_custname=cust_obj.cust_name,sa_discuser=None,sa_disctotal=0.0,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                    sa_depositamt=0.0,sa_transacamt=0.0,sa_round=0,total_outstanding=outstanding,
                    trans_user_login=fmspw.pw_password,trans_user_loginid=fmspw,sa_transacno_ref=sa_transacno_ref,sa_transacno_type="Redeem Service",
                    issuestrans_user_login=fmspw.pw_userlogin)
                    # appt_time=app_obj.appt_fr_time,

                    hdr.save()
                    # print(hdr.id,"hdr")
                    if hdr.pk:
                        control_obj.control_no = int(control_obj.control_no) + 1
                        control_obj.save()
                        refcontrol_obj.control_no = int(refcontrol_obj.control_no) + 1
                        refcontrol_obj.save()
                        
        
            state = status.HTTP_201_CREATED
            message = "Created Succesfully"
            error = False
            taud_d = PosTaud.objects.filter(pk__in=taud_ids,ItemSIte_Codeid__pk=site.pk).first()
            # serializer_final = self.get_serializer(taud_d, many=True)
            # data_d = serializer_final.data
            # for data in data_d:
            #     data['subtotal'] = "{:.2f}".format(float(data['subtotal']))
            #     data['discount_amt'] =  "{:.2f}".format(float(data['discount_amt']))
            #     data['pay_actamt'] = "{:.2f}".format(float(data['pay_actamt']))
            #     data['tax'] = "{:.2f}".format(float(data['tax']))
            #     data['pay_amt'] = "{:.2f}".format(float(data['pay_amt']))
            #     data['billable_amount'] = "{:.2f}".format(float(data['billable_amount']))
            
            for i in id_lst:
                c = ItemCart.objects.filter(id=i,isactive=True).exclude(type__in=type_ex).first()
                c.is_payment = True
                c.cart_status = "Completed"
                c.sa_transacno = sa_transacno
                c.save()    

            # serializer_final.data
            result = {'status': state,"message":message,'error': error, 'data': {'sa_transacno':taud_d.sa_transacno}}
            return Response(result, status=status.HTTP_201_CREATED)
        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)
     
        # state = status.HTTP_400_BAD_REQUEST
        # message = "Invalid Input"
        # error = True
        # result = {'status': state,"message":message,'error': error, 'data':  serializer.errors}
        # return Response(result, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def TopUpPostaudCreate(self, request):
        global type_ex
        request = self.request
        cart_date = timezone.now().date()

        if request.GET.get('cart_date',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give cart date",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('cust_noid',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Customer ID",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
        if not cust_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        cart_id = request.GET.get('cart_id',None)
        if cart_id is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content cart_id is not given",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if not self.request.GET.get('sitecodeid',None) is None:
            site = ItemSitelist.objects.filter(pk=self.request.GET.get('sitecodeid',None),itemsite_isactive=True).first()
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Site ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site = fmspw.loginsite

        empl = fmspw.Emp_Codeid
       
        cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
        cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
        if cartc_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
       

        control_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw.loginsite.pk).first()
        if not control_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
            raise serializers.ValidationError(result)
        
        sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
       
        refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Receipt No",Site_Codeid__pk=fmspw.loginsite.pk).first()
        if not refcontrol_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Receipt Control No does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

        sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
        
        
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 3",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
    
        value = postaud_calculation(self, request, queryset)
       
        pay_amt = 0.0  ; taud_ids = []; check=[]
        # satransacno = request.GET.get('satransacno',None)
        for r in request.data:
            paytable = Paytable.objects.filter(pk=r['pay_typeid'],pay_isactive=True).first()
            pay_amt += float(r['pay_amt'])
            if paytable.pay_groupid.pay_group_code == 'CASH':
                if "CASH" not in check:
                    check.append("CASH")

        # print(pay_amt,value['billable_amount']) 
        if pay_amt < float(value['billable_amount']) or pay_amt > float(value['billable_amount']):
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Pay amount should be equal to billable amount!!",'error': True} 
            raise serializers.ValidationError(result)

        add = 0.0
        for idx, req in enumerate(request.data, start=1): 
            # print(idx,"idx")
            paytable = Paytable.objects.filter(pk=req['pay_typeid'],pay_isactive=True).first()
            pay_ids = Paytable.objects.filter(pk=req['pay_typeid'],pay_isactive=True)
            if not pay_ids:
                msg = "Paytable ID %s is does not exist!!".format(req['pay_typeid'])
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                raise serializers.ValidationError(result)

            serializer_one = self.get_serializer(data=req)
            #pos_taud creation
            if serializer_one.is_valid():
                # pay_gst = (float(req['pay_amt']) / (100+gst.item_value)) * gst.item_value
                if gst.is_exclusive == True:
                    pay_gst = float(req['pay_amt']) * (gst.item_value / 100)
                else:
                    pay_gst = (float(req['pay_amt']) * gst.item_value ) / (100+gst.item_value)

                # tax="{:.2f}".format(float(value['tax_amt'])), discount_amt="{:.2f}".format(float(value['discount'])),
                taud = serializer_one.save(sa_transacno=sa_transacno,billed_by=fmspw,ItemSIte_Codeid=site,itemsite_code=site.itemsite_code,
                pay_groupid=paytable.pay_groupid,pay_group=paytable.pay_groupid.pay_group_code,pay_typeid=paytable,pay_type=paytable.pay_code,
                pay_desc=paytable.pay_description,pay_tendamt=req['pay_amt'],pay_tendrate=1.0,pay_amt=req['pay_amt'],pay_amtrate=1.0,pay_status=1,dt_lineno=idx,
                pay_actamt=req['pay_amt'],subtotal="{:.2f}".format(float(value['subtotal'])),paychange=0.0,
                tax="{:.2f}".format(float(pay_gst)), discount_amt="{:.2f}".format(float(value['discount'])),
                billable_amount="{:.2f}".format(float(value['billable_amount'])),
                pay_gst_amt_collect="{:.2f}".format(float(pay_gst)),pay_gst="{:.2f}".format(float(pay_gst)))
                # print(taud,"taud")
                # print(taud.pay_premise,taud.credit_debit)
                if taud:
                    taud_ids.append(taud.pk)

                if "CASH" not in check:
                    amount = float(req['pay_amt']) - pay_gst
                elif "CASH" in check:
                    if len(request.data) == 1:
                        # amount = float(req['pay_amt']) - float(value['tax_amt'])
                        amount = float(req['pay_amt']) - pay_gst
                    elif len(request.data) == 2:
                        if paytable.pay_groupid.pay_group_code == 'CASH': 
                            amount = float(req['pay_amt'])
                        elif paytable.pay_groupid.pay_group_code != 'CASH': 
                            # amount = float(req['pay_amt']) - float(value['tax_amt'])  
                            amount = float(req['pay_amt']) - pay_gst
                            if amount <= 0:
                                amount = 0
                    elif len(request.data) == 3: 
                        add += pay_gst
                        if paytable.pay_groupid.pay_group_code == 'CASH': 
                            amount = float(req['pay_amt']) 
                        elif paytable.pay_groupid.pay_group_code != 'CASH': 
                            amount = float(req['pay_amt']) - add
                            if amount <= 0:
                                amount = 0
                            add = 0.0

                depo_type = DepositType(sa_transacno=sa_transacno,pay_group=paytable.pay_groupid.pay_group_code,
                pay_type=paytable.pay_code,amount="{:.2f}".format(float(amount)),card_no=None,pay_desc=paytable.pay_description,
                pay_tendcurr=None,pay_tendrate=1.0,site_code=site.itemsite_code,pos_taud_lineno=idx) 
                depo_type.save()
                # print(depo_type.id,"depo_type")    


        outstanding =  float(value['trans_amt']) - float(value['deposit_amt'])
        #detail creation
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
        cart_ids = queryset
        outstanding_new = 0.0
        for idx, c in enumerate(cart_ids, start=1):
            if idx == 1:
                alsales_staff = c.sales_staff.all().first()

            # print(c,"cc")
            # controlobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
            # if not controlobj:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
            #     raise serializers.ValidationError(result)
            # treatment_parentcode = "TRM"+str(controlobj.control_prefix)+str(controlobj.Site_Codeid.itemsite_code)+str(controlobj.control_no)
            
            sales_staff = c.sales_staff.all().first()
            salesstaff = c.sales_staff.all()

            # total = c.price * c.quantity
            totQty += c.quantity
            # discount_amt += float(c.discount_amt)
            # additional_discountamt += float(c.additional_discountamt)
            total_disc += c.discount_amt + c.additional_discountamt
            totaldisc = c.discount_amt + c.additional_discountamt
            # dt_discPercent = (float(total_disc) * 100) / float(value['subtotal'])
            dt_discPercent = c.discount + c.additional_discount

            if c.is_foc == True:
                isfoc = True
                item_remarks = c.focreason.foc_reason_ldesc if c.focreason and c.focreason.foc_reason_ldesc else None 
            else:
                isfoc = False  
                item_remarks = None   
            
           
            stock = Stock.objects.filter(pk=c.itemcodeid.pk,item_isactive=True).first()
            multi_itemcode = None
            gst_amt_collect = c.deposit * (gst.item_value / 100)
            if gst.is_exclusive == True:
                gst_amt_collect = c.deposit * (gst.item_value / 100)
            else:
                gst_amt_collect = c.deposit * gst.item_value / (100+gst.item_value)

            if c.treatment_account is not None:
                topup_code = c.treatment_account.treatment_parentcode
                multi_itemcode = c.treatment_account.treatment_parentcode

                acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment_account.ref_transacno,
                treatment_parentcode=c.treatment_account.treatment_parentcode,Site_Codeid=site,
                type__in=('Deposit','Top Up')).order_by('id').last()

                outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)

                dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
                dt_itemno=c.treatment_account.treatment_parentcode,dt_itemdesc=c.itemcodeid.item_name,
                dt_price=c.price,dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                dt_discamt="{:.2f}".format(float(totaldisc)),dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,
                dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                dt_discuser=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                dt_transacamt=0,dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,
                itemcart=c,st_ref_treatmentcode=None,first_trmt_done=False,topup_outstanding=outstanding_acc,
                record_detail_type="TP SERVICE",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                dt_remark=c.remark,isfoc=isfoc,item_remarks=item_remarks,topup_prepaid_trans_code="",
                topup_service_trmt_code=topup_code,item_status_code=c.itemstatus.status_desc if c.itemstatus and c.itemstatus.status_desc else None)
                #appt_time=app_obj.appt_fr_time,
            
            elif c.deposit_account is not None:

                decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                if not decontrolobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

                treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                multi_itemcode = treat_code

                acc_ids = DepositAccount.objects.filter(ref_transacno=c.deposit_account.sa_transacno,
                ref_productcode=c.deposit_account.treat_code,Site_Codeid=site,type__in=('Deposit', 'Top Up')).order_by('id').last()
                
                outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)

                dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
                dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=c.itemcodeid.item_name,
                dt_price="{:.2f}".format(float(c.price)),dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                dt_discamt="{:.2f}".format(float(totaldisc)),dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,
                dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                dt_discuser=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                dt_transacamt=0,dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,
                itemcart=c,st_ref_treatmentcode=None,first_trmt_done=False,topup_outstanding=outstanding_acc,
                record_detail_type="TP PRODUCT",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                dt_remark=c.remark,isfoc=isfoc,item_remarks=item_remarks,topup_product_treat_code = treat_code,
                topup_prepaid_trans_code="",item_status_code=c.itemstatus.status_desc if c.itemstatus and c.itemstatus.status_desc else None)
                #appt_time=app_obj.appt_fr_time, 


            elif c.prepaid_account is not None:
                topup_code = c.prepaid_account.transac_no
                multi_itemcode = topup_code

                acc_ids = PrepaidAccount.objects.filter(Site_Codeid=site).order_by('id').first() #transac_no=

                outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)

                dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
                dt_itemno=topup_code,dt_itemdesc=c.itemcodeid.item_name,
                dt_price=c.price,dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
                dt_discamt="{:.2f}".format(float(totaldisc)),dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,
                dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                dt_discuser=None,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                dt_transacamt=0,dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,
                itemcart=c,st_ref_treatmentcode=None,first_trmt_done=False,topup_outstanding=outstanding_acc,
                record_detail_type="TP PREPAID",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
                dt_remark=c.remark,isfoc=isfoc,item_remarks=item_remarks,
                topup_prepaid_trans_code=c.prepaid_account.pp_no,topup_prepaid_type_code=c.prepaid_account.pp_type,
                topup_prepaid_pos_trans_lineno=c.lineno,item_status_code=c.itemstatus.status_desc if c.itemstatus and c.itemstatus.status_desc else None)
                #appt_time=app_obj.appt_fr_time, 

            else:
                acc_ids = None                

            dtl.save()
            # print(dtl.id,"dtl")
            if dtl.pk not in id_lst:
                id_lst.append(c.pk)


            #multi staff table creation
            ratio = 0.0
            if c.sales_staff.all().count() > 0:
                count = c.sales_staff.all().count()
                ratio = float(c.ratio) / float(count)

            for sale in c.sales_staff.all():
                multi = Multistaff(sa_transacno=sa_transacno,item_code=multi_itemcode,
                emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
                dt_lineno=c.lineno)
                multi.save()
                # print(multi.id,"multi")


            desc = "Top Up Amount: "+str("{:.2f}".format(float(c.deposit)))
            if c.treatment_account is not None:

                tp_balance = acc_ids.balance + c.deposit if acc_ids.balance else c.deposit
                print(tp_balance,"foc")
                #treatment Account creation
                treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                description=desc,type="Top Up",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(tp_balance)),User_Nameid=fmspw,
                user_name=fmspw.pw_userlogin,ref_transacno=acc_ids.ref_transacno,sa_transacno=sa_transacno,
                qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)),deposit=None,
                treatment_parentcode=c.treatment_account.treatment_parentcode,treatment_code="",sa_status="SA",
                cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),dt_lineno=c.lineno,
                Site_Codeid=site,site_code=site.itemsite_code,treat_code=c.treatment_account.treatment_parentcode,itemcart=c,
                focreason=item_remarks,ref_no=sa_transacno)
                treatacc.save()
            # print(treatacc.id,"treatacc")
            elif c.deposit_account is not None:
                  
               
                #deposit Account creation
                depositacc = DepositAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                description=desc,type="Top Up",amount="{:.2f}".format(float(c.deposit)),balance="{:.2f}".format(float(acc_ids.balance + c.deposit)),
                user_name=fmspw.pw_userlogin,sa_transacno=c.deposit_account.sa_transacno,qty=c.quantity,
                outstanding="{:.2f}".format(float(outstanding_acc)),deposit="{:.2f}".format(float(c.deposit)),treat_code=treat_code,sa_status="SA",
                cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),dt_lineno=c.lineno,
                Site_Codeid=site,site_code=site.itemsite_code,Item_Codeid=c.itemcodeid,
                item_code=c.itemcodeid.item_code,ref_transacno=c.deposit_account.ref_transacno,
                ref_productcode=c.deposit_account.ref_productcode,ref_code=sa_transacno,
                deposit_type="PRODUCT",item_barcode=str(c.itemcodeid.item_code)+"0000",
                item_description=c.itemcodeid.item_name,void_link=None,lpackage=False,package_code=None)
                depositacc.save()
                
                
                if depositacc.pk:
                    decontrolobj.control_no = int(decontrolobj.control_no) + 1
                    decontrolobj.save()

            elif c.prepaid_account is not None:
                #prepaid Account creation
                prepaid_valid_period = timezone.now() + timedelta(int(c.itemcodeid.prepaid_valid_period))
                pp_bonus = c.itemcodeid.prepaid_value - c.itemcodeid.prepaid_sell_amt
                print(c.prepaid_account.remain,"remain1")
                remain = c.prepaid_account.remain + c.deposit
                c.prepaid_account.status = False
                c.prepaid_account.save()
                outstanding = float(c.prepaid_account.outstanding) - float(c.deposit)

                prepaidacc = PrepaidAccount(pp_no=c.prepaid_account.pp_no,pp_type=c.itemcodeid.item_range,
                pp_desc=c.itemcodeid.item_name,exp_date=prepaid_valid_period,Cust_Codeid=cust_obj,
                cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name,pp_amt=c.itemcodeid.prepaid_sell_amt,
                pp_total=c.itemcodeid.prepaid_value, pp_bonus=pp_bonus,transac_no="",item_no="",
                use_amt=0,remain=remain,ref1="",ref2="",status=True,site_code=site.itemsite_code,
                sa_status="TOPUP",exp_status=True,voucher_no="",isvoucher=False,has_deposit=True,
                topup_amt=c.deposit,outstanding=outstanding,active_deposit_bonus=False,topup_no=sa_transacno,
                topup_date=timezone.now(),line_no=c.prepaid_account.line_no,
                staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                staff_name=','.join([v.emp_name for v in salesstaff if v.emp_name]), 
                pp_type2=c.prepaid_account.pp_type2,condition_type1=c.prepaid_account.condition_type1,
                pos_daud_lineno=c.prepaid_account.pos_daud_lineno,Site_Codeid=site,
                Item_Codeid=c.itemcodeid,item_code=c.itemcodeid.item_code)
                prepaidacc.save()

            totaldisc = c.discount_amt + c.additional_discountamt
            totalpercent = c.discount + c.additional_discount


            #PosDisc Creation for each cart line with or without line disc (disc per/amt = line disc + trasac disc)
            # if transc disc for whole cart is applied that time need to create one record in PosDisc (disc per/amt = trasac disc).
            # discreason = None
            # if c.pos_disc.all().exists():
            #     # for d in c.disc_reason.all():
            #     #     if d.r_code == '100006' and d.r_desc == 'Others':
            #     #         discreason = c.discreason_txt
            #     #     elif d.r_desc:
            #     #         discreason = d.r_desc  
                       
            #     for po in c.pos_disc.all():
            #         po.sa_transacno = sa_transacno
            #         po.dt_status = "SA"
            #         po.dt_price = c.price
            #         po.save()
            # else:
            #     if totaldisc == 0.0 or totalpercent == 0.0 and len(c.pos_disc.all()) == 0:
            #         posdisc = PosDisc(sa_transacno=sa_transacno,dt_itemno=c.itemcodeid.item_code+"0000",disc_amt=totaldisc,
            #         disc_percent=totalpercent,dt_lineno=c.lineno,remark=discreason,site_code=site.itemsite_code,
            #         dt_status="SA",dt_auto=0,line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=c.price,istransdisc=False)
            #         posdisc.save()
                    # print(posdisc.pk,"posdisc")

                
            # #HoldItemDetail creation for retail products
            # if c.itemcodeid.Item_Divid.itm_code == 1 and c.itemcodeid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.itm_isactive == True:
            #     con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #     if not con_obj:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
            #         raise serializers.ValidationError(result)

            #     product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                
            #     hold = HoldItemDetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
            #     transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
            #     hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #     hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=c.trans_amt,hi_qty=c.holditemqty,
            #     hi_discamt=totaldisc,hi_discpercent=totalpercent,hi_discdesc=None,
            #     hi_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #     hi_lineno=c.lineno,hi_uom=c.item_uom.uom_desc,hold_item=True,hi_deposit=c.deposit,
            #     holditemqty=c.holditemqty,status="OPEN",sa_custno=cust_obj.cust_code,
            #     sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
            #     product_issues_no=product_issues_no)
            #     hold.save()
            #     # print(hold.pk,"hold")
            #     if hold.pk:
            #         con_obj.control_no = int(con_obj.control_no) + 1
            #         con_obj.save()

            # if '0' in str(c.quantity):
            #     no = str(c.quantity).split('0')
            #     if no[0] == '':
            #         number = no[1]
            #     else:
            #         number = c.quantity
            # else:
            #     number = c.quantity

            # dtl_st_ref_treatmentcode = ""
            # for i in range(1,int(number)+1):
            #     treat = c
            #     Price = c.deposit
            #     Unit_Amount = Price / c.quantity
            #     times = str(i).zfill(2)
            #     treatment_no = str(c.quantity).zfill(2)
            #     treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #     treatment_parentcode=treatment_parentcode,course=treat.itemcodeid.item_desc,times=times,
            #     treatment_no=treatment_no,price=Price,unit_amount=Unit_Amount,Cust_Codeid=treat.cust_noid,
            #     cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
            #     status="Open",item_code=treat.itemcodeid.item_code,Item_Codeid=treat.itemcodeid,
            #     sa_transacno=sa_transacno,sa_status="SA",
            #     dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,
            #     treatment_account=treatacc)

            #     #and str(treatmentid.treatment_code) == str(treatment_parentcode)+"-"+"01"
            #     if c.helper_ids.exists():
            #         for h in c.helper_ids.all().filter(times=times):
                       
            #             # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                        
            #             treatmentid.status = "Done"
            #             wp1 = h.workcommpoints / float(c.helper_ids.all().filter(times=times).count())
            #             share_amt = treatmentid.unit_amount / float(c.helper_ids.all().filter(times=times).count())

            #             TmpItemHelper.objects.filter(id=h.id).update(item_code=treatment_parentcode+"-"+str(times),
            #             item_name=c.itemcodeid.item_desc,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
            #             amount=treatmentid.unit_amount,sa_date=dtl.sa_date,site_code=site.itemsite_code,
            #             wp1=wp1,wp2=0.0,wp3=0.0)

            #             # Item helper create
            #             helper = ItemHelper(item_code=treatment_parentcode+"-"+str(times),item_name=c.itemcodeid.item_desc,
            #             line_no=dtl.dt_lineno,sa_transacno=sa_transacno,amount=treatmentid.unit_amount,
            #             helper_name=h.helper_name,helper_code=h.helper_code,sa_date=dtl.sa_date,
            #             site_code=site.itemsite_code,share_amt=share_amt,helper_transacno=sa_transacno,
            #             wp1=wp1,wp2=0.0,wp3=0.0)
            #             helper.save()
            #             # print(helper.id,"helper")

            #             #appointment treatment creation
            #             if h.appt_fr_time and h.appt_to_time != False and h.add_duration != False:
            #                 stock_obj = c.itemcodeid

            #                 if stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
            #                     stk_duration = 60
            #                 else:
            #                     stk_duration = int(stock_obj.srv_duration)

            #                 stkduration = int(stk_duration) + 30
            #                 # print(stkduration,"stkduration")

            #                 hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
            #                 start_time =  get_in_val(self, h.appt_fr_time)
            #                 starttime = datetime.datetime.strptime(start_time, "%H:%M")

            #                 end_time = starttime + datetime.timedelta(minutes = stkduration)
            #                 endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            #                 duration = hrs

            #                 treat_all = Treatment.objects.filter(sa_transacno=sa_transacno,treatment_parentcode=treatment_parentcode)
            #                 length = [t.status for t in treat_all if t.status == 'Done']
            #                 if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
            #                     master_status = "Done"
            #                 else:
            #                     master_status = "Open"
   
            #                 master = Treatment_Master(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #                 treatment_parentcode=treatment_parentcode,sa_transacno=sa_transacno,
            #                 course=stock_obj.item_desc,times=times,treatment_no=treatment_no,
            #                 price=stock_obj.item_price,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
            #                 cust_name=cust_obj.cust_name,status=master_status,unit_amount=stock_obj.item_price,
            #                 Item_Codeid=stock_obj,item_code=stock_obj.item_code,
            #                 sa_status="SA",dt_lineno=dtl.dt_lineno,type="N",duration=stkduration,
            #                 Site_Codeid=site,site_code=site.itemsite_code,
            #                 trmt_room_code=h.Room_Codeid.room_code,Trmt_Room_Codeid=h.Room_Codeid,
            #                 Item_Class=stock_obj.Item_Classid,PIC=stock_obj.Stock_PIC,
            #                 start_time=h.appt_fr_time,end_time=h.appt_to_time,add_duration=h.add_duration,
            #                 appt_remark=stock_obj.item_desc,requesttherapist=False)

            #                 master.save()
            #                 master.emp_no.add(h.helper_id.pk)
            #                 # print(master.id,"master")

            #                 ctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #                 if not ctrl_obj:
            #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
            #                     raise serializers.ValidationError(result)
                            
            #                 appt_code = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                            
            #                 channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()
            #                 if not channel:
            #                     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
            #                     raise serializers.ValidationError(result)

            #                 appt = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=date.today(),
            #                 appt_fr_time=h.appt_fr_time,Appt_typeid=channel,appt_type=channel.appt_type_desc,
            #                 appt_phone=cust_obj.cust_phone2,appt_remark=stock_obj.item_desc,
            #                 emp_noid=h.helper_id,emp_no=h.helper_id.emp_code,emp_name=h.helper_id.emp_name,
            #                 cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
            #                 appt_to_time=h.appt_to_time,Appt_Created_Byid=fmspw,
            #                 appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            #                 Room_Codeid=h.Room_Codeid,room_code=h.Room_Codeid.room_code,
            #                 Source_Codeid=h.Source_Codeid,source_code=h.Source_Codeid.source_code,
            #                 cust_refer=cust_obj.cust_refer,requesttherapist=False,new_remark=h.new_remark,
            #                 item_code=stock_obj.item_code,sa_transacno=sa_transacno,treatmentcode=str(treatment_parentcode)+"-"+str(times))
            #                 appt.save()

            #                 if appt.pk:
            #                     master.Appointment = appt
            #                     master.appt_time = timezone.now()
            #                     master.save()
            #                     ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
            #                     ctrl_obj.save()
                            
            #         #treatment Account creation for done treatment 01
            #         if c.helper_ids.all().filter(times=times).first():
            #             acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,treatment_parentcode=treatment_parentcode).order_by('id').last()
            #             td_desc = str(stock_obj.item_desc)
            #             balance = acc_ids.balance - treatmentid.unit_amount if acc_ids.balance else treatmentid.unit_amount

            #             treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
            #             cust_code=cust_obj.cust_code,ref_no=treatmentid.treatment_code,
            #             description=td_desc,type='Sales',amount=-treatmentid.unit_amount,balance=balance,
            #             User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=treatmentid.sa_transacno,
            #             sa_transacno=sa_transacno,qty=1,outstanding=treatacc.outstanding,deposit=0.0,
            #             treatment_parentcode=treatmentid.treatment_parentcode,treatment_code="",
            #             sa_status="SA",cas_name=fmspw.pw_userlogin,
            #             sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #             sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #             dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
            #             treat_code=treatmentid.treatment_parentcode,itemcart=c)
            #             treatacc_td.save()
            #             # print(treatacc_td.id,"treatacc_td")
                        
            #             if dtl_st_ref_treatmentcode == "":
            #                 dtl_st_ref_treatmentcode = str(treatment_parentcode)+"-"+str(times)
            #             elif not dtl_st_ref_treatmentcode == "":
            #                 dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)


            #     treatmentid.save()
            #     # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
            #     # print(treatmentid.id,"treatment_id")

            # if treatacc and treatmentid:
            #     controlobj.control_no = int(controlobj.control_no) + 1
            #     controlobj.save()

            # # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
            # dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
            # dtl.first_trmt_done = True
            # dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
            # dtl.first_trmt_done_staff_name = ','.join([v.helper_id.emp_name for v in c.helper_ids.all() if v.helper_id.emp_name])
            # dtl.save()

        #header creation
        if alsales_staff:
            Emp_code = alsales_staff.emp_code
            Emp_name = alsales_staff.emp_name
        else:
            alsales_staff = None
            Emp_code = ""  
            Emp_name = ""

        outstanding_new += outstanding_acc
        print(value['tax_amt'],"tax_amt")
        hdr = PosHaud(cas_name=fmspw.pw_userlogin,sa_transacno=sa_transacno,sa_status="SA",
        sa_totamt="{:.2f}".format(float(value['deposit_amt'])),sa_totqty=totQty,sa_totdisc="{:.2f}".format(float(total_disc)),sa_totgst="{:.2f}".format(float(value['tax_amt'])),
        sa_staffnoid=alsales_staff,sa_staffno=Emp_code,sa_staffname=Emp_name,sa_custnoid=cust_obj,sa_custno=cust_obj.cust_code,
        sa_custname=cust_obj.cust_name,sa_discuser=None,sa_disctotal="{:.2f}".format(float(total_disc)),ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
        sa_depositamt="{:.2f}".format(float(value['deposit_amt'])),sa_transacamt="{:.2f}".format(float(value['trans_amt'])),sa_round="{:.2f}".format(float(value['sa_Round'])),
        total_outstanding="{:.2f}".format(float(outstanding_new)),trans_user_login=fmspw.pw_password,trans_user_loginid=fmspw,
        sa_transacno_ref=sa_transacno_ref,sa_transacno_type="Receipt",
        issuestrans_user_login=fmspw.pw_userlogin)
        
        # appt_time=app_obj.appt_fr_time,

        hdr.save()
        # print(hdr.id,"hdr")
        if hdr.pk:
            control_obj.control_no = int(control_obj.control_no) + 1
            control_obj.save()
            refcontrol_obj.control_no = int(refcontrol_obj.control_no) + 1
            refcontrol_obj.save()
       
        state = status.HTTP_201_CREATED
        message = "Created Succesfully"
        error = False
        taud_d = PosTaud.objects.filter(pk__in=taud_ids,ItemSIte_Codeid__pk=site.pk)
        serializer_final = self.get_serializer(taud_d, many=True)
        data_d = serializer_final.data
        for data in data_d:
            data['subtotal'] = "{:.2f}".format(float(data['subtotal']))
            data['discount_amt'] =  "{:.2f}".format(float(data['discount_amt']))
            data['pay_actamt'] = "{:.2f}".format(float(data['pay_actamt']))
            data['tax'] = "{:.2f}".format(float(data['tax']))
            data['pay_amt'] = "{:.2f}".format(float(data['pay_amt']))
            data['billable_amount'] = "{:.2f}".format(float(data['billable_amount']))
        
        for i in id_lst:
            c = ItemCart.objects.filter(id=i,isactive=True).exclude(type__in=type_ex).first()
            c.is_payment = True
            c.cart_status = "Completed"
            c.sa_transacno = sa_transacno
            c.save()    

        result = {'status': state,"message":message,'error': error, 'data':  serializer_final.data}
        return Response(result, status=status.HTTP_201_CREATED)

        state = status.HTTP_400_BAD_REQUEST
        message = "Invalid Input"
        error = True
        result = {'status': state,"message":message,'error': error, 'data':  serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def SalesPostaudCreate(self, request):
        global type_ex
        cart_date = timezone.now().date()

        request = self.request
        if request.GET.get('cart_date',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give cart date",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('cust_noid',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Customer ID",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_noid',None),cust_isactive=True).first()
        if not cust_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        cart_id = request.GET.get('cart_id',None)
        if cart_id is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content cart_id is not given",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if not self.request.GET.get('sitecodeid',None) is None:
            site = ItemSitelist.objects.filter(pk=self.request.GET.get('sitecodeid',None),itemsite_isactive=True).first()
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Site ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site = fmspw.loginsite

        empl = fmspw.Emp_Codeid
       
        cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
        cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site).exclude(type__in=type_ex)
        if cartc_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
       

        control_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw.loginsite.pk).first()
        if not control_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
            raise serializers.ValidationError(result)
        
        sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
        
        refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference Redeem Service No",Site_Codeid__pk=fmspw.loginsite.pk).first()
        if not refcontrol_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference Redeem Service Control No does not exist!!",'error': True} 
            raise serializers.ValidationError(result)
        
        sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
        
        
        queryset = self.filter_queryset(self.get_queryset())
        if not queryset:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 4",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
    
        value = postaud_calculation(self, request, queryset)
       
        pay_amt = 0.0  ; taud_ids = []
        # satransacno = request.GET.get('satransacno',None)
        for r in request.data:
            pay_amt += float(r['pay_amt'])

        # print(pay_amt,value['billable_amount']) 
        if pay_amt != 0.0:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Pay amount should be equal to Zero for Redeem!!",'error': True} 
            raise serializers.ValidationError(result)

        for idx, req in enumerate(request.data, start=1): 
            # print(idx,"idx")
            paytable = Paytable.objects.filter(pk=req['pay_typeid'],pay_isactive=True).first()
            pay_ids = Paytable.objects.filter(pk=req['pay_typeid'],pay_isactive=True)
            if not pay_ids:
                msg = "Paytable ID %s is does not exist!!".format(req['pay_typeid'])
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                raise serializers.ValidationError(result)

            serializer_one = self.get_serializer(data=req)

            #pos_taud creation
            if serializer_one.is_valid():
                # pay_gst = (float(req['pay_amt']) / (100+gst.item_value)) * gst.item_value
                if gst.is_exclusive == True:
                    pay_gst = float(req['pay_amt']) * (gst.item_value / 100)
                else:
                    pay_gst = (float(req['pay_amt']) * gst.item_value ) / (100+gst.item_value)

                taud = serializer_one.save(sa_transacno=sa_transacno,billed_by=fmspw,ItemSIte_Codeid=site,itemsite_code=site.itemsite_code,
                pay_groupid=paytable.pay_groupid,pay_group=paytable.pay_groupid.pay_group_code,pay_typeid=paytable,pay_type=paytable.pay_code,
                pay_desc=paytable.pay_description,pay_tendamt=req['pay_amt'],pay_tendrate=1.0,pay_amt=req['pay_amt'],pay_amtrate=1.0,pay_status=1,dt_lineno=idx,
                pay_actamt=0.0,subtotal="{:.2f}".format(float(value['subtotal'])) if value['subtotal'] else 0.0,paychange=0.0,
                tax=0.0, discount_amt="{:.2f}".format(float(value['discount'])) if value['discount'] else 0.0,
                billable_amount=0.0,pay_gst_amt_collect=0.0,pay_gst=0.0)
                # print(taud,"taud")
                # print(taud.pay_premise,taud.credit_debit)
                if taud:
                    taud_ids.append(taud.pk)

                # depo_type = DepositType(sa_transacno=sa_transacno,pay_group=paytable.pay_groupid.pay_group_code,
                # pay_type=paytable.pay_code,amount=req['pay_amt'],card_no=None,pay_desc=paytable.pay_description,
                # pay_tendcurr=None,pay_tendrate=1.0,site_code=site.itemsite_code,pos_taud_lineno=idx) 
                # depo_type.save()
                # # print(depo_type.id,"depo_type")    


        # outstanding =  float(value['trans_amt']) - float(value['deposit_amt'])
        #detail creation
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0;outstanding = 0.0
        cart_ids = queryset
        for idx, c in enumerate(cart_ids, start=1):
            if idx == 1:
                alservice_staff = c.service_staff.all().first()

            if not c.treatment.helper_ids.all().exists():
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment done service staffs not mapped!!",'error': True} 
                raise serializers.ValidationError(result)


            # print(c,"cc")
            controlobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
            if not controlobj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
            treatment_parentcode = "TRM"+str(controlobj.control_prefix)+str(controlobj.Site_Codeid.itemsite_code)+str(controlobj.control_no)
            
            service_staff = c.service_staff.all().first()
            servicestaff = c.service_staff.all()

            # total = c.price * c.quantity
            totQty += c.quantity
            # discount_amt += float(c.discount_amt)
            # additional_discountamt += float(c.additional_discountamt)
            total_disc += c.discount_amt + c.additional_discountamt
            # dt_discPercent = (float(total_disc) * 100) / float(value['subtotal'])
            dt_discPercent = c.discount + c.additional_discount

            if c.is_foc == True:
                isfoc = True
                item_remarks = c.focreason.foc_reason_ldesc if c.focreason and c.focreason.foc_reason_ldesc else None 
            else:
                isfoc = False  
                item_remarks = None   
            
           
            time = c.treatment.times 
            dt_itemdesc = str(time)+"/"+str(c.treatment.treatment_no)+" "+str(c.itemcodeid.item_name)

            dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid if c.itemcodeid else None,
            dt_itemno=c.itemcodeid.item_code+"0000" if c.itemcodeid else None,dt_itemdesc=dt_itemdesc if dt_itemdesc else None,dt_price=c.price if c.price else 0.0,
            dt_promoprice="{:.2f}".format(float(c.discount_price)) if c.discount_price else 0.0,dt_amt="{:.2f}".format(float(c.trans_amt)) if c.trans_amt else 0.0,dt_qty=c.quantity if c.quantity else 0.0,dt_discamt=0.0,
            dt_discpercent=0.0,dt_Staffnoid=service_staff if service_staff else None,dt_staffno=service_staff.emp_code if service_staff.emp_code else None,
            dt_staffname=service_staff.emp_name if service_staff.emp_name else None,dt_discuser=None,ItemSite_Codeid=site,
            itemsite_code=site.itemsite_code,dt_transacamt=0.0,dt_deposit=0.0,dt_lineno=c.lineno,
            itemcart=c,st_ref_treatmentcode=c.treatment.treatment_code if c.treatment.treatment_code else '',first_trmt_done=False,
            first_trmt_done_staff_code="",first_trmt_done_staff_name="",
            record_detail_type="TD",trmt_done_staff_code=','.join([v.emp_code for v in servicestaff if v.emp_code]),
            trmt_done_staff_name=','.join([v.emp_name for v in servicestaff if v.emp_name]),
            trmt_done_id=c.treatment.treatment_code if c.treatment.treatment_code else '',trmt_done_type="N",gst_amt_collect=0.0,
            dt_remark=c.remark if c.remark else '',isfoc=isfoc,item_remarks=item_remarks,
            item_status_code=c.itemstatus.status_desc if c.itemstatus and c.itemstatus.status_desc else None)
            #appt_time=app_obj.appt_fr_time,                

            dtl.save()
            # print(dtl.id,"dtl")
            if dtl.pk not in id_lst:
                id_lst.append(c.pk)


            #multi staff table creation
            ratio = 0.0
            if c.sales_staff.all().count() > 0:
                count = c.sales_staff.all().count()
                ratio = float(c.ratio) / float(count)

            multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000" if c.itemcodeid else None,
            emp_code=service_staff.emp_code if service_staff.emp_code else None,ratio=c.ratio if c.ratio else None,salesamt="{:.2f}".format(float(c.deposit)) if c.deposit else 0.0,type=None,isdelete=False,role=1,
            dt_lineno=c.lineno if c.lineno else None)
            multi.save()
            # print(multi.id,"multi")


            acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            treatment_parentcode=c.treatment.treatment_parentcode,Site_Codeid=site).order_by('id').exclude(type='Sales').last()

            Balance = acc_ids.balance - c.treatment.unit_amount if acc_ids.balance else c.treatment.unit_amount

            outstanding += acc_ids.outstanding
            print(outstanding,"foc")
            #treatment Account creation
            # amount=-float("{:.2f}".format(float(c.treatment.unit_amount))) if c.treatment.unit_amount else 0.0,balance="{:.2f}".format(float(Balance)) if Balance else None,User_Nameid=fmspw,
            treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
            description=dt_itemdesc,ref_no=c.treatment.treatment_code if c.treatment.treatment_code else '',type="Sales",
            amount=-float("{:.2f}".format(float(c.treatment.unit_amount * c.quantity ) )) if c.treatment.unit_amount else 0.0,balance="{:.2f}".format(float(Balance)) if Balance else None,User_Nameid=fmspw,
            user_name=fmspw.pw_userlogin,ref_transacno=c.treatment.sa_transacno if c.treatment.sa_transacno else None,sa_transacno=sa_transacno,
            qty=c.quantity if c.quantity else None,outstanding="{:.2f}".format(float(acc_ids.outstanding)) if acc_ids.outstanding else 0.0,deposit=0,
            treatment_parentcode=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else '',treatment_code="",sa_status="SA",
            cas_name=fmspw.pw_userlogin,sa_staffno=service_staff.emp_code if service_staff.emp_code else '',
            sa_staffname=service_staff.emp_name if service_staff.emp_name else '',dt_lineno=c.lineno,
            Site_Codeid=site,site_code=site.itemsite_code,treat_code=c.treatment.treatment_parentcode if c.treatment.treatment_parentcode else None,itemcart=c,
            focreason=item_remarks)
            treatacc.save()
            # print(treatacc.id,"treatacc")
            helper = c.treatment.helper_ids.all().first()
            # trmt_up = Treatment.objects.filter(pk=c.treatment.pk).update(status="Done",
            # trmt_room_code=helper.Room_Codeid.room_code if helper.Room_Codeid else None,record_status='PENDING',
            # transaction_time=timezone.now(),treatment_count_done=1)
            print(c.quantity,"here")
            for iqty in range(0, c.quantity-1):
                print(c.treatment.pk-iqty,"iqty")
                trmt_up = Treatment.objects.filter(pk=c.treatment.pk-iqty).update(status="Done",
                trmt_room_code=helper.Room_Codeid.room_code if helper.Room_Codeid else None,record_status='PENDING',
                transaction_time=timezone.now(),treatment_count_done=1)
    

            totaldisc = c.discount_amt + c.additional_discountamt
            totalpercent = c.discount + c.additional_discount

            # if c.discount_amt != 0.0 and c.additional_discountamt != 0.0:
            #     totaldisc = c.discount_amt + c.additional_discountamt
            #     totalpercent = c.discount + c.additional_discount
            #     istransdisc = True
            # elif c.discount_amt != 0.0:
            #     totaldisc = c.discount_amt
            #     totalpercent = c.discount
            #     istransdisc = False
            # elif c.additional_discountamt != 0.0:
            #     totaldisc = c.additional_discountamt
            #     totalpercent = c.additional_discount
            #     istransdisc = True    
            # else:
            #     totaldisc = 0.0
            #     totalpercent = 0.0
            #     istransdisc = False

            #PosDisc Creation for each cart line with or without line disc (disc per/amt = line disc + trasac disc)
            # if transc disc for whole cart is applied that time need to create one record in PosDisc (disc per/amt = trasac disc).
            # discreason = None
            # if c.pos_disc.all().exists():
            #     # for d in c.disc_reason.all():
            #     #     if d.r_code == '100006' and d.r_desc == 'Others':
            #     #         discreason = c.discreason_txt
            #     #     elif d.r_desc:
            #     #         discreason = d.r_desc  
                       
            #     for po in c.pos_disc.all():
            #         po.sa_transacno = sa_transacno
            #         po.dt_status = "SA"
            #         po.dt_price = c.price
            #         po.save()
            # else:
            #     if totaldisc == 0.0 or totalpercent == 0.0 and len(c.pos_disc.all()) == 0:
            #         posdisc = PosDisc(sa_transacno=sa_transacno,dt_itemno=c.itemcodeid.item_code+"0000",disc_amt=totaldisc,
            #         disc_percent=totalpercent,dt_lineno=c.lineno,remark=discreason,site_code=site.itemsite_code,
            #         dt_status="SA",dt_auto=0,line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=c.price,istransdisc=False)
            #         posdisc.save()
            #         # print(posdisc.pk,"posdisc")

                
            #HoldItemDetail creation for retail products
            # if c.itemcodeid.Item_Divid.itm_code == 1 and c.itemcodeid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.itm_isactive == True:
            #     con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
            #     if not con_obj:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
            #         raise serializers.ValidationError(result)

            #     product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                
            #     hold = HoldItemDetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
            #     transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
            #     hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            #     hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=c.trans_amt,hi_qty=c.holditemqty,
            #     hi_discamt=totaldisc,hi_discpercent=totalpercent,hi_discdesc=None,
            #     hi_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            #     hi_lineno=c.lineno,hi_uom=c.item_uom.uom_desc,hold_item=True,hi_deposit=c.deposit,
            #     holditemqty=c.holditemqty,status="OPEN",sa_custno=cust_obj.cust_code,
            #     sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
            #     product_issues_no=product_issues_no)
            #     hold.save()
            #     # print(hold.pk,"hold")
            #     if hold.pk:
            #         con_obj.control_no = int(con_obj.control_no) + 1
            #         con_obj.save()

            # if '0' in str(c.quantity):
            #     no = str(c.quantity).split('0')
            #     if no[0] == '':
            #         number = no[1]
            #     else:
            #         number = c.quantity
            # else:
            #     number = c.quantity

            # dtl_st_ref_treatmentcode = "";dtl_first_trmt_done = False
            # for i in range(1,int(number)+1):
            #     treat = c
            #     Price = c.trans_amt
            #     Unit_Amount = Price / c.quantity
            #     times = str(i).zfill(2)
            #     treatment_no = str(c.quantity).zfill(2)
            #     treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
            #     treatment_parentcode=treatment_parentcode,course=treat.itemcodeid.item_desc,times=times,
            #     treatment_no=treatment_no,price=Price,unit_amount=Unit_Amount,Cust_Codeid=treat.cust_noid,
            #     cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
            #     status="Open",item_code=treat.itemcodeid.item_code,Item_Codeid=treat.itemcodeid,
            #     sa_transacno=sa_transacno,sa_status="SA",type="N",
            #     dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,
            #     treatment_account=treatacc)

                #and str(treatmentid.treatment_code) == str(treatment_parentcode)+"-"+"01"
            if c.treatment.helper_ids.exists():
                for h in c.treatment.helper_ids.all():
                    
                    # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                    
                    # treatmentid.status = "Done"
                    wp1 = h.workcommpoints / float(c.treatment.helper_ids.all().count())
                    share_amt = float(c.treatment.unit_amount) / float(c.treatment.helper_ids.all().count())

                    TmpItemHelper.objects.filter(id=h.id).update(item_code=c.treatment.treatment_code,
                    item_name=c.itemcodeid.item_name,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
                    amount=c.treatment.unit_amount,sa_date=dtl.sa_date,site_code=site.itemsite_code,
                    wp1=wp1,wp2=0.0,wp3=0.0)

                    # Item helper create
                    helper = ItemHelper(item_code=c.treatment.treatment_code,item_name=c.itemcodeid.item_name,
                    line_no=dtl.dt_lineno,sa_transacno=c.treatment.sa_transacno,amount=c.treatment.unit_amount,
                    helper_name=h.helper_name,helper_code=h.helper_code,sa_date=dtl.sa_date,
                    site_code=site.itemsite_code,share_amt=share_amt,helper_transacno=sa_transacno,
                    wp1=wp1,wp2=0.0,wp3=0.0)
                    helper.save()
                    # print(helper.id,"helper")

                    #appointment treatment creation
                    if h.appt_fr_time and h.appt_to_time != False and h.add_duration != False:
                        stock_obj = c.itemcodeid

                        if stock_obj.srv_duration is None or float(stock_obj.srv_duration) == 0.0:
                            stk_duration = 60
                        else:
                            stk_duration = int(stock_obj.srv_duration)

                        stkduration = int(stk_duration) + 30
                        # print(stkduration,"stkduration")

                        hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                        start_time =  get_in_val(self, h.appt_fr_time)
                        starttime = datetime.datetime.strptime(start_time, "%H:%M")

                        end_time = starttime + datetime.timedelta(minutes = stkduration)
                        endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                        duration = hrs

                        treat_all = Treatment.objects.filter(sa_transacno=c.treatment.sa_transacno,
                        treatment_parentcode=c.treatment.treatment_parentcode,site_code=site.itemsite_code)
                        length = [t.status for t in treat_all if t.status == 'Done']
                        if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
                            master_status = "Done"
                        else:
                            master_status = "Open"

                        master = Treatment_Master(treatment_code=c.treatment.treatment_code,
                        treatment_parentcode=c.treatment.treatment_parentcode,sa_transacno=c.treatment.sa_transacno,
                        course=stock_obj.item_desc,times=h.times,treatment_no=h.treatment_no,
                        price="{:.2f}".format(float(c.treatment.unit_amount)) if c.treatment.unit_amount else 0.0,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
                        cust_name=cust_obj.cust_name,status=master_status,unit_amount="{:.2f}".format(float(c.treatment.unit_amount)) if c.treatment.unit_amount else 0.0,
                        Item_Codeid=stock_obj,item_code=stock_obj.item_code,
                        sa_status="SA",dt_lineno=dtl.dt_lineno,type="N",duration=stkduration,
                        Site_Codeid=site,site_code=site.itemsite_code,
                        trmt_room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,Trmt_Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,
                        Item_Class=stock_obj.Item_Classid if stock_obj.Item_Classid else None,PIC=stock_obj.Stock_PIC if stock_obj.Stock_PIC else None,
                        start_time=h.appt_fr_time if h.appt_fr_time else None,end_time=h.appt_to_time if h.appt_to_time else None,add_duration=h.add_duration if h.add_duration else None,
                        appt_remark=stock_obj.item_desc if stock_obj.item_desc else None,requesttherapist=False)

                        master.save()
                        master.emp_no.add(h.helper_id.pk)
                        # print(master.id,"master")

                        ctrl_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=fmspw.loginsite.pk).first()
                        if not ctrl_obj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
                            raise serializers.ValidationError(result)
                        
                        appt_code = str(ctrl_obj.Site_Codeid.itemsite_code)+str(ctrl_obj.control_prefix)+str(ctrl_obj.control_no)
                        
                        channel = ApptType.objects.filter(appt_type_code="10003",appt_type_isactive=True).first()
                        # if not channel:
                        #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
                        #     raise serializers.ValidationError(result)

                        appt = Appointment(cust_noid=cust_obj,cust_no=cust_obj.cust_code,appt_date=date.today(),
                        appt_fr_time=h.appt_fr_time if h.appt_fr_time else None,Appt_typeid=channel if channel else None,appt_type=channel.appt_type_desc if channel.appt_type_desc else None,
                        appt_phone=cust_obj.cust_phone2[:20] if cust_obj.cust_phone2 else None,appt_remark=stock_obj.item_desc if stock_obj.item_desc else None,
                        emp_noid=h.helper_id if h.helper_id else None,emp_no=h.helper_id.emp_code if h.helper_id.emp_code else None,emp_name=h.helper_id.emp_name if h.helper_id.emp_name else None,
                        cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
                        appt_to_time=h.appt_to_time if h.appt_to_time else None,Appt_Created_Byid=fmspw,
                        appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                        Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,
                        Source_Codeid=h.Source_Codeid if h.Source_Codeid else None,source_code=h.Source_Codeid.source_code if h.Source_Codeid else None,
                        cust_refer=cust_obj.cust_refer if cust_obj.cust_refer else None,requesttherapist=False,new_remark=h.new_remark if h.new_remark else None,
                        item_code=stock_obj.item_code if stock_obj.item_code else None,sa_transacno=c.treatment.sa_transacno,treatmentcode=c.treatment.treatment_code)
                        appt.save()

                        if appt.pk:
                            master.Appointment = appt
                            master.appt_time = timezone.now()
                            master.save()
                            ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
                            ctrl_obj.save()
                        
                    #treatment Account creation for done treatment 01
                    # if c.helper_ids.all().filter(times=times).first():
                    #     acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,treatment_parentcode=treatment_parentcode).order_by('id').last()
                    #     td_desc = str(stock_obj.item_desc)
                    #     balance = acc_ids.balance - treatmentid.unit_amount if acc_ids.balance else treatmentid.unit_amount

                    #     treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
                    #     cust_code=cust_obj.cust_code,ref_no=treatmentid.treatment_code,
                    #     description=td_desc,type='Sales',amount=-treatmentid.unit_amount,balance=balance,
                    #     User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=treatmentid.sa_transacno,
                    #     sa_transacno=sa_transacno,qty=1,outstanding=treatacc.outstanding,deposit=0.0,
                    #     treatment_parentcode=treatmentid.treatment_parentcode,treatment_code="",
                    #     sa_status="SA",cas_name=fmspw.pw_userlogin,
                    #     sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    #     sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                    #     dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
                    #     treat_code=treatmentid.treatment_parentcode,itemcart=c)
                    #     treatacc_td.save()
                    #     # print(treatacc_td.id,"treatacc_td")
                    #     dtl_first_trmt_done = True
                    #     if dtl_st_ref_treatmentcode == "":
                    #         dtl_st_ref_treatmentcode = str(treatment_parentcode)+"-"+str(times)
                    #     elif not dtl_st_ref_treatmentcode == "":
                    #         dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)


                # treatmentid.save()
                # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
                # print(treatmentid.id,"treatment_id")

            if treatacc:
                controlobj.control_no = int(controlobj.control_no) + 1
                controlobj.save()

            # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
            # dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
            # dtl.first_trmt_done = dtl_first_trmt_done
            # dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
            # dtl.first_trmt_done_staff_name = ','.join([v.helper_id.emp_name for v in c.helper_ids.all() if v.helper_id.emp_name])
            # dtl.save()

        #header creation
        if alservice_staff:
            Emp_code = alservice_staff.emp_code
            Emp_name = alservice_staff.emp_name
        else:
            alservice_staff = None
            Emp_code = ""  
            Emp_name = ""

        hdr = PosHaud(cas_name=fmspw.pw_userlogin,sa_transacno=sa_transacno,sa_status="SA",
        sa_totamt=0.0,sa_totqty=0.0,sa_totdisc=0.0,sa_totgst=None,
        sa_staffnoid=alservice_staff,sa_staffno=Emp_code,sa_staffname=Emp_name,sa_custnoid=cust_obj,sa_custno=cust_obj.cust_code,
        sa_custname=cust_obj.cust_name,sa_discuser=None,sa_disctotal=0.0,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
        sa_depositamt=0.0,sa_transacamt=0.0,sa_round=0,total_outstanding=outstanding,
        trans_user_login=fmspw.pw_password,trans_user_loginid=fmspw,sa_transacno_ref=sa_transacno_ref,sa_transacno_type="Redeem Service",
        issuestrans_user_login=fmspw.pw_userlogin)
        # appt_time=app_obj.appt_fr_time,

        hdr.save()
        # print(hdr.id,"hdr")
        if hdr.pk:
            control_obj.control_no = int(control_obj.control_no) + 1
            control_obj.save()
            refcontrol_obj.control_no = int(refcontrol_obj.control_no) + 1
            refcontrol_obj.save()

       
        state = status.HTTP_201_CREATED
        message = "Created Succesfully"
        error = False
        taud_d = PosTaud.objects.filter(pk__in=taud_ids,ItemSIte_Codeid__pk=site.pk)
        serializer_final = self.get_serializer(taud_d, many=True)
        data_d = serializer_final.data
        for data in data_d:
            data['subtotal'] = "{:.2f}".format(float(data['subtotal']))
            data['discount_amt'] =  "{:.2f}".format(float(data['discount_amt']))
            data['pay_actamt'] = "{:.2f}".format(float(data['pay_actamt']))
            data['tax'] = "{:.2f}".format(float(data['tax']))
            data['pay_amt'] = "{:.2f}".format(float(data['pay_amt']))
            data['billable_amount'] = "{:.2f}".format(float(data['billable_amount']))
        
        for i in id_lst:
            c = ItemCart.objects.filter(id=i,isactive=True).exclude(type__in=type_ex).first()
            c.is_payment = True
            c.cart_status = "Completed"
            c.sa_transacno = sa_transacno
            c.save()    

        result = {'status': state,"message":message,'error': error, 'data':  serializer_final.data}
        return Response(result, status=status.HTTP_201_CREATED)

        state = status.HTTP_400_BAD_REQUEST
        message = "Invalid Input"
        error = True
        result = {'status': state,"message":message,'error': error, 'data':  serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


def receipt_calculation(self, request, daud):
    fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
    site = fmspw.loginsite
    satransacno = request.GET.get('sa_transacno',None)
    # cart_ids = ItemCart.objects.filter(isactive=True,Appointment=app_obj,is_payment=True)
    gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
    subtotal = 0.0; discount = 0.0;discount_amt=0.0;additional_discountamt=0.0; 
    trans_amt=0.0 ;deposit_amt =0.0; tax_amt = 0.0; billable_amount=0.0
    posdaud = PosDaud.objects.filter(sa_transacno=satransacno,ItemSite_Codeid__pk=site.pk).first()

    for ct in daud:
        c = ct.itemcart
        # total = "{:.2f}".format(float(c.price) * int(c.quantity))
        subtotal += float(c.total_price)
        discount_amt += float(c.discount_amt)
        additional_discountamt += float(c.additional_discountamt)
        trans_amt += float(c.trans_amt)
        deposit_amt += float(c.deposit)

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
    calcgst = 0
    if gst:
        calcgst = gst.item_value
    if calcgst > 0:
        sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
        if sitegst:
            if sitegst.site_is_gst == False:
                calcgst = 0
    print(calcgst,"1 calcgst")

    if calcgst > 0:
        if gst.is_exclusive == True:
            tax_amt = deposit_amt * (calcgst / 100)
            billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
        else:
            billable_amount = "{:.2f}".format(deposit_amt)
            tax_amt = deposit_amt * calcgst / (100+calcgst)
    else:
        billable_amount = "{:.2f}".format(deposit_amt)

    # print(request.data,"request_data")
    totaltax=0
    linetax=0
    if request.data is not None:
        for rgt in request.data:
            paytablegt = Paytable.objects.filter(pk=rgt['pay_typeid'],pay_isactive=True).first()
            stringgt = paytablegt.gt_group
            st_newgt= "".join(stringgt.split())
            linetax=0
            if st_newgt == 'GT1': 
                if calcgst > 0:
                    if gst.is_exclusive == True:
                        linetax = rgt['pay_amt'] * (calcgst / 100)
                    else:
                        linetax = rgt['pay_amt'] * calcgst / (100+calcgst)
            totaltax+=linetax

    # print(totaltax,"totaltax")
    if totaltax>0:
        tax_amt = totaltax

    sub_total = "{:.2f}".format(float(subtotal))
    round_val = float(round_calc(billable_amount)) # round()
    billable_amount = float(billable_amount) + round_val 
    sa_Round = round_val
    discount = discount_amt + additional_discountamt

    now = datetime.datetime.now()
    time = datetime.datetime.now().strftime('%H:%M:%S')  #  Time like '23:12:05'
    fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
    itemvalue = "{:.2f}".format(float(gst.item_value))

    value = {'date':now,'time':time,'billed_by':fmspw.pw_userlogin,'bill_no':posdaud.sa_transacno,
    'subtotal':sub_total,'discount': "{:.2f}".format(float(discount)),'trans_amt': "{:.2f}".format(float(trans_amt)),
    'deposit_amt': "{:.2f}".format(float(deposit_amt)),'tax_amt':"{:.2f}".format(float(tax_amt)),
    'tax_lable': "Tax Amount"+"("+str(itemvalue)+" "+"%"+")",'sa_Round': "{:.2f}".format(float(sa_Round)),
    'billable_amount': "{:.2f}".format(float(billable_amount))}
    return value

   
class CustomerReceiptPrintList(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = PosHaud.objects.filter().order_by('-pk')
    serializer_class = PoshaudSerializer
   
    def list(self, request):
        if request.GET.get('sa_transacno',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sa_transacno!!",'error': True} 
            raise serializers.ValidationError(result)    

        satransacno = request.GET.get('sa_transacno',None)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        ip = get_client_ip(request)
        #sa_transacno_type="Receipt"
        hdr_ids = PosHaud.objects.filter(sa_transacno=satransacno,ItemSite_Codeid__pk=site.pk).only('sa_transacno','ItemSite_Codeid').order_by("pk")
        # count = hdr_ids.count()
        # if count > 1:
        #     last = hdr_ids.last()
        #     delhdr_ids = PosHaud.objects.filter(sa_transacno=satransacno,
        #     ItemSite_Codeid=site).only('sa_transacno','ItemSite_Codeid').exclude(pk=last.pk).order_by("pk").delete()


        hdr = PosHaud.objects.filter(sa_transacno=satransacno,ItemSite_Codeid__pk=site.pk).only('sa_transacno','ItemSite_Codeid').order_by("pk")[:1]
        if not hdr:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud ID does not exist!!",'error': True} 
            raise serializers.ValidationError(result) 



        daud = PosDaud.objects.filter(sa_transacno=satransacno,ItemSite_Codeid__pk=site.pk)
        taud = PosTaud.objects.filter(sa_transacno=satransacno,ItemSIte_Codeid__pk=site.pk)
        title = Title.objects.filter(product_license=site.itemsite_code).order_by("pk").first()
        if title:
            pic = False
            if title.logo_pic:
                pic = str(ip)+str(title.logo_pic.url)
            company_hdr = {'logo':pic if pic else '','name':title.trans_h1 if title.trans_h1 else '','address': title.trans_h2 if title.trans_h2 else ''}
            footer = {'remark':hdr[0].trans_remark if hdr[0].trans_remark else '','footer1':title.trans_footer1 if title.trans_footer1 else '','footer2':title.trans_footer2 if title.trans_footer2 else '',
            'footer3':title.trans_footer3 if title.trans_footer3 else '','footer4':title.trans_footer4 if title.trans_footer4 else ''}
        else:
            company_hdr = {'remark':'','logo':'','name':'','address':''}
            footer = {'footer1':'','footer2':'','footer3':'','footer4':''}
                 

        if not taud:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"sa_transacno Does not exist!!",'error': True} 
            raise serializers.ValidationError(result)    

        queryset = self.get_queryset()
        hdr_serializer = PoshaudSerializer(hdr, many=True)
        hdr_data = hdr_serializer.data
        for h in hdr_data:
            h['trans'] = hdr[0].sa_transacno_ref
            h['issued'] = fmspw.pw_userlogin
            dsplit = str(h['sa_date']).split("T")
            date = datetime.datetime.strptime(str(dsplit[0]), '%Y-%m-%d').strftime("%d-%b-%Y")

            esplit = str(h['sa_time']).split("T")
            # print(esplit,"esplit")
            Time = str(esplit[1]).split(":")

            time = Time[0]+":"+Time[1]
            # starttime = datetime.datetime.strptime(time, "%H:%M %p")

            #h['sa_date'] = date
            #h['sa_time'] = time
           

            h['sa_date'] = date
            # now = timezone.now()
            h['sa_time'] = time

        dtl_serializer = PosdaudSerializer(daud, many=True)
        dtl_data = dtl_serializer.data
        tot_qty = 0;tot_trans = 0 ; tot_depo = 0; tot_bal = 0;balance = 0
        tot_amt = 0; tot_disc = 0
        for idx, d in enumerate(dtl_data, start=1):
            d_obj = PosDaud.objects.filter(pk=d['id'],ItemSite_Codeid__pk=site.pk).first()
            package_desc = []; packages = ""
            # print(d_obj.dt_combocode,"id")
            if d['record_detail_type'] == "PACKAGE":
                # package_dtl = PackageDtl.objects.filter(package_code=d['dt_combocode'],isactive=True)
                package_dtl = PackageDtl.objects.filter(package_code=d_obj.dt_combocode,isactive=True)
                for i in package_dtl:
                    desc = i.description
                    package_desc.append(desc)
                packages = tuple(package_desc)

            if d['isfoc'] == True:
                # d['dt_itemdesc'] = d['dt_itemdesc']
                d['dt_itemdesc'] = d['dt_itemdesc']+"-"+str(packages)    
            elif d['dt_status'] == 'SA' and d['record_detail_type'] == "PACKAGE":
                d['dt_itemdesc'] = d['dt_itemdesc']+"-"+str(packages)    
            elif d['dt_status'] == 'SA' and d['record_detail_type'] == "TD":
                d['dt_transacamt'] = ""
                d['dt_deposit'] = ""
                balance = ""
                d['balance'] = ""
                d['dt_itemdesc'] = d['record_detail_type'] +"-"+ d['dt_itemdesc']
            elif d['dt_status'] == 'SA' and d['record_detail_type'] in ['TP SERVICE','TP PRODUCT','TP PREPAID']:
                d['dt_itemdesc'] = d['record_detail_type'] +"-"+ d['dt_itemdesc']
            elif d['dt_status'] == 'VT':
                d['dt_itemdesc'] = d['dt_itemdesc']    
            elif d['dt_status'] == 'VT' and d['record_detail_type'] == "TD":
                d['dt_itemdesc'] = d['dt_itemdesc']
            elif d['dt_status'] == 'VT' and d['record_detail_type'] in ['TP SERVICE','TP PRODUCT','TP PREPAID']:
                d['dt_itemdesc'] = d['dt_itemdesc']
            elif d['holditemqty'] is not None and d['record_detail_type'] == 'PRODUCT':  
                d['dt_itemdesc'] = d['record_detail_type'] +"-"+ d['dt_itemdesc']+"(H"+str(d['holditemqty'])+")"                    
            else:    
                d['dt_itemdesc'] = d['record_detail_type'] +"-"+ d['dt_itemdesc']

            if d['dt_status'] == 'SA' and d['record_detail_type'] == "TD":
                d['dt_transacamt'] = ""
                d['dt_deposit'] = ""
                balance = ""
                d['balance'] = ""
                d['amount'] =  ""
                d['disc_amt'] = ""
            elif d['isfoc'] == True:
                d['amount'] = "0.00"
                d['disc_amt'] = "0.00"
                d['dt_transacamt'] = "0.00"
            else:    
                d['amount'] =  "{:.2f}".format(float(d_obj.dt_price * d_obj.dt_qty))
                tot_amt += float(d_obj.dt_price * d_obj.dt_qty)
                disc_value = (d_obj.dt_price * d_obj.dt_qty) - d_obj.dt_amt
                d['disc_amt'] = "{:.2f}".format(float(disc_value))
                d['dt_transacamt'] = "{:.2f}".format(float(d_obj.dt_amt))
                d['dt_deposit'] = "{:.2f}".format(float(d['dt_deposit']))
                balance = float(d_obj.dt_amt) - float(d['dt_deposit'])
                d['balance'] = "{:.2f}".format(float(balance))
                tot_trans += float(d_obj.dt_amt)
                tot_depo += float(d['dt_deposit'])
                tot_bal += float(balance)
                tot_disc += disc_value

            if d['record_detail_type'] == "TD":
                d['staffs'] = "/"+ d["trmt_done_staff_name"]
            else:
                d['staffs'] = d['staffs']    

            tot_qty += int(d['dt_qty'])
            # app_obj = Appointment.objects.filter(pk=d['Appointment']).first()
            d['no'] = idx
            d['dt_qty'] = d['dt_qty']
            # d['dt_price'] = "{:.2f}".format(float(d['dt_price']))
            # d['dt_discamt'] = "{:.2f}".format(float(d['dt_discamt']))
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

            # d_obj.staffs = sales +" "+"/"+" "+ service
            # d_obj.save()
    
            

        # value = receipt_calculation(self, request, daud)
        # sub_data = {'subtotal': "{:.2f}".format(float(value['subtotal'])),'total_disc':"{:.2f}".format(float(value['discount'])),
        #         'trans_amt':"{:.2f}".format(float(value['trans_amt'])),'deposit_amt':"{:.2f}".format(float(value['deposit_amt'])),
        #         'tax_amt':"{:.2f}".format(float(value['tax_amt'])),'tax_lable': value['tax_lable'],
        #         'billing_amount':"{:.2f}".format(float(value['billable_amount']))}
        # sub_data = {'tot_qty':str(tot_qty),'tot_net':str("{:.2f}".format((tot_trans))),
        # 'tot_paid':str("{:.2f}".format((tot_depo))),'tot_bal':str("{:.2f}".format((tot_bal))),
        # 'sub_total':str("{:.2f}".format((tot_depo)))}
        sub_data = {'tot_qty':str(tot_qty),'tot_net':str("{:.2f}".format((tot_trans))),
        'tot_paid':str("{:.2f}".format((tot_depo))),'tot_bal':str("{:.2f}".format((tot_bal))),
        'sub_total':str("{:.2f}".format((tot_depo))),'tot_amt': str("{:.2f}".format((tot_amt))),
        'tot_disc': str("{:.2f}".format((tot_disc)))}

        taud_serializer = PostaudprintSerializer(taud, many=True)
        taud_data = taud_serializer.data
        tot_payamt = 0.0
        tot_gst = 0.0
        for ta in taud_data:
            pay_amt = float(ta['pay_amt'])
            pay = str("{:.2f}".format((pay_amt)))
            ta['pay_amt'] = pay
            tot_payamt += pay_amt
            pay_gst = float(ta['pay_gst'])
            tot_gst += pay_gst
            # val = {'pay_mode': t['pay_type_name'],'pay_amt':pay}

        print(tot_gst,"tot_gst")

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
        label = False
        if calcgst > 0:
            if gst.is_exclusive == True:
                tax_amt = "{:.2f}".format(float(tot_depo * (calcgst / 100)))
            else:
                # tax_amt = "0.00"    
                tax_amt = "{:.2f}".format(float(tot_depo * calcgst / (100+calcgst)))

            if gst.item_value:
                # label = "Inclusive"+" "+str(int(gst.item_value))+" "+"GST"
                label = str(int(calcgst))+"% "+"GST (Included)"

        print(request.data,"request_data")
        totaltax=0
        linetax=0
        if request.data is not None:
            for rgt in request.data:
                paytablegt = Paytable.objects.filter(pk=rgt['pay_typeid'],pay_isactive=True).first()
                stringgt = paytablegt.gt_group
                st_newgt= "".join(stringgt.split())
                linetax=0
                if st_newgt == 'GT1': 
                    if calcgst > 0:
                        if gst.is_exclusive == True:
                            linetax = rgt['pay_amt'] * (calcgst / 100)
                        else:
                            linetax = rgt['pay_amt'] * calcgst / (100+calcgst)
                totaltax+=linetax

        print(totaltax,"totaltax")
        if totaltax>0:
            tax_amt = totaltax

        tax_amt = tot_gst
        if hdr:
            if hdr[0].sa_round:
                rounding = str("{:.2f}".format(float(hdr[0].sa_round)))
            else:
                rounding = "0.00"

        taud_sub = {'gst_label':label if label else '','gst':tax_amt,'total':str("{:.2f}".format((tot_payamt))),
        'rounding':rounding,'grand_tot':str("{:.2f}".format((tot_payamt)))}   

        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
       
        result = {'status': state,"message":message,'error': error,'company_hdr':company_hdr, 
        'hdr_data': hdr_data[0],'dtl_data':dtl_data,'sub_data':sub_data,
        'taud_data':taud_data,'taud_sub':taud_sub,'footer':footer}
        return Response(data=result, status=status.HTTP_200_OK)

class PayGroupViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PayGroup.objects.filter().order_by('seq')
    serializer_class = PayGroupSerializer

    def list(self, request):
        paygroup = Paytable.objects.filter(pay_isactive=True).only('pay_groupid_id').order_by('pay_groupid_id')
        message="error"
        if paygroup:
            group = list(set([p.pay_groupid_id for p in paygroup if p.pay_groupid_id]))
            # queryset = Paytable.objects.filter(pay_isactive=True,pay_groupid__pk__in=group).order_by('-pk')
            queryset = PayGroup.objects.filter(id__in=group).order_by('pk')
            # print(group,"group")
        else:
            queryset = self.filter_queryset(self.get_queryset())

        # queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":message,'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)           
    

class PaytableViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Paytable.objects.filter(pay_isactive=True).order_by('-pk')
    serializer_class = PaytableSerializer

    def list(self, request):
        paygroupid = self.request.GET.get('paygroupid',None)
        if paygroupid:
            print(paygroupid,"paygroupid")
            paygroup = PayGroup.objects.filter(id=paygroupid).order_by('pk')
        else:
            paygroup = PayGroup.objects.filter().order_by('pk')

        group = list(set([p.pk for p in paygroup if p.pk]))
        value = {}
        queryset = Paytable.objects.filter(pay_isactive=True,pay_groupid__pk__in=group).order_by('-pk')
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            for s in serializer.data:
                val = dict(s)
                if not val['pay_group_name'] in value:
                    value[val['pay_group_name']] = [val]
                else:
                    value[val['pay_group_name']].append(val)  
        
        if value != {}:        
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': value}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 5",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)          

class PaytableNewViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Paytable.objects.filter(pay_isactive=True).order_by('-pk')
    serializer_class = PaytableSerializer

    def list(self, request):
        paygroupid = self.request.GET.get('paygroupid',None)
        if paygroupid:
            # print(paygroupid,"paygroupid")
            paygroup = PayGroup.objects.filter(id=paygroupid).order_by('pk')
        else:
            paygroup = PayGroup.objects.filter().order_by('pk')

        group = list(set([p.pk for p in paygroup if p.pk]))
        value = []
        queryset = Paytable.objects.filter(pay_isactive=True,pay_groupid__pk__in=group).order_by('-pk')
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            for s in serializer.data:
                val = dict(s)
                # if not val['pay_group_name'] in value:
                #     value[val['pay_group_name']] = [val]
                # else:
                #    value[val['pay_group_name']].append(val)  
                value.append(val)
        
        if value != {}:        
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': value}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 5",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)          


class ItemStatusViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ItemStatus.objects.filter(itm_isactive=True).order_by('-pk')
    serializer_class = ItemStatusSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 6",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)           


class AppointmentCalender(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')
    serializer_class = AppointmentCalendarSerializer

    def get_queryset(self):
        dt = datetime.datetime
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            raise serializers.ValidationError(result)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            raise serializers.ValidationError(result)
        if not fmspw[0].LEVEL_ItmIDid.pk:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee has no security level",'error': True} 
            raise serializers.ValidationError(result)

        if fmspw[0].flgappt == False:
            queryset = Employee.objects.none()
            return queryset

        emp = fmspw[0].Emp_Codeid
        site = fmspw[0].loginsite   
      
        date = self.request.GET.get('date',None)
        date = parser.parse(date)

        check = self.request.GET.get('check',None)
        # customer = request.GET.get('customer_id',None)
        # search = request.GET.get('search',None)
        # print(search,type(search),"search")
        # format_d = ""
        # if search:
        #     if '-' in search:
        #         format_d = "date"
        #     elif ':' in search:
        #         format_d = "time"     
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select site in calendar view",'error': True} 
            raise serializers.ValidationError(result)  
        if not date:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select date in calendar view",'error': True} 
            raise serializers.ValidationError(result)
        # print(emp.show_in_appt,"emp.show_in_appt")

        if not check:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give parms for day/week/month",'error': True} 
            raise serializers.ValidationError(result)  

        if emp.show_in_appt == True:
            site_list = EmpSitelist.objects.filter(Emp_Codeid=emp,Site_Codeid__pk=site.pk,isactive=True)
            if site_list:
                month = None 
                if check == "day":
                    month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid=emp,
                    site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                elif check == "week":
                    startweek = date - timedelta(date.weekday())
                    endweek = startweek + timedelta(7)
                    month = ScheduleMonth.objects.filter(itm_date__range=[startweek,endweek],Emp_Codeid=emp,
                    site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                elif check == "month":
                    month = ScheduleMonth.objects.filter(itm_date__month=date.month,Emp_Codeid=emp,
                    site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()  

                if month:
                    emp_id = month.Emp_Codeid
                    queryset = Employee.objects.filter(pk=emp_id.pk,emp_isactive=True).order_by('emp_seq_webappt')
                    return queryset
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"There is no appointment available for this day",'error': True} 
                    raise serializers.ValidationError(result) 
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"You are not allowed to view this site record",'error': True} 
                raise serializers.ValidationError(result)  
        elif emp.show_in_appt == False:
            emp_list = []
            for e in EmpSitelist.objects.filter(Site_Codeid__pk=site.pk,isactive=True):
                emp = e.Emp_Codeid
                if e:
                    if emp.show_in_appt == True:
                        month = None

                        if check == "day":
                            month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid=emp,
                            site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                        elif check == "week":
                            startweek = date - timedelta(date.weekday())
                            endweek = startweek + timedelta(7)
                            month = ScheduleMonth.objects.filter(itm_date__range=[startweek,endweek],Emp_Codeid=emp,
                            site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                        elif check == "month":
                            month = ScheduleMonth.objects.filter(itm_date__month=date.month,Emp_Codeid=emp,
                            site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()

                        # if check in ("day","week","month"):
                        #     month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid=emp,
                        #     site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                        if month:
                            emp_id = month.Emp_Codeid
                            queryset = Employee.objects.filter(pk=emp_id.pk,emp_isactive=True).order_by('emp_seq_webappt')
                            if emp_id.pk not in emp_list:
                                emp_list.append(emp_id.pk)
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"You are not allowed to view this site record",'error': True} 
                    raise serializers.ValidationError(result)  

            if emp_list != []:
                queryset = Employee.objects.filter(pk__in=emp_list,emp_isactive=True)
                return queryset
            # else:
            #     result = {'status': status.HTTP_200_OK,"message":"No content 7",'error': False,'data':[]} 
            #     return Response(data=result, status=status.HTTP_200_OK)          


    def appointment_filter(self, request, emp_id):
        dt = datetime.datetime
        check = request.GET.get('check',None)
        date = request.GET.get('date',None)
        date = parser.parse(date)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)

        if fmspw[0].flgappt == False:
            queryset = Appointment.objects.none()
            return queryset

        if check == "day":
            queryset = Appointment.objects.filter(emp_noid__pk=emp_id,appt_date=date,appt_isactive=True).order_by('-pk')
            return queryset
        elif check == "week":
            startweek = date - timedelta(date.weekday())
            endweek = startweek + timedelta(7)
            queryset = Appointment.objects.filter(emp_noid__pk=emp_id,appt_date__range=[startweek,endweek],appt_isactive=True).order_by('-pk')
            return queryset
        elif check == "month":
            queryset = Appointment.objects.filter(emp_noid__pk=emp_id,appt_date__month=date.month,appt_isactive=True).order_by('-pk')
            return queryset    


    def list(self, request):
        date = request.GET.get('date',None)
        date = parser.parse(date) 
        emp_queryset = self.filter_queryset(self.get_queryset())
        if emp_queryset:
            serializer = StaffsAvailableSerializer(emp_queryset,many=True,  context={'request': self.request})
            empdata = serializer.data
        else:
            result = {'status': status.HTTP_200_OK,"message": "No Content 8",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        
        primary_lst = [
            ('Booking', '#f0b5ec'),
            ('Waiting', '#c928f3'),
            ('Confirmed', '#ebef8b'),
            ('Cancelled', '#ff531a'),
            ('Arrived', '#42e2c7'),
            ('Done', '#80c4f8'),
            ('LastMinCancel', '#e1920b'),
            ('Late',  '#66d9ff'),
            ('No Show', '#c56903'),
        ]

        lst = []
        for e in empdata:
            val = dict(e)
            emp_id = val['id']
            queryset = self.appointment_filter(request,emp_id)
            if queryset:
                serializer = AppointmentCalendarSerializer(queryset,many=True, context={'request': self.request})
                data = serializer.data
                for data in serializer.data:
                    appt = Appointment.objects.filter(pk=data['id'],appt_isactive=True).first()

                    master_ids = Treatment_Master.objects.filter(Appointment=data['id']).order_by('id').first()
                    # print(master_ids,master_ids.pk,"master_ids")
                    treat_ids = Treatment.objects.filter(sa_transacno=appt.sa_transacno,
                    treatment_parentcode=master_ids.treatment_parentcode,Item_Codeid=master_ids.Item_Codeid,
                    Site_Codeid=appt.ItemSite_Codeid,status="Open").order_by('pk').last()
                       
                    # print(master_ids,"master_ids")
                    if master_ids:
                        # print(treat_ids,"treat_ids")
                        if treat_ids != None:
                            treatment = treat_ids.course+" "+"["+str(treat_ids.times)+"]"
                            acc_ids = TreatmentAccount.objects.filter(ref_transacno=treat_ids.sa_transacno,
                            treatment_parentcode=treat_ids.treatment_parentcode,Site_Codeid=appt.ItemSite_Codeid,
                            type__in=('Deposit', 'Top Up')).order_by('id').last()
                            # print(acc_ids.id,acc_ids.balance,acc_ids.outstanding,"acc_ids")
                            data['balance_available'] = "{:.2f}".format(acc_ids.balance)
                            data['outstanding'] = "{:.2f}".format(acc_ids.outstanding)
                        else:
                            treatment = master_ids.course  
                            data['balance_available'] = 0.00
                            data['outstanding'] = 0.00
                            
                        data['treatment'] = treatment
                        for i in primary_lst:
                            if data['appt_status'] == i[0]:
                                new = {'start_date':data['start'],'end_date':data['end'],'text':data['treatment'],
                                'id':data['id'],'user_id':data['emp_noid'],'status': i[0] ,'color': i[1],'title': data['cust_name'],
                                'staff_name':data['emp_name'],'emp_pic':data['emp_img'] if data['emp_img'] else ""}
                                lst.append(new)

                        # print(data['treatment'],",",master_ids.Item_Codeid.id,",","stockname,,stockid")
                        # new = {'start_date':data['start'],'end_date':data['end'],'text':data['treatment'],
                        # 'id':data['id'],'user_id':data['emp_noid']}
                        # lst.append(new)

        if lst:  
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst}
            return Response(data=result, status=status.HTTP_200_OK)   
        else:
            result = {'status': status.HTTP_204_NO_CONTENT,"message": "No Content 9",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)

def calculate(born):
    today = date.today()
    extra_year = 1 if ((today.month, today.day) < (born.month, born.day)) else 0
    yr = (today.year - born.year) - extra_year
    return yr


class EmployeeAppointmentView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')
    # serializer_class = StaffsAvailableSerializer

    def get_serializer_class(self):
        if self.request.GET.get('type',None) == 'staff':
            return StaffsAvailableSerializer
        elif self.request.GET.get('type',None) == 'room':     
            return RoomAppointmentSerializer
        elif self.request.GET.get('type',None) == 'department': 
            return DeptAppointmentSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        # if fmspw[0].flgappt == False:
        #    queryset = Employee.objects.none()
        #    return queryset

        emp = fmspw[0].Emp_Codeid
        site = fmspw[0].loginsite   
      
        if self.request.GET.get('date',None) and not self.request.GET.get('date',None) is None:
            date = self.request.GET.get('date',None)
            date = parser.parse(date)
        else:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            date = parser.parse(date)
     
        if not date:
            raise Exception('Please Select date in calendar view')
        
        check = self.request.GET.get('check',None)
        if not check:
            raise Exception('Please give parms for day/week/month') 

        
        if fmspw[0].flgappt == True: 
            #Therapist
            #if emp.show_in_appt == True:
            if 1==3:
                site_list = EmpSitelist.objects.filter(Emp_Codeid=emp,Site_Codeid__pk=site.pk,isactive=True)
                if site_list:
                    month = False 
                    if check == "day":
                        month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid=emp,
                        site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                    elif check == "week":
                        startweek = date - timedelta(date.weekday())
                        endweek = startweek + timedelta(7)
                        month = ScheduleMonth.objects.filter(itm_date__range=[startweek,endweek],Emp_Codeid=emp,
                        site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                    elif check == "month":
                        month = ScheduleMonth.objects.filter(itm_date__month=date.month,Emp_Codeid=emp,
                        site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()  

                    print(month,"month1") 
                   
                    if month:
                        emp_id = month.Emp_Codeid
                        queryset = Employee.objects.filter(pk=emp_id.pk,emp_isactive=True,
                        show_in_appt=True).order_by('emp_seq_webappt')
                        # print(queryset,"queryset")
                        if queryset:
                            return queryset
                        else:
                            return None    
                    else:
                        raise Exception('Login User,There is no ScheduleMonth available for this day')     
                else:
                    raise Exception('Login User,EmpSitelist record does not exist')
            
            #manager -> Therapist,Consultant staffs as Resources
            elif emp.show_in_appt == False:
                #print("iff")
                emp_siteids = EmpSitelist.objects.filter(Site_Codeid__pk=site.pk,isactive=True)
                #print(emp_siteids,"emp_siteids")
                staffs = list(set([e.Emp_Codeid.pk for e in emp_siteids if e.Emp_Codeid and e.Emp_Codeid.emp_isactive == True]))
                emp_queryset = Employee.objects.filter(pk__in=staffs,emp_isactive=True,
                show_in_appt=True) 
                #print(staffs,"staffs")
                staffs_f = list(set([e.pk for e in emp_queryset if e.pk and e.emp_isactive == True]))
                #print(staffs_f,"staffs_f") 

                month = False

                if check == "day":
                    month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid__pk__in=staffs_f,
                    site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007'))
                elif check == "week":
                    startweek = date - timedelta(date.weekday())
                    endweek = startweek + timedelta(7)
                    month = ScheduleMonth.objects.filter(itm_date__range=[startweek,endweek],Emp_Codeid__pk__in=staffs_f,
                    site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007'))
                elif check == "month":
                    month = ScheduleMonth.objects.filter(itm_date__month=date.month,Emp_Codeid__pk__in=staffs_f,
                    site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007'))

                #print(month,"month2") 
                if month:
                    final = list(set([e.Emp_Codeid.pk for e in month if e.Emp_Codeid]))
                    queryset = Employee.objects.filter(pk__in=final,emp_isactive=True,
                    show_in_appt=True).order_by('emp_seq_webappt')
                    # print(queryset,"queryset emp")
                    if queryset:
                        return queryset
                    else:
                        return None   
                else:
                    raise Exception('Login User,There is no ScheduleMonth available for this day')   

                # emp_list = []
                # for e in EmpSitelist.objects.filter(Site_Codeid__pk=site.pk,isactive=True):
                #     # print(e.Emp_Codeid.emp_name,"emp_name")
                #     emp = e.Emp_Codeid
                #     if e:
                #         if emp.show_in_appt == True:
                #             month = None
                #             month = ScheduleMonth.objects.filter(itm_date=date,Emp_Codeid=emp,
                #             site_code=site.itemsite_code).filter(~Q(itm_Typeid__itm_code='100007')).first()
                #             # print(month,"month")

                #             if month:
                #                 emp_id = month.Emp_Codeid
                #                 queryset = Employee.objects.filter(pk=emp_id.pk,emp_isactive=True).order_by('emp_seq_webappt')
                #                 if emp_id.pk not in emp_list:
                #                     emp_list.append(emp_id.pk)
                #     # else:
                #     #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"You are not allowed to view this site record",'error': True} 
                #     #     return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                # # print(emp_list,"emp_list")
                # if emp_list != []:
                #     queryset = Employee.objects.filter(pk__in=emp_list,emp_isactive=True)
                #     # print(queryset,"queryset emp_list")
                #     return queryset
                # else:
                #     return None             

    
    def appointment_filter(self, request, emp_id):
        if self.request.GET.get('date',None) and not self.request.GET.get('date',None) is None:
            date = self.request.GET.get('date',None)
            date = parser.parse(date)
        else:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            date = parser.parse(date)

        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        check = request.GET.get('check',None)
   
        if fmspw[0].flgappt == False:
            queryset = Appointment.objects.none()
            return queryset

        if check == "day":
            queryset = Appointment.objects.filter(emp_noid__pk=emp_id,appt_date=date,appt_isactive=True,
            itemsite_code=site.itemsite_code).order_by('-pk')
        elif check == "week":
            startweek = date - timedelta(date.weekday())
            endweek = startweek + timedelta(7)
            queryset = Appointment.objects.filter(emp_noid__pk=emp_id,appt_date__range=[startweek,endweek],
            appt_isactive=True,itemsite_code=site.itemsite_code).order_by('-pk')
        elif check == "month":
            queryset = Appointment.objects.filter(emp_noid__pk=emp_id,appt_date__month=date.month,
            appt_isactive=True,itemsite_code=site.itemsite_code).order_by('-pk')
            
        # print(queryset,"appt")
        return queryset

    def appointmentroom_filter(self, request, room_id):
        if self.request.GET.get('date',None) and not self.request.GET.get('date',None) is None:
            date = self.request.GET.get('date',None)
            date = parser.parse(date)
        else:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            date = parser.parse(date)

        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        check = request.GET.get('check',None)
   
        if fmspw[0].flgappt == False:
            queryset = Appointment.objects.none()
            return queryset

        if check == "day":
            queryset = Appointment.objects.filter(Room_Codeid__pk=room_id,appt_date=date,appt_isactive=True,
            itemsite_code=site.itemsite_code).order_by('-pk')
        elif check == "week":
            startweek = date - timedelta(date.weekday())
            endweek = startweek + timedelta(7)
            queryset = Appointment.objects.filter(Room_Codeid__pk=room_id,appt_date__range=[startweek,endweek],
            appt_isactive=True,itemsite_code=site.itemsite_code).order_by('-pk')
        elif check == "month":
            queryset = Appointment.objects.filter(Room_Codeid__pk=room_id,appt_date__month=date.month,
            appt_date__year=date.year,appt_isactive=True,itemsite_code=site.itemsite_code).order_by('-pk')
            
        # print(queryset,"appt")
        return queryset


    def appointmentdept_filter(self, request, dept_code):
        # print(dept_code,"dept_code")
        if self.request.GET.get('date',None) and not self.request.GET.get('date',None) is None:
            date = self.request.GET.get('date',None)
            date = parser.parse(date)
        else:
            now = datetime.datetime.now()
            date = now.strftime("%Y-%m-%d")
            date = parser.parse(date)

        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        check = request.GET.get('check',None)
   
        if fmspw[0].flgappt == False:
            queryset = Appointment.objects.none()
            return queryset

        if check == "day":
            master = Treatment_Master.objects.filter(appt_time__date=date,Item_Codeid__item_dept=dept_code,
            site_code=site.itemsite_code).order_by('-pk')
            apptlst = [i.Appointment.pk for i in master if i.Appointment]
            queryset = Appointment.objects.filter(pk__in=apptlst,appt_date=date,appt_isactive=True,
            itemsite_code=site.itemsite_code).order_by('-pk')
        elif check == "week":
            startweek = date - timedelta(date.weekday())
            endweek = startweek + timedelta(7)
            master = Treatment_Master.objects.filter(appt_time__date__range=[startweek,endweek],Item_Codeid__item_dept=dept_code,
            site_code=site.itemsite_code).order_by('-pk')
            # print(master,"master")
            apptlst = [i.Appointment.pk for i in master if i.Appointment]
            queryset = Appointment.objects.filter(pk__in=apptlst,appt_date__range=[startweek,endweek],
            appt_isactive=True,itemsite_code=site.itemsite_code).order_by('-pk')
        elif check == "month":
            master = Treatment_Master.objects.filter(appt_time__month=date.month,
            appt_time__year=date.year,Item_Codeid__item_dept=dept_code,
            site_code=site.itemsite_code).order_by('-pk')
            # print(master,"master")
            apptlst = [i.Appointment.pk for i in master if i.Appointment]
            queryset = Appointment.objects.filter(pk__in=apptlst,appt_date__month=date.month,
            appt_date__year=date.year,appt_isactive=True,itemsite_code=site.itemsite_code).order_by('-pk')
            
        # print(queryset,"appt")
        return queryset
    
    def list(self, request): 
        # try:
            # now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite   
            empobj = Employee.objects.filter(emp_code=fmspw.emp_code,emp_isactive=True).first()
            if not empobj:
                raise Exception('Login Employee Does not exist')

            # now = datetime.datetime.now()
            # print(now,"now")
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            view_type = request.GET.get('type',None)

            if request.GET.get('date',None) and not request.GET.get('date',None) is None:
                date = request.GET.get('date',None)
                date = parser.parse(date)
            else:
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                date = parser.parse(date)

            q = self.request.GET.get('search',None)

            if view_type == "staff":
                appt_ids_lst = [];emp_ids_lst = []  
                if q and q is not None:
                    appt_searchids = Appointment.objects.filter(appt_date=date,appt_isactive=True,
                    itemsite_code=site.itemsite_code).filter(Q(cust_name__icontains=q) | Q(cust_no__icontains=q)).order_by('-pk')
                    appt_ids_lst = list(set([a.pk for a in appt_searchids if a.pk]))
                    emp_ids_lst = list(set([a.emp_noid.pk for a in appt_searchids if a.emp_noid.pk]))
            elif view_type == "room": 
                appt_ids_lst = [];room_ids_lst = []  
                if q and q is not None:
                    appt_searchids = Appointment.objects.filter(appt_date=date,appt_isactive=True,
                    itemsite_code=site.itemsite_code).filter(Q(cust_name__icontains=q) | Q(cust_no__icontains=q)).order_by('-pk')
                    appt_ids_lst = list(set([a.pk for a in appt_searchids if a.pk]))
                    room_ids_lst = list(set([a.Room_Codeid.pk for a in appt_searchids if a.Room_Codeid.pk]))
            elif view_type == "department":
                appt_ids_lst = [];dept_ids_lst = []  
                if q and q is not None:
                    appt_searchids = Appointment.objects.filter(appt_date=date,appt_isactive=True,
                    itemsite_code=site.itemsite_code).order_by('-pk')
                    appt_ids_lst = list(set([a.pk for a in appt_searchids if a.pk]))
                    treatmaster_ids = list(Treatment_Master.objects.filter(Appointment__pk__in=appt_ids_lst).values_list('Item_Codeid__item_dept', flat=True))
                    dep = list(set([int(i) for i in treatmaster_ids]))
                    deptid = ItemDept.objects.filter(itm_code__in=dep)
                    dept_ids_lst = list(set([a.pk for a in deptid if a.pk]))

            
            primary_lst = {
                "Booking": {"color":"#f0b5ec","border_color":"#ec40e1"},
                "Waiting": {"color":"#c928f3","border_color":"#49035a"},
                "Confirmed": {"color":"#ebef8b","border_color":"#9ba006"},
                "Cancelled": {"color":"#ff531a","border_color":"#7a2306"},
                "Arrived": {"color":"#42e2c7","border_color":"#076858"},
                "Done": {"color":"#80c4f8","border_color":"#05508a"},
                "LastMinCancel": {"color":"#e1920b","border_color":"#724903"},
                "Late": {"color":"#66d9ff","border_color":"#097396"},
                "No Show": {"color":"#c56903","border_color":"#6e3e06"},
                "Block": {"color":"#b2b2b2","border_color":"#000000"}
                }
            
            if view_type == "staff":
                if self.filter_queryset(self.get_queryset()):
                    if emp_ids_lst != []:
                        queryset = self.filter_queryset(self.get_queryset()).filter(pk__in=emp_ids_lst
                        ).exclude(emp_seq_webappt=None).order_by('emp_seq_webappt')
                    else:
                        queryset = self.filter_queryset(self.get_queryset()).exclude(emp_seq_webappt=None
                        ).order_by('emp_seq_webappt')
                else:
                    queryset = False
            elif view_type == "room": 
                if room_ids_lst != []:
                    queryset = Room.objects.filter(isactive=True,site_code=site.itemsite_code,pk__in=room_ids_lst).order_by('pk')
                else:
                    queryset = Room.objects.filter(isactive=True,site_code=site.itemsite_code).order_by('pk')

            elif view_type == "department":
                if dept_ids_lst != []:
                    queryset = ItemDept.objects.filter(is_service=True,itm_status=True,itm_showonsales=True,pk__in=dept_ids_lst).order_by('pk')
                else:
                    queryset = ItemDept.objects.filter(is_service=True,itm_status=True,itm_showonsales=True).order_by('pk')

            # print(emp_queryset,"emp_queryset 111111")
            final = [];event = []
            # print(emp_queryset,"emp_queryset")

            if queryset:
                if view_type == "staff":
                    serializer_class = StaffsAvailableSerializer
                elif view_type == "room": 
                    serializer_class = RoomAppointmentSerializer
                elif view_type == "department": 
                    serializer_class = DeptAppointmentSerializer

                total = len(queryset)
                state = status.HTTP_200_OK
                message = "Listed Succesfully"
                error = False
                data = None
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
                # print(result,"result")
                v = result.get('data')
                # print(v,"v")
                d = v.get('dataList')
                # print(d,"d 6666666666")
                for e in d:
                    val = dict(e)
                    # emp_id = val['id']
                    # queryset = self.appointment_filter(request,emp_id)

                    if view_type == "staff":
                        emp_id = val['id']
                        newqueryset = self.appointment_filter(request,emp_id)
                    elif view_type == "room":  
                        room_id = val['id']
                        newqueryset = self.appointmentroom_filter(request,room_id)
                    elif view_type == "department":
                        dept_obj = ItemDept.objects.filter(pk=val['id']).first()
                        dept_code = dept_obj.itm_code
                        newqueryset = self.appointmentdept_filter(request,dept_code)

                    if newqueryset:
                        serializer = AppointmentCalendarSerializer(newqueryset,many=True, context={'request': self.request})
                        data = serializer.data
                        for data in serializer.data:
                            basic = True;req_therapist = False; balance = False;birthday = False;outstanding = False;remark=False;walkin=False
                            remark_val = ""
                            appt_ids = Appointment.objects.filter(pk=data['id']).first()
                            master_ids = Treatment_Master.objects.filter(Appointment=data['id']).order_by('id').first()
                            if master_ids:
                                treatment = master_ids.course  
                                duration = master_ids.add_duration
                                appt_date = datetime.datetime.strptime(str(data['appt_date']), "%Y-%m-%d").strftime("%Y-%m-%d")
                                apptdate = datetime.datetime.strptime(str(data['appt_date']), "%Y-%m-%d").strftime("%d/%m/%Y")
                                starttime = datetime.datetime.strptime(str(data['appt_fr_time']), "%H:%M:%S").strftime("%H:%M:%S")
                                endtime = datetime.datetime.strptime(str(data['appt_to_time']), "%H:%M:%S").strftime("%H:%M:%S")
                                startDate =  str(appt_date)+"T"+str(starttime)
                                endDate =  str(appt_date)+"T"+str(endtime)

                                # treat_ids = Treatment.objects.filter(sa_transacno=appt_ids.sa_transacno,
                                # treatment_parentcode=appt_ids.treatmentcode,Item_Codeid=master_ids.Item_Codeid,
                                # site_code=site.itemsite_code,status="Open",cust_code=appt_ids.cust_no).order_by('pk')

                                treat_ids = Treatment.objects.filter(site_code=site.itemsite_code,
                                status="Open",cust_code=appt_ids.cust_no).order_by('pk')
                            
                                if treat_ids:
                                    balance = True
                                    
                                # custobj = Customer.objects.filter(cust_code=appt_ids.cust_no,cust_isactive=True,
                                # site_code=site.itemsite_code).first() 
                                custobj = Customer.objects.filter(cust_code=appt_ids.cust_no,cust_isactive=True).first() 
                                if custobj:
                                    
                                    #if custobj.cust_dob:
                                    #    dob = datetime.datetime.strptime(str(custobj.cust_dob), '%Y-%m-%d')
                                    #    age = calculate(dob)
                                    # print(age,"age")

                                    gender = ""
                                    if custobj.cust_sexes:
                                        gendr = Gender.objects.filter(itm_code=custobj.cust_sexes).first()
                                        if gendr.itm_code == "1":
                                            gender = "M"
                                        elif gendr.itm_code == "2":
                                            gender = "F" 

                                    if custobj.cust_dob:
                                        custdob = datetime.datetime.strptime(str(custobj.cust_dob), "%Y-%m-%d")
                                        if custdob.month == date.month:
                                            birthday = True
                                        dob = datetime.datetime.strptime(str(custobj.cust_dob), '%Y-%m-%d')
                                        age = calculate(dob)

                                    #tre_accids = TreatmentAccount.objects.filter(cust_code=custobj.cust_code, 
                                    #site_code=site.itemsite_code, outstanding__gt = 0).order_by('pk')
                                    tre_accids = TreatmentAccount.objects.filter(cust_code=custobj.cust_code, 
                                    outstanding__gt = 0).order_by('pk')
                                    if tre_accids:
                                        outstanding = True

                                    deposit_accids = DepositAccount.objects.filter(cust_code=custobj.cust_code, 
                                    outstanding__gt=0).order_by('pk')
                                    if deposit_accids:
                                        outstanding = True

                                    pre_acc_ids = PrepaidAccount.objects.filter(cust_code=custobj.cust_code,
                                    outstanding__gt=0).order_by('pk')
                                    if pre_acc_ids:
                                        outstanding = True
                                    

                                if appt_ids.new_remark:
                                    remark = True
                                    remark_val = "["+str(data['new_remark'])+" - "+"Remark By: "+str(appt_ids.appt_created_by)+" - "+str(apptdate)+"]"
                                
                                if appt_ids.requesttherapist == True:
                                    req_therapist = True

                                if appt_ids.walkin == True:
                                    walkin = True     
                                
                                if data['appt_status'] in primary_lst:
                                    statusval = primary_lst[data['appt_status']]
                                    
                                    appt_val = {'id':e['id'],'text':treatment,'startDate': startDate, 
                                    'endDate':endDate,'cust_name':data['cust_name'] if data['cust_name'] else "",
                                    'cust_phone': custobj.cust_phone2 if custobj.cust_phone2 else "",
                                    'cust_refer':data['cust_refer'] if data['cust_refer'] else "",
                                    'status': data['appt_status'],'color': statusval['color'],
                                    'border_color': statusval['border_color'],'inital':basic,'req_therapist':req_therapist,
                                    'balance':balance,'birthday':birthday,'outstanding':outstanding,'remark':remark,
                                    'walkin':walkin,'remark_val':remark_val,'appt_id':appt_ids.pk,
                                    'staff':appt_ids.emp_noid.display_name,'appt_remark':appt_ids.appt_remark if appt_ids.appt_remark else "",
                                    'reason':appt_ids.appt_remark if appt_ids.appt_remark else "",
                                    'cust_code' : custobj.cust_code,'gender' : gender,'cust_phone1' :custobj.cust_phone1 if custobj.cust_phone1 else "",
                                    'permanent_remark' : custobj.cust_remark if custobj.cust_remark else "",
                                    'age' : age,'room':appt_ids.Room_Codeid.displayname if appt_ids.Room_Codeid and appt_ids.Room_Codeid.displayname else "",
                                    'cust_id' : custobj.pk
                                    }

                                    if appt_ids_lst != []:
                                        if appt_ids.pk in appt_ids_lst:
                                            event.append(appt_val)
                                    else:
                                        event.append(appt_val)

                   
                    if view_type == "staff": 
                        emp_val = {'text': e['display_name'],'emp_pic':e['emp_img'] if e['emp_img'] else "",
                        'staff_name':e['display_name'],'id':e['id']}
                        if emp_ids_lst != []:
                            if e['id'] in emp_ids_lst:
                                final.append(emp_val)
                        else:
                            final.append(emp_val)
                    elif view_type == "room":  
                        room_val = {'text': e['displayname'],'emp_pic':e['room_img'] if e['room_img'] else "",
                        'staff_name':e['displayname'],'id':e['id']}
                        if room_ids_lst != []:
                            if e['id'] in room_ids_lst:
                                final.append(room_val)
                        else:
                            final.append(room_val)   

                    elif view_type == "department":
                        dept_val = {'text': e['itm_desc'],'emp_pic':e['dept_img'] if e['dept_img'] else "",
                        'staff_name':e['itm_desc'],'id':e['id']}
                        if dept_ids_lst != []:
                            if e['id'] in dept_ids_lst:
                                final.append(dept_val)
                        else:
                            final.append(dept_val) 

                
                if final != []:  
                    v['dataList'] =  final 
                    # print(final,"final") 
                    result['event'] = event
                    # now1 = timezone.now()
                    # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
                    # total = now1.second - now.second
                    # print(total,"total")
                    return Response(result, status=status.HTTP_200_OK) 
                    # result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': final,
                    # 'event':event}
                    # return Response(data=result, status=status.HTTP_200_OK)   
                else:
                    result = {'status': status.HTTP_204_NO_CONTENT,"message": "No Content",'error': False, 'data': [],'event':[]}
                    return Response(data=result, status=status.HTTP_200_OK)    
            else:
                result = {'status': status.HTTP_200_OK,"message": "No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
                
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)        
      

class SecuritiesAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Securities.objects.filter(level_isactive=True).order_by('-pk')
    serializer_class = SecuritiesSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 10",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 

# class CustList(generics.ListAPIView):
#     authentication_classes = []
#     permission_classes = []
#     queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')
#     serializer_class = CustApptSerializer
#     search_fields = ['cust_name','cust_phone2','cust_email','cust_code','cust_nric']
#     filter_backends = (filters.SearchFilter,)

#     def get_queryset(self):
#         cust = Customer.objects.filter(cust_isactive=True,Site_Codeid=self.request.GET.get('Outlet',None)).order_by('-pk')
#         print(cust,"cust")
#         return cust
        

class CustApptAPI(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')
    serializer_class = CustApptSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        branch = ItemSitelist.objects.filter(pk=site.pk,itemsite_isactive=True).first()
        if not branch:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Outlet Id does not exist!!",'error': True} 
            raise serializers.ValidationError(result)

        q = self.request.GET.get('search',None)
        if q:
            queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')
            queryset = queryset.filter(Q(cust_name__icontains=q) | 
            Q(cust_email__icontains=q) | Q(cust_code__icontains=q) | Q(cust_phone2__icontains=q) | Q(cust_phone1__icontains=q) |
            Q(cust_nric__icontains=q)  | Q(cust_refer__icontains=q) )[:20]
        else:
            queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')[:20]
    
        return queryset
                        
    def list(self, request, *args, **kwargs):
        serializer_class = CustApptSerializer
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 11",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
       
class ApptTypeAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ApptType.objects.filter(appt_type_isactive=True).order_by('-pk')
    serializer_class = ApptTypeSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 12",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 



class TmpItemHelperViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = TmpItemHelper.objects.filter().order_by('-id')
    serializer_class = TmpItemHelperSerializer

    # @authenticated_only
    def list(self, request):
        if request.GET.get('cartid',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Cart Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).first().type in ['Top Up','Sales']:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
        cart_obj = ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).exclude(type__in=('Top Up','Sales')).first()
        if not cart_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if int(cart_obj.itemcodeid.item_div) in [1,2,4,5,6]:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Done Not allowed for this product!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if cart_obj.itemcodeid.item_type == 'PACKAGE':
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Done Not allowed for this Package product!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if int(cart_obj.itemcodeid.item_div) == 3 and str(cart_obj.itemcodeid.item_type) == "COURSE":
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Done Not allowed for Package Product!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
        if cart_obj.deposit < cart_obj.discount_price:
            msg = "Min Deposit for this treatment is SS {0} ! Treatment Done not allow.".format(str(cart_obj.discount_price))
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if cart_obj.itemcodeid.workcommpoints == None or cart_obj.itemcodeid.workcommpoints == 0.0:
            workcommpoints = 0.0
            # result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Work Point should not be None/zero value!!",'error': True} 
            # return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        else:
            workcommpoints = cart_obj.itemcodeid.workcommpoints

        stock_obj = Stock.objects.filter(pk=cart_obj.itemcodeid.pk,item_isactive=True).first()
        if stock_obj.srv_duration is None or stock_obj.srv_duration == 0.0:
            srvduration = 60
        else:
            srvduration = stock_obj.srv_duration

        stkduration = int(srvduration) + 30
        hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))

                   
        h_obj = TmpItemHelper.objects.filter(itemcart=cart_obj).first()
        value = {'Item':cart_obj.itemdesc,'Price':"{:.2f}".format(float(cart_obj.trans_amt)),
        'work_point':"{:.2f}".format(float(workcommpoints)),'Room':None,'Source':None,'new_remark':None,
        'times': cart_obj.quantity if cart_obj.quantity else "",'add_duration':hrs}
        if h_obj:
            if not h_obj.Room_Codeid is None:
                value['Room']  = h_obj.Room_Codeid.displayname
            if not h_obj.Source_Codeid is None:
                value['Source']  = h_obj.Source_Codeid.source_desc
            if not h_obj.new_remark is None:
                value['new_remark']  = h_obj.new_remark
            if h_obj.times:
                value['times']  = cart_obj.quantity if cart_obj.quantity else ""   
            # if h_obj.workcommpoints:
            #    sumwp1 = TmpItemHelper.objects.filter(itemcart=cart_obj.pk).aggregate(Sum('wp1'))
            #    value['work_point'] = "{:.2f}".format(float(sumwp1['wp1__sum']))       
   
        queryset = TmpItemHelper.objects.filter(itemcart=cart_obj).order_by('id')
        serializer = self.get_serializer(queryset, many=True)
        final = []
        if queryset:
            for t in serializer.data:
                s = dict(t)
                s['wp1'] = "{:.2f}".format(float(s['wp1']))
                s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
                s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
                s['add_duration'] =  get_in_val(self, s['add_duration'])
                final.append(s)
        # else:
        #     val = {'id':None,'helper_id':None,'helper_name':None,'wp1':None,'appt_fr_time':None,
        #     'appt_to_time':None,'add_duration':None}  
        #     final.append(val)
      
        result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
        'value': value,'data':  final}
        return Response(data=result, status=status.HTTP_200_OK)  

    def create(self, request):
        
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        if request.GET.get('cartid',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Cart Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).first().type in ['Top Up','Sales']:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
      
        cart_obj = ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).exclude(type__in=('Top Up','Sales')).first()
        if not cart_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if int(cart_obj.itemcodeid.item_div) in [1,2,4,5,6]:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Done Not allowed for this product!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if cart_obj.itemcodeid.item_type == 'PACKAGE':
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Done Not allowed for this Package product!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if int(cart_obj.itemcodeid.item_div) == 3 and str(cart_obj.itemcodeid.item_type) == "COURSE":
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Done Not allowed for Package Product!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
        if request.GET.get('times',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Session must not be empty!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        if request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
            workcommpoints = 0.0
        else:
            workcommpoints = request.GET.get('workcommpoints',None)  

        h_obj = TmpItemHelper.objects.filter(itemcart=cart_obj).order_by('pk')
        if h_obj:
            if int(request.GET.get('times',None)) != int(h_obj[0].times):
                msg = '''Already {0} Session is mapped for Treatment Done,Can Do Only one session Treatment Done in cart.Delete Old Session & Try!!'''.format(h_obj[0].times)
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        tmp = []

        count = 1;Source_Codeid=None;Room_Codeid=None;new_remark=None;appt_fr_time=None;appt_to_time=None;add_duration=None
        if cart_obj.itemcodeid.srv_duration is None or float(cart_obj.itemcodeid.srv_duration) == 0.0:
            stk_duration = 60
        else:
            stk_duration = int(cart_obj.itemcodeid.srv_duration)

        stkduration = int(stk_duration) + 30
        hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
        duration = hrs
        add_duration = duration

        if h_obj:
            count = int(h_obj.count()) + 1
            Source_Codeid = h_obj[0].Source_Codeid
            Room_Codeid = h_obj[0].Room_Codeid
            new_remark = h_obj[0].new_remark
            last = h_obj.last()
            
            start_time =  get_in_val(self, last.appt_to_time); endtime = None
            if start_time:
                starttime = datetime.datetime.strptime(str(start_time), "%H:%M")

                end_time = starttime + datetime.timedelta(minutes = stkduration)
                endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
            appt_fr_time = starttime if start_time else None
            appt_to_time = endtime if endtime else None

        # wp1 = float(workcommpoints) / float(count)
        wp1 = float(workcommpoints)
        wp11 = wp1
        wp12 = 0
        wp13 = 0
        wp14 = 0
        if float(workcommpoints) > 0 :
            wp11 = wp1 / float(count)
            if count == 2:
                wp12 = wp1 / float(count)
            if count == 3:
                wp12 = wp1 / float(count)
                wp13 = wp1 / float(count)
            if count == 4:
                wp12 = wp1 / float(count)
                wp13 = wp1 / float(count)
                wp14 = wp1 / float(count)

            if count == 2 and wp1 == 3:
                wp11 = 2
                wp12 = 1
            if count == 2 and wp1 == 5:
                wp11 = 3
                wp12 = 2
            if count == 2 and wp1 == 7:
                wp11 = 4
                wp12 = 3
            if count == 2 and wp1 == 9:
                wp11 = 5
                wp12 = 4
            if count == 2 and wp1 == 11:
                wp11 = 6
                wp12 = 5

            if count == 3 and wp1 == 2:
                wp11 = 1
                wp12 = 1
                wp13 = 0
            if count == 3 and wp1 == 4:
                wp11 = 2
                wp12 = 1
                wp13 = 1
            if count == 3 and wp1 == 5:
                wp11 = 2
                wp12 = 2
                wp13 = 1
            if count == 3 and wp1 == 7:
                wp11 = 3
                wp12 = 2
                wp13 = 2
            if count == 3 and wp1 == 8:
                wp11 = 3
                wp12 = 3
                wp13 = 2
            if count == 3 and wp1 == 10:
                wp11 = 4
                wp12 = 3
                wp13 = 3
            if count == 3 and wp1 == 11:
                wp11 = 4
                wp12 = 4
                wp13 = 3

        string = ""
        if cart_obj.done_sessions == None:
            string = request.GET.get('times',None).zfill(2)
        elif not cart_obj.done_sessions == None:
            string = cart_obj.done_sessions+","+ request.GET.get('times',None).zfill(2)
        
        ItemCart.objects.filter(id=cart_obj.id).update(done_sessions=string)  
       
        helper_obj = Employee.objects.filter(emp_isactive=True,pk=request.data['helper_id']).first()
        if not helper_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        alemp_ids = TmpItemHelper.objects.filter(itemcart__pk=cart_obj.pk,helper_code=helper_obj.emp_code).order_by('pk')
        if alemp_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Employee already selected!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        # print(request.data,"request.data")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # helper_name=helper_obj.emp_name,helper_code=helper_obj.emp_code,Room_Codeid=Room_Codeid,
            temph = serializer.save(item_name=cart_obj.itemcodeid.item_desc,helper_id=helper_obj,
            helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,Room_Codeid=Room_Codeid,
            site_code=site.itemsite_code,times=request.GET.get('times',None).zfill(2),
            treatment_no=cart_obj.quantity,wp1=0.0,wp2=0.0,wp3=0.0,itemcart=cart_obj,Source_Codeid=Source_Codeid,
            new_remark=new_remark,appt_fr_time=appt_fr_time,appt_to_time=appt_to_time,add_duration=add_duration,
            workcommpoints=workcommpoints)
            # cart_obj.service_staff.add(helper_obj.pk) 
            # cart_obj.helper_ids.add(temph.id) 
            tmp.append(temph.id)

            runx = 1
            for h in TmpItemHelper.objects.filter(itemcart=cart_obj).order_by('pk'):
                # TmpItemHelper.objects.filter(id=h.id).update(wp1=wp1)  
                if runx == 1:
                   TmpItemHelper.objects.filter(id=h.id).update(wp1=wp11)
                if runx == 2:
                   TmpItemHelper.objects.filter(id=h.id).update(wp1=wp12)
                if runx == 3:
                   TmpItemHelper.objects.filter(id=h.id).update(wp1=wp13)
                if runx == 4:
                   TmpItemHelper.objects.filter(id=h.id).update(wp1=wp14)
                runx = float(runx) + 1

        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 
            'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
        if tmp != []:
            value = {'Item':cart_obj.itemcodeid.item_desc,'Price':"{:.2f}".format(float(cart_obj.trans_amt)),
            'work_point':"{:.2f}".format(float(workcommpoints)),'Room':None,
            'Source':None,'new_remark':None,'times':request.GET.get('times',None).zfill(2)}  
            tmp_h = TmpItemHelper.objects.filter(id__in=tmp)
            serializer_final = self.get_serializer(tmp_h, many=True)
            final = []
            for t in serializer_final.data:
                s = dict(t)
                s['wp1'] = "{:.2f}".format(float(s['wp1']))
                s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
                s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
                s['add_duration'] =  get_in_val(self, s['add_duration'])
                final.append(s)

            result = {'status': status.HTTP_201_CREATED,"message": "Created Succesfully",'error': False, 
            'value':value,'data':  final}
            return Response(result, status=status.HTTP_201_CREATED)

        result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Invalid Input",'error': False, 
        'data':  serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    def get_object(self, pk):
        #try:
            return TmpItemHelper.objects.get(pk=pk)
        #except TmpItemHelper.DoesNotExist:
        #    raise Http404

    def retrieve(self, request, pk=None):
        queryset = TmpItemHelper.objects.filter().order_by('pk')
        tmpitm = get_object_or_404(queryset, pk=pk)
        serializer = TmpItemHelperSerializer(tmpitm)
        result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
        'data':  serializer.data}
        return Response(data=result, status=status.HTTP_200_OK)  
    

    def partial_update(self, request, pk=None):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        if request.GET.get('Room_Codeid',None) == "null":
            room_ids = None
        else:
            room_ids = Room.objects.filter(id=request.GET.get('Room_Codeid',None),isactive=True).first()
            if not room_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('Source_Codeid',None)  == "null":
            source_ids = None 
        else:            
            source_ids = Source.objects.filter(id=request.GET.get('Source_Codeid',None),source_isactive=True).first()
            if not source_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Source ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        # if request.GET.get('Room_Codeid',None) is None or request.GET.get('Room_Codeid',None) == "null":
        if not request.GET.get('Room_Codeid',None):
            room_ids = None

        # if request.GET.get('Source_Codeid',None) is None or request.GET.get('Source_Codeid',None) == "null":
        if not request.GET.get('Source_Codeid',None):     
            source_ids = None 

        if request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
            workcommpoints = 0.0
        else:
            workcommpoints = request.GET.get('workcommpoints',None)  

        tmpobj = self.get_object(pk)
        if tmpobj.itemcart:
            if ItemCart.objects.filter(isactive=True,id=tmpobj.itemcart.pk).first().type in ['Top Up','Sales']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
        appt = Appointment.objects.filter(cust_noid=tmpobj.itemcart.cust_noid,appt_date=date.today(),
        ItemSite_Codeid=site)    
        if not appt:
            if (not 'appt_fr_time' in request.data or str(request.data['appt_fr_time']) is None) and (not 'add_duration' in request.data or str(request.data['add_duration']) is None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment is not available today so please give appointment details",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        

        serializer = self.get_serializer(tmpobj, data=request.data, partial=True)
        if serializer.is_valid():
            if ('appt_fr_time' in request.data and not request.data['appt_fr_time'] == None):
                if ('add_duration' in request.data and not request.data['add_duration'] == None):
                    if tmpobj.itemcart.itemcodeid.srv_duration is None or float(tmpobj.itemcart.itemcodeid.srv_duration) == 0.0:
                        stk_duration = 60
                    else:
                        stk_duration = int(tmpobj.itemcart.itemcodeid.srv_duration)

                    stkduration = int(stk_duration) + 30
                    t1 = datetime.datetime.strptime(str(request.data['add_duration']), '%H:%M')
                    t2 = datetime.datetime(1900,1,1)
                    addduration = (t1-t2).total_seconds() / 60.0

                    hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                    start_time =  get_in_val(self, request.data['appt_fr_time'])
                    starttime = datetime.datetime.strptime(start_time, "%H:%M")

                    end_time = starttime + datetime.timedelta(minutes = addduration)
                    endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                    duration = hrs
                    serializer.save(appt_fr_time=starttime,appt_to_time=endtime,add_duration=request.data['add_duration'],
                    Room_Codeid=room_ids,Source_Codeid=source_ids,new_remark=request.GET.get('new_remark',None))

                    next_recs = TmpItemHelper.objects.filter(id__gte=tmpobj.pk).order_by('pk')
                    for t in next_recs:
                        start_time =  get_in_val(self, t.appt_to_time)
                        if start_time:
                            starttime = datetime.datetime.strptime(start_time, "%H:%M")
                            end_time = starttime + datetime.timedelta(minutes = stkduration)
                            endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                            idobj = TmpItemHelper.objects.filter(id__gt=t.pk).order_by('pk').first()
                            if idobj:
                                TmpItemHelper.objects.filter(id=idobj.pk).update(appt_fr_time=starttime,
                                appt_to_time=endtime,add_duration=duration)

            if 'wp1' in request.data and not request.data['wp1'] == None:
                serializer.save(wp1=float(request.data['wp1']))
                tmpids = TmpItemHelper.objects.filter(itemcart=tmpobj.itemcart).order_by('pk').aggregate(Sum('wp1'))
                value ="{:.2f}".format(float(tmpids['wp1__sum']))
                tmpl_ids = TmpItemHelper.objects.filter(itemcart=tmpobj.itemcart).order_by('pk')

                # for t in tmpl_ids:
                #    TmpItemHelper.objects.filter(id=t.pk).update(workcommpoints=value)


            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
            return Response(result, status=status.HTTP_200_OK)

        result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
        return Response(result, status=status.HTTP_200_OK)  

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def confirm(self, request):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if request.GET.get('cartid',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Cart Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).first().type in ['Top Up','Sales']:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
        cart_obj = ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).exclude(type__in=('Top Up','Sales')).first()
        if not cart_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        print(request,"request")
        cart_obj = ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).exclude(type__in=('Top Up','Sales'))       
        if cart_obj:
            tmp_ids = TmpItemHelper.objects.filter(itemcart=cart_obj[0])
            if not tmp_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Without employee cant do confirm!!",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            for emp in tmp_ids:
                appt = Appointment.objects.filter(cust_noid=cart_obj[0].cust_noid,appt_date=date.today(),
                ItemSite_Codeid=fmspw[0].loginsite,emp_no=emp.helper_code) 
                if not appt:
                    tmpids = TmpItemHelper.objects.filter(itemcart=cart_obj[0],helper_code=emp.helper_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                    if tmpids:
                        amsg = "Appointment is not available today, please give Start Time & Add Duration for employee {0} ".format(emp.helper_name)
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":amsg,'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                #need to uncomment later
                # if emp.appt_fr_time and emp.appt_to_time:         
                #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
                #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
                #     if appt_ids:
                #         msg = "In These timing already Appointment is booked for employee {0} so allocate other duration".format(emp.helper_name)
                #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)


            for existing in cart_obj[0].helper_ids.all():
                cart_obj[0].helper_ids.remove(existing) 

            for t in tmp_ids:
                cart_obj[0].helper_ids.add(t)        
        
        result = {'status': status.HTTP_200_OK , "message": "Confirmed Succesfully", 'error': False}
        return Response(result, status=status.HTTP_200_OK) 
    

    @action(detail=False, methods=['delete'], name='delete', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def delete(self, request):        
        if self.request.GET.get('clear_all',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give clear all/line in parms!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('cartid',None) is None:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Cart Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
        if ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).first().type in ['Top Up','Sales']:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Topup/Sales Cart Edit is not applicable!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
        cart_obj = ItemCart.objects.filter(isactive=True,id=request.GET.get('cartid',None)).exclude(type__in=('Top Up','Sales')).first()
        if not cart_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart record ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        state = status.HTTP_204_NO_CONTENT
        #try:
        if 1==1:
            tmp_ids = TmpItemHelper.objects.filter(itemcart=cart_obj).values_list('id')
            if not tmp_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Tmp Item Helper records is not present for this cart record id!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if self.request.GET.get('clear_all',None) == "1":
                queryset = TmpItemHelper.objects.filter(itemcart=cart_obj).order_by('id')
                for existing in queryset:
                    empobj = existing.helper_id.pk
                    cart_obj.service_staff.remove(empobj) 
                    existing.delete()

                cart_obj.done_sessions = None
                cart_obj.save()

            elif self.request.GET.get('clear_all',None) == "0":
                queryset = TmpItemHelper.objects.filter(itemcart=cart_obj).order_by('id').first()
                if TmpItemHelper.objects.filter(itemcart=cart_obj).order_by('id').count() == 1:
                    cart_obj.done_sessions = None
                    cart_obj.save()

                empobj = queryset.helper_id.pk
                cart_obj.service_staff.remove(empobj) 
                queryset.delete()

                if cart_obj.itemcodeid.workcommpoints == None or cart_obj.itemcodeid.workcommpoints == 0.0:
                    workcommpoints = 0.0
                else:
                    workcommpoints = cart_obj.itemcodeid.workcommpoints
            
                h_obj = TmpItemHelper.objects.filter(itemcart=cart_obj)
                count = 1
                if h_obj:
                    count = int(h_obj.count())
           
                wp1 = float(workcommpoints)
                wp11 = wp1
                wp12 = 0
                wp13 = 0
                wp14 = 0
                if float(workcommpoints) > 0 :
                    wp11 = wp1 / float(count)
                    if count == 2:
                        wp12 = wp1 / float(count)
                    if count == 3:
                        wp12 = wp1 / float(count)
                        wp13 = wp1 / float(count)
                    if count == 4:
                        wp12 = wp1 / float(count)
                        wp13 = wp1 / float(count)
                        wp14 = wp1 / float(count)

                    if count == 2 and wp1 == 3:
                        wp11 = 2
                        wp12 = 1
                    if count == 2 and wp1 == 5:
                        wp11 = 3
                        wp12 = 2
                    if count == 2 and wp1 == 7:
                        wp11 = 4
                        wp12 = 3
                    if count == 2 and wp1 == 9:
                        wp11 = 5
                        wp12 = 4
                    if count == 2 and wp1 == 11:
                        wp11 = 6
                        wp12 = 5

                    if count == 3 and wp1 == 2:
                        wp11 = 1
                        wp12 = 1
                        wp13 = 0
                    if count == 3 and wp1 == 4:
                        wp11 = 2
                        wp12 = 1
                        wp13 = 1
                    if count == 3 and wp1 == 5:
                        wp11 = 2
                        wp12 = 2
                        wp13 = 1
                    if count == 3 and wp1 == 7:
                        wp11 = 3
                        wp12 = 2
                        wp13 = 2
                    if count == 3 and wp1 == 8:
                        wp11 = 3
                        wp12 = 3
                        wp13 = 2
                    if count == 3 and wp1 == 10:
                        wp11 = 4
                        wp12 = 3
                        wp13 = 3
                    if count == 3 and wp1 == 11:
                        wp11 = 4
                        wp12 = 4
                        wp13 = 3

                    runx = 1
                    for h in TmpItemHelper.objects.filter(itemcart=cart_obj).order_by('pk'):
                        # TmpItemHelper.objects.filter(id=h.id).update(wp1=wp1)  
                        if runx == 1:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp11)
                        if runx == 2:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp12)
                        if runx == 3:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp13)
                        if runx == 4:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp14)
                        runx = float(runx) + 1

            result = {'status': status.HTTP_204_NO_CONTENT,"message":"Deleted Succesfully",'error': False}
            return Response(result,status=status.HTTP_200_OK)    
        #except Http404:
        #    pass

        result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 13",'error': True}
        return Response(result,status=status.HTTP_200_OK)    

class FocReasonAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FocReason.objects.filter(foc_reason_isactive=True).order_by('id')
    serializer_class = FocReasonSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content 15",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 


# from .models import (City,CustomerClass,State,Country,Maritalstatus,Races,Religious,Nationality,
# CommType,EmpSocso,Days,ReverseHdr,ReverseDtl,ItemRange)

# class UpdateTablesAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         # itemsitelist = ItemSitelist.objects.filter().order_by('-pk')
#         # for i in itemsitelist:
#         #     cityobj = City.objects.filter(itm_code=i.itemsite_city).first()
#         #     stateobj = State.objects.filter(itm_code=i.itemsite_state).first()
#         #     countryobj = Country.objects.filter(itm_code=i.itemsite_country).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=i.itemsite_user).first()
#         #     sitegroupobj = SiteGroup.objects.filter(code=i.site_group).first()
#         #     ItemSitelist.objects.filter(pk=i.pk).update(ItemSite_Cityid=cityobj,ItemSite_Stateid=stateobj,
#         #     ItemSite_Countryid=countryobj,ItemSite_Userid=fmspwobj,Site_Groupid=sitegroupobj) 
#         #     print(i.ItemSite_Cityid,i.ItemSite_Stateid,i.ItemSite_Countryid,i.ItemSite_Userid,i.Site_Groupid,"itemsitelist")

#         # voucherrecord = VoucherRecord.objects.filter().order_by('-pk')
#         # for v in voucherrecord:
#         #     custobj = Customer.objects.filter(cust_code=v.cust_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=v.site_code).first()
#         #     VoucherRecord.objects.filter(pk=v.pk).update(cust_codeid=custobj,site_codeid=siteobj)
#         #     print(v.cust_codeid,v.site_codeid,"voucherrecord")

#         # treatment = Treatment.objects.filter().order_by('-pk')
#         # for t in treatment:
#         #     custobj = Customer.objects.filter(cust_code=t.cust_code).first()
#         #     stockobj = Stock.objects.filter(item_code=t.item_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=t.site_code).first()
#         #     Treatment.objects.filter(pk=t.pk).update(Cust_Codeid=custobj,Item_Codeid=stockobj,Site_Codeid=siteobj)
#         #     print(t.Cust_Codeid,t.Item_Codeid,t.Site_Codeid,"treatment")

#         # employee = Employee.objects.filter().order_by('-pk')
#         # for e in employee:
#         #     genderobj = Gender.objects.filter(itm_code=e.emp_sexes).first()
#         #     maritalobj = Maritalstatus.objects.filter(itm_code=e.emp_marital).first()
#         #     racesobj = Races.objects.filter(itm_code=e.emp_race).first()
#         #     religiousobj = Religious.objects.filter(itm_code=e.emp_religion).first()
#         #     natobj = Nationality.objects.filter(itm_code=e.emp_nationality).first()
#         #     daysobj = Days.objects.filter(itm_code=e.emp_leaveday).first()
#         #     levelobj = EmpLevel.objects.filter(level_code=e.emp_type).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=e.site_code).first()
#         #     dsiteobj = ItemSitelist.objects.filter(itemsite_code=e.defaultsitecode).first()

#         #     Employee.objects.filter(pk=e.pk).update(Emp_sexesid=genderobj,Emp_maritalid=maritalobj,
#         #     Emp_raceid=racesobj,Emp_religionid=religiousobj,Emp_nationalityid=natobj,Emp_LeaveDayid=daysobj,
#         #     EMP_TYPEid=levelobj,Site_Codeid=siteobj,defaultSiteCodeid=dsiteobj)
#         #     print(e.EMP_TYPEid,e.Site_Codeid,e.defaultSiteCodeid,"Employee")    

#         # fmspw = Fmspw.objects.filter().order_by('-pk')
#         # for f in fmspw:
#         #     securitiesobj = Securities.objects.filter(level_code=f.level_itmid).first()
#         #     empobj = Employee.objects.filter(emp_code=f.emp_code).first()
#         #     user_obj = User.objects.filter(username=f.pw_userlogin)
#         #     user = None
#         #     if not user_obj:
#         #         user = User.objects.create_user(username=f.pw_userlogin,email=empobj.emp_email,password=f.pw_password)    
#         #         token = Token.objects.create(user=user)
#         #     Fmspw.objects.filter(pk=f.pk).update(LEVEL_ItmIDid=securitiesobj,Emp_Codeid=empobj,user=user)
#         #     print(f.LEVEL_ItmIDid,f.Emp_Codeid,"fmspw")

#         # customer = Customer.objects.filter().order_by('-pk')
#         # for c in customer:
#         #     genderobj = Gender.objects.filter(itm_code=c.cust_sexes).first()
#         #     custclassobj = CustomerClass.objects.filter(class_code=c.cust_class).first()
#         #     sourceobj = Source.objects.filter(source_code=c.cust_source).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=c.site_code).first()
#         #     Customer.objects.filter(pk=c.pk).update(Cust_sexesid=genderobj,Cust_Classid=custclassobj,
#         #     Cust_Sourceid=sourceobj,Site_Codeid=siteobj)
#         #     print(c.Cust_sexesid,c.Cust_Classid,c.Cust_Sourceid,c.Site_Codeid,"customer")

#         # treatmentaccount = TreatmentAccount.objects.filter().order_by('-pk')
#         # for a in treatmentaccount:
#         #     custobj = Customer.objects.filter(cust_code=a.cust_code).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=a.user_name).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=a.site_code).first()

#         #     TreatmentAccount.objects.filter(pk=a.pk).update(Cust_Codeid=custobj,User_Nameid=fmspwobj,
#         #     Site_Codeid=siteobj)
#         #     print(a.Cust_Codeid,a.User_Nameid,a.Site_Codeid,"TreatmentAccount")

#         # reversedtl = ReverseDtl.objects.filter().order_by('-pk')
#         # for r in reversedtl:
#         #     hdobj = ReverseHdr.objects.filter(reverse_no=r.reverse_no).first()
#         #     ReverseDtl.objects.filter(pk=r.pk).update(Reverse_Noid=hdobj)
#         #     print(r.Reverse_Noid,"ReverseDtl")

#         # poshaud = PosHaud.objects.filter().order_by('-pk')
#         # for h in poshaud:
#         #     empobj = Employee.objects.filter(emp_code=h.sa_staffno).first()
#         #     custobj = Customer.objects.filter(cust_code=h.sa_custno).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=h.itemsite_code).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=h.trans_user_login).first()
#         #     PosHaud.objects.filter(pk=h.pk).update(sa_staffnoid=empobj,sa_custnoid=custobj,
#         #     ItemSite_Codeid=siteobj,trans_user_loginid=fmspwobj)
#         #     print(h.sa_staffnoid,h.sa_custnoid,h.ItemSite_Codeid,h.trans_user_loginid,"PosHaud")

#         # posdaud = PosDaud.objects.filter().order_by('-pk')
#         # for d in posdaud:
#         #     s = d.dt_itemno
#         #     dt_itemno = s[:-4]
#         #     stockobj = Stock.objects.filter(item_code=dt_itemno).first()
#         #     empobj = Employee.objects.filter(emp_code=d.dt_staffno).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=d.itemsite_code).first()
#         #     PosDaud.objects.filter(pk=d.pk).update(dt_itemnoid=stockobj,dt_Staffnoid=empobj,
#         #     ItemSite_Codeid=siteobj)
#         #     print(d.dt_itemnoid,d.dt_Staffnoid,d.ItemSite_Codeid,"PosDaud")

#         # postaud = PosTaud.objects.filter().order_by('-pk')
#         # for ta in postaud:
#         #     grpobj = PayGroup.objects.filter(pay_group_code=ta.pay_group).first()
#         #     payobj = PAYTABLE.objects.filter(pay_code=ta.pay_type).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=ta.itemsite_code).first()
#         #     PosTaud.objects.filter(pk=ta.pk).update(pay_groupid=grpobj,pay_typeid=payobj,
#         #     ItemSIte_Codeid=siteobj)
#         #     print(t.pay_groupid,t.pay_typeid,t.ItemSIte_Codeid,"PosTaud")

#         # paytable = Paytable.objects.filter().order_by('-pk')
#         # for p in paytable:
#         #     grpobj = PayGroup.objects.filter(pay_group_code=p.pay_group).first()
#         #     Paytable.objects.filter(pk=p.pk).update(pay_groupid=grpobj)
#         #     print(p.pay_groupid,"Paytable")

#         # itemrange = ItemRange.objects.filter().order_by('-pk')
#         # for ra in itemrange:
#         #     depobj = ItemDept.objects.filter(itm_code=ra.itm_dept).first()
#         #     ItemRange.objects.filter(pk=ra.pk).update(itm_Deptid=depobj)
#         #     print(ra.itm_Deptid,"ItemRange") 

#         # itemuomprice = ItemUomprice.objects.filter().order_by('-pk')
#         # for u in itemuomprice:
#         #     uomobj = ItemUom.objects.filter(uom_code=u.item_uom).first()
#         #     uomobj2 = ItemUom.objects.filter(uom_code=u.item_uom2).first()
#         #     ItemUomprice.objects.filter(pk=u.pk).update(ITEM_UOMid=uomobj,ITEM_UOM2id=uomobj2)
#         #     print(u.ITEM_UOMid,u.ITEM_UOM2id,"ItemUomprice")       

#         # scmonth = ScheduleMonth.objects.filter().order_by('-pk')
#         # for m in scmonth:
#         #     empobj = Employee.objects.filter(emp_code=m.emp_code).first()
#         #     typeobj = ScheduleHour.objects.filter(itm_code=m.itm_type).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=m.user_name).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=m.site_code).first()
#         #     ScheduleMonth.objects.filter(pk=m.pk).update(Emp_Codeid=empobj,itm_Typeid=typeobj,
#         #     User_Nameid=fmspwobj,Site_Codeid=siteobj)
#         #     print(m.Emp_Codeid,m.itm_Typeid,m.User_Nameid,m.Site_Codeid,"ScheduleMonth")    

#         # attendance2 = Attendance2.objects.filter().order_by('-pk')
#         # for at in attendance2:
#         #     empobj = Employee.objects.filter(emp_code=at.attn_emp_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=at.attn_site_code).first()
#         #     Attendance2.objects.filter(pk=at.pk).update(Attn_Emp_codeid=empobj,Attn_Site_Codeid=siteobj)
#         #     print(at.Attn_Emp_codeid,at.Attn_Site_Codeid,"Attendance2")   

#         # empSitelist = EmpSitelist.objects.filter().order_by('-pk')
#         # for es in empSitelist:
#         #     empobj = Employee.objects.filter(emp_code=es.emp_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=es.site_code).first()
#         #     EmpSitelist.objects.filter(pk=es.pk).update(Emp_Codeid=empobj,Site_Codeid=siteobj)
#         #     print(es.Emp_Codeid,es.Site_Codeid,"EmpSitelist")  

#         # appointment = Appointment.objects.filter().order_by('-pk')
#         # for ap in appointment:
#         #     custobj = Customer.objects.filter(cust_code=ap.cust_no).first()
#         #     aptobj = ApptType.objects.filter(appt_type_desc=ap.appt_type).first()
#         #     empobj = Employee.objects.filter(emp_code=ap.emp_no).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=ap.appt_created_by).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=ap.itemsite_code).first()
#         #     sourceobj = Source.objects.filter(source_code=ap.source_code).first()

#         #     Appointment.objects.filter(pk=ap.pk).update(cust_noid=custobj,Appt_typeid=aptobj,
#         #     emp_noid=empobj,ItemSite_Codeid=siteobj,Appt_Created_Byid=fmspwobj,Source_Codeid=sourceobj)
#         #     print(ap.cust_noid,ap.Appt_typeid,ap.emp_noid,ap.Appt_Created_Byid,ap.ItemSite_Codeid,ap.Source_Codeid,"Appointment")       
                
#         # control = ControlNo.objects.filter().order_by('-pk')
#         # for co in control:
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=co.site_code).first()
#         #     ControlNo.objects.filter(pk=co.pk).update(Site_Codeid=siteobj)
#         #     print(co.Site_Codeid,"ControlNo")  


#         result = {'status': status.HTTP_200_OK,"message":"Updated Successfully",'error': False}
#         return Response(data=result, status=status.HTTP_200_OK) 

class AppointmentBlockViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('pk')
    serializer_class = AppointmentBlockSerializer

    def create(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            
            reason_obj = BlockReason.objects.filter(active=True,pk=request.data['reason_id']).first()
            if not reason_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"BlockReason ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not request.data['start_date']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Start Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not request.data['end_date']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give End Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not request.data['reason_id']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Reason!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not request.data['emp_ids'] or request.data['emp_ids'] == [] or request.data['emp_ids'] is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Select Employee!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                

            start_date = datetime.datetime.strptime(str(request.data['start_date']), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(str(request.data['end_date']), "%Y-%m-%d").date()
            day_count = (end_date - start_date).days + 1
            dateloop = [d for d in (start_date + timedelta(n) for n in range(day_count)) if d <= end_date]
            todaydate = timezone.now().date()         
            
            for e in request.data['emp_ids']:
                empobj = Employee.objects.filter(pk=e,emp_isactive=True).first()
                if not empobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                for single_date in dateloop:
                    sdate = datetime.datetime.strptime(str(single_date), "%Y-%m-%d").date()

                    if sdate < todaydate:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cant Block Appointments for Past days!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    prev_appts = Appointment.objects.filter(appt_date=sdate,emp_no=empobj.emp_code
                    ).filter(Q(appt_to_time__gt=request.data['appt_fr_time']) & Q(
                    appt_fr_time__lt=request.data['appt_to_time'])).order_by('-pk')
                    if prev_appts:
                        msg = "StartTime {0} EndTime {1} Employee {2} Already have appointment for this time".format(str(request.data['appt_fr_time']),str(request.data['appt_to_time']),str(empobj.display_name))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

            for em in request.data['emp_ids']:
                emp_obj = Employee.objects.filter(pk=em,emp_isactive=True).first()
                for singledate in dateloop:
                    control_obj = ControlNo.objects.filter(control_description__iexact="APPOINTMENT CODE",Site_Codeid__pk=site.pk).first()
                    if not control_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment Control No does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    appt_code = str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_prefix)+str(control_obj.control_no)
            
                    serializer = AppointmentBlockSerializer(data=request.data, context={'request': self.request})
                    if serializer.is_valid():
                        adate = datetime.datetime.strptime(str(singledate), "%Y-%m-%d").date()
                        duration = request.data['duration']
                        factors = (60, 1, 1/60)
                        minutes = sum(i*j for i, j in zip(map(int, duration.split(':')), factors))

                        starttime = datetime.datetime.strptime(request.data['appt_fr_time'], "%H:%M")
                        addduration = datetime.datetime.strptime(request.data['duration'], "%H:%M")

                        end_time = starttime + datetime.timedelta(minutes = minutes)
                        endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
              
                        appt = serializer.save(appt_date=adate,emp_noid=emp_obj,emp_no=emp_obj.emp_code,
                        emp_name=emp_obj.emp_name,appt_code=appt_code,appt_status="Block",
                        appt_created_by=fmspw.pw_userlogin,Appt_Created_Byid=fmspw,ItemSite_Codeid=site,
                        itemsite_code=site.itemsite_code,duration=minutes,reason=reason_obj.b_reason)
                        
                        if appt.pk:
                            control_obj.control_no = int(control_obj.control_no) + 1
                            control_obj.save()

                        master = Treatment_Master(course=reason_obj.b_reason,status="Block",appt_time=adate,duration=minutes,
                        Site_Codeid=site,site_code=site.itemsite_code,start_time=starttime,end_time=endtime,
                        add_duration=addduration,Appointment=appt)
                        master.save()
                        master.emp_no.add(emp_obj.pk)

                        apptlog = AppointmentLog(appt_id=appt,userid=fmspw.Emp_Codeid,
                        username=fmspw.Emp_Codeid.display_name,appt_date=adate,
                        appt_fr_time=starttime,appt_to_time=endtime,emp_code=emp_obj.emp_code,
                        appt_status="Block",appt_remark=request.data['appt_remark'],
                        add_duration=request.data['duration']).save()

                    else:
                        data = serializer.errors
                        # print(data,"data")
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",'error': False}
            return Response(result, status=status.HTTP_201_CREATED)

        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message) 

    def get_object(self, pk):
        #try:
            return Appointment.objects.get(pk=pk,appt_isactive=True)
        #except Appointment.DoesNotExist:
        #    raise Exception('Appointment Does not Exist') 

    def retrieve(self, request, pk=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            appointment = self.get_object(pk)
            appt = Appointment.objects.filter(pk=appointment.pk,appt_isactive=True,itemsite_code=site.itemsite_code).first()
            if not appt:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment does not exist",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            reason_obj = BlockReason.objects.filter(active=True,b_reason=appt.reason).first()
           
            serializer = AppointmentBlockSerializer(appointment, context={'request': self.request})
            data = serializer.data
            master_ids = Treatment_Master.objects.filter(Appointment=appointment,site_code=site.itemsite_code).order_by('id').first()

            start_time = get_in_val(self, master_ids.start_time) 
            end_time = get_in_val(self, master_ids.end_time) 
            add_duration = get_in_val(self, master_ids.add_duration) 

            trt_lst = []
            if master_ids and appointment:
                appt_date = datetime.datetime.strptime(str(data['appt_date']), "%Y-%m-%d").strftime("%d/%m/%Y")
                appt_data = {'start_date':appt_date,'end_date':appt_date,'appt_fr_time':start_time,
                'appt_to_time':end_time,'reason_id': reason_obj.pk if reason_obj else "",
                'duration':add_duration,'appt_remark':appt.appt_remark,'emp_noid':appt.emp_noid.pk,
                'emp_no':appt.emp_no,'emp_name':appt.emp_name}
                
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': appt_data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message) 

    def partial_update(self, request, pk=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            app = self.get_object(pk)
            master_id = Treatment_Master.objects.filter(Appointment__pk=app.pk).first()
            if app.appt_status != "Block":
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Only Blocked Appointment will allow to do update!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            reason_obj = BlockReason.objects.filter(active=True,pk=request.data['reason_id']).first()
            if not reason_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"BlockReason ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
                
            serializer = self.get_serializer(app, data=request.data, partial=True)
            if serializer.is_valid():
                duration = request.data['duration']
                factors = (60, 1, 1/60)
                minutes = sum(i*j for i, j in zip(map(int, duration.split(':')), factors))

                starttime = datetime.datetime.strptime(request.data['appt_fr_time'], "%H:%M")
                addduration = datetime.datetime.strptime(request.data['duration'], "%H:%M")

                end_time = starttime + datetime.timedelta(minutes = minutes)
                endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
              
                serializer.save(duration=minutes,reason=reason_obj.b_reason)

                apptlog = AppointmentLog(appt_id=app,userid=fmspw.Emp_Codeid,
                username=fmspw.Emp_Codeid.display_name,appt_date=app.appt_date,
                appt_fr_time=starttime,appt_to_time=endtime,emp_code=app.emp_no,
                appt_status=app.appt_status,appt_remark=app.appt_remark,
                add_duration=addduration).save()

                if master_id:
                    masterobj = Treatment_Master.objects.filter(pk=master_id.pk).update(
                    start_time=starttime,end_time=endtime,add_duration=addduration,duration=minutes,
                    course=reason_obj.b_reason)
                     
                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_200_OK)  
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)         


class BlockReasonAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = BlockReason.objects.filter(active=True).order_by('id')
    serializer_class = BlockReasonSerializer

    def list(self, request):
        # try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)     

class AppointmentLogAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = AppointmentLog.objects.filter().order_by('id')
    serializer_class = AppointmentLogSerializer

    def list(self, request):
        #try:
            if not request.GET.get('appt_id',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Appointment ID!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            serializer_class = AppointmentLogSerializer
            queryset = AppointmentLog.objects.filter(appt_id__pk=request.GET.get('appt_id',None)).order_by('-id')
            if queryset:
                total = len(queryset)
                state = status.HTTP_200_OK
                message = "Listed Succesfully"
                error = False
                data = None
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action='list')

                v = result.get('data')
                d = v.get('dataList')
                final = []
                for dat in d:
                    s = dict(dat)
                    s['appt_date'] = datetime.datetime.strptime(str(s['appt_date']), "%Y-%m-%d").strftime("%d/%m/%Y")
                    s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
                    s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
                    s['add_duration'] =  get_in_val(self, s['add_duration'])
                    dsplit = str(s['created_at']).split("T")
                    # s['created_at'] = datetime.datetimdoe.strptime(str(dsplit[0]), "%Y-%m-%d").strftime("%d/%m/%Y")
                    logdate = datetime.datetime.strptime(str(dsplit[0]), '%Y-%m-%d').strftime("%d/%m/%Y")
                    # print(dsplit,"dsplit")
                    # logtime = datetime.datetime.strptime(str(dsplit[1]), "%H:%M:%S").strftime("%H:%M:%S")
                    # print(logtime,"logtime")
                    s['created_at'] = logdate + ' ' + str(dsplit[1])[:5]
                    emp_obj = Employee.objects.filter(emp_code=s['emp_code'],emp_isactive=True).order_by('pk').first()
                    s['emp_name'] = emp_obj.display_name
                    final.append(s)

                v['dataList'] =  final  
                return Response(result, status=status.HTTP_200_OK)  

            else:
                result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK) 
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)                 


class AppointmentListPdf(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request, format=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            if not request.GET.get('start_date',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Start Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not request.GET.get('end_date',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give End Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            report_type = request.GET.get('type',None)
            if not report_type:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Type!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

            start_date = request.GET.get('start_date',None)
            end_date = request.GET.get('end_date',None)
            emp_ids = request.GET.get('emp_ids',None)
            site_ids = request.GET.get('site_ids',None)
            # print(site_ids,"site_ids")
            appt_status = request.GET.get('status',None)
            sec_status = request.GET.get('sec_status',None)

            appt_ids = Appointment.objects.filter(appt_date__gte=start_date,appt_date__lte=end_date,
            appt_isactive=True).order_by('appt_date')
            # print(appt_ids,len(appt_ids),"appt_ids")  

            if site_ids:
                if "," in site_ids:
                    split_s = site_ids.split(",")
                else:
                    split_s = str(site_ids).split(' ')
                
                sitec_ids = ItemSitelist.objects.filter(pk__in=split_s,itemsite_isactive=True)
                qsite_ids = list(set([e.itemsite_code for e in sitec_ids if e.itemsite_code]))
                appt_ids = appt_ids.filter(itemsite_code__in=qsite_ids).order_by('appt_date')
            

            if emp_ids:
                if "," in emp_ids:
                    split_e = emp_ids.split(",")
                else:
                    split_e = str(emp_ids).split(' ')

                empl_ids = Employee.objects.filter(pk__in=split_e,emp_isactive=True)
                qempids = list(set([e.emp_code for e in empl_ids if e.emp_code]))
                appt_ids = appt_ids.filter(emp_no__in=qempids).order_by('appt_date')
           

            if appt_status:
                if "," in appt_status:
                    split_sa = appt_status.split(",")
                else:
                    split_sa = str(appt_status).split(' ')

                appt_ids = appt_ids.filter(appt_status__in=split_sa).order_by('appt_date')

            if sec_status:
                if "," in sec_status:
                    split_se = sec_status.split(",")
                else:
                    split_se = str(sec_status).split(' ')

                appt_ids = appt_ids.filter(sec_status__in=split_se).order_by('appt_date')

            appt_dict = {} ; appt_lst = [] 
            
            if appt_ids:
                for a in appt_ids:
                    if a.pk not in appt_lst:
                        apptdate = datetime.datetime.strptime(str(a.appt_date), '%Y-%m-%d').strftime("%d/%m/%Y")
                        starttime = datetime.datetime.strptime(str(a.appt_fr_time), "%H:%M:%S").strftime("%H:%M:%S")
                        endtime = datetime.datetime.strptime(str(a.appt_to_time), "%H:%M:%S").strftime("%H:%M:%S")

                        # print(appt_dict,"appt_dict")
                        # print(a.pk,"pkk")
                        # print(a.appt_date,"appt_date")
                        # print(a.appt_status,"a.appt_status")
                        val = {'id':a.pk,'date':apptdate,'cust_name':a.cust_name if a.cust_name else "",
                            'phone':a.appt_phone if a.appt_phone else "",
                            'start_time': starttime,'end_time': endtime,'staff':a.emp_name,
                            'service':a.appt_remark,'status':a.appt_status}
                        if apptdate in appt_dict.keys():
                            # print("iff")
                            # print(appt_dict[apptdate],"appt_dict[apptdate]")
                            for ji in appt_dict[apptdate]:
                                # print(ji.keys(),"ji.keys()")
                                if a.appt_status in ji.keys():
                                    if not any(d['id'] == a.pk for d in ji[a.appt_status]):
                                        ji[a.appt_status].append(val)
                                else:
                                    # if not any(d['id'] == a.pk for d in ji[a.appt_status]):
                                    ji[a.appt_status] = [val]
                                    # appt_dict[apptdate].append(stat_val)
                        else:
                            # print("else")
                            stat_dict = {}
                            stat_dict[a.appt_status] = [val]
                            appt_dict[apptdate] = [stat_dict]

                        appt_lst.append(a.pk)  

            print(appt_dict,"appt_dict")
            
           

            title = Title.objects.filter(product_license=site.itemsite_code).first()
            path = None
            if title and title.logo_pic:
                path = BASE_DIR + title.logo_pic.url

            data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
            'address': title.trans_h2 if title and title.trans_h2 else '', 
            'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
            'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
            'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
            'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
            'path':path if path else '','title':title if title else None,
            'appt_data': appt_dict
            }
            
            if report_type == 'Pdf':
                template = get_template('appointment_list.html')
                display = Display(visible=0, size=(800, 600))
                display.start()
                html = template.render(data)
                options = {
                    'margin-top': '.25in',
                    'margin-right': '.25in',
                    'margin-bottom': '.25in',
                    'margin-left': '.25in',
                    'encoding': "UTF-8",
                    'no-outline': None,                
                }
                
                dst ="AppointmentReport" + ".pdf"

                p=pdfkit.from_string(html,False,options=options)
                PREVIEW_PATH = dst
                pdf = FPDF() 

                pdf.add_page() 
                
                pdf.set_font("Arial", size = 15) 
                file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                pdf.output(file_path) 

                if p:
                    file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                    report = os.path.isfile(file_path)
                    if report:
                        file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                        with open(file_path, 'wb') as fh:
                            fh.write(p)
                        display.stop()

                        ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/AppointmentReport"+".pdf"

                        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",
                        'error': False, 'data': ip_link}
                        return Response(data=result, status=status.HTTP_200_OK)

            elif report_type == 'Excel':
                dst ="AppointmentReport"+".xlsx"

                file_path = os.path.join(settings.PDF_ROOT, dst)
                # print(file_path,"file_path")

                workbook = xlsxwriter.Workbook(file_path)
                worksheet = workbook.add_worksheet('Appointment List')
                format1 = workbook.add_format({'align': 'left'})
                hformat = workbook.add_format({'font_size': 10, 'bold': True})
                dformat = workbook.add_format({'font_size': 10})

                worksheet.set_column(0, 10, 17, format1)

                worksheet.write('A1', 'DATE', hformat)
                worksheet.write('B1', 'Customer Name', hformat)
                worksheet.write('C1', 'Contact (HP)', hformat)
                worksheet.write('D1', 'Start Time', hformat)
                worksheet.write('E1', 'End Time', hformat)
                worksheet.write('F1', 'Staff', hformat)
                worksheet.write('G1', 'Service', hformat)
                
                row = 1
                for i in appt_dict:
                    worksheet.write(row, 0, 'Appointment Date :', hformat)
                    worksheet.write(row, 1, i, hformat)
                    row += 1
                    for j in appt_dict[i]:
                        for k in j:
                            worksheet.write(row, 0, 'Status :', hformat)
                            worksheet.write(row, 1, k, hformat)
                            row += 1
                            for l in j[k]:
                                worksheet.write(row, 0, l['date'], dformat)
                                worksheet.write(row, 1, l['cust_name'], dformat)
                                worksheet.write(row, 2, l['phone'], dformat)
                                worksheet.write(row, 3, l['start_time'], dformat)
                                worksheet.write(row, 4, l['end_time'], dformat)
                                worksheet.write(row, 5, l['staff'], dformat)
                                worksheet.write(row, 6, l['service'], dformat)
                                row += 1

                workbook.close()

                ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/"+dst

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",
                'error': False, 'data': ip_link}
                return Response(data=result, status=status.HTTP_200_OK) 
                
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)               

class DayEndListAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
   
    def list(self, request):
        # try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            givendate = request.GET.get('date',None)
            if not givendate:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            date_str = str(datetime.datetime.strptime(str(givendate), '%Y-%m-%d').strftime("%d-%m-%Y"))
            # date_val = str(date_str.day)+"_"+str(date_str.month)+"_"+str(date_str.year)
            date_display = str(datetime.datetime.strptime(str(givendate), '%Y-%m-%d').strftime("%d-%b-%Y"))

            saleslst = []; nonsaleslst = []

            listtype = request.GET.get('type',None)
            if not listtype:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Type!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            gt1_ids = Paytable.objects.filter(gt_group='GT1',pay_isactive=True).order_by('-pk') 
            gt1_lst = list(set([i.pay_code for i in gt1_ids if i.pay_code]))
            # print(gt1_lst,"gt1_lst")

            gt2_ids = Paytable.objects.filter(gt_group='GT2',pay_isactive=True).order_by('-pk') 
            gt2_lst = list(set([i.pay_code for i in gt2_ids if i.pay_code]))
            # print(gt2_lst,"gt2_lst")

            haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,isvoid=False).order_by('-pk')
            satranacno = list(set([i.sa_transacno for i in haudids if i.sa_transacno]))
            # print(satranacno,"satranacno")
            
            
            taud_salesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
            pay_type__in=gt1_lst,sa_transacno__in=satranacno).order_by('-pk').values('pay_type').order_by('pay_type'
            ).annotate(qty=Count('pay_type'),amount=Sum('pay_amt'),desc=F('pay_desc'),
            before_tax=Sum('pay_amt')-Sum('pay_gst')).order_by('-qty') 
            # print(taud_salesids,"taud_salesids")
            if taud_salesids:
                sales = list(taud_salesids)
                # print(sales,"sales")
                saleslst = [{'desc': i['desc'], 'qty': i['qty'], 'amount': "{:.2f}".format(i['amount']),'before_tax': "{:.2f}".format(i['before_tax'])}  for i in sales]
            # print(saleslst,"saleslst")

            sales_total_amt =  "{:.2f}".format(float(sum([float(i['amount']) for i in saleslst])))
            # print(sales_total_amt,"sales_total_amt")
            sales_qty =  sum([int(i['qty']) for i in saleslst])
            # print(sales_qty,"sales_qty")
            sales_beforetax = "{:.2f}".format(float(sum([float(i['before_tax']) for i in saleslst])))


            taud_nonsalesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
            pay_type__in=gt2_lst,sa_transacno__in=satranacno).order_by('-pk').values('pay_type').order_by('pay_type'
            ).annotate(qty=Count('pay_type'),amount=Sum('pay_amt'),desc=F('pay_desc')).order_by('-qty') 
            # print(taud_nonsalesids,"taud_nonsalesids") 
            if taud_nonsalesids:
                nonsales = list(taud_nonsalesids)
                nonsaleslst = [{'desc': i['desc'], 'qty': i['qty'], 'amount': "{:.2f}".format(i['amount'])}  for i in nonsales]
            
            # print(nonsaleslst,"nonsaleslst")
            nonsales_total_amt =  "{:.2f}".format(float(sum([float(i['amount']) for i in nonsaleslst])))
            nonsales_qty =  sum([float(i['qty']) for i in nonsaleslst])

            depo_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
            isvoid=False,sa_transacno_type__in=['Receipt','Non Sales']).order_by('-pk')
            # print(depo_haudids,"depo_haudids")
            
            depo_lst = []; ar_lst = []
            for d in depo_haudids:
                check_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
                sa_transacno=d.sa_transacno,record_detail_type__in=['SERVICE','PRODUCT',
                'PREPAID','VOUCHER','PACKAGE']).order_by('-pk')
                if check_ids:
                    daud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
                    sa_transacno=d.sa_transacno,record_detail_type__in=['SERVICE','PRODUCT',
                    'PREPAID','VOUCHER','PACKAGE']).order_by('-pk').aggregate(amount=Sum('dt_transacamt'),
                    paid=Sum('dt_deposit'),outstanding=Sum('dt_transacamt') - Sum('dt_deposit'))
                    # print(daud_ids,"daud_ids")

                    if daud_ids['amount'] > 0 and daud_ids['paid'] > 0:
                        val = {'satransac_ref' : d.sa_transacno_ref,'amount': "{:.2f}".format(float(daud_ids['amount'])),
                        'paid': "{:.2f}".format(float(daud_ids['paid'])),'outstanding': "{:.2f}".format(float(daud_ids['outstanding']))}
                        depo_lst.append(val)
                
                ardaudar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
                sa_transacno=d.sa_transacno,record_detail_type__in=['TP SERVICE','TP PRODUCT',
                'TP PREPAID']).order_by('-pk')
                if ardaudar_ids:
                    ardaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
                    sa_transacno=d.sa_transacno,record_detail_type__in=['TP SERVICE','TP PRODUCT',
                    'TP PREPAID']).order_by('-pk').aggregate(amount=Sum('dt_deposit'))
                    # print(ardaud_ids,"ardaud_ids")

                    if ardaud_ids['amount'] > 0:
                        arval = {'satransac_ref' : d.sa_transacno_ref,'amount': "{:.2f}".format(float(ardaud_ids['amount']))}
                        ar_lst.append(arval)


            # print(depo_lst,"depo_lst")  
            # print(ar_lst,"ar_lst")
            depo_amount =  "{:.2f}".format(float(sum([float(i['amount']) for i in depo_lst])))
            depo_paid =  "{:.2f}".format(float(sum([float(i['paid']) for i in depo_lst])))
            depo_outstanding =  "{:.2f}".format(float(sum([float(i['outstanding']) for i in depo_lst])))

            ar_amount =  "{:.2f}".format(float(sum([float(i['amount']) for i in ar_lst])))
               
            td_daud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
            sa_transacno__in=satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
            # print(td_daud_ids,"td_daud_ids") 
            tdlst = []
            for td in td_daud_ids:
                if td.st_ref_treatmentcode:
                    haudid = PosHaud.objects.filter(itemsite_code=site.itemsite_code,
                    sa_date__date=givendate,isvoid=False,sa_transacno=td.sa_transacno).order_by('-pk').first()
                    if haudid:
                        treat_ids = Treatment.objects.filter(site_code=site.itemsite_code,treatment_code=td.st_ref_treatmentcode,
                        status='Done',treatment_date__date=givendate).order_by('-pk').first()
                        if treat_ids:
                            td_vals = {'treatment_done':haudid.sa_transacno_ref,'desc':treat_ids.course,
                            'amount': "{:.2f}".format(treat_ids.unit_amount)}
                            tdlst.append(td_vals)

            td_amount =  "{:.2f}".format(float(sum([float(i['amount']) for i in tdlst])))
            # print(tdlst,"tdlst")
            dept_ids = ItemDept.objects.filter(is_service=True, itm_status=True).order_by('-pk')
            
            deptlst = []
            for dp in dept_ids:
                deptdaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
                sa_transacno__in=satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TP SERVICE'],
                dt_itemnoid__item_dept=dp.itm_code).order_by('-pk')
                if deptdaud_ids:
                    dept_daud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=givendate,
                    sa_transacno__in=satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TP SERVICE'],
                    dt_itemnoid__item_dept=dp.itm_code).order_by('-pk').aggregate(amount=Sum('dt_deposit'))
                   
                    if dept_daud_ids['amount'] > 0:
                        dep_vals = {'dept_sales':dp.itm_desc, 'amount': "{:.2f}".format(dept_daud_ids['amount'])}
                        deptlst.append(dep_vals)
            
            # print(deptlst,"deptlst")
            dept_amount =  "{:.2f}".format(float(sum([float(i['amount']) for i in deptlst])))
            # print(dept_amount,"dept_amount")
                       
            if listtype == 'list':
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",
                'error': False, 'sales_collec': {'sales': saleslst, 'total': sales_total_amt if float(sales_total_amt) > 0.0 else "0.00", 'qty': sales_qty,
                'total_tax':sales_beforetax if float(sales_beforetax) > 0.0 else "0.00"},
                'nonsales_collec': {'nonsales': nonsaleslst, 'total': nonsales_total_amt if float(nonsales_total_amt) > 0.0 else "0.00", 'qty': nonsales_qty},
                'sales_trasac': {'sales_trasac': depo_lst, 'total_amount': depo_amount if float(depo_amount) > 0.0 else "0.00", 
                'total_paid': depo_paid if float(depo_paid) > 0.0 else  "0.00", 
                'total_outstanding': depo_outstanding if float(depo_outstanding) > 0.0 else "0.00"},
                'ar_trasac': {'ar_trasac': ar_lst, 'total_amount': ar_amount if float(ar_amount) > 0.0 else "0.00"},
                'treatment_done': {'treatment_done': tdlst, 'total_amount': td_amount if float(td_amount) > 0.0 else "0.00"},
                'dept_sales': {'dept_sales': deptlst, 'total_amount': dept_amount if float(dept_amount) > 0.0 else "0.00"}
                }
                return Response(data=result, status=status.HTTP_200_OK)

            elif listtype in ['pdf','email']:
                title = Title.objects.filter(product_license='HQ').first()
                path = None
                if title and title.logo_pic:
                    path = BASE_DIR + title.logo_pic.url

                data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else '', 
                'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
                'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
                'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
                'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
                'saleslst': saleslst, 'sales_total_amt': sales_total_amt if float(sales_total_amt) > 0.0 else "0.00", 'sales_qty': sales_qty,'total_tax':sales_beforetax if float(sales_beforetax) > 0.0 else "0.00",
                'nonsaleslst': nonsaleslst,'nonsales_total_amt': nonsales_total_amt if float(nonsales_total_amt) > 0.0 else "0.00", 'nonsales_qty': nonsales_qty,
                'sales_trasac':depo_lst,'salestrasc_total_amount': depo_amount if float(depo_amount) > 0.0 else "0.00", 
                'salestrasc_total_paid': depo_paid if float(depo_paid) > 0.0 else  "0.00", 
                'salestrasc_total_outstanding': depo_outstanding if float(depo_outstanding) > 0.0 else "0.00",
                'ar_trasac':ar_lst,'artrasac_total_amount': ar_amount if float(ar_amount) > 0.0 else "0.00",
                'treatment_done':tdlst,'td_total_amount': td_amount if float(td_amount) > 0.0 else "0.00",
                'dept_sales': deptlst,'dept_total_amount': dept_amount if float(dept_amount) > 0.0 else "0.00",
                'path':path if path else '','title':title if title else None,
                'date_display': date_display}
                
                template = get_template('dayend.html')
                display = Display(visible=0, size=(800, 600))
                display.start()
                html = template.render(data)
                options = {
                    'margin-top': '.25in',
                    'margin-right': '.25in',
                    'margin-bottom': '.25in',
                    'margin-left': '.25in',
                    'encoding': "UTF-8",
                    'no-outline': None,
                    
                }
                
                dst ="DayEnd_"+date_str+".pdf"
                   
                p=pdfkit.from_string(html,False,options=options)

                if listtype == 'pdf':
                    PREVIEW_PATH = dst
                    pdf = FPDF() 

                    pdf.add_page() 
                    
                    pdf.set_font("Arial", size = 15) 
                    file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                    pdf.output(file_path) 

                    if p:
                        file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                        report = os.path.isfile(file_path)
                        if report:
                            file_path = os.path.join(settings.PDF_ROOT, PREVIEW_PATH)
                            with open(file_path, 'wb') as fh:
                                fh.write(p)
                            display.stop()

                            ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/DayEnd_"+date_str+".pdf"
                            
                            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                            'data': ip_link}
                            return Response(data=result, status=status.HTTP_200_OK)

                elif listtype == 'email':
                    subject = 'DayEnd Report PDF'

                    html_message = '''Dear Manager,\nKindly Find DayEnd Report on {0}.\nThank You,'''.format(date_str)
                    plain_message = strip_tags(html)
                  
                    system_setup = Systemsetup.objects.filter(title='DayEnd Email Setting',value_name='Email CC To').first()
                    if system_setup: 
                        to = [system_setup.value_data] if system_setup.value_data else []
                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give To Email in System Setting",'error': True}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
  

                    msg = EmailMultiAlternatives(subject, html_message, EMAIL_HOST_USER, to)

                    msg.attach(dst,p,'application/pdf')
                    msg.send()
                    response = HttpResponse(p,content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="DayEnd Report.pdf"'
                    result = {'status': status.HTTP_200_OK,"message":"Email sent succesfully",'error': False}
                    display.stop()
                    return Response(data=result, status=status.HTTP_200_OK)            
    
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)               


class TitleViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Title.objects.filter().order_by('-pk')
    serializer_class = TitleSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        queryset = Title.objects.none()
        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24: 
            queryset = Title.objects.filter().order_by('-pk')
       
        return queryset

    def list(self, request):
        #try:
            serializer_class = TitleSerializer
            queryset = self.filter_queryset(self.get_queryset())
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK) 
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)

    def create(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            serializer = TitleSerializer(data=request.data)
            if serializer.is_valid():
                siteobj = ItemSitelist.objects.filter(pk=request.data['site_id'],itemsite_isactive=True).first()
                serializer.save(product_license=siteobj.itemsite_code)
                result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_201_CREATED)
            
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
            'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)

    def get_object(self, pk):
        #try:
            return Title.objects.get(pk=pk)
        #except Title.DoesNotExist:
        #    raise Exception('Title Does not Exist') 

    def retrieve(self, request, pk=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            title = self.get_object(pk)
            serializer = TitleSerializer(title, context={'request': self.request})
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
            'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message) 
    
    
    def partial_update(self, request, pk=None):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            title = self.get_object(pk)

            serializer = self.get_serializer(title, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(updated_at=timezone.now())

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_200_OK)  
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)   


    def destroy(self, request, pk=None):
        title = self.get_object(pk)
        title.delete()
        result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
        return Response(result, status=status.HTTP_200_OK)



class CustApptUpcomingAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Appointment.objects.filter(appt_isactive=True).order_by('-pk')
    serializer_class = CustApptUpcomingSerializer

    def list(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite
            cust_id = self.request.GET.get('cust_id',None)
            if not cust_id:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Customer ID",
                'error': True, 'data': serializer.errors}
            
            cust_obj = Customer.objects.filter(pk=cust_id,
            cust_isactive=True,site_code=site.itemsite_code).first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  
            
                
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite            
            serializer_class = CustApptUpcomingSerializer
            queryset = Appointment.objects.filter(appt_date__gte=date.today(),itemsite_code=site.itemsite_code,
            appt_isactive=True,cust_noid__pk=cust_id).order_by('-pk')
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action='list')
            return Response(result, status=status.HTTP_200_OK) 
            
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)   


class AttendanceStaffsAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Attendance2.objects.filter().order_by('pk')
    serializer_class = AttendanceStaffsSerializer

    def list(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True).first()
            site = fmspw.loginsite 
            serializer_class = AttendanceStaffsSerializer

            query = Attendance2.objects.filter(attn_date__date=date.today(),
            attn_site_code=site.itemsite_code).order_by('-pk')
            lst = list(set([i.attn_emp_code for i in query]))
            data = []
            for i in lst:
                query = Attendance2.objects.filter(attn_date__date=date.today(),
                attn_site_code=site.itemsite_code,attn_emp_code=i).order_by('pk').last()
                data.append(query.pk)

            queryset = Attendance2.objects.filter(pk__in=data).order_by('-pk')

            if queryset:
                total = len(queryset)
                state = status.HTTP_200_OK
                message = "Listed Succesfully"
                error = False
                data = None
                result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action='list')
                return Response(result, status=status.HTTP_200_OK)  

            else:
                result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK) 

        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)                 


class StaffPlusViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Employee.objects.all().order_by('-pk')
    serializer_class = StaffPlusSerializer
    filter_backends = [DjangoFilterBackend, ]

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Unauthenticated Users are not allowed!!",
                      'error': True}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Unauthenticated Users are not Permitted!!",
                      'error': True}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        site = fmspw[0].loginsite
        empl = fmspw[0].Emp_Codeid
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Users Item Site is not mapped!!",
                      'error': True}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        emp_ids = EmpSitelist.objects.filter(Site_Codeid__pk=site.pk, isactive=True)

        queryset = Employee.objects.none()

        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24:
            # queryset = Employee.objects.filter(emp_isactive=True).order_by('-pk')
            queryset = Employee.objects.all().order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 31:
            emp_lst = list(set([e.Emp_Codeid.pk for e in emp_ids if e.Emp_Codeid]))
            # queryset = Employee.objects.filter(pk__in=emp_lst, emp_isactive=True).order_by('-pk')
            queryset = Employee.objects.filter(pk__in=emp_lst).order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) == 27:
            emp_lst = list(set([e.Emp_Codeid.pk for e in emp_ids if e.Emp_Codeid.pk == empl.pk]))
            # queryset = Employee.objects.filter(pk__in=emp_lst, emp_isactive=True).order_by('-pk')
            queryset = Employee.objects.filter(pk__in=emp_lst).order_by('-pk')
        q = self.request.GET.get('search', None)
        value = self.request.GET.get('sortValue', None)
        key = self.request.GET.get('sortKey', None)

        if q is not None:
            queryset = queryset.filter(Q(emp_name__icontains=q) | Q(emp_code__icontains=q) |
                                       Q(skills__item_desc__icontains=q) | Q(Site_Codeid__itemsite_desc__icontains=q) |
                                       Q(defaultSiteCodeid__itemsite_desc__icontains=q)).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'emp_name':
                    queryset = queryset.order_by('emp_name')
                elif key == 'emp_code':
                    queryset = queryset.order_by('emp_code')
                elif key == 'skills':
                    queryset = queryset.order_by('skills')
                elif key == 'Site_Codeid':
                    queryset = queryset.order_by('Site_Codeid')
                elif key == 'defaultSiteCodeid':
                    queryset = queryset.order_by('defaultSiteCodeid')
            elif value == "desc":
                if key == 'emp_name':
                    queryset = queryset.order_by('-emp_name')
                elif key == 'emp_code':
                    queryset = queryset.order_by('-emp_code')
                elif key == 'skills':
                    queryset = queryset.order_by('-skills')
                elif key == 'Site_Codeid':
                    queryset = queryset.order_by('-Site_Codeid')
                elif key == 'defaultSiteCodeid':
                    queryset = queryset.order_by('defaultSiteCodeid')

        return queryset

    def list(self, request):
        try:
            serializer_class = StaffPlusSerializer
            queryset = self.filter_queryset(self.get_queryset())
            query_parm_dict = request.GET
            for k, v in query_parm_dict.items():
                if hasattr(Employee, k):
                    try:
                        queryset = queryset.filter(**{k: v})
                    except FieldError:
                        continue
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def create(self, request):
        try:
            state = status.HTTP_400_BAD_REQUEST
            result = {}
            fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
            Site_Codeid = fmspw[0].loginsite
            if not self.request.user.is_authenticated:
                result = {'status': state, "message": "Unauthenticated Users are not allowed!!", 'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            if not fmspw:
                result = {'status': state, "message": "Unauthenticated Users are not Permitted!!", 'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            if not Site_Codeid:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Users Item Site is not mapped!!",
                          'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            queryset = None
            serializer_class = None
            total = None
            serializer = self.get_serializer(data=request.data, context={'request': self.request})

            if int(fmspw[0].level_itmid) not in [24, 31]:
                result = {'status': status.HTTP_400_BAD_REQUEST,
                          "message": "Staffs / other login user not allow to create staff!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if serializer.is_valid():
                try:
                    with transaction.atomic():
                        control_obj = ControlNo.objects.filter(control_description__iexact="EMP CODE",
                                                               Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                        if not control_obj:
                            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Employee Control No does not exist!!",
                                      'error': True}
                            # return Response(result, status=status.HTTP_400_BAD_REQUEST)
                            raise ValueError("Employee Control No does not exist!!")
                        emp_code = str(control_obj.control_prefix) + str(control_obj.control_no)
                        defaultobj = ItemSitelist.objects.filter(pk=request.data['defaultSiteCodeid'],
                                                                 itemsite_isactive=True).first()

                        site_unique = EmpSitelist.objects.filter(emp_code=emp_code, site_code=defaultobj.itemsite_code,
                                                                 isactive=True)
                        if site_unique:
                            result = {'status': state, "message": "Unique Constrain for emp_code and site_code!!",
                                      'error': True}
                            # return Response(result, status=status.HTTP_400_BAD_REQUEST)
                            raise ValueError("Unique Constrain for emp_code and site_code!!")
                        user_obj = User.objects.filter(username=request.data['emp_name'])
                        if user_obj:
                            result = {'status': state, "message": "Username already exist!!", 'error': True}
                            raise ValueError("Username already exist!!")
                            # return Response(result, status=status.HTTP_400_BAD_REQUEST)
                        emp_obj = Employee.objects.filter(emp_name=request.data['emp_name'])
                        if emp_obj:
                            result = {'status': state, "message": "Employee already exist!!", 'error': True}
                            raise ValueError("Employee already exist!!")
                        fmspw_obj = Fmspw.objects.filter(pw_userlogin=request.data['emp_name'])
                        if fmspw_obj:
                            result = {'status': state, "message": "Fmspw already exist!!", 'error': True}
                            # return Response(result, status=status.HTTP_400_BAD_REQUEST)
                            raise ValueError("Fmspw already exist!!")

                        token_obj = Fmspw.objects.filter(user__username=request.data['emp_name'])
                        if token_obj:
                            result = {'status': state, "message": "Token for this employee user is already exist!!",
                                      'error': True}
                            # return Response(result, status=status.HTTP_400_BAD_REQUEST)
                            raise ValueError("Token for this employee user is already exist!!")

                        jobtitle = EmpLevel.objects.filter(id=request.data['EMP_TYPEid'], level_isactive=True).first()
                        gender = Gender.objects.filter(pk=request.data.get('Emp_sexesid'), itm_isactive=True).first()
                        gender_code = gender.itm_code if gender else None
                        # self.perform_create(serializer) # commented this line to fix sitecode () issue.
                        s = serializer.save(emp_code=emp_code, emp_type=jobtitle.level_code, emp_sexes=gender_code,
                                            defaultsitecode=defaultobj.itemsite_code, site_code=Site_Codeid.itemsite_code
                                            )
                        s.emp_code = emp_code
                        s.save()
                        token = False
                        if s.is_login == True:
                            if request.data.get('pw_password') is None:
                                result = {'status': status.HTTP_400_BAD_REQUEST,
                                          "message": "pw_password Field is required.",
                                          'error': True}
                                raise ValueError("pw_password Field is required.")

                            if request.data.get('LEVEL_ItmIDid') is None:
                                result = {'status': status.HTTP_400_BAD_REQUEST,
                                          "message": "LEVEL_ItmIDid Field is required.",
                                          'error': True}
                                raise ValueError("LEVEL_ItmIDid Field is required.")


                            EmpSitelist(Emp_Codeid=s, emp_code=emp_code, Site_Codeid=s.defaultSiteCodeid,
                                        site_code=s.defaultSiteCodeid.itemsite_code).save()
                            user = User.objects.create_user(username=s.emp_name, email=s.emp_email,
                                                            password=request.data['pw_password'])
                            levelobj = Securities.objects.filter(pk=request.data['LEVEL_ItmIDid'], level_isactive=True).first()
                            Fmspw(pw_userlogin=s.emp_name,
                                  pw_password=request.data['pw_password'],
                                  LEVEL_ItmIDid=levelobj,
                                  level_itmid=levelobj.level_code,
                                  level_desc=levelobj.level_description,
                                  Emp_Codeid=s,
                                  emp_code=emp_code,
                                  user=user,
                                  loginsite=None,
                                  flgappt = s.show_in_appt,
                                  flgsales = s.show_in_sales,
                                  ).save()
                            s.pw_userlogin = s.emp_name
                            s.pw_password = request.data['pw_password']
                            s.LEVEL_ItmIDid = levelobj
                            s.save()
                            token = Token.objects.create(user=user)
                        if s.pk:
                            control_obj.control_no = int(control_obj.control_no) + 1
                            control_obj.save()
                except ValueError as e:
                    # result = {'status': state, "message": str(e),
                    #           'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    result = {'status': status.HTTP_400_BAD_REQUEST, "message": str(e),
                              'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)


                state = status.HTTP_201_CREATED
                message = "Created Succesfully"
                error = False
                data = serializer.data
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                v = result.get('data')
                if token:
                    v["token"] = token.key

                return Response(result, status=status.HTTP_201_CREATED)

            message = "Invalid Input"
            error = True
            data = serializer.errors
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def get_object(self, pk):
        try:
            # return Employee.objects.get(pk=pk, emp_isactive=True)
            return Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            raise Http404("Invalid Staff Id")

    def retrieve(self, request, pk=None):
        try:
            ip = get_client_ip(request)
            queryset = None
            total = None
            serializer_class = None
            employee = self.get_object(pk)
            serializer = StaffPlusSerializer(employee)
            data = serializer.data
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            v = result.get('data')
            if v['emp_pic']:
                images = str(ip) + str(v['emp_pic'])
                v['emp_pic'] = images
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            employee = self.get_object(pk)
            serializer = StaffPlusSerializer(employee, data=request.data, context={'request': self.request})
            if serializer.is_valid():
                if 'emp_name' in request.data and not request.data['emp_name'] is None:
                    serializer.save()
                    fmspw_obj = Fmspw.objects.filter(Emp_Codeid=employee, pw_isactive=True).first()
                    if fmspw_obj:
                        fmspw_obj.pw_userlogin = request.data['emp_name']
                        fmspw_obj.save()
                        if fmspw_obj.user:
                            fmspw_obj.user.username = request.data['emp_name']
                            fmspw_obj.user.save()
                        else:
                            result = {'status': status.HTTP_400_BAD_REQUEST,
                                      "message": "FMSPW User is not Present.Please map", 'error': True}
                            return Response(result, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_204_NO_CONTENT
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def partial_update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            employee = self.get_object(pk)
            serializer = StaffPlusSerializer(employee, data=request.data, partial=True,
                                             context={'request': self.request})
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_204_NO_CONTENT
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
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
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)
            except Http404:
                pass

            message = "No Content"
            error = True
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def perform_destroy(self, instance):
        instance.emp_isactive = False
        instance.save()

    @action(detail=True, methods=['PUT'], permission_classes=[IsAuthenticated & authenticated_only],
            authentication_classes=[TokenAuthentication], url_path='EmpInfo', url_name='EmpInfo')
    def EmpInfo(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            employee = self.get_object(pk)
            serializer = EmpInfoSerializer(employee, data=request.data, partial=True,
                                           context={'request': self.request})
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_204_NO_CONTENT
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @action(detail=True, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated & authenticated_only],
            authentication_classes=[TokenAuthentication], url_path='WorkSchedule', url_name='WorkSchedule')
    def WorkSchedule(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            employee = self.get_object(pk)
            is_alt = request.GET.get("is_alt", "false")

            is_alt = True if is_alt.lower() == "true" else False

            work_schedule = Workschedule.objects.filter(emp_code=employee.emp_code, is_alternative=is_alt).first()
            if work_schedule is None:
                work_schedule = Workschedule.objects.create(emp_code=employee.emp_code, is_alternative=is_alt)

            if request.method == "PUT":
                serializer = EmpWorkScheduleSerializer(work_schedule, data=request.data, partial=True,
                                                       context={'request': self.request})
                if serializer.is_valid():
                    serializer.save()
                    state = status.HTTP_200_OK
                    message = "Updated Succesfully"
                    error = False
                    data = serializer.data
                    result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                      action=self.action)
                    return Response(result, status=status.HTTP_200_OK)

                state = status.HTTP_204_NO_CONTENT
                message = "Invalid Input"
                error = True
                data = serializer.errors
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)
            else:
                serializer = EmpWorkScheduleSerializer(work_schedule)
                data = serializer.data
                state = status.HTTP_200_OK
                message = "Listed Succesfully"
                error = False
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    @action(detail=True, methods=['GET', 'POST'], permission_classes=[IsAuthenticated & authenticated_only],
            authentication_classes=[TokenAuthentication], url_path='StaffSkills', url_name='StaffSkills')
    def StaffSkills(self, request, pk=None):
        try:
            employee = self.get_object(pk)
            site_code = employee.site_code # todo: site_code get from FE
            if request.method == "POST":
                skill_list = request.data.get("skillsCodeList", [])
                old_skills = list(Skillstaff.objects.filter(sitecode=site_code, staffcode=employee.emp_code))
                # print("before",len(old_skills))
                try:
                    # transaction starts: if skill code is invalid or Skillstaff data insertion failed
                    # db will roll back to previous status
                    with transaction.atomic():
                        for skill_code in skill_list:

                            _skill = Stock.objects.get(item_code=skill_code)
                            if not _skill.item_isactive:
                                result = {'status': status.HTTP_400_BAD_REQUEST,
                                          'message': f"{skill_code} skill is inactive",
                                          'error': True, "data": None}
                                return Response(result, status=status.HTTP_400_BAD_REQUEST)

                            skillstaff_obj = Skillstaff(sitecode=employee.site_code,
                                                        staffcode=employee.emp_code,
                                                        itemcode=skill_code)
                            skillstaff_obj.save()

                        for _old in old_skills:
                            _old.delete()

                    # transaction ends here
                except Exception as e:
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                                      'message': f"invalid skill code {skill_code}, {e}",
                                      'error': True, "data": None}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                message = "updated Succesfully"

            elif request.method == "GET":
                message = "Listed Succesfully"

            skill_qs = Skillstaff.objects.filter(staffcode=employee.emp_code,sitecode=employee.site_code)
            responseData = {}
            skills_list = []
            for sk in skill_qs:
                itm_code = str(sk.itemcode)
                _stock = Stock.objects.filter(item_code=itm_code).values("item_code", "item_name").first()
                if _stock:
                    skills_list.append(_stock)
            state = status.HTTP_200_OK
            responseData["skills"] = skills_list
            result = {'status': state, 'message': message,
                      'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

        # from .models import (City,CustomerClass,State,Country,Maritalstatus,Races,Religious,Nationality,


# CommType,EmpSocso,Days,ReverseHdr,ReverseDtl,ItemRange)

# class UpdateTablesAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]

#     def post(self, request):
#         # itemsitelist = ItemSitelist.objects.filter().order_by('-pk')
#         # for i in itemsitelist:
#         #     cityobj = City.objects.filter(itm_code=i.itemsite_city).first()
#         #     stateobj = State.objects.filter(itm_code=i.itemsite_state).first()
#         #     countryobj = Country.objects.filter(itm_code=i.itemsite_country).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=i.itemsite_user).first()
#         #     sitegroupobj = SiteGroup.objects.filter(code=i.site_group).first()
#         #     ItemSitelist.objects.filter(pk=i.pk).update(ItemSite_Cityid=cityobj,ItemSite_Stateid=stateobj,
#         #     ItemSite_Countryid=countryobj,ItemSite_Userid=fmspwobj,Site_Groupid=sitegroupobj)
#         #     print(i.ItemSite_Cityid,i.ItemSite_Stateid,i.ItemSite_Countryid,i.ItemSite_Userid,i.Site_Groupid,"itemsitelist")

#         # voucherrecord = VoucherRecord.objects.filter().order_by('-pk')
#         # for v in voucherrecord:
#         #     custobj = Customer.objects.filter(cust_code=v.cust_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=v.site_code).first()
#         #     VoucherRecord.objects.filter(pk=v.pk).update(cust_codeid=custobj,site_codeid=siteobj)
#         #     print(v.cust_codeid,v.site_codeid,"voucherrecord")

#         # treatment = Treatment.objects.filter().order_by('-pk')
#         # for t in treatment:
#         #     custobj = Customer.objects.filter(cust_code=t.cust_code).first()
#         #     stockobj = Stock.objects.filter(item_code=t.item_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=t.site_code).first()
#         #     Treatment.objects.filter(pk=t.pk).update(Cust_Codeid=custobj,Item_Codeid=stockobj,Site_Codeid=siteobj)
#         #     print(t.Cust_Codeid,t.Item_Codeid,t.Site_Codeid,"treatment")

#         # employee = Employee.objects.filter().order_by('-pk')
#         # for e in employee:
#         #     genderobj = Gender.objects.filter(itm_code=e.emp_sexes).first()
#         #     maritalobj = Maritalstatus.objects.filter(itm_code=e.emp_marital).first()
#         #     racesobj = Races.objects.filter(itm_code=e.emp_race).first()
#         #     religiousobj = Religious.objects.filter(itm_code=e.emp_religion).first()
#         #     natobj = Nationality.objects.filter(itm_code=e.emp_nationality).first()
#         #     daysobj = Days.objects.filter(itm_code=e.emp_leaveday).first()
#         #     levelobj = EmpLevel.objects.filter(level_code=e.emp_type).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=e.site_code).first()
#         #     dsiteobj = ItemSitelist.objects.filter(itemsite_code=e.defaultsitecode).first()

#         #     Employee.objects.filter(pk=e.pk).update(Emp_sexesid=genderobj,Emp_maritalid=maritalobj,
#         #     Emp_raceid=racesobj,Emp_religionid=religiousobj,Emp_nationalityid=natobj,Emp_LeaveDayid=daysobj,
#         #     EMP_TYPEid=levelobj,Site_Codeid=siteobj,defaultSiteCodeid=dsiteobj)
#         #     print(e.EMP_TYPEid,e.Site_Codeid,e.defaultSiteCodeid,"Employee")

#         # fmspw = Fmspw.objects.filter().order_by('-pk')
#         # for f in fmspw:
#         #     securitiesobj = Securities.objects.filter(level_code=f.level_itmid).first()
#         #     empobj = Employee.objects.filter(emp_code=f.emp_code).first()
#         #     user_obj = User.objects.filter(username=f.pw_userlogin)
#         #     user = None
#         #     if not user_obj:
#         #         user = User.objects.create_user(username=f.pw_userlogin,email=empobj.emp_email,password=f.pw_password)
#         #         token = Token.objects.create(user=user)
#         #     Fmspw.objects.filter(pk=f.pk).update(LEVEL_ItmIDid=securitiesobj,Emp_Codeid=empobj,user=user)
#         #     print(f.LEVEL_ItmIDid,f.Emp_Codeid,"fmspw")

#         # customer = Customer.objects.filter().order_by('-pk')
#         # for c in customer:
#         #     genderobj = Gender.objects.filter(itm_code=c.cust_sexes).first()
#         #     custclassobj = CustomerClass.objects.filter(class_code=c.cust_class).first()
#         #     sourceobj = Source.objects.filter(source_code=c.cust_source).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=c.site_code).first()
#         #     Customer.objects.filter(pk=c.pk).update(Cust_sexesid=genderobj,Cust_Classid=custclassobj,
#         #     Cust_Sourceid=sourceobj,Site_Codeid=siteobj)
#         #     print(c.Cust_sexesid,c.Cust_Classid,c.Cust_Sourceid,c.Site_Codeid,"customer")

#         # treatmentaccount = TreatmentAccount.objects.filter().order_by('-pk')
#         # for a in treatmentaccount:
#         #     custobj = Customer.objects.filter(cust_code=a.cust_code).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=a.user_name).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=a.site_code).first()

#         #     TreatmentAccount.objects.filter(pk=a.pk).update(Cust_Codeid=custobj,User_Nameid=fmspwobj,
#         #     Site_Codeid=siteobj)
#         #     print(a.Cust_Codeid,a.User_Nameid,a.Site_Codeid,"TreatmentAccount")

#         # reversedtl = ReverseDtl.objects.filter().order_by('-pk')
#         # for r in reversedtl:
#         #     hdobj = ReverseHdr.objects.filter(reverse_no=r.reverse_no).first()
#         #     ReverseDtl.objects.filter(pk=r.pk).update(Reverse_Noid=hdobj)
#         #     print(r.Reverse_Noid,"ReverseDtl")

#         # poshaud = PosHaud.objects.filter().order_by('-pk')
#         # for h in poshaud:
#         #     empobj = Employee.objects.filter(emp_code=h.sa_staffno).first()
#         #     custobj = Customer.objects.filter(cust_code=h.sa_custno).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=h.itemsite_code).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=h.trans_user_login).first()
#         #     PosHaud.objects.filter(pk=h.pk).update(sa_staffnoid=empobj,sa_custnoid=custobj,
#         #     ItemSite_Codeid=siteobj,trans_user_loginid=fmspwobj)
#         #     print(h.sa_staffnoid,h.sa_custnoid,h.ItemSite_Codeid,h.trans_user_loginid,"PosHaud")

#         # posdaud = PosDaud.objects.filter().order_by('-pk')
#         # for d in posdaud:
#         #     s = d.dt_itemno
#         #     dt_itemno = s[:-4]
#         #     stockobj = Stock.objects.filter(item_code=dt_itemno).first()
#         #     empobj = Employee.objects.filter(emp_code=d.dt_staffno).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=d.itemsite_code).first()
#         #     PosDaud.objects.filter(pk=d.pk).update(dt_itemnoid=stockobj,dt_Staffnoid=empobj,
#         #     ItemSite_Codeid=siteobj)
#         #     print(d.dt_itemnoid,d.dt_Staffnoid,d.ItemSite_Codeid,"PosDaud")

#         # postaud = PosTaud.objects.filter().order_by('-pk')
#         # for ta in postaud:
#         #     grpobj = PayGroup.objects.filter(pay_group_code=ta.pay_group).first()
#         #     payobj = PAYTABLE.objects.filter(pay_code=ta.pay_type).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=ta.itemsite_code).first()
#         #     PosTaud.objects.filter(pk=ta.pk).update(pay_groupid=grpobj,pay_typeid=payobj,
#         #     ItemSIte_Codeid=siteobj)
#         #     print(t.pay_groupid,t.pay_typeid,t.ItemSIte_Codeid,"PosTaud")

#         # paytable = Paytable.objects.filter().order_by('-pk')
#         # for p in paytable:
#         #     grpobj = PayGroup.objects.filter(pay_group_code=p.pay_group).first()
#         #     Paytable.objects.filter(pk=p.pk).update(pay_groupid=grpobj)
#         #     print(p.pay_groupid,"Paytable")

#         # itemrange = ItemRange.objects.filter().order_by('-pk')
#         # for ra in itemrange:
#         #     depobj = ItemDept.objects.filter(itm_code=ra.itm_dept).first()
#         #     ItemRange.objects.filter(pk=ra.pk).update(itm_Deptid=depobj)
#         #     print(ra.itm_Deptid,"ItemRange")

#         # itemuomprice = ItemUomprice.objects.filter().order_by('-pk')
#         # for u in itemuomprice:
#         #     uomobj = ItemUom.objects.filter(uom_code=u.item_uom).first()
#         #     uomobj2 = ItemUom.objects.filter(uom_code=u.item_uom2).first()
#         #     ItemUomprice.objects.filter(pk=u.pk).update(ITEM_UOMid=uomobj,ITEM_UOM2id=uomobj2)
#         #     print(u.ITEM_UOMid,u.ITEM_UOM2id,"ItemUomprice")

#         # scmonth = ScheduleMonth.objects.filter().order_by('-pk')
#         # for m in scmonth:
#         #     empobj = Employee.objects.filter(emp_code=m.emp_code).first()
#         #     typeobj = ScheduleHour.objects.filter(itm_code=m.itm_type).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=m.user_name).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=m.site_code).first()
#         #     ScheduleMonth.objects.filter(pk=m.pk).update(Emp_Codeid=empobj,itm_Typeid=typeobj,
#         #     User_Nameid=fmspwobj,Site_Codeid=siteobj)
#         #     print(m.Emp_Codeid,m.itm_Typeid,m.User_Nameid,m.Site_Codeid,"ScheduleMonth")

#         # attendance2 = Attendance2.objects.filter().order_by('-pk')
#         # for at in attendance2:
#         #     empobj = Employee.objects.filter(emp_code=at.attn_emp_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=at.attn_site_code).first()
#         #     Attendance2.objects.filter(pk=at.pk).update(Attn_Emp_codeid=empobj,Attn_Site_Codeid=siteobj)
#         #     print(at.Attn_Emp_codeid,at.Attn_Site_Codeid,"Attendance2")

#         # empSitelist = EmpSitelist.objects.filter().order_by('-pk')
#         # for es in empSitelist:
#         #     empobj = Employee.objects.filter(emp_code=es.emp_code).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=es.site_code).first()
#         #     EmpSitelist.objects.filter(pk=es.pk).update(Emp_Codeid=empobj,Site_Codeid=siteobj)
#         #     print(es.Emp_Codeid,es.Site_Codeid,"EmpSitelist")

#         # appointment = Appointment.objects.filter().order_by('-pk')
#         # for ap in appointment:
#         #     custobj = Customer.objects.filter(cust_code=ap.cust_no).first()
#         #     aptobj = ApptType.objects.filter(appt_type_desc=ap.appt_type).first()
#         #     empobj = Employee.objects.filter(emp_code=ap.emp_no).first()
#         #     fmspwobj = Fmspw.objects.filter(pw_userlogin=ap.appt_created_by).first()
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=ap.itemsite_code).first()
#         #     sourceobj = Source.objects.filter(source_code=ap.source_code).first()

#         #     Appointment.objects.filter(pk=ap.pk).update(cust_noid=custobj,Appt_typeid=aptobj,
#         #     emp_noid=empobj,ItemSite_Codeid=siteobj,Appt_Created_Byid=fmspwobj,Source_Codeid=sourceobj)
#         #     print(ap.cust_noid,ap.Appt_typeid,ap.emp_noid,ap.Appt_Created_Byid,ap.ItemSite_Codeid,ap.Source_Codeid,"Appointment")

#         # control = ControlNo.objects.filter().order_by('-pk')
#         # for co in control:
#         #     siteobj = ItemSitelist.objects.filter(itemsite_code=co.site_code).first()
#         #     ControlNo.objects.filter(pk=co.pk).update(Site_Codeid=siteobj)
#         #     print(co.Site_Codeid,"ControlNo")  


#         result = {'status': status.HTTP_200_OK,"message":"Updated Successfully",'error': False}
#         return Response(data=result, status=status.HTTP_200_OK)


@api_view(['GET', ])
def meta_race(request):
    try:
        race_qs = Races.objects.filter(itm_isactive=True).values('itm_id', 'itm_name', 'itm_code')
        response_data = {
            "races": list(race_qs),
            "message": "Listed successfuly"
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except:
        response_data = {
            "message": "error"
        }
        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def meta_nationality(request):
    try:
        qs = Nationality.objects.filter(itm_isactive=True).values('itm_id', 'itm_name', 'itm_code')
        response_data = {
            "nationalities": list(qs),
            "message": "Listed successfuly"
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except:
        response_data = {
            "message": "error"
        }
        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def meta_religious(request):
    try:
        qs = Religious.objects.filter(itm_isactive=True).values('itm_id', 'itm_name', 'itm_code')
        response_data = {
            "religions": list(qs),
            "message": "Listed successfuly"
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except:
        response_data = {
            "message": "error"
        }
        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def meta_country(request):
    try:
        qs = Country.objects.filter(itm_isactive=True).values('itm_id', 'itm_desc', 'itm_code', 'phonecode')
        response_data = {
            "countries": list(qs),
            "message": "Listed successfuly"
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except:
        response_data = {
            "message": "error"
        }
        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)


class MonthlyWorkSchedule(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        # result = {'status': state, "message": message, 'error': error, 'data': data}
        try:
            emp_obj = Employee.objects.get(emp_code=request.GET.get("emp_code"))
        except:
            return general_error_response("Invalid emp_code")

        try:
            # year = int(request.GET.get("year"))
            # month = int(request.GET.get("month"))
            # start_date = datetime.datetime(year=year,month=month,day=1)
            # end_date = datetime.datetime(year=year,month=month+1,day=1)
            # change to date range
            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        except Exception as e:
            print(e)
            return general_error_response("Invalid start and end date format")
        monthlySchedule = []

        # if site_code hasn't in request, get month schedule by default site_code
        site_code = request.GET.get("site_code", emp_obj.site_code)

        try:
            for date in date_range:
                month_schedule = ScheduleMonth.objects.filter(emp_code=emp_obj.emp_code,
                                                              site_code=site_code,
                                                              itm_date=date,
                                                              ).first()
                if not month_schedule:
                    month_schedule = ScheduleMonth.objects.create(emp_code=request.GET.get("emp_code"),
                                                                  site_code=site_code,
                                                                  itm_date=date, )

                monthlySchedule.append({
                    "id": month_schedule.id,
                    "emp_code": month_schedule.emp_code,
                    "itm_date": month_schedule.itm_date,
                    "itm_type": month_schedule.itm_type,

                })
        except Exception as e:
            return general_error_response(e)

        work_schedule = Workschedule.objects.filter(emp_code=emp_obj.emp_code, is_alternative=False).first()
        if work_schedule is None:
            work_schedule = Workschedule.objects.create(emp_code=emp_obj.emp_code, is_alternative=False)

        work_schedule_alt = Workschedule.objects.filter(emp_code=emp_obj.emp_code, is_alternative=True).first()
        if work_schedule_alt is None:
            work_schedule_alt = Workschedule.objects.create(emp_code=emp_obj.emp_code, is_alternative=True)

        resData = {
            "monthlySchedule": monthlySchedule,
            "weekSchedule": EmpWorkScheduleSerializer(work_schedule).data,
            "altWeekSchedule": EmpWorkScheduleSerializer(work_schedule_alt).data
        }

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        requestData = request.data

        month_schedule_list = requestData.get("monthlySchedule")

        for ms in month_schedule_list:
            try:
                h_schedule = ScheduleHour.objects.filter(itm_code=ms["itm_type"]).first()
                m_schedule = ScheduleMonth.objects.get(id=ms['id'])
                m_schedule.itm_type = ms["itm_type"]
                m_schedule.itm_Typeid = h_schedule
                m_schedule.save()
            except Exception as e:
                print(e)

        week_schedule_dict = requestData.get("weekSchedule")
        try:
            work_schedule = Workschedule.objects.get(id=week_schedule_dict['id'])
            work_schedule.monday = week_schedule_dict.get("monday")
            work_schedule.tuesday = week_schedule_dict.get("tuesday")
            work_schedule.wednesday = week_schedule_dict.get("wednesday")
            work_schedule.thursday = week_schedule_dict.get("thursday")
            work_schedule.friday = week_schedule_dict.get("friday")
            work_schedule.saturday = week_schedule_dict.get("saturday")
            work_schedule.sunday = week_schedule_dict.get("sunday")
            work_schedule.save()
        except Exception as e:
            return general_error_response(e)

        alt_week_schedule_dict = requestData.get("altWeekSchedule")
        try:
            alt_work_schedule = Workschedule.objects.get(id=alt_week_schedule_dict['id'])
            alt_work_schedule.monday = alt_week_schedule_dict.get("monday")
            alt_work_schedule.tuesday = alt_week_schedule_dict.get("tuesday")
            alt_work_schedule.wednesday = alt_week_schedule_dict.get("wednesday")
            alt_work_schedule.thursday = alt_week_schedule_dict.get("thursday")
            alt_work_schedule.friday = alt_week_schedule_dict.get("friday")
            alt_work_schedule.saturday = alt_week_schedule_dict.get("saturday")
            alt_work_schedule.sunday = alt_week_schedule_dict.get("sunday")
            alt_work_schedule.save()
        except Exception as e:
            return general_error_response(e)

        result = {'status': status.HTTP_200_OK, 'message': "update success", 'error': False}
        return Response(result, status=status.HTTP_200_OK)


class MonthlyAllSchedule(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        # result = {'status': state, "message": message, 'error': error, 'data': data}
        try:
            site = ItemSitelist.objects.get(itemsite_id=request.GET.get("site_id"))
        except Exception as e:
            print(e)
            return general_error_response("Invalid site_id format")

        try:
            year = int(request.GET.get("year"))
            month = int(request.GET.get("month"))
            start_date = datetime.datetime(year=year, month=month, day=1)
            end_date = datetime.datetime(year=year, month=month + 1, day=1)
            # change to date range
            # start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            # end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0,(end_date-start_date).days)]
        except Exception as e:
            print(e)
            return general_error_response("Invalid start and end date format")
        monthlySchedule = []

        # if site_code hasn't in request, get month schedule by default site_code
        # site_code = request.GET.get("site_code",emp_obj.site_code)

        try:
            emp_qs = Employee.objects.filter(Site_Codeid=site,emp_isactive=True)
            # todo: more filters
            full_tot = emp_qs.count()
            try:
                limit = int(request.GET.get("limit",8))
            except:
                limit = 8
            try:
                page = int(request.GET.get("page",1))
            except:
                page = 1

            paginator = Paginator(emp_qs, limit)
            total_page = paginator.num_pages

            try:
                emp_qs = paginator.page(page)
            except (EmptyPage, InvalidPage):
                emp_qs = paginator.page(total_page) # last page

            emp_schedule_list = []
            for emp in emp_qs:
                date_list = []

                for date in date_range:
                    month_schedule = ScheduleMonth.objects.filter(emp_code=emp.emp_code,
                                                                  site_code=site.itemsite_code,
                                                                  itm_date=date,
                                                                  ).first()
                    # if not month_schedule:
                    #     month_schedule = ScheduleMonth.objects.create(emp_code=emp.emp_code,
                    #                                                   site_code=site.itemsite_code,
                    #                                                   itm_date=date, )

                    date_list.append({
                        "id": month_schedule.id if month_schedule else None,
                        "date": date,
                        "itm_type": month_schedule.itm_type if month_schedule else None,
                    })
                emp_schedule_list.append({
                    "emp_name": emp.emp_name,
                    "emp_code": emp.emp_code,
                    "schedules": date_list
                })
        except Exception as e:
            return general_error_response(e)

        resData = {
            "fullSchedule": emp_schedule_list,
            "total_emp": len(emp_schedule_list),
            "total_dates": len(date_range),
            'pagination': {
                           "per_page":limit,
                           "current_page":page,
                           "total":full_tot,
                           "total_pages":total_page
            }

        }
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
        return Response(result, status=status.HTTP_200_OK)

    # def post(self, request):
    #     requestData = request.data
    #
    #     month_schedule_list = requestData.get("monthlySchedule")
    #
    #     for ms in month_schedule_list:
    #         try:
    #             h_schedule = ScheduleHour.objects.filter(itm_code=ms["itm_type"]).first()
    #             m_schedule_id = ms.get('id')
    #             if m_schedule_id:
    #                 m_schedule = ScheduleMonth.objects.get(id=ms['id'])
    #                 m_schedule.itm_type = ms["itm_type"]
    #                 m_schedule.itm_Typeid = h_schedule
    #                 m_schedule.save()
    #             else:
    #
    #                 m_schedule = ScheduleMonth.objects.create()
    #         except Exception as e:
    #             print(e)
    #
    #     week_schedule_dict = requestData.get("weekSchedule")
    #     try:
    #         work_schedule = Workschedule.objects.get(id=week_schedule_dict['id'])
    #         work_schedule.monday = week_schedule_dict.get("monday")
    #         work_schedule.tuesday = week_schedule_dict.get("tuesday")
    #         work_schedule.wednesday = week_schedule_dict.get("wednesday")
    #         work_schedule.thursday = week_schedule_dict.get("thursday")
    #         work_schedule.friday = week_schedule_dict.get("friday")
    #         work_schedule.saturday = week_schedule_dict.get("saturday")
    #         work_schedule.sunday = week_schedule_dict.get("sunday")
    #         work_schedule.save()
    #     except Exception as e:
    #         return general_error_response(e)
    #
    #     alt_week_schedule_dict = requestData.get("altWeekSchedule")
    #     try:
    #         alt_work_schedule = Workschedule.objects.get(id=alt_week_schedule_dict['id'])
    #         alt_work_schedule.monday = alt_week_schedule_dict.get("monday")
    #         alt_work_schedule.tuesday = alt_week_schedule_dict.get("tuesday")
    #         alt_work_schedule.wednesday = alt_week_schedule_dict.get("wednesday")
    #         alt_work_schedule.thursday = alt_week_schedule_dict.get("thursday")
    #         alt_work_schedule.friday = alt_week_schedule_dict.get("friday")
    #         alt_work_schedule.saturday = alt_week_schedule_dict.get("saturday")
    #         alt_work_schedule.sunday = alt_week_schedule_dict.get("sunday")
    #         alt_work_schedule.save()
    #     except Exception as e:
    #         return general_error_response(e)
    #
    #     result = {'status': status.HTTP_200_OK, 'message': "update success", 'error': False}
    #     return Response(result, status=status.HTTP_200_OK)


@api_view(['GET', ])
def schedule_hours(request):
    try:
        qs = ScheduleHour.objects.filter(itm_isactive=True).values('id', 'itm_code', 'itm_desc', 'fromtime', 'totime',
                                                                   'offday', 'itm_color', 'shortDesc')
        response_data = {
            "schedules": list(qs),
            "message": "Listed successfuly"
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except:
        response_data = {
            "message": "error"
        }
        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
def SkillsItemTypeList(request):
    try:
        qs = ItemType.objects.all().values('itm_id', 'itm_name', 'itm_removable')

        response_data = {
            "skillsTypes": list(qs),
            "message": "Listed successfuly"
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        response_data = {
            "message": "error"
        }
        return JsonResponse(response_data, status=status.HTTP_400_BAD_REQUEST)


class EmployeeSkillView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        try:
            emp_qs = Employee.objects.filter(emp_isactive=True)
            emp_type = request.GET.get("emp_type")
            item_type = request.GET.get("item_type")
            if emp_type:
                emp_qs = emp_qs.filter(EMP_TYPEid=emp_type)

            emp_list = []
            for emp in emp_qs:
                skill_qs = Skillstaff.objects.filter(staffcode=emp.emp_code)
                skills_list = []
                for sk in skill_qs:
                    itm_code = str(sk.itemcode)
                    if item_type:
                        _stock = Stock.objects.filter(item_code=itm_code, Item_Typeid=item_type)
                    else:
                        _stock = Stock.objects.filter(item_code=itm_code)
                    if _stock:
                        skills_list.append(
                            _stock.values("item_no", "item_code", "item_name", "item_type", "Item_Typeid").first())
                if skills_list:
                    emp_list.append({
                        "emp_no": emp.emp_no,
                        "emp_code": emp.emp_code,
                        "emp_type": emp.emp_type,
                        "emp_type_id": emp.EMP_TYPEid.id,
                        "staffname": emp.display_name,
                        "skills": skills_list
                    })

        except Exception as e:
            return general_error_response(e)

        responseData = {
            "data": emp_list
        }

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class CustomerFormSettingsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
            site = fmspw[0].loginsite
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "user has no site", 'error': True, "data": None}
            return Response(result, status=status.HTTP_200_OK)

        query_set = CustomerFormControl.objects.filter(isActive=True, Site_Codeid=site).order_by('order')
        serializer = CustomerFormControlSerializer(query_set, many=True)

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
        return Response(result, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            return CustomerFormControl.objects.get(id=pk)
        except CustomerFormControl.DoesNotExist:
            raise Http404

    def put(self, request):
        control_list = request.data.get("customerControlList", [])

        for control in control_list:
            cf_obj = self.get_object(control['id'])
            serializer = CustomerFormControlSerializer(cf_obj, data=control, partial=True)
            if serializer.is_valid():
                print("yes")
                serializer.save()

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, }  # "data": serializer.data}
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET', ])
def CustomerFormSettings(request):
    try:
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
        site = fmspw[0].loginsite
    except:
        result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "user has no site", 'error': True, "data": None}
        return Response(result, status=status.HTTP_200_OK)

    query_set = CustomerFormControl.objects.filter(isActive=True, Site_Codeid=site)
    serializer = CustomerFormControlSerializer(query_set, many=True)

    settings_list = serializer.data

    for _setting in settings_list:
        # if hasattr(Customer,_setting["field_name"]):
        _attr = getattr(Customer, _setting["field_name"])
        _data_type = str(type(_attr.field)).strip("<class ''>").split(".")[-1]

        _choices = None
        if _data_type == "ForeignKey":
            # Site_Codeid, Cust_sexesid(Gender), Cust_Classid(CustomerClass), Cust_Sourceid(Source) current (03/06/2020) fks.

            _related_model_class = _attr.field.related_model
            _qs = _related_model_class.objects.all()
            _isactive_fileds = [x.name for x in _related_model_class._meta.get_fields() if "isactive" in x.name]
            if len(_isactive_fileds) == 1:
                _qs = _qs.filter(**{_isactive_fileds[0]: True})
            elif len(_isactive_fileds) > 1:
                _qs = _qs.filter(**{_isactive_fileds[0]: True})
                # todo: if related model have more than one fields that contain 'isactive', filter statement should
                #       choose needed one. and should be implement logger instead print
                print(f"Warning: CustomerFormSettings, {_setting['field_name']}: {_related_model_class} "
                      f"have more than one isactive fields")
            try:
                _choices = [obj.choice_dict for obj in _qs]
            except:
                result = {'status': status.HTTP_400_BAD_REQUEST, 'message': f"{_related_model_class} has not 'choice_dict' called property", 'error': True,
                          "data": None}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)


        # elif _data_type == "ManyToManyField":
        #     # currently there aren't any ManyToManyFields in Customer model
        #     pass

        _setting["data_type"] = DYNAMIC_FIELD_CHOICES.get(_data_type, "DATA TYPE NOTE DEFINED")
        _setting["selection"] = _choices

    result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": settings_list}
    return Response(result, status=status.HTTP_200_OK)


class CustomerPlusViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Customer.objects.filter(cust_isactive=True).order_by('-pk')
    serializer_class = CustomerPlusSerializer

    # filter_backends = [DjangoFilterBackend, ]

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
        site = fmspw[0].loginsite

        queryset = Customer.objects.filter(cust_isactive=True,
                                           Site_Codeid__pk=site.pk).only('cust_isactive', 'Site_Codeid').order_by('-pk')
        if int(fmspw[0].LEVEL_ItmIDid.level_code) == 24:
            queryset = Customer.objects.filter(cust_isactive=True).only('cust_isactive').order_by('-pk')
        elif int(fmspw[0].LEVEL_ItmIDid.level_code) in [27, 31]:
            queryset = Customer.objects.filter(cust_isactive=True,
                                               Site_Codeid__pk=site.pk).only('cust_isactive', 'Site_Codeid').order_by(
                '-pk')

        q = self.request.GET.get('search', None)
        value = self.request.GET.get('sortValue', None)
        key = self.request.GET.get('sortKey', None)

        if q is not None:
            queryset = queryset.filter(Q(cust_name__icontains=q) | Q(cust_address__icontains=q)).order_by('-pk')
        elif value and key is not None:
            if value == "asc":
                if key == 'cust_name':
                    queryset = queryset.order_by('cust_name')
                elif key == 'cust_address':
                    queryset = queryset.order_by('cust_address')
            elif value == "desc":
                if key == 'cust_name':
                    queryset = queryset.order_by('-cust_name')
                elif key == 'cust_address':
                    queryset = queryset.order_by('-cust_address')

        return queryset

    def list(self, request):
        try:
            serializer_class = CustomerPlusSerializer
            queryset = self.filter_queryset(self.get_queryset())
            query_parm_dict = request.GET
            for k, v in query_parm_dict.items():
                if hasattr(Customer, k):
                    try:
                        queryset = queryset.filter(**{k: v})
                    except FieldError:
                        continue
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def create(self, request):
        try:
            state = status.HTTP_400_BAD_REQUEST
            fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
            queryset = None
            serializer_class = None
            total = None
            serializer = CustomerPlusSerializer(data=request.data, context={'request': self.request, "action": self.action})
            if serializer.is_valid():
                self.perform_create(serializer)
                site = fmspw[0].loginsite
                if not site:
                    result = {'status': status.HTTP_400_BAD_REQUEST,
                              "message": "Users Employee Site_Codeid is not mapped!!", 'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

                control_obj = ControlNo.objects.filter(control_description__iexact="VIP CODE",
                                                       Site_Codeid__pk=site.pk).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Customer Control No does not exist!!",
                              'error': True}
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)

                cus_code = str(control_obj.Site_Codeid.itemsite_code) + str(control_obj.control_no)
                gender = False
                if request.data['Cust_sexesid']:
                    gender = Gender.objects.filter(pk=request.data['Cust_sexesid'], itm_isactive=True).first()
                k = serializer.save(site_code=site.itemsite_code, cust_code=cus_code,
                                    cust_sexes=gender.itm_code if gender else None, cust_joindate=timezone.now())
                if k.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()
                state = status.HTTP_201_CREATED
                message = "Created Succesfully "
                error = False
                data = serializer.data
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_201_CREATED)

            error = True
            # print(serializer.errors,"serializer.errors")
            data = serializer.errors
            # print(data,"data")
            if 'non_field_errors' in data:
                message = data['non_field_errors'][0]
            else:
                message = "Invalid Input"
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk, cust_isactive=True)
        except Customer.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            customer = self.get_object(pk)
            serializer = CustomerPlusSerializer(customer)
            data = serializer.data
            #todo hide nirc value
            # if 'masked_nric' in data:
            #     data['cust_nric'] = data['masked_nric']
            # _nric = data.get('cust_nric',"")
            # if len(_nric) > 4:
            #     _str = '*' * (len(_nric) - 4)
            #     data['cust_nric'] = _str + _nric[-4:]

            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            customer = self.get_object(pk)
            requestData = request.data
            if requestData.get('cust_nric',"").startswith("*"):
                requestData['cust_nric'] = customer.cust_nric
                print(requestData)
            serializer = CustomerPlusSerializer(customer, data=requestData, context={'request': self.request, "action": self.action})
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            data = serializer.errors
            message = data['non_field_errors'][0]
            state = status.HTTP_204_NO_CONTENT
            error = True
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def partial_update(self, request, pk=None):
        try:
            queryset = None
            total = None
            serializer_class = None
            customer = self.get_object(pk)
            serializer = CustomerPlusSerializer(customer, data=request.data, partial=True,
                                                  context={'request': self.request,"action": self.action})
            if serializer.is_valid():
                serializer.save()
                state = status.HTTP_200_OK
                message = "Updated Succesfully"
                error = False
                data = serializer.data
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)

            state = status.HTTP_204_NO_CONTENT
            message = "Invalid Input"
            error = True
            data = serializer.errors
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
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
            instance = self.get_object(pk)
            if instance:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "You are not allowed to delete customer!!",
                          'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            try:
                self.perform_destroy(instance)
                message = "Deleted Succesfully"
                error = False
                result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                                  action=self.action)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                pass

            message = "No Content"
            error = True
            result = response(self, request, queryset, total, state, message, error, serializer_class, data,
                              action=self.action)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

    def perform_destroy(self, instance):
        instance.cust_isactive = False
        instance.save()

    @action(detail=True, methods=['GET', 'POST'], permission_classes=[IsAuthenticated & authenticated_only],
            authentication_classes=[TokenAuthentication], url_path='photoDiagnosis', url_name='photoDiagnosis')
    def photoDiagnosis(self,request,pk=None):
        site = request.GET.get("site")
        customer_obj = self.get_object(pk)
        if not site:
            fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
            site = fmspw[0].loginsite.itemsite_code
        if request.method == "GET":
            diag_qs = Diagnosis.objects.filter(site_code=site,cust_no=customer_obj)

            full_tot = diag_qs.count()
            try:
                limit = int(request.GET.get("limit", 8))
            except:
                limit = 8
            try:
                page = int(request.GET.get("page", 1))
            except:
                page = 1

            paginator = Paginator(diag_qs, limit)
            total_page = paginator.num_pages

            try:
                diag_qs = paginator.page(page)
            except (EmptyPage, InvalidPage):
                diag_qs = paginator.page(total_page)  # last page

            serializer = DiagnosisSerializer(diag_qs, many=True)

            resData = {
                'diagnosisList': serializer.data,
                'pagination': {
                    "per_page": limit,
                    "current_page": page,
                    "total": full_tot,
                    "total_pages": total_page
                }
            }
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
            return Response(result, status=status.HTTP_200_OK)
        elif request.method == "POST":
            requestData = request.POST
            requestData._mutable = True
            requestData['pic_path'] = request.FILES.get("pic_path")
            requestData['cust_no'] = pk
            requestData['site_code'] = site
            serializer = DiagnosisSerializer(data=requestData)
            if serializer.is_valid():
                serializer.save()
                result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
                return Response(result, status=status.HTTP_200_OK)
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid input", 'error': True, "data": None,
                      "error": serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET', 'POST'], permission_classes=[IsAuthenticated & authenticated_only],
            authentication_classes=[TokenAuthentication], url_path='photoDiagnosisCompare', url_name='photoDiagnosisCompare')
    def photoDiagnosisCompare(self, request, pk=None):
        site = request.GET.get("site")
        customer_obj = self.get_object(pk)
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True).first()
        if not site:
            site = fmspw.loginsite.itemsite_code
        if request.method == "GET":
            diag_qs = Diagnosis.objects.filter(site_code=site)

            compare_qs = DiagnosisCompare.objects.filter(Q(diagnosis1_id__in=diag_qs) | Q(diagnosis2_id__in=diag_qs))
            full_tot = compare_qs.count()
            try:
                limit = int(request.GET.get("limit", 8))
            except:
                limit = 8
            try:
                page = int(request.GET.get("page", 1))
            except:
                page = 1

            paginator = Paginator(compare_qs, limit)
            total_page = paginator.num_pages

            try:
                compare_qs = paginator.page(page)
            except (EmptyPage, InvalidPage):
                compare_qs = paginator.page(total_page)  # last page

            serializer = DiagnosisCompareSerializer(compare_qs, many=True)
            resData = {
                'diagnosisList': serializer.data,
                'pagination': {
                    "per_page": limit,
                    "current_page": page,
                    "total": full_tot,
                    "total_pages": total_page
                }
            }

            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
            return Response(result, status=status.HTTP_200_OK)

        if request.method == "POST":
            requestData = request.data
            compare_user = fmspw.emp_code
            requestData['compare_user'] = compare_user
            serializer = DiagnosisCompareSerializer(data=requestData)
            if serializer.is_valid():
                serializer.save()
                result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
                return Response(result, status=status.HTTP_200_OK)
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid input", 'error': True, "data": None,
                      "error": serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

class RewardPolicyViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = RewardPolicySerializer

    # filter_backends = [DjangoFilterBackend, ]

    def get_queryset(self):
        qs = RewardPolicy.objects.all()
        return qs

    def list(self, request):
        try:
            qs = RewardPolicy.objects.all()
            full_tot = qs.count()
            try:
                limit = int(request.GET.get("limit", 8))
            except:
                limit = 8
            try:
                page = int(request.GET.get("page", 1))
            except:
                page = 1

            paginator = Paginator(qs, limit)
            total_page = paginator.num_pages

            try:
                qs = paginator.page(page)
            except (EmptyPage, InvalidPage):
                qs = paginator.page(total_page)  # last page
            serializer = RewardPolicySerializer(qs, many=True)
            resData = {
                'dataList': serializer.data,
                'pagination': {
                    "per_page": limit,
                    "current_page": page,
                    "total": full_tot,
                    "total_pages": total_page
                }
            }
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
            return Response(result, status=status.HTTP_200_OK)
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "fail", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def create(self,request):
        requestData = request.data
        serializer = RewardPolicySerializer(data=requestData)

        if serializer.is_valid():
            serializer.save()
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "fail", 'error': True, "data": serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self,pk):
        try:
            return RewardPolicy.objects.get(id=pk)
        except:
            raise Http404

    def retrieve(self,request,pk=None):
        obj = self.get_object(pk)
        serializer = RewardPolicySerializer(obj)
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
        return Response(result, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        obj = self.get_object(pk)
        requestData = request.data
        serializer = RewardPolicySerializer(obj,data=requestData,partial=True)
        if serializer.is_valid():
            serializer.save()
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "fail", 'error': True, "data": serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class RedeemPolicyViewSet(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = RedeemPolicySerializer

    # filter_backends = [DjangoFilterBackend, ]

    def get_queryset(self):
        qs = RedeemPolicy.objects.all()
        return qs

    def list(self, request):
        try:
            qs = RedeemPolicy.objects.all()
            full_tot = qs.count()
            try:
                limit = int(request.GET.get("limit", 8))
            except:
                limit = 8
            try:
                page = int(request.GET.get("page", 1))
            except:
                page = 1

            paginator = Paginator(qs, limit)
            total_page = paginator.num_pages

            try:
                qs = paginator.page(page)
            except (EmptyPage, InvalidPage):
                qs = paginator.page(total_page)  # last page
            serializer = RedeemPolicySerializer(qs, many=True)
            resData = {
                'dataList': serializer.data,
                'pagination': {
                    "per_page": limit,
                    "current_page": page,
                    "total": full_tot,
                    "total_pages": total_page
                }
            }
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
            return Response(result, status=status.HTTP_200_OK)
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "fail", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def create(self,request):
        requestData = request.data
        serializer = RedeemPolicySerializer(data=requestData)

        if serializer.is_valid():
            serializer.save()
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "fail", 'error': True, "data": serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self,pk):
        try:
            return RedeemPolicy.objects.get(id=pk)
        except:
            raise Http404

    def retrieve(self,request,pk=None):
        obj = self.get_object(pk)
        serializer = RedeemPolicySerializer(obj)
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
        return Response(result, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        obj = self.get_object(pk)
        requestData = request.data
        serializer = RedeemPolicySerializer(obj,data=requestData,partial=True)
        if serializer.is_valid():
            serializer.save()
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "fail", 'error': True, "data": serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class SkillsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        _type = request.GET.get('item_type')
        if not _type:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "<query param: item_type> is required",
                      'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        try:
            item_type = ItemType.objects.get(itm_id=_type)
        except ItemType.DoesNotExist:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid item_type",
                      'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return general_error_response(e)

        qs = Stock.objects.filter(Item_Typeid=item_type, item_isactive=True)
        serializer = SkillSerializer(qs, many=True)
        resData = serializer.data
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
        return Response(result, status=status.HTTP_200_OK)


class PhotoDiagnosis(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        # fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
        # site = fmspw[0].loginsite.itemsite_code
        search_key = request.GET.get("search")
        customer_list = None
        if search_key:
            customer_list = Customer.objects.filter(Q(cust_name__icontains=search_key) |
                                                    Q(cust_code__icontains=search_key) |
                                                    Q(cust_phone1__icontains=search_key)).values('cust_no')

        site = request.GET.get("site")

        if not site:
            fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
            site = fmspw[0].loginsite.itemsite_code

        diag_qs = Diagnosis.objects.filter(site_code=site)

        if customer_list:
            diag_qs = diag_qs.filter(cust_no_id__in=customer_list)

        full_tot = diag_qs.count()
        try:
            limit = int(request.GET.get("limit", 8))
        except:
            limit = 8
        try:
            page = int(request.GET.get("page", 1))
        except:
            page = 1

        paginator = Paginator(diag_qs, limit)
        total_page = paginator.num_pages

        try:
            diag_qs = paginator.page(page)
        except (EmptyPage, InvalidPage):
            diag_qs = paginator.page(total_page)  # last page

        serializer = DiagnosisSerializer(diag_qs, many=True)

        resData = {
            'diagnosisList': serializer.data,
            'pagination': {
                "per_page": limit,
                "current_page": page,
                "total": full_tot,
                "total_pages": total_page
            }
        }
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
        return Response(result, status=status.HTTP_200_OK)

    def post(self,request):
        requestData = request.POST
        # print(requestData,request.FILES)
        requestData._mutable = True
        requestData['pic_path'] = request.FILES.get("pic_path")

        serializer = DiagnosisSerializer(data=requestData)
        if serializer.is_valid():
            serializer.save()
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid input", 'error': True, "data": None, "error": serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)



class DiagnosisCompareView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        search_key = request.GET.get("search")
        customer_list = None
        if search_key:
            customer_list = Customer.objects.filter(Q(cust_name__icontains=search_key) |
                                                    Q(cust_code__icontains=search_key) |
                                                    Q(cust_phone1__icontains=search_key)).values('cust_no')
        site = request.GET.get("site")
        if not site:
            fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
            site = fmspw[0].loginsite.itemsite_code

        diag_qs = Diagnosis.objects.filter(site_code=site)
        if customer_list:
            diag_qs = diag_qs.filter(cust_no_id__in=customer_list)

        # diag_list = diag_qs.values('sys_code')

        compare_qs = DiagnosisCompare.objects.filter(Q(diagnosis1_id__in=diag_qs) | Q(diagnosis2_id__in=diag_qs))
        full_tot = compare_qs.count()
        try:
            limit = int(request.GET.get("limit", 8))
        except:
            limit = 8
        try:
            page = int(request.GET.get("page", 1))
        except:
            page = 1

        paginator = Paginator(compare_qs, limit)
        total_page = paginator.num_pages

        try:
            compare_qs = paginator.page(page)
        except (EmptyPage, InvalidPage):
            compare_qs = paginator.page(total_page)  # last page

        serializer = DiagnosisCompareSerializer(compare_qs,many=True)
        resData = {
            'diagnosisList': serializer.data,
            'pagination': {
                "per_page": limit,
                "current_page": page,
                "total": full_tot,
                "total_pages": total_page
            }
        }

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": resData}
        return Response(result, status=status.HTTP_200_OK)

    def post(self, request):
        requestData = request.data
        fmspw = Fmspw.objects.filter(user=request.user).first()
        compare_user = fmspw.emp_code
        requestData['compare_user'] = compare_user
        serializer = DiagnosisCompareSerializer(data=requestData)
        if serializer.is_valid():
            serializer.save()
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid input", 'error': True, "data": None,
                  "error": serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)



class EmployeeSecuritySettings(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        security_qs = Securities.objects.filter(level_isactive=True)
        s_list = []
        for _s in security_qs:
            # level_list = []
            level_qs = Securitylevellist.objects.filter(level_itemid=_s.level_code)
            level_serializer = SecuritylevellistSerializer(level_qs,many=True)
            s_list.append({
                "securieties": _s.level_name,
                "code": _s.level_code,
                "levels": level_serializer.data,
            })

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": s_list}
        return Response(result, status=status.HTTP_200_OK)

    def post(self,request):
        requestData = request.data
        level_list = requestData.get("level_list",[])
        for level in level_list:
            level_obj = Securitylevellist.objects.get(id=level['id'])
            l_serializer = SecuritylevellistSerializer(level_obj,data=level,partial=True)
            if l_serializer.is_valid():
                l_serializer.save()
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid input", 'error': True,
                          "data": None,
                          "error": l_serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False}
        return Response(result, status=status.HTTP_200_OK)


@api_view(['GET', ])
def MultiLanguage(request):
    qs = Multilanguage.objects.all().values('id', 'english', 'zh_sg')
    response_data = {
        "language": list(qs),
        "message": "Listed successfuly"
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)


@api_view(['GET', ])
def EmployeeLevels(request):
    qs = Securities.objects.filter(level_isactive=True).values('level_itmid','level_name','level_description','level_code')
    response_data = {
        "language": list(qs),
        "message": "Listed successfuly"
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)


class IndividualEmpSettings(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request,emp_no):

        try:
            emp_obj = Employee.objects.get(emp_no=emp_no)
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid emp_no", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        level_code = emp_obj.LEVEL_ItmIDid.level_code
        level_qs = Securitylevellist.objects.filter(level_itemid=level_code)
        level_serializer = SecuritylevellistSerializer(level_qs, many=True)
        settings_list = level_serializer.data
        responseData = {
            "emp_no": emp_obj.emp_no,
            "emp_code": emp_obj.emp_code,
            "LEVEL_ItmIDid": level_code,
            "settings_list": settings_list
        }
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)

    def post(self,request,emp_no):
        try:
            emp_obj = Employee.objects.get(emp_no=emp_no)
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid emp_no", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        requestData = request.data
        try:
            sec_obj = Securities.objects.get(level_code=requestData['level_code'])
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid level_code", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        emp_obj.LEVEL_ItmIDid = sec_obj
        emp_obj.save()

        level_qs = Securitylevellist.objects.filter(level_itemid=sec_obj.level_code)
        level_serializer = SecuritylevellistSerializer(level_qs, many=True)
        settings_list = level_serializer.data
        responseData = {
            "emp_no": emp_obj.emp_no,
            "emp_code": emp_obj.emp_code,
            "LEVEL_ItmIDid": sec_obj.level_code,
            "settings_list": settings_list
        }
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)

        # level_list = requestData.get("level_list", [])
        # for level in level_list:
        #     level_obj = Securitylevellist.objects.get(id=level['id'])
        #     l_serializer = SecuritylevellistSerializer(level_obj, data=level, partial=True)
        #     if l_serializer.is_valid():
        #         l_serializer.save()
        #     else:
        #         result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid input", 'error': True,
        #                   "data": l_serializer.errors,
        #                   }
        #         return Response(result, status=status.HTTP_400_BAD_REQUEST)
        #
        # result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False}
        # return Response(result, status=status.HTTP_200_OK)


class DailySalesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        start = request.GET.get("start")
        end = request.GET.get("end")
        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "user must have login site", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        qs = DailysalesdataDetail.objects.filter(sitecode=site.itemsite_code).order_by('business_date')
        try:
            if start:
                qs = qs.filter(business_date__gte=datetime.datetime.strptime(start, "%Y-%m-%d"))
            if end:
                qs = qs.filter(business_date__lte=datetime.datetime.strptime(end, "%Y-%m-%d"))
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid start end date format use: YYYY-MM-DD", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        serializer = DailysalesdataDetailSerializer(qs,many=True)

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
        return Response(result, status=status.HTTP_200_OK)


class DailySalesSummeryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        start = request.GET.get("start")
        end = request.GET.get("end")
        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "user must have login site", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        qs = DailysalesdataSummary.objects.filter(sitecode=site.itemsite_code).order_by('business_date')
        try:
            if start:
                qs = qs.filter(business_date__gte=datetime.datetime.strptime(start, "%Y-%m-%d"))
            if end:
                qs = qs.filter(business_date__lte=datetime.datetime.strptime(end, "%Y-%m-%d"))
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "invalid start end date format use: YYYY-MM-DD", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        serializer = DailysalesdataSummarySerializer(qs,many=True)

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": serializer.data}
        return Response(result, status=status.HTTP_200_OK)


class MonthlySalesSummeryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):

        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "user must have login site", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        qs = DailysalesdataSummary.objects.filter(sitecode=site.itemsite_code).order_by('business_date')


        s_year = int(request.GET.get("syear"))
        e_year = int(request.GET.get("eyear"))
        s_month = int(request.GET.get("smonth"))
        e_month = int(request.GET.get("emonth"))
        start_date = datetime.datetime(year=s_year,month=s_month,day=1)
        end_date = datetime.datetime(year=e_year,month=e_month+1,day=1)

        month_list = list(rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date))

        sales_list = []

        for i, curr in enumerate(month_list):
            try:
                next = month_list[i+1] - datetime.timedelta(days=1)
                month_qs = DailysalesdataSummary.objects.filter(business_date__range=[curr, next],sitecode=site.itemsite_code)
                print([curr, next])
                # change to date range
                month_dict = month_qs.aggregate(
                    sales_gt1_withgst=Sum('sales_gt1_withgst'),
                    sales_gt1_gst=Sum('sales_gt1_gst'),
                    sales_gt1_beforegst=Sum('sales_gt1_beforegst'),
                    servicesales_gt1=Sum('servicesales_gt1'),
                    productsales_gt1=Sum('productsales_gt1'),
                    vouchersales_gt1=Sum('vouchersales_gt1'),
                    prepaidsales_gt1=Sum('prepaidsales_gt1'),
                    sales_gt2_withgst=Sum('sales_gt2_withgst'),
                    sales_gt2_gst=Sum('sales_gt2_gst'),
                    sales_gt2_beforegst=Sum('sales_gt2_beforegst'),
                    servicesales_gt2=Sum('servicesales_gt2'),
                    productsales_gt2=Sum('productsales_gt2'),
                    vouchersales_gt2=Sum('vouchersales_gt2'),
                    prepaidsales_gt2=Sum('prepaidsales_gt2'),
                    treatmentdoneqty=Sum('treatmentdoneqty'),
                    treatmentdoneamount=Sum('treatmentdoneamount'),

                )
                print(month_dict)
                month_dict['date'] = curr

                sales_list.append(month_dict)
            except IndexError:
                break
            except Exception:
                continue

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": sales_list}
        return Response(result, status=status.HTTP_200_OK)
            # start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            # end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            # date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]

class DailySalesSummeryBySiteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        # sales_setting = request.GET.get("setting","GT1")
        # if not sales_setting in ["GT1","GT2","BOTH"]:
        #     result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "settings query parameter must be GT1 or GT2 or BOTH ", 'error': True, "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
                exclude(itemsite_code__icontains="HQ").\
                values_list('itemsite_code', flat=True)

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)


        sales_qs = DailysalesdataSummary.objects.filter(sitecode__in=site_code_list,business_date__range=[start_date,end_date])

        data_list = []
        site_total_dict = {}

        for i, date in enumerate(date_range):
            row_dict = {"id":i+1 ,"date":date}
            # _amount = {"GT1":0, "GT2": 0, "BOTH": 0}
            _amount = 0
            for site in site_code_list:
                try:
                    sale_obj = sales_qs.get(sitecode=site, business_date=date)
                    # total = sale_obj.get_total_amount[sales_setting]
                    total = sale_obj.sales_gt1_withgst if sale_obj.sales_gt1_withgst else 0
                except Exception as e:
                    print(e)
                    # total = {"GT1":0, "GT2": 0, "BOTH": 0}
                    total = 0
                # _amount["GT1"] += total['GT1']
                # _amount["GT2"] += total["GT2"]
                # _amount["BOTH"] += total["BOTH"]
                _amount += total
                row_dict[site] = round(total,2)
                site_total_dict[site] = round(site_total_dict.get(site,0) + total,2)
            row_dict["total"] = round(_amount,2)
            data_list.append(row_dict)
        # data_list.append(site_total_dict)
        responseData = {"data":data_list, "chart":site_total_dict}
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class MonthlySalesSummeryBySiteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        try:
            s_year = int(request.GET.get("syear"))
            e_year = int(request.GET.get("eyear"))
            s_month = int(request.GET.get("smonth"))
            e_month = int(request.GET.get("emonth"))
            start_date = datetime.datetime(year=s_year, month=s_month, day=1)
            end_date = datetime.datetime(year=e_year, month=e_month + 1, day=1)

            month_list = list(rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date))
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "syear, eyear, smonth and emonth query parameters are mandatory.",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
                exclude(itemsite_code__icontains="HQ").\
                values_list('itemsite_code', flat=True)

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)


        sales_qs = DailysalesdataSummary.objects.filter(sitecode__in=site_code_list,business_date__range=[start_date,end_date])
        data_list = []
        site_total_dict = {}
        for i, curr_month in enumerate(month_list):
            row_dict = {'id':i+1, 'month':curr_month.strftime("%b, %Y")}
            _amount = 0
            try:
                for site in site_code_list:
                    next_month = month_list[i+1]
                    _tot = sales_qs.filter(business_date__range=[curr_month, next_month],sitecode=site).aggregate(Sum('sales_gt1_withgst'))
                    total = _tot['sales_gt1_withgst__sum'] if type(_tot['sales_gt1_withgst__sum']) == float else 0
                    row_dict[site] = round(total,2)
                    _amount += total
                    site_total_dict[site] = round(site_total_dict.get(site, 0) + total, 2)
            except IndexError:
                continue
            row_dict['total'] = _amount
            data_list.append(row_dict)
            responseData = {"data": data_list, "chart": site_total_dict}
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class DailySalesSummeryByConsultantView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):

        try:
            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
                exclude(itemsite_code__icontains="HQ").\
                values_list('itemsite_code', flat=True)

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)
        site_code_q = ', '.join(['\''+str(code)+'\'' for code in site_code_list])
        raw_q = f"SELECT MAX(e.display_name) Consultant, " \
                        f"cast(SUM(pd.dt_deposit/100*ms.ratio) AS decimal(9,2)) amount, " \
                        f"pd.ItemSite_Code AS siteCode, MAX(e.emp_name) FullName " \
                f"FROM pos_daud pd " \
                f"INNER JOIN multistaff ms ON pd.sa_transacno = ms.sa_transacno and pd.dt_lineno = ms.dt_lineno " \
                f"LEFT JOIN employee e on ms.emp_code = e.emp_code " \
                f"WHERE pd.ItemSite_Code IN ({site_code_q})" \
                f"AND pd.sa_date BETWEEN '{start_date}' AND '{end_date}' " \
                f"GROUP BY ms.emp_code, pd.ItemSite_Code " \
                f"ORDER BY Amount DESC"

        with connection.cursor() as cursor:
            cursor.execute(raw_q)
            raw_qs = cursor.fetchall()
            desc = cursor.description
            # responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]
            # for row in raw_qs:
            data_list = []
            site_total_dict = {}
            for i,row in enumerate(raw_qs):
                _d = dict(zip([col[0] for col in desc], row))
                _d['id'] = i+1
                data_list.append(_d)
                site_total_dict[_d['Consultant']] = round(site_total_dict.get(_d['Consultant'], 0) + _d['amount'], 2)

            responseData = {"data": data_list, "chart": site_total_dict}
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)



class ServicesByOutletView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):

        try:
            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            # site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
            #     exclude(itemsite_code__icontains="HQ").\
            #     values_list('itemsite_code', flat=True)
            site_filter = ""

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
            _site_code_q = ', '.join(['\'' + str(code) + '\'' for code in site_code_list])
            site_filter = f"and a.itemSite_code in ({_site_code_q}) "
        elif _siteGroup:
            # site_code_list = site_code_list.filter(site_group=_siteGroup)
            site_filter = f"and item_sitelist.Site_Group = {_siteGroup}"

        # site_code_q = ', '.join(['\''+str(code)+'\'' for code in site_code_list])
        raw_q = f"select a.itemSite_code as SiteCode,item_sitelist.ItemSite_Desc as Outlet,sum(a.dt_deposit) as Sales " \
                f"from pos_daud a " \
                f"inner join pos_haud ph on a.sa_transacno=ph.sa_transacno " \
                f"inner join stock on stock.item_code+'0000'=a.dt_itemno " \
                f"left join item_sitelist on item_sitelist.ItemSite_Code=a.itemSite_code " \
                f"where  a.sa_date BETWEEN '{start_date}' and '{end_date}' " \
                f"and a.Record_Detail_Type in ('SERVICE') " \
                f"and ph.Isvoid!=1 " \
                f"and stock.Item_type='SINGLE' {site_filter}" \
                f"group by a.itemSite_code,item_sitelist.ItemSite_Desc " \
                f"ORDER BY Sales DESC"
        print(raw_q)
        with connection.cursor() as cursor:
            cursor.execute(raw_q)
            raw_qs = cursor.fetchall()
            desc = cursor.description
            # responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]
            # for row in raw_qs:
            data_list = []
            site_total_dict = {}
            for i,row in enumerate(raw_qs):
                _d = dict(zip([col[0] for col in desc], row))
                _d['id'] = i +1
                data_list.append(_d)
                site_total_dict[_d['SiteCode']] = round(site_total_dict.get(_d['SiteCode'], 0) + _d['Sales'], 2)

            responseData = {"data": data_list, "chart": site_total_dict}
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def temp_login(request):
    u = User.objects.get(username="ABC")
    tokens, _ = Token.objects.get_or_create(user=u)
    if tokens:
        token = multiple_expire_handler(tokens)
    data = {}
    # is_expired, token = token_expire_handler(token)
    data["token"] = token.key
    data['salon'] = "HEALSPA"
    data['branch'] = "JY01"
    data['session_id'] = request.session.session_key
    data['role'] = "ADMINISTRATOR"


    result = {'status': status.HTTP_200_OK, "message": "Login Successful", 'error': False, 'data': data}
    return Response(result, status=status.HTTP_200_OK)


@api_view(['GET', ])
def site_group_list(request):
    qs = SiteGroup.objects.filter(is_active=True).values('id','code','description')
    response_data = {
        "groups": list(qs),
        "message": "Listed successfuly"
    }
    result = {'status': status.HTTP_200_OK, "message": "Login Successful", 'error': False, 'data': response_data}
    return Response(result, status=status.HTTP_200_OK)


class SalesSummeryByOutletView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):

        try:
            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")

        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
                exclude(itemsite_code__icontains="HQ").\
                values_list('itemsite_code', flat=True)

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        _query = f"Select pos_haud.ID, pos_haud.itemSite_code,pos_daud.dt_deposit as PrdctSales, pos_daud.record_detail_type " \
                 f"from pos_haud " \
                 f"inner join pos_daud on pos_haud.sa_transacno=pos_daud.sa_transacno " \
                 f"Where pos_haud.sa_date>='{start_date}' " \
                 f"and pos_haud.sa_date<='{end_date}' " \
                 f"and pos_haud.isVoid!=1 " \
                 f"and pos_daud.record_detail_type in ('PRODUCT','TP PRODUCT')"

        pos_haud_qs = PosHaud.objects.raw(_query)