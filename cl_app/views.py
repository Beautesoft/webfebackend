import pyotp
import time
from twilio.rest import Client
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .serializers import (SiteGroupSerializer, CatalogItemDeptSerializer, 
ItemRangeSerializer, StockSerializer, StockRetailSerializer, StockIdSerializer,
OtpRequestSerializer, OtpValidationSerializer, ResetPasswordSerializer, CustomerSignSerializer,
TreatmentAccountSerializer, TopupSerializer, TreatmentDoneSerializer, TopupproductSerializer,
TopupprepaidSerializer,TreatmentReversalSerializer,ShowBalanceSerializer,ReverseTrmtReasonSerializer,
VoidSerializer,PosDaudDetailsSerializer,VoidReasonSerializer,TreatmentAccSerializer,
DashboardSerializer,CreditNoteSerializer,ProductAccSerializer,PrepaidAccSerializer,PrepaidacSerializer,
CreditNoteAdjustSerializer,BillingSerializer,CreditNotePaySerializer,PrepaidPaySerializer,VoidListSerializer,
CartPrepaidSerializer, VoidCancelSerializer,HolditemdetailSerializer,HolditemSerializer,HolditemupdateSerializer,
TreatmentHistorySerializer,StockUsageSerializer,StockUsageProductSerializer,TreatmentUsageSerializer,
StockUsageMemoSerializer,TreatmentfaceSerializer)
from cl_table.serializers import PostaudSerializer, TmpItemHelperSerializer
from .models import (SiteGroup, ItemSitelist, ReverseTrmtReason, VoidReason,TreatmentUsage,UsageMemo,
Treatmentface,Usagelevel)
from cl_table.models import (Employee, Fmspw, ItemClass, ItemDept, ItemRange, Stock, ItemUomprice, ItemBatch, 
PackageDtl, ItemDiv, PosDaud, PosTaud, Customer, GstSetting, ControlNo, TreatmentAccount, DepositAccount, 
PrepaidAccount, Treatment,PosHaud,TmpItemHelper,Appointment,Source,PosHaud,ReverseDtl,ReverseHdr,
CreditNote,Multistaff,ItemHelper,ItemUom,Treatment_Master,Holditemdetail,PrepaidAccountCondition,
CnRefund,ItemBrand,Title,ItemBatch,Stktrn,Paytable,ItemLink,ItemStocklist)
from custom.models import ItemCart, Room, Combo_Services,VoucherRecord,PosPackagedeposit
from datetime import date, timedelta
from datetime import datetime
import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import Http404
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from custom.views import response, get_client_ip
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from Cl_beautesoft.settings import SMS_SECRET_KEY, SMS_ACCOUNT_SID, SMS_AUTH_TOKEN, SMS_SENDER
from custom.services import GeneratePDF
from .permissions import authenticated_only
from rest_framework.decorators import action
from cl_table.views import get_in_val
from rest_framework import generics
from django.db.models import Sum
from rest_framework import exceptions
from django.shortcuts import get_object_or_404
from custom.serializers import ComboServicesSerializer
from .utils import general_error_response
from django.template.loader import get_template
from Cl_beautesoft.settings import BASE_DIR
from fpdf import FPDF 
from pyvirtualdisplay import Display
import pdfkit
import os
import math
import os.path
from Cl_beautesoft import settings
from django.template.defaulttags import register
from dateutil.relativedelta import relativedelta
import random
from django.db.models import Count

type_ex = ['VT-Deposit','VT-Top Up','VT-Sales']
type_tx = ['Deposit','Top Up','Sales']
# Create your views here.

class SalonViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = SiteGroup.objects.filter(is_active=True).order_by('-id')
    serializer_class = SiteGroupSerializer


    def get_queryset(self):
        queryset = SiteGroup.objects.filter(is_active=True).order_by('-id')
        q = self.request.GET.get('search',None)
        value = self.request.GET.get('sortValue',None)
        key = self.request.GET.get('sortKey',None)

        if q is not None:
            queryset = SiteGroup.objects.filter(is_active=True,description__icontains=q).order_by('-id')
        elif value and key is not None:
            if value == "asc":
                if key == 'description':
                    queryset = SiteGroup.objects.filter(is_active=True).order_by('description')
            elif value == "desc":
                if key == 'description':
                    queryset = SiteGroup.objects.filter(is_active=True).order_by('-description')

        return queryset

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Successfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)         
   
    # @authenticated_only
    def create(self, request):
        queryset = None
        serializer_class = None
        total = None
        serializer = self.get_serializer(data=request.data)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        if serializer.is_valid():
            self.perform_create(serializer)
            control_obj = ControlNo.objects.filter(control_description__icontains="SiteGroup",Site_Codeid__id=site.id).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
                
            code = str(control_obj.control_no)
            k = serializer.save(code=code)
            if k.id:
                control_obj.control_no = int(control_obj.control_no) + 1
                control_obj.save()

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
            return SiteGroup.objects.get(pk=pk,is_active=True)
        except SiteGroup.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        queryset = None
        total = None
        serializer_class = None
        site_group = self.get_object(pk)
        serializer = SiteGroupSerializer(site_group)
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
        site_group = self.get_object(pk)
        serializer = SiteGroupSerializer(site_group, data=request.data)
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
        return Response(serializer.errors, status=status.HTTP_200_OK)
    

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

        message = "No Content"
        error = True
        result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
        return Response(result,status=status.HTTP_200_OK)  

    def perform_destroy(self, instance):
        instance.is_active = False
        site = ItemSitelist.objects.filter(Site_Groupid=instance).update(Site_Groupid=None)
        instance.save()   


class CatalogItemDeptViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CatalogItemDeptSerializer

    def list(self, request):
        if not request.GET.get('Item_Dept', None) is None:
            print(request.GET.get('Item_Deptid',None),"dept")
            if request.GET.get('Item_Dept', None) == 'SERVICE':
                queryset = ItemDept.objects.filter(is_service=True, itm_status=True).order_by('itm_seq')
            elif request.GET.get('Item_Dept', None) == 'PACKAGE':
                queryset = ItemDept.objects.filter(is_service=True, itm_status=True).order_by('itm_seq')
            elif request.GET.get('Item_Dept', None) == 'RETAIL':
                queryset = ItemBrand.objects.filter(retail_product_brand=True, itm_status=True).order_by('itm_seq')
            elif request.GET.get('Item_Dept', None) == 'PREPAID':
                queryset = ItemBrand.objects.filter(prepaid_brand=True, itm_status=True).order_by('itm_seq')
            elif request.GET.get('Item_Dept', None) == 'VOUCHER':
                queryset = ItemBrand.objects.filter(voucher_brand=True, itm_status=True).order_by('itm_seq')
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Dept id does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Dept id does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            return ItemDept.objects.get(pk=pk,itm_status=True)
        except ItemDept.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        itemdept = self.get_object(pk)
        serializer = CatalogItemDeptSerializer(itemdept)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  serializer.data}
        return Response(result, status=status.HTTP_200_OK)


class CatalogItemRangeViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ItemRangeSerializer

    def list(self, request):
        if not request.GET.get('Item_Deptid',None) is None:
            print(request.GET.get('Item_Deptid',None),"range")
            item_id = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), itm_status=True).first() 
            if item_id:
                queryset = ItemRange.objects.filter(itm_dept=item_id.itm_code, isservice=True).order_by('pk')
            if item_id is None:
                branditem_id = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), itm_status=True).first()
                if branditem_id:
                    queryset = ItemRange.objects.filter(itm_brand=branditem_id.itm_code, isproduct=True).order_by('pk')
            if not item_id and not branditem_id:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)


class ServiceStockViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    def list(self, request):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        # print(site,"site")
        # if site.itemsite_code == "KL":
        #    queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_div="3", item_no__gte=13160).order_by('pk')
        #else:
        queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_div="3").order_by('item_name')

        # queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_div="3").order_by('pk')
        if request.GET.get('Item_Deptid',None):
            if not request.GET.get('Item_Deptid',None) is None:
                item_dept = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), is_service=True, itm_status=True).first()
                if not item_dept:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                # if site.itemsite_code == "KL":
                #    queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_dept=item_dept.itm_code, item_no__gte=13160).order_by('pk')
                #else:
                queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_dept=item_dept.itm_code).order_by('item_name')
            # else:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        if request.GET.get('Item_Rangeid',None):
            if not request.GET.get('Item_Rangeid',None) is None:
                if request.GET.get('Item_Rangeid',None):
                    itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isservice=True).first()
                    if not itemrange:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    #if site.itemsite_code == "KL":
                    #    queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_range=itemrange.itm_code, item_no__gte=13160).order_by('pk')
                    #else:
                    queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_range=itemrange.itm_code).order_by('item_name')
                else:
                    #if site.itemsite_code == "KL":
                    # queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_dept=item_dept.itm_code, item_no__gte=13160).order_by('pk')
                    #else:
                    queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_dept=item_dept.itm_code).order_by('item_name')
        
        if request.GET.get('search',None):
            if not request.GET.get('search',None) is None:
                queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))

        # querysetsite = ItemStocklist.objects.filter(itemstocklist_status=True,itemsite_code=site.itemsite_code).order_by('pk')

        serializer_class =  StockSerializer
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        for dat in d:
            dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
        return Response(result, status=status.HTTP_200_OK)   

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True, item_type="SINGLE")
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        stock = self.get_object(pk)
        serializer = StockSerializer(stock)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        v = result.get('data')
        if v['Stock_PIC']:
            v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
        if v['item_price']:
            v['item_price'] = "{:.2f}".format(float(v['item_price']))
        return Response(result, status=status.HTTP_200_OK)


class RetailStockListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockRetailSerializer

    def list(self, request):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        #if site.itemsite_code == "KL":
        #   queryset = Stock.objects.filter(item_isactive=True, item_div="1",item_no__gte=13160).order_by('pk')
        #else:
        queryset = Stock.objects.filter(item_isactive=True, item_div="1").order_by('item_name')

        # queryset = Stock.objects.filter(item_isactive=True, item_div="1").order_by('pk')
        if request.GET.get('Item_Deptid',None):
            if not request.GET.get('Item_Deptid',None) is None:
                item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None),retail_product_brand=True,itm_status=True).first()
                if not item_brand:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Brand id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                # queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code, item_div=1).order_by('pk')
                #if site.itemsite_code == "KL":
                #   queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code, item_div=1,item_no__gte=13160).order_by('pk')
                #else:
                queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code, item_div=1).order_by('item_name')

            # else:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        if request.GET.get('Item_Rangeid',None):
            if not request.GET.get('Item_Rangeid',None) is None:
                if request.GET.get('Item_Rangeid',None):
                    itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isproduct=True).first()
                    if not itemrange:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    #if site.itemsite_code == "KL":
                    #    queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code,item_no__gte=13160).order_by('item_name')
                    #else:
                    queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code).order_by('item_name')
                else:
                    #if site.itemsite_code == "KL":
                    #    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code,item_no__gte=13160).order_by('item_name')
                    #else:
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('item_name')
        
        if request.GET.get('search',None):
            if not request.GET.get('search',None) is None:
                queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))

        serializer_class =  StockRetailSerializer
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        lst = []
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        for dat in d:
            q = dict(dat)
            uomlst = []
            stock = Stock.objects.filter(item_isactive=True, pk=q['id']).first()
            itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code).order_by('id')
            
            for i in itemuomprice:
                itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                itembatch = ItemBatch.objects.filter(item_code=stock.item_code,site_code=site.itemsite_code,uom=i.item_uom).order_by('id').first()
                itemuom_id = None; itemuom_desc = None; itemqty = 0
                if itembatch:
                    itemqty = itembatch.qty

                if itemuom:
                    itemuom_id = int(itemuom.id)
                    itemuom_desc = itemuom.uom_desc
                uom = {
                        "itemuomprice_id": int(i.id),
                        "item_uom": i.item_uom,
                        "uom_desc": i.uom_desc,
                        "item_price": "{:.2f}".format(float(i.item_price)),
                        "itemuom_id": itemuom_id, 
                        "qty": itemqty, 
                        "itemuom_desc" : itemuom_desc}
                uomlst.append(uom)

            val = {'uomprice': uomlst}  
            q.update(val) 
            lst.append(q)
            v['dataList'] = lst    
        return Response(result, status=status.HTTP_200_OK)   

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        ip = get_client_ip(request)
        stock = self.get_object(pk)
        serializer = StockRetailSerializer(stock)
        uomlst = []; uom = {}
        itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code)
        for i in itemuomprice:
            itemuom = ItemUom.objects.filter(uom_isactive=True,uom_desc=i.uom_desc).order_by('id').first()
            uom = {
                    "itemuomprice_id": int(i.id),
                    "item_uom": i.item_uom,
                    "uom_desc": i.uom_desc,
                    "item_price": "{:.2f}".format(float(i.item_price)),
                    "itemuom_id": int(itemuom.id), 
                    "itemuom_desc" : itemuom.uom_desc}
            uomlst.append(uom)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data, 'Item_Price': uomlst}
        v = result.get('data')
        q = dict(v)
        if v['Stock_PIC']:
            v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
        val = {'uomprice': uomlst}  
        q.update(val) 
        result['data'] = q       
        return Response(result, status=status.HTTP_200_OK)

    # def create(self, request):
    #     if self.request.GET.get('cust_id',None) is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer id!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
    #     cust_id = Customer.objects.filter(pk=self.request.GET.get('cust_id',None)).last()

    #     if self.request.GET.get('stock_id',None) is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Stock id!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 
    #     stock_id = Stock.objects.filter(pk=self.request.GET.get('stock_id',None)).last() 
    
    #     if self.request.GET.get('uom_id',None) is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give uom id!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
    #     uom_id = ItemUomprice.objects.filter(pk=self.request.GET.get('uom_id',None)).last()

    #     item_uom = self.request.GET.get('item_uom',None)
    #     if item_uom is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give item uom!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

    #     item_price = self.request.GET.get('item_price',None)
    #     if item_price is None:
    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give item price!!",'error': True} 
    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

    #     temp_uomprice = TempUomPrice.objects.create(Cust_Codeid=cust_id,Item_Codeid=stock_id,Item_UOMid=uom_id,
    #                         item_uom=item_uom,item_price=item_price)
    #     if temp_uomprice:
    #         result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False}
    #     else:
    #         result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to create ", 'error': False}
    #     return Response(data=result, status=status.HTTP_200_OK)


class PackageStockViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    def list(self, request):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        #if site.itemsite_code == "KL":
        #   queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_div="3",item_no__gte=13160).order_by('pk')
        #else:
        queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_div="3").order_by('item_name')

        # queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_div="3").order_by('pk')
        if request.GET.get('Item_Deptid',None):
            if not request.GET.get('Item_Deptid',None) is None:
                item_dept = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), is_service=True, itm_status=True).first()
                if not item_dept:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                #if site.itemsite_code == "KL":
                #    queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code,item_no__gte=13160).order_by('pk')
                #else:
                queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code).order_by('item_name')
            # else:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        if request.GET.get('Item_Rangeid',None):
            if not request.GET.get('Item_Rangeid',None) is None:
                if request.GET.get('Item_Rangeid',None):
                    itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isservice=True).first()
                    if not itemrange:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    #if site.itemsite_code == "KL":
                    #queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_range=itemrange.itm_code,item_no__gte=13160).order_by('pk')
                    #else:
                    queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_range=itemrange.itm_code).order_by('item_name')
                else:
                    #if site.itemsite_code == "KL":
                    #    queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code,item_no__gte=13160).order_by('pk')
                    #else:
                    queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code).order_by('item_name')
        
        if request.GET.get('search',None):
            if not request.GET.get('search',None) is None:
                queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))

        serializer_class =  StockSerializer
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        for dat in d:
            dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
        return Response(result, status=status.HTTP_200_OK)      

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True, item_type="PACKAGE")
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        stock = self.get_object(pk)
        serializer = StockSerializer(stock)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        v = result.get('data')
        if v['Stock_PIC']:
            v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
        if v['item_price']:
            v['item_price'] = "{:.2f}".format(float(v['item_price']))
        return Response(result, status=status.HTTP_200_OK)


class PackageDtlViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockIdSerializer

    def list(self, request):
        stock = Stock.objects.filter(pk=request.GET.get('stock_id',None), item_isactive=True)
        if not stock:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock Id does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        for s in stock:     
            if s.Stock_PIC:   
                image = {"STOCK_PIC" : str("http://"+request.META['HTTP_HOST'])+str(s.Stock_PIC.url)}
            else:
                image = None
            detail = []; package = {}
            package_dtl = PackageDtl.objects.filter(package_code=s.item_code)
            if package_dtl:
                for p in package_dtl:
                    package = {
                        "stock_id": s.pk,
                        "id": p.id,
                        "quantity": p.qty,
                        "Description": p.description}
                    detail.append(package)
                package_data = {"package_description": detail,
                                "image" : image}
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': package_data }
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)


class PrepaidStockViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    def list(self, request):
        queryset = Stock.objects.filter(item_isactive=True, item_div="5").order_by('item_name')
        if request.GET.get('Item_Deptid',None):
            if not request.GET.get('Item_Deptid',None) is None:
                item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), prepaid_brand=True).first()
                if not item_brand:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('item_name')
            # else:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        if request.GET.get('Item_Rangeid',None):
            if not request.GET.get('Item_Rangeid',None) is None:
                if request.GET.get('Item_Rangeid',None):
                    itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isprepaid=True).first()
                    if not itemrange:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code).order_by('item_name')
                else:
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('item_name')

        if request.GET.get('search',None):
            if not request.GET.get('search',None) is None:
                queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))
         
        serializer_class =  StockSerializer
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        for dat in d:
            dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
        return Response(result, status=status.HTTP_200_OK)   

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        stock = self.get_object(pk)
        serializer = StockSerializer(stock)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        v = result.get('data')
        if v['Stock_PIC']:
            v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
        if v['item_price']:
            v['item_price'] = "{:.2f}".format(float(v['item_price']))
        return Response(result, status=status.HTTP_200_OK)


class VoucherStockViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    def list(self, request):
        queryset = Stock.objects.filter(item_isactive=True,  item_div="4").order_by('item_name')

        if request.GET.get('Item_Deptid',None):
            if not request.GET.get('Item_Deptid',None) is None:
                item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), voucher_brand=True).first()
                if not item_brand:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('item_name')

            # else:
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        if request.GET.get('Item_Rangeid',None):
            if not request.GET.get('Item_Rangeid',None) is None:
                if request.GET.get('Item_Rangeid',None):
                    itemrange = ItemRange.objects.filter(pk=request.GET.get('Item_Rangeid',None), isvoucher=True).first()
                    if not itemrange:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Range Id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code).order_by('item_name')
                else:
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('item_name')
        
        if request.GET.get('search',None):
            if not request.GET.get('search',None) is None:
                queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)) | Q(item_desc__icontains=request.GET.get('search',None)))

        serializer_class =  StockSerializer
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        for dat in d:
            dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
        return Response(result, status=status.HTTP_200_OK)   

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        stock = self.get_object(pk)
        serializer = StockSerializer(stock)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        v = result.get('data')
        if v['Stock_PIC']:
            v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
        if v['item_price']:
            v['item_price'] = "{:.2f}".format(float(v['item_price']))
        return Response(result, status=status.HTTP_200_OK)


class CatalogSearchViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    def get_queryset(self):
        q = self.request.GET.get('search',None)
        if q:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            # if site.itemsite_code == "KL":
            #     queryset = Stock.objects.filter(item_isactive=True,item_no__gte=13160).order_by('pk')
            #else:
            queryset = Stock.objects.filter(~Q(item_div="2"), item_isactive=True).order_by('item_name')

            # queryset = Stock.objects.filter(item_isactive=True).order_by('pk')
            queryset = queryset.filter(Q(item_name__icontains=q) | Q(item_desc__icontains=q))
        else:
            queryset = Stock.objects.none()
        return queryset
                        
    def list(self, request, *args, **kwargs):
        serializer_class = StockSerializer
        queryset = self.filter_queryset(self.get_queryset())
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = []
        result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        # for dat in d:
        #     dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
        # return Response(result, status=status.HTTP_200_OK)            

        # v = result.get('data')
        # d = v.get("dataList")
        lst = []
        # print(self.request.user,"usr")
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        for dat in d:
            q = dict(dat)
            if q['item_div'] != "1":
                dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
                return Response(result, status=status.HTTP_200_OK)            

            uomlst = []
            stock = Stock.objects.filter(item_isactive=True, pk=q['id']).first()
            itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code).order_by('id')
            print(site,"usr")
            
            for i in itemuomprice:
                itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                itembatch = ItemBatch.objects.filter(item_code=stock.item_code,site_code=site.itemsite_code,uom=i.item_uom).order_by('id').first()
                itemuom_id = None; itemuom_desc = None; itemqty = 0
                if itembatch:
                    itemqty = itembatch.qty

                if itemuom:
                    itemuom_id = int(itemuom.id)
                    itemuom_desc = itemuom.uom_desc
                uom = {
                        "itemuomprice_id": int(i.id),
                        "item_uom": i.item_uom,
                        "uom_desc": i.uom_desc,
                        "item_price": "{:.2f}".format(float(i.item_price)),
                        "itemuom_id": itemuom_id, 
                        "qty": itemqty, 
                        "itemuom_desc" : itemuom_desc}
                uomlst.append(uom)

            val = {'uomprice': uomlst}  
            q.update(val) 
            lst.append(q)
            v['dataList'] = lst    
        return Response(result, status=status.HTTP_200_OK)   

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        stock = self.get_object(pk)
        serializer = StockSerializer(stock)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        v = result.get('data')
        if v['Stock_PIC']:
            v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
        if v['item_price']:
            v['item_price'] = "{:.2f}".format(float(v['item_price']))

        return Response(result, status=status.HTTP_200_OK)

class CatalogFavoritesViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def get_queryset(self):
        today = timezone.now().date()
        month = today.month
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        daud_ids = PosDaud.objects.filter(ItemSite_Codeid__pk=site.pk,created_at__date__month=month,
        dt_qty__gt = 0,dt_status='SA').only('itemsite_code','created_at','dt_qty','dt_status').order_by('-pk')
        pro_lst = []
        for d in daud_ids:
            daudids = PosDaud.objects.filter(ItemSite_Codeid__pk=site.pk,created_at__date__month=month,
            dt_itemnoid=d.dt_itemnoid,dt_qty__gt = 0,dt_status='SA').only('itemsite_code','created_at','dt_itemnoid','dt_qty','dt_status').aggregate(Sum('dt_qty'))
            qdaudids = PosDaud.objects.filter(ItemSite_Codeid__pk=site.pk,created_at__date__month=month,
            dt_itemnoid=d.dt_itemnoid,dt_qty__gt = 0,dt_status='SA').only('itemsite_code','created_at','dt_itemnoid','dt_qty','dt_status').order_by('-pk')[:1]
           
            #client qty > 10 need to change later
            if float(daudids['dt_qty__sum']) > 1:
                if d.dt_itemnoid.pk not in pro_lst:
                    pro_lst.append(d.dt_itemnoid.pk)
        
        if pro_lst != []:
            queryset = Stock.objects.filter(pk__in=pro_lst,item_isactive=True).order_by('pk')
        else:
            queryset = Stock.objects.none()
        return queryset
                        
    def list(self, request, *args, **kwargs):
        serializer_class = StockSerializer
        queryset = self.filter_queryset(self.get_queryset())
        total = len(queryset)
        state = status.HTTP_200_OK
        message = "Listed Succesfully"
        error = False
        data = None
        result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
        v = result.get('data')
        d = v.get("dataList")
        for dat in d:
            dat["item_price"] = "{:.2f}".format(float(dat['item_price']))
        return Response(result, status=status.HTTP_200_OK)            

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        stock = self.get_object(pk)
        serializer = StockSerializer(stock)
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        v = result.get('data')
        if v['Stock_PIC']:
            v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
        if v['item_price']:
            v['item_price'] = "{:.2f}".format(float(v['item_price']))
        return Response(result, status=status.HTTP_200_OK)

        

class SalonProductSearchViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = StockSerializer

    def get_queryset(self):
        q = self.request.GET.get('search',None)
        if q is not None:
            itm_div = ItemDiv.objects.filter(itm_isactive=True, itm_code=2, itm_desc="SALON PRODUCT").first()
            queryset = Stock.objects.filter(item_isactive=True, Item_Divid=itm_div).filter(Q(item_name__icontains=q) | Q(item_desc__icontains=q)).order_by('pk')
        else:
            queryset = Stock.objects.none()
        return queryset
                        
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
        v = result.get('data')
        for i in v:
            i["item_price"] = "{:.2f}".format(float(i['item_price']))
        return Response(result, status=status.HTTP_200_OK)            


class ForgotPswdRequestOtpAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OtpRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        emp_name = request_data['emp_name']
        employee = Employee.objects.get(emp_name=emp_name)
        fmspw = Fmspw.objects.get(Emp_Codeid=employee, pw_isactive=True)
        if fmspw:
            totp = pyotp.TOTP(SMS_SECRET_KEY)
            otp = totp.now()
            employee.otp = otp
            employee.save()
            client = Client(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
            receiver = employee.emp_phone1
            message = client.messages.create(
                    body='Your change password request otp is {}'.format(otp),
                    from_=SMS_SENDER,
                    to=receiver
                )
            result = {'status': status.HTTP_200_OK, "message": "OTP Sended Successfully", 'error': False}
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to send OTP", 'error': False}
        return Response(data=result, status=status.HTTP_200_OK)


class ForgotPswdOtpValidationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OtpValidationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        emp_name = self.request.GET.get('emp_name',None)
        otp = request_data['otp']
        employee = Employee.objects.get(emp_name=emp_name)
        fmspw = Fmspw.objects.get(Emp_Codeid=employee, pw_isactive=True)
        if fmspw and employee.otp == otp:
            result = {'status': status.HTTP_200_OK, "message": "OTP Verified Successfully", 'error': False}
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed...! Please enter a valid OTP", 'error': False}
        return Response(data=result, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        emp_name = self.request.GET.get('emp_name',None)
        new_password = request_data['new_password']
        employee = Employee.objects.get(emp_name=emp_name)
        fmspw = Fmspw.objects.get(Emp_Codeid=employee, pw_isactive=True)
        user = User.objects.get(username=emp_name)
        if fmspw:
            fmspw.pw_password = new_password
            fmspw.save()
            user.set_password(new_password)
            user.save()
            employee.pw_password = new_password
            employee.save()
            result = {'status': status.HTTP_200_OK, "message": "Password Changed Successfully", 'error': False}
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "Failed to change Password", 'error': False}
        return Response(data=result, status=status.HTTP_200_OK)


# class UpdateStockAPIView(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#     queryset = Stock.objects.filter().order_by('-pk')
#     serializer_class = StockSerializer

#     def post(self, request):
#         queryset = Stock.objects.filter().order_by('-pk')
#         for s in queryset:
#             print(s.pk,"PK")
#             divobj = ItemDiv.objects.filter(itm_code=s.item_div).first()
#             deptobj = ItemDept.objects.filter(itm_code=s.item_dept).first()
#             classobj = ItemClass.objects.filter(itm_code=s.item_class).first()
#             rangeobj = ItemRange.objects.filter(itm_code=s.item_range).first()
#             typeobj = ItemType.objects.filter(itm_name=s.item_type).first()
#             Stock.objects.filter(pk=s.pk).update(Item_Divid=divobj,Item_Deptid=deptobj,Item_Classid=classobj,Item_Rangeid=rangeobj,Item_Typeid=typeobj) 
#             print(s.Item_Divid,s.Item_Deptid,s.Item_Classid,s.Item_Rangeid,s.Item_Typeid,"kkk")
#         return True


class ReceiptPdfSendSMSAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def post(self, request, format=None):
        if request.GET.get('sa_transacno',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give sa_transacno!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 

        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        sa_transacno = request.GET.get('sa_transacno',None)
        hdr = PosHaud.objects.filter(sa_transacno=sa_transacno,
        ItemSite_Codeid__pk=site.pk).order_by("pk")
        if not hdr:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Sa Transacno Does not exist in Poshaud!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

        pdf_link = GeneratePDF(self,request, sa_transacno)
        if not pdf_link:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Pdf link not generated",'error': True}
            return Response(data=result, status=status.HTTP_200_OK)      

        Pos_daud = PosDaud.objects.filter(sa_transacno=sa_transacno,
        ItemSite_Codeid__pk=site.pk).first()
        if not Pos_daud.itemcart.cust_noid.cust_phone2:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer mobile number!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  
        
        allow_sms = Pos_daud.itemcart.cust_noid.custallowsendsms
        if allow_sms:
            cust_name = Pos_daud.itemcart.cust_noid.cust_name
            client = Client(SMS_ACCOUNT_SID, SMS_AUTH_TOKEN)
            receiver = Pos_daud.itemcart.cust_noid.cust_phone2
            try:
                message = client.messages.create(
                        body='''Dear {0},\nYour receipt bill no {1}.Please check your bill in this link {2}.\nThank You,'''.format(cust_name,sa_transacno,pdf_link),
                        from_=SMS_SENDER,
                        to=receiver
                    )

                result = {'status': status.HTTP_200_OK,"message":"SMS sent succesfully",'error': False}
            except Exception as e:
                invalid_message = str(e)
                return general_error_response(invalid_message)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "Customer doesn't wish to send SMS", 'error': False}
        return Response(data=result, status=status.HTTP_200_OK)


class CustomerSignatureAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSignSerializer

    def post(self, request):
        cust_code = self.request.GET.get('cust_code',None)
        cust_obj = Customer.objects.filter(cust_code=cust_code,cust_isactive=True)
        if not cust_obj:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer code!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)  

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_data = serializer.validated_data
        
        customer = Customer.objects.get(cust_code=cust_code,cust_isactive=True)
        customersign = request_data['customersign']
        
        if customer and customersign is not None:
            customer.customersign = bytes(customersign, encoding='utf8')
            customer.save()
            result = {'status': status.HTTP_200_OK, "message": "Customer Signature updated Successfully", 'error': False}
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "Failed to update customer signature", 'error': False}
        return Response(data=result, status=status.HTTP_200_OK)

class TopupViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TreatmentAccountSerializer

    def list(self, request):
        cust_id = self.request.GET.get('cust_id',None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
        if cust_obj is None:
            result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
            return Response(data=result, status=status.HTTP_200_OK)  
 
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
        # queryset = TreatmentAccount.objects.filter(Cust_Codeid=cust_id, Site_Codeid=site, type='Deposit', outstanding__gt = 0).order_by('pk')
        queryset = TreatmentAccount.objects.filter(Cust_Codeid=cust_id, type='Deposit', outstanding__gt = 0).order_by('pk')
        if queryset:
            sum = 0; lst = []
            for q in queryset:
                #type__in=('Deposit', 'Top Up')
                # accids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                # treatment_parentcode=q.treatment_parentcode,Site_Codeid=site).order_by('id').first()
                # trmtobj = Treatment.objects.filter(treatment_account__pk=accids.pk,status='Open').order_by('pk').first()

                # acc_ids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                # treatment_parentcode=q.treatment_parentcode,Site_Codeid=site).order_by('id').last()
                acc_ids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                treatment_parentcode=q.treatment_parentcode).order_by('sa_date').last()
                acc = TreatmentAccount.objects.filter(pk=acc_ids.pk)
                serializer = self.get_serializer(acc, many=True)

                if acc_ids.outstanding > 0.0:
                    for data in serializer.data:
                        pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,
                        sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                        # pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                        # sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                        sum += data['outstanding']
                        if pos_haud.sa_date:
                            splt = str(pos_haud.sa_date).split(" ")
                            data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        
                        data['TreatmentAccountid'] = q.pk
                        data["pay_amount"] = None
                        if data['sa_transacno']:
                            data['sa_transacno'] = pos_haud.sa_transacno_ref 
                        if data['treatment_parentcode']:
                            data['treatment_parentcode'] = q.treatment_parentcode     
                        if data["description"]:
                            trmt = Treatment.objects.filter(treatment_account=q.pk).last()
                            if trmt:
                                data["description"] = trmt.course  
                                data['stock_id'] = trmt.Item_Codeid.pk
                        if data["balance"]:
                            data["balance"] = "{:.2f}".format(float(data['balance']))
                        else:
                            data["balance"] = "0.00"
                        if data["outstanding"]:
                            data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                        else:
                            data["outstanding"] = "0.00"    
                        lst.append(data) 
                           

            if lst != []:
                header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "{:.2f}".format(float(sum)),
                "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(sum))}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                return Response(result, status=status.HTTP_200_OK)
            else:
                header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
                "topup_amount" : "0.00","new_outstanding" : "0.00"}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,'header_data':header_data,  'data': []}
                return Response(result, status=status.HTTP_200_OK)        
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(result, status=status.HTTP_200_OK)    

        
    # def get_object(self, pk):
    #     try:
    #         return TreatmentAccount.objects.get(pk=pk)
    #     except TreatmentAccount.DoesNotExist:
    #         raise Http404

    # def retrieve(self, request, pk=None):
    #     topup = self.get_object(pk)
    #     serializer = TopupSerializer(topup)
    #     result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
    #     v = result.get('data')
    #     if v["description"]:
    #         description = Treatment.objects.filter(treatment_account=v["id"]).last()
    #         v["description"] = description.course
    #     if v["amount"]:
    #         v["amount"] = "{:.2f}".format(float(v['amount']))
    #     else:
    #         v["amount"] = "0.00"            
    #     if v["balance"]:
    #         v["balance"] = "{:.2f}".format(float(v['balance']))
    #     else:
    #         v["balance"] = "0.00"
    #     if v["outstanding"]:
    #         v["outstanding"] = "{:.2f}".format(float(v['outstanding']))
    #     else:
    #         v["outstanding"] = "0.00"    
    #     return Response(result, status=status.HTTP_200_OK)    


class TreatmentDoneViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentDoneSerializer

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def Year(self, request):
        try:
            today = timezone.now()
            year = today.year
            res = [r for r in range(2010, today.year+1)]
            res.append("All")
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': res[::-1]}
            return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       

    def list(self, request):
        # try:
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not self.request.user.is_authenticated:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            if not fmspw:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
            # status="Open").order_by('pk')
            queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open").order_by('pk')

            if request.GET.get('year',None):
                year = request.GET.get('year',None)
                if year != "All":
                    # queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
                    # status="Open", treatment_date__year=year).order_by('pk')
                    queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code,status="Open", treatment_date__year=year).order_by('pk')
                    par_lst = list(set([e.treatment_parentcode for e in queryset if e.treatment_parentcode])) 
                    id_lst = []
                    for p in par_lst:
                        # query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
                        # status="Open", treatment_date__year=year).order_by('pk').last()
                        query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code,
                        status="Open", treatment_date__year=year).order_by('pk').last()
                        id_lst.append(query.pk) 

                    # queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,site_code=site.itemsite_code, status="Open", treatment_date__year=year).order_by('pk')
                    queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,status="Open", treatment_date__year=year).order_by('pk')
        
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []
                for i in serializer.data:
                    session = 0
                    treatmentids=[]
                    splt = str(i['treatment_date']).split('T')
                    # print(i['id'],"ids")
                    trmt_obj = Treatment.objects.filter(pk=i['id']).first()
                    # tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj)
                    tmp_ids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code)
                    #reverseorder = True
                    #trmtparobj1 = Treatment.objects.filter(treatment_parentcode=i['treatment_parentcode'],status="Open").only('pk').order_by('-pk').first
                    #if trmtparobj1:
                    #    print(trmtparobj1.times,"trmtparobj1.times")
                    #    if trmtparobj1.times > 1:
                    #        reverseorder = True:
                    trmtparobj = Treatment.objects.filter(treatment_parentcode=i['treatment_parentcode'],status="Open").only('pk').order_by('pk')
                    for oneids in trmtparobj:
                        treatmentids.append(oneids.pk)
                        if oneids.helper_ids.all().exists():
                            session += 1
                    
                    # Following Monica to remove this block
                    # for emp in tmp_ids:
                    #    appt = Appointment.objects.filter(cust_no=trmt_obj.cust_code,appt_date=date.today(),
                    #    itemsite_code=fmspw[0].loginsite.itemsite_code,emp_no=emp.helper_code) 
                    #    if not appt:
                    #        # tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_code=emp.helper_code,
                    #        # site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
                    #        # tmpids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,helper_code=emp.helper_code,
                    #        # site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                    #        tmpids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,helper_code=emp.helper_code
                    #        ).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
                    #        if tmpids:
                    #            emp.delete()
                        
                        #need to uncomment later
                        # if emp.appt_fr_time and emp.appt_to_time:         
                        #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
                        #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
                        #     if appt_ids:
                        #         emp.delete()

                    for existing in trmt_obj.helper_ids.all():
                        trmt_obj.helper_ids.remove(existing) 
                    
                    #for t in TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code):
                    #    trmt_obj.helper_ids.add(t)
                    for t in TmpItemHelper.objects.filter(treatment=trmt_obj):
                        trmt_obj.helper_ids.add(t)

                    # for t in TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,site_code=site.itemsite_code):
                    #     trmt_obj.helper_ids.add(t)

                    # pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                    # sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()        

                    # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
                    # sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()

                    # if not pos_haud:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Payment not done yet!!",'error': True} 
                    #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    item_code = str(trmt_obj.item_code)
                    itm_code = item_code[:-4]
                    # print(Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk'),"sss")
                    stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()
                    if pos_haud and stockobj: 
                        # acc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
                        # site_code=site.itemsite_code).order_by('pk').first()
                        # trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=i['treatment_parentcode']).order_by('-id').first()
                        trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=i['treatment_parentcode']).order_by('-sa_date','-sa_time').first()
                        if trmtAccObj:
                            i["balance"] = trmtAccObj.balance
                            i["ar"] = trmtAccObj.outstanding
                        acc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode).order_by('pk').first()
                        i['treatment_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        # i['TreatmentAccountid'] = trmt_obj.treatment_account.pk
                        i['TreatmentAccountid'] = acc_obj.pk
                        # i['stockid'] = trmt_obj.Item_Codeid.pk
                        i['stockid'] = stockobj.pk if stockobj else ""
                        i["transacno_ref"] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                        if i["unit_amount"]:
                            i["unit_amount"] = "{:.2f}".format(float(i['unit_amount']))
                        # i["rev"] = False
                        #i["td"] = i["times"] + "/" +  i["treatment_no"]
                        i["td"] = str(len(treatmentids)) + "/" +  i["treatment_no"]
                        i["rev"] = "0/" +  i["treatment_no"]
                        #i["open"] = i["times"]
                        i["open"] = str(len(treatmentids))
                        i["session"] = session
                        # Allow Reversal in other salons for Healspa. Set False for Midyson
                        i["iscurrentloggedinsalon"] = True
                        if site.itemsite_code == acc_obj.site_code:
                            i["iscurrentloggedinsalon"] = True
                        i["limit"] = None
                        i["treatmentids"] = treatmentids
                        # print(trmt_obj.helper_ids.all().exists(), "helperids")
                        if trmt_obj.helper_ids.all().exists():
                            i["sel"] = True 
                            i["staff"] = ','.join([v.helper_id.display_name for v in trmt_obj.helper_ids.all() if v.helper_id.display_name])
                        else:    
                            i["sel"] = None 
                            i["staff"] = None
                        lst.append(i)

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst}
                return Response(data=result, status=status.HTTP_200_OK)  
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                return Response(result, status=status.HTTP_200_OK)
        # except Exception as e:
        #     invalid_message = str(e)
        #    return general_error_response(invalid_message)        
 

class OldTreatmentDoneViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TreatmentDoneSerializer

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated],
    authentication_classes=[TokenAuthentication])
    def Year(self, request):
        today = timezone.now()
        year = today.year
        res = [r for r in range(2010, today.year+1)]
        res.append("All")
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': res[::-1]}
        return Response(result, status=status.HTTP_200_OK)    

    def list(self, request):
        cust_id = self.request.GET.get('cust_id',None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
        if cust_obj is None:
            result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
            return Response(data=result, status=status.HTTP_200_OK)  

        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        # queryset = Treatment.objects.filter(Cust_Codeid=cust_obj, Site_Codeid=site, status="Open").order_by('pk')
        queryset = Treatment.objects.filter(Cust_Codeid=cust_obj, status="Open").order_by('pk')
        # print(request.GET.get('year',None),"Year")
        if request.GET.get('year',None):
            print(request.GET.get('year',None),"Year")
            year = request.GET.get('year',None)
            if year != "All":
                # queryset = Treatment.objects.filter(Cust_Codeid=cust_obj, Site_Codeid=site, status="Open", treatment_date__year=year).order_by('pk')
                queryset = Treatment.objects.filter(Cust_Codeid=cust_obj, status="Open", treatment_date__year=year).order_by('pk')
                par_lst = list(set([e.treatment_parentcode for e in queryset if e.treatment_parentcode])) 
                id_lst = []
                for p in par_lst:
                   # query = Treatment.objects.filter(treatment_parentcode=p, Cust_Codeid=cust_obj, Site_Codeid=site, status="Open", treatment_date__year=year).order_by('pk').last()
                   query = Treatment.objects.filter(treatment_parentcode=p, Cust_Codeid=cust_obj, status="Open", treatment_date__year=year).order_by('pk').last()
                   id_lst.append(query.pk) 

                # # queryset = Treatment.objects.filter(pk__in=id_lst,Cust_Codeid=cust_obj, Site_Codeid=site, status="Open", treatment_date__year=year).order_by('pk')
                queryset = Treatment.objects.filter(pk__in=id_lst,Cust_Codeid=cust_obj, status="Open", treatment_date__year=year).order_by('pk')
                print(id_lst,"id_lst")
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            lst = []
            for i in serializer.data:
                splt = str(i['treatment_date']).split('T')
                # print(splt,"splt")
                trmt_obj = Treatment.objects.filter(pk=i['id']).first()
                trmtAccObj = TreatmentAccount.objects.filter(treatment_parentcode=i['treatment_parentcode']).order_by('-id').first()
                if trmtAccObj:
                    i["balance"] = trmtAccObj.balance

                tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj)
                
                for emp in tmp_ids:
                    # appt = Appointment.objects.filter(cust_noid=trmt_obj.Cust_Codeid,appt_date=date.today(),
                    # ItemSite_Codeid=fmspw[0].loginsite,emp_no=emp.helper_code) 
                    appt = Appointment.objects.filter(cust_noid=trmt_obj.Cust_Codeid,appt_date=date.today(),emp_no=emp.helper_code) 
                    if not appt:
                        # tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_code=emp.helper_code,
                        # site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                        tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_code=emp.helper_code
                        ).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                        if tmpids:
                            emp.delete()
                    
                    #need to uncomment later
                    # if emp.appt_fr_time and emp.appt_to_time:         
                    #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
                    #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
                    #     if appt_ids:
                    #         emp.delete()

                for existing in trmt_obj.helper_ids.all():
                    trmt_obj.helper_ids.remove(existing) 

                # for t in TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code):
                for t in TmpItemHelper.objects.filter(treatment=trmt_obj):
                    trmt_obj.helper_ids.add(t)
                        
                #pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                #sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()
                pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,
                sa_transacno=i["sa_transacno"]).first()
                # if not pos_haud:
                #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Payment not done yet!!",'error': True} 
                #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if pos_haud: 
                    i['treatment_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                    i['TreatmentAccountid'] = trmt_obj.treatment_account.pk
                    i['stockid'] = trmt_obj.Item_Codeid.pk
                    i["transacno_ref"] = pos_haud.sa_transacno_ref
                    if i["unit_amount"]:
                        i["unit_amount"] = "{:.2f}".format(float(i['unit_amount']))
                    i["rev"] = False
                    i["limit"] = None
                    if trmt_obj.helper_ids.all().exists():
                        i["sel"] = True 
                        i["staff"] = ','.join([v.helper_id.emp_name for v in trmt_obj.helper_ids.all() if v.helper_id.emp_name])
                    else:    
                        i["sel"] = None 
                        i["staff"] = None
                    lst.append(i)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst}
            return Response(data=result, status=status.HTTP_200_OK)  
        else:
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(result, status=status.HTTP_200_OK)



class TrmtTmpItemHelperViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = TmpItemHelper.objects.filter().order_by('-id')
    serializer_class = TmpItemHelperSerializer

    # def get_permissions(self):
    #     if self.request.GET.get('treatmentid',None) is None:
    #         msg = {'status': status.HTTP_204_NO_CONTENT,"message":"Please give Treatment Record ID",'error': False} 
    #         raise exceptions.AuthenticationFailed(msg)
    #     else:
    #         self.permission_classes = [permissions.IsAuthenticated,]
    #         return self.permission_classes

    def list(self, request):
        #print(request,"list")

        if request.GET.get('treatmentid',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        arrtreatmentid = request.GET.get('treatmentid',None).split(',')
        # print(arrtreatmentid,"td")
        for t in arrtreatmentid:
            # trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            trmt_obj = Treatment.objects.filter(status="Open",pk=t).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
            #acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.sa_transacno,
            #treatment_parentcode=trmt_obj.treatment_parentcode,Site_Codeid=trmt_obj.Site_Codeid).order_by('id').last()
            acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.sa_transacno,
            treatment_parentcode=trmt_obj.treatment_parentcode).order_by('-sa_date','-sa_time').first()

            if acc_ids and acc_ids.balance:  
                if acc_ids.balance < trmt_obj.unit_amount:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Insufficient Amount in Treatment Account. Please Top Up!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        

            # if cart_obj.deposit < cart_obj.discount_price:
            #     msg = "Min Deposit for this treatment is SS {0} ! Treatment Done not allow.".format(str(cart_obj.discount_price))
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if trmt_obj.Item_Codeid.workcommpoints == None or trmt_obj.Item_Codeid.workcommpoints == 0.0:
                workcommpoints = 0.0
                # result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Work Point should not be None/zero value!!",'error': True} 
                # return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            else:
                workcommpoints = trmt_obj.Item_Codeid.workcommpoints
        
            stock_obj = Stock.objects.filter(pk=trmt_obj.Item_Codeid.pk,item_isactive=True).first()
            if stock_obj.srv_duration is None or stock_obj.srv_duration == 0.0:
                srvduration = 60
            else:
                srvduration = stock_obj.srv_duration

            stkduration = int(srvduration) + 30
            hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))

            # print(t,"td1")
            
            h_obj = TmpItemHelper.objects.filter(treatment=trmt_obj).first()
            value = {'Item':trmt_obj.course,'Price':"{:.2f}".format(float(trmt_obj.unit_amount)),
            'work_point':"{:.2f}".format(float(workcommpoints)),'room_id':None,'room_name':None,
            'source_id': trmt_obj.times if trmt_obj.times else "",'source_name':None,'new_remark':None,
            'times':trmt_obj.times if trmt_obj.times else "",'add_duration':hrs}
            if h_obj:
                if not h_obj.Room_Codeid is None:
                    value['room_id'] = h_obj.Room_Codeid.pk
                    value['room_name']  = h_obj.Room_Codeid.displayname
                if not h_obj.Source_Codeid is None:
                   value['source_id'] = h_obj.Source_Codeid.pk
                   value['source_name']  = h_obj.Source_Codeid.source_desc
                if not h_obj.new_remark is None:
                    value['new_remark']  = h_obj.new_remark
                if not h_obj.session is None:
                    value['session']  = h_obj.session
                if h_obj.times:
                    value['times']  = trmt_obj.times
                # if h_obj.workcommpoints:
                #    sumwp1 = TmpItemHelper.objects.filter(treatment=trmt_obj.pk).aggregate(Sum('wp1'))
                #    value['work_point'] = "{:.2f}".format(float(sumwp1['wp1__sum']))       
            # print(t,"td2")
        
        queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id')
        serializer = self.get_serializer(queryset, many=True)
        final = []
        if queryset:
            for t1 in serializer.data:
                s = dict(t1)
                s['wp1'] = "{:.2f}".format(float(s['wp1']))
                print(s,"s")
                s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
                s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
                s['add_duration'] =  get_in_val(self, s['add_duration'])
                s['session'] = "{:.2f}".format(float(s['session']))
                final.append(s)
        # else:
        #     val = {'id':None,'helper_id':None,'helper_name':None,'wp1':None,'appt_fr_time':None,
        #     'appt_to_time':None,'add_duration':None}  
        #     final.append(val)def 
      
        result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
        'value': value,'data':  final}
        return Response(data=result, status=status.HTTP_200_OK)  

    def create(self, request):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        if request.GET.get('treatmentid',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        arrtreatmentid = request.GET.get('treatmentid',None).split(',')
        # print(arrtreatmentid,"td")
        for t in arrtreatmentid:
            # print(t,"td")
            # trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            trmt_obj = Treatment.objects.filter(status="Open",pk=t).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist / not in open status!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
            item_code = str(trmt_obj.item_code)
            itm_code = item_code[:-4]
            stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()
        
            # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.treatment_account.ref_transacno,
            # treatment_parentcode=trmt_obj.treatment_account.treatment_parentcode,Site_Codeid=site,).order_by('id').last()
            acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.treatment_account.ref_transacno,
            treatment_parentcode=trmt_obj.treatment_account.treatment_parentcode).order_by('-sa_date','-sa_time').first()

            if acc_ids and acc_ids.balance:        
                if acc_ids.balance < trmt_obj.unit_amount:
                    msg = "Treatment Account Balance is SS {0} is not less than Treatment Price {1}.".format(str(acc_ids.balance),str(trmt_obj.unit_amount))
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        

            # if not request.GET.get('Room_Codeid',None) is None:
            #     room_ids = Room.objects.filter(id=request.GET.get('Room_Codeid',None),isactive=True).first()
            #     if not room_ids:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
            #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # if not request.GET.get('Source_Codeid',None) is None:
            #     source_ids = Source.objects.filter(id=request.GET.get('Source_Codeid',None),source_isactive=True).first()
            #     if not source_ids:
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Source ID does not exist!!",'error': True} 
            #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # if request.GET.get('Room_Codeid',None) is None:
            #     room_ids = None

            # if request.GET.get('Source_Codeid',None) is None:
            #     source_ids = None 

    
            if request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
                workcommpoints = 0.0
            else:
                workcommpoints = request.GET.get('workcommpoints',None)  

            tmp = []
            h_obj = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk')

            count = 1;Source_Codeid=None;Room_Codeid=None;new_remark=None;appt_fr_time=None;appt_to_time=None;add_duration=None
            session=1
            if trmt_obj.Item_Codeid.srv_duration is None or float(trmt_obj.Item_Codeid.srv_duration) == 0.0:
                stk_duration = 60
            else:
                stk_duration = stockobj.srv_duration
                # stk_duration = int(last.treatment.Item_Codeid.srv_duration)

            stkduration = int(stk_duration) + 30
            hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
            duration = hrs
            add_duration = duration

            helper_obj = Employee.objects.filter(emp_isactive=True,pk=request.data['helper_id']).first()
            if not helper_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            alemp_ids = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,
            helper_code=helper_obj.emp_code,site_code=site.itemsite_code).order_by('pk')
            if alemp_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"This Employee already selected!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
            if h_obj:
                count = int(h_obj.count()) + 1
                Source_Codeid = h_obj[0].Source_Codeid
                Room_Codeid = h_obj[0].Room_Codeid
                new_remark = h_obj[0].new_remark
                session = h_obj[0].session
                last = h_obj.last()
           
                start_time =  get_in_val(self, last.appt_to_time); endtime = None
                if start_time:
                    starttime = datetime.datetime.strptime(start_time, "%H:%M")

                    end_time = starttime + datetime.timedelta(minutes = stkduration)
                    endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                appt_fr_time = starttime if start_time else None
                appt_to_time = endtime if endtime else None
            
            # wp1 = float(workcommpoints) / float(count)
            wp11 = float(workcommpoints)
            wp12 = 0
            wp13 = 0
            wp14 = 0
            wp1 = float(workcommpoints)
            if wp1 > 0 :
                wp11 = float(workcommpoints) / float(count)
                if count == 2:
                    wp12 = float(workcommpoints) / float(count)
                if count == 3:
                    wp12 = float(workcommpoints) / float(count)
                    wp13 = float(workcommpoints) / float(count)
                if count == 4:
                    wp12 = float(workcommpoints) / float(count)
                    wp13 = float(workcommpoints) / float(count)
                    wp14 = float(workcommpoints) / float(count)
    
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
      
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                # helper_name=helper_obj.emp_name,helper_code=helper_obj.emp_code,Room_Codeid=Room_Codeid,
                temph = serializer.save(item_name=trmt_obj.Item_Codeid.item_desc,helper_id=helper_obj,
                helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,Room_Codeid=Room_Codeid,
                site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
                wp1=wp1,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,Source_Codeid=Source_Codeid,
                new_remark=new_remark,appt_fr_time=appt_fr_time,appt_to_time=appt_to_time,
                add_duration=add_duration,workcommpoints=workcommpoints,session=session)
                # trmt_obj.helper_ids.add(temph.id) 
                trmt_obj.helper_ids.add(temph.id) 
                tmp.append(temph.id)
   
                runx=1
                # for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,site_code=site.itemsite_code).order_by('pk'):
                for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk'):
                    # TmpItemHelper.objects.filter(id=h.id).update(wp1=wp1)
                    if runx == 1:
                        TmpItemHelper.objects.filter(id=h.id).update(wp1=wp11)
                    if runx == 2:
                        TmpItemHelper.objects.filter(id=h.id).update(wp1=wp12)
                    if runx == 3:
                        TmpItemHelper.objects.filter(id=h.id).update(wp1=wp13)
                    if runx == 4:
                        TmpItemHelper.objects.filter(id=h.id).update(wp1=wp14)
                    runx = runx + 1

            else:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 
                'data': serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
        if tmp != []:
            value = {'Item':trmt_obj.Item_Codeid.item_desc,'Price':"{:.2f}".format(float(trmt_obj.unit_amount)),
            'work_point':"{:.2f}".format(float(workcommpoints)),'Room':None,'Source':None,'new_remark':None,
            'times':trmt_obj.times}  
            tmp_h = TmpItemHelper.objects.filter(id__in=tmp)
            serializer_final = self.get_serializer(tmp_h, many=True)
            final = []
            for t1 in serializer_final.data:
                s = dict(t1)
                s['wp1'] = "{:.2f}".format(float(s['wp1']))
                s['appt_fr_time'] =  get_in_val(self, s['appt_fr_time'])
                s['appt_to_time'] =  get_in_val(self, s['appt_to_time'])
                s['add_duration'] =  get_in_val(self, s['add_duration'])
                # s['session'] =  s['session']
                final.append(s)
            print(final,"final")
            result = {'status': status.HTTP_201_CREATED,"message": "Created Succesfully",'error': False, 
            'value':value,'data':  final}
            return Response(result, status=status.HTTP_201_CREATED)

        result = {'status': status.HTTP_400_BAD_REQUEST,"message": "Invalid Input",'error': False, 
        'data':  serializer.errors}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    def get_object(self, pk):
        try:
            return TmpItemHelper.objects.get(pk=pk)
        except TmpItemHelper.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        print(request,"retrieve")
        queryset = TmpItemHelper.objects.filter().order_by('pk')
        tmpitm = get_object_or_404(queryset, pk=pk)
        serializer = TmpItemHelperSerializer(tmpitm)
        print(serializer.data,"serializer.data")
        result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
        'data':  serializer.data}
        return Response(data=result, status=status.HTTP_200_OK)  

    
    def partial_update(self, request, pk=None):
        # print(request,"partial_update")
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        if request.GET.get('Room_Codeid',None):
            room_ids = Room.objects.filter(id=request.GET.get('Room_Codeid',None),isactive=True).first()
            if not room_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        source_ids = None 
        room_ids = None
        # if request.GET.get('Source_Codeid',None):
        # #    print(request.GET.get('Source_Codeid',None),"source")
        # #    source_ids = Source.objects.filter(id=request.GET.get('Source_Codeid',None),source_isactive=True).first()
        #    source_ids = Source.objects.filter(id=request.GET.get('Source_Codeid',None)).first()
        #     if not source_ids:
        #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Source ID does not exist!!",'error': True} 
        #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        # if request.GET.get('Room_Codeid',None) is None or request.GET.get('Room_Codeid',None) == "null":
        if not request.GET.get('Room_Codeid',None):
            room_ids = None

        # if request.GET.get('Source_Codeid',None) is None or request.GET.get('Source_Codeid',None) == "null":
        # if not request.GET.get('Source_Codeid',None):     
        #     source_ids = None 

        if request.GET.get('workcommpoints',None) is None or float(request.GET.get('workcommpoints',None)) == 0.0:
            workcommpoints = 0.0
        else:
            workcommpoints = request.GET.get('workcommpoints',None)  

        tmpobj = self.get_object(pk)
        # appt = Appointment.objects.filter(cust_noid=tmpobj.treatment.Cust_Codeid,appt_date=date.today(),
        # ItemSite_Codeid=site)    
        # if not appt:
        #     if (not 'appt_fr_time' in request.data or str(request.data['appt_fr_time']) is None) and (not 'add_duration' in request.data or str(request.data['add_duration']) is None):
        #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment is not available today so please give appointment details",'error': True} 
        #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(tmpobj, data=request.data, partial=True)
        if serializer.is_valid():
            if ('appt_fr_time' in request.data and not request.data['appt_fr_time'] == None):
                if ('add_duration' in request.data and not request.data['add_duration'] == None):
                    if tmpobj.treatment.Item_Codeid.srv_duration is None or float(tmpobj.treatment.Item_Codeid.srv_duration) == 0.0:
                        stk_duration = 60
                    else:
                        stk_duration = int(tmpobj.treatment.Item_Codeid.srv_duration)

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

                    next_recs = TmpItemHelper.objects.filter(id__gte=tmpobj.pk,site_code=site.itemsite_code).order_by('pk')
                    for t in next_recs:
                        start_time =  get_in_val(self, t.appt_to_time)
                        if start_time:
                            starttime = datetime.datetime.strptime(str(start_time), "%H:%M")
                            end_time = starttime + datetime.timedelta(minutes = stkduration)
                            endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                            idobj = TmpItemHelper.objects.filter(id__gt=t.pk,site_code=site.itemsite_code).order_by('pk').first()
                            if idobj:
                                TmpItemHelper.objects.filter(id=idobj.pk).update(appt_fr_time=starttime,
                                appt_to_time=endtime,add_duration=duration)

            if 'session' in request.data and not request.data['session'] == None:
                serializer.save(session=float(request.data['session']))

            if 'wp1' in request.data and not request.data['wp1'] == None:
                serializer.save(wp1=float(request.data['wp1']))
                tmpids = TmpItemHelper.objects.filter(treatment=tmpobj.treatment,site_code=site.itemsite_code).order_by('pk').aggregate(Sum('wp1'))
                value ="{:.2f}".format(float(tmpids['wp1__sum']))
                tmpl_ids = TmpItemHelper.objects.filter(treatment=tmpobj.treatment,site_code=site.itemsite_code).order_by('pk')
                for t in tmpl_ids:
                    TmpItemHelper.objects.filter(id=t.pk).update(workcommpoints=value)

            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
            return Response(result, status=status.HTTP_200_OK)

        result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)  
    

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def confirm(self, request):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        # per = self.check_permissions(self.get_permissions(self))
        # print(per,"per")
        if request.GET.get('treatmentid',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        arrtreatmentid = request.GET.get('treatmentid',None).split(',')
        # print(arrtreatmentid,"td")
        for t in arrtreatmentid:
            # trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            trmt_obj = Treatment.objects.filter(status="Open",pk=t).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
         
            # trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None))
            trmt_obj = Treatment.objects.filter(status="Open",pk=t)
            if trmt_obj:
                tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj[0],site_code=site.itemsite_code)
                if not tmp_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Without employee cant do confirm!!",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
                # for emp in tmp_ids:
                #    appt = Appointment.objects.filter(cust_noid=trmt_obj[0].Cust_Codeid,appt_date=date.today(),
                #     ItemSite_Codeid=fmspw[0].loginsite,emp_no=emp.helper_code) 
                #    if not appt:
                #        tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj[0],
                #        helper_code=emp.helper_code,site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                #        if tmpids:
                #            amsg = "Appointment is not available today, please give Start Time & Add Duration for employee {0} ".format(emp.helper_name)
                #            result = {'status': status.HTTP_400_BAD_REQUEST,"message": amsg,'error': True} 
                #            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
   
                    #need to uncomment later
                    # if emp.appt_fr_time and emp.appt_to_time:         
                    #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
                    #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
                    #     if appt_ids:
                    #         msg = "In These timing already Appointment is booked for employee {0} so allocate other duration".format(emp.helper_name)
                    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                
                for existing in trmt_obj[0].helper_ids.all():
                    trmt_obj[0].helper_ids.remove(existing) 

                print(trmt_obj[0],"id")
                for t1 in tmp_ids:
                    trmt_obj[0].helper_ids.add(t1)
            
        result = {'status': status.HTTP_200_OK , "message": "Confirmed Succesfully", 'error': False}
        return Response(result, status=status.HTTP_200_OK)    

    
    @action(detail=False, methods=['delete'], name='delete', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def delete(self, request):   
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite

        if self.request.GET.get('clear_all',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give clear all/line in parms!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
    
        if request.GET.get('treatmentid',None) is None:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        arrtreatmentid = request.GET.get('treatmentid',None).split(',')
        # print(arrtreatmentid,"td")
        for tt in arrtreatmentid:
            # print(arrtreatmentid,"td")
            # trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            trmt_obj = Treatment.objects.filter(status="Open",pk=tt).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
            state = status.HTTP_204_NO_CONTENT
        # try:
            # tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).values_list('id')
            tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj).values_list('id')
            if not tmp_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Tmp Item Helper records is not present for this Treatment record id!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if self.request.GET.get('clear_all',None) == "1":
                # queryset = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).order_by('id').delete()
                queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id').delete()
                
            elif self.request.GET.get('clear_all',None) == "0":
                # queryset = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).order_by('id').first().delete()
                queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id').first().delete()

                if trmt_obj.Item_Codeid.workcommpoints == None or trmt_obj.Item_Codeid.workcommpoints == 0.0:
                    workcommpoints = 0.0
                else:
                    workcommpoints = trmt_obj.Item_Codeid.workcommpoints
                h_obj = TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk')
                count = 1
                if h_obj:
                    count = int(h_obj.count())

                # print(count,"count")
                # print(workcommpoints,"workcommpoints")
                wp11 = float(workcommpoints)
                wp12 = 0
                wp13 = 0
                wp14 = 0
                wp1 = float(workcommpoints)
                if wp1 > 0 :
                    wp11 = float(workcommpoints) / float(count)
                    if count == 2:
                        wp12 = float(workcommpoints) / float(count)
                    if count == 3:
                        wp12 = float(workcommpoints) / float(count)
                        wp13 = float(workcommpoints) / float(count)
                    if count == 4:
                        wp12 = float(workcommpoints) / float(count)
                        wp13 = float(workcommpoints) / float(count)
                        wp14 = float(workcommpoints) / float(count)

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

                    runx=1
                    for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk).order_by('pk'):
                        if runx == 1:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp11)
                        if runx == 2:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp12)
                        if runx == 3:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp13)
                        if runx == 4:
                            TmpItemHelper.objects.filter(id=h.id).update(wp1=wp14)
                        runx = runx + 1
               
        result = {'status': status.HTTP_200_OK , "message": "Deleted Succesfully", 'error': False}
        return Response(result, status=status.HTTP_200_OK) 
    
        # except Http404:
        #    pass

        # result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': True}
        # return Response(result,status=status.HTTP_200_OK)    


class TopupproductViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TopupproductSerializer

    def list(self, request):
        cust_id = self.request.GET.get('cust_id',None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
        if cust_obj is None:
            result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
            return Response(data=result, status=status.HTTP_200_OK)  
 
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        queryset = DepositAccount.objects.filter(Cust_Codeid=cust_id, Site_Codeid=site, type='Deposit', 
        outstanding__gt=0).order_by('pk')
        if queryset:
            sum = 0; lst = []
            for q in queryset:
                # ,type__in=('Deposit', 'Top Up')
                acc_ids = DepositAccount.objects.filter(ref_transacno=q.sa_transacno,
                ref_productcode=q.treat_code,Site_Codeid=site).order_by('id').last()
                acc = DepositAccount.objects.filter(pk=acc_ids.pk)
                serializer = self.get_serializer(acc, many=True)
                if acc_ids.outstanding > 0.0:
                    for data in serializer.data:
                        pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                        sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                        sum += data['outstanding']
                        data['DepositAccountid'] = q.pk
                        data["pay_amount"] = None
                        data['transaction_code'] = pos_haud.sa_transacno_ref     
                        data['stock_id'] = acc_ids.Item_Codeid.pk
                        if data["balance"]:
                            data["balance"] = "{:.2f}".format(float(data['balance']))
                        else:
                            data["balance"] = "0.00"    
                        if data["outstanding"]:
                            data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                        else:
                            data["outstanding"] = "0.00"    
                        lst.append(data)    

            if lst != []:
                header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "{:.2f}".format(float(sum)),
                "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(sum))}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                return Response(result, status=status.HTTP_200_OK)   
            else:
                header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
                "topup_amount" : "0.00","new_outstanding" : "0.00"}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK)

        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(result, status=status.HTTP_200_OK)    


class TopupprepaidViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class =  TopupprepaidSerializer

    def list(self, request):
        cust_id = self.request.GET.get('cust_id',None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
        if cust_obj is None:
            result = {'status': status.HTTP_200_OK,"message":"Customer ID does not exist!!",'error': True} 
            return Response(data=result, status=status.HTTP_200_OK)  
 
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        if not self.request.user.is_authenticated:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not allowed!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        if not fmspw:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        site = fmspw[0].loginsite
        if not site:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
      
        #queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno_type="Receipt",
        #ItemSite_Codeid__pk=site.pk)
        queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno_type="Receipt")
        if queryset:
            sum = 0; lst = []
            for q in queryset:
                #daud = PosDaud.objects.filter(sa_transacno=q.sa_transacno,
                #ItemSite_Codeid__pk=site.pk)
                #print(q.sa_transacno,"q.sa_transacno")
                daud = PosDaud.objects.filter(sa_transacno=q.sa_transacno)
                for d in daud:
                    # acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,Item_Codeid=d.dt_itemnoid,
                    # Site_Codeid=d.ItemSite_Codeid,pos_daud_lineno=d.dt_lineno,outstanding__gt = 0).order_by('id').last()
                    
                    #if int(d.dt_itemnoid.item_div) == 3 and d.dt_itemnoid.item_type == 'PACKAGE':
                    #    #acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,package_code=d.dt_combocode,
                    #    #Site_Codeid=d.ItemSite_Codeid,pos_daud_lineno=d.dt_lineno,outstanding__gt = 0).order_by('id').last()
                    #    acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,package_code=d.dt_combocode,
                    #    pos_daud_lineno=d.dt_lineno,outstanding__gt = 0).order_by('id').last()
                    #else:
                    #    #acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,Item_Codeid=d.dt_itemnoid,
                    #    #Site_Codeid=d.ItemSite_Codeid,pos_daud_lineno=d.dt_lineno,outstanding__gt = 0,status=1).order_by('id').last()
                    acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,
                    outstanding__gt = 0,status=1).order_by('id').last()

                    if acc_ids:
                        print(acc_ids.pp_no,"acc_ids.pp_no")

                        acc = PrepaidAccount.objects.filter(pk=acc_ids.pk)
                        serializer = self.get_serializer(acc, many=True)
                
                        for data in serializer.data:
                            #pos_haud = PosHaud.objects.filter(sa_custnoid=cust_obj,ItemSite_Codeid__pk=site.pk,
                            #sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                            pos_haud = PosHaud.objects.filter(sa_custnoid=cust_obj,
                            sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                            sum += data['outstanding']
                            splt = str(data['exp_date']).split('T')
                            if data['exp_date']:
                                data['exp_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                            data['transaction_code'] = pos_haud.sa_transacno_ref
                            data['prepaid_id']  = acc_ids.pk
                            data['stock_id'] = d.dt_itemnoid.pk
                            data["pay_amount"] = None
                            if data["remain"]:
                                data["remain"] = "{:.2f}".format(float(data['remain']))
                            if data["outstanding"]:
                                data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                            lst.append(data)    

            if lst != []:
                header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "{:.2f}".format(float(sum)),
                "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(sum))}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                 
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(result, status=status.HTTP_200_OK)   

class ReversalListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TreatmentReversalSerializer

    def list(self, request):
        # try:
            treatment_id = self.request.GET.get('treatment_id',None)
            if treatment_id is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            if not fmspw:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Unauthenticated Users are not Permitted!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            site = fmspw[0].loginsite
            if not site:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Users Item Site is not mapped!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            treat_id = treatment_id.split(',')
            sum = 0; lst = []; count = 0 ; tot_balance = 0 ; tot_credit = 0; checklst = []
            for i in treat_id:
                count +=1
                # queryset = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code).order_by('-pk')
                queryset = Treatment.objects.filter(pk=i,status='Open').order_by('-pk')
                if queryset:
                    # type__in=('Deposit', 'Top Up','CANCEL')
                    # acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    # treatment_parentcode=queryset[0].treatment_parentcode,Site_Codeid=queryset[0].Site_Codeid).order_by('id').last()
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    treatment_parentcode=queryset[0].treatment_parentcode).order_by('id').last()
                    serializer = self.get_serializer(queryset, many=True)
                    for data in serializer.data:
                        if queryset[0].treatment_parentcode not in checklst:
                            checklst.append(queryset[0].treatment_parentcode)
                            if acc_ids:
                                tot_balance += acc_ids.balance

                            if float(acc_ids.balance) > float(queryset[0].unit_amount):
                                tot_credit += queryset[0].unit_amount
                            elif float(acc_ids.balance) <= float(queryset[0].unit_amount):
                                tot_credit += acc_ids.balance

                        data['no'] = count
                        sum += data['unit_amount']
                        data['unit_amount'] = "{:.2f}".format(float(data['unit_amount']))
                        lst.append(data) 
                else:
                    result = {'status': status.HTTP_200_OK,"message":"Treatment ID does not exist/Not in Open Status!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK) 
            
            if lst != []:
                control_obj = ControlNo.objects.filter(control_description__iexact="Reverse No",Site_Codeid=site).first()
                if not control_obj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reverse Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                rev_code = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
                header_data = {"reverse_no" : rev_code, "total" : "{:.2f}".format(float(sum)),
                "total_depobalance" : "{:.2f}".format(float(tot_balance)),"total_credit" : "{:.2f}".format(float(tot_credit))}
                
                # if self.request.GET.get('adjustment',None) is not None:
                #     header_data["creditnote_after_adjustment"] = "Null"
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                return Response(result, status=status.HTTP_200_OK)     
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)      

    def create(self, request):
        # try:
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

            treatment_id = self.request.GET.get('treatment_id',None)
            if treatment_id is None:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 
            print(treatment_id,"treatment_id")
            
            recontrol_obj = ControlNo.objects.filter(control_description__iexact="Reverse No",Site_Codeid=site).first()
            if not recontrol_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reverse Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            rev_code = str(recontrol_obj.control_prefix)+str(recontrol_obj.Site_Codeid.itemsite_code)+str(recontrol_obj.control_no)
            
            control_obj = ControlNo.objects.filter(control_description__iexact="Reference Credit Note No",Site_Codeid=site).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reverse Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            credit_code = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)

            fmspw = fmspw.first()
            treat_id = treatment_id.split(',')
            sum = 0; lst = [];total = 0;trm_lst = [];total_r = 0.0;rea_obj = False
            
            if treat_id:
                for i in treat_id:
                    # queryset = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code).order_by('-pk')
                    queryset = Treatment.objects.filter(pk=i,status='Open').order_by('-pk')
                    if not queryset:
                        result = {'status': status.HTTP_200_OK,"message":"Treatment ID does not exist/Not in Open Status!!",'error': True} 
                        return Response(data=result, status=status.HTTP_200_OK) 
                    
                    # type__in=('Deposit', 'Top Up','CANCEL')
                    # acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    # treatment_parentcode=queryset[0].treatment_parentcode,Site_Codeid=queryset[0].Site_Codeid).order_by('id').last()
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    treatment_parentcode=queryset[0].treatment_parentcode).order_by('id').last()

                    # if acc_ids.balance == 0.0:
                    #     result = {'status': status.HTTP_200_OK,"message":"Treatment Account for this customer is Zero so cant create Credit Note!!",'error': True} 
                    #     return Response(data=result, status=status.HTTP_200_OK) 


                    j = queryset.first()
                    #treatment update
                    j.status = 'Cancel'
                    j.transaction_time = timezone.now()
                    j.save()
                    cust_obj = Customer.objects.filter(cust_code=j.cust_code,cust_isactive=True).first()

                    # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
                    # sa_transacno=j.sa_transacno).first()
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno=j.sa_transacno).first()

                    val = {'invoice': "Credit for Invoice Number : "+str(pos_haud.sa_transacno_ref),
                    'desc':j.course,'amount':j.unit_amount}
                    trm_lst.append(val)
                    total_r += j.unit_amount
                    
                    
                    #reversedtl creation
                    reversedtl = ReverseDtl(treatment_no=j.treatment_code,treatment_desc=j.course,
                    treatment_price=j.unit_amount,transac_no=j.sa_transacno,reverse_no=rev_code,
                    site_code=j.site_code)
                    reversedtl.save()

                    desc = "CANCEL" +" "+ str(j.course)+" "+str(j.times)+"/"+str(j.treatment_no)
                    #treatment Account creation 
                    if acc_ids.balance > queryset[0].unit_amount: 
                        balance = acc_ids.balance - queryset[0].unit_amount 
                        tamount =  queryset[0].unit_amount
                        total += j.unit_amount
                    elif acc_ids.balance <= queryset[0].unit_amount:  
                        balance = acc_ids.balance - acc_ids.balance  
                        tamount = acc_ids.balance 
                        total += acc_ids.balance
    
                    # description=desc,ref_no=j.treatment_parentcode,type='CANCEL',amount=-float("{:.2f}".format(float(tamount))) if tamount else 0,
                    treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                    description=desc,ref_no=j.treatment_code,type='CANCEL',amount=-float("{:.2f}".format(float(tamount))) if tamount else 0,
                    balance="{:.2f}".format(float(balance)),User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=j.sa_transacno,
                    sa_transacno="",qty=1,outstanding="{:.2f}".format(float(acc_ids.outstanding)),deposit=None,treatment_parentcode=j.treatment_parentcode,
                    treatment_code=None,sa_status="VT",cas_name=fmspw.pw_userlogin,sa_staffno=acc_ids.sa_staffno,sa_staffname=acc_ids.sa_staffname,
                    next_paydate=None,hasduedate=0,dt_lineno=j.dt_lineno,Site_Codeid=site,
                    site_code=j.site_code,treat_code=j.treatment_parentcode)
                    treatacc.save()
                            
                #creditnote creation  
                creditnote = CreditNote(treatment_code=j.treatment_parentcode,treatment_name=j.course,
                treatment_parentcode=j.treatment_parentcode,type="CANCEL",cust_code=j.cust_code,
                cust_name=j.cust_name,sa_transacno=j.sa_transacno,status="OPEN",
                credit_code=credit_code,deposit_type="TREATMENT",site_code=j.site_code,
                treat_code=j.treatment_parentcode)
                creditnote.save()
                if creditnote.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()
                    if creditnote.pk not in lst:
                        lst.append(creditnote.pk)

                #reversehdr creation
                reversehdr = ReverseHdr(reverse_no=rev_code,staff_code="",staff_name="",
                cust_code=j.cust_code,cust_name=j.cust_name,site_code=j.site_code,
                ref_creditnote=creditnote.credit_code,total_balance=total)

                reversehdr.save()
                if reversehdr.pk:
                    recontrol_obj.control_no = int(recontrol_obj.control_no) + 1
                    recontrol_obj.save()

                if self.request.GET.get('adjustment_value',None) and float(self.request.GET.get('adjustment_value',None)) != 0.0:
                    amount = self.request.GET.get('adjustment_value',None)

                    reversehdr.has_adjustment = True  
                    reversehdr.adjustment_value = amount 
                    split = str(amount).split('-')
                    if '-' in split:
                        reversehdr.credit_note_amt = total - float(amount)
                        creditnote.amount = total - float(amount)
                        creditnote.balance = total - float(amount)
                    else:
                        reversehdr.credit_note_amt = total + float(amount)
                        creditnote.amount = total + float(amount)
                        creditnote.balance = total + float(amount)

                    if creditnote.amount == 0.0 and creditnote.balance == 0.0:     
                        creditnote.status = "CLOSE"
                        
                    creditnote.save()
                    if not self.request.GET.get('reason_id',None) is None:
                        rea_obj = ReverseTrmtReason.objects.filter(id=self.request.GET.get('reason_id',None),
                        is_active=True)

                        if not rea_obj:
                            result = {'status': status.HTTP_200_OK,"message":"Reason ID does not exist!!",'error': True} 
                            return Response(data=result, status=status.HTTP_200_OK)  

                        reversehdr.reason = rea_obj[0].rev_desc
                      

                    if not self.request.GET.get('remark',None) is None:
                        reversehdr.remark = self.request.GET.get('remark',None)

                    if rea_obj[0].rev_no == '100001':
                        if rea_obj:
                            reversehdr.reason1 = rea_obj[0].rev_desc 
                        if amount:
                            reversehdr.reason_adj_value1 = amount

                    reversehdr.save()
                else:
                    creditnote.amount = total
                    creditnote.balance = total
                    if creditnote.amount == 0.0 and creditnote.balance == 0.0:     
                        creditnote.status = "CLOSE"
                    creditnote.save() 
                    reversehdr.credit_note_amt = total
                    reversehdr.save()


           
            if lst != [] and trm_lst != []:
                title = Title.objects.filter(product_license=site.itemsite_code).first()

                credit_ids = CreditNote.objects.filter(pk__in=lst).order_by('pk')
                    
                # print(title.logo_pic.url,"title.logo_pic.url")
                path = None
                if title and title.logo_pic:
                    path = BASE_DIR + title.logo_pic.url

                split = str(credit_ids[0].sa_date).split(" ")
                date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d/%m/%Y")
                adjustamt = self.request.GET.get('adjustment_value',None)
                remark = self.request.GET.get('remark',None)
                if adjustamt:
                    total_credit = float(total_r) + float(adjustamt)
                else:
                    total_credit = float(total_r)


                data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
                'address': title.trans_h2 if title and title.trans_h2 else '', 
                'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
                'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
                'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
                'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
                'credit_ids': credit_ids, 'date':date,'total':total_r,'adjustamt':adjustamt if adjustamt else "",
                'reason':rea_obj[0] if rea_obj else "",'remark':remark if remark else "",'total_credit':total_credit,
                'credit': trm_lst,'cust': cust_obj,'creditno': credit_ids[0].credit_code,'fmspw':fmspw,'adjustamtstr': "0.00",
                'path':path if path else '','title':title if title else None,
                }

                template = get_template('creditnote.html')
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

                dst ="creditnote_" + str(str(credit_ids[0].credit_code)) + ".pdf"

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

                        ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/creditnote_"+str(credit_ids[0].credit_code)+".pdf"

                        result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False,
                        'data': ip_link}
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Failed to create ", 'error': False}
            return Response(data=result, status=status.HTTP_200_OK)
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)     


class ShowBalanceViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ShowBalanceSerializer

    def list(self, request):
        treatment_id = self.request.GET.get('treatment_id',None)
        if treatment_id is None:
            result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
            return Response(data=result, status=status.HTTP_200_OK) 
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite     

        treat_id = treatment_id.split(',')
        checklst = []; lst = []; sum = 0
        for i in treat_id:
            q = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code)
            if not q:
                result = {'status': status.HTTP_200_OK,"message":"Treatment ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK) 
            
            # 'Deposit', 'Top Up','CANCEL')
            acc_ids = TreatmentAccount.objects.filter(ref_transacno=q[0].sa_transacno,
            treatment_parentcode=q[0].treatment_parentcode,Site_Codeid=q[0].Site_Codeid).order_by('id').last()
            if q[0].treatment_parentcode not in checklst:
                reverse_amt = 0
                reverse_amt += q[0].unit_amount
                checklst.append(q[0].treatment_parentcode)
                queryset = TreatmentAccount.objects.filter(pk=acc_ids.pk)
                if queryset:
                    serializer = self.get_serializer(queryset, many=True)
                    for data in serializer.data:
                        if data['balance']:
                            data['balance'] = "{:.2f}".format(float(data['balance']))
                        if data["outstanding"]:    
                            data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                        dict_v = dict(data)
                        lst.append(dict_v) 
            else:
                if q[0].treatment_parentcode in checklst:
                    reverse_amt += q[0].unit_amount
 
            for l in lst:
                if str(l['treatment_parentcode']) == q[0].treatment_parentcode:
                    l['reverse_price'] = "{:.2f}".format(float(reverse_amt))
                    
        if lst != []:
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': lst}
            return Response(result, status=status.HTTP_200_OK)     
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)


class ReverseTrmtReasonAPIView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ReverseTrmtReason.objects.filter(is_active=True).order_by('id')
    serializer_class = ReverseTrmtReasonSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
        else:
            serializer = self.get_serializer()
            result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK) 
       

class VoidViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = PosHaud.objects.filter(isvoid=False).order_by('-pk')
    serializer_class = VoidSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        year = date.today().year
        month = date.today().month
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        transac_no = self.request.GET.get('transac_no',None)
        cust_code = self.request.GET.get('cust_code',None)
        cust_name = self.request.GET.get('cust_name',None)
        # queryset = PosHaud.objects.filter(isvoid=False,sa_date__year=year,
        # ItemSite_Codeid__pk=site.pk).order_by('-pk')
        # queryset = PosHaud.objects.filter(isvoid=False,ItemSite_Codeid__pk=site.pk).order_by('-pk')
        queryset = PosHaud.objects.filter(isvoid=False).order_by('-pk')
        if not from_date and not to_date and not transac_no and not cust_code and not cust_name:
            queryset = queryset
        else:
            if from_date and to_date: 
                # queryset = queryset.filter(Q(sa_date__date__gte=from_date,sa_date__date__lte=to_date)
                #     | Q(sa_date__year__gte=year,sa_date__year__lte=year)
                #     | Q(sa_date__month__gte=month,sa_date__month__lte=month)).order_by('-pk')
                queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('-pk')
            if transac_no:
                queryset = queryset.filter(sa_transacno_ref__icontains=transac_no).order_by('-pk')
            if cust_code:
                # print(site.itemsite_code,"site_code")
                # customer = Customer.objects.filter(pk=cust_code,cust_isactive=True,site_code=site.itemsite_code).last()
                customer = Customer.objects.filter(pk=cust_code,cust_isactive=True).last()
                # print(customer.cust_code,"cust_code")
                queryset = queryset.filter(sa_custno__icontains=customer.cust_code).order_by('-pk')
                # queryset = queryset.filter(sa_custno__icontains=customer.cust_code).order_by('-pk')
                # queryset = PosHaud.objects.filter(sa_custnoid=15497).order_by('-pk')
            if cust_name:
               queryset = queryset.filter(sa_custname__icontains=cust_name).order_by('-pk')
        return queryset

    def list(self, request):
            if str(self.request.GET.get('cust_code',None)) != "undefined":
                if isinstance(int(self.request.GET.get('cust_code',None)), int):
                    serializer_class = VoidSerializer
                    queryset = self.filter_queryset(self.get_queryset())
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
                        dict_d = dict(dat)
                        if dict_d['sa_date']:
                            splt = str(dict_d['sa_date']).split('T')
                            dict_d['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        lst.append(dict_d)
                    v['dataList'] =  lst  
                    return Response(result, status=status.HTTP_200_OK)   
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Data",'error': False, "data":[]}
                return Response(data=result, status=status.HTTP_200_OK)   
               

    @action(detail=False, methods=['get'], name='Details', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def Details(self, request):
        #try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            poshdr_id = self.request.GET.get('poshdr_id',None)
            # if not isinstance(poshdr_id, int):
            #     result = {'status': status.HTTP_200_OK,"message":"Poshaud ID Should be Integer only!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_200_OK)
            # print(poshdr_id, "poshdr_id")
            haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            ItemSite_Codeid__pk=site.pk).first()
            if haud_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"PosHaud ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            pp_obj = PrepaidAccount.objects.filter(pp_no=haud_obj.sa_transacno,sa_status='SA').first()
            if pp_obj is None:
                usenothing = ""
            else:
                result = {'status': status.HTTP_200_OK,"message":"Cannot Void Invoice After Prepaid Usage!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            cust_obj = Customer.objects.filter(cust_code=haud_obj.sa_custno,cust_isactive=True).first()

            daud_ids = PosDaud.objects.filter(sa_transacno=haud_obj.sa_transacno,
            ItemSite_Codeid__pk=site.pk) 
            if daud_ids:
                serializer = PosDaudDetailsSerializer(daud_ids, many=True)
                for data in serializer.data:
                    data['dt_amt'] = "{:.2f}".format(float(data['dt_amt']))
                    data['cust_noid'] = cust_obj.pk
                    data['cart_id'] = haud_obj.cart_id

                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        #except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)
                   

    def create(self, request):
        # try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
        
            poshdr_id = self.request.GET.get('poshdr_id',None)
            # poshdrid = poshdr_id.split(',')
            # for i in poshdrid:
            haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            ItemSite_Codeid__pk=site.pk).first()
            print(poshdr_id,'here1')
            if haud_obj is None:
                print(poshdr_id,'poshdr')
                result = {'status': status.HTTP_200_OK,"message":"PosHaud ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            print(poshdr_id,'here2')
            gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()

            # for p in poshdrid:
            haudobj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            ItemSite_Codeid__pk=site.pk).first()
            # print(site.itemsite_code,"sitecode=site.itemsite_code")
            if haudobj.cart_id:
                ids_cart = ItemCart.objects.filter(isactive=True,cart_id=haudobj.cart_id,
                sitecode=site.itemsite_code,cart_date=date.today(),
                cust_noid__pk=haud_obj.sa_custnoid.pk).exclude(type__in=type_tx)
                if ids_cart:
                    print(poshdr_id,'here3')
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Cart is Created!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    haudobj.cart_id = None
                    print(poshdr_id,'here4')
                    haudobj.save()
                    ids_cartold = ItemCart.objects.filter(cart_id=haudobj.cart_id,cart_status="Inprogress",
                    sitecode=site.itemsite_code,cust_noid__pk=haud_obj.sa_custnoid.pk).exclude(type__in=type_tx).delete()

            print(poshdr_id,'here41')
            daud_ids = PosDaud.objects.filter(sa_transacno=haudobj.sa_transacno,
            ItemSite_Codeid__pk=site.pk) 
            lineno = 0
            control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
            if not control_obj:
                print(poshdr_id,'here5')
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
            
            cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
            final = list(set([r.cart_id for r in cartre]))
            print(final,len(final),"final")
            code_site = site.itemsite_code
            prefix = control_obj.control_prefix
            # print(control_obj.Site_Codeid.itemsite_code,"control_obj.Site_Codeid.itemsite_code")
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
                
            haudobj.cart_id = cart_id
            haudobj.save()
            print(cart_id,'here42')
           
            cart_lst = []
            for d in daud_ids:
                print(d.dt_itemno,'lineno')
                #if d.itemcart:
                if 1==1:
                    lineno += 1
                    if lineno == 1:
                        check = "New"
                    else:
                        check = "Old"

                    # cust_obj = Customer.objects.filter(pk=d.itemcart.cust_noid.pk,cust_isactive=True).first()
                    cust_obj = Customer.objects.filter(cust_code=haud_obj.sa_custno,cust_isactive=True).first()
                    #stock_obj = Stock.objects.filter(pk=d.itemcart.itemcodeid.pk,item_isactive=True).first()
                    stock_obj = Stock.objects.filter(item_code=d.dt_itemno[:8],item_isactive=True).first()
                    
                    tax_value = 0.0
                    # if stock_obj.is_have_tax == True:
                    #    tax_value = gst.item_value
                    
                    #if d.itemcart.type == "Deposit":
                    #    type = "VT-Deposit"
                    #elif d.itemcart.type == "Top Up":
                    #    type = "VT-Top Up" 
                    #elif d.itemcart.type == "Sales":
                    #    type = "VT-Sales"
                    #else:
                    #    type = d.itemcart.type            
                    if d.record_detail_type == "TD" :
                        type = "VT-Sales"
                    elif d.record_detail_type[:2] == "TP":
                        type = "VT-Top Up" 
                    else:
                        type = "VT-Deposit"

                    print(poshdr_id,'here43')
                    cart = ItemCart(cart_date=date.today(),phonenumber=cust_obj.cust_phone2,
                    customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                    itemcodeid=stock_obj,itemcode=d.dt_itemno,itemdesc=stock_obj.item_desc,
                    quantity=d.dt_qty,price="{:.2f}".format(float(d.dt_price)),
                    sitecodeid=d.ItemSite_Codeid,sitecode=d.itemsite_code,
                    cart_status="Inprogress",cart_id=cart_id,
                    tax="{:.2f}".format(tax_value),check=check,ratio=0,
                    discount=d.dt_discpercent,discount_amt=d.dt_discamt,
                    discount_price=d.dt_promoprice,total_price=d.dt_promoprice,
                    trans_amt=d.dt_transacamt,deposit=d.dt_deposit,type=type,
                    discreason_txt=d.dt_remark)
                    cart.save()
                    print(poshdr_id,'here44')
                    
                    #for s in d.itemcart.sales_staff.all(): 
                    #    cart.sales_staff.add(s)
                    #    print(s,"adding staff")

                    #for se in d.itemcart.service_staff.all(): 
                    #    cart.service_staff.add(se)

                    #for h in d.itemcart.helper_ids.all(): 
                    #    cart.helper_ids.add(h)    
                    
                    #for dis in d.itemcart.disc_reason.all(): 
                    #    cart.disc_reason.add(dis)
                    
                    #for po in d.itemcart.pos_disc.all(): 
                    #    cart.pos_disc.add(po)

                    if cart.pk:
                        if cart.pk not in cart_lst:
                            cart_lst.append(cart.pk)
    
            if cart_lst != [] and len(cart_lst) == len(daud_ids):
                print(poshdr_id,'here6')
                result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False,'data':cart_id}
                return Response(data=result, status=status.HTTP_200_OK)
                
        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)
                     
    

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def VoidReturn(self, request):
        # try:
            global type_tx
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
        
            cart_id = self.request.GET.get('cart_id',None)
            if not cart_id:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Cart ID parms not given!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            
            #This Transaction already VOID, no permission allow
            cartobj_ids = ItemCart.objects.filter(isactive=True,cart_id=cart_id,
            sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress").exclude(type__in=type_tx)
            if not cartobj_ids or cartobj_ids is None:
                result = {'status': status.HTTP_200_OK,"message":"Cart ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()

            haudobj = PosHaud.objects.filter(cart_id=cart_id,isvoid=False,
            ItemSite_Codeid__pk=site.pk,sa_custnoid=cartobj_ids[0].cust_noid).first()
            if not haudobj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"sa transacno does not exist in Poshaud!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
            daud_ids = PosDaud.objects.filter(sa_transacno=haudobj.sa_transacno,
            ItemSite_Codeid__pk=site.pk)
            taud_ids = PosTaud.objects.filter(sa_transacno=haudobj.sa_transacno,
            ItemSIte_Codeid__pk=site.pk)
            multi_ids = Multistaff.objects.filter(sa_transacno=haudobj.sa_transacno)

            control_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Transaction Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
            
            sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
            
            refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference VOID No",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
            if not refcontrol_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference VOID Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
            
            sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
            
            voidreason_id = self.request.GET.get('voidreason_id',None)
            void_obj = VoidReason.objects.filter(pk=voidreason_id,isactive=True)
            if void_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"VoidReason ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            
            finalsatrasc  = False
            if haudobj.sa_transacno_type in ['Receipt','Non Sales']:
                for t in taud_ids:
                    taud = PosTaud(sa_transacno=sa_transacno,pay_groupid=t.pay_groupid,pay_group=t.pay_group,
                    pay_typeid=t.pay_typeid,pay_type=t.pay_type,pay_desc=t.pay_desc,pay_tendamt=t.pay_tendamt,
                    pay_tendrate=t.pay_tendrate,pay_tendcurr=t.pay_tendcurr,pay_amt=-t.pay_amt,pay_amtrate=t.pay_amtrate,
                    pay_amtcurr=t.pay_amtcurr,pay_rem1=t.pay_rem1,pay_rem2=t.pay_rem2,pay_rem3=t.pay_rem3,pay_rem4=t.pay_rem4,
                    pay_status=t.pay_status,pay_actamt=-t.pay_actamt,ItemSIte_Codeid=t.ItemSIte_Codeid,
                    itemsite_code=t.itemsite_code,paychange=t.paychange,dt_lineno=t.dt_lineno,
                    pay_gst_amt_collect=-t.pay_gst_amt_collect,pay_gst=-t.pay_gst,posdaudlineno=t.posdaudlineno,
                    posdaudlineamountassign=t.posdaudlineamountassign,posdaudlineamountused=t.posdaudlineamountused,
                    voucher_name=t.voucher_name,billed_by=t.billed_by,
                    subtotal=0 if t.subtotal is None else -t.subtotal,
                    tax=0 if t.tax is None else -t.tax,
                    discount_amt=0 if t.discount_amt is None else -t.discount_amt,
                    billable_amount=0 if t.billable_amount is None else -t.billable_amount,
                    credit_debit=t.credit_debit,
                    points=t.points,prepaid=t.prepaid,pay_premise=t.pay_premise,is_voucher=t.is_voucher,
                    voucher_no=t.voucher_no,voucher_amt=t.voucher_amt)
                    taud.save()


                    if t.pay_desc == 'PREPAID':
                         # pac_ids = PrepaidAccount.objects.filter(transac_no=haudobj.sa_transacno,sa_status='SA',
                         # cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                         pac_ids = PrepaidAccount.objects.filter(transac_no=t.sa_transacno,sa_status='SA',
                         cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                         # pac_ids = PrepaidAccount.objects.filter(Q(pp_no=d.sa_transacno) | Q(topup_no=d.sa_transacno) | Q(topup_no=d.sa_transacno),
                         # sa_status='SA',cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                         print(pac_ids,"pac_ids")
                         for pa in pac_ids:
                             remain = float(pa.remain) + float(pa.use_amt)
                             pac_lastid = PrepaidAccount.objects.filter(pp_no=pa.pp_no,line_no=pa.line_no,
                             cust_code=haudobj.sa_custno,site_code=site.itemsite_code,status=True).first()

                             if pac_lastid:
                                 # print(pac_lastid.pp_no,"pp_no")
                                 remain = float(pac_lastid.remain) + float(pa.use_amt)
                                 # PrepaidAccount.objects.filter(pk=pac_lastid.pk).update(status=False)
                                 PrepaidAccount.objects.filter(pp_no=pa.pp_no,line_no=pa.line_no).update(status=False)

                             pacc_ids = PrepaidAccountCondition.objects.filter(pp_no=pa.pp_no,
                             pos_daud_lineno=pa.line_no).only('pp_no','pos_daud_lineno').first()
                             if pacc_ids:                                
                                 cuseamt = float(pacc_ids.use_amt) - float(pa.use_amt)
                                 acc = PrepaidAccountCondition.objects.filter(pk=pacc_ids.pk).update(use_amt=cuseamt,remain=remain)

                             useamt = 0 - float(pa.use_amt)
                             prepacc = PrepaidAccount(pp_no=pa.pp_no,pp_type=pa.pp_type,
                             pp_desc=pa.pp_desc,exp_date=pa.exp_date,cust_code=pa.cust_code,
                             cust_name=pa.cust_name,pp_amt=pa.pp_amt,pp_total=pa.pp_total,
                             pp_bonus=pa.pp_bonus,transac_no=pa.transac_no,item_no=pa.item_no,use_amt=useamt,
                             remain=remain,ref1=pa.ref1,ref2=pa.ref2,status=True,site_code=site.itemsite_code,sa_status="VT",exp_status=pa.exp_status,
                             voucher_no=pa.voucher_no,isvoucher=pa.isvoucher,has_deposit=pa.has_deposit,topup_amt=0,
                             outstanding=pa.outstanding,active_deposit_bonus=pa.active_deposit_bonus,topup_no="",topup_date=None,
                             line_no=pa.line_no,staff_name=None,staff_no=None,
                             pp_type2=pa.pp_type2,condition_type1=pa.condition_type1,pos_daud_lineno=pa.line_no,Cust_Codeid=pa.Cust_Codeid,Site_Codeid=pa.Site_Codeid,
                             Item_Codeid=pa.Item_Codeid,item_code=pa.item_code)
                             prepacc.save()

                    if t.pay_desc == 'Credit Note':
                        crdobj = CreditNote.objects.filter(credit_code=t.pay_rem1,cust_code=haudobj.sa_custno).first()
                        # print(card_no,"card_no")
                        if crdobj:
                            crbalance = float(crdobj.balance) + float(t.pay_amt)
                            print(crbalance,"crbalance")
                            if crbalance == 0.0:
                                crstatus = "CLOSE"
                            elif crbalance < 0.0:
                                crstatus = "CLOSE" 
                                crbalance = 0.0   
                            elif crbalance > 0.0:
                                crstatus = "OPEN"    
                            CreditNote.objects.filter(pk=crdobj.pk).update(balance=crbalance,status=crstatus)

                    if t.pay_desc == 'Voucher':
                        crdobj = VoucherRecord.objects.filter(voucher_no=t.pay_rem1,cust_code=haudobj.sa_custno).first()
                        print(t.pay_rem1,"Voucher Reset")
                        if crdobj:
                            VoucherRecord.objects.filter(pk=crdobj.pk).update(isvalid=True,used=False)

                for m in multi_ids:
                    multi =  Multistaff(sa_transacno=sa_transacno,item_code=m.item_code,emp_code=m.emp_code,
                    ratio=m.ratio,salesamt=-float("{:.2f}".format(float(m.salesamt))) if m.salesamt else 0,type=m.type,isdelete=m.isdelete,role=m.role,dt_lineno=m.dt_lineno,
                    level_group_code=m.level_group_code) 
                    multi.save()
                
                for d in daud_ids:
                    # print(d.dt_lineno,"d.dt_lineno")
                    cart_obj = ItemCart.objects.filter(isactive=True,cart_id=cart_id,lineno=d.dt_lineno,
                    sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress",
                    cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx).first()
                    
                    topup_outstanding = d.topup_outstanding
                    #if d.itemcart.type == 'Top Up':
                    if d.record_detail_type == 'TP':
                        topup_outstanding = d.topup_outstanding + d.dt_price

                    sales = "";service = ""
                    if cart_obj.sales_staff.all():
                        for i in cart_obj.sales_staff.all():
                            if sales == "":
                                # sales = sales + i.emp_name
                                sales = sales + i.display_name
                            elif not sales == "":
                                # sales = sales +","+ i.emp_name
                                sales = sales +","+ i.display_name
                    if cart_obj.service_staff.all(): 
                        for s in cart_obj.service_staff.all():
                            if service == "":
                                # service = service + s.emp_name
                                service = service + s.display_name
                            elif not service == "":
                                # service = service +","+ s.emp_name 
                                service = service +","+ s.display_name 
                    
                    
                    daud = PosDaud(sa_transacno=sa_transacno,dt_status="VT",dt_itemnoid=d.dt_itemnoid,
                    dt_itemno=d.dt_itemno,dt_itemdesc=d.dt_itemdesc,dt_price=d.dt_price,dt_promoprice="{:.2f}".format(float(d.dt_promoprice)),
                    dt_amt=-float("{:.2f}".format(float(d.dt_amt))),dt_qty=-d.dt_qty,dt_discamt=-d.dt_discamt if float(d.dt_discamt) > 0.0 else d.dt_discamt,
                    dt_discpercent=-d.dt_discpercent if float(d.dt_discpercent) > 0.0 else d.dt_discpercent,
                    dt_discdesc=d.dt_discdesc,dt_discno=d.dt_discno,dt_remark=d.dt_remark,dt_Staffnoid=d.dt_Staffnoid,
                    dt_staffno=d.dt_staffno,dt_staffname=d.dt_staffname,dt_reason=d.dt_reason,dt_discuser="",
                    dt_combocode=d.dt_combocode,ItemSite_Codeid=d.ItemSite_Codeid,itemsite_code=d.itemsite_code,
                    dt_lineno=d.dt_lineno,dt_stockupdate=d.dt_stockupdate,dt_stockremark=d.dt_stockremark,
                    dt_uom=d.dt_uom,isfoc=d.isfoc,item_remarks=None,next_payment=None,next_appt=None,
                    dt_transacamt="{:.2f}".format(float(d.dt_transacamt)),dt_deposit=-float("{:.2f}".format(float(d.dt_deposit))) if d.dt_deposit else 0,appt_time=None,hold_item_out=d.hold_item_out,
                    issue_date=d.issue_date,hold_item=d.hold_item,holditemqty=d.holditemqty,st_ref_treatmentcode='',
                    item_status_code=d.item_status_code,first_trmt_done=d.first_trmt_done,first_trmt_done_staff_code=d.first_trmt_done_staff_code,
                    first_trmt_done_staff_name=d.first_trmt_done_staff_name,record_detail_type=d.record_detail_type,
                    trmt_done_staff_code=d.trmt_done_staff_code,trmt_done_staff_name=d.trmt_done_staff_name,
                    trmt_done_id=d.trmt_done_id,trmt_done_type=d.trmt_done_type,topup_service_trmt_code=d.topup_service_trmt_code,
                    topup_product_treat_code=d.topup_product_treat_code,topup_prepaid_trans_code=d.topup_prepaid_trans_code,
                    topup_prepaid_type_code=d.topup_prepaid_type_code,voucher_link_cust=d.voucher_link_cust,
                    voucher_no=d.voucher_no,update_prepaid_bonus=d.update_prepaid_bonus,deduct_commission=d.deduct_commission,
                    deduct_comm_refline=d.deduct_comm_refline,gst_amt_collect=-float("{:.2f}".format(float(d.gst_amt_collect))) if d.gst_amt_collect else 0,
                    topup_prepaid_pos_trans_lineno=d.topup_prepaid_pos_trans_lineno,open_pp_uid_ref=None,compound_code=d.compound_code,
                    topup_outstanding=topup_outstanding,t1_tax_code=d.t1_tax_code,t1_tax_amt=d.t1_tax_amt,
                    t2_tax_code=d.t2_tax_code,t2_tax_amt=d.t2_tax_amt,dt_grossamt=d.dt_grossamt,dt_topup_old_outs_amt=d.dt_topup_old_outs_amt,
                    dt_topup_new_outs_amt=d.dt_topup_new_outs_amt,dt_td_tax_amt=d.dt_td_tax_amt,earnedpoints=d.earnedpoints,
                    earnedtype=d.earnedtype,redeempoints=d.redeempoints,redeemtype=d.redeemtype,itemcart=cart_obj,
                    staffs=sales +" "+"/"+" "+ service)
                    
                    daud.save()

                    #if int(d.itemcart.itemcodeid.item_div) == 3:
                    if (d.record_detail_type != 'PRODUCT' and d.record_detail_type == 'PREPAID' and d.record_detail_type != 'TP PRODUCT' and d.record_detail_type == 'TP PREPAID') :
                        #if d.itemcart.type == 'Deposit':
                        if (d.record_detail_type == 'SERVICE' or d.record_detail_type == 'PACKAGE') :
                            acc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Deposit',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                            for acc in acc_ids:
                                TreatmentAccount.objects.filter(pk=acc.pk).update(sa_status="VOID",updated_at=timezone.now())   
                            
                            treat_ids = Treatment.objects.filter(sa_transacno=haudobj.sa_transacno,
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                            for trt in treat_ids:
                                Treatment.objects.filter(pk=trt.pk).update(status="Cancel",sa_status="VOID")
                            
                            sal_acc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                            for sal in sal_acc_ids:
                                TreatmentAccount.objects.filter(pk=acc.pk).update(description=d.itemcart.itemcodeid.item_name,sa_status="VOID",updated_at=timezone.now())   
                                appt_ids = Appointment.objects.filter(sa_transacno=sal.ref_transacno,
                                treatmentcode=sal.ref_no,itemsite_code=site.itemsite_code).update(appt_status="Cancelled")
                                master_ids = Treatment_Master.objects.filter(sa_transacno=sal.ref_transacno,
                                treatment_code=sal.ref_no,site_code=site.itemsite_code).update(status="Cancel")
                           
                        elif (d.record_detail_type == 'TP SERVICE' or d.record_detail_type == 'TP PACKAGE') :
                        # elif d.itemcart.type == 'Top Up':
                            tacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Top Up',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)

                            for ac in tacc_ids:
                                balance = ac.balance - ac.amount
                                outstanding = ac.outstanding + ac.amount
                                TreatmentAccount(Cust_Codeid=ac.Cust_Codeid,cust_code=ac.cust_code,
                                description=ac.description,ref_no=sa_transacno,type=ac.type,amount=-float("{:.2f}".format(float(ac.amount))) if ac.amount else 0,
                                balance="{:.2f}".format(float(balance)),user_name=ac.user_name,User_Nameid=ac.User_Nameid,
                                ref_transacno=ac.ref_transacno,sa_transacno=sa_transacno,qty=-ac.qty,
                                outstanding="{:.2f}".format(float(outstanding)),deposit=-float("{:.2f}".format(float(ac.deposit))) if ac.deposit else 0,treatment_parentcode=ac.treatment_parentcode,
                                treatment_code=ac.treatment_code,sa_status="VT",cas_name=ac.cas_name,sa_staffno=ac.sa_staffno,
                                sa_staffname=ac.sa_staffname,next_paydate=ac.next_paydate,hasduedate=ac.hasduedate,
                                dt_lineno=ac.dt_lineno,lpackage=ac.lpackage,package_code=ac.package_code,Site_Codeid=ac.Site_Codeid,
                                site_code=ac.site_code,treat_code=ac.treat_code,focreason=ac.focreason,itemcart=cart_obj).save()
                        
                        elif (d.record_detail_type == 'TD' ) :
                        #elif d.itemcart.type == 'Sales':
                            sacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                        
                            description = d.itemcart.itemcodeid.item_name+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)
                            
                            Treatment.objects.filter(pk=d.itemcart.treatment.pk).update(course=description,status="Open",
                            trmt_room_code=None,treatment_count_done=0)
                            
                            for sa in sacc_ids:
                                master_ids = Treatment_Master.objects.filter(sa_transacno=sa.ref_transacno,
                                treatment_code=sa.ref_no,site_code=site.itemsite_code).update(status="Cancel")
                                appt_ids = Appointment.objects.filter(sa_transacno=sa.ref_transacno,
                                treatmentcode=sa.ref_no,itemsite_code=site.itemsite_code).update(appt_status="Cancelled")
    
                                TreatmentAccount.objects.filter(pk=sa.pk).update(sa_status='VOID')
                                # type__in=('Deposit', 'Top Up')
                                olacc_ids = TreatmentAccount.objects.filter(ref_transacno=sa.ref_transacno,
                                treatment_parentcode=sa.treatment_parentcode,cust_code=haudobj.sa_custno,site_code=site.itemsite_code).order_by('id').exclude(type='Sales').last()

                                TreatmentAccount(Cust_Codeid=sa.Cust_Codeid,cust_code=sa.cust_code,
                                description=description,ref_no=sa.ref_no,type=sa.type,amount="{:.2f}".format(float(d.itemcart.treatment.unit_amount)),
                                balance="{:.2f}".format(float(olacc_ids.balance)),user_name=sa.user_name,User_Nameid=sa.User_Nameid,
                                ref_transacno=sa.ref_transacno,sa_transacno=sa_transacno,qty=sa.qty,
                                outstanding="{:.2f}".format(float(olacc_ids.outstanding)) if olacc_ids.outstanding else None,deposit=-float("{:.2f}".format(float(sa.deposit))) if sa.deposit else 0,treatment_parentcode=sa.treatment_parentcode,
                                treatment_code=sa.treatment_code,sa_status="SA",cas_name=fmspw[0].pw_userlogin,sa_staffno=sa.sa_staffno,
                                sa_staffname=sa.sa_staffname,next_paydate=sa.next_paydate,hasduedate=sa.hasduedate,
                                dt_lineno=sa.dt_lineno,lpackage=sa.lpackage,package_code=sa.package_code,Site_Codeid=sa.Site_Codeid,
                                site_code=sa.site_code,treat_code=sa.treat_code,focreason=sa.focreason,itemcart=cart_obj).save()

                            
                        ihelper_ids = ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,site_code=site.itemsite_code)
                        for hlp in ihelper_ids:
                            ItemHelper(item_code=hlp.item_code,item_name=hlp.item_name,line_no=hlp.line_no,
                            sa_transacno=hlp.sa_transacno,amount=-hlp.amount,helper_name=hlp.helper_name,
                            helper_code=hlp.helper_code,site_code=hlp.site_code,share_amt=-hlp.share_amt,
                            helper_transacno=sa_transacno,system_remark=hlp.system_remark,
                            wp1=hlp.wp1,wp2=hlp.wp2,wp3=hlp.wp3,td_type_code=hlp.td_type_code,
                            td_type_short_desc=hlp.td_type_short_desc).save()

                    elif (d.record_detail_type == 'PRODUCT' or d.record_detail_type == 'TP PRODUCT') :
                    # elif int(d.itemcart.itemcodeid.item_div) == 1:
                        if d.record_detail_type == 'PRODUCT':
                        
                            dacc_ids = DepositAccount.objects.filter(sa_transacno=haudobj.sa_transacno,sa_status='SA',type='Deposit',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                
                            for depo in dacc_ids:
                                tpcontrolobj = ControlNo.objects.filter(control_description__iexact="TopUp",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                                if not tpcontrolobj:
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"TopUp Control No does not exist!!",'error': True} 
                                    raise serializers.ValidationError(result)

                                tp_code = str(tpcontrolobj.control_prefix)+str(tpcontrolobj.Site_Codeid.itemsite_code)+str(tpcontrolobj.control_no)
                            
                                balance = depo.balance - depo.amount
                                desc = "Cancel"+" "+"Product Amount : "+str("{:.2f}".format(float(depo.amount)))
                                DepositAccount(cust_code=depo.cust_code,type="CANCEL",amount=-float("{:.2f}".format(float(depo.amount))) if depo.amount else 0,balance="{:.2f}".format(float(balance)),
                                user_name=depo.user_name,qty=depo.qty,outstanding=0.0,deposit="{:.2f}".format(float(depo.deposit)),
                                cas_name=fmspw[0].pw_userlogin,sa_staffno=depo.sa_staffno,sa_staffname=depo.sa_staffname,
                                deposit_type=depo.deposit_type,sa_transacno=depo.sa_transacno,description=desc,
                                sa_status="VT",item_barcode=depo.item_barcode,item_description=depo.item_description,
                                treat_code=depo.treat_code,void_link=depo.void_link,lpackage=depo.lpackage,
                                package_code=depo.package_code,dt_lineno=depo.dt_lineno,Cust_Codeid=depo.Cust_Codeid,
                                Site_Codeid=depo.Site_Codeid,site_code=depo.site_code,Item_Codeid=depo.Item_Codeid,
                                item_code=depo.item_code,ref_transacno=depo.ref_transacno,ref_productcode=depo.ref_productcode,
                                ref_code=tp_code).save()

                                tpcontrolobj.control_no = int(tpcontrolobj.control_no) + 1
                                tpcontrolobj.save()
                            #    DepositAccount.objects.filter(pk=depo.pk).update(sa_status="VT",item_description="Cancel"+depo.item_description,updated_at=timezone.now())

                            holdids = Holditemdetail.objects.filter(sa_transacno=d.sa_transacno,
                            itemno=d.dt_itemno,status='Open').only('sa_transacno','itemno').first()  
                            hold_qty = d.dt_qty
                            if holdids:
                                #for hold in holdids:
                                hold_qty -= holdids.holditemqty                    
                                Holditemdetail.objects.filter(pk=holdids.pk).update(status="Close",holditemqty=0)

                            if hold_qty > 0:
                                #ItemBatch
                                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                                item_code=d.dt_itemnoid.item_code,uom=d.dt_uom).order_by('pk').last()
                                if batch_ids:
                                    # addamt = batch_ids.qty + d.dt_qty
                                    addamt = batch_ids.qty + hold_qty
                                    batch_ids.qty = addamt
                                    batch_ids.save()

                                #Stktrn
                                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                                itemcode=d.dt_itemno,item_uom=d.dt_uom,trn_docno=haudobj.sa_transacno,
                                line_no=d.dt_lineno).last() 
                                currenttime = timezone.now()
                                post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                                if stktrn_ids:
                                    amt_add = stktrn_ids.trn_balqty - stktrn_ids.trn_qty
                                    stktrn_id = Stktrn(trn_no=stktrn_ids.trn_no,post_time=post_time,aperiod=stktrn_ids.aperiod,
                                    itemcode=stktrn_ids.itemcode,store_no=site.itemsite_code,trn_date=stktrn_ids.trn_date,
                                    tstore_no=stktrn_ids.tstore_no,fstore_no=stktrn_ids.fstore_no,trn_docno=sa_transacno,
                                    trn_type="VT",trn_db_qty=stktrn_ids.trn_db_qty,trn_cr_qty=stktrn_ids.trn_cr_qty,trn_post=stktrn_ids.trn_post,
                                    trn_qty=-stktrn_ids.trn_qty,trn_balqty=amt_add,trn_balcst=stktrn_ids.trn_balcst,
                                    trn_amt=stktrn_ids.trn_amt,trn_cost=stktrn_ids.trn_cost,trn_ref=stktrn_ids.trn_ref,
                                    hq_update=stktrn_ids.hq_update,line_no=stktrn_ids.line_no,item_uom=stktrn_ids.item_uom,
                                    item_batch=stktrn_ids.item_batch,mov_type=stktrn_ids.mov_type,item_batch_cost=stktrn_ids.item_batch_cost,
                                    stock_in=stktrn_ids.stock_in,trans_package_line_no=stktrn_ids.trans_package_line_no).save()
                        
                        #elif d.itemcart.type == 'Top Up':
                        elif d.record_detail_type == 'TP PRODUCT':
                            dtacc_ids = DepositAccount.objects.filter(ref_code=haudobj.sa_transacno,sa_status='SA',type='Top Up',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                        
                            for dt in dtacc_ids:
                                balance = dt.balance - dt.amount
                                outstanding = dt.outstanding + dt.amount

                                DepositAccount(cust_code=dt.cust_code,type=dt.type,amount=-float("{:.2f}".format(float(dt.amount))) if dt.amount else 0,
                                balance="{:.2f}".format(float(balance)),user_name=dt.user_name,qty=-dt.qty,outstanding="{:.2f}".format(float(outstanding)),
                                deposit="{:.2f}".format(float(dt.deposit)),cas_name=dt.cas_name,sa_staffno=dt.sa_staffno,
                                sa_staffname=dt.sa_staffname,deposit_type=dt.deposit_type,sa_transacno=dt.sa_transacno,
                                description=dt.description,ref_code=sa_transacno,sa_status="VT",item_barcode=dt.item_barcode,
                                item_description=dt.item_description,treat_code=dt.treat_code,void_link=dt.void_link,
                                lpackage=dt.lpackage,package_code=dt.package_code,dt_lineno=dt.dt_lineno,Cust_Codeid=dt.Cust_Codeid,
                                Site_Codeid=dt.Site_Codeid,site_code=dt.site_code,Item_Codeid=dt.Item_Codeid,item_code=dt.item_code,
                                ref_transacno=dt.ref_transacno,ref_productcode=dt.ref_productcode).save()

                    elif (d.record_detail_type == 'PREPAID' or d.record_detail_type == 'TP PREPAID') :
                    # elif int(d.itemcart.itemcodeid.item_div) == 5:
                        #if d.itemcart.type == 'Deposit':
                        if d.record_detail_type == 'PREPAID':
                            pacc_ids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,sa_status='DEPOSIT',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)

                            for pa in pacc_ids:
                                PrepaidAccount.objects.filter(pk=pa.pk).update(remain=0.0,status=False,sa_status="VT",updated_at=timezone.now(),
                                cust_code=haudobj.sa_custno,site_code=site.itemsite_code)

                        #elif d.itemcart.type == 'Top Up':
                        elif d.record_detail_type == 'PREPAID':
                            ptacc_ids = PrepaidAccount.objects.filter(topup_no=haudobj.sa_transacno,sa_status='TOPUP',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                            
                            for pt in ptacc_ids:

                                remain = float(pt.remain) - float(pt.topup_amt)
                                outstanding = pt.outstanding + pt.topup_amt
                                pac_lastid = PrepaidAccount.objects.filter(pp_no=pt.pp_no,line_no=pt.line_no,
                                cust_code=haudobj.sa_custno,site_code=site.itemsite_code,status=True).first()

                                if pac_lastid:
                                    # print(pac_lastid.pp_no,"topup")
                                    remain = float(pac_lastid.remain) - float(pt.topup_amt)
                                    outstanding = pac_lastid.outstanding + pt.topup_amt
                                    # PrepaidAccount.objects.filter(pk=pac_lastid.pk).update(status=False)
                                    # PrepaidAccount.objects.filter(pp_no=pa.pp_no,line_no=pa.line_no).update(status=False)

                                # PrepaidAccount.objects.filter(pk=pt.pk).update(status=False,updated_at=timezone.now())
                                PrepaidAccount.objects.filter(pp_no=pt.pp_no,line_no=pt.line_no).update(status=False,updated_at=timezone.now())
                                #sa_status='TOPUP',exp_status=pt.exp_status,voucher_no=pt.voucher_no,isvoucher=pt.isvoucher,

                                # remain = pt.remain - pt.topup_amt
                                # outstanding = pt.outstanding + pt.topup_amt
                                PrepaidAccount(pp_no=pt.pp_no,pp_type=pt.pp_type,pp_desc=pt.pp_desc,exp_date=pt.exp_date,
                                cust_code=pt.cust_code,cust_name=pt.cust_name,pp_amt=pt.pp_amt,pp_bonus=pt.pp_bonus,
                                pp_total=pt.pp_total,transac_no=pt.transac_no,item_no=pt.item_no,use_amt=pt.use_amt,
                                remain=remain,ref1=pt.ref1,ref2=pt.ref2,status=True,site_code=pt.site_code,
                                sa_status='VT',exp_status=pt.exp_status,voucher_no=pt.voucher_no,isvoucher=pt.isvoucher,
                                has_deposit=pt.has_deposit,topup_amt=-pt.topup_amt,outstanding=outstanding,
                                active_deposit_bonus=pt.active_deposit_bonus,topup_no=sa_transacno,topup_date=pt.topup_date,
                                line_no=pt.line_no,staff_name=pt.staff_name,staff_no=pt.staff_no,pp_type2=pt.pp_type2,
                                condition_type1=pt.condition_type1,pos_daud_lineno=pt.pos_daud_lineno,mac_uid_ref=pt.mac_uid_ref,
                                lpackage=pt.lpackage,package_code=pt.package_code,package_code_lineno=pt.package_code_lineno,
                                prepaid_disc_type=pt.prepaid_disc_type,prepaid_disc_percent=pt.prepaid_disc_percent,
                                Cust_Codeid=pt.Cust_Codeid,Site_Codeid=pt.Site_Codeid,Item_Codeid=pt.Item_Codeid,
                                item_code=pt.item_code).save()

                h = haudobj 
                # void_obj[0].reason_desc if void_obj else None
                PosHaud.objects.filter(pk=h.pk).update(isvoid=True,void_refno=sa_transacno)
                total_outstanding = h.total_outstanding + h.sa_transacamt
                haud = PosHaud(cas_name=fmspw[0].pw_userlogin,sa_transacno=sa_transacno,sa_status="VT",
                sa_remark=h.sa_remark,sa_totamt=-float("{:.2f}".format(float(h.sa_totamt))),sa_totqty=-h.sa_totqty,sa_totdisc=-float("{:.2f}".format(float(h.sa_totdisc))) if h.sa_totdisc else 0,
                sa_totgst=-float("{:.2f}".format(float(h.sa_totgst))) if h.sa_totgst else None,sa_totservice=h.sa_totservice if h.sa_totservice else None,sa_amtret=h.sa_amtret if h.sa_amtret else None,sa_staffnoid=h.sa_staffnoid,
                sa_staffno=h.sa_staffno,sa_staffname=h.sa_staffname,sa_custnoid=h.sa_custnoid,sa_custno=h.sa_custno,
                sa_custname=h.sa_custname,sa_reason=None,sa_discuser=h.sa_discuser,sa_discno=h.sa_discno,
                sa_discdesc=h.sa_discdesc,sa_discvalue=h.sa_discvalue,sa_discamt=-float("{:.2f}".format(float(h.sa_discamt))) if h.sa_discamt else 0,sa_disctotal=-float("{:.2f}".format(float(h.sa_disctotal))) if h.sa_disctotal else 0,
                ItemSite_Codeid=h.ItemSite_Codeid,itemsite_code=h.itemsite_code,sa_cardno=h.sa_cardno,seat_no=h.seat_no,
                sa_depositamt=-h.sa_depositamt,sa_chargeamt=None,isvoid=True,void_refno=h.sa_transacno,
                payment_remarks=h.payment_remarks,next_payment=h.next_payment,next_appt=h.next_appt,
                sa_transacamt=h.sa_transacamt,appt_time=h.appt_time,hold_item=h.hold_item,sa_discecard=h.sa_discecard,
                holditemqty=h.holditemqty,walkin=h.walkin,cust_sig=h.cust_sig,sa_round="{:.2f}".format(float(h.sa_round)) if h.sa_round else None,
                total_outstanding="{:.2f}".format(float(total_outstanding)) if total_outstanding else None,trans_user_login=h.trans_user_login,
                trans_user_loginid=h.trans_user_loginid,sa_transacno_ref=sa_transacno_ref,
                sa_transacno_type='Void Transaction',cust_sig_path=h.cust_sig_path,sa_transacno_title="VOID",
                issuestrans_user_login=h.trans_user_login)
                haud.save()

                if haud.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()
                    refcontrol_obj.control_no = int(refcontrol_obj.control_no) + 1
                    refcontrol_obj.save()
                    finalsatrasc = haud.sa_transacno

                cart_ids = ItemCart.objects.filter(isactive=True,cart_id=cart_id,cart_status="Inprogress",
                sitecode=site.itemsite_code,cart_date=date.today(),cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx)
                for cart in cart_ids:
                    ItemCart.objects.filter(pk=cart.pk).update(cart_status='Completed',quantity=-cart.quantity)

                result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False, 'data':{'sa_transacno':finalsatrasc if finalsatrasc else None}}
                return Response(data=result, status=status.HTTP_200_OK)
        
            elif haudobj.sa_transacno_type == 'Redeem Service':
                for ta in taud_ids:
                    taud = PosTaud(sa_transacno=sa_transacno,pay_groupid=ta.pay_groupid,pay_group=ta.pay_group,
                    pay_typeid=ta.pay_typeid,pay_type=ta.pay_type,pay_desc=ta.pay_desc,pay_tendamt=ta.pay_tendamt,
                    pay_tendrate=ta.pay_tendrate,pay_tendcurr=ta.pay_tendcurr,pay_amt=ta.pay_amt,pay_amtrate=ta.pay_amtrate,
                    pay_amtcurr=ta.pay_amtcurr,pay_rem1=ta.pay_rem1,pay_rem2=ta.pay_rem2,pay_rem3=ta.pay_rem3,pay_rem4=ta.pay_rem4,
                    pay_status=ta.pay_status,pay_actamt=ta.pay_actamt,ItemSIte_Codeid=ta.ItemSIte_Codeid,
                    itemsite_code=ta.itemsite_code,paychange=ta.paychange,dt_lineno=ta.dt_lineno,pay_gst_amt_collect=ta.pay_gst_amt_collect,
                    pay_gst=ta.pay_gst,posdaudlineno=ta.posdaudlineno,posdaudlineamountassign=ta.posdaudlineamountassign,
                    posdaudlineamountused=ta.posdaudlineamountused,voucher_name=ta.voucher_name,pp_bal=ta.pp_bal,
                    billed_by=ta.billed_by,subtotal=ta.subtotal,tax=ta.tax,discount_amt=ta.discount_amt,
                    billable_amount=ta.billable_amount,credit_debit=ta.credit_debit,points=ta.points,prepaid=ta.prepaid,
                    pay_premise=ta.pay_premise,is_voucher=ta.is_voucher,voucher_no=ta.voucher_no,voucher_amt=ta.voucher_amt)
                
                    taud.save()
                
                for m in multi_ids:
                    multi =  Multistaff(sa_transacno=sa_transacno,item_code=m.item_code,emp_code=m.emp_code,
                    ratio=m.ratio,salesamt=-float("{:.2f}".format(float(m.salesamt))) if m.salesamt else 0,type=m.type,isdelete=m.isdelete,role=m.role,dt_lineno=m.dt_lineno,
                    level_group_code=m.level_group_code) 
                    multi.save()

                for da in daud_ids:
                    if float(da.dt_discpercent) > 0.0:
                        dt_discpercent = -da.dt_discpercent
                    else:
                        dt_discpercent = da.dt_discpercent    
                    
                    cart_obj = ItemCart.objects.filter(isactive=True,cart_id=cart_id,lineno=da.dt_lineno,
                    sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress",
                    cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx).first()

                    sales = "";service = ""
                    if cart_obj.sales_staff.all():
                        for i in cart_obj.sales_staff.all():
                            if sales == "":
                                sales = sales + i.emp_name
                            elif not sales == "":
                                sales = sales +","+ i.emp_name
                    if cart_obj.service_staff.all(): 
                        for s in cart_obj.service_staff.all():
                            if service == "":
                                service = service + s.emp_name
                            elif not service == "":
                                service = service +","+ s.emp_name 

                    daud = PosDaud(sa_transacno=sa_transacno,dt_status="VT",dt_itemnoid=da.dt_itemnoid,dt_itemno=da.dt_itemno,
                    dt_itemdesc=da.dt_itemdesc,dt_price=da.dt_price,dt_promoprice="{:.2f}".format(float(da.dt_promoprice)),dt_amt=-float("{:.2f}".format(float(da.dt_amt))) if da.dt_amt else 0,
                    dt_qty=-da.dt_qty,dt_discamt=-da.dt_discamt if float(da.dt_discamt) > 0.0 else da.dt_discamt, 
                    dt_discpercent=-da.dt_discpercent if float(da.dt_discpercent) > 0.0 else da.dt_discpercent,dt_discdesc=da.dt_discdesc,
                    dt_discno=da.dt_discno,dt_remark=da.dt_remark,dt_Staffnoid=da.dt_Staffnoid,dt_staffno=da.dt_staffno,
                    dt_staffname=da.dt_staffname,dt_reason=da.dt_reason,dt_discuser=da.dt_discuser,dt_combocode=da.dt_combocode,
                    ItemSite_Codeid=da.ItemSite_Codeid,itemsite_code=da.itemsite_code,dt_lineno=da.dt_lineno,
                    dt_stockupdate=da.dt_stockupdate,dt_stockremark=da.dt_stockremark,dt_uom=da.dt_uom,isfoc=da.isfoc,
                    item_remarks=da.item_remarks,next_payment=da.next_payment,next_appt=da.next_appt,dt_transacamt="{:.2f}".format(float(da.dt_transacamt)),
                    dt_deposit=-float("{:.2f}".format(float(da.dt_deposit))) if da.dt_deposit else 0,appt_time=da.appt_time,hold_item_out=da.hold_item_out,issue_date=da.issue_date,
                    hold_item=da.hold_item,holditemqty=da.holditemqty,st_ref_treatmentcode=da.st_ref_treatmentcode,
                    item_status_code=da.item_status_code,first_trmt_done=da.first_trmt_done,
                    first_trmt_done_staff_code=da.first_trmt_done_staff_code,first_trmt_done_staff_name=da.first_trmt_done_staff_name,
                    record_detail_type=da.record_detail_type,trmt_done_staff_code=da.trmt_done_staff_code,trmt_done_staff_name=da.trmt_done_staff_name,
                    trmt_done_id=da.trmt_done_id,trmt_done_type=da.trmt_done_type,topup_service_trmt_code=da.topup_service_trmt_code,
                    topup_product_treat_code=da.topup_product_treat_code,topup_prepaid_trans_code=da.topup_prepaid_trans_code,
                    topup_prepaid_type_code=da.topup_prepaid_type_code,voucher_link_cust=da.voucher_link_cust,
                    voucher_no=da.voucher_no,update_prepaid_bonus=da.update_prepaid_bonus,deduct_commission=da.deduct_commission,
                    deduct_comm_refline=da.deduct_comm_refline,gst_amt_collect=-float("{:.2f}".format(float(da.gst_amt_collect))) if da.gst_amt_collect else 0,
                    topup_prepaid_pos_trans_lineno=da.topup_prepaid_pos_trans_lineno,open_pp_uid_ref=None,compound_code=da.compound_code,
                    topup_outstanding=da.topup_outstanding,t1_tax_code=da.t1_tax_code,t1_tax_amt=da.t1_tax_amt,
                    t2_tax_code=da.t2_tax_code,t2_tax_amt=da.t2_tax_amt,dt_grossamt=da.dt_grossamt,dt_topup_old_outs_amt=da.dt_topup_old_outs_amt,
                    dt_topup_new_outs_amt=da.dt_topup_new_outs_amt,dt_td_tax_amt=da.dt_td_tax_amt,earnedpoints=da.earnedpoints,
                    earnedtype=da.earnedtype,redeempoints=da.redeempoints,redeemtype=da.redeemtype,itemcart=cart_obj,
                    staffs=sales +" "+"/"+" "+ service)
                    daud.save()

                    #if int(da.itemcart.itemcodeid.item_div) == 3:
                    if 1 == 1:
                        if da.record_detail_type == 'TD':
                            sacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                        
                            #description = da.itemcart.itemcodeid.item_name+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)
                            description = da.dt_itemdesc +" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)
                            
                            #Treatment.objects.filter(pk=da.itemcart.treatment.pk).update(course=description,status="Open",
                            Treatment.objects.filter(treatment_code=da.trmt_done_id).update(course=description,status="Open",
                            trmt_room_code=None,treatment_count_done=0)
                            
                            for sa in sacc_ids:
                                master_ids = Treatment_Master.objects.filter(sa_transacno=sa.ref_transacno,
                                treatment_code=sa.ref_no,site_code=site.itemsite_code).update(status="Cancel")
                                appt_ids = Appointment.objects.filter(sa_transacno=sa.ref_transacno,
                                treatmentcode=sa.ref_no,itemsite_code=site.itemsite_code).update(appt_status="Cancelled")
    
                                TreatmentAccount.objects.filter(pk=sa.pk).update(sa_status='VOID')
                                # type__in=('Deposit', 'Top Up')
                                olacc_ids = TreatmentAccount.objects.filter(ref_transacno=sa.ref_transacno,
                                treatment_parentcode=sa.treatment_parentcode,cust_code=haudobj.sa_custno,site_code=site.itemsite_code).order_by('id').exclude(type='Sales').last()

                                TreatmentAccount(Cust_Codeid=sa.Cust_Codeid,cust_code=sa.cust_code,
                                #description=description,ref_no=sa.ref_no,type=sa.type,amount="{:.2f}".format(float(da.itemcart.treatment.unit_amount)),
                                description=description,ref_no=sa.ref_no,type=sa.type,amount="{:.2f}".format(float(olacc_ids.amount)),
                                balance="{:.2f}".format(float(olacc_ids.balance)),user_name=sa.user_name,User_Nameid=sa.User_Nameid,
                                ref_transacno=sa.ref_transacno,sa_transacno=sa_transacno,qty=sa.qty,
                                outstanding="{:.2f}".format(float(olacc_ids.outstanding)) if olacc_ids.outstanding else None,deposit=-float("{:.2f}".format(float(sa.deposit))) if sa.deposit else 0,treatment_parentcode=sa.treatment_parentcode,
                                treatment_code=sa.treatment_code,sa_status="SA",cas_name=fmspw[0].pw_userlogin,sa_staffno=sa.sa_staffno,
                                sa_staffname=sa.sa_staffname,next_paydate=sa.next_paydate,hasduedate=sa.hasduedate,
                                dt_lineno=sa.dt_lineno,lpackage=sa.lpackage,package_code=sa.package_code,Site_Codeid=sa.Site_Codeid,
                                site_code=sa.site_code,treat_code=sa.treat_code,focreason=sa.focreason,itemcart=cart_obj).save()

                            ihelper_ids = ItemHelper.objects.filter(helper_transacno=haudobj.sa_transacno,
                            site_code=site.itemsite_code)
                            for hlp in ihelper_ids:
                                ItemHelper(item_code=hlp.item_code,item_name=hlp.item_name,line_no=hlp.line_no,
                                sa_transacno=hlp.sa_transacno,amount=-float("{:.2f}".format(float(hlp.amount))) if hlp.amount else 0,helper_name=hlp.helper_name,
                                helper_code=hlp.helper_code,site_code=hlp.site_code,share_amt=-hlp.share_amt,
                                helper_transacno=sa_transacno,system_remark=hlp.system_remark,
                                wp1=hlp.wp1,wp2=hlp.wp2,wp3=hlp.wp3,td_type_code=hlp.td_type_code,
                                td_type_short_desc=hlp.td_type_short_desc).save()

                h = haudobj 
                # void_obj[0].reason_desc if void_obj else None
                PosHaud.objects.filter(pk=h.pk).update(isvoid=True,void_refno=sa_transacno)
                haud = PosHaud(cas_name=fmspw[0].pw_userlogin,sa_transacno=sa_transacno,sa_status="VT",
                sa_remark=h.sa_remark,sa_totamt="{:.2f}".format(float(h.sa_totamt)),sa_totqty=h.sa_totqty,sa_totdisc="{:.2f}".format(float(h.sa_totdisc)) if h.sa_totdisc else 0,
                sa_totgst="{:.2f}".format(float(h.sa_totgst)) if h.sa_totgst else 0,sa_totservice="{:.2f}".format(float(h.sa_totservice)) if h.sa_totservice else 0,sa_amtret="{:.2f}".format(float(h.sa_amtret)) if h.sa_amtret else 0 ,sa_staffnoid=h.sa_staffnoid,
                sa_staffno=h.sa_staffno,sa_staffname=h.sa_staffname,sa_custnoid=h.sa_custnoid,sa_custno=h.sa_custno,
                sa_custname=h.sa_custname,sa_reason=None,sa_discuser=h.sa_discuser,sa_discno=h.sa_discno,
                sa_discdesc=h.sa_discdesc,sa_discvalue=h.sa_discvalue,sa_discamt="{:.2f}".format(float(h.sa_discamt)) if h.sa_discamt else 0,sa_disctotal="{:.2f}".format(float(h.sa_disctotal)) if h.sa_disctotal else 0,
                ItemSite_Codeid=h.ItemSite_Codeid,itemsite_code=h.itemsite_code,sa_cardno=h.sa_cardno,seat_no=h.seat_no,
                sa_depositamt="{:.2f}".format(float(h.sa_depositamt)) if h.sa_depositamt else 0,sa_chargeamt=None,isvoid=True,void_refno=h.sa_transacno,
                payment_remarks=h.payment_remarks,next_payment=h.next_payment,next_appt=h.next_appt,
                sa_transacamt="{:.2f}".format(float(h.sa_transacamt)) if h.sa_transacamt else 0,appt_time=h.appt_time,hold_item=h.hold_item,sa_discecard=h.sa_discecard,
                holditemqty=h.holditemqty,walkin=h.walkin,cust_sig=h.cust_sig,sa_round="{:.2f}".format(float(h.sa_round)) if h.sa_round else 0,
                total_outstanding="{:.2f}".format(float(h.total_outstanding)) if h.total_outstanding else 0,trans_user_login=h.trans_user_login,
                trans_user_loginid=h.trans_user_loginid,sa_transacno_ref=sa_transacno_ref,
                sa_transacno_type='Void Transaction',cust_sig_path=h.cust_sig_path,sa_transacno_title="VOID",
                issuestrans_user_login=fmspw[0].pw_userlogin)
                haud.save()

                if haud.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()
                    refcontrol_obj.control_no = int(refcontrol_obj.control_no) + 1
                    refcontrol_obj.save()
                    finalsatrasc = haud.sa_transacno

                cart_ids = ItemCart.objects.filter(isactive=True,cart_id=cart_id,cart_status="Inprogress",
                sitecode=site.itemsite_code,cart_date=date.today(),cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx)
                for cart in cart_ids:
                    ItemCart.objects.filter(pk=cart.pk).update(cart_status='Completed',quantity=-cart.quantity)
        
                result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False,
                'data':{'sa_transacno':finalsatrasc if finalsatrasc else None}}
                return Response(data=result, status=status.HTTP_200_OK)
        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)
                    

