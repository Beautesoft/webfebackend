from rest_framework import serializers
from .models import (SiteGroup,ItemSitelist,ReverseTrmtReason,VoidReason,TreatmentUsage,UsageMemo,
Treatmentface)
from cl_table.models import (ItemDept, ItemRange, Stock, TreatmentAccount, Treatment,DepositAccount,
PrepaidAccount,PosHaud,PosDaud, Customer, PosTaud,CreditNote,PrepaidAccountCondition,Fmspw,Holditemdetail)
from django.utils import timezone
from django.db.models import Sum
from custom.views import round_calc
from custom.models import ItemCart
from datetime import date, timedelta, datetime
import datetime

class SiteGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteGroup
        fields = ['id','description','is_active','created_at']
        read_only_fields = ('created_at','is_active') 

class CatalogItemDeptSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemDept
        fields = ['id','itm_code','itm_desc','itm_seq']

class ItemRangeSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
   
    class Meta:
        model = ItemRange
        fields = ['id','itm_code','itm_desc']

class StockSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_name','item_desc','Stock_PIC','item_price','item_div']

class StockRetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_name','item_desc','Stock_PIC','onhand_qty','item_div']

class StockIdSerializer(serializers.Serializer): 
    stock_id = serializers.IntegerField(required=True)

class OtpRequestSerializer(serializers.Serializer):
    emp_name = serializers.CharField(required=True)

class OtpValidationSerializer(serializers.Serializer):
    emp_name = serializers.CharField(required=False)
    otp = serializers.CharField(required=True)

class ResetPasswordSerializer(serializers.Serializer):
    emp_name = serializers.CharField(required=False)
    new_password = serializers.CharField(required=True)

class CustomerSignSerializer(serializers.Serializer):
    customersign = serializers.CharField()

class TreatmentAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentAccount
        fields = ['id','sa_date','sa_transacno','treatment_parentcode','description','balance','outstanding','sa_staffname']

class TopupSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentAccount
        fields = ['id','sa_date','description','type','amount','balance','outstanding']

class TreatmentDoneSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id','treatment_date','treatment_code','sa_transacno','course','type',
        'expiry','unit_amount','status','times','isfoc','treatment_parentcode','treatment_no']

class TopupproductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositAccount
        fields = ['id','item_description','balance','outstanding','sa_staffname']

class TopupprepaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepaidAccount
        fields = ['id','pp_desc','exp_date','remain','outstanding','staff_name']

class TreatmentReversalSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id','treatment_code','course','unit_amount']

class ShowBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentAccount
        fields = ['id','treatment_parentcode','balance','outstanding']

class ReverseTrmtReasonSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReverseTrmtReason
        fields = ['id','rev_desc']

class VoidSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosHaud
        fields = ['id','sa_transacno_ref','sa_custno','sa_custname','sa_date','sa_status','void_refno','payment_remarks','sa_reason']

class VoidListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PosHaud
        fields = ['cart_id']

class VoidCancelSerializer(serializers.Serializer):

    cart_id = serializers.CharField(required=True)



class PosDaudDetailsSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
    desc = serializers.SerializerMethodField() 

    def get_desc(self, obj):
        if obj:
            desc = str(obj.dt_itemdesc)+" "+"$$"+" "+str("{:.2f}".format(float(obj.dt_promoprice)))
        else:
            desc = None  
        return desc      
    
    class Meta:
        model = PosDaud
        fields = ['id','dt_itemdesc','dt_amt','desc','dt_qty']


class VoidReasonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VoidReason
        fields = ['id','reason_desc']

