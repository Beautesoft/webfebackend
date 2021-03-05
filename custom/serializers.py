from rest_framework import serializers
from .models import (EmpLevel, Room, Combo_Services,ItemCart,VoucherRecord, PaymentRemarks, HolditemSetup,
PosPackagedeposit)
from cl_table.models import Treatment, Stock, PackageDtl, ItemClass, ItemRange, Employee
from cl_table.serializers import get_client_ip


class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemClass
        fields = ['id','itm_desc']
        read_only_fields = ('created_at', 'updated_at','itm_isactive') 

class TypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemRange
        fields = ['id','itm_desc']
        read_only_fields = ('created_at', 'updated_at')  
      
class EmpLevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmpLevel
        fields = ['id','level_desc','level_isactive']
        read_only_fields = ('created_at', 'updated_at','level_isactive') 

class RoomSerializer(serializers.ModelSerializer):

    sitecode_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)
    room_img = serializers.SerializerMethodField() 
    
    def get_room_img(self, obj):
        ip = get_client_ip(self.context['request'])
        if obj.Room_PIC:
            pic = str(obj.Room_PIC.url)
        else:
            pic = None    
        return pic

    class Meta:
        model = Room
        fields = ['id','displayname','room_img','Site_Codeid','sitecode_name','isactive']
        read_only_fields = ('created_at','Site_Codeid','sitecode_name', 'updated_at','isactive') 


class ComboServicesSerializer(serializers.ModelSerializer):

    # sitecode_name = serializers.CharField(source='Site_Code.itemsite_desc',required=False)

    class Meta:
        model = Combo_Services
        fields = ['id','Price','discount','services','combo_names']
        # read_only_fields = ('created_at', 'Site_Code','sitecode_name','updated_at','Isactive')

    def validate(self, data):
        if 'services' in data:
            if data['services'] is not None:
                for t in data['services']:
                    if Stock.objects.filter(id=t.id,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!")

        return data    

    def create(self, validated_data):
        services_data = validated_data.pop('services')
        combo = Combo_Services.objects.create(Price=validated_data.get('Price'))
        
        for s in services_data:
            combo.services.add(s)

        return combo 

    def update(self, instance, validated_data):
        instance.Price = validated_data.get("Price", instance.Price)
        services_data = validated_data.pop('services')
        if services_data:
            for existing in instance.services.all():
                instance.services.remove(existing) 

            for s in services_data:
                instance.services.add(s)

        instance.save()    
          
        return instance   


    def to_representation(self, value):
        ip = get_client_ip(self.context['request'])
        obj = Combo_Services.objects.filter(id=value.id).first()
        if obj.services.all():
            string = ""
            for i in obj.services.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc

        val =  list(set([str(ip)+str(t.Stock_PIC.url) for t in obj.services.all() if t.Stock_PIC]))

        mapped_object = {
            'id': value.id,
            'Price': "{:.2f}".format(float(value.Price)),
            'discount': "{:.2f}".format(float(value.discount)),
            'services' : list(set([t.pk for t in obj.services.all() if t.pk])),
            'combo_names' : string,
            'images' : val
            }
       
        return mapped_object           
                          

class itemCartSerializer(serializers.ModelSerializer): 
    sitecode_name = serializers.CharField(source='sitecodeid.itemsite_desc',required=False)
    itemstatus_name = serializers.CharField(source='itemstatus.status_short_desc',required=False)
    customer = serializers.CharField(source='cust_noid.cust_name',required=False)
    helper_name = serializers.SerializerMethodField() 

    def get_helper_name(self, obj):
        if obj.helper_ids.all().exists():
            string = ""
            for i in obj.helper_ids.all():
                if string == "":
                    string = string + i.helper_id.emp_name
                elif not string == "":
                    string = string +","+ i.helper_id.emp_name
            return string
        else:
            return None 

    class Meta:
        model = ItemCart
        fields = ['id','cust_noid','customer','customercode','cart_id','cart_date','cart_status','lineno',
        'check','itemcodeid','itemdesc','quantity','price','total_price','sitecodeid','sitecode_name',
        'sitecode','discount','discount_amt','discount_price','additional_discount','additional_discountamt',
        'deposit','trans_amt','tax','itemstatus','itemstatus_name','ratio','helper_name','done_sessions',
        'type','treatment_account','treatment','deposit_account','prepaid_account','item_uom']
        read_only_fields = ('sitecode',)

    # def get_validation_exclusions(self):
    #     exclusions = super(itemCartSerializer, self).get_validation_exclusions()
    #     print(exclusions,"exclusions")
    #     return exclusions + ['cust_noid']    
    
class itemCartListSerializer(serializers.ModelSerializer): 
    item = serializers.CharField(source='itemcodeid.item_desc',required=False)
    item_class = serializers.CharField(source='itemcodeid.Item_Classid.itm_desc',required=False)
    itemstatus_name = serializers.CharField(source='itemstatus.status_short_desc',required=False)
    focreason_name = serializers.CharField(source='focreason.foc_reason_ldesc',required=False)
    holdreason_name = serializers.CharField(source='holdreason.hold_desc',required=False)

    class Meta:
        model = ItemCart
        fields = ['id','item','item_class','quantity','price','total_price','discount_price','trans_amt','deposit','itemstatus',
        'itemstatus_name','remark','focreason','focreason_name','holdreason','holdreason_name','holditemqty','ratio','discount',
        'discount_amt','additional_discountamt','is_foc']
        
    
class VoucherRecordSerializer(serializers.ModelSerializer): 

    sitecode_name = serializers.CharField(source='site_codeid.itemsite_desc',required=False)
    cust_name = serializers.CharField(source='cust_codeid.cust_name',required=False)


    class Meta:
        model = VoucherRecord
        fields = ['id','voucher_no','cust_codeid','cust_name','value','percent','site_codeid','sitecode_name','issued_expiry_date','isvalid']
                 

class EmployeeDropSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Employee
        fields = ['id','emp_name','emp_pic']

class PaymentRemarksSerializer(serializers.ModelSerializer):
 
    class Meta:
        model = PaymentRemarks
        fields = ['id','r_code','r_desc']

class HolditemSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolditemSetup
        fields = ['id','hold_code','hold_desc']

class PosPackagedepositSerializer(serializers.ModelSerializer):
    
    net_amt = serializers.SerializerMethodField() 

    def get_net_amt(self, obj):
        if obj.price and obj.qty:
            netamt = obj.price * obj.qty
        else:
            netamt =  0.00
        return netamt        


    class Meta:
        model = PosPackagedeposit
        fields = ['id','description','qty','deposit_amt','net_amt','auto','hold_qty','itemcart']

class PosPackagedepositpostSerializer(serializers.ModelSerializer):

    class Meta:
        model = PosPackagedeposit
        fields = ['id','deposit_amt','hold_qty','itemcart']

