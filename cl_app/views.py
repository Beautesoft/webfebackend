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
CartPrepaidSerializer, VoidCancelSerializer,HolditemdetailSerializer,HolditemSerializer,HolditemupdateSerializer)
from cl_table.serializers import PostaudSerializer, TmpItemHelperSerializer
from .models import (SiteGroup, ItemSitelist, ReverseTrmtReason, VoidReason)
from cl_table.models import (Employee, Fmspw, ItemClass, ItemDept, ItemRange, Stock, ItemUomprice, 
PackageDtl, ItemDiv, PosDaud, PosTaud, Customer, GstSetting, ControlNo, TreatmentAccount, DepositAccount, 
PrepaidAccount, Treatment,PosHaud,TmpItemHelper,Appointment,Source,PosHaud,ReverseDtl,ReverseHdr,
CreditNote,Multistaff,ItemHelper,ItemUom,Treatment_Master,Holditemdetail,PrepaidAccountCondition,
CnRefund,ItemBrand,Title,ItemBatch,Stktrn)
from custom.models import ItemCart, Room, Combo_Services,VoucherRecord
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
from cl_table.authentication import ExpiringTokenAuthentication
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

type_ex = ['VT-Deposit','VT-Top Up','VT-Sales']
type_tx = ['Deposit','Top Up','Sales']
# Create your views here.

class SalonViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
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
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Successfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                  
    
    # @authenticated_only
    def create(self, request):
        try:
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
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                    
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         
        
    def get_object(self, pk):
        try:
            return SiteGroup.objects.get(pk=pk,is_active=True)
        except SiteGroup.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         
            
    def update(self, request, pk=None):
        try:
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
        instance.is_active = False
        site = ItemSitelist.objects.filter(Site_Groupid=instance).update(Site_Groupid=None)
        instance.save()   


class CatalogItemDeptViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CatalogItemDeptSerializer

    def list(self, request):
        try:
            if not request.GET.get('Item_Dept', None) is None:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
             

    def get_object(self, pk):
        try:
            return ItemDept.objects.get(pk=pk,itm_status=True)
        except ItemDept.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            itemdept = self.get_object(pk)
            serializer = CatalogItemDeptSerializer(itemdept)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data':  serializer.data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

class CatalogItemRangeViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ItemRangeSerializer

    def list(self, request):
        try:
            if not request.GET.get('Item_Deptid',None) is None:
                item_id = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), itm_status=True).first() 
                if item_id:
                    queryset = ItemRange.objects.filter(itm_dept=item_id.itm_code, isservice=True).order_by('pk')
                if item_id is None:
                    branditem_id = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), itm_status=True).first()
                    if branditem_id:
                        queryset = ItemRange.objects.filter(itm_brand=branditem_id.itm_code).order_by('pk')
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
             

class ServiceStockViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_div="3").order_by('pk')
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_dept = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), is_service=True, itm_status=True).first()
                    if not item_dept:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_dept=item_dept.itm_code).order_by('pk')
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
                        queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_range=itemrange.itm_code).order_by('pk')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_type="SINGLE", item_dept=item_dept.itm_code).order_by('pk')
            
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
          

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True, item_type="SINGLE")
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         


class RetailStockListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockRetailSerializer

    def list(self, request):
        try:
            queryset = Stock.objects.filter(item_isactive=True, item_div="1").order_by('pk')
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None),retail_product_brand=True,itm_status=True).first()
                    if not item_brand:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Brand id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('pk')
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
                        queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code).order_by('pk')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('pk')
            
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
            for dat in d:
                q = dict(dat)
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
         

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
         

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
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_div="3").order_by('pk')
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_dept = ItemDept.objects.filter(pk=request.GET.get('Item_Deptid',None), is_service=True, itm_status=True).first()
                    if not item_dept:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code).order_by('pk')
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
                        queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_range=itemrange.itm_code).order_by('pk')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_type="PACKAGE", item_dept=item_dept.itm_code).order_by('pk')
            
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
            

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True, item_type="PACKAGE")
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                

class PackageDtlViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockIdSerializer

    def list(self, request):
        try:
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
                            "Description": p.description}
                        detail.append(package)
                    package_data = {"package_description": detail,
                                    "image" : image}
                    result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': package_data }
                else:
                    serializer = self.get_serializer()
                    result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                    

class PrepaidStockViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            queryset = Stock.objects.filter(item_isactive=True, item_div="5").order_by('pk')
            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), prepaid_brand=True).first()
                    if not item_brand:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('pk')
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
                        queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code).order_by('pk')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('pk')

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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                   

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                

class VoucherStockViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def list(self, request):
        try:
            queryset = Stock.objects.filter(item_isactive=True,  item_div="4").order_by('pk')

            if request.GET.get('Item_Deptid',None):
                if not request.GET.get('Item_Deptid',None) is None:
                    item_brand = ItemBrand.objects.filter(pk=request.GET.get('Item_Deptid',None), voucher_brand=True).first()
                    if not item_brand:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Dept id does not exist!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('pk')

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
                        queryset = Stock.objects.filter(item_isactive=True, item_range=itemrange.itm_code).order_by('pk')
                    else:
                        queryset = Stock.objects.filter(item_isactive=True, item_brand=item_brand.itm_code).order_by('pk')
            
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                  

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                

class CatalogSearchViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = StockSerializer

    def get_queryset(self):
        q = self.request.GET.get('search',None)
        if q:
            queryset = Stock.objects.filter(item_isactive=True).order_by('pk')
            queryset = queryset.filter(Q(item_name__icontains=q) | Q(item_desc__icontains=q))
        else:
            queryset = Stock.objects.none()
        return queryset
                        
    def list(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                           

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                

class CatalogFavoritesViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
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
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                            

    def get_object(self, pk):
        try:
            return Stock.objects.get(pk=pk, item_isactive=True)
        except Stock.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            stock = self.get_object(pk)
            serializer = StockSerializer(stock)
            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 'data': serializer.data}
            v = result.get('data')
            if v['Stock_PIC']:
                v['Stock_PIC'] = str("http://"+request.META['HTTP_HOST']) + str(v['Stock_PIC'])
            if v['item_price']:
                v['item_price'] = "{:.2f}".format(float(v['item_price']))
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                


class SalonProductSearchViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
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
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                       

class ForgotPswdRequestOtpAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OtpRequestSerializer

    def post(self, request):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                


class ForgotPswdOtpValidationAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = OtpValidationSerializer

    def post(self, request):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


class ResetPasswordAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


# class UpdateStockAPIView(APIView):
#     authentication_classes = [ExpiringTokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]
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
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]

    def post(self, request, format=None):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    


class CustomerSignatureAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CustomerSignSerializer

    def post(self, request):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

class TopupViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentAccountSerializer

    def list(self, request):
        try:
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
                
            queryset = TreatmentAccount.objects.filter(Cust_Codeid=cust_id, Site_Codeid=site, type='Deposit', outstanding__gt = 0).order_by('pk')
            sum = 0; lst = []
            header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
            "topup_amount" : "0.00","new_outstanding" : "0.00"}
            if queryset:
                for q in queryset:
                    #type__in=('Deposit', 'Top Up')
                    # accids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                    # treatment_parentcode=q.treatment_parentcode,Site_Codeid=site).order_by('id').first()
                    # trmtobj = Treatment.objects.filter(treatment_account__pk=accids.pk,status='Open').order_by('pk').first()

                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=q.sa_transacno,
                    treatment_parentcode=q.treatment_parentcode,Site_Codeid=site).order_by('id').last()
                    acc = TreatmentAccount.objects.filter(pk=acc_ids.pk)
                    serializer = self.get_serializer(acc, many=True)

                    if acc_ids.outstanding > 0.0:
                        for data in serializer.data:
                            pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                            sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                            sum += data['outstanding']
                            if pos_haud:
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
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False,'header_data':header_data,  'data': []}
                    return Response(result, status=status.HTTP_200_OK)        
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)           

        
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
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentDoneSerializer

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
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
        try:
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

            queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
            status="Open").order_by('pk')

            if request.GET.get('year',None):
                year = request.GET.get('year',None)
                if year != "All":
                    queryset = Treatment.objects.filter(cust_code=cust_obj.cust_code, site_code=site.itemsite_code, 
                    status="Open", treatment_date__year=year).order_by('pk')
                    par_lst = list(set([e.treatment_parentcode for e in queryset if e.treatment_parentcode])) 
                    id_lst = []
                    for p in par_lst:
                        query = Treatment.objects.filter(treatment_parentcode=p, cust_code=cust_obj.cust_code, site_code=site.itemsite_code,
                        status="Open", treatment_date__year=year).order_by('pk').last()
                        id_lst.append(query.pk) 

                    queryset = Treatment.objects.filter(pk__in=id_lst,cust_code=cust_obj.cust_code,site_code=site.itemsite_code, status="Open", treatment_date__year=year).order_by('pk')
        
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []
                for i in serializer.data:
                    splt = str(i['treatment_date']).split('T')
                    trmt_obj = Treatment.objects.filter(pk=i['id']).first()
                    # tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj)
                    tmp_ids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code)
                    
                    for emp in tmp_ids:
                        appt = Appointment.objects.filter(cust_no=trmt_obj.cust_code,appt_date=date.today(),
                        itemsite_code=fmspw[0].loginsite.itemsite_code,emp_no=emp.helper_code) 
                        if not appt:
                            # tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj,helper_code=emp.helper_code,
                            # site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
                            tmpids = TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,helper_code=emp.helper_code,
                            site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                            
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
                    
                    for t in TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code):
                        trmt_obj.helper_ids.add(t)
                    # for t in TmpItemHelper.objects.filter(item_code=trmt_obj.treatment_code,site_code=site.itemsite_code):
                    #     trmt_obj.helper_ids.add(t)

                    # pos_haud = PosHaud.objects.filter(sa_custnoid=cust_id,ItemSite_Codeid__pk=site.pk,
                    # sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()        
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
                    sa_transacno_type__in=('Receipt', 'Non Sales'),sa_transacno=i["sa_transacno"]).first()
                    # if not pos_haud:
                    #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Payment not done yet!!",'error': True} 
                    #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    item_code = str(trmt_obj.item_code)
                    itm_code = item_code[:-4]
                    # print(Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk'),"sss")
                    stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()
                    
                    if pos_haud and stockobj: 
                        acc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
                        site_code=site.itemsite_code).order_by('pk').first()
                        i['treatment_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        # i['TreatmentAccountid'] = trmt_obj.treatment_account.pk
                        i['TreatmentAccountid'] = acc_obj.pk
                        # i['stockid'] = trmt_obj.Item_Codeid.pk
                        i['stockid'] = stockobj.pk if stockobj else ""
                        i["transacno_ref"] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        



class TrmtTmpItemHelperViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
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
        try:
            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.sa_transacno,
            # treatment_parentcode=trmt_obj.treatment_parentcode,Site_Codeid=trmt_obj.Site_Codeid).order_by('id').last()
            acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.sa_transacno,
            treatment_parentcode=trmt_obj.treatment_parentcode,site_code=trmt_obj.site_code).order_by('id').last()

            if acc_ids and acc_ids.balance:  
                if acc_ids.balance < trmt_obj.unit_amount:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Insufficient Amount in Treatment Account. Please Top Up!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            

            # if cart_obj.deposit < cart_obj.discount_price:
            #     msg = "Min Deposit for this treatment is SS {0} ! Treatment Done not allow.".format(str(cart_obj.discount_price))
            #     result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
            #     return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            item_code = str(trmt_obj.item_code)
            itm_code = item_code[:-4]
            stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()

            # if trmt_obj.Item_Codeid.workcommpoints == None or trmt_obj.Item_Codeid.workcommpoints == 0.0:             
            if stockobj.workcommpoints == None or stockobj.workcommpoints == 0.0:
                workcommpoints = 0.0
                # result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Work Point should not be None/zero value!!",'error': True} 
                # return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            else:
                workcommpoints = stockobj.workcommpoints
            
            # stock_obj = Stock.objects.filter(pk=trmt_obj.Item_Codeid.pk,item_isactive=True).first()
            if stockobj.srv_duration is None or stockobj.srv_duration == 0.0:
                srvduration = 60
            else:
                srvduration = stockobj.srv_duration

            stkduration = int(srvduration) + 30
            hrs = '{:02d}:{:02d}'.format(*divmod(stkduration, 60))
                
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
                if h_obj.times:
                    value['times']  = trmt_obj.times
                if h_obj.workcommpoints:
                    sumwp1 = TmpItemHelper.objects.filter(treatment=trmt_obj.pk).aggregate(Sum('wp1'))
                    value['work_point'] = "{:.2f}".format(float(sumwp1['wp1__sum']))       
        
        
            queryset = TmpItemHelper.objects.filter(treatment=trmt_obj).order_by('id')
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    

    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            
            trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist / not in open status!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            item_code = str(trmt_obj.item_code)
            itm_code = item_code[:-4]
            stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()

            # acc_ids = TreatmentAccount.objects.filter(ref_transacno=trmt_obj.treatment_account.ref_transacno,
            # treatment_parentcode=trmt_obj.treatment_account.treatment_parentcode,Site_Codeid=site,).order_by('id').last()
            
            tracc_obj = TreatmentAccount.objects.filter(treatment_parentcode=trmt_obj.treatment_parentcode,
            site_code=site.itemsite_code).order_by('pk').first()

            acc_ids = TreatmentAccount.objects.filter(ref_transacno=tracc_obj.ref_transacno,
            treatment_parentcode=tracc_obj.treatment_parentcode,site_code=site.itemsite_code,).order_by('id').last()

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
            if stockobj.srv_duration is None or float(stockobj.srv_duration) == 0.0:
                stk_duration = 60
            else:
                stk_duration = int(stockobj.srv_duration)

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
                last = h_obj.last()
            
                start_time =  get_in_val(self, last.appt_to_time); endtime = None
                if start_time:
                    starttime = datetime.datetime.strptime(start_time, "%H:%M")

                    end_time = starttime + datetime.timedelta(minutes = stkduration)
                    endtime = datetime.datetime.strptime(str(end_time), "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
                appt_fr_time = starttime if start_time else None
                appt_to_time = endtime if endtime else None
                
            wp1 = float(workcommpoints) / float(count)
        
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                temph = serializer.save(item_name=stockobj.item_desc,helper_id=helper_obj,
                helper_name=helper_obj.display_name,helper_code=helper_obj.emp_code,Room_Codeid=Room_Codeid,
                site_code=site.itemsite_code,times=trmt_obj.times,treatment_no=trmt_obj.treatment_no,
                wp1=wp1,wp2=0.0,wp3=0.0,itemcart=None,treatment=trmt_obj,Source_Codeid=Source_Codeid,
                new_remark=new_remark,appt_fr_time=appt_fr_time,appt_to_time=appt_to_time,
                add_duration=add_duration,workcommpoints=workcommpoints)
                # trmt_obj.helper_ids.add(temph.id) 
                tmp.append(temph.id)

                for h in TmpItemHelper.objects.filter(treatment__pk=trmt_obj.pk,site_code=site.itemsite_code).order_by('pk'):
                    TmpItemHelper.objects.filter(id=h.id).update(wp1=wp1)
            else:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Input",'error': True, 
                'data': serializer.errors}
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
            if tmp != []:
                value = {'Item':stockobj.item_desc,'Price':"{:.2f}".format(float(trmt_obj.unit_amount)),
                'work_point':"{:.2f}".format(float(workcommpoints)),'Room':None,'Source':None,'new_remark':None,
                'times':trmt_obj.times}  
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)    
        

    def get_object(self, pk):
        try:
            return TmpItemHelper.objects.get(pk=pk)
        except TmpItemHelper.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            queryset = TmpItemHelper.objects.filter().order_by('pk')
            tmpitm = get_object_or_404(queryset, pk=pk)
            serializer = TmpItemHelperSerializer(tmpitm)
            result = {'status': status.HTTP_200_OK,"message": "Listed Succesfully",'error': False, 
            'data':  serializer.data}
            return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      

    
    def partial_update(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            if request.GET.get('Room_Codeid',None):
                room_ids = Room.objects.filter(id=request.GET.get('Room_Codeid',None),isactive=True).first()
                if not room_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Room Id does not exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if request.GET.get('Source_Codeid',None):
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
            # appt = Appointment.objects.filter(cust_noid=tmpobj.treatment.Cust_Codeid,appt_date=date.today(),
            # ItemSite_Codeid=site)    
            # if not appt:
            #     if (not 'appt_fr_time' in request.data or str(request.data['appt_fr_time']) is None) and (not 'add_duration' in request.data or str(request.data['add_duration']) is None):
            #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Appointment is not available today so please give appointment details",'error': True} 
            #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            item_code = str(tmpobj.treatment.item_code)
            itm_code = item_code[:-4]
            stockobj = Stock.objects.filter(item_code=itm_code,item_isactive=True).order_by('pk').first()

            serializer = self.get_serializer(tmpobj, data=request.data, partial=True)
            if serializer.is_valid():
                if ('appt_fr_time' in request.data and not request.data['appt_fr_time'] == None):
                    if ('add_duration' in request.data and not request.data['add_duration'] == None):
                        if stockobj.srv_duration is None or float(stockobj.srv_duration) == 0.0:
                            stk_duration = 60
                        else:
                            stk_duration = int(stockobj.srv_duration)

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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      
        

    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def confirm(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            # per = self.check_permissions(self.get_permissions(self))
            # print(per,"per")
            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist/Status Should be in Open only!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None))
            # print(trmt_obj,"trmt_obj")
            if trmt_obj:
                tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj[0],site_code=site.itemsite_code)
                # print(tmp_ids,"tmp_ids")
                if not tmp_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Without employee cant do confirm!!",'error': False}
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
                for emp in tmp_ids:
                    appt = Appointment.objects.filter(cust_no=trmt_obj[0].cust_code,appt_date=date.today(),
                    itemsite_code=fmspw[0].loginsite.itemsite_code,emp_no=emp.helper_code)
                    # print(appt,"appt") 
                    if not appt:
                        tmpids = TmpItemHelper.objects.filter(treatment=trmt_obj[0],
                        helper_code=emp.helper_code,site_code=site.itemsite_code).filter(Q(appt_fr_time__isnull=True) | Q(appt_to_time__isnull=True) | Q(add_duration__isnull=True))
                        if tmpids:
                            amsg = "Appointment is not available today, please give Start Time & Add Duration for employee {0} ".format(emp.helper_name)
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message": amsg,'error': True} 
                            return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                    #need to uncomment later
                    # if emp.appt_fr_time and emp.appt_to_time:         
                    #     appt_ids = Appointment.objects.filter(appt_date=date.today(),emp_no=emp.helper_code,
                    #     itemsite_code=fmspw[0].loginsite.itemsite_code).filter(Q(appt_to_time__gte=emp.appt_fr_time) & Q(appt_fr_time__lte=emp.appt_to_time))
                    #     if appt_ids:
                    #         msg = "In These timing already Appointment is booked for employee {0} so allocate other duration".format(emp.helper_name)
                    #         result = {'status': status.HTTP_400_BAD_REQUEST,"message":msg,'error': True} 
                    #         return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                    
                # print(trmt_obj[0].helper_ids.all(),"trmt_obj[0].helper_ids")
                for existing in trmt_obj[0].helper_ids.all():
                    trmt_obj[0].helper_ids.remove(existing) 
                
                # print(tmp_ids,"111")
                for t in tmp_ids:
                    trmt_obj[0].helper_ids.add(t)
                
                # print(trmt_obj[0].helper_ids.all(),"222")
            result = {'status': status.HTTP_200_OK , "message": "Confirmed Succesfully", 'error': False}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        

    
    @action(detail=False, methods=['delete'], name='delete', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def delete(self, request): 
        try:  
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite

            if self.request.GET.get('clear_all',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give clear all/line in parms!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
        
            if request.GET.get('treatmentid',None) is None:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Please give Treatment Record ID",'error': False}
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            trmt_obj = Treatment.objects.filter(status="Open",pk=request.GET.get('treatmentid',None)).first()
            if not trmt_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment ID does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
            
            state = status.HTTP_204_NO_CONTENT
            try:
                tmp_ids = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).values_list('id')
                if not tmp_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Tmp Item Helper records is not present for this Treatment record id!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

                if self.request.GET.get('clear_all',None) == "1":
                    queryset = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).order_by('id').delete()
                    
                elif self.request.GET.get('clear_all',None) == "0":
                    queryset = TmpItemHelper.objects.filter(treatment=trmt_obj,site_code=site.itemsite_code).order_by('id').first().delete()
                
                result = {'status': status.HTTP_200_OK , "message": "Deleted Succesfully", 'error': False}
                return Response(result, status=status.HTTP_200_OK) 
        
            except Http404:
                pass

            result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': True}
            return Response(result,status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)       


class TopupproductViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TopupproductSerializer

    def list(self, request):
        try:
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
            sum = 0; lst = []
            header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
            "topup_amount" : "0.00","new_outstanding" : "0.00"}

            if queryset:
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
                            if pos_haud:
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
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': []}
                    return Response(result, status=status.HTTP_200_OK)

            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)           


class TopupprepaidViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class =  TopupprepaidSerializer

    def list(self, request):
        try:
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
        
            queryset = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,sa_transacno_type="Receipt",
            ItemSite_Codeid__pk=site.pk)
            sum = 0; lst = []
            header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "0.00",
            "topup_amount" : "0.00","new_outstanding" : "0.00"}
            if queryset:
                for q in queryset:
                    daud = PosDaud.objects.filter(sa_transacno=q.sa_transacno,
                    ItemSite_Codeid__pk=site.pk)
                    for d in daud:
                        if int(d.dt_itemnoid.item_div) == 3 and d.dt_itemnoid.item_type == 'PACKAGE':
                            acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,package_code=d.dt_combocode,
                            Site_Codeid=d.ItemSite_Codeid,pos_daud_lineno=d.dt_lineno,outstanding__gt = 0).order_by('id').last()
                        else:
                            acc_ids = PrepaidAccount.objects.filter(pp_no=d.sa_transacno,Item_Codeid=d.dt_itemnoid,
                            Site_Codeid=d.ItemSite_Codeid,pos_daud_lineno=d.dt_lineno,outstanding__gt = 0).order_by('id').last()
                            
                        if acc_ids:
                            acc = PrepaidAccount.objects.filter(pk=acc_ids.pk)
                            serializer = self.get_serializer(acc, many=True)
                    
                            for data in serializer.data:
                                pos_haud = PosHaud.objects.filter(sa_custnoid=cust_obj,ItemSite_Codeid__pk=site.pk,
                                sa_transacno_type="Receipt",sa_transacno=q.sa_transacno).first()
                                if pos_haud:
                                    sum += data['outstanding']
                                    splt = str(data['exp_date']).split('T')
                                    if data['exp_date']:
                                        data['exp_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                                    data['transaction_code'] = pos_haud.sa_transacno_ref
                                    data['prepaid_id']  = acc_ids.pk

                                    if int(d.dt_itemnoid.item_div) == 3 and d.dt_itemnoid.item_type == 'PACKAGE':
                                        data['stock_id'] = acc_ids.Item_Codeid.pk
                                    else:
                                        data['stock_id'] = d.dt_itemnoid.pk

                                    data["pay_amount"] = None
                                    if data["remain"]:
                                        data["remain"] = "{:.2f}".format(float(data['remain']))
                                    if data["outstanding"]:
                                        data["outstanding"] = "{:.2f}".format(float(data['outstanding']))
                                    lst.append(data)    

                header_data = {"customer_name" : cust_obj.cust_name,"old_outstanding" : "{:.2f}".format(float(sum)),
                "topup_amount" : None,"new_outstanding" : "{:.2f}".format(float(sum))}
                if lst != []:
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'header_data':header_data, 'data': lst}
                else:
                    result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT,"message":"No Content",'error': False,'header_data':header_data, 'data': []}
                return Response(result, status=status.HTTP_200_OK)    
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)           


class ReversalListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentReversalSerializer

    def list(self, request):
        try:
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
                queryset = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code).order_by('-pk')
                if queryset:
                    # type__in=('Deposit', 'Top Up','CANCEL')
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    treatment_parentcode=queryset[0].treatment_parentcode,Site_Codeid=queryset[0].Site_Codeid).order_by('id').last()
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)      

    def create(self, request):
        try:
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
                    queryset = Treatment.objects.filter(pk=i,status='Open',site_code=site.itemsite_code).order_by('-pk')
                    if not queryset:
                        result = {'status': status.HTTP_200_OK,"message":"Treatment ID does not exist/Not in Open Status!!",'error': True} 
                        return Response(data=result, status=status.HTTP_200_OK) 
                    
                    # type__in=('Deposit', 'Top Up','CANCEL')
                    acc_ids = TreatmentAccount.objects.filter(ref_transacno=queryset[0].sa_transacno,
                    treatment_parentcode=queryset[0].treatment_parentcode,Site_Codeid=queryset[0].Site_Codeid).order_by('id').last()

                    # if acc_ids.balance == 0.0:
                    #     result = {'status': status.HTTP_200_OK,"message":"Treatment Account for this customer is Zero so cant create Credit Note!!",'error': True} 
                    #     return Response(data=result, status=status.HTTP_200_OK) 


                    j = queryset.first()
                    #treatment update
                    j.status = 'Cancel'
                    j.transaction_time = timezone.now()
                    j.save()
                    cust_obj = Customer.objects.filter(cust_code=j.cust_code,cust_isactive=True).first()

                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,itemsite_code=site.itemsite_code,
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
    
                    treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                    description=desc,ref_no=j.treatment_parentcode,type='CANCEL',amount=-float("{:.2f}".format(float(tamount))) if tamount else 0,
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


class ShowBalanceViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ShowBalanceSerializer

    def list(self, request):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     


class ReverseTrmtReasonAPIView(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = ReverseTrmtReason.objects.filter(is_active=True).order_by('id')
    serializer_class = ReverseTrmtReasonSerializer

    def list(self, request):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data':  serializer.data}
            else:
                serializer = self.get_serializer()
                result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 'data': []}
            return Response(data=result, status=status.HTTP_200_OK) 
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     
        

class VoidViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    queryset = PosHaud.objects.filter(isvoid=False).order_by('-pk')
    serializer_class = VoidSerializer

    def get_queryset(self):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        # year = date.today().year
        # month = date.today().month
        from_date = self.request.GET.get('from_date',None)
        to_date = self.request.GET.get('to_date',None)
        transac_no = self.request.GET.get('transac_no',None)
        cust_code = self.request.GET.get('cust_code',None)
        cust_name = self.request.GET.get('cust_name',None)
        queryset = PosHaud.objects.filter(isvoid=False,
        ItemSite_Codeid__pk=site.pk).order_by('-pk')
        if not from_date and not to_date and not transac_no and not cust_code and not cust_name:
            queryset = queryset
        else:
            if from_date and to_date: 
                queryset = queryset.filter(Q(sa_date__date__gte=from_date,sa_date__date__lte=to_date)).order_by('-pk')
               
            if transac_no:
                queryset = queryset.filter(sa_transacno_ref__icontains=transac_no).order_by('-pk')
            if cust_code:
                customer = Customer.objects.filter(pk=cust_code,cust_isactive=True,site_code=site.itemsite_code).last()
                if customer:
                    queryset = queryset.filter(sa_custno__icontains=customer.cust_code).order_by('-pk')
                else:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Logined Site Customer Doesn't Exist!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            if cust_name:
               queryset = queryset.filter(sa_custname__icontains=cust_name).order_by('-pk')
        return queryset

    def list(self, request):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
               

    @action(detail=False, methods=['get'], name='Details', permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def Details(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
            site = fmspw.loginsite
            poshdr_id = self.request.GET.get('poshdr_id',None)
            # if not isinstance(poshdr_id, int):
            #     result = {'status': status.HTTP_200_OK,"message":"Poshaud ID Should be Integer only!!",'error': True} 
            #     return Response(data=result, status=status.HTTP_200_OK)

            haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            ItemSite_Codeid__pk=site.pk).first()
            if haud_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"PosHaud ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            cust_obj = Customer.objects.filter(cust_code=haud_obj.sa_custno,cust_isactive=True,
            site_code=site.itemsite_code).first()

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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                   


    def create(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
        
            poshdr_id = self.request.GET.get('poshdr_id',None)
            # poshdrid = poshdr_id.split(',')
            # for i in poshdrid:
            haud_obj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            ItemSite_Codeid__pk=site.pk).first()
            if haud_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"PosHaud ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)

            gst = GstSetting.objects.filter(item_desc='GST',isactive=True).first()

            # for p in poshdrid:
            haudobj = PosHaud.objects.filter(pk=poshdr_id,isvoid=False,
            ItemSite_Codeid__pk=site.pk).first()
            if haudobj.cart_id:
                ids_cart = ItemCart.objects.filter(isactive=True,cart_id=haudobj.cart_id,
                sitecode=site.itemsite_code,cart_date=date.today(),
                cust_noid__pk=haud_obj.sa_custnoid.pk).exclude(type__in=type_tx)
                if ids_cart:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Already Cart is Created!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                else:
                    haudobj.cart_id = None
                    haudobj.save()
                    ids_cartold = ItemCart.objects.filter(cart_id=haudobj.cart_id,cart_status="Inprogress",
                    sitecode=site.itemsite_code,cust_noid__pk=haud_obj.sa_custnoid.pk).exclude(type__in=type_tx).delete()

            daud_ids = PosDaud.objects.filter(sa_transacno=haudobj.sa_transacno,
            ItemSite_Codeid__pk=site.pk) 
            lineno = 0
            control_obj = ControlNo.objects.filter(control_description__iexact="ITEM CART",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
            if not control_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Item Cart Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
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
                

            haudobj.cart_id = cart_id
            haudobj.save()
            
            cart_lst = []
            for d in daud_ids:
                if d.itemcart:
                    lineno += 1
                    if lineno == 1:
                        check = "New"
                    else:
                        check = "Old"

                    cust_obj = Customer.objects.filter(pk=d.itemcart.cust_noid.pk,cust_isactive=True).first()
                    stock_obj = Stock.objects.filter(pk=d.itemcart.itemcodeid.pk,item_isactive=True).first()
                    
                    tax_value = 0.0
                    if stock_obj.is_have_tax == True:
                        tax_value = gst.ITEM_VALUE
                    
                    if d.itemcart.type == "Deposit":
                        type = "VT-Deposit"
                    elif d.itemcart.type == "Top Up":
                        type = "VT-Top Up" 
                    elif d.itemcart.type == "Sales":
                        type = "VT-Sales"
                    else:
                        type = d.itemcart.type            

                    cart = ItemCart(cart_date=date.today(),phonenumber=cust_obj.cust_phone2,
                    customercode=cust_obj.cust_code,cust_noid=cust_obj,lineno=lineno,
                    itemcodeid=stock_obj,itemcode=stock_obj.item_code,itemdesc=stock_obj.item_desc,
                    quantity=d.itemcart.quantity,price="{:.2f}".format(float(d.itemcart.price)),
                    sitecodeid=d.itemcart.sitecodeid,sitecode=d.itemcart.sitecodeid.itemsite_code,
                    cart_status="Inprogress",cart_id=cart_id,item_uom=d.itemcart.item_uom,
                    tax="{:.2f}".format(tax_value),check=check,ratio=d.itemcart.ratio,
                    discount=d.itemcart.discount,discount_amt=d.itemcart.discount_amt,
                    additional_discount=d.itemcart.additional_discount,
                    additional_discountamt=d.itemcart.additional_discountamt,
                    discount_price=d.itemcart.discount_price,total_price=d.itemcart.total_price,
                    trans_amt=d.itemcart.trans_amt,deposit=d.itemcart.deposit,type=type,
                    itemstatus=d.itemcart.itemstatus,remark=d.itemcart.remark,
                    discreason_txt=d.itemcart.discreason_txt,focreason=d.itemcart.focreason,
                    holditemqty=d.itemcart.holditemqty,holdreason=d.itemcart.holdreason,
                    done_sessions=d.itemcart.done_sessions,treatment_account=d.itemcart.treatment_account,
                    treatment=d.itemcart.treatment,deposit_account=d.itemcart.deposit_account,
                    prepaid_account=d.itemcart.prepaid_account)
                    cart.save()

                    for s in d.itemcart.sales_staff.all(): 
                        cart.sales_staff.add(s)

                    for se in d.itemcart.service_staff.all(): 
                        cart.service_staff.add(se)

                    for h in d.itemcart.helper_ids.all(): 
                        cart.helper_ids.add(h)    
                    
                    for dis in d.itemcart.disc_reason.all(): 
                        cart.disc_reason.add(dis)
                    
                    for po in d.itemcart.pos_disc.all(): 
                        cart.pos_disc.add(po)

                    if cart.pk:
                        if cart.pk not in cart_lst:
                            cart_lst.append(cart.pk)
    
            if cart_lst != [] and len(cart_lst) == len(daud_ids):
                result = {'status': status.HTTP_200_OK, "message": "Created Successfully", 'error': False,'data':cart_id}
                return Response(data=result, status=status.HTTP_200_OK)
                
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
                     
    

    @action(methods=['post'], detail=False, permission_classes=[IsAuthenticated & authenticated_only],
    authentication_classes=[ExpiringTokenAuthentication])
    def VoidReturn(self, request):
        try:
            global type_tx
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
            site = fmspw[0].loginsite
            cart_date = timezone.now().date()

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
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 

            haudre = PosHaud.objects.filter(ItemSite_Codeid__pk=site.pk).order_by('sa_transacno')
            final = list(set([r.sa_transacno for r in haudre]))
            # print(final,len(final),"final")
            saprefix = control_obj.control_prefix
            code_site = site.itemsite_code

            lst = []
            if final != []:
                for f in final:
                    newstr = f.replace(saprefix,"")
                    new_str = newstr.replace(code_site, "")
                    lst.append(new_str)
                    lst.sort(reverse=True)

                # print(lst,"lst")
                sa_no = int(lst[0]) + 1
                sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(sa_no)
            else:
                sa_transacno = str(control_obj.control_prefix)+str(control_obj.Site_Codeid.itemsite_code)+str(control_obj.control_no)
            
            refcontrol_obj = ControlNo.objects.filter(control_description__iexact="Reference VOID No",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
            if not refcontrol_obj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Reference VOID Control No does not exist!!",'error': True} 
                return Response(result, status=status.HTTP_400_BAD_REQUEST) 
            
            sa_transacno_ref = str(refcontrol_obj.control_prefix)+str(refcontrol_obj.Site_Codeid.itemsite_code)+str(refcontrol_obj.control_no)
            
            poshaud_ids = PosHaud.objects.filter(sa_transacno=sa_transacno,sa_custno=haudobj.sa_custno,
            ItemSite_Codeid__pk=site.pk,sa_transacno_ref=sa_transacno_ref)
            if poshaud_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Void sa transacno Already Created!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            pos_haud_ids = PosHaud.objects.filter(sa_transacno=sa_transacno,sa_custno=haudobj.sa_custno,
            ItemSite_Codeid__pk=site.pk)
            if pos_haud_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosHaud Void sa transacno Already Created!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)

            cartnew_ids = ItemCart.objects.filter(isactive=True,cart_date=cart_date,
            cart_id=cart_id,cart_status="Completed",is_payment=True,sitecodeid__pk=site.pk,
            customercode=cartobj_ids[0].customercode).exclude(type__in=type_tx)
            if cartnew_ids:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Invalid Cart ID,Send correct Cart Id,Given Cart ID Payment done for this Customer!!",'error': True} 
                return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
     
            for ctl in cartnew_ids:
                #,itemcart__pk=ctl.pk
                pos_daud_ids = PosDaud.objects.filter(sa_transacno=sa_transacno,dt_itemnoid__pk=ctl.itemcodeid.pk,
                ItemSite_Codeid__pk=site.pk,dt_lineno=ctl.lineno)
                if pos_daud_ids:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosDaud Void Already Created!!",'error': True} 
                    return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                  
            
            voidreason_id = self.request.GET.get('voidreason_id',None)
            void_obj = VoidReason.objects.filter(pk=voidreason_id,isactive=True)
            if void_obj is None:
                result = {'status': status.HTTP_200_OK,"message":"VoidReason ID Does not exist!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)
            
            finalsatrasc  = False
            if haudobj.sa_transacno_type in ['Receipt','Non Sales']:
                for t in taud_ids:
                    ids_taud = PosTaud.objects.filter(sa_transacno=sa_transacno,dt_lineno=t.dt_lineno,
                    ItemSIte_Codeid__pk=site.pk)
                    # print(ids_taud,"ids_taud")
                    if ids_taud:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"PosTaud Void Already Created!!",'error': True} 
                        return Response(data=result, status=status.HTTP_400_BAD_REQUEST)
                            
                            
                    taud = PosTaud(sa_transacno=sa_transacno,pay_groupid=t.pay_groupid,pay_group=t.pay_group,
                    pay_typeid=t.pay_typeid,pay_type=t.pay_type,pay_desc=t.pay_desc,pay_tendamt=t.pay_tendamt,
                    pay_tendrate=t.pay_tendrate,pay_tendcurr=t.pay_tendcurr,pay_amt=-t.pay_amt,pay_amtrate=t.pay_amtrate,
                    pay_amtcurr=t.pay_amtcurr,pay_rem1=t.pay_rem1,pay_rem2=t.pay_rem2,pay_rem3=t.pay_rem3,pay_rem4=t.pay_rem4,
                    pay_status=t.pay_status,pay_actamt=-t.pay_actamt,ItemSIte_Codeid=t.ItemSIte_Codeid,
                    itemsite_code=t.itemsite_code,paychange=t.paychange,dt_lineno=t.dt_lineno,
                    pay_gst_amt_collect=-t.pay_gst_amt_collect,pay_gst=-t.pay_gst,posdaudlineno=t.posdaudlineno,
                    posdaudlineamountassign=t.posdaudlineamountassign,posdaudlineamountused=t.posdaudlineamountused,
                    voucher_name=t.voucher_name,billed_by=t.billed_by,subtotal=-t.subtotal,tax=-t.tax,
                    discount_amt=-t.discount_amt,billable_amount=-t.billable_amount,credit_debit=t.credit_debit,
                    points=t.points,prepaid=t.prepaid,pay_premise=t.pay_premise,is_voucher=t.is_voucher,
                    voucher_no=t.voucher_no,voucher_amt=t.voucher_amt)
                    taud.save()

                for m in multi_ids:
                    multi =  Multistaff(sa_transacno=sa_transacno,item_code=m.item_code,emp_code=m.emp_code,
                    ratio=m.ratio,salesamt=-float("{:.2f}".format(float(m.salesamt))) if m.salesamt else 0,type=m.type,isdelete=m.isdelete,role=m.role,dt_lineno=m.dt_lineno,
                    level_group_code=m.level_group_code) 
                    multi.save()
                
                for d in daud_ids:
                
                    cart_obj = ItemCart.objects.filter(isactive=True,cart_id=cart_id,lineno=d.dt_lineno,
                    sitecode=site.itemsite_code,cart_date=date.today(),cart_status="Inprogress",
                    cust_noid=haudobj.sa_custnoid).exclude(type__in=type_tx).first()
                    
                    topup_outstanding = d.topup_outstanding
                    if d.itemcart.type == 'Top Up':
                        topup_outstanding = d.topup_outstanding + d.dt_price

                    sales = "";service = ""
                    if cart_obj.sales_staff.all():
                        for i in cart_obj.sales_staff.all():
                            if sales == "":
                                sales = sales + i.display_name
                            elif not sales == "":
                                sales = sales +","+ i.display_name
                    if cart_obj.service_staff.all(): 
                        for s in cart_obj.service_staff.all():
                            if service == "":
                                service = service + s.display_name
                            elif not service == "":
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


                    if int(d.itemcart.itemcodeid.item_div) == 3:
                        if d.itemcart.type == 'Deposit':
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
                            
                        elif d.itemcart.type == 'Top Up':
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
                        
                        elif d.itemcart.type == 'Sales':
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

                    elif int(d.itemcart.itemcodeid.item_div) == 1:
                        if d.itemcart.type == 'Deposit':
                        
                            dacc_ids = DepositAccount.objects.filter(sa_transacno=haudobj.sa_transacno,sa_status='SA',type='Deposit',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                
                            for depo in dacc_ids:
                                tpcontrolobj = ControlNo.objects.filter(control_description__iexact="TopUp",Site_Codeid__pk=fmspw[0].loginsite.pk).first()
                                if not tpcontrolobj:
                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"TopUp Control No does not exist!!",'error': True} 
                                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

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

                            #ItemBatch
                            batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                            item_code=d.dt_itemnoid.item_code,uom=d.dt_uom).order_by('pk').last()
                            if batch_ids:
                                addamt = batch_ids.qty + d.dt_qty
                                batch_ids.qty = addamt
                                batch_ids.save()

                            #Stktrn
                            stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                            itemcode=d.dt_itemno,item_uom=d.dt_uom,trn_docno=haudobj.sa_transacno,
                            line_no=d.dt_lineno).last() 
                            currenttime = timezone.now()
                            post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                            amt_add = stktrn_ids.trn_balqty - stktrn_ids.trn_qty
                            if stktrn_ids:
                                stktrn_id = Stktrn(trn_no=stktrn_ids.trn_no,post_time=post_time,aperiod=stktrn_ids.aperiod,
                                itemcode=stktrn_ids.itemcode,store_no=site.itemsite_code,
                                tstore_no=stktrn_ids.tstore_no,fstore_no=stktrn_ids.fstore_no,trn_docno=sa_transacno,
                                trn_type="VT",trn_db_qty=stktrn_ids.trn_db_qty,trn_cr_qty=stktrn_ids.trn_cr_qty,
                                trn_qty=-stktrn_ids.trn_qty,trn_balqty=amt_add,trn_balcst=stktrn_ids.trn_balcst,
                                trn_amt=stktrn_ids.trn_amt,trn_cost=stktrn_ids.trn_cost,trn_ref=stktrn_ids.trn_ref,
                                hq_update=stktrn_ids.hq_update,line_no=stktrn_ids.line_no,item_uom=stktrn_ids.item_uom,
                                item_batch=stktrn_ids.item_batch,mov_type=stktrn_ids.mov_type,item_batch_cost=stktrn_ids.item_batch_cost,
                                stock_in=stktrn_ids.stock_in,trans_package_line_no=stktrn_ids.trans_package_line_no).save()
                        
                        elif d.itemcart.type == 'Top Up':
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


                    elif int(d.itemcart.itemcodeid.item_div) == 5:
                        if d.itemcart.type == 'Deposit':
                            pacc_ids = PrepaidAccount.objects.filter(pp_no=haudobj.sa_transacno,sa_status='DEPOSIT',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)

                            for pa in pacc_ids:
                                PrepaidAccount.objects.filter(pk=pa.pk).update(remain=0.0,status=False,sa_status="VT",updated_at=timezone.now(),
                                cust_code=haudobj.sa_custno,site_code=site.itemsite_code)

                        elif d.itemcart.type == 'Top Up':
                            ptacc_ids = PrepaidAccount.objects.filter(topup_no=haudobj.sa_transacno,sa_status='TOPUP',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                            
                            for pt in ptacc_ids:
                                PrepaidAccount.objects.filter(pk=pt.pk).update(status=False,updated_at=timezone.now())

                                remain = pt.remain - pt.topup_amt
                                outstanding = pt.outstanding + pt.topup_amt
                                PrepaidAccount(pp_no=pt.pp_no,pp_type=pt.pp_type,pp_desc=pt.pp_desc,exp_date=pt.exp_date,
                                cust_code=pt.cust_code,cust_name=pt.cust_name,pp_amt=pt.pp_amt,pp_bonus=pt.pp_bonus,
                                pp_total=pt.pp_total,transac_no=pt.transac_no,item_no=pt.item_no,use_amt=pt.use_amt,
                                remain=remain,ref1=pt.ref1,ref2=pt.ref2,status=True,site_code=pt.site_code,
                                sa_status='TOPUP',exp_status=pt.exp_status,voucher_no=pt.voucher_no,isvoucher=pt.isvoucher,
                                has_deposit=pt.has_deposit,topup_amt=-pt.topup_amt,outstanding=outstanding,
                                active_deposit_bonus=pt.active_deposit_bonus,topup_no=sa_transacno,topup_date=pt.topup_date,
                                line_no=pt.line_no,staff_name=pt.staff_name,staff_no=pt.staff_no,pp_type2=pt.pp_type2,
                                condition_type1=pt.condition_type1,pos_daud_lineno=pt.pos_daud_lineno,mac_uid_ref=pt.mac_uid_ref,
                                lpackage=pt.lpackage,package_code=pt.package_code,package_code_lineno=pt.package_code_lineno,
                                prepaid_disc_type=pt.prepaid_disc_type,prepaid_disc_percent=pt.prepaid_disc_percent,
                                Cust_Codeid=pt.Cust_Codeid,Site_Codeid=pt.Site_Codeid,Item_Codeid=pt.Item_Codeid,
                                item_code=pt.item_code).save()

                    elif int(d.itemcart.itemcodeid.item_div) == 4:
                        if d.itemcart.type == 'Deposit':
                            voucher_ids = VoucherRecord.objects.filter(sa_transacno=haudobj.sa_transacno,
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code).order_by('pk')
                            
                            for vcc in voucher_ids:
                                VoucherRecord.objects.filter(pk=vcc.pk).update(value=-vcc.value,updated_at=timezone.now())
    

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
                                sales = sales + i.display_name
                            elif not sales == "":
                                sales = sales +","+ i.display_name
                    if cart_obj.service_staff.all(): 
                        for s in cart_obj.service_staff.all():
                            if service == "":
                                service = service + s.display_name
                            elif not service == "":
                                service = service +","+ s.display_name 

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

                    if int(da.itemcart.itemcodeid.item_div) == 3:
                        if da.itemcart.type == 'Sales':
                            sacc_ids = TreatmentAccount.objects.filter(sa_transacno=haudobj.sa_transacno,type='Sales',
                            cust_code=haudobj.sa_custno,site_code=site.itemsite_code)
                        
                            description = da.itemcart.itemcodeid.item_name+" "+"(Void Transaction by {0})".format(fmspw[0].pw_userlogin)
                            
                            Treatment.objects.filter(pk=da.itemcart.treatment.pk).update(course=description,status="Open",
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
                                description=description,ref_no=sa.ref_no,type=sa.type,amount="{:.2f}".format(float(da.itemcart.treatment.unit_amount)),
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)


def sa_transacno_update_void(self, site, fmspw):
    sacontrol_obj = ControlNo.objects.filter(control_description__iexact="Transaction number",Site_Codeid__pk=fmspw.loginsite.pk).first()
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


class VoidCheck(generics.ListAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = VoidListSerializer

    def list(self, request):
        try:
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
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 

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

                            savalue = sa_transacno_update_void(self, site, fmspw) 

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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)

class VoidCancel(generics.CreateAPIView):
    authentication_classes = [ExpiringTokenAuthentication]
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
    authentication_classes = [ExpiringTokenAuthentication]
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
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = TreatmentAccSerializer

    def list(self, request):
        try:
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
                    queryset = TreatmentAccount.objects.filter(site_code=fmspw.loginsite.itemsite_code,cust_code=cust_obj.cust_code,sa_date__year=year,type='Deposit').only('site_code','cust_code','sa_date','type').order_by('pk')
                else:
                    queryset = TreatmentAccount.objects.filter(site_code=fmspw.loginsite.itemsite_code,cust_code=cust_obj.cust_code,type='Deposit').only('site_code','cust_code','type').order_by('pk')
            else:
                result = {'status': status.HTTP_200_OK,"message":"Please give year!!",'error': True} 
                return Response(data=result, status=status.HTTP_200_OK)  
         
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []; id_lst = []; balance = 0; outstanding = 0
                for data in serializer.data:
                    trobj = TreatmentAccount.objects.filter(pk=data["id"]).first()
                    # trmids = Treatment.objects.filter(treatment_account__pk=trobj.pk,site_code=site.itemsite_code).only('treatment_account').first()
                    trmids = Treatment.objects.filter(treatment_parentcode=trobj.treatment_parentcode,
                    site_code=site.itemsite_code).only('treatment_parentcode').first()

                    # print(data,"data")
                    if data["id"] not in id_lst:
                        id_lst.append(data["id"])
                    
                    # pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    # sa_transacno=trobj.sa_transacno,sa_transacno_type='Receipt',
                    # itemsite_code=fmspw.loginsite.itemsite_code).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
                    # sa_transacno_type__in=['Receipt','NON SALES']

                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno=trobj.sa_transacno,itemsite_code=fmspw.loginsite.itemsite_code
                    ).only('sa_custno','sa_transacno').order_by('pk').first()
                    
                    if pos_haud:
                        data['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                        if pos_haud.sa_date:
                            splt = str(pos_haud.sa_date).split(" ")
                            data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        
                        data['description'] = ""
                        if trmids:
                            if trmids.course:
                                data['description'] = trmids.course 
                                
                        sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                        treatment_parentcode=data["treatment_parentcode"],site_code=trobj.site_code,
                        type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('balance'))
                        if sumacc_ids:
                            data["payment"] = "{:.2f}".format(float(sumacc_ids['balance__sum']))
                        else:
                            data["payment"] = "0.00"

                        acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
                        treatment_parentcode=data["treatment_parentcode"],site_code=trobj.site_code
                        ).only('ref_transacno','treatment_parentcode','site_code').last()
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
                    'header_data':header_data, 'data': lst}
                    return Response(data=result, status=status.HTTP_200_OK)
                else:
                    result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                    return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         

    def get_object(self, pk):
        try:
            return TreatmentAccount.objects.get(pk=pk)
        except TreatmentAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            account = self.get_object(pk)
            queryset = TreatmentAccount.objects.filter(ref_transacno=account.sa_transacno,
            treatment_parentcode=account.treatment_parentcode,site_code=account.site_code
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

                result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False,
                'header_data':{'credit_balance':last.balance if last.balance else "0.00",
                'outstanding_balance':last.outstanding if last.outstanding else "0.00"}, 
                'data': serializer.data}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         


class CreditNoteListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = CreditNoteSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)
            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)
            site = fmspw[0].loginsite
            
            is_all = self.request.GET.get('is_all', None)
            if is_all:
                queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code).only('cust_code').order_by('pk')
            else:
                queryset = CreditNote.objects.filter(cust_code=cust_obj.cust_code, status='OPEN',site_code=site.itemsite_code).only('cust_code','status').order_by('pk')

            
            
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []
                for data in serializer.data:
                    if data['sa_date']:
                        splt = str(data['sa_date']).split('T')
                        data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d/%m/%Y")

                    crdobj = CreditNote.objects.filter(pk=data["id"]).first()
                    # sa_transacno_type='Receipt',
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code, sa_transacno=crdobj.sa_transacno,
                    itemsite_code=site.itemsite_code).order_by('pk').first()
                    if pos_haud:
                        data['transaction'] = pos_haud.sa_transacno_ref
                    else:
                        data['transaction'] = "" 
                            
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def get_object(self, pk):
        try:
            return CreditNote.objects.get(pk=pk)
        except CreditNote.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            creditnote = self.get_object(pk)
            serializer = CreditNoteAdjustSerializer(creditnote,context={'request': self.request})
            adjustamt = 0.00
            val =  serializer.data
            data = {'id': val['id'],'credit_code': val['credit_code'],'balance': val['balance'],
            'new_balance': val['new_balance'],'refund_amt': val['refund_amt'],
            'adjust_amount':"{:.2f}".format(float(adjustamt))}

            result = {'status': status.HTTP_200_OK , "message": "Listed Succesfully", 'error': False, 
            'data': data}
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)     

    def partial_update(self, request, pk=None):
        try:
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
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        
        


class ProductAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = ProductAccSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            site = fmspw.loginsite

            queryset = DepositAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
            type='Deposit').only('site_code','cust_code','type').order_by('pk')
            
            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []; id_lst = []; balance = 0; outstanding = 0; hold_qty = 0
                for data in serializer.data:
                    depobj = DepositAccount.objects.filter(pk=data["id"]).only('pk').first()
                    if data["id"]:
                        id_lst.append(data["id"])
                    
                    # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk,
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno=depobj.sa_transacno,itemsite_code=site.itemsite_code,
                    ).only('sa_custno','sa_transacno','itemsite_code').order_by('pk').first()
                    if pos_haud:
                        data['transaction'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""
                        if pos_haud.sa_date:
                            splt = str(pos_haud.sa_date).split(" ")
                            data['sa_date'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        
                        if not data['package_code']:
                            data['package_code'] = ""

                        acc_ids = DepositAccount.objects.filter(sa_transacno=depobj.sa_transacno,
                        site_code=depobj.site_code,ref_productcode=depobj.ref_productcode
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

                        holdids = Holditemdetail.objects.filter(sa_transacno=depobj.sa_transacno,
                        itemno=depobj.item_barcode,itemsite_code=site.itemsite_code,
                        sa_custno=cust_obj.cust_code).only('sa_transacno','itemno').last()  
                        if holdids:
                            data['item_status'] = holdids.status if holdids.status else ""
                            hold_qty += holdids.holditemqty
                            data["hold_qty"] = holdids.holditemqty  
                            data['hold_id']  =  holdids.pk                
                        else:
                            data['item_status'] = ""
                            data["hold_qty"] = ""
                            data['hold_id']  = ""              

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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         
            
    
    def get_object(self, pk):
        try:
            return DepositAccount.objects.get(pk=pk)
        except DepositAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
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
                "totalholdqty" : hold_qty}, 
                'data': serializer.data}
                return Response(result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         


class PrepaidAccListViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = PrepaidAccSerializer

    def list(self, request):
        try:
            cust_id = self.request.GET.get('cust_id', None)
            cust_obj = Customer.objects.filter(pk=request.GET.get('cust_id', None),cust_isactive=True).only('pk','cust_isactive').first()
            if cust_obj is None:
                result = {'status': status.HTTP_200_OK, "message": "Customer ID does not exist!!", 'error': True}
                return Response(data=result, status=status.HTTP_200_OK)

            fmspw = Fmspw.objects.filter(user=self.request.user, pw_isactive=True)[0]
            site = fmspw.loginsite

            is_all = self.request.GET.get('is_all',None)
            if is_all:
                queryset = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
                sa_status__in=['DEPOSIT','SA']).only('site_code','cust_code','sa_status').order_by('pk')
            else:
                queryset = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
                sa_status__in=['DEPOSIT','SA'],remain__gt=0).only('site_code','cust_code','sa_status').order_by('pk')

            if queryset:
                serializer = self.get_serializer(queryset, many=True)
                lst = []; id_lst = []; product_type = 0; service_type = 0; all_type = 0
                for data in serializer.data:
                    data.pop('voucher_no'); data.pop('condition_type1')
                    preobj = PrepaidAccount.objects.filter(pk=data["id"]).only('pk').first()
                    if data["id"]:
                        id_lst.append(data["id"])
                    
                    # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk
                    pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
                    sa_transacno=preobj.pp_no,itemsite_code=site.itemsite_code,
                    ).only('sa_custno','sa_transacno','sa_transacno_type','itemsite_code').order_by('pk').first()
                    if pos_haud:
                        data['prepaid'] = pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else ""

                        last_acc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                        site_code=preobj.site_code,status=True,line_no=preobj.line_no).only('pp_no','site_code','status','line_no').last()
                        l_splt = str(data['last_update']).split("T")
                        data['last_update'] = datetime.datetime.strptime(str(l_splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")

                        if last_acc_ids:
                            if last_acc_ids.sa_date:
                                splt = str(last_acc_ids.sa_date).split(" ")
                                data['last_update'] = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        
                        oriacc_ids = PrepaidAccount.objects.filter(pp_no=preobj.pp_no,
                        site_code=preobj.site_code,sa_status__in=['DEPOSIT','SA'],line_no=preobj.line_no).only('pp_no','site_code','sa_status','line_no').first()
                        if oriacc_ids.sa_date: #purchase date
                            #purchase date
                            splt_st = str(oriacc_ids.sa_date).split(" ")
                            data['sa_date'] = datetime.datetime.strptime(str(splt_st[0]), "%Y-%m-%d").strftime("%d-%m-%Y")
                        
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
                        data["product"] = 0.00;data["service"] = 0.00;data["all"] = 0.00
                        if open_ids.conditiontype1 == "Product Only":
                            data["product"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                            product_type += last_acc_ids.pp_amt 
                        elif open_ids.conditiontype1 == "Service Only":
                            data["service"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                            service_type += last_acc_ids.pp_amt
                        elif open_ids.conditiontype1 == "All":
                            data["all"] = "{:.2f}".format(float(last_acc_ids.pp_amt))
                            all_type += last_acc_ids.pp_amt
        
                        lst.append(data)

                if lst != []:
                    header_data = {"balance_producttype" : "{:.2f}".format(float(product_type)), 
                    "balance_servicetype" : "{:.2f}".format(float(service_type)),
                    "balance_alltype" : "{:.2f}".format(float(all_type)),"totalprepaid_count" : len(id_lst)}
                    result = {'status': status.HTTP_200_OK,"message":"Listed Succesfully",'error': False, 
                    'header_data':header_data, 'data': lst}
                    return Response(data=result, status=status.HTTP_200_OK)
                else:
                    result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                    return Response(data=result, status=status.HTTP_200_OK)
            else:
                result = {'status': status.HTTP_204_NO_CONTENT, 'message': "No Content", 'error': False, 'data': []}
                return Response(data=result, status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         
            
    def get_object(self, pk):
        try:
            return PrepaidAccount.objects.get(pk=pk)
        except PrepaidAccount.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first() 
            site = fmspw.loginsite
            account = self.get_object(pk)
            queryset = PrepaidAccount.objects.filter(pp_no=account.pp_no,line_no=account.line_no,
            site_code=account.site_code).only('pp_no','line_no').order_by('pk')
            if queryset:
                last = queryset.last()
                serializer = PrepaidacSerializer(queryset, many=True)
                # sa_transacno_type='Receipt',ItemSite_Codeid__pk=site.pk
                pos_haud = PosHaud.objects.filter(sa_custno=account.cust_code,
                sa_transacno=account.pp_no,itemsite_code=site.itemsite_code,
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

                depoamt_acc_ids = PrepaidAccount.objects.filter(pp_no=account.pp_no,
                site_code=account.site_code,line_no=account.line_no,sa_status__in=('DEPOSIT', 'TOPUP','SA')).only('pp_no','site_code','line_no','sa_status').aggregate(Sum('topup_amt'))
                        
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)         


class ComboViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
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
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [IsAuthenticated & authenticated_only]
    serializer_class = DashboardSerializer

    def get(self, request):
        try:
            fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)[0]
            site = ItemSitelist.objects.filter(pk=fmspw.loginsite.pk)
            serializer = DashboardSerializer(site, many=True)
            data = serializer.data[0]
            result = {'status': status.HTTP_200_OK,"message":"Listed Successful",'error': False,
            'data': data} 
            return Response(result,status=status.HTTP_200_OK)
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
     
class BillingViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
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


class CreditNotePayAPIView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
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
    authentication_classes = [ExpiringTokenAuthentication]
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
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)
    
    def get_object(self, pk):
        try:
            return PrepaidAccount.objects.get(pk=pk)
        except PrepaidAccount.DoesNotExist:
            raise Http404

    def partial_update(self, request, pk=None):
        try:
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
        except Exception as e:
            invalid_message = str(e)
            return general_error_response(invalid_message)        
                


# class DeleteAPIView(generics.CreateAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]

#     def post(self, request):
#         cart_ids = ItemCart.objects.filter(customercode='HQ100022',price=0)
#         treat_ids = Treatment.objects.filter(cust_code='HQ100022',unit_amount=0)
#         return Response(data="deleted sucessfully", status=status.HTTP_200_OK)         
    

# class ControlAPIView(generics.CreateAPIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated & authenticated_only]

#     def post(self, request):
#         site_ids = ItemSitelist.objects.filter().exclude(itemsite_code='HQ')
#         control_ids = ControlNo.objects.filter(site_code='HQ')
#         for s in site_ids:
#             for c in control_ids:
#                 ControlNo(control_no=c.control_no,control_prefix=c.control_prefix,
#                 control_description=c.control_description,controldate=c.controldate,
#                 Site_Codeid=s,site_code=s.itemsite_code,mac_code=c.mac_code).save()

#         return Response(data="Created Sucessfully", status=status.HTTP_200_OK)         

# @register.filter
# def get_item(dictionary, key):
#     return dictionary.get(key)           

class HolditemdetailViewset(viewsets.ModelViewSet):
    authentication_classes = [ExpiringTokenAuthentication]
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
    authentication_classes=[ExpiringTokenAuthentication])
    def issued(self, request):  
        try:
            if request.data:
                fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
                site = fmspw[0].loginsite 
                
                for idx, reqt in enumerate(request.data, start=1): 
                    hold_obj = Holditemdetail.objects.filter(hi_no=reqt['id']).first()
                    if not hold_obj:
                        raise Exception('Holditemdetail id Does not exist')

                    cust_obj = Customer.objects.filter(cust_code=hold_obj.sa_custno,cust_isactive=True,site_code=site.itemsite_code).first()
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

                    else:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":serializer.errors,'error': True}
                        return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                
                
                if lst != []:
                    # print(lst[0])
                    value = lst[0]['id']
                    # print(value,"value")
                    title = Title.objects.filter(product_license=site.itemsite_code).first()
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
          
                








       

    
    
        
 
       


       