class TreatmentAccSerializer(serializers.ModelSerializer):

    payment = serializers.FloatField(source='amount',required=False)

    class Meta:
        model = TreatmentAccount
        fields = ['id','sa_date','treatment_parentcode','description','payment','balance','outstanding']
    
    # def to_representation(self, instance):
    #     fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True).first()
    #     site = fmspw.loginsite  
    #     trobj = instance
    #     print(trobj.pk,"trobj") 
    #     cust_obj = Customer.objects.filter(cust_code=trobj.cust_code,cust_isactive=True).only('cust_code','cust_isactive').first()
    #     pos_haud = PosHaud.objects.filter(sa_custno=cust_obj.cust_code,
    #     sa_transacno=trobj.sa_transacno,sa_transacno_type='Receipt',
    #     ItemSite_Codeid__pk=site.pk).only('sa_custno','sa_transacno','sa_transacno_type').order_by('pk').first()
    #     if pos_haud:
    #         sumacc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #         treatment_parentcode=trobj.treatment_parentcode,site_code=trobj.site_code,
    #         type__in=('Deposit', 'Top Up')).only('ref_transacno','treatment_parentcode','site_code','type').order_by('pk').aggregate(Sum('balance'))
            
    #         acc_ids = TreatmentAccount.objects.filter(ref_transacno=trobj.sa_transacno,
    #         treatment_parentcode=trobj.treatment_parentcode,site_code=trobj.site_code).only('ref_transacno','treatment_parentcode','site_code').last()
    #         # if data["balance"]:
    #         # data["balance"] = 
    #         # # if data["outstanding"]:
    #         # data["outstanding"] = 
    #         # outstanding += acc_ids.outstanding
    #         # if data["amount"]:
            
    #         mapped_object = {'id': instance.pk,'sa_date':pos_haud.sa_date if pos_haud.sa_date else None,
    #         'transaction':pos_haud.sa_transacno_ref if pos_haud.sa_transacno_ref else None,
    #         'description': trobj.description,'payment':"{:.2f}".format(float(sumacc_ids['balance__sum'])) if sumacc_ids else 0.0,
    #         'balance': "{:.2f}".format(float(acc_ids.balance)) if acc_ids else 0.0,
    #         'outstanding': "{:.2f}".format(float(acc_ids.outstanding)) if acc_ids else 0.0}
    #         return mapped_object

class CreditNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNote
        fields = ['id','credit_code','sa_date','amount','balance','status']

class CreditNoteAdjustSerializer(serializers.ModelSerializer):
    new_balance = serializers.FloatField(source='balance',required=True)
    refund_amt = serializers.SerializerMethodField()

    class Meta:
        model = CreditNote
        fields = ['id','credit_code','balance','new_balance','refund_amt']
        extra_kwargs = {'refund_amt': {'required': True}}
    
    def get_refund_amt(self, obj):
        return "{:.2f}".format(float(0.00))
    

    def validate(self, data):
        request = self.context['request']
        if not 'new_balance' in request.data:
            raise serializers.ValidationError("new_balance Field is required.")
        else:
            if request.data['new_balance'] is None: 
                raise serializers.ValidationError("new_balance Field is required!!")
        if not 'refund_amt' in request.data:
            raise serializers.ValidationError("refund_amt Field is required.")
        else:
            if request.data['refund_amt'] is None: 
                raise serializers.ValidationError("refund_amt Field is required!!")
        return data      


class ProductAccSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositAccount
        fields = ['id','sa_date','package_code','item_description','balance','outstanding']

class PrepaidAccSerializer(serializers.ModelSerializer):
    last_update = serializers.DateTimeField(source='sa_date',required=False)

    class Meta:
        model = PrepaidAccount
        fields = ['id','pp_desc','last_update','sa_date','exp_date','exp_status',
        'pp_amt','pp_bonus','pp_total','use_amt','remain','voucher_no','topup_amt','outstanding',
        'condition_type1','status','sa_status','cust_code','pp_no','line_no']

class PrepaidacSerializer(serializers.ModelSerializer):

    class Meta:
        model = PrepaidAccount
        fields = ['id','item_no','use_amt','topup_amt']        

class DashboardSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSitelist
        fields = ['id']

    def to_representation(self, instance):
        repeat_cust = [];cust_repeat = 0;pay_amount = 0
        today = timezone.now().date()
        month = today.month
        sitecust_cnt = Customer.objects.filter(site_code=instance.itemsite_code).only('site_code').count()
        sitenewcust_cnt = Customer.objects.filter(site_code=instance.itemsite_code,created_at__date__month=month).only('site_code','created_at').count()
        products_ids = PosDaud.objects.filter(ItemSite_Codeid__pk=instance.pk,created_at__date__month=month,
        dt_itemnoid__item_div=1,record_detail_type='PRODUCT',dt_qty__gt = 0).only('itemsite_code','created_at','dt_itemnoid','record_detail_type','dt_qty').aggregate(Sum('dt_qty'))
        products_cnt = "{:.2f}".format(float(products_ids['dt_qty__sum'])) if products_ids['dt_qty__sum'] else 0   
        service_ids = PosDaud.objects.filter(ItemSite_Codeid__pk=instance.pk,created_at__date__month=month,
        dt_itemnoid__item_div=3,record_detail_type='SERVICE',dt_qty__gt = 0).only('itemsite_code','created_at','dt_itemnoid','record_detail_type','dt_qty').aggregate(Sum('dt_qty'))
        service_cnt = "{:.2f}".format(float(service_ids['dt_qty__sum'])) if service_ids['dt_qty__sum'] else 0
        custids = Customer.objects.filter(site_code=instance.itemsite_code).only('site_code','cust_code').values_list('cust_code', flat=True)
        recustids = PosHaud.objects.filter(ItemSite_Codeid__pk=instance.pk,created_at__date__month=month,
        sa_custno__in=custids).only('itemsite_code','created_at','sa_custno').values_list('sa_custno', flat=True)
       
        recust =list(recustids)
        for c in custids:
            if c in recust:
                cusid = recust.count(c)
                if cusid > 1 and c not in repeat_cust:
                    repeat_cust.append(c)
        
        if repeat_cust !=[]:
            cust_repeat = len(repeat_cust)
       
        # payids = PosTaud.objects.filter(ItemSIte_Codeid__pk=instance.pk,created_at__date__month=month,pay_amt__gt = 0).only('itemsite_code','created_at').aggregate(Sum('pay_amt'))
        payids = PosTaud.objects.filter(ItemSIte_Codeid__pk=instance.pk,created_at__date__month=month).only('itemsite_code','created_at').aggregate(Sum('pay_amt'))
        
        round_val = float(round_calc(payids['pay_amt__sum'])) if payids['pay_amt__sum'] else 0 # round()
        if payids['pay_amt__sum']:
            pay_amount = float(payids['pay_amt__sum']) + round_val 

        mapped_object = {'id': instance.pk,'customer_site':sitecust_cnt,'new_customer':sitenewcust_cnt,
        'product':int(float(products_cnt)),'services':int(float(service_cnt)),'repeat_customer':cust_repeat if cust_repeat else 0,
        'monthly_earnigs':"{:.2f}".format(float(pay_amount)) if pay_amount else "0.00"}
        return mapped_object
        

class BillingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PosHaud
        fields = ['id','sa_custno','sa_custname','sa_date','sa_totamt','sa_transacno_ref','void_refno',
        'sa_staffname','sa_status','sa_transacno','sa_transacno_type','isvoid'] 


    def to_representation(self, instance):
        request = self.context['request']
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        if instance.sa_date:
            splt = str(instance.sa_date).split(" ")
            sa_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

        if instance.isvoid == False:
            void_refno = ""
        else:
            sa_ids = PosHaud.objects.filter(void_refno=instance.sa_transacno,
            ItemSite_Codeid__pk=site.pk,sa_custno=instance.sa_custno).order_by('pk').first()
            if sa_ids:
                void_refno = sa_ids.sa_transacno_ref
            else:
                void_refno = ""
   
        mapped_object = {'id': instance.pk,'sa_custno': instance.sa_custno,'sa_custname': instance.sa_custname, 
        'sa_date': sa_date if sa_date else '','sa_totamt': str("{:.2f}".format(float(instance.sa_totamt))) if instance.sa_totamt else "0.00",
        'void_refno': void_refno if void_refno else "",'sa_staffname': instance.sa_staffname,'sa_status': instance.sa_status,
        'sa_transacno': instance.sa_transacno,'sa_transacno_ref': instance.sa_transacno_ref,'sa_transacno_type':instance.sa_transacno_type,
        'isvoid': instance.isvoid}
       
        return mapped_object


class CreditNotePaySerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditNote
        # fields = ['id','credit_code','sa_date','sa_transacno','amount','balance']
        fields = ['id']

    def to_representation(self, instance):
        if instance.sa_date:
            splt = str(instance.sa_date).split(" ")
            reversal_date = datetime.datetime.strptime(str(splt[0]), "%Y-%m-%d").strftime("%d-%b-%y")

        mapped_object = {'id':instance.pk,'credit_code':instance.credit_code if instance.credit_code else '',
        'reversal_date':reversal_date if reversal_date else '','invoice':instance.sa_transacno if instance.sa_transacno else '',
        'credit': str("{:.2f}".format(float(instance.amount))) if instance.amount else "0.00",
        'balance': str("{:.2f}".format(float(instance.balance))) if instance.balance else "0.00"}
        return mapped_object


class PrepaidPaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrepaidAccount
        # fields = ['id','pp_desc','exp_date','pp_amt,'use_amt','remain']
        fields = ['id','pp_desc','exp_date',]

    def to_representation(self, instance):
        fmspw = Fmspw.objects.filter(user=self.request.user,pw_isactive=True)
        site = fmspw[0].loginsite
        # print(instance.sa_date,"sa_date")
        if instance.exp_date:
            splt_ex = str(instance.exp_date).split(" ")
            exp_date = datetime.datetime.strptime(str(splt_ex[0]), "%Y-%m-%d").strftime("%d-%b-%y")
                        
        open_ids = PrepaidAccountCondition.objects.filter(pp_no=instance.pp_no,
        pos_daud_lineno=instance.line_no).only('pp_no','pos_daud_lineno').first()
        product = 0.00; service = 0.00; allval = 0.00
        if open_ids.conditiontype1 == "Product Only":
            product = "{:.2f}".format(float(instance.remain))
        elif open_ids.conditiontype1 == "Service Only":
            service = "{:.2f}".format(float(instance.remain))
        elif open_ids.conditiontype1 == "All":
            allval = "{:.2f}".format(float(instance.remain))

        pac_ids = PrepaidAccount.objects.filter(pp_no=instance.pp_no,line_no=instance.line_no,
        cust_code=instance.cust_code,site_code=site.itemsite_code).only('pp_no','line_no').order_by('pk').aggregate(Sum('use_amt'))
        accumulate = str("{:.2f}".format(float(pac_ids['use_amt__sum'])))  

        pay_rem1 = str(instance.pp_no)+""+"-"+" "+str(instance.line_no)+" "+"-"+""+str(instance.pp_desc)     

        mapped_object = {'id':instance.pk,'pp_desc':instance.pp_desc if instance.pp_desc else '',
        'exp_date': exp_date if exp_date else '','amount': str("{:.2f}".format(float(instance.pp_total))) if instance.pp_total else "0.00",
        'accumulate': accumulate if accumulate else "0.00",
        'current_use': "0.00",'remain' : str("{:.2f}".format(float(instance.remain))) if instance.remain else "0.00",
        'type': "PREPAID",'remark1': instance.ref1 if instance.ref1 else '','remark2': instance.ref2 if instance.ref2 else '',
        'supplementary':'','product': product if product else "0.00",
        'service': service if service else "0.00",'all': allval if allval else "0.00",
        'item_code': '','pay_rem1':pay_rem1 if pay_rem1 else ''}

        return mapped_object


class CartPrepaidSerializer(serializers.ModelSerializer): 

    class Meta:
        model = ItemCart
        fields = ['id','itemcode']

    def to_representation(self, instance):
        if instance.itemcodeid:
            ctype = False
            if instance.itemcodeid.item_div == '3':
                ctype = "Service"
            elif instance.itemcodeid.item_div == '1':
                ctype = "Product" 

        if instance.itemcodeid:
            description = instance.itemcodeid.item_name if instance.itemcodeid.item_name else ''

        mapped_object = {'id': instance.pk ,'no':instance.lineno if instance.lineno else '',
        'itemcode': instance.itemcode,'type': ctype if ctype else '',
        'description':description if description else '','transac_amount': str("{:.2f}".format(float(instance.deposit))) if instance.deposit else "0.00",
        'use':"0.00",'outstanding':str("{:.2f}".format(float(instance.deposit))) if instance.deposit else "0.00"}
        return mapped_object

class HolditemdetailSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Holditemdetail
        fields = ['id','sa_date','hi_itemdesc','itemno','holditemqty']

class HolditemSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Holditemdetail
        fields = ['id','hi_itemdesc','holditemqty']

class HolditemupdateSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
    issued_qty = serializers.SerializerMethodField()
    emp_id = serializers.SerializerMethodField()


    class Meta:
        model = Holditemdetail
        fields = ['id','issued_qty','emp_id']

class TreatmentHistorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id','treatment_code','course','status','record_status','remarks','type']

class StockUsageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id','treatment_code','course']

class StockUsageProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_desc','item_code','rpt_code','Stock_PIC']


class TreatmentUsageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    link_code = serializers.SerializerMethodField()
    stock_id = serializers.SerializerMethodField()


    def get_link_code(self, obj):
        return None 

    def get_stock_id(self, obj):
        return None    


    class Meta:
        model = TreatmentUsage
        fields = ['id','item_code','link_code','item_desc','qty','uom','stock_id']


class StockUsageMemoSerializer(serializers.ModelSerializer):
    stock_id = serializers.SerializerMethodField()
    emp_id = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()


    def get_stock_id(self, obj):
        return None   

    def get_emp_id(self, obj):
        return None 

    def get_quantity(self, obj):
        return None 

    def get_date(self, obj):
        return None          
     
    class Meta:
        model = UsageMemo
        fields = ['id','item_name','date_out','memo_no','staff_name','uom','qty','memo_remarks','stock_id','emp_id',
        'quantity','date']


class TreatmentfaceSerializer(serializers.ModelSerializer):

    room_id = serializers.SerializerMethodField()
    treat_remarks = serializers.SerializerMethodField()


    def get_room_id(self, obj):
        return None 

    def get_treat_remarks(self, obj):
        return None          
         
    class Meta:
        model = Treatmentface
        fields = ['id','treatment_code','str1','str2','str3','str4','str5','room_id','treat_remarks']