class VoidCheck(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = VoidListSerializer

    def list(self, request):
        # try:
            if str(self.request.GET.get('cust_id',None)) != "undefined":
                if isinstance(int(self.request.GET.get('cust_id',None)), int):
                    fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
                    site = fmspw.loginsite
                    cust_id = self.request.GET.get('cust_id',None)
                    cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
                    if cust_obj is None:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give customer id!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    if str(self.request.GET.get('cust_id',None)) == "undefined":
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select customer!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)         
                    
                    control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not control_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                        raise serializers.ValidationError(result)

                    # poshdr_id = self.request.GET.get('poshdr_id',None)
                
                    # queryset = ItemCart.objects.filter(isactive=True,cart_date=date.today(),customercode=cust_obj.cust_code,
                    # sitecode=site.itemsite_code,cart_status="Inprogress",is_payment=False).exclude(type__in=type_tx)
                    #sa_date__date=date.today()

                    queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    isvoid=False,ItemSite_Codeid__pk=site.pk).only('sa_custno','isvoid','cart_id',
                    'itemsite_code').exclude(cart_id=None).order_by('pk')
                    # print(queryset,"queryset")
                    oldidcart = list(set([q.cart_id for q in queryset if q.cart_id]))
                    # print(oldidcart,"oldidcart")

                    old_cart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                    cart_id__in=oldidcart,sitecode=site.itemsite_code,isactive=True,
                    cart_status="Inprogress").filter(~Q(cart_date=date.today())).exclude(type__in=type_tx).order_by('pk')
                    todidcart = list(set([t.cart_id for t in old_cart_ids if t.cart_id]))
                    # print(todidcart,"todidcart")
                    
                    if queryset:
                        if len(queryset) >= 1:
                            #previous record
                            query_set = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                            isvoid=False,ItemSite_Codeid__pk=site.pk,cart_id__in=todidcart).only('sa_custno','isvoid',
                            'cart_id','itemsite_code').exclude(cart_id=None).order_by('pk')
                            # print(query_set,"query_set")
                            
                            for q in query_set:
                                # active / Inactive , not today rec
                                q.cart_id = None
                                q.save()
                                idscart = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                cart_id__in=todidcart,sitecode=site.itemsite_code,
                                cart_status="Inprogress").filter(~Q(cart_date=date.today())).exclude(type__in=type_tx).delete()
                                # print(idscart,"idscart")

                            #today record
                            querysetafter = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                            isvoid=False,ItemSite_Codeid__pk=site.pk).only('sa_custno','isvoid','cart_id',
                            'itemsite_code').exclude(cart_id=None).order_by('pk')

                            idcart = list(set([e.cart_id for e in querysetafter if e.cart_id]))

                            idscart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                            cart_id__in=idcart,sitecode=site.itemsite_code,cart_date=date.today(),
                            isactive=True,cart_status="Inprogress").exclude(type__in=type_tx).order_by('pk')
                            # print(idscart_ids,"idscart_ids")
                            
                            if len(querysetafter) > 1:
                                if idscart_ids:
                                    lastrec = idscart_ids.last()
                                    # print(lastrec,"lastrec")
                                    del_query_set = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                                    isvoid=False,ItemSite_Codeid__pk=site.pk).only('sa_custno','isvoid',
                                    'cart_id','itemsite_code').filter(~Q(cart_id=lastrec.cart_id)).exclude(cart_id=None).order_by('pk')
                                    # print(del_query_set,"del_query_set")

                                    for dq in del_query_set:
                                        dq.cart_id = None
                                        dq.save()
                                        idscart = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                        cart_id=dq.cart_id,sitecode=site.itemsite_code,cart_date=date.today(),
                                        cart_status="Inprogress").filter(~Q(cart_id=lastrec.cart_id)).exclude(type__in=type_tx).delete()
                                        
                            
                            cartre = ItemCart.objects.filter(sitecodeid=site).order_by('cart_id')
                            final = list(set([r.cart_id for r in cartre]))
                            code_site = site.itemsite_code
                            # print(code_site,"code_site")
                            prefix = control_obj.control_prefix

                            clst = []
                            if final != []:
                                for f in final:
                                    newstr = f.replace(prefix,"")
                                    new_str = newstr.replace(code_site, "")
                                    clst.append(new_str)
                                    clst.sort(reverse=True)

                                # print(clst,"clst")
                                cart_id = int(clst[0][-6:]) + 1
                                
                                control_obj.control_no = str(cart_id)
                                control_obj.save()
                            
                            last_rec = idscart_ids.last()
                            if last_rec:
                                ids_cart_ids = ItemCart.objects.filter(customercode=cust_obj.cust_code,
                                cart_id=last_rec.cart_id,sitecode=site.itemsite_code,cart_date=date.today(),
                                isactive=True,cart_status="Inprogress").exclude(type__in=type_tx).order_by('pk')
                                # print(ids_cart_ids,"ids_cart_ids")
                                if ids_cart_ids:
                                    finalquery = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                                    isvoid=False,ItemSite_Codeid__pk=site.pk,cart_id=last_rec.cart_id).only('sa_custno','isvoid','cart_id',
                                    'itemsite_code').exclude(cart_id=None).order_by('pk')
                                    if finalquery:
                                        serializer = VoidListSerializer(finalquery, many=True)
                                        result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
                                    else:
                                        result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                                else:
                                    result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                            else:
                                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                    else:
                        result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
                    return Response(data=result, status=status.HTTP_200_OK) 
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Data",'error': False, "data":[]}
                return Response(data=result, status=status.HTTP_200_OK)           
        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)

class VoidCancel(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = VoidCancelSerializer
    
    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            serializer = self.get_serializer(data=request.data)
            # print(serializer,"serializer")
            if serializer.is_valid():
                # print(request.data,"request.data")
                cart_id = request.data['cart_id']
                # print(cart_id,"cart_id")
                if cart_id:
                    # print(cart_id,"cart_id")
                    bro_ids = ItemCart.objects.filter(cart_id=cart_id,sitecode=site.itemsite_code,
                    cart_status="Inprogress",cart_date=date.today())
                    if bro_ids:
                        queryset = PosHaud.objects.filter(cart_id=cart_id,sa_custno=bro_ids[0].customercode,
                        isvoid=False,ItemSite_Codeid__pk=site.pk).only('isvoid','cart_id',
                        'sa_custno','itemsite_code').exclude(cart_id=None).order_by('pk')
                        if queryset:
                            queryset[0].cart_id = None
                            queryset[0].save()
                        #cart_date=date.today()
                        ids_cart = ItemCart.objects.filter(cart_id=cart_id,cust_noid=bro_ids[0].cust_noid,
                        sitecode=site.itemsite_code,cart_status="Inprogress").exclude(type__in=type_tx).delete()
                        result = {'status': status.HTTP_200_OK,"message":"Void Cancelled Successfully",'error': False}
                        return Response(data=result, status=status.HTTP_200_OK) 
                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"ItemCart is not in Inprogress so cant delete!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID !!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST) 
                                
            else:
                data = serializer.errors
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['cart_id'][0],'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
            
            

class VoidReasonViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = VoidReason.objects.filter(isactive=True).order_by('pk')
    serializer_class = VoidReasonSerializer

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
                 

class TreatmentAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentAccSerializer

    def list(self, request):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
        site = fmspw.loginsite
        cust_id = self.request.GET.get('cust_id',None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).only('pk','cust_isactive').first()
        if not cust_obj:
            result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
            return Response(data=result, status=status.HTTP_200_OK)  

        if self.request.GET.get('year',None):
            year = self.request.GET.get('year',None)
            if year != "All":
                # queryset = TreatmentAccount.objects.filter(site_code=fmspw.loginsite.itemsite_code,cust_code=cust_obj.cust_code,sa_date__year=year,type='Deposit').only('site_code','cust_code','sa_date','type').order_by('pk')
                queryset = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,sa_date__year=year,type='Deposit').only('site_code','cust_code','sa_date','type').order_by('pk')
            else:
                # queryset = TreatmentAccount.objects.filter(site_code=fmspw.loginsite.itemsite_code,cust_code=cust_obj.cust_code,type='Deposit').only('site_code','cust_code','type').order_by('pk')
                queryset = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,type='Deposit').only('site_code','cust_code','type').order_by('pk')
        else:
            result = {'status': status.HTTP_200_OK,"message":"Please give year!!",'error': True} 
            return Response(data=result, status=status.HTTP_200_OK)  

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            lst = []; id_lst = []; balance = 0; outstanding = 0
            for data in serializer.data:
                trobj = TreatmentAccount.objects.filter(pk=data["id"]).first()
                # trmids = Treatment.objects.filter(treatment_account__pk=trobj.pk,site_code=site.itemsite_code).only('treatment_account').first()
                # trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode).only('treatment_parentcode').first()
                trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode,status='Open').only('treatment_parentcode').first()
                # print(data,"data")
                # if data["id"]:
                if data["id"] not in id_lst:
                    id_lst.append(data["id"])

                # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                # sa_transacno=trobj.sa_transacno,sa_transacno_type='Receipt',
                # ItemSite_Codeid__pk=fmspw.loginsite.pk).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()

                pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                sa_transacno=trobj.sa_transacno).only('sa_custno','sa_transacno').order_by('pk').first()

                if pos_haud:
                    # data['transaction'] = pos_haud.sa_transacno_ref
                    data['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                    if pos_haud.sa_date:
                        splt = str(pos_haud.sa_date).split(" ")
                        data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                    
                    data['description'] = ""
                    if trmids:
                        if trmids.course:
                            data['description'] = trmids.course 
                            data['qty'] = trmids.times + "/" + trmids.treatment_no
                            
                    # sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                    # treatment_parentcode=data["treatment_parentcode"],site_code=trobj.site_code,
                    # type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('balance'))
                    
                    # sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                    # treatment_parentcode=data["treatment_parentcode"],
                    # type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('balance'))

                    sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                    treatment_parentcode=data["treatment_parentcode"],
                    type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').last()

                    if sumacc_ids:
                        # data["payment"] = "{:.2f}".format(float(sumacc_ids['balance__sum']))
                        data["payment"] = "{:.2f}".format(float(sumacc_ids.balance))
                    else:
                        data["payment"] = "0.00"

                    # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                    # treatment_parentcode=data["treatment_parentcode"],site_code=trobj.site_code
                    # ).only('ref_transacno','treatment_parentcode','site_code').last()
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                    treatment_parentcode=data["treatment_parentcode"]
                    ).only('ref_transacno','treatment_parentcode','site_code').order_by('sa_date').last()
                    if acc_ids.balance:
                        data["balance"] = "{:.2f}".format(float(acc_ids.balance))
                        balance += acc_ids.balance
                    else:
                        data["balance"] = "0.00"

                    if acc_ids.outstanding:   
                        data["outstanding"] = "{:.2f}".format(float(acc_ids.outstanding))
                        outstanding += acc_ids.outstanding
                    else:
                        data["outstanding"] = "0.00"
                    lst.append(data)

            if lst != []:
                header_data = {"balance" : "{:.2f}".format(float(balance)),
                "outstanding" : "{:.2f}".format(float(outstanding)), "treatment_count" : len(id_lst)}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'header_data':header_data, 'data': serializer.data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            return TreatmentAccount.objects.get(pk=pk)
        except TreatmentAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        account = self.get_object(pk)
        # queryset = TreatmentAccount.objects.filter(ref_transacno=account.sa_transacno,
        # treatment_parentcode=account.treatment_parentcode,site_code=account.site_code
        # ).only('ref_transacno','treatment_parentcode','site_code').order_by('pk')
        queryset = TreatmentAccount.objects.filter(ref_transacno=account.sa_transacno,
        treatment_parentcode=account.treatment_parentcode
        ).only('ref_transacno','treatment_parentcode','site_code').order_by('pk')
        if queryset:
            last = queryset.last()
            serializer = self.get_serializer(queryset, many=True)

            for v in serializer.data:
                v.pop('payment')
                if v['sa_date']:
                    splt = str(v['sa_date']).split('T')
                    v['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

                trobj = TreatmentAccount.objects.filter(pk=v["id"]).only('pk').first()
                v['type'] = trobj.type
                if trobj.amount:
                    v["amount"] = "{:.2f}".format(float(trobj.amount))
                else:
                    v["amount"] = "0.00"    
                if v["balance"]:
                    v["balance"] = "{:.2f}".format(float(v['balance']))
                else:
                    v["balance"] = "0.00"
                if v["outstanding"]:
                    v["outstanding"] = "{:.2f}".format(float(v['outstanding']))
                else:
                    v["outstanding"] = "0.00"

                pos_haud = PosHaud.objects.filter(sa_transacno=trobj.sa_transacno).only('sa_custno','sa_transacno').order_by('pk').first()

                if pos_haud:
                    v['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
            'header_data':{'credit_balance':last.balance if last.balance else "0.00",
            'outstanding_balance':last.outstanding if last.outstanding else "0.00"}, 
            'data': serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)


class CreditNoteListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CreditNoteSerializer

    def list(self, request):
        cust_id = self.request.GET.get('cust_id', None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
        if cust_obj is None:
            result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_200_OK)
        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        
        is_all = self.request.GET.get('is_all', None)
        if is_all:
            # queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code).only('cust_code').order_by('pk')
            queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code).only('cust_code').order_by('pk')
        else:
            # queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code, status='OPEN',site_code=site.itemsite_code).only('cust_code','status').order_by('pk')
            queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code, status='OPEN').only('cust_code','status').order_by('pk')
        
        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            lst = []
            for data in serializer.data:
                if data['sa_date']:
                    splt = str(data['sa_date']).split('T')
                    data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

                crdobj = CreditNote.objects.filter(pk=data["id"]).first()
                # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code, sa_transacno=crdobj.sa_transacno,
                # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk).order_by('pk').first()
                pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code, sa_transacno=crdobj.sa_transacno,
                sa_transacno_type='Receipt').order_by('pk').first()
                if pos_haud:
                    data['transaction'] = pos_haud.sa_transacno_ref
                if data["amount"]:
                    data["amount"] = "{:.2f}".format(float(data['amount']))
                else:
                    data["amount"] = "0.00"    
                if data["balance"]:
                    data["balance"] = "{:.2f}".format(float(data['balance']))
                else:
                    data["balance"] = "0.00"    
                lst.append(data)
            result = {'status': status.HTTP_200_OK, "message": "Listed Succesfully", 'error': False, 'data': lst}
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
        return Response(data=result, status=status.HTTP_200_OK)

    def get_object(self, pk):
        try:
            return CreditNote.objects.get(pk=pk)
        except CreditNote.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        creditnote = self.get_object(pk)
        serializer = CreditNoteAdjustSerializer(creditnote,context={'request': self.request})
        adjustamt = 0.00
        serializer.data['adjust_amount'] = "{:.2f}".format(float(adjustamt))
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
        'data': serializer.data}
        return Response(result, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        new_balance = self.request.data.get('new_balance', None)
        refund_amt = self.request.data.get('refund_amt', None) 
        
        if new_balance is None and refund_amt is None:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Please give New Balance or refund amount!!", 'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        creditnt = self.get_object(pk)
        #front calculation
        #adjust_amount = new_balance - creditnt.balance
        balance = creditnt.balance
      
        serializer = CreditNoteAdjustSerializer(creditnt, data=request.data, partial=True, context={'request': self.request})
        if serializer.is_valid():
            if float(new_balance) == float(refund_amt):
                if float(new_balance) == balance:
                    result = {'status': status.HTTP_400_BAD_REQUEST, "message": "New Balance and Refund Amt, Existing credit note Balance should not be same!!", 'error': True}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if float(refund_amt) > float(balance):
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Refund Amt Should not be greater than new balance!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            control_obj = ControlNo.objects.filter(control_description__iexact="Refund CN",Site_Codeid__pk=site.pk).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Refund CN Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)

            refund_code = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)

            adjustamt = float(balance) - float(new_balance)

            if not refund_amt is None and float(refund_amt) > 0.00:
                amount = refund_amt
            elif not refund_amt is None and float(refund_amt) == 0.00:  
                amount = 0.00
    
            # print(amount,balance,adjustamt,new_balance,"daa")   
            cn_refund = CnRefund.objects.create(rfn_trans_no=refund_code,cn_no=creditnt.credit_code,
            site_code=site.itemsite_code,amount=amount,staff_code=fmspw[0].emp_code,transac_no=creditnt.sa_transacno,
            rfn_before_amt=balance,rfn_adjust_amt=adjustamt,rfn_new_amt=float(new_balance),
            rfn_date=timezone.now()) 

            if cn_refund.pk:
                control_obj.control_no = int(control_obj.control_no) + 1
                control_obj.save()

            if not new_balance is None and float(new_balance) > 0.00:
                serializer.save(balance=new_balance)
            elif not new_balance is None and float(new_balance) == 0.00:
                serializer.save(balance=new_balance,status="CLOSE")

            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
            return Response(result, status=status.HTTP_200_OK)

        result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
        return Response(result, status=status.HTTP_400_BAD_REQUEST)    
  

class ProductAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ProductAccSerializer

    def list(self, request):
        cust_id = self.request.GET.get('cust_id', None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
        if cust_obj is None:
            result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_200_OK)

        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
        site = fmspw.loginsite

        # queryset = DepositAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
        # type='Deposit').only('site_code','cust_code','type').order_by('pk')
        queryset = DepositAccount.objects.filter(cust_code=cust_obj.cust_code,
        type='Deposit').only('site_code','cust_code','type').order_by('pk')

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            lst = []; id_lst = []; balance = 0; outstanding = 0; hold_qty = 0
            for data in serializer.data:
                depobj = DepositAccount.objects.filter(pk=data["id"]).only('pk').first()
                if data["id"]:
                    id_lst.append(data["id"])

                # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                # sa_transacno=depobj.sa_transacno,sa_transacno_type='Receipt',
                # ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
                pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno=depobj.sa_transacno
                ).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
                if pos_haud:
                    data['transaction'] = pos_haud.sa_transacno_ref
                    if pos_haud.sa_date:
                        splt = str(pos_haud.sa_date).split(" ")
                        data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                    
                    if not data['package_code']:
                        data['package_code'] = ""

                    # acc_ids = DepositAccount.objects.filter(sa_transacno=depobj.sa_transacno,
                    # site_code=depobj.site_code,ref_productcode=depobj.ref_productcode
                    # ).only('sa_transacno','site_code','ref_productcode').last()
                    acc_ids = DepositAccount.objects.filter(sa_transacno=depobj.sa_transacno,
                    ref_productcode=depobj.ref_productcode
                    ).only('sa_transacno','site_code','ref_productcode').last()
                    if acc_ids.balance:
                        data["balance"] = "{:.2f}".format(float(acc_ids.balance))
                        balance += acc_ids.balance
                    else:
                        data["balance"] = "0.00"    
                    if acc_ids.outstanding:   
                        data["outstanding"] = "{:.2f}".format(float(acc_ids.outstanding))
                        outstanding += acc_ids.outstanding
                    else:
                        data["outstanding"] = "0.00"

                    # holdids = Holditemdetail.objects.filter(sa_transacno=depobj.sa_transacno,
                    # itemno=depobj.item_barcode,itemsite_code=site.itemsite_code,
                    # sa_custno=cust_obj.cust_code).only('sa_transacno','itemno').first()  
                    holdids = Holditemdetail.objects.filter(sa_transacno=depobj.sa_transacno,
                    itemno=depobj.item_barcode,
                    sa_custno=cust_obj.cust_code).only('sa_transacno','itemno').first()  
                    if holdids:
                        data['item_status'] = holdids.status if holdids.status else ""
                        hold_qty += holdids.holditemqty                    
                    else:
                        data['item_status'] = ""

                    lst.append(data)

            if lst != []:
                header_data = {"balance" : "{:.2f}".format(float(balance)), "totalholdqty" : hold_qty,
                "outstanding" : "{:.2f}".format(float(outstanding)), "totalproduct_count" : len(id_lst)}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'header_data':header_data, 'data': lst}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        
    
    def get_object(self, pk):
        try:
            return DepositAccount.objects.get(pk=pk)
        except DepositAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        account = self.get_object(pk)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        queryset = DepositAccount.objects.filter(sa_transacno=account.sa_transacno,
        site_code=account.site_code,ref_productcode=account.ref_productcode).only('sa_transacno',
        'site_code','ref_productcode').order_by('pk')
        if queryset:
            hold_qty = 0
            last = queryset.last()
            holdids = Holditemdetail.objects.filter(sa_transacno=account.sa_transacno,
            itemno=account.item_barcode,itemsite_code=site.itemsite_code,
            sa_custno=account.cust_code).only('sa_transacno','itemno','itemsite_code','sa_custno').first()  
            if holdids:
                hold_qty += holdids.holditemqty                    
                
            serializer = self.get_serializer(queryset, many=True)
            for v in serializer.data:
                v.pop('package_code');v.pop('item_description')
                if v['sa_date']:
                    splt = str(v['sa_date']).split('T')
                    v['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

                depobj = DepositAccount.objects.filter(pk=v["id"]).first()
                v['description'] = depobj.description # transaction
                v['type'] = depobj.type #treatment
                if depobj.amount:
                    v["payment"] = "{:.2f}".format(float(depobj.amount))
                else:
                    v["payment"] = "0.00"    
                if v["balance"]:
                    v["balance"] = "{:.2f}".format(float(v['balance']))
                else:
                    v["balance"] = "0.00"
                if v["outstanding"]:
                    v["outstanding"] = "{:.2f}".format(float(v['outstanding']))
                else:
                    v["outstanding"] = "0.00"

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
            'header_data':{'credit_balance':"{:.2f}".format(float(last.balance)) if last.balance else "0.00",
            'outstanding_balance':"{:.2f}".format(float(last.outstanding)) if last.outstanding else "0.00",
            "totalholdqty" : hold_qty,}, 
            'data': serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)


class PrepaidAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = PrepaidAccSerializer

    def list(self, request):
        cust_id = self.request.GET.get('cust_id', None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
        if cust_obj is None:
            result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_200_OK)

        fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
        site = fmspw.loginsite
        # print(site.itemsite_code,"site_code")
        is_all = self.request.GET.get('is_all',None)
        if is_all:
            # queryset = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
            # sa_status='DEPOSIT').only('site_code','cust_code','sa_status').order_by('pk')
            print(is_all,"is_all")
            queryset = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
            sa_status='DEPOSIT').only('site_code','cust_code','sa_status').order_by('pk')
        else:
            # queryset = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
            # sa_status='DEPOSIT',remain__gt=0).only('site_code','cust_code','sa_status').order_by('pk')
            queryset = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
            status=True,remain__gt=0).only('site_code','cust_code','sa_status').order_by('pk')

        if queryset:
            serializer = self.get_serializer(queryset, many=True)
            lst = []; id_lst = []; product_type = 0; service_type = 0; all_type = 0
            for data in serializer.data:
                data.pop('voucher_no'); data.pop('condition_type1')
                preobj = PrepaidAccount.objects.filter(pk=data["id"]).only('pk').first()
                if data["id"]:
                    id_lst.append(data["id"])

                # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                # sa_transacno=preobj.pp_no,sa_transacno_type='Receipt',
                # ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
                # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                # sa_transacno=preobj.pp_no,sa_transacno_type='Receipt'
                # ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
                pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno=preobj.pp_no
                ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
                if pos_haud:
                    data['prepaid'] = pos_haud.sa_transacno_ref

                    # last_acc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                    # site_code=preobj.site_code,status=True,line_no=preobj.line_no).only('pp_no','site_code','status','line_no').last()
                    if is_all:
                        last_acc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                        line_no=preobj.line_no).only('pp_no','site_code','status','line_no').last()
                    else:
                        last_acc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                        status=True,line_no=preobj.line_no).only('pp_no','site_code','status','line_no').last()

                    l_splt = str(data['last_update']).split("T")
                    data['last_update'] = datetime.datetime.strptime(str(l_splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")

                    if last_acc_ids:
                        if last_acc_ids.sa_date:
                            splt = str(last_acc_ids.sa_date).split(" ")
                            data['last_update'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                    
                    # oriacc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                    # site_code=preobj.site_code,sa_status='DEPOSIT',line_no=preobj.line_no).only('pp_no','site_code','sa_status','line_no').first()
                    oriacc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                    sa_status='DEPOSIT',line_no=preobj.line_no).only('pp_no','site_code','sa_status','line_no').first()
                    if oriacc_ids:
                        if oriacc_ids.sa_date:
                            #purchase date
                            splt_st = str(oriacc_ids.sa_date).split(" ")
                            data['sa_date'] = datetime.datetime.strptime(str(splt_st[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                    
                    if last_acc_ids:
                        if last_acc_ids.pp_type:
                            rangeobj = ItemRange.objects.filter(itm_code=last_acc_ids.pp_type).first()
                            if rangeobj:
                                data['type'] = rangeobj.itm_desc
                            else:
                                data['type'] = " "
    
                        if last_acc_ids.exp_date:
                            splt_ex = str(last_acc_ids.exp_date).split(" ")
                            data['exp_date'] = datetime.datetime.strptime(str(splt_ex[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        if last_acc_ids.exp_status:
                            if last_acc_ids.exp_status == True:
                                data['exp_status'] = "Open"
                            elif last_acc_ids.exp_status == False:
                                data['exp_status'] = "Expired"
                        else:
                            data['exp_status'] = ""        

                        if last_acc_ids.pp_amt:
                            data['pp_amt'] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                        if last_acc_ids.pp_bonus:
                            data['pp_bonus'] = "{:.2f}".format(float(last_acc_ids.pp_bonus))
                        if last_acc_ids.pp_total:
                            data['pp_total'] = "{:.2f}".format(float(last_acc_ids.pp_total))
                        if last_acc_ids.use_amt:
                            data['use_amt'] = "{:.2f}".format(float(last_acc_ids.use_amt ))
                        if last_acc_ids.remain:
                            data['remain'] = "{:.2f}".format(float(last_acc_ids.remain))
                    
                        data['voucher'] = "P.P"
                        if last_acc_ids.topup_amt: # Deposit
                            data['topup_amt'] = "{:.2f}".format(float(last_acc_ids.topup_amt ))
                        if last_acc_ids.outstanding:
                            data['outstanding'] = "{:.2f}".format(float(last_acc_ids.outstanding))

                    open_ids = PrepaidAccountCondition.objects.filter(pp_no=preobj.pp_no,
                    pos_daud_lineno=preobj.line_no).only('pp_no','pos_daud_lineno').first()
                    data["conditiontype1"]=open_ids.conditiontype1
                    data["product"] = 0.00;data["service"] = 0.00;data["all"] = 0.00
                    if open_ids.conditiontype1 == "Product Only":
                        # data["product"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                        # product_type += last_acc_ids.pp_amt 
                        data["product"] = "{:.2f}".format(float(last_acc_ids.remain))
                        product_type += last_acc_ids.remain
                    elif open_ids.conditiontype1 == "Service Only":
                        # data["service"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                        # service_type += last_acc_ids.pp_amt
                        data["service"] = "{:.2f}".format(float(last_acc_ids.remain))
                        service_type += last_acc_ids.remain
                    elif open_ids.conditiontype1 == "All":
                        # data["all"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                        # all_type += last_acc_ids.pp_amt
                        data["all"] = "{:.2f}".format(float(last_acc_ids.remain))
                        all_type += last_acc_ids.remain
       
                    lst.append(data)

            if lst != []:
                header_data = {"balance_producttype" : "{:.2f}".format(float(product_type)), 
                "balance_servicetype" : "{:.2f}".format(float(service_type)),
                "balance_alltype" : "{:.2f}".format(float(all_type)),"totalprepaid_count" : len(id_lst)}
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'header_data':header_data, 'data': serializer.data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        
    def get_object(self, pk):
        try:
            return PrepaidAccount.objects.get(pk=pk)
        except PrepaidAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first() 
        site = fmspw.loginsite
        account = self.get_object(pk)
        # queryset = PrepaidAccount.objects.filter(pp_no=account.pp_no,line_no=account.line_no,
        # site_code=account.site_code).only('pp_no','line_no').order_by('pk')
        queryset = PrepaidAccount.objects.filter(pp_no=account.pp_no,line_no=account.line_no
        ).only('pp_no','line_no').order_by('pk')
        if queryset:
            last = queryset.last()
            serializer = PrepaidacSerializer(queryset, many=True)
            # pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
            # sa_transacno=account.pp_no,sa_transacno_type='Receipt',
            # ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
            # pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
            # sa_transacno=account.pp_no,sa_transacno_type='Receipt'
            # ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
            pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,sa_transacno=account.pp_no,
            ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
            for v in serializer.data:
                if pos_haud:
                    v['prepaid_ref'] = pos_haud.sa_transacno_ref
                else:
                    v['prepaid_ref'] = "" 

                
                ppobj = PrepaidAccount.objects.filter(pk=v["id"]).first()
                if ppobj.sa_status in ['DEPOSIT','TOPUP']:
                    v['old_transaction'] = "-"
                    v['transaction_ref'] = "-"
                    v['voucher#'] = "-"
                    v['item_no'] = "-"
                    v['item_name'] = "-"
                elif ppobj.sa_status == 'SA':
                    if ppobj.transac_no:
                        poshaud = PosHaud.objects.filter(sa_custno=account.cust_code,
                        sa_transacno=ppobj.transac_no,ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno').order_by('pk').first()
                        if poshaud:
                            v['old_transaction'] = poshaud.sa_transacno
                            v['transaction_ref'] = poshaud.sa_transacno_ref
                        else:
                            v['old_transaction'] = "-"
                            v['transaction_ref'] = "-"

                    v['voucher#'] = "-"
                    v['item_no'] = ppobj.item_no if ppobj.item_no else "-"
                    stockobj = Stock.objects.filter(item_code=ppobj.item_no).only('item_code').first()
                    if stockobj:
                        v['item_name'] = stockobj.item_name if stockobj.item_name else "-"
                    else:
                        v['item_name'] = "-"  
                else:
                    v['old_transaction'] = "-";v['transaction_ref'] = "-";v['voucher#'] = "-";v['item_no'] = "-"
                    v['item_name'] = "-";

                v['use_amt'] = "{:.2f}".format(float(v['use_amt'])) if v['use_amt'] else 0.00
                if ppobj.sa_status == 'DEPOSIT':
                    v['topup_amt'] = "-"
                    v['topup_no'] = "-"
                    v['topup_date'] = "-"
                    v['status'] = "-"
                elif ppobj.sa_status == 'TOPUP': 
                    v['topup_amt'] = "{:.2f}".format(float(v['topup_amt'])) if v['topup_amt'] else ""
                    v['topup_no'] = ppobj.topup_no
                    if ppobj.topup_date:
                        splt = str(ppobj.topup_date).split(" ")
                        v['topup_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                    v['status'] = ppobj.sa_status
                elif ppobj.sa_status == 'SA':
                    v['topup_amt'] = "-"
                    v['topup_no'] = "-"
                    v['topup_date'] = "-"
                    v['status'] = "-"
                else:
                    v['topup_amt'] = "-";v['topup_no'] = "-";v['topup_date'] = "-";v['status'] = "-"

                v['balance'] = "{:.2f}".format(float(ppobj.remain)) if ppobj.remain else 0.00  
                v['supplementary'] = ""

            # depoamt_acc_ids = PrepaidAccount.objects.filter(pp_no=account.pp_no,
            # site_code=account.site_code,line_no=account.line_no,sa_status__in=('DEPOSIT', 'TOPUP')).only('pp_no','site_code','line_no','sa_status').aggregate(Sum('topup_amt'))
            depoamt_acc_ids = PrepaidAccount.objects.filter(pp_no=account.pp_no,
            line_no=account.line_no,sa_status__in=('DEPOSIT', 'TOPUP')).only('pp_no','site_code','line_no','sa_status').aggregate(Sum('topup_amt'))
                    
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
            'header_data':{'prepaid_amount':"{:.2f}".format(float(last.pp_amt)) if last.pp_amt else "0.00",
            'used_amount':"{:.2f}".format(float(last.use_amt)) if last.use_amt else "0.00", 
            'bonus':"{:.2f}".format(float(last.pp_bonus)) if last.pp_bonus else "0.00", 
            'balance':"{:.2f}".format(float(last.remain)) if last.remain else "0.00", 
            'outstanding':"{:.2f}".format(float(last.outstanding)) if last.outstanding else "0.00", 
            'deposit_amount': "{:.2f}".format(float(depoamt_acc_ids['topup_amt__sum'])) if depoamt_acc_ids else "0.00"}, 
            'data': serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)


class ComboViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ComboServicesSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        queryset = Combo_Services.objects.filter(Isactive=True,Site_Code__pk=site.pk).order_by('-pk')
        return queryset

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer_class =  ComboServicesSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            # print(result,"result") 
            return Response(result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
     

    def get_object(self, pk):
        try:
            return Combo_Services.objects.get(pk=pk, Isactive=True)
        except Combo_Services.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        combo = self.get_object(pk)
        serializer = ComboServicesSerializer(combo,context={'request': self.request})
        result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
        return Response(result, status=status.HTTP_200_OK)


class DashboardAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = DashboardSerializer

    def get(self, request):
        # try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = ItemSitelist.objects.filter(pk=fmspw.loginsite.pk)
            # if int(fmspw.LEVEL_ItmIDid.level_code) == 24: 
            serializer = DashboardSerializer(site, many=True)
            data = serializer.data[0]
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'data': data} 
            return Response(result,status=status.HTTP_200_OK)
            #else: 
            #    result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
            #    return Response(data=result, status=status.HTTP_200_OK)

        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)

class DashboardCustAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = []

    def get(self, request):
        try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            if int(fmspw.LEVEL_ItmIDid.level_code) != 24: 
                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'customer': {},'product_sold':{},'service_sold':{}} 
                return Response(result,status=status.HTTP_200_OK)
               
            today_date = timezone.now().date()
            #newcustomer
            daily_custids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__date=today_date).only('site_code','cust_joindate').order_by('-pk').count()
            monthly_custids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=today_date.month,
            cust_joindate__year=today_date.year).only('site_code','cust_joindate').order_by('-pk').count()
            total_custids = Customer.objects.filter(site_code=site.itemsite_code).only('site_code').order_by('-pk').count()
            customer = {'daily_custcnt':daily_custids,'monthly_custcnt':monthly_custids,'total_cust':total_custids}
            
            daily_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,isvoid=False).only('itemsite_code','sa_date','isvoid').order_by('-pk')
            daily_satranacno = list(set([i.sa_transacno for i in daily_haudids if i.sa_transacno]))

            month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,isvoid=False).only('itemsite_code','sa_date','isvoid').order_by('-pk')
            month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))
            

            #Daily Product
            daily_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_productqty = sum([i.dt_qty for i in daily_product_ids])
            daily_productdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_product_ids])))
            daily_product_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='TP PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_product_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_product_ar_ids])))
            
            #monthly Product
            month_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_productqty = sum([i.dt_qty for i in month_product_ids])
            month_productdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_product_ids])))
            month_product_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type='TP PRODUCT').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_product_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in month_product_ar_ids])))

            product_sold = {'dailyproduct_qty':daily_productqty,'monthlyproduct_qty':month_productqty,
            'daily_product': "0.00" if daily_productdeposit == 0 else daily_productdeposit,
            'monthly_product': "0.00" if month_productdeposit == 0 else month_productdeposit,
            'daily_product_ar': "0.00" if daily_product_ar == 0 else daily_product_ar,
            'monthly_product_ar': "0.00" if month_product_ar == 0 else month_product_ar}

            #Daily Service
            daily_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_serviceqty = sum([i.dt_qty for i in daily_service_ids])
            daily_servicedeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_service_ids])))
            daily_service_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='TP SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            daily_service_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_service_ar_ids])))

            #monthly Service
            month_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_serviceqty = sum([i.dt_qty for i in month_service_ids])
            month_servicedeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_service_ids])))
            month_service_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type='TP SERVICE').only('itemsite_code','sa_date',
            'sa_transacno','dt_status','record_detail_type').order_by('-pk')
            month_service_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in month_service_ar_ids])))

            service_sold = {'dailyservice_qty':daily_serviceqty,'monthlyservice_qty':month_serviceqty,
            'daily_service': "0.00" if daily_servicedeposit == 0 else daily_servicedeposit,
            'monthly_service': "0.00" if month_servicedeposit == 0 else month_servicedeposit,
            'daily_service_ar': "0.00" if daily_service_ar == 0 else daily_service_ar,
            'monthly_service_ar': "0.00" if month_service_ar == 0 else month_service_ar}
            
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'customer': customer,'product_sold':product_sold,'service_sold':service_sold} 
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


class DashboardVoucherAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite

            if int(fmspw.LEVEL_ItmIDid.level_code) != 24: 
                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'voucher_sold':{},'prepaid_sold':{}} 
                return Response(result,status=status.HTTP_200_OK)
                # result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                # return Response(data=result, status=status.HTTP_200_OK)

            today_date = timezone.now().date()
            #newcustomer
           
            daily_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,isvoid=False).order_by('-pk')
            daily_satranacno = list(set([i.sa_transacno for i in daily_haudids if i.sa_transacno]))

            month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,isvoid=False).order_by('-pk')
            month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))
            

            #Daily Voucher
            daily_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk')
            daily_voucherqty = sum([i.dt_qty for i in daily_voucher_ids])
            daily_voucherdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_voucher_ids])))

            #monthly Voucher
            month_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk')
            month_voucherqty = sum([i.dt_qty for i in month_voucher_ids])
            month_voucherdeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_voucher_ids])))

            voucher_sold = {'dailyvoucher_qty':daily_voucherqty,'monthlyvoucher_qty':month_voucherqty,
            'daily_voucher': "0.00" if daily_voucherdeposit == 0 else daily_voucherdeposit,
            'monthly_voucher': "0.00" if month_voucherdeposit == 0 else month_voucherdeposit}
            
            #Daily prepaid
            daily_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk')
            daily_prepaidqty = sum([i.dt_qty for i in daily_prepaid_ids])
            daily_prepaiddeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_prepaid_ids])))
            daily_prepaid_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type='TP PREPAID').order_by('-pk')
            daily_prepaid_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in daily_prepaid_ar_ids])))

            #monthly prepaid
            month_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk')
            month_prepaidqty = sum([i.dt_qty for i in month_prepaid_ids])
            month_prepaiddeposit = "{:.2f}".format(float(sum([i.dt_deposit for i in month_prepaid_ids])))
            month_prepaid_ar_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type='TP PREPAID').order_by('-pk')
            month_prepaid_ar = "{:.2f}".format(float(sum([i.dt_deposit for i in month_prepaid_ar_ids])))

            prepaid_sold = {'dailyprepaid_qty':daily_prepaidqty,'monthlyprepaid_qty':month_prepaidqty,
            'daily_prepaid': "0.00" if daily_prepaiddeposit == 0 else daily_prepaiddeposit,
            'monthly_prepaid': "0.00" if month_prepaiddeposit == 0 else month_prepaiddeposit,
            'daily_prepaid_ar': "0.00" if daily_prepaid_ar == 0 else daily_prepaid_ar,
            'monthly_prepaid_ar': "0.00" if month_prepaid_ar == 0 else month_prepaid_ar}

            
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'voucher_sold':voucher_sold,'prepaid_sold':prepaid_sold} 
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)



class DashboardTDAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = []

    def get(self, request):
        # try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite

            if int(fmspw.LEVEL_ItmIDid.level_code) != 24: 
                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'treatment_done':{},'total_collection':{}} 
                return Response(result,status=status.HTTP_200_OK)
                # result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                # return Response(data=result, status=status.HTTP_200_OK)

            today_date = timezone.now().date()

            daily_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,isvoid=False).order_by('-pk')
            daily_satranacno = list(set([i.sa_transacno for i in daily_haudids if i.sa_transacno]))

            month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,isvoid=False).order_by('-pk')
            month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))
            

            #Treatment Done
            daily_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            sa_transacno__in=daily_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
            refer_lst = list(set([i.st_ref_treatmentcode for i in daily_td_ids if i.st_ref_treatmentcode]))
            # print(refer_lst,"refer_lst")

            daily_treatids = Treatment.objects.filter(site_code=site.itemsite_code,treatment_code__in=refer_lst,
            status='Done').order_by('-pk')
            # print(daily_treatids,"daily_treatids")
            daily_tdqty = daily_treatids.count()
            # print(daily_tdqty,"daily_tdqty")
            
            if daily_treatids:
                daily_vals = daily_treatids.aggregate(Sum('unit_amount'))
                # print(daily_vals,"daily_vals")
                daily_unitamt ="{:.2f}".format(float(daily_vals['unit_amount__sum']))
            else:
                daily_unitamt = "0.00"


            monthly_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
            record_detail_type__in=['SERVICE','TD']).order_by('-pk')
            
            refer_lstmonth = list(set([i.st_ref_treatmentcode for i in monthly_td_ids if i.st_ref_treatmentcode]))
            # print(refer_lst,"refer_lst")

            month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
            treatment_code__in=refer_lstmonth,status='Done').order_by('-pk')
            
            monthly_tdqty = month_treatids.count()

            if month_treatids:
                month_vals = month_treatids.aggregate(Sum('unit_amount'))
                month_unitamt ="{:.2f}".format(float(month_vals['unit_amount__sum']))
            else:
                month_unitamt = "0.00"

            treatment_done = {'daily_tdqty':daily_tdqty,'monthly_tdqty':monthly_tdqty,
            'daily_tdamt':daily_unitamt,'monthly_tdamt':month_unitamt}


            #Total Collection
            gt1_ids = Paytable.objects.filter(gt_group='GT1',pay_isactive=True).order_by('-pk') 
            gt1_lst = list(set([i.pay_code for i in gt1_ids if i.pay_code]))
            # print(gt1_lst,"gt1_lst")

            gt2_ids = Paytable.objects.filter(gt_group='GT2',pay_isactive=True).order_by('-pk') 
            gt2_lst = list(set([i.pay_code for i in gt2_ids if i.pay_code]))
            # print(gt2_lst,"gt2_lst")

            daily_taud_salesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            pay_type__in=gt1_lst).order_by('-pk')
            # print(daily_taud_salesids,"daily_taud_salesids")
            if daily_taud_salesids:
                daily_taud_salesvals = daily_taud_salesids.aggregate(Sum('pay_actamt'))
                # print(daily_taud_salesvals,"daily_taud_salesvals")
                daily_sales ="{:.2f}".format(float(daily_taud_salesvals['pay_actamt__sum'])) 
            else:
                daily_sales = "0.00"

            month_taud_salesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,pay_type__in=gt1_lst).order_by('-pk')
            # print(month_taud_salesids,"month_taud_salesids")
            if month_taud_salesids:
                month_taud_salesvals = month_taud_salesids.aggregate(Sum('pay_actamt'))
                # print(month_taud_salesvals,"month_taud_salesvals")
                monthly_sales ="{:.2f}".format(float(month_taud_salesvals['pay_actamt__sum'])) 
            else:
                monthly_sales = "0.00"   

            daily_taud_nsalesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date=today_date,
            pay_type__in=gt2_lst).order_by('-pk')
            # print(daily_taud_nsalesids,"daily_taud_nsalesids")
            if daily_taud_nsalesids:
                daily_taud_nsalesvals = daily_taud_nsalesids.aggregate(Sum('pay_actamt'))
                # print(daily_taud_nsalesvals,"daily_taud_nsalesvals")
                daily_nonsales ="{:.2f}".format(float(daily_taud_nsalesvals['pay_actamt__sum']))  
            else:
                daily_nonsales = "0.00"

            month_taud_nsalesids = PosTaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,pay_type__in=gt2_lst).order_by('-pk')
            # print(month_taud_nsalesids,"month_taud_nsalesids")
            if month_taud_nsalesids:
                month_taud_nsalesvals = month_taud_nsalesids.aggregate(Sum('pay_actamt'))
                # print(month_taud_nsalesvals,"month_taud_nsalesvals")
                monthly_nonsales ="{:.2f}".format(float(month_taud_nsalesvals['pay_actamt__sum'])) 
            else:
                monthly_nonsales = "0.00"


            total_daily = float(daily_sales) + float(daily_nonsales)
            total_monthly = float(monthly_sales) + float(monthly_nonsales)
            total_collection = {'daily_sales':daily_sales,'monthly_sales':monthly_sales,
            'daily_nonsales':daily_nonsales,'monthly_nonsales':monthly_nonsales,
            'total_daily': "{:.2f}".format(float(total_daily)) ,
            'total_monthly':"{:.2f}".format(float(total_monthly))}

            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'treatment_done':treatment_done,'total_collection':total_collection} 
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)

#Month Top 10 / Top 20 
class DashboardTopProductAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        try:
            now = timezone.now()
            # print(str(now.hour) + '  ' +  str(now.minute) + '  ' +  str(now.second),"Start hour, minute, second\n")
            
            if not self.request.GET.get('select',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Top Value",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if not self.request.GET.get('order_by',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Order by",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            if int(fmspw.LEVEL_ItmIDid.level_code) != 24: 
                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'top_product':{},'top_service':{},'top_prepaid':{},
                'top_voucher':{},'top_td':{}} 
                return Response(result,status=status.HTTP_200_OK)

                # result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                # return Response(data=result, status=status.HTTP_200_OK)

            today_date = timezone.now().date()

            month_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
            sa_date__year=today_date.year,isvoid=False).only('itemsite_code','sa_date','isvoid').order_by('-pk')
            month_satranacno = list(set([i.sa_transacno for i in month_haudids if i.sa_transacno]))
            

            if str(self.request.GET.get('order_by',None)) == "price": 
                month_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
                # print(month_product_ids,"month_product_ids")

                month_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
                # print(month_service_ids,"month_service_ids")

                month_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
                # print(month_prepaid_ids,"month_prepaid_ids")

                month_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_trasc')
                # print(month_voucher_ids,"month_voucher_ids")

                monthly_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
                record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                # print(monthly_td_ids,"monthly_td_ids")
                refer_lstmonth = list(set([i.st_ref_treatmentcode for i in monthly_td_ids if i.st_ref_treatmentcode]))
                # print(refer_lstmonth,"refer_lstmonth")

                month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                treatment_code__in=refer_lstmonth,status='Done').order_by('-pk').values('item_code',
                ).order_by('item_code').annotate(total_qty=Count('item_code'),total_unitamt=Sum('unit_amount')).order_by('-total_unitamt')
                # print(month_treatids,"month_treatids") 
                td_val_lst = list(month_treatids) 
                for td in td_val_lst:
                    item_code = td['item_code'][:-4]
                    stock_obj = Stock.objects.filter(item_isactive=True,item_code=item_code).order_by('-pk').first()
                    td['item_name'] = stock_obj.item_name
                # print(td_val_lst,"td_val_lst") 
  
            elif str(self.request.GET.get('order_by',None)) == "qty": 
                month_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
                # print(month_product_ids,"month_product_ids")

                month_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
                # print(month_service_ids,"month_service_ids")


                month_prepaid_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='PREPAID').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
                # print(month_prepaid_ids,"month_prepaid_ids")

                month_voucher_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",record_detail_type='VOUCHER').order_by('-pk').values('dt_itemno','dt_itemnoid__item_name',
                ).order_by('dt_itemno').annotate(total_qty=Sum('dt_qty'),total_trasc=Sum('dt_transacamt')).order_by('-total_qty')
                # print(month_voucher_ids,"month_voucher_ids")

                monthly_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=today_date.month,
                sa_date__year=today_date.year,sa_transacno__in=month_satranacno,dt_status="SA",
                record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                # print(monthly_td_ids,"monthly_td_ids")
                refer_lstmonth = list(set([i.st_ref_treatmentcode for i in monthly_td_ids if i.st_ref_treatmentcode]))
                # print(refer_lstmonth,"refer_lstmonth")

                month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                treatment_code__in=refer_lstmonth,status='Done').order_by('-pk').values('item_code',
                ).order_by('item_code').annotate(total_qty=Count('item_code'),total_unitamt=Sum('unit_amount')).order_by('-total_qty')
                # print(month_treatids,"month_treatids") 

                td_val_lst = list(month_treatids) 
                for td in td_val_lst:
                    item_code = td['item_code'][:-4]
                    stock_obj = Stock.objects.filter(item_isactive=True,item_code=item_code).order_by('-pk').first()
                    td['item_name'] = stock_obj.item_name

                # print(td_val_lst,"td_val_lst") 
    
                
            if int(self.request.GET.get('select',None)) == 10:
              
                top10_pro_lst = month_product_ids[:10]
                product_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_pro_lst])
                
                top10_ser_lst = month_service_ids[:10]
                service_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_ser_lst])
                
                top10_pre_lst = month_prepaid_ids[:10]
                prepaid_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_pre_lst])

                top10_vou_lst = month_voucher_ids[:10]
                voucher_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top10_vou_lst])
                
                top10_td_lst = td_val_lst[:10]
                td_val = list([{'item': i['item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_unitamt']))} for i in top10_td_lst])
  
            
            elif int(self.request.GET.get('select',None)) == 20: 
                
                top20_pro_lst = month_product_ids[:20]
                product_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_pro_lst])
                
                top20_ser_lst = month_service_ids[:20]
                service_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_ser_lst])
                
                top20_pre_lst = month_prepaid_ids[:20]
                prepaid_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_pre_lst])
                
                top20_vou_lst = month_voucher_ids[:20]
                voucher_val = list([{'item': i['dt_itemnoid__item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_trasc']))} for i in top20_vou_lst])
                
                top20_td_lst = td_val_lst[:20]
                td_val = list([{'item': i['item_name'],'qty': i['total_qty'], 'amount': "{:.2f}".format(float(i['total_unitamt']))} for i in top20_td_lst])
  
           
        
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'top_product':product_val,'top_service':service_val,'top_prepaid':prepaid_val,
            'top_voucher':voucher_val,'top_td':td_val} 
            now1 = timezone.now()
            # print(str(now1.hour) + '  ' +  str(now1.minute) + '  ' +  str(now1.second),"End hour, minute, second\n")
            total = now1.second - now.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


class DashboardChartAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = []

    def get(self, request):
        # try:
            tnow = timezone.now()
            # print(str(tnow.hour) + '  ' +  str(tnow.minute) + '  ' +  str(tnow.second),"Start hour, minute, second\n")
           
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'data': [{},{},{},{}]}                    
            return Response(result,status=status.HTTP_200_OK)
            if int(fmspw.LEVEL_ItmIDid.level_code) != 24: 
                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'data': [{},{},{},{}]}                    
                return Response(result,status=status.HTTP_200_OK)

                # result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                # return Response(data=result, status=status.HTTP_200_OK)

            today_date = timezone.now().date()

            if not self.request.GET.get('select',None):
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Quarterly / Yearly",'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            # result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please select Quarterly / Yearly",'error': True}
            # return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            select = self.request.GET.get('select',None)  
            now = datetime.datetime(today_date.year,1,1)
            # print(now,"now")
            if select == "Yearly":
                categories = [(now + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range(12)] 
                # print(categories,"categories") 
                xstep = 1

                #new Customer
                male_lst = []; female_lst = [] 
                for i in range(1, 13):
                    # print(i,"iii")
                    monthly_mcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=today_date.year,Cust_sexesid__pk=1).order_by('-pk').count()
                    # print(monthly_mcustids,"monthly_mcustids")
                    male_lst.append(monthly_mcustids)

                    monthly_fcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=today_date.year,Cust_sexesid__pk=2).order_by('-pk').count()
                    female_lst.append(monthly_fcustids)
                
                total_custids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month__gte=1,
                cust_joindate__month__lte=12,cust_joindate__year=today_date.year).order_by('-pk').count()

                newcust_data = {
                'title': { 'text': "New Customer" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': [
                            {
                                'name': "New Customer (Male)",
                                'data': male_lst,
                                'color': "#ffa31a"
                            },
                            {
                                'name': "New Customer (Female)",
                                'data': female_lst,
                                'color': "#a1cae2"
                            }
                        ],
                'outlinetext' : "Total Number of Customer",
                'outlinevalue': total_custids               
                }  


                #Product Sold Qty

                yearly_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                # print(yearly_haudids,len(yearly_haudids),"yearly_haudids")
                yearly_satranacno = list(set([i.sa_transacno for i in yearly_haudids if i.sa_transacno]))
                # print(yearly_satranacno,len(yearly_satranacno),"yearly_satranacno")
            

                yearly_prodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk')
                # print(yearly_prodaud_ids,len(yearly_prodaud_ids),"yearly_prodaud_ids")
                pro_lst = []

                for y in yearly_prodaud_ids:
                    # print(y,y.pk,"YY")
                    brand_code = y.dt_itemnoid.item_brand
                    # print(brand_code,"brand_code")
                    brand_ids = ItemBrand.objects.filter(itm_code=brand_code,retail_product_brand=True,itm_status=True).first()
                    # print(brand_ids,"brand_ids")
                    if brand_ids:
                        # print("first iff")
                        # print(pro_lst,"pro_lst")
                        # print(any(d['code'] == brand_code for d in pro_lst),"any")
                        # print(not any(d['code'] == brand_code for d in pro_lst),"NOOT")
                        if not any(d['code'] == brand_code for d in pro_lst):
                            # print("iff")
                            r = lambda: random.randint(0,255)
                            color = '#%02X%02X%02X' % (r(),r(),r())
                            # print(color,"kkk")
                            pro_vals = {'code':brand_code,'name':brand_ids.itm_desc,'color':color}
                            # print(vals,"vals")
                            pro_lst.append(pro_vals)


                # print(pro_lst,"pro_lst")  
                tot_proqty = 0          
                for b in pro_lst:
                    datalst = []
                    for i in range(1, 13):
                        month_bhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                        month_bsatranacno = list(set([i.sa_transacno for i in month_bhaudids if i.sa_transacno]))
                        
                        eachmonth_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_bsatranacno,dt_status="SA",record_detail_type='PRODUCT',
                        dt_itemnoid__item_brand=b['code']).order_by('-pk')
                        # print(eachmonth_product_ids,"eachmonth_product_ids")
                        eachmonth_productqty = sum([i.dt_qty for i in eachmonth_product_ids])
                        # print(eachmonth_productqty,"eachmonth_productqty")
                        tot_proqty += eachmonth_productqty
                        datalst.append(eachmonth_productqty)
                    b['data'] = datalst

                # print(pro_lst,"pro_lst After") 

                produtsold_data = {
                'title': { 'text': "Product Sold QTY" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': pro_lst ,
                'outlinetext' : "Total Product Sold QTY",
                'outlinevalue' : tot_proqty,       
                }  
                
                #Service Sales Amount
                
                yearly_servicedaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk')
                # print(yearly_servicedaud_ids,len(yearly_servicedaud_ids),"yearly_servicedaud_ids")
                service_lst = []

                for s in yearly_servicedaud_ids:
                    # print(s,s.pk,"SSS")
                    dept_code = s.dt_itemnoid.item_dept
                    # print(dept_code,"dept_code")
                    dept_ids = ItemDept.objects.filter(itm_code=dept_code,is_service=True, itm_status=True).first()
                    # print(dept_ids,"dept_ids")
                    if dept_ids:
                        # print("first iff")
                        # print(service_lst,"service_lst")
                        # print(any(d['code'] == dept_code for d in service_lst),"any")
                        # print(not any(d['code'] == dept_code for d in service_lst),"NOOT")
                        if not any(d['code'] == dept_code for d in service_lst):
                            # print("iff")
                            r = lambda: random.randint(0,255)
                            color = '#%02X%02X%02X' % (r(),r(),r())
                            # print(color,"kkk")
                            service_vals = {'code':dept_code,'name':dept_ids.itm_desc,'color':color}
                            # print(vals,"vals")
                            service_lst.append(service_vals)


                # print(service_lst,"service_lst")  
                tot_serviceamt = 0.0          
                for e in service_lst:
                    sdatalst = []
                    for i in range(1, 13):
                        month_shaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                        month_ssatranacno = list(set([i.sa_transacno for i in month_shaudids if i.sa_transacno]))
                        
                        eachmonth_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_ssatranacno,dt_status="SA",record_detail_type='SERVICE',
                        dt_itemnoid__item_dept=e['code']).order_by('-pk')
                        # print(eachmonth_service_ids,"eachmonth_service_ids")
                        eachmonth_serviceqty = sum([i.dt_transacamt for i in eachmonth_service_ids])
                        # print(eachmonth_serviceqty,"eachmonth_serviceqty")
                        tot_serviceamt += eachmonth_serviceqty
                        sdatalst.append(int(eachmonth_serviceqty))
                    e['data'] = sdatalst

                # print(service_lst,"service_lst After")     

                servicesales_data = {
                'title': { 'text': "Service Sales Amount" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': service_lst,
                'outlinetext' : "Total Service Sales Amount",
                'outlinevalue' : "{:.2f}".format(float(tot_serviceamt))         
                }  

                #Treatment Done Count

                yearly_tddaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__gte=1,sa_date__month__lte=12,
                sa_date__year=today_date.year,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                # print(yearly_tddaud_ids,len(yearly_tddaud_ids),"yearly_tddaud_ids")
                td_lst = []

                for t in yearly_tddaud_ids:
                    # print(t,t.pk,"TTTT")
                    tdept_code = t.dt_itemnoid.item_dept
                    print(tdept_code,"tdept_code")
                    tdept_ids = ItemDept.objects.filter(itm_code=tdept_code,is_service=True, itm_status=True).first()
                    # print(tdept_ids,"tdept_ids")
                    if tdept_ids:
                        if t.st_ref_treatmentcode:
                            treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                            treatment_code=t.st_ref_treatmentcode,status='Done').order_by('-pk').first()
                            if treatids:
                                # print("first iff")
                                # print(td_lst,"td_lst")
                                # print(any(d['code'] == tdept_code for d in td_lst),"any")
                                # print(not any(d['code'] == tdept_code for d in td_lst),"NOOT")
                                if not any(d['code'] == tdept_code for d in td_lst):
                                    # print("iff")
                                    r = lambda: random.randint(0,255)
                                    color = '#%02X%02X%02X' % (r(),r(),r())
                                    # print(color,"kkk")
                                    td_vals = {'code':tdept_code,'name':tdept_ids.itm_desc,'color':color}
                                    # print(vals,"vals")
                                    td_lst.append(td_vals)

                # print(td_lst,"td_lst")  
                tot_tdcount = 0          
                for l in td_lst:
                    tddatalst = []
                    for i in range(1, 13):
                        month_tdhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,isvoid=False).order_by('-pk')
                        month_tdsatranacno = list(set([i.sa_transacno for i in month_tdhaudids if i.sa_transacno]))
                        
                        eachmonth_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=today_date.year,sa_transacno__in=month_tdsatranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD'],
                        dt_itemnoid__item_dept=l['code']).order_by('-pk')
                        # print(eachmonth_td_ids,"eachmonth_td_ids")
                        refer_lstmonth = list(set([i.st_ref_treatmentcode for i in eachmonth_td_ids if i.st_ref_treatmentcode]))
                        # print(refer_lst,"refer_lst")

                        month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                        treatment_code__in=refer_lstmonth,status='Done',Item_Codeid__item_dept=l['code']).order_by('-pk')
                        
                        monthly_tdqty = month_treatids.count()
                        tot_tdcount += monthly_tdqty
                        tddatalst.append(monthly_tdqty)
                    l['data'] = tddatalst

                # print(td_lst,"td_lst After")  

                treatmentdone_data = {
                'title': { 'text': "Treatment Done Count" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': td_lst ,
                'outlinetext' : "Total Number of Treatment Done Count",
                'outlinevalue' : tot_tdcount        
                }  


                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'data': [newcust_data,produtsold_data,servicesales_data,treatmentdone_data]}                    
            
            elif select == "Quarterly": 
                current_month = today_date.month
                # current_month = 1

                if current_month == 1:
                    range_lst = [12,1,2,3]
                    new_rangelst = [1,2,3]
                    now1 = datetime.datetime(today_date.year-1,12,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in new_rangelst] 
                    # print(categories ,"categories bbb")
                    dec_val = "Dec"+"-"+str(today_date.year-1)
                    categories.insert(0,dec_val)
                    # print(categories,"categories aa")
                elif current_month in [2,3]: 
                    range_lst = [1,2,3,4]
                    now1 = datetime.datetime(today_date.year-1,12,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                    # print(categories,"categories")
                elif current_month == 4: 
                    range_lst = [3,4,5,6]
                    now1 = datetime.datetime(today_date.year,3,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                elif current_month == 5:
                    range_lst = [4,5,6,7]
                    now1 = datetime.datetime(today_date.year,4,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                elif current_month == 6:
                    range_lst = [5,6,7,8]
                    now1 = datetime.datetime(today_date.year,5,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                elif current_month == 7:
                    range_lst = [6,7,8,9]
                    now1 = datetime.datetime(today_date.year,6,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                elif current_month == 8:
                    range_lst = [7,8,9,10]
                    now1 = datetime.datetime(today_date.year,7,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                elif current_month == 9:
                    range_lst = [8,9,10,11]
                    now1 = datetime.datetime(today_date.year,8,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 
                elif current_month in [10, 11, 12]:
                    range_lst = [9,10,11,12]
                    now1 = datetime.datetime(today_date.year,9,1)
                    categories = [(now1 + relativedelta(months=i)).strftime('%b')+"-"+str(today_date.year) for i in range_lst] 


                xstep = 1 
                #new Customer
                male_lst = []; female_lst = [] 
                for i in range_lst:
                    # print(i,"iii")
                    if current_month == 1:
                        year = today_date.year
                        if i == 12:
                            year = today_date.year - 1
                    else:
                        year = today_date.year        

                    monthly_mcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=year,Cust_sexesid__pk=1).order_by('-pk').count()
                    # print(monthly_mcustids,"monthly_mcustids")
                    male_lst.append(monthly_mcustids)

                    monthly_fcustids = Customer.objects.filter(site_code=site.itemsite_code,cust_joindate__month=i,
                    cust_joindate__year=year,Cust_sexesid__pk=2).order_by('-pk').count()
                    female_lst.append(monthly_fcustids)
                
                total_custids = sum(male_lst) + sum(female_lst)

                newcust_data = {
                'title': { 'text': "New Customer" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': [
                            {
                                'name': "New Customer (Male)",
                                'data': male_lst,
                                'color': "#ffa31a"
                            },
                            {
                                'name': "New Customer (Female)",
                                'data': female_lst,
                                'color': "#a1cae2"
                            }
                        ],
                'outlinetext' : "Total Number of Customer",
                'outlinevalue' : total_custids               
                }  

                
                year_lst = [today_date.year]  

                #Product Sold Qty
                if current_month == 1:
                    start_date = datetime.datetime(today_date.year-1,12,1).date()
                    end_date = datetime.datetime(today_date.year,3,31).date()

                

                    yearly_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,isvoid=False).order_by('-pk')
                    yearly_satranacno = list(set([i.sa_transacno for i in yearly_haudids if i.sa_transacno]))

                    yearly_prodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk')
                    
                else:
                    yearly_haudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,isvoid=False).order_by('-pk')
                    # print(yearly_haudids,len(yearly_haudids),"yearly_haudids")
                    yearly_satranacno = list(set([i.sa_transacno for i in yearly_haudids if i.sa_transacno]))
                    # print(yearly_satranacno,len(yearly_satranacno),"yearly_satranacno")

                    yearly_prodaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='PRODUCT').order_by('-pk')
                    # print(yearly_prodaud_ids,len(yearly_prodaud_ids),"yearly_prodaud_ids")
                    
                pro_lst = []

                for y in yearly_prodaud_ids:
                    # print(y,y.pk,"YY")
                    brand_code = y.dt_itemnoid.item_brand
                    # print(brand_code,"brand_code")
                    brand_ids = ItemBrand.objects.filter(itm_code=brand_code,retail_product_brand=True,itm_status=True).first()
                    # print(brand_ids,"brand_ids")
                    if brand_ids:
                        # print("first iff")
                        # print(pro_lst,"pro_lst")
                        # print(any(d['code'] == brand_code for d in pro_lst),"any")
                        # print(not any(d['code'] == brand_code for d in pro_lst),"NOOT")
                        if not any(d['code'] == brand_code for d in pro_lst):
                            # print("iff")
                            r = lambda: random.randint(0,255)
                            color = '#%02X%02X%02X' % (r(),r(),r())
                            # print(color,"kkk")
                            pro_vals = {'code':brand_code,'name':brand_ids.itm_desc,'color':color}
                            # print(vals,"vals")
                            pro_lst.append(pro_vals)


                # print(pro_lst,"pro_lst")  
                tot_proqty = 0          
                for b in pro_lst:
                    datalst = []
                    for i in range_lst:
                        if current_month == 1:
                            year = today_date.year
                            if i == 12:
                                year = today_date.year - 1
                        else:
                            year = today_date.year  

                        month_bhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,isvoid=False).order_by('-pk')
                        month_bsatranacno = list(set([i.sa_transacno for i in month_bhaudids if i.sa_transacno]))
                        
                        eachmonth_product_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_bsatranacno,dt_status="SA",record_detail_type='PRODUCT',
                        dt_itemnoid__item_brand=b['code']).order_by('-pk')
                        # print(eachmonth_product_ids,"eachmonth_product_ids")
                        eachmonth_productqty = sum([i.dt_qty for i in eachmonth_product_ids])
                        # print(eachmonth_productqty,"eachmonth_productqty")
                        tot_proqty += eachmonth_productqty
                        datalst.append(eachmonth_productqty)

                    b['data'] = datalst

                # print(pro_lst,"pro_lst After") 

                produtsold_data = {
                'title': { 'text': "Product Sold QTY" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': pro_lst,
                'outlinetext' : "Total Product Sold QTY",
                'outlinevalue' : tot_proqty       
                }  

                #Service Sales Amount

                if current_month == 1:
                   
                    yearly_servicedaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk')
                    # print(yearly_servicedaud_ids,len(yearly_servicedaud_ids),"yearly_servicedaud_ids")
                else:
                    yearly_servicedaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type='SERVICE').order_by('-pk')
                    # print(yearly_servicedaud_ids,len(yearly_servicedaud_ids),"yearly_servicedaud_ids")

                service_lst = []

                for s in yearly_servicedaud_ids:
                    # print(s,s.pk,"SSS")
                    dept_code = s.dt_itemnoid.item_dept
                    # print(dept_code,"dept_code")
                    dept_ids = ItemDept.objects.filter(itm_code=dept_code,is_service=True, itm_status=True).first()
                    # print(dept_ids,"dept_ids")
                    if dept_ids:
                        # print("first iff")
                        # print(service_lst,"service_lst")
                        # print(any(d['code'] == dept_code for d in service_lst),"any")
                        # print(not any(d['code'] == dept_code for d in service_lst),"NOOT")
                        if not any(d['code'] == dept_code for d in service_lst):
                            # print("iff")
                            r = lambda: random.randint(0,255)
                            color = '#%02X%02X%02X' % (r(),r(),r())
                            # print(color,"kkk")
                            service_vals = {'code':dept_code,'name':dept_ids.itm_desc,'color':color}
                            # print(vals,"vals")
                            service_lst.append(service_vals)


                # print(service_lst,"service_lst")  
                tot_serviceamt = 0.0          
                for e in service_lst:
                    sdatalst = []
                    for i in range_lst:
                        if current_month == 1:
                            year = today_date.year
                            if i == 12:
                                year = today_date.year - 1
                        else:
                            year = today_date.year  

                        month_shaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,isvoid=False).order_by('-pk')
                        month_ssatranacno = list(set([i.sa_transacno for i in month_shaudids if i.sa_transacno]))
                        
                        eachmonth_service_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_ssatranacno,dt_status="SA",record_detail_type='SERVICE',
                        dt_itemnoid__item_dept=e['code']).order_by('-pk')
                        # print(eachmonth_service_ids,"eachmonth_service_ids")
                        eachmonth_serviceqty = sum([i.dt_transacamt for i in eachmonth_service_ids])
                        # print(eachmonth_serviceqty,"eachmonth_serviceqty")
                        tot_serviceamt += eachmonth_serviceqty
                        sdatalst.append(int(eachmonth_serviceqty))
                    e['data'] = sdatalst

                # print(service_lst,"service_lst After")     

                servicesales_data = {
                'title': { 'text': "Service Sales Amount" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': service_lst,
                'outlinetext' : "Total Service Sales Amount",
                'outlinevalue' : "{:.2f}".format(float(tot_serviceamt))        
                }  

                #Treatment Done Count

                if current_month == 1:
                    yearly_tddaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__date__gte=start_date,
                    sa_date__date__lte=end_date,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                    # print(yearly_tddaud_ids,len(yearly_tddaud_ids),"yearly_tddaud_ids")
                else:
                    yearly_tddaud_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month__in=range_lst,
                    sa_date__year__in=year_lst,sa_transacno__in=yearly_satranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD']).order_by('-pk')
                    # print(yearly_tddaud_ids,len(yearly_tddaud_ids),"yearly_tddaud_ids")

                td_lst = []

                for t in yearly_tddaud_ids:
                    # print(t,t.pk,"TTTT")
                    tdept_code = t.dt_itemnoid.item_dept
                    print(tdept_code,"tdept_code")
                    tdept_ids = ItemDept.objects.filter(itm_code=tdept_code,is_service=True, itm_status=True).first()
                    # print(tdept_ids,"tdept_ids")
                    if tdept_ids:
                        if t.st_ref_treatmentcode:
                            treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                            treatment_code=t.st_ref_treatmentcode,status='Done').order_by('-pk').first()
                            if treatids:
                                # print("first iff")
                                # print(td_lst,"td_lst")
                                # print(any(d['code'] == tdept_code for d in td_lst),"any")
                                # print(not any(d['code'] == tdept_code for d in td_lst),"NOOT")
                                if not any(d['code'] == tdept_code for d in td_lst):
                                    # print("iff")
                                    r = lambda: random.randint(0,255)
                                    color = '#%02X%02X%02X' % (r(),r(),r())
                                    # print(color,"kkk")
                                    td_vals = {'code':tdept_code,'name':tdept_ids.itm_desc,'color':color}
                                    # print(vals,"vals")
                                    td_lst.append(td_vals)

                # print(td_lst,"td_lst")  
                tot_tdcount = 0          
                for l in td_lst:
                    tddatalst = []
                    for i in range_lst:
                        if current_month == 1:
                            year = today_date.year
                            if i == 12:
                                year = today_date.year - 1
                        else:
                            year = today_date.year 

                        month_tdhaudids = PosHaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,isvoid=False).order_by('-pk')
                        month_tdsatranacno = list(set([i.sa_transacno for i in month_tdhaudids if i.sa_transacno]))
                        
                        eachmonth_td_ids = PosDaud.objects.filter(itemsite_code=site.itemsite_code,sa_date__month=i,
                        sa_date__year=year,sa_transacno__in=month_tdsatranacno,dt_status="SA",record_detail_type__in=['SERVICE','TD'],
                        dt_itemnoid__item_dept=l['code']).order_by('-pk')
                        # print(eachmonth_td_ids,"eachmonth_td_ids")
                        refer_lstmonth = list(set([i.st_ref_treatmentcode for i in eachmonth_td_ids if i.st_ref_treatmentcode]))
                        # print(refer_lst,"refer_lst")

                        month_treatids = Treatment.objects.filter(site_code=site.itemsite_code,
                        treatment_code__in=refer_lstmonth,status='Done',Item_Codeid__item_dept=l['code']).order_by('-pk')
                        
                        monthly_tdqty = month_treatids.count()
                        tot_tdcount += monthly_tdqty
                        tddatalst.append(monthly_tdqty)
                    l['data'] = tddatalst

                # print(td_lst,"td_lst After")  

                treatmentdone_data = {
                'title': { 'text': "Treatment Done Count" },
                'xAxis' : {'categories': categories, 'labels':  {'step': xstep} },
                'yAxis' : {'min': 0, 'title': {'text': ""}, 'labels' : {'step': 1, 'format' : "{value}"}},
                'legend': {'position': "bottom",'align': "center"},
                'series': td_lst,
                'outlinetext' : "Total Number of Treatment Done Count",
                'outlinevalue' : tot_tdcount        
                }  


                result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
                'data': [newcust_data,produtsold_data,servicesales_data,treatmentdone_data]}                    


            tnow1 = timezone.now()
            # print(str(tnow1.hour) + '  ' +  str(tnow1.minute) + '  ' +  str(tnow1.second),"End hour, minute, second\n")
            total = tnow1.second - tnow.second
            # print(total,"total")
                   
            return Response(result,status=status.HTTP_200_OK)
        # except Exception as e:
        #    invalid_message = str(e)
        #    return general_error_response(invalid_message)          
    
class BillingViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = BillingSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        year = timezone.now().year
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        transac_no = self.request.GET.get('transac_no',None)
        cust_code = self.request.GET.get('cust_code',None)
        cust_name = self.request.GET.get('cust_name',None)
        queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('-pk')
        # queryset = PosHaud.objects.filter().order_by('-pk')

        if cust_code:
            if cust_code != '':
                cust_obj = Customer.objects.filter(pk=cust_code).only('cust_code').first()
                if cust_obj:
                    cust_code = cust_obj.cust_code
        if not from_date and not to_date and not transac_no and not cust_code and not cust_name:
            queryset = queryset
        else:
            if from_date and to_date: 
                queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('-pk')
            if transac_no:
                queryset = queryset.filter(sa_transacno_ref__icontains=transac_no).order_by('-pk')
            if cust_code:
                queryset = queryset.filter(sa_custno__icontains=cust_code).order_by('-pk')
            if cust_name:
                queryset = queryset.filter(sa_custname__icontains=cust_name).order_by('-pk')
        return queryset
    
    def list(self, request):
        # try:
            year = timezone.now().year
            queryset = self.filter_queryset(self.get_queryset()).order_by('-pk')
            # queryset = PosHaud.objects.filter(sa_date__year=year).order_by('-pk')
            serializer_class =  BillingSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)   
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)     


class CreditNotePayAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CreditNotePaySerializer

    def get(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = fmspw.loginsite
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code, status='OPEN',site_code=site.itemsite_code).only('cust_code','status').order_by('pk')

            if queryset:
                serializer = CreditNotePaySerializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK, "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message": "No Content",'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


class PrepaidPayViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = PrepaidPaySerializer
    queryset = PrepaidAccount.objects.filter().order_by('-id')

    def get_queryset(self,request):
        global type_ex
        type_ex.append('Sales')
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
        # print(fmspw,"fmspw")
        site = fmspw.loginsite
        cart_date = timezone.now().date()
        cust_obj = Customer.objects.filter(pk=self.request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
        cart_id = self.request.GET.get('cart_id',None)

        cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
        cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')
        # print(cartc_ids,"cartc_ids")
        if cartc_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        cartids = ItemCart.objects.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
        cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code,
        itemcodeid__item_div__in=[1,3]).exclude(type__in=type_ex).order_by('lineno')
        if not cartids:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Given Cart ID does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        return cartids

    def list(self, request):
        # try:
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
        site = fmspw.loginsite
        cust_id = self.request.GET.get('cust_id', None)
        cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
        if cust_obj is None:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Customer ID does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        cart_id = self.request.GET.get('cart_id',None)
        if not cart_id:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart_id is not given",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        cartids = self.filter_queryset(self.get_queryset(request))

        cartquery = []
        if cartids:    
            cartquery = CartPrepaidSerializer(cartids, many=True)     
        
        queryset = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,status=True).only('site_code','cust_code','status').order_by('pk')
        if queryset:
            serializer = PrepaidPaySerializer(queryset, many=True)
            data = {'pp_data':serializer.data,'cart_data': cartquery.data if cartquery else []}
            result = {'status': status.HTTP_200_OK, "message": "Listed Succesfully", 'error': False, 'data': data}
            return Response(data=result, status=status.HTTP_200_OK)
        else:
            result = {'status': status.HTTP_204_NO_CONTENT,"message": "No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)
    
    def get_object(self, pk):
        try:
            return PrepaidAccount.objects.get(pk=pk)
        except PrepaidAccount.DoesNotExist:
            raise Http404

    def partial_update(self, request, pk=None):
        global type_ex
        type_ex.append('Sales')
        pp = self.get_object(pk)  
        serializer = PrepaidPaySerializer(pp, data=request.data, partial=True)
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
        site = fmspw.loginsite
        cart_date = timezone.now().date()
        cust_obj = Customer.objects.filter(cust_code=pp.cust_code,cust_isactive=True).only('cust_code','cust_isactive').first()
        cart_id = self.request.GET.get('cart_id',None)
        if not cart_id:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"cart_id is not given",'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        cartc_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
        cart_id=cart_id,cart_status="Completed",is_payment=True,sitecode=site.itemsite_code).exclude(type__in=type_ex).order_by('lineno')
        if cartc_ids:
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done!!",'error': True} 
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
        cartids = ItemCart.objects.filter(cust_noid=cust_obj,cart_id=cart_id,cart_date=cart_date,
        cart_status="Inprogress",isactive=True,is_payment=False,sitecode=site.itemsite_code,
        itemcodeid__item_div__in=[1,3]).exclude(type__in=type_ex).order_by('lineno')
        if not cartids:
            result = {'status': status.HTTP_400_BAD_REQUEST, "message": "Given Cart ID does not exist!!", 'error': True}
            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            
            div = list(set([c.itemcodeid.item_div for c in cartids if c.itemcodeid.item_div]))
            open_ids = PrepaidAccountCondition.objects.filter(pp_no=pp.pp_no,
            pos_daud_lineno=pp.line_no).only('pp_no','pos_daud_lineno').first()
            if open_ids:
                if open_ids.conditiontype1 == "Product Only":
                    if '1' not in div:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Condition found for Retail Product in order list",'error': True}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                elif open_ids.conditiontype1 == "Service Only":
                    if '3' not in div:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Condition found for Service in order list",'error': True}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                elif open_ids.conditiontype1 == "All":
                    if '1' not in div and '3' not in div:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"No Condition found for Service/Retail Product in order list",'error': True}
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                        
            result = {'status': status.HTTP_200_OK,"message":"Checked Succesfully",'error': False}
            return Response(result, status=status.HTTP_200_OK)

        result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
        return Response(result, status=status.HTTP_200_OK)    
            


# class DeleteAPIView(generics.CreateAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         cart_ids = ItemCart.objects.filter(customercode='HQ100022',price=0)
#         treat_ids = Treatment.objects.filter(cust_code='HQ100022',unit_amount=0)
#         return Response(data="deleted sucessfully", status=status.HTTP_200_OK)         
    

# class ControlAPIView(generics.CreateAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         site_ids = ItemSitelist.objects.filter().exclude(itemsite_code='HQ')
#         control_ids = ControlNo.objects.filter(site_code='HQ')
#         for s in site_ids:
#             for c in control_ids:
#                 ControlNo(control_no=c.control_no,control_prefix=c.control_prefix,
#                 control_description=c.control_description,controldate=c.controldate,
#                 Site_Codeid=s,site_code=s.itemsite_code,mac_code=c.mac_code).save()

#         return Response(data="Created Sucessfully", status=status.HTTP_200_OK)         

class HolditemdetailViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Holditemdetail.objects.filter().order_by('-id')
    serializer_class = HolditemdetailSerializer

    
    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            site = fmspw.loginsite
            queryset = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
            status='OPEN').order_by('-pk')
            satrasc_ids = list(set([e.sa_transacno for e in queryset if e.sa_transacno]))
            # print(satrasc_ids,"satrasc_ids")


            lst = [] ; final = []
            if satrasc_ids:
                for q in satrasc_ids:
                    # print(q,"sa_transacno")
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno=q,sa_transacno_type='Receipt',
                    ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
                    # print(pos_haud,"pos_haud")

                    if pos_haud:
                        line_ids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
                        status='OPEN',sa_transacno=q).order_by('-pk')

                        lineno_ids = list(set([e.hi_lineno for e in line_ids if e.hi_lineno]))
                        # print(lineno_ids,"lineno_ids")
 
                        if lineno_ids:
                            for l in lineno_ids:
                                # print(l,"line noo")
                                queryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
                                status='OPEN',sa_transacno=q,hi_lineno=l
                                ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk').last()
                                # print(queryids,"queryids")
                                if queryids:
                                    depoids = DepositAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
                                    sa_status="SA",sa_transacno=q,item_barcode=queryids.itemno,dt_lineno=l).only('site_code','cust_code','sa_status').order_by('pk').last()
                                    # print(depoids,"depoids")
                                    if depoids:
                                        laqueryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=cust_obj.cust_code,
                                        status='OPEN',sa_transacno=q,hi_lineno=l,itemno=queryids.itemno
                                        ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk').last()
                                        # print(laqueryids,"laqueryids")
                                        if laqueryids:
                                            if laqueryids.pk not in lst:
                                                lst.append(laqueryids.pk)
                                                if laqueryids.sa_date:
                                                    # print(laqueryids.sa_date,"data['sa_date']")
                                                    splt = str(laqueryids.sa_date).split(" ")
                                                    sa_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d/%m/%Y")

                                                    check = "" 
                                                    if depoids.outstanding == 0:
                                                        check = "fullpay"
                                                    elif depoids.outstanding > 0:
                                                        check = "partialpay"    

                            
                                                    val ={'id':laqueryids.pk,'sa_date':sa_date,'sa_transacno_ref':pos_haud.sa_transacno_ref,
                                                    'hi_itemdesc':laqueryids.hi_itemdesc,'itemno':laqueryids.itemno,
                                                    'holditemqty':laqueryids.holditemqty,'qty_issued':"",'staff_issued':"",'check':check}
                                                    final.append(val)

              
            # print(lst,"lst")
            if final != []:
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                'data': final}
                return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)  


    def get_object(self, pk):
        try:
            return Holditemdetail.objects.get(pk=pk)
        except Holditemdetail.DoesNotExist:
            raise Http404       

    def retrieve(self, request, pk=None):
        try:
            holditem = self.get_object(pk)
            serializer = HolditemSerializer(holditem)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[TokenAuthentication])
    def issued(self, request):  
        try:
        # if self:
            if request.data:
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite 
                
                for idx, reqt in enumerate(request.data, start=1): 
                    hold_obj = Holditemdetail.objects.filter(hi_no=reqt['id']).first()
                    if not hold_obj:
                        raise Exception('Holditemdetail id Does not exist')

                    # cust_obj = Customer.objects.filter(cust_code=hold_obj.sa_custno,cust_isactive=True,site_code=site.itemsite_code).first()
                    cust_obj = Customer.objects.filter(cust_code=hold_obj.sa_custno,cust_isactive=True).first()
                    if not cust_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Customer ID does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    if not reqt['issued_qty']:
                        msg = "{0} This Product issued qty should not empty".format(str(hold_obj.hi_itemdesc))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                    if not reqt['emp_id']:
                        msg = "{0} This Product staff issued should not empty".format(str(hold_obj.hi_itemdesc))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                    if int(reqt['issued_qty']) <= 0:
                        msg = "{0} This Product issued qty should not be less than 0".format(str(hold_obj.hi_itemdesc))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

    
                    if int(reqt['issued_qty']) > int(hold_obj.holditemqty) :
                        msg = "{0} This Product should not greater than Qty Hold".format(str(hold_obj.hi_itemdesc))
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message": msg,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)

                    empobj = Employee.objects.filter(pk=int(reqt['emp_id']),emp_isactive=True).first()
                    if not empobj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee ID does not exist!!",'error': True} 
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                # print(request.data,"request.data")
                lst = []
                for idx, req in enumerate(request.data, start=1): 
                    # print(req,"req")

                    serializer = HolditemupdateSerializer(data=req)
                    if serializer.is_valid():
                        holdobj = Holditemdetail.objects.filter(hi_no=req['id']).first()
                        new_balance = int(holdobj.holditemqty) - int(req['issued_qty'])
                        val = {'sa_transacno':holdobj.sa_transacno,'hi_itemdesc':holdobj.hi_itemdesc,
                        'balance':holdobj.holditemqty,'issued_qty':int(req['issued_qty']),
                        'new_balance':new_balance,'id': holdobj.pk}
                        lst.append(val)
                        
                        emp_obj = Employee.objects.filter(pk=int(req['emp_id']),emp_isactive=True).first()
                       
                        remainqty = int(holdobj.holditemqty) - int(req['issued_qty']) 
                        # print(remainqty,"remainqty")

                        laqueryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=holdobj.sa_custno,
                        status='OPEN',sa_transacno=holdobj.sa_transacno,hi_lineno=holdobj.hi_lineno,itemno=holdobj.itemno
                        ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk')
                        # print(laqueryids,"laqueryids")
                        length = len(laqueryids) + 1

                        con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                        if not con_obj:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                        product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                        

                        hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=holdobj.sa_transacno,
                        transacamt=holdobj.transacamt,itemno=holdobj.itemno,
                        hi_staffno=emp_obj.emp_code,
                        hi_itemdesc=holdobj.hi_itemdesc,hi_price=holdobj.hi_price,hi_amt=holdobj.hi_amt,hi_qty=holdobj.hi_qty,
                        hi_staffname=emp_obj.emp_name,
                        hi_lineno=holdobj.hi_lineno,hi_uom=holdobj.hi_uom,hold_item=True,hi_deposit=holdobj.hi_deposit,
                        holditemqty=remainqty,sa_custno=holdobj.sa_custno,
                        sa_custname=holdobj.sa_custname,history_line=length,hold_type=holdobj.hold_type,
                        product_issues_no=product_issues_no) 

                        if remainqty == 0:
                            oldqueryids = Holditemdetail.objects.filter(itemsite_code=site.itemsite_code,sa_custno=holdobj.sa_custno,
                            status='OPEN',sa_transacno=holdobj.sa_transacno,hi_lineno=holdobj.hi_lineno,itemno=holdobj.itemno
                            ).only('itemsite_code','sa_custno','status','sa_transacno','itemno','hi_lineno').order_by('pk').update(status="CLOSE")
                            print(oldqueryids,"oldqueryids")
                            
                            hold.status = "CLOSE"

                            hold.save()
                        elif remainqty > 0: 

                            hold.status = "OPEN"
                            hold.save()

                        qtytodeduct = int(req['issued_qty'])
                        deduct = 0
                        batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=holdobj.itemno[:8],
                        uom=holdobj.hi_uom).order_by('pk').last() 
                        #ItemBatch
                        if batchids:
                            # deduct = batchids.qty - c.quantity
                            deduct = batchids.qty - qtytodeduct
                            batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                        else:
                            batch_id = ItemBatch(item_code=holdobj.itemno[:8],site_code=site.itemsite_code,
                            batch_no="",uom=holdobj.hi_uom,qty=-qtytodeduct,exp_date=None,batch_cost=0).save()
                            deduct = -qtytodeduct

                        #Stktrn
                        currenttime = timezone.now()
                        currentdate = timezone.now().date()
                   
                        post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                        stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=holdobj.itemno,
                        item_uom=holdobj.hi_uom).order_by('pk').last() 

                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=holdobj.itemno,
                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=holdobj.sa_transacno,trn_date=currentdate,
                        trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                        trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                        trn_amt=stktrn_ids.trn_amt if stktrn_ids and stktrn_ids.trn_amt else 0,
                        trn_post=currentdate,
                        trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                        hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                        line_no=1,item_uom=holdobj.hi_uom,item_batch=None,mov_type=None,item_batch_cost=None,
                        stock_in=None,trans_package_line_no=None).save()

                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                
                if lst != []:
                    # print(lst[0])
                    value = lst[0]['id']
                    # print(value,"value")
                    title = Title.objects.filter(product_license='HQ').first()
                    # holdids = Holditemdetail.objects.filter(pk__in=lst)
                    hold_ids = Holditemdetail.objects.filter(pk=value).order_by('-pk').first()

                    path = None
                    if title and title.logo_pic:
                        path = BASE_DIR + title.logo_pic.url

                    split = str(hold_ids.sa_date).split(" ")
                    date = datetime.datetime.strptime(str(split[0]), '%Y-%m-%d').strftime("%d/%m/%Y")

   
                    data = {'name': title.trans_h1 if title and title.trans_h1 else '', 
                    'address': title.trans_h2 if title and title.trans_h2 else '', 
                    'footer1':title.trans_footer1 if title and title.trans_footer1 else '',
                    'footer2':title.trans_footer2 if title and title.trans_footer2 else '',
                    'footer3':title.trans_footer3 if title and title.trans_footer3 else '',
                    'footer4':title.trans_footer4 if title and title.trans_footer4 else '',
                    'hold_ids': hold_ids, 'date':date,
                    'hold': lst,'cust':cust_obj,'staff':hold_ids.hi_staffname,'fmspw':fmspw,
                    'path':path if path else '','title':title if title else None,
                    }

                    template = get_template('hold_item.html')
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

                    dst ="holditem_" + str(str(hold_ids.sa_transacno)) + ".pdf"

   
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

                            ip_link = "http://"+request.META['HTTP_HOST']+"/media/pdf/holditem_"+str(hold_ids.sa_transacno)+".pdf"


                            result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                            'error': False,'data': ip_link}
                            return Response(result, status=status.HTTP_200_OK)         
            else:
                raise Exception('Request body data does not exist') 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)  

       
class TreatmentHistoryAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Treatment.objects.filter().order_by('id')
    serializer_class = TreatmentHistorySerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id',None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id',None),cust_isactive=True).first()
            if not cust_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give customer id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  

            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code).filter(~Q(status="Open")).order_by('-pk')
            # print(queryset,"queryset") 
            if request.GET.get('year',None):
                year = request.GET.get('year',None)
                if year != "All":
                    queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
                    treatment_date__year=year).filter(~Q(status="Open")).order_by('-pk') 

            serializer_class = TreatmentHistorySerializer
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
                    i = dict(dat)
                    # print(i,"ii")
                    trmt_obj = Treatment.objects.filter(pk=i['id']).first()
                    splt = str(trmt_obj.treatment_date).split(' ')

                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
                    sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=trmt_obj.sa_transacno).first()
                  
                    if pos_haud: 
                        splt_sa = str(pos_haud.sa_date).split(' ')

                        i['trasac_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d/%m/%Y")
                        i['purchase_date'] = datetime.datetime.strptime(str(splt_sa[0]), "%Y-%m-%d").strftime("%d/%m/%Y")
                        i['transac'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                        i['link_code'] = ""
                        i['record_status'] = i['record_status'] if i['record_status'] else ""
                        i['remarks'] = i['remarks'] if i['remarks'] else ""

                    final.append(i)

                v['dataList'] =  final  
                return Response(result, status=status.HTTP_200_OK)  
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Content",'error': False, 'data': []}
                return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        



class StockUsageViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Treatment.objects.filter().order_by('-id')
    serializer_class = StockUsageSerializer

    def get_object(self, pk):
        # try:
            return Treatment.objects.get(pk=pk)
        # except Treatment.DoesNotExist:
        #     raise Exception('Record does not exist') 

    def retrieve(self, request, pk=None):
        # try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            treat = self.get_object(pk)
            treat_obj = Treatment.objects.filter(pk=treat.pk,site_code=site.itemsite_code).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            serializer = StockUsageSerializer(treat)
            # print(serializer.data,"data")
            newdict = {"remarks": treat.remarks if treat.remarks else ""}
            newdict.update(serializer.data)

            accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
            type="Sales").order_by('id').first()

            if not accids:
                result = {'status': status.HTTP_200_OK,"message":"Treatment Account is not there!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

                        
            usageids = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
            site_code=site.itemsite_code,sa_transacno=accids.sa_transacno,isactive=True).order_by('pk')

            uselst = [{'id': u.pk,'no':i,'item_code': u.item_code[:-4],'item_desc': u.item_desc, 'qty': int(u.qty), 'uom': u.uom} for i,u in enumerate(usageids,start=1)]
            
            for u in uselst:
                u['link_code'] = ""
                code = u['item_code']+"0000"
                linkobj = ItemLink.objects.filter(item_code=code,link_type='L',itm_isactive=True).order_by('pk')
                if linkobj:
                    u['link_code'] = linkobj[0].link_code

            newdict['usage'] = uselst

            helper_ids = ItemHelper.objects.filter(item_code=treat_obj.treatment_code,
            sa_transacno=treat_obj.sa_transacno,site_code=site.itemsite_code).order_by('-pk')
            staffs = [{'no':idx, 'staff_code': h.helper_code, 'helper_name': h.helper_name} for idx, h in enumerate(helper_ids, start=1)]
            
            newdict['staffs'] = staffs
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
            'data':  newdict}
            return Response(result, status=status.HTTP_200_OK)

        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message) 

    def create(self, request):
        # try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            
            accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
            type="Sales").order_by('id').first()
            if not accids:
                result = {'status': status.HTTP_200_OK,"message":"Treatment Account is not there!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            now = datetime.datetime.now()
            s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))

            for idx, req in enumerate(request.data, start=1):
                # print(req,"req 4444")
                serializer = TreatmentUsageSerializer(data=req)
                if serializer.is_valid():
                    stock_obj = Stock.objects.filter(pk=req['stock_id'],item_isactive=True).first()
                   
                    useids = TreatmentUsage.objects.filter(treatment_code=treat_obj.treatment_code,
                    site_code=site.itemsite_code,sa_transacno=accids.sa_transacno).order_by('line_no') 

                    if not useids:
                        lineno = 1
                    else:
                        rec = useids.last()
                        lineno = float(rec.line_no) + 1  

                    use = serializer.save(treatment_code=treat_obj.treatment_code,
                    item_code=req['item_code']+"0000",item_desc=stock_obj.item_desc,
                    site_code=site.itemsite_code,usage_status="Usage",line_no=lineno,
                    usage_update=s1,
                    sa_transacno=accids.sa_transacno if accids and accids.sa_transacno else "")
                    
                    # Inventory Control
                   
                    if req['qty'] > 0:
                        batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=req['item_code'],
                        uom=req['uom']).order_by('pk').last() 
                        #ItemBatch
                        if batchids:
                            deduct = batchids.qty - int(req['qty'])
                            batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                        else:
                            batch_id = ItemBatch(item_code=req['item_code'],site_code=site.itemsite_code,
                            batch_no="",uom=req['uom'],qty=-req['qty'],exp_date=None,batch_cost=stock_obj.lstpo_ucst).save()
                            deduct = -req['qty']

                        #Stktrn
                        currenttime = timezone.now()
                        currentdate = timezone.now().date()
                   
                        post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                        stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(req['item_code'])+"0000",
                        item_uom=req['uom']).order_by('pk').last() 

                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(req['item_code'])+"0000",
                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=treat_obj.treatment_code,trn_date=currentdate,
                        trn_type="Usage",trn_db_qty=None,trn_cr_qty=None,trn_qty=-req['qty'],trn_balqty=deduct,
                        trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                        trn_amt=None,trn_post=currentdate,
                        trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                        hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                        line_no=lineno,item_uom=req['uom'],item_batch=None,mov_type=None,item_batch_cost=None,
                        stock_in=None,trans_package_line_no=None).save()


                else:
                    data = serializer.errors
                    # print(data,"data")
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            if request.GET.get('treat_remarks',None):
                treat_obj.remarks = request.GET.get('treat_remarks',None)
                treat_obj.save()

            result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",'error': False}
            return Response(result, status=status.HTTP_201_CREATED)

        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message) 
    
    def get_object_usage(self, pk):
        # try:
            return TreatmentUsage.objects.get(pk=pk)
        # except TreatmentUsage.DoesNotExist:
        #    raise Exception('Record does not exist') 

    def partial_update(self, request, pk=None):
        # try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            
            accids = TreatmentAccount.objects.filter(ref_transacno=treat_obj.sa_transacno,
            treatment_parentcode=treat_obj.treatment_parentcode,site_code=site.itemsite_code,ref_no=treat_obj.treatment_code,
            type="Sales").order_by('id').first()
            if not accids:
                result = {'status': status.HTTP_200_OK,"message":"Treatment Account is not there!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            instance = self.get_object_usage(pk)
            # print(instance,"instance")
            if instance:
                now = datetime.datetime.now()
                s1 = str(now.strftime("%Y/%m/%d %H:%M:%S"))
  
                instance.isactive = False
                instance.usage_update = s1
                instance.save()
                useids = TreatmentUsage.objects.filter(treatment_code=instance.treatment_code,
                site_code=site.itemsite_code,sa_transacno=accids.sa_transacno).order_by('line_no') 

                rec = useids.last()
                lineno = float(rec.line_no) + 1    

            
                TreatmentUsage(treatment_code=instance.treatment_code,item_code=instance.item_code,
                item_desc=instance.item_desc,qty=-instance.qty,uom=instance.uom,site_code=instance.site_code,
                usage_status="Void Usage",line_no=lineno,void_line_ref=1,usage_update=s1,
                sa_transacno=instance.sa_transacno,isactive=False).save()
                
                #ItemBatch
                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                item_code=instance.item_code,uom=instance.uom).order_by('pk').last()
                
                if batch_ids:
                    addamt = batch_ids.qty + instance.qty
                    batch_ids.qty = addamt
                    batch_ids.updated_at = timezone.now()
                    batch_ids.save()

                #Stktrn
                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                itemcode=instance.item_code,item_uom=instance.uom).last() 
                # print(stktrn_ids,"stktrn_ids")

                currenttime = timezone.now()

                post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                
                if stktrn_ids:
                    amt_add = stktrn_ids.trn_balqty + instance.qty

                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=instance.item_code,store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=instance.treatment_code,
                    trn_type="Void Usage",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=instance.qty,trn_balqty=amt_add,trn_balcst=None,
                    trn_amt=None,trn_cost=None,trn_ref=None,
                    hq_update=0,line_no=instance.line_no,item_uom=instance.uom,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None).save()
            
                
                result = {'status': status.HTTP_200_OK,"message":"Deleted Succesfully",'error': False}
                return Response(result,status=status.HTTP_200_OK)     
            else:
                result = {'status': status.HTTP_200_OK,"message":"No Content",'error': True}
                return Response(result,status=status.HTTP_200_OK)  
        # except Exception as e:
        #     invalid_message = str(e)
        #     return general_error_response(invalid_message)        

            

class StockUsageProductAPIView(generics.ListAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockUsageProductSerializer

    def list(self, request):
        try:
            queryset = Stock.objects.filter(item_isactive=True, item_div="2").order_by('pk')
            if request.GET.get('is_retail',None) and int(request.GET.get('is_retail',None)) == 1:
                queryset = Stock.objects.filter(item_isactive=True, item_div="1").order_by('pk')
            elif request.GET.get('is_retail',None) and int(request.GET.get('is_retail',None)) == 2:
                queryset = Stock.objects.filter(item_isactive=True).filter(Q(item_div="1") | Q(item_div="2")).order_by('pk')
        
            if request.GET.get('search',None):
                if not request.GET.get('search',None) is None:
                    queryset = queryset.filter(Q(item_name__icontains=request.GET.get('search',None)
                    ) | Q(item_desc__icontains=request.GET.get('search',None)) | Q(item_code__icontains=request.GET.get('search',None)))

            serializer_class =  StockUsageProductSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action='list')
            v = result.get('data')
            d = v.get("dataList")
            lst = []
            for dat in d:
                q = dict(dat)
               
                q['link_code'] = ""
                code = q['item_code']+"0000"
                linkobj = ItemLink.objects.filter(item_code=code,link_type='L',itm_isactive=True).order_by('pk')
                if linkobj:
                   q['link_code'] = linkobj[0].link_code

                uomlst = []
                stock = Stock.objects.filter(item_isactive=True, pk=q['id']).first()
                itemuomprice = ItemUomprice.objects.filter(isactive=True, item_code=stock.item_code).order_by('id')
                
                for i in itemuomprice:
                    itemuom = ItemUom.objects.filter(uom_isactive=True,uom_code=i.item_uom).order_by('id').first()
                    itemuom_id = None; itemuom_desc = None
                    if itemuom:
                        itemuom_id = int(itemuom.id)
                        itemuom_desc = itemuom.uom_desc
                    uom = {
                            "itemuomprice_id": int(i.id),
                            "item_uom": i.item_uom,
                            "uom_desc": i.uom_desc,
                            "item_price": "{:.2f}".format(float(i.item_price)),
                            "itemuom_id": itemuom_id, 
                            "itemuom_desc" : itemuom_desc}
                    uomlst.append(uom)

                val = {'uomprice': uomlst}  
                q.update(val) 
                lst.append(q)
                v['dataList'] = lst    
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

class StockUsageMemoViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = UsageMemo.objects.filter().order_by('-id')
    serializer_class = StockUsageMemoSerializer

    def list(self, request):
        try:
            serializer_class = StockUsageMemoSerializer
            if not request.GET.get('date'):
                result = {'status': status.HTTP_200_OK,"message":"Please give Date!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            queryset = UsageMemo.objects.filter(date_out__date=request.GET.get('date'),qty__gt=0).order_by('-pk')
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset,total,  state, message, error, serializer_class, data, action=self.action)
            
            v = result.get('data')
            d = v.get("dataList")
            for dat in d:
                # print(dat['date_out'],"dat['date_out']")
                splt_sa = str(dat['date_out']).split('T')
                dat["date_out"] = datetime.datetime.strptime(str(splt_sa[0]), "%Y-%m-%d").strftime("%d/%m/%Y")
                
            return Response(result, status=status.HTTP_200_OK)  
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)            
    

    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            control_obj = ControlNo.objects.filter(control_description__iexact="STOCK USAGE MEMO",site_code=site.itemsite_code).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"STOCK USAGE MEMO Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            memo_no = str(control_obj.site_code)+str(control_obj.control_no)
            if not request.data['stock_id']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Stock Id!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            if not request.data['emp_id']:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please Give Emp Id!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
    

            stock_obj = Stock.objects.filter(pk=request.data['stock_id'],item_isactive=True).first()
            if not stock_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Stock id Does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            emp_obj = Employee.objects.filter(pk=request.data['emp_id'],emp_isactive=True).first()
            if not emp_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee id Does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
            
            time = datetime.datetime.now().time()
            date = datetime.datetime.strptime(str(request.data['date']), "%Y-%m-%d")
            datetime_new = datetime.datetime.combine(date, time)
    
            serializer = StockUsageMemoSerializer(data=request.data)
            if serializer.is_valid():

                k = serializer.save(date_out=datetime_new,memo_no=memo_no,item_code=stock_obj.item_code+"0000",item_name=stock_obj.item_name,
                staff_code=emp_obj.emp_code,staff_name=emp_obj.display_name,staff_barcode=emp_obj.emp_code,
                date_return=None,time_return=None,created_by=fmspw.pw_userlogin,status="OUT",site_code=site.itemsite_code)
                
                if k.pk:
                    control_obj.control_no = int(control_obj.control_no) + 1
                    control_obj.save()

                if request.data['qty'] > 0:
                    batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=stock_obj.item_code,
                    uom=request.data['uom']).order_by('pk').last() 
                    #ItemBatch
                    if batchids:
                        deduct = batchids.qty - int(request.data['qty'])
                        batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                    else:
                        batch_id = ItemBatch(item_code=stock_obj.item_code,site_code=site.itemsite_code,
                        batch_no=None,uom=request.data['uom'],qty=-request.data['qty'],exp_date=None,batch_cost=stock_obj.lstpo_ucst).save()
                        deduct = -request.data['qty']


                    #Stktrn
                    currenttime = timezone.now()
                    currentdate = timezone.now().date()
                
                    post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                    stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(stock_obj.item_code)+"0000",
                    item_uom=request.data['uom']).order_by('pk').last() 

                    itemuom_ids = ItemUomprice.objects.filter(item_code=stock_obj.item_code,item_uom=request.data['uom']).order_by('pk').first()

                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(stock_obj.item_code)+"0000",
                    store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=memo_no,
                    trn_type="SUM",trn_db_qty=None,trn_cr_qty=None,trn_qty=-request.data['qty'],trn_balqty=deduct,
                    trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                    trn_amt=itemuom_ids.item_price if itemuom_ids and itemuom_ids.item_price else None,
                    trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                    hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                    line_no=1,item_uom=request.data['uom'],item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None).save()
    

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
            return UsageMemo.objects.get(pk=pk)
        except UsageMemo.DoesNotExist:
            raise Exception('Record does not exist') 

    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            if int(request.data['quantity']) <= 0:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please enter valid quantity",
                'error': True}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

            instance = self.get_object(pk)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                quantity = instance.qty - request.data['quantity']
                serializer.save(qty=quantity,updated_at=timezone.now())
                
                
                #ItemBatch
                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                item_code=instance.item_code[:-4],uom=instance.uom).order_by('pk').last()
                
                if batch_ids:
                    addamt = batch_ids.qty + request.data['quantity']
                    batch_ids.qty = addamt
                    batch_ids.updated_at = timezone.now()
                    batch_ids.save()

                #Stktrn
                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                itemcode=instance.item_code,item_uom=instance.uom).last() 
                # print(stktrn_ids,"stktrn_ids")

                currenttime = timezone.now()

                post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                itemuom_ids = ItemUomprice.objects.filter(item_code=instance.item_code[:-4],item_uom=instance.uom).order_by('pk').first()

                
                if stktrn_ids:
                    amt_add = stktrn_ids.trn_balqty + request.data['quantity']

                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=instance.item_code,store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=instance.memo_no,
                    trn_type="SUA",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=request.data['quantity'],trn_balqty=amt_add,trn_balcst=0,
                    trn_amt=itemuom_ids.item_price if itemuom_ids and itemuom_ids.item_price else None,
                    trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                    hq_update=0,line_no=1,item_uom=instance.uom,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None).save()
                

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",'error': False}
                return Response(result, status=status.HTTP_200_OK)

            result = {'status': status.HTTP_204_NO_CONTENT,"message":serializer.errors,'error': True}
            return Response(result, status=status.HTTP_200_OK) 

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        

class TreatmentFaceViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = Treatmentface.objects.filter().order_by('-id')
    serializer_class = TreatmentfaceSerializer

    def get_object(self, pk):
        try:
            return Treatmentface.objects.get(pk=pk)
        except Treatmentface.DoesNotExist:
            raise Exception('Record does not exist') 

    def list(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            treatface = Treatmentface.objects.filter(treatment_code=treat_obj.treatment_code,
            site_code=site.itemsite_code).order_by('pk').first()
           
            if treatface:
                serializer = TreatmentfaceSerializer(treatface)
                newdict = dict()
                newdict.update(serializer.data)
                newdict.update({'room_id':treat_obj.Trmt_Room_Codeid.pk if treat_obj.Trmt_Room_Codeid else "",
                'room_name': treat_obj.Trmt_Room_Codeid.displayname if treat_obj.Trmt_Room_Codeid else "",
                'remarks': treat_obj.remarks})
                 
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
                'data':  newdict}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
                'data':  []}
                return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            if request.GET.get('treat_id',None):
                treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
                if not treat_obj:
                    result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                    return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            
            treatface_ids = Treatmentface.objects.filter(treatment_code=treat_obj.treatment_code,
            site_code=site.itemsite_code).order_by('pk')
            if treatface_ids:
                result = {'status': status.HTTP_200_OK,"message":"Already Record is there for Treatment Face!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            
           
            serializer = TreatmentfaceSerializer(data=request.data)
            if serializer.is_valid():
                treat_obj.remarks = request.data['treat_remarks']
                if request.data['room_id']:
                    room_obj = Room.objects.filter(pk=request.data['room_id'],site_code=site.itemsite_code).first()
                    treat_obj.Trmt_Room_Codeid = room_obj if room_obj else None
                    treat_obj.trmt_room_code = room_obj.room_code
                    treat_obj.save()
                
                serializer.save(site_code=site.itemsite_code)

                result = {'status': status.HTTP_201_CREATED,"message":"Created Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_201_CREATED)
            
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",
            'error': True, 'data': serializer.errors}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
            

    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            instance = self.get_object(pk)
            treat_obj = Treatment.objects.filter(pk=request.GET.get('treat_id',None),site_code=site.itemsite_code).first()
            if not treat_obj:
                result = {'status': status.HTTP_200_OK,"message":"Please give Treatment id!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid(): 
                treat_obj.remarks = request.data['treat_remarks']
                if request.data['room_id']:
                    room_obj = Room.objects.filter(pk=request.data['room_id'],site_code=site.itemsite_code).first()
                    treat_obj.Trmt_Room_Codeid = room_obj if room_obj else None
                    treat_obj.trmt_room_code = room_obj.room_code
                    treat_obj.save()
                
                serializer.save(updated_at=timezone.now())

                result = {'status': status.HTTP_200_OK,"message":"Updated Succesfully",
                'error': False}
                return Response(result, status=status.HTTP_200_OK)
            
            
            data = serializer.errors
            result = {'status': status.HTTP_400_BAD_REQUEST,"message":data['non_field_errors'][0],'error': True, 'data': serializer.errors} 
            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
             
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
                 

class TransactionHistoryViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = BillingSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        year = timezone.now().year
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        transac_no = self.request.GET.get('transac_no',None)
        cust_code = self.request.GET.get('cust_code',None)
        cust_name = self.request.GET.get('cust_name',None)
        invoice_type = self.request.GET.get('invoice_type',None)
        cust_id = self.request.GET.get('cust_id',None)
        
        if cust_id:
            queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk,sa_custnoid__pk=cust_id).order_by('-pk')
        else:
            queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('-pk')


        if not from_date and not to_date and not transac_no and not cust_code and not cust_name:
            queryset = queryset
        else:
            if from_date and to_date:
                if invoice_type == "All": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date).order_by('-pk')
                elif invoice_type == "Sales": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    sa_transacno_type="Receipt").order_by('-pk')
                elif invoice_type == "Void": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    sa_transacno_type="Void Transaction").order_by('-pk')
                elif invoice_type == "TD": 
                    queryset = queryset.filter(sa_date__date__gte=from_date,sa_date__date__lte=to_date,
                    sa_transacno_type="Redeem Service").order_by('-pk')
                               
            if transac_no:
                if cust_id:
                    queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk,sa_date__date__gte=from_date,
                    sa_date__date__lte=to_date,sa_transacno_ref__icontains=transac_no,sa_custnoid__pk=cust_id).order_by('-pk')
                else:
                    queryset = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk,sa_date__date__gte=from_date,
                    sa_date__date__lte=to_date,sa_transacno_ref__icontains=transac_no).order_by('-pk')

            if cust_code:
                queryset = queryset.filter(sa_custno__icontains=cust_code).order_by('-pk')
            if cust_name:
                queryset = queryset.filter(sa_custname__icontains=cust_name).order_by('-pk')
        return queryset
    
    def list(self, request):
        try:
            year = timezone.now().year
            queryset = self.filter_queryset(self.get_queryset()).order_by('-pk')
            # queryset = PosHaud.objects.filter(sa_date__year=year).order_by('-pk')
            serializer_class =  BillingSerializer
            total = len(queryset)
            state = status.HTTP_200_OK
            message = "Listed Succesfully"
            error = False
            data = None
            result=response(self,request, queryset, total, state, message, error, serializer_class, data, action=self.action)
            return Response(result, status=status.HTTP_200_OK)   
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    
    
        
 
       


       
