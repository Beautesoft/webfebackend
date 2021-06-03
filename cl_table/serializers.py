from rest_framework import serializers
from .models import (Gender, Employee, Fmspw, Attendance2, Customer, Images, Treatment, Stock,
                     EmpSitelist, ItemClass, ItemRange, PackageDtl, Appointment, ItemDept, Treatment_Master, PayGroup,
                     Paytable,
                     PosTaud, PosDaud, PosHaud, ItemStatus, Source, Securities, ScheduleHour, ApptType, TmpItemHelper,
                     FocReason, Workschedule, CustomerFormControl,
                     CustomerClass, RewardPolicy, RedeemPolicy, Diagnosis)
from cl_app.models import ItemSitelist, SiteGroup
from custom.models import EmpLevel
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import authenticate, get_user_model, password_validation
from rest_framework import status
import datetime as dt
from django.db.models import Q

def get_client_ip(request):
    # url = request.build_absolute_uri()
    # ip = url.split('api')
    # string = ""
    # for idx, val in enumerate(ip[0]):
    #     if idx != 21:
    #         string += val
    ip_str = str("http://"+request.META['HTTP_HOST'])
    return ip_str
  
# class GenderSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Gender
#         fields = '__all__'
#         read_only_fields = ('itm_isactive', 'Sync_LstUpd','created_at') 

class FMSPWSerializer(serializers.ModelSerializer):
    
    id = serializers.IntegerField(source='pk',required=False)
    sitecode = serializers.CharField(source='loginsite.itemsite_code',required=False)
    empcode = serializers.CharField(source='Emp_Codeid.emp_code',required=False)

    class Meta:
        model = Fmspw
        fields = ['id','pw_userlogin','pw_password','LEVEL_ItmIDid','level_desc','Emp_Codeid','empcode','user','loginsite','sitecode']
        read_only_fields = ('pw_isactive','level_desc','user','created_at') 

    def validate(self, data):
        if 'LEVEL_ItmIDid' in data:
            if data['LEVEL_ItmIDid'] is not None:
                if Securities.objects.filter(pk=data['LEVEL_ItmIDid'].pk,level_isactive=False):
                    raise serializers.ValidationError("Securities ID Does not exist!!")

                if not Securities.objects.filter(pk=data['LEVEL_ItmIDid'].pk,level_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Securities Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

        if 'Emp_Codeid' in data:
            if data['Emp_Codeid'] is not None:
                if Employee.objects.filter(pk=data['Emp_Codeid'].pk,emp_isactive=False):
                    raise serializers.ValidationError("Employee ID Does not exist!!")

                if not Employee.objects.filter(pk=data['Emp_Codeid'].pk,emp_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Employee Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
     
        return data        


class UserLoginSerializer(serializers.Serializer):

    salon = serializers.IntegerField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True,style={'input_type': 'password'})

    default_error_messages = {
        'inactive_account': _('User account is disabled.'),
        'invalid_credentials': _('Unable to login with provided credentials.'),
        'invalid_user' : _('Invalid Username.'),
        'invalid_branch' : _('Salon Does not exist.'),
        'invalid' : _('Salon Does not match with User salon.'),
        'site_notmapped' : _('Users is not allowed to login in this site'),
        'sitegrp_notmapped' : _('Site Group is not mapped'),

    }

    def __init__(self, *args, **kwargs):
        super(UserLoginSerializer, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, attrs):
        if attrs.get("salon"):
           branch = ItemSitelist.objects.filter(pk=attrs.get("salon"),itemsite_isactive=True) 
           if not branch:
                raise serializers.ValidationError(self.error_messages['invalid_branch']) 

        if User.objects.filter(username=attrs.get("username")):
            self.user = authenticate(username=attrs.get("username"), password=attrs.get('password'))
            if self.user:
                if not self.user.is_active:
                    raise serializers.ValidationError(self.error_messages['inactive_account'])

                fmspw = Fmspw.objects.filter(user=self.user.id,pw_isactive=True)
                if not fmspw:
                    raise serializers.ValidationError(self.error_messages['inactive_account'])

                emp = fmspw[0].Emp_Codeid.pk
                sitelist_ids = EmpSitelist.objects.filter(Emp_Codeid=emp,Site_Codeid=branch[0].pk,isactive=True)
                if not sitelist_ids:
                    raise serializers.ValidationError(self.error_messages['site_notmapped'])

                if int(sitelist_ids[0].Site_Codeid.pk) != int(attrs.get("salon")):
                    raise serializers.ValidationError(self.error_messages['invalid']) 

                if not branch[0].Site_Groupid:
                    raise serializers.ValidationError(self.error_messages['sitegrp_notmapped'])

                return attrs
            else:
                raise serializers.ValidationError(self.error_messages['invalid_credentials'])
        else:
            raise serializers.ValidationError(self.error_messages['invalid_user']) 

        
class CustomerSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    gender = serializers.CharField(source='Cust_sexesid.itm_name',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name','cust_address','Site_Codeid','site_name','site_code','last_visit',
        'upcoming_appointments','cust_dob','cust_phone2','Cust_sexesid','gender','cust_email','prepaid_card',
        'creditnote','voucher_available','oustanding_payment','cust_refer','custallowsendsms','cust_maillist']
        read_only_fields = ('cust_isactive','created_at', 'updated_at','last_visit','upcoming_appointments',
        'Site_Code','cust_code','ProneToComplain') 
        extra_kwargs = {'cust_name': {'required': True},'cust_address':{'required': True}} 


    def validate(self, data):
        request = self.context['request']
        if not 'cust_name' in request.data:
            raise serializers.ValidationError("cust_name Field is required.")
        else:
            if request.data['cust_name'] is None:
                raise serializers.ValidationError("cust_name Field is required.")
        # if not 'cust_address' in request.data:
        #     raise serializers.ValidationError("cust_address Field is required.")
        # else:
        #     if request.data['cust_address'] is None:
        #         raise serializers.ValidationError("cust_address Field is required.")
        # if not 'cust_dob' in request.data:
        #     raise serializers.ValidationError("cust_dob Field is required.")
        # else:
        #     if request.data['cust_dob'] is None:
        #         raise serializers.ValidationError("cust_dob Field is required.")
        if not 'cust_phone2' in request.data:
            raise serializers.ValidationError("cust_phone2 Field is required.")
        else:
            if request.data['cust_phone2'] is None:
                raise serializers.ValidationError("cust_phone2 Field is required.")
        # if not 'Cust_sexesid' in request.data:
        #     raise serializers.ValidationError("Cust_sexesid Field is required.")
        # else:
        #     if request.data['Cust_sexesid'] is None:
        #         raise serializers.ValidationError("Cust_sexesid Field is required.")
        if not 'Site_Codeid' in request.data:
            raise serializers.ValidationError("Site_Codeid Field is required.")
        else:
            if request.data['Site_Codeid'] is None:
                raise serializers.ValidationError("Site_Codeid Field is required.")
        
        if 'Cust_sexesid' in data:
            if data['Cust_sexesid'] is not None:
                if Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Gender ID Does not exist!!")

                if not Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Gender Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
        
        # if not 'cust_maillist' in request.data:
        #     raise serializers.ValidationError("cust_maillist Field is required.")
        # else:
        #     if request.data['cust_maillist'] is None:
        #         raise serializers.ValidationError("cust_maillist Field is required.")
        # if not 'custallowsendsms' in request.data:
        #     raise serializers.ValidationError("custallowsendsms Field is required.")
        # else:
        #     if request.data['custallowsendsms'] is None:
        #         raise serializers.ValidationError("custallowsendsms Field is required.")    
        # Email and Mobile number validation
        if request.data['cust_email']:
            customer_mail =  Customer.objects.filter(cust_email=request.data['cust_email'])
            if len(customer_mail) > 0:
                raise serializers.ValidationError("Email id is already associated with another account")
        customer =  Customer.objects.filter(cust_phone2=request.data['cust_phone2'])
        if len(customer) > 0:
            raise serializers.ValidationError("Mobile number is already associated with another account")
        return data    

class CustomerClassSerializer(serializers.ModelSerializer):
    class Meta:
        model= CustomerClass
        fields = ["id","class_desc","class_code"]


class CustomerPlusSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    gender = serializers.CharField(source='Cust_sexesid.itm_name',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)
    # class_name = serializers.CharField(source='Cust_Classid.class_desc',required=False)
    custClass = CustomerClassSerializer(source="Cust_Classid",read_only=True)

    class Meta:
        model = Customer
        fields = ['id','cust_code','cust_name','cust_address','Site_Codeid','site_name','site_code','last_visit','custClass',
                  # 'class_name',
        'upcoming_appointments','cust_dob','cust_phone2','Cust_sexesid','gender','cust_email','prepaid_card','cust_occupation',
        'creditnote','voucher_available','oustanding_payment','cust_refer','custallowsendsms','cust_maillist','cust_title']
        read_only_fields = ('cust_isactive','created_at', 'updated_at','last_visit','upcoming_appointments',
        'Site_Code','cust_code','ProneToComplain')
        extra_kwargs = {'cust_name': {'required': True},'cust_address':{'required': True}}


    def validate(self, data):
        request = self.context['request']

        action = self.context.get('action')

        # customer form settings validation
        fmspw = Fmspw.objects.filter(user=request.user, pw_isactive=True)
        site = fmspw[0].loginsite
        form_control_qs = CustomerFormControl.objects.filter(isActive=True,Site_Codeid=site)
        allowed_fields = []

        # if action == "list":
        #     allowed_fields = form_control_qs.filter(visible_in_listing=True).values_list("field_name",flat=True)
        # elif action == "retrieve":
        #     allowed_fields = form_control_qs.filter(visible_in_profile=True).values_list("field_name",flat=True)
        # if action == "create":
        #     allowed_fields = form_control_qs.filter(visible_in_registration=True) #.values_list("field_name",flat=True)
        mandatory_fields = form_control_qs.filter(mandatory=True).values_list("field_name",flat=True)

        for _field in mandatory_fields:
            if request.data.get(_field) is None:
                raise serializers.ValidationError(f"{_field} Field is required.")




        # if not 'cust_name' in request.data:
        #     raise serializers.ValidationError("cust_name Field is required.")
        # else:
        #     if request.data['cust_name'] is None:
        #         raise serializers.ValidationError("cust_name Field is required.")
        # # if not 'cust_address' in request.data:
        # #     raise serializers.ValidationError("cust_address Field is required.")
        # # else:
        # #     if request.data['cust_address'] is None:
        # #         raise serializers.ValidationError("cust_address Field is required.")
        # # if not 'cust_dob' in request.data:
        # #     raise serializers.ValidationError("cust_dob Field is required.")
        # # else:
        # #     if request.data['cust_dob'] is None:
        # #         raise serializers.ValidationError("cust_dob Field is required.")
        # if not 'cust_phone2' in request.data:
        #     raise serializers.ValidationError("cust_phone2 Field is required.")
        # else:
        #     if request.data['cust_phone2'] is None:
        #         raise serializers.ValidationError("cust_phone2 Field is required.")
        # if not 'Cust_sexesid' in request.data:
        #     raise serializers.ValidationError("Cust_sexesid Field is required.")
        # else:
        #     if request.data['Cust_sexesid'] is None:
        #         raise serializers.ValidationError("Cust_sexesid Field is required.")
        if not 'Site_Codeid' in request.data:
            raise serializers.ValidationError("Site_Codeid Field is required.")
        else:
            if request.data['Site_Codeid'] is None:
                raise serializers.ValidationError("Site_Codeid Field is required.")

        if 'Cust_sexesid' in data:
            if data['Cust_sexesid'] is not None:
                if Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Gender ID Does not exist!!")

                if not Gender.objects.filter(pk=data['Cust_sexesid'].pk,itm_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Gender Id does not exist!!",'error': True}
                    raise serializers.ValidationError(result)
        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")

        # if not 'cust_maillist' in request.data:
        #     raise serializers.ValidationError("cust_maillist Field is required.")
        # else:
        #     if request.data['cust_maillist'] is None:
        #         raise serializers.ValidationError("cust_maillist Field is required.")
        # if not 'custallowsendsms' in request.data:
        #     raise serializers.ValidationError("custallowsendsms Field is required.")
        # else:
        #     if request.data['custallowsendsms'] is None:
        #         raise serializers.ValidationError("custallowsendsms Field is required.")
        # Email and Mobile number validation
        # if request.data['cust_email']:
        #     customer_mail =  Customer.objects.filter(cust_email=request.data['cust_email'])
        #     if len(customer_mail) > 0:
        #         raise serializers.ValidationError("Email id is already associated with another account")
        # customer =  Customer.objects.filter(cust_phone2=request.data['cust_phone2'])
        # if len(customer) > 0:
        #     raise serializers.ValidationError("Mobile number is already associated with another account")
        return data


class CustomerUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    gender = serializers.CharField(source='Cust_sexesid.itm_name',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_name','cust_address','Site_Codeid','site_name',
        'cust_dob','cust_phone2','Cust_sexesid','gender',
        'cust_email','custallowsendsms','cust_maillist']

    def validate(self, data):
        pk = self.instance.pk
        # Email and Mobile number validation
        customer_mail =  Customer.objects.filter(cust_email=data['cust_email']).exclude(pk=pk)
        if len(customer_mail) > 0:
            raise serializers.ValidationError("Email id is already associated with another account")
        customer =  Customer.objects.filter(cust_phone2=data['cust_phone2']).exclude(pk=pk)
        if len(customer) > 0:
            raise serializers.ValidationError("Mobile number is already associated with another account")
        return data


class CustomerallSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_name']

class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ['id','image']

class StockListTreatmentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Stock
        fields = ['id','treatment_details','procedure','Stock_PIC']

class ServicesSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    images = ImagesSerializer(source='images_set', many=True, read_only=True)
    category_name = serializers.CharField(source='Item_Classid.itm_desc',required=False)
    type_name = serializers.CharField(source='Item_Rangeid.itm_desc',required=False)


    class Meta:
        model = Stock
        fields = ['id','item_desc','Item_Classid','category_name','item_price','tax','itm_disc','sutiable_for',
        'description','Item_Rangeid','type_name','images']
        read_only_fields = ('updated_at','item_isactive','category_name','Item_Class')
        

    def validate(self, data):
        request = self.context['request']
        if not 'item_desc' in request.data:
            raise serializers.ValidationError("item_desc Field is required.")
        else:
            if request.data['item_desc'] is None:
                raise serializers.ValidationError("item_desc Field is required.")
        if not 'Item_Classid' in request.data:
            raise serializers.ValidationError("Item_Classid Field is required.")
        else:
            if request.data['Item_Classid'] is None:
                raise serializers.ValidationError("Item_Classid Field is required.")
        if not 'item_price' in request.data:
            raise serializers.ValidationError("item_price Field is required.")
        else:
            if request.data['item_price'] is None:
                raise serializers.ValidationError("item_price Field is required.")
        if not 'tax' in request.data:
            raise serializers.ValidationError("tax Field is required.")
        else:
            if request.data['tax'] is None:
                raise serializers.ValidationError("tax Field is required.")
        if not 'itm_disc' in request.data:
            raise serializers.ValidationError("itm_disc Field is required.")
        else:
            if request.data['itm_disc'] is None:
                raise serializers.ValidationError("itm_disc Field is required.")

        if 'Item_Classid' in data:
            if data['Item_Classid'] is not None:
                if ItemClass.objects.filter(pk=data['Item_Classid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Category ID Does not exist!!")
                if not ItemClass.objects.filter(pk=data['Item_Classid'].pk,itm_isactive=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Category Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)
     
        if 'Item_Rangeid' in data:
            if data['Item_Rangeid'] is not None:
                if ItemRange.objects.filter(pk=data['Item_Rangeid'].pk,itm_status=False):
                    raise serializers.ValidationError("Type ID Does not exist!!")
                if not ItemRange.objects.filter(pk=data['Item_Rangeid'].pk,itm_status=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Type Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)                        
        return data      
        
    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        stock = Stock.objects.create(item_desc=validated_data.get('item_desc'),Item_Classid=validated_data.get('Item_Classid'),
        item_price=validated_data.get('item_price'),tax=validated_data.get('tax'),itm_disc=validated_data.get('itm_disc'),
        sutiable_for=validated_data.get('sutiable_for'),description=validated_data.get('description'),
        Item_Rangeid=validated_data.get('Item_Rangeid'),item_code=validated_data.get('item_code'))
 
       
        for image_data in images_data.values():
            Images.objects.create(services=stock, image=image_data)
        return stock 

    def update(self, instance, validated_data):
        images_data = self.context.get('view').request.FILES
        instance.item_desc = validated_data.get("item_desc", instance.item_desc)
        instance.Item_Classid = validated_data.get("Item_Classid", instance.Item_Classid)
        instance.item_price = validated_data.get("item_price", instance.item_price)
        instance.tax = validated_data.get("tax", instance.tax)
        instance.itm_disc = validated_data.get("itm_disc", instance.itm_disc)
        instance.sutiable_for = validated_data.get("sutiable_for", instance.sutiable_for)
        instance.description = validated_data.get("description", instance.description)
        instance.Item_Rangeid = validated_data.get("Item_Rangeid", instance.Item_Rangeid)
        

        if self.context['request'].method == 'PUT': 
            if images_data:
                # instance.images_set.all().delete()
                for image_data in images_data.values():
                    Images.objects.create(services=instance, image=image_data)

        instance.save()    
          
        return instance

class ItemSiteListAPISerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ItemSitelist
        fields = ['id','itemsite_desc','itemsite_code']


class ItemSiteListSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    skills = serializers.SerializerMethodField() 
    images = ImagesSerializer(source='images_set', many=True, read_only=True)
    salon_name = serializers.CharField(source='Site_Groupid.description',required=False)

    def get_skills(self, obj):
        if obj.services:
            string = ""
            for i in obj.services.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None 


    class Meta:
        model = ItemSitelist
        fields = ['id','skills_list','itemsite_desc','itemsite_code','Site_Groupid','salon_name','skills','services',
        'itemsite_phone1','itemsite_date','itemsite_email','images']
        read_only_fields = ('created_at', 'updated_at','itemsite_isactive')


    def validate(self, data):
        request = self.context['request']
        if not 'itemsite_desc' in request.data:
            raise serializers.ValidationError("itemsite_desc Field is required.")
        else:
            if request.data['itemsite_desc'] is None:
                raise serializers.ValidationError("itemsite_desc Field is required.")
        if not 'itemsite_date' in request.data:
            raise serializers.ValidationError("itemsite_date Field is required.")
        else:
            if request.data['itemsite_date'] is None:
                raise serializers.ValidationError("itemsite_date Field is required.")
        if not 'Site_Groupid' in request.data:
            raise serializers.ValidationError("Site_Groupid Field is required.")
        else:
            if request.data['Site_Groupid'] is None:
                raise serializers.ValidationError("Site_Groupid Field is required.")
        if not 'skills_list' in request.data:
            raise serializers.ValidationError("skills_list Field is required.")
        else:
            if request.data['skills_list'] is None:
                raise serializers.ValidationError("skills_list Field is required.")
        if not 'itemsite_phone1' in request.data:
            raise serializers.ValidationError("itemsite_phone1 Field is required.")
        else:
            if request.data['itemsite_phone1'] is None:
                raise serializers.ValidationError("itemsite_phone1 Field is required.")
        if not 'itemsite_email' in request.data:
            raise serializers.ValidationError("itemsite_email Field is required.")
        else:
            if request.data['itemsite_email'] is None:
                raise serializers.ValidationError("itemsite_email Field is required.")
        if not 'itemsite_code' in request.data:
            raise serializers.ValidationError("itemsite_code Field is required.")
        else:
            if request.data['itemsite_code'] is None:
                raise serializers.ValidationError("itemsite_code Field is required.")
            
        if 'Site_Groupid' in data:
            if data['Site_Groupid'] is not None:
                if SiteGroup.objects.filter(id=data['Site_Groupid'].id,is_active=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not SiteGroup.objects.filter(id=data['Site_Groupid'].id,is_active=True):
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Branch Id does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)      

        if 'services' in data:
            if data['services'] is not None:
                for t in data['services']:
                    if Stock.objects.filter(pk=t.pk,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!") 
                     

        if 'skills_list' in data:
            if data['skills_list'] is not None:
                if ',' in data['skills_list']:
                    res = data['skills_list'].split(',')
                else:
                    res = data['skills_list'].split(' ')
                for t in res:
                    id_val = int(t)
                    if Stock.objects.filter(pk=id_val,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!")    
                    if not Stock.objects.filter(pk=id_val,item_isactive=True):
                        raise serializers.ValidationError("Services ID Does not exist!!")    
                                   
        return data

    def create(self, validated_data):
        images_data = self.context.get('view').request.FILES
        site_id = ItemSitelist.objects.create(itemsite_code=validated_data.get('itemsite_code'),
        itemsite_desc=validated_data.get('itemsite_desc'),itemsite_date=validated_data.get('itemsite_date'),
        itemsite_phone1=validated_data.get('itemsite_phone1'),itemsite_email=validated_data.get('itemsite_email'),
        Site_Groupid=validated_data.get('Site_Groupid'))
        
        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')

        for service in res:
            site_id.services.add(service)

        for image_data in images_data.values():
            Images.objects.create(item_sitelist=site_id, image=image_data)
    
        return site_id 

    def update(self, instance, validated_data):
        images_data = self.context.get('view').request.FILES
        instance.itemsite_code = validated_data.get("itemsite_code", instance.itemsite_code)
        instance.itemsite_desc = validated_data.get("itemsite_desc", instance.itemsite_desc)
        instance.itemsite_date = validated_data.get("itemsite_date", instance.itemsite_date)
        instance.itemsite_phone1 = validated_data.get("itemsite_phone1", instance.itemsite_phone1)
        instance.itemsite_email = validated_data.get("itemsite_email", instance.itemsite_email)
        instance.Site_Groupid = validated_data.get("Site_Groupid", instance.Site_Groupid)

        if self.context['request'].method == 'PUT': 
            if images_data:
                # instance.images_set.all().delete()
                for image_data in images_data.values():
                    Images.objects.create(item_sitelist=instance, image=image_data)           


        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')

        if skills_data:
            for existing in instance.services.all():
                instance.services.remove(existing) 

            for skill in res:
                instance.services.add(skill)

        instance.save()    
          
        return instance     


class EmployeeSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    services =  serializers.SerializerMethodField() 
    gender = serializers.CharField(source='Emp_sexesid.itm_name',required=False)
    jobtitle_name = serializers.CharField(source='EMP_TYPEid.level_desc',required=False)
    shift_name = serializers.SerializerMethodField()
    level_desc = serializers.CharField(source='LEVEL_ItmIDid.level_description',required=False)
    site_name = serializers.CharField(source='defaultSiteCodeid.itemsite_desc',required=False)


    def get_shift_name(self, obj):
        if obj.shift:
            att = obj.shift
            return str(att.attn_time) +" "+ "to" +" "+str(att.attn_mov_in)
        else:
            return None    

    def get_services(self, obj):
        if obj.skills.all():
            string = ""
            for i in obj.skills.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None            


    class Meta:
        model = Employee
        fields = ['id','skills_list','emp_name','display_name','emp_phone1','emp_code','skills','services','emp_address',
        'Emp_sexesid','gender','defaultSiteCodeid','defaultsitecode','site_name','Site_Codeid','site_code',
        'emp_dob','emp_joindate','shift','shift_name','emp_email','emp_pic','EMP_TYPEid','jobtitle_name',
        'is_login','pw_password','LEVEL_ItmIDid','level_desc','emp_isactive',"emp_nric"]
        read_only_fields = ('emp_isactive','updated_at','created_at','emp_code','branch')
        extra_kwargs = {'emp_email': {'required': False},'Site_Codeid': {'required': False},
        'emp_name': {'required': True}}


    def validate(self, data):
        request = self.context['request']
        if not 'emp_name' in request.data:
            raise serializers.ValidationError("emp_name Field is required.")
        else:
            if request.data['emp_name'] is None:
                raise serializers.ValidationError("emp_name Field is required.")
        if not 'Emp_sexesid' in request.data:
            raise serializers.ValidationError("Emp_sexesid Field is required.")
        else:
            if request.data['Emp_sexesid'] is None:
                raise serializers.ValidationError("Emp_sexesid Field is required.")
        if not 'emp_phone1' in request.data:
            raise serializers.ValidationError("emp_phone1 Field is required.")
        else:
            if request.data['emp_phone1'] is None:
                raise serializers.ValidationError("emp_phone1 Field is required.")
        if not 'emp_address' in request.data:
            raise serializers.ValidationError("emp_address Field is required.")
        else:
            if request.data['emp_address'] is None:
                raise serializers.ValidationError("emp_address Field is required.")
        if not 'emp_dob' in request.data:
            raise serializers.ValidationError("emp_dob Field is required.")
        else:
            if request.data['emp_dob'] is None:
                raise serializers.ValidationError("emp_dob Field is required.")
        if not 'emp_joindate' in request.data:
            raise serializers.ValidationError("emp_joindate Field is required.")
        else:
            if request.data['emp_joindate'] is None:
                raise serializers.ValidationError("emp_joindate Field is required.")
        if not 'EMP_TYPEid' in request.data:
            raise serializers.ValidationError("EMP_TYPEid Field is required.")
        else:
            if request.data['EMP_TYPEid'] is None:
                raise serializers.ValidationError("EMP_TYPEid Field is required.")
        if not 'skills_list' in request.data:
            raise serializers.ValidationError("skills_list Field is required.")
        else:
            if request.data['skills_list'] is None:
                raise serializers.ValidationError("skills_list Field is required.")
        if not 'defaultSiteCodeid' in request.data:
            raise serializers.ValidationError("defaultSiteCodeid Field is required.")
        else:
            if request.data['defaultSiteCodeid'] is None:
                raise serializers.ValidationError("defaultSiteCodeid Field is required.")
        if not 'emp_pic' in request.data:
            raise serializers.ValidationError("emp_pic Field is required.")
        else:
            if request.data['emp_pic'] is None:
                raise serializers.ValidationError("emp_pic Field is required.")


        if 'skills_list' in data:
            if data['skills_list'] is not None:
                if ',' in data['skills_list']:
                    res = data['skills_list'].split(',')
                else:
                    res = data['skills_list'].split(' ')
                for t in res:
                    id_val = int(t)
                    if Stock.objects.filter(pk=id_val,item_isactive=False):
                        raise serializers.ValidationError("Services ID Does not exist!!")  

                    if not Stock.objects.filter(pk=id_val,item_isactive=True):
                        raise serializers.ValidationError("Services ID Does not exist!!")                
                                         
                                 
        if 'Emp_sexesid' in data:
            if data['Emp_sexesid'] is not None:
                if Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=False):
                    raise serializers.ValidationError("Gender ID Does not exist!!")
                if not Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=True):
                    raise serializers.ValidationError("Gender ID Does not exist!!")
 

        if 'shift' in data:
            if data['shift'] is not None:
                if Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")
                if not Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")


        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")


      
        if 'defaultSiteCodeid' in data:
            if data['defaultSiteCodeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")

        
        if 'EMP_TYPEid' in data:
            if data['EMP_TYPEid'] is not None:
                if EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=False):
                    raise serializers.ValidationError("Job Title ID Does not exist!!") 
                if not EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=True):
                    raise serializers.ValidationError("Job Title ID Does not exist!!")   
              
        return data       

    def create(self, validated_data):
        fmspw = Fmspw.objects.filter(user=self.context['request'].user,pw_isactive=True).first()
        Site_Codeid = fmspw.loginsite
        siteobj = ItemSitelist.objects.filter(pk=validated_data.get('defaultSiteCodeid').pk,itemsite_isactive=True).first()
        employee = Employee.objects.create(emp_name=validated_data.get('emp_name'),
                                           emp_phone1=validated_data.get('emp_phone1'),
                                           display_name=validated_data.get('emp_name'),
                                           emp_address=validated_data.get('emp_address'),
                                           Emp_sexesid=validated_data.get('Emp_sexesid'),
                                           emp_dob=validated_data.get('emp_dob'),
                                           emp_joindate=validated_data.get('emp_joindate'),
                                           shift=validated_data.get('shift'),
                                           defaultSiteCodeid=validated_data.get('defaultSiteCodeid'),
                                           defaultsitecode=siteobj.itemsite_code,
                                           emp_pic=validated_data.get('emp_pic'),
                                           is_login=validated_data.get('is_login'),
                                           EMP_TYPEid=validated_data.get('EMP_TYPEid'),
                                           Site_Codeid=Site_Codeid,
                                           site_code=Site_Codeid.itemsite_code)
        
        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')
        for skill in res:
            employee.skills.add(skill)
        return employee 

    def update(self, instance, validated_data):
        instance.emp_name = validated_data.get("emp_name", instance.emp_name)
        instance.emp_phone1 = validated_data.get("emp_phone1", instance.emp_phone1)
        instance.emp_address = validated_data.get("emp_address", instance.emp_address)
        instance.Emp_sexesid = validated_data.get("Emp_sexesid", instance.Emp_sexesid)
        instance.emp_dob = validated_data.get("emp_dob", instance.emp_dob)
        instance.emp_joindate = validated_data.get("emp_joindate", instance.emp_joindate)
        instance.shift = validated_data.get("shift", instance.shift)
        instance.emp_pic = validated_data.get("emp_pic", instance.emp_pic)
        instance.EMP_TYPEid = validated_data.get("EMP_TYPEid", instance.EMP_TYPEid)
        instance.defaultSiteCodeid = validated_data.get("defaultSiteCodeid", instance.defaultSiteCodeid)
        instance.defaultsitecode = instance.defaultSiteCodeid.itemsite_code
        instance.Site_Codeid = validated_data.get("Site_Codeid", instance.Site_Codeid)
        instance.site_code = instance.Site_Codeid.itemsite_code

        if 'emp_email' in validated_data:
            if validated_data['emp_email'] is not None:
                instance.emp_email = validated_data.get("emp_email", instance.emp_email)

        skills_data = validated_data.pop('skills_list')
        if ',' in skills_data:
            res = skills_data.split(',')
        else:
            res = skills_data.split(' ')

        if skills_data:
            for existing in instance.skills.all():
                instance.skills.remove(existing) 

            for skill in res:
                instance.skills.add(skill)
        instance.save()    
        return instance

class StaffPlusSerializer(serializers.ModelSerializer):
    """
    most parts are identical to EmployeeSerializer. validation little bit different.
    use for StaffPlus APIs.
    TODO:   should be figure out a way to use same serializer (EmployeeSerializer) to both old stadd apis and
            staff plus apis without any conflicts.
    """
    id = serializers.IntegerField(source='pk',required=False)
    services =  serializers.SerializerMethodField()
    gender = serializers.CharField(source='Emp_sexesid.itm_name',required=False)
    jobtitle_name = serializers.CharField(source='EMP_TYPEid.level_desc',required=False)
    shift_name = serializers.SerializerMethodField()
    level_desc = serializers.CharField(source='LEVEL_ItmIDid.level_description',required=False)
    site_name = serializers.CharField(source='defaultSiteCodeid.itemsite_desc',required=False)


    def get_shift_name(self, obj):
        if obj.shift:
            att = obj.shift
            return str(att.attn_time) +" "+ "to" +" "+str(att.attn_mov_in)
        else:
            return None

    def get_services(self, obj):
        if obj.skills.all():
            string = ""
            for i in obj.skills.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None


    class Meta:
        model = Employee
        fields = ['id','skills_list','emp_name','display_name','emp_phone1','emp_code','skills','services',
                  'emp_address', 'Emp_sexesid','gender','defaultSiteCodeid','defaultsitecode','site_name',
                  'Site_Codeid','site_code', 'emp_dob','emp_joindate','shift','shift_name','emp_email','emp_pic',
                  'EMP_TYPEid','jobtitle_name', 'is_login','pw_password','LEVEL_ItmIDid','level_desc','emp_isactive',
                  "emp_nric","max_disc", 'emp_race', 'Emp_nationalityid', 'Emp_maritalid', 'Emp_religionid', 'emp_emer',
                  'emp_emerno', 'emp_country', 'emp_remarks','show_in_trmt','show_in_appt','show_in_sales']
        read_only_fields = ('updated_at','created_at','emp_code','branch')
        extra_kwargs = {'emp_email': {'required': False},'Site_Codeid': {'required': False},
        'emp_name': {'required': True}}


    def validate(self, data):
        """ validation for StaffPlusSerializer"""
        request = self.context['request']
        if not 'emp_name' in request.data:
            raise serializers.ValidationError("emp_name Field is required.")
        else:
            if request.data['emp_name'] is None:
                raise serializers.ValidationError("emp_name Field is required.")

        if request.data.get("emp_isactive") is None:
            raise serializers.ValidationError("emp_isactive field is required.")

        if request.data.get("display_name") is None:
            raise serializers.ValidationError("display_name field is required.")

        if request.data.get("max_disc") is None:
            raise serializers.ValidationError("max_disc field is required.")

        if request.data.get("emp_joindate") is None:
            raise serializers.ValidationError("emp_joindate field is required.")

        # if request.data.get("emp_nric") is None:
        #     raise serializers.ValidationError("emp_nric field is required.")

        # if 'skills_list' in data:
        #     if data['skills_list'] is not None:
        #         if ',' in data['skills_list']:
        #             res = data['skills_list'].split(',')
        #         else:
        #             res = data['skills_list'].split(' ')
        #         for t in res:
        #             id_val = int(t)
        #             if Stock.objects.filter(pk=id_val,item_isactive=False):
        #                 raise serializers.ValidationError("Services ID Does not exist!!")
        #
        #             if not Stock.objects.filter(pk=id_val,item_isactive=True):
        #                 raise serializers.ValidationError("Services ID Does not exist!!")


        # if 'Emp_sexesid' in data:
        #     if data['Emp_sexesid'] is not None:
        #         if Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=False):
        #             raise serializers.ValidationError("Gender ID Does not exist!!")
        #         if not Gender.objects.filter(pk=data['Emp_sexesid'].pk,itm_isactive=True):
        #             raise serializers.ValidationError("Gender ID Does not exist!!")


        if 'shift' in data:
            if data['shift'] is not None:
                if Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")
                if not Attendance2.objects.filter(pk=data['shift'].pk):
                    raise serializers.ValidationError("Shift ID Does not exist!!")


        if 'Site_Codeid' in data:
            if data['Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")



        if 'defaultSiteCodeid' in data:
            if data['defaultSiteCodeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Branch ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['defaultSiteCodeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Branch ID Does not exist!!")


        if 'EMP_TYPEid' in data:
            if data['EMP_TYPEid'] is not None:
                if EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=False):
                    raise serializers.ValidationError("Job Title ID Does not exist!!")
                if not EmpLevel.objects.filter(id=data['EMP_TYPEid'].id,level_isactive=True):
                    raise serializers.ValidationError("Job Title ID Does not exist!!")

        return data

    def create(self, validated_data):
        fmspw = Fmspw.objects.filter(user=self.context['request'].user,pw_isactive=True).first()
        Site_Codeid = fmspw.loginsite
        site_code_str = str(Site_Codeid.itemsite_code)
        siteobj = ItemSitelist.objects.filter(pk=validated_data.get('defaultSiteCodeid').pk,itemsite_isactive=True).first()
        employee = Employee.objects.create(emp_name=validated_data.get('emp_name'),
                                           emp_phone1=validated_data.get('emp_phone1'),
                                           display_name=validated_data.get('display_name'),
                                           emp_address=validated_data.get('emp_address'),
                                           Emp_sexesid=validated_data.get('Emp_sexesid'),
                                           emp_dob=validated_data.get('emp_dob'),
                                           emp_joindate=validated_data.get('emp_joindate'),
                                           shift=validated_data.get('shift'),
                                           defaultSiteCodeid=validated_data.get('defaultSiteCodeid'),
                                           defaultsitecode=siteobj.itemsite_code,
                                           emp_pic=validated_data.get('emp_pic'),
                                           is_login=validated_data.get('is_login'),
                                           EMP_TYPEid=validated_data.get('EMP_TYPEid'),
                                           emp_isactive=validated_data.get('emp_isactive'),
                                           emp_nric=validated_data.get('emp_nric'),
                                           max_disc=validated_data.get('max_disc'),
                                           show_in_sales=validated_data.get('show_in_sales'),
                                           show_in_appt=validated_data.get('show_in_appt'),
                                           show_in_trmt=validated_data.get('show_in_trmt'),
                                           Site_Codeid=Site_Codeid,
                                           site_code=site_code_str)

        # skills_data = validated_data.pop('skills_list')
        # if ',' in skills_data:
        #     res = skills_data.split(',')
        # else:
        #     res = skills_data.split(' ')
        # for skill in res:
        #     employee.skills.add(skill)
        return employee

    def update(self, instance, validated_data):
        instance.emp_name = validated_data.get("emp_name", instance.emp_name)
        instance.display_name = validated_data.get("display_name", instance.display_name)
        instance.emp_phone1 = validated_data.get("emp_phone1", instance.emp_phone1)
        instance.emp_address = validated_data.get("emp_address", instance.emp_address)
        instance.Emp_sexesid = validated_data.get("Emp_sexesid", instance.Emp_sexesid)
        instance.emp_dob = validated_data.get("emp_dob", instance.emp_dob)
        instance.emp_joindate = validated_data.get("emp_joindate", instance.emp_joindate)
        instance.shift = validated_data.get("shift", instance.shift)
        instance.emp_pic = validated_data.get("emp_pic", instance.emp_pic)
        instance.EMP_TYPEid = validated_data.get("EMP_TYPEid", instance.EMP_TYPEid)
        instance.defaultSiteCodeid = validated_data.get("defaultSiteCodeid", instance.defaultSiteCodeid)
        instance.defaultsitecode = instance.defaultSiteCodeid.itemsite_code
        instance.Site_Codeid = validated_data.get("Site_Codeid", instance.Site_Codeid)
        instance.emp_isactive = validated_data.get("emp_isactive", instance.emp_isactive)
        instance.emp_nric = validated_data.get("emp_nric", instance.emp_nric)
        instance.max_disc = validated_data.get("max_disc", instance.max_disc)
        instance.site_code = instance.Site_Codeid.itemsite_code,
        instance.show_in_sales = validated_data.get("show_in_sales", instance.show_in_sales)
        instance.show_in_appt = validated_data.get("show_in_appt", instance.show_in_appt)
        instance.show_in_trmt = validated_data.get("show_in_trmt", instance.show_in_trmt)

        if 'emp_email' in validated_data:
            if validated_data['emp_email'] is not None:
                instance.emp_email = validated_data.get("emp_email", instance.emp_email)


        instance.save()
        return instance

class Attendance2Serializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    emp_name = serializers.CharField(source='Attn_Emp_codeid.emp_name',required=False)
    emp_img = serializers.ImageField(source='Attn_Emp_codeid.emp_pic',required=False)
    sitecode_name = serializers.CharField(source='Attn_Site_Codeid.itemsite_desc',required=False)
    shift_name = serializers.SerializerMethodField()

    def get_shift_name(self, obj):
        if obj:
            att = obj
            return str(att.attn_time) +" "+ "to" +" "+str(att.attn_mov_in) 
        else:
            return None  

    class Meta:
        model = Attendance2
        fields = ['id','shift_name','Attn_Emp_codeid','emp_name','emp_img','attn_date',
        'Attn_Site_Codeid','sitecode_name','attn_site_code','attn_time','attn_mov_in']
        read_only_fields = ('Create_date','Create_time', 'updated_at','emp_name','emp_img','attn_site_code')

    def validate(self, data):
        request = self.context['request']
        if not 'Attn_Emp_codeid' in request.data:
            raise serializers.ValidationError("Attn_Emp_codeid Field is required.")
        else:
            if request.data['Attn_Emp_codeid'] is None:
                raise serializers.ValidationError("Attn_Emp_codeid Field is required.")
        if not 'attn_date' in request.data:
            raise serializers.ValidationError("attn_date Field is required.")
        else:
            if request.data['attn_date'] is None:
                raise serializers.ValidationError("attn_date Field is required.")
        if not 'attn_time' in request.data:
            raise serializers.ValidationError("attn_time Field is required.")
        else:
            if request.data['attn_time'] is None:
                raise serializers.ValidationError("attn_time Field is required.")
        if not 'attn_mov_in' in request.data:
            raise serializers.ValidationError("attn_mov_in Field is required.")
        else:
            if request.data['attn_mov_in'] is None:
                raise serializers.ValidationError("attn_mov_in Field is required.")
        
        if 'Attn_Emp_codeid' in data:
            if data['Attn_Emp_codeid'] is not None:
                if Employee.objects.filter(pk=data['Attn_Emp_codeid'].pk,emp_isactive=False):
                    raise serializers.ValidationError("Employee ID Does not exist!!")
                if not Employee.objects.filter(pk=data['Attn_Emp_codeid'].pk,emp_isactive=True):
                        raise serializers.ValidationError("Employee ID Does not exist!!")


        if 'Attn_Site_Codeid' in data: 
            if data['Attn_Site_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['Attn_Site_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['Attn_Site_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site ID Does not exist!!")

        return data
    
class AppointmentSerializer(serializers.ModelSerializer):   
    id = serializers.IntegerField(source='pk',required=False)
    cust_name = serializers.CharField(source='cust_noid.cust_name',required=False)
    source_name = serializers.CharField(source='Source_Codeid.source_desc',required=False)
    site_name = serializers.CharField(source='ItemSite_Codeid.itemsite_desc',required=False)


    class Meta:
        model = Appointment
        fields = ['id','appt_date','appt_code','appt_fr_time','appt_to_time','Appt_typeid','appt_type','cust_noid',
        'cust_name','appt_phone','new_remark','appt_created_by','Source_Codeid','source_name','Room_Codeid',
        'room_code','appt_status','emp_noid','emp_name','requesttherapist','ItemSite_Codeid','itemsite_code',
        'site_name','cust_refer','sec_status','walkin']
        read_only_fields = ('cust_name','appt_code')

    def validate(self, data):
        if 'cust_noid' in data:
            if data['cust_noid'] is not None:
                if Customer.objects.filter(pk=data['cust_noid'].pk,cust_isactive=False):
                    raise serializers.ValidationError("Customer ID Does not exist!!")
                if not Customer.objects.filter(pk=data['cust_noid'].pk,cust_isactive=True):
                    raise serializers.ValidationError("Customer ID Does not exist!!")
        
        if 'ItemSite_Codeid' in data:
            if data['ItemSite_Codeid'] is not None:
                if ItemSitelist.objects.filter(pk=data['ItemSite_Codeid'].pk,itemsite_isactive=False):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")
                if not ItemSitelist.objects.filter(pk=data['ItemSite_Codeid'].pk,itemsite_isactive=True):
                    raise serializers.ValidationError("Site Code ID Does not exist!!")

        if 'Source_Codeid' in data:
            if data['Source_Codeid'] is not None:
                if Source.objects.filter(id=data['Source_Codeid'].id,source_isactive=False):
                    raise serializers.ValidationError("Source ID Does not exist!!")
                if not Source.objects.filter(id=data['Source_Codeid'].id,source_isactive=True):
                    raise serializers.ValidationError("Source ID Does not exist!!")
                
        return data      
               
class AppointmentCalendarSerializer(serializers.ModelSerializer):   

    id = serializers.IntegerField(source='pk',required=False)
    Cust_phone = serializers.CharField(source='cust_noid.cust_phone2',required=False)
    job_title = serializers.CharField(source='emp_noid.EMP_TYPEid.level_desc',required=False)
    start = serializers.SerializerMethodField() 
    end = serializers.SerializerMethodField() 
    emp_img =  serializers.SerializerMethodField() 

    def get_emp_img(self, obj):
        ip = get_client_ip(self.context['request'])
        pic = None

        if obj.emp_noid.emp_pic:
            pic = str(ip)+str(obj.emp_noid.emp_pic.url)
        return pic

    def get_start(self, obj):
        if obj.appt_date and obj.appt_fr_time:
            appt_date = obj.appt_date
            appt_time = obj.appt_fr_time
            #.lstrip("0").replace(" 0", " ")
            mytime = dt.datetime.strptime(str(appt_time),'%H:%M:%S').strftime("%H:%M")
            # mydatetime = dt.datetime.combine(appt_date, fr_time)
            mydatetime = str(appt_date) +" "+ str(mytime)
            return str(mydatetime)
        else:
            return []  

    def get_end(self, obj):
        if obj.appt_date and obj.appt_fr_time:
            appt_date = obj.appt_date
            appt_time = obj.appt_to_time
            # .lstrip("0").replace(" 0", " ")
            mytime = dt.datetime.strptime(str(appt_time),'%H:%M:%S').strftime("%H:%M")
            mydatetime = str(appt_date) +" "+ str(mytime)
            return str(mydatetime)
        else:
            return []          

    class Meta:
        model = Appointment
        fields = ['id','start','end','emp_img','emp_noid','emp_name','job_title','cust_noid','cust_name',
        'cust_refer', 'Cust_phone','new_remark','appt_status','appt_date','appt_fr_time','appt_to_time']


class Item_DeptSerializer(serializers.ModelSerializer):  
    id = serializers.IntegerField(source='pk',required=False)
  
    class Meta:
        model = ItemDept
        fields = ['id','itm_desc','deptpic']

class StockListSerializer(serializers.ModelSerializer): 
    id = serializers.IntegerField(source='pk',required=False)
    Item_Class = serializers.CharField(source='Item_Classid.itm_desc',required=False)
  
    class Meta:
        model = Stock
        fields = ['id','item_desc','item_name','item_price','Stock_PIC','Item_Classid','Item_Class','srv_duration']
        read_only_fields = ('item_code',)

class SkillSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    # Item_Class = serializers.CharField(source='Item_Classid.itm_desc',required=False)

    class Meta:
        model = Stock
        fields = ['id','item_desc','item_name','item_price','item_code']
        read_only_fields = ('item_code',)


class TreatmentMasterSerializer(serializers.ModelSerializer): 
    item_class = serializers.CharField(source='Item_Class.itm_desc',required=False)
    emp_name = serializers.SerializerMethodField() 
    room_name = serializers.CharField(source='Trmt_Room_Codeid.displayname',required=False)
    room_img = serializers.CharField(source='Trmt_Room_Codeid.Room_PIC.url',required=False)
    emp_img =  serializers.SerializerMethodField() 
    stock_name = serializers.CharField(source='Item_Codeid.item_desc',required=False)
    site_name = serializers.CharField(source='Site_Codeid.itemsite_desc',required=False)


    def get_emp_img(self, obj):
        ip = get_client_ip(self.context['request'])
        pic_lst = []
        if obj.emp_no:
            for e in obj.emp_no.all():
                if e.emp_pic:
                    pic = str(ip)+str(e.emp_pic.url)
                    pic_lst.append(pic)
        return pic_lst
    
    def get_emp_name(self, obj):
        if obj.emp_no:
            string = ""
            for i in obj.emp_no.all():
                if string == "":
                    string = string + i.emp_name
                elif not string == "":
                    string = string +","+ i.emp_name
            return string
        else:
            return None 

    class Meta:
        model = Treatment_Master
        fields = ['id','PIC','course','item_class','Item_Class','Item_Codeid','stock_name','treatment_date',
        'start_time','end_time','add_duration','duration','site_name','Site_Codeid','site_code','price','treatment_no','times','status',
        'emp_no','emp_name','Trmt_Room_Codeid','room_name','cus_requests','treatment_details','requesttherapist',
        'procedure','products_used','recurring_appointment','room_img','emp_img','sa_transacno','appt_time']

   
    def validate(self, data):
        if 'treatment_no' in data:
            if data['treatment_no'] is None:
                raise serializers.ValidationError("treatment_no Field is required.")
        if 'emp_no' in data:
            if data['emp_no'] is None:
                raise serializers.ValidationError("emp_no Field is required.")

        if 'Trmt_Room_Codeid' in data:
            if data['Trmt_Room_Codeid'] is None:
                raise serializers.ValidationError("Trmt_Room_Code Field is required.")  

        if 'cus_requests' in data:
            if data['cus_requests'] is None:
                raise serializers.ValidationError("cus_requests Field is required.") 

        if 'products_used' in data:
            if data['products_used'] is None:
                raise serializers.ValidationError("products_used Field is required.")

        if 'recurring_appointment' in data:
            if data['recurring_appointment'] is None:
                raise serializers.ValidationError("recurring_appointment Field is required.")
            
        return data

    # def update(self, instance, validated_data):
    #     instance.save()    
    #     return instance      


class StaffsAvailableSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    job_title = serializers.CharField(source='EMP_TYPEid.level_desc',required=False)
    emp_img =  serializers.SerializerMethodField() 
    services =  serializers.SerializerMethodField() 

    def get_emp_img(self, obj):
        ip = get_client_ip(self.context['request'])
        if obj.emp_pic:
            pic = str(ip)+str(obj.emp_pic.url)
        else:
            pic = None    
        return pic

    def get_services(self, obj):
        if obj.skills.all():
            string = ""
            for i in obj.skills.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None        

    class Meta:
        model = Employee
        fields = ['id','emp_name','display_name','emp_img','job_title','services']

class PayGroupSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PayGroup
        fields = ['id','pay_group_code']        

class PaytableSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    pay_group_name = serializers.CharField(source='pay_groupid.pay_group_code',required=False)

    class Meta:
        model = Paytable
        fields = ['id','pay_code','pay_description','pay_groupid','pay_group_name','gt_group']

class PostaudSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    billed_by_name = serializers.CharField(source='billed_by.pw_userlogin',required=False)
    pay_type_name = serializers.CharField(source='pay_typeid.pay_description',required=False)
    pay_group_name = serializers.CharField(source='pay_groupid.pay_group_code',required=False)

    class Meta:
        model = PosTaud
        fields = ['id','sa_date','sa_time','billed_by','billed_by_name','sa_transacno','pay_groupid','pay_group_name',
        'pay_typeid','pay_type_name','pay_desc','pay_tendamt','pay_amt','pay_actamt','ItemSIte_Codeid','itemsite_code','subtotal','tax','discount_amt',
        'sa_transacno','billable_amount','pay_premise','credit_debit','points','prepaid','is_voucher','pay_rem1',
        'pay_rem2','pay_rem3','pay_rem4']

class PoshaudSerializer(serializers.ModelSerializer):
    # billed_by_name = serializers.CharField(source='trans_user_loginid.pw_userlogin',required=False)

    class Meta:
        model = PosHaud
        fields = ['id','sa_custno','sa_custname','sa_date','sa_time']

class PosdaudSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = PosDaud
        fields = ['id','dt_itemdesc','dt_qty','dt_deposit','record_detail_type',
        'dt_status','itemcart','staffs','isfoc','holditemqty','trmt_done_staff_name','dt_combocode']

class PostaudprintSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    pay_type_name = serializers.CharField(source='pay_typeid.pay_description',required=False)

    class Meta:
        model = PosTaud
        fields = ['id','pay_rem1','pay_type_name','pay_amt']

class ItemStatusSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    class Meta:
        model = ItemStatus
        fields = ['id','status_code','status_desc','status_short_desc'] 

class SourceSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Source
        fields = ['id','source_code','source_desc']

class AppointmentPopupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    contact_no = serializers.CharField(source='cust_noid.cust_phone2',required=False)
    cust_dob = serializers.CharField(source='cust_noid.cust_dob',required=False)
   

    class Meta:
        model = Appointment
        fields = ['id','appt_fr_time','appt_to_time','cust_name','cust_refer','cust_noid',
        'contact_no','cust_dob','appt_remark','appt_status',]

class AppointmentResourcesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    room_name = serializers.CharField(source='Room_Codeid.displayname',required=False)
    edit_remark = serializers.SerializerMethodField()
    emp_id = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    add_duration = serializers.SerializerMethodField()
    item_id = serializers.SerializerMethodField()

    def get_edit_remark(self, obj):
        return None 

    def get_emp_id(self, obj):
        return None

    def get_start_time(self, obj):
        return None  

    def get_end_time(self, obj):
        return None 

    def get_add_duration(self, obj):
        return None   

    def get_item_id(self, obj):
        return None             


    class Meta:
        model = Appointment
        fields = ['id','appt_date','cust_name','cust_noid','appt_status','new_remark',
        'sec_status','Room_Codeid','room_name','requesttherapist','edit_remark','emp_id',
        'start_time','end_time','add_duration','item_id']
        extra_kwargs = {'edit_remark': {'required': True},'emp_id': {'required': True}}

    def validate(self, data):
        request = self.context['request']
        if not 'edit_remark' in request.data:
            raise serializers.ValidationError("edit_remark Field is required.")
        else:
            if request.data['edit_remark'] is None: 
                raise serializers.ValidationError("edit_remark Field is required!!")
        
        return data  

class SecuritiesSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='pk',required=False)
    class Meta:
        model = Securities
        fields = ['id', 'level_name', 'level_description', 'level_code']
    
class CustTransferSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    site_id = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['id', 'Site_Codeid', 'site_id']
        extra_kwargs = {'site_id': {'required': True}}

    def validate(self, data):
        request = self.context['request']
        if not 'site_id' in request.data:
            raise serializers.ValidationError("site_id Field is required.")
        else:
            if request.data['site_id'] is None: 
                raise serializers.ValidationError("site_id Field is required!!")
        
        return data     

    
class EmpTransferPerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    site_id = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'emp_code', 'emp_name','site_id'] 
        extra_kwargs = {'site_id': {'required': True}}

    def validate(self, data):
        request = self.context['request']
        if not 'site_id' in request.data:
            raise serializers.ValidationError("site_id Field is required.")
        else:
            if request.data['site_id'] is None: 
                raise serializers.ValidationError("site_id Field is required!!")
        
        return data    

class EmpTransferTempSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    site_id = serializers.SerializerMethodField()
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    hour_id = serializers.SerializerMethodField()


    class Meta:
        model = Employee
        fields = ['id', 'emp_code', 'emp_name','site_id','start_date','end_date','hour_id'] 
        extra_kwargs = {'site_id': {'required': True},'hour_id': {'required': True}}

    def validate(self, data):
        request = self.context['request']
        if not 'site_id' in request.data:
            raise serializers.ValidationError("site_id Field is required.")
        else:
            if request.data['site_id'] is None: 
                raise serializers.ValidationError("site_id Field is required!!")
        
        if not 'hour_id' in request.data:
            raise serializers.ValidationError("hour_id Field is required.")
        else:
            if request.data['hour_id'] is not None:
                if ScheduleHour.objects.filter(id=request.data['hour_id'],itm_isactive=False):
                    raise serializers.ValidationError("ScheduleHour ID Does not exist!!")
                if not ScheduleHour.objects.filter(id=request.data['hour_id'],itm_isactive=True):
                    raise serializers.ValidationError("ScheduleHour ID Does not exist!!")
        
        return data


class EmpInfoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk', required=False)
    # site_id = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['id', 'emp_code', 'emp_name',
                  'emp_phone1','emp_address','Emp_sexesid','emp_race','Emp_nationalityid','Emp_maritalid','Emp_religionid',
                  'emp_emer','emp_emerno','emp_country','emp_remarks','show_in_sales','show_in_appt','show_in_trmt']
        # extra_kwargs = {'site_id': {'required': False}}

    def validate(self, data):
        request = self.context['request']
        # if not 'site_id' in request.data:
        #     raise serializers.ValidationError("site_id Field is required.")
        # else:
        #     if request.data['site_id'] is None:
        #         raise serializers.ValidationError("site_id Field is required!!")

        return data

    def update(self, instance, validated_data):
        instance.emp_phone1 = validated_data.get("emp_phone1", instance.emp_phone1)
        instance.emp_address = validated_data.get("emp_address", instance.emp_address)
        instance.Emp_sexesid = validated_data.get("Emp_sexesid", instance.Emp_sexesid)
        instance.Emp_nationalityid = validated_data.get("Emp_nationalityid", instance.Emp_nationalityid)
        instance.Emp_maritalid = validated_data.get("Emp_maritalid", instance.Emp_maritalid)
        instance.Emp_religionid = validated_data.get("Emp_religionid", instance.Emp_religionid)
        instance.emp_emer = validated_data.get("emp_emer", instance.emp_emer)
        instance.emp_emerno = validated_data.get("emp_emerno", instance.emp_emerno)
        instance.emp_remarks = validated_data.get("emp_remarks", instance.emp_remarks)
        instance.emp_country = validated_data.get("emp_country", instance.emp_country)
        instance.emp_race = validated_data.get("emp_race", instance.emp_race)


        # todo:
        #   country, emergancy person, emergncy contact number
        instance.save()
        return instance


class EmpSitelistSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmpSitelist
        fields = ['id','site_code']

class ScheduleHourSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ScheduleHour
        fields = ['id','itm_code','itm_desc','offday']

class EmpWorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workschedule
        fields = ['id','monday','tuesday','wednesday','thursday','friday','saturday','sunday','emp_code']
        read_only_fields = ('updated_at', 'created_at', 'emp_code')

    def validate(self, data):
        request = self.context['request']
        print("req",data)
        return data


    # def update(self, validated_data):

        # work_schedule = Workschedule.objects.create(emp_code=self.emp.emp_code,
        #                                             monday=validated_data.get('monday'),
        #                                             tuesday=validated_data.get('tuesday'),
        #                                             wednesday=validated_data.get('wednesday'),
        #                                             thursday=validated_data.get('thursday'),
        #                                             friday=validated_data.get('friday'),
        #                                             saturday=validated_data.get('saturday'),
        #                                             sunday=validated_data.get('sunday'),
        #                                             name=self.emp.emp_name,
        #                                             )
    def update(self, instance, validated_data):
        print(validated_data)
        instance.monday = validated_data.get('monday',instance.monday)
        instance.tuesday = validated_data.get('tuesday',instance.tuesday)
        instance.wednesday = validated_data.get('wednesday',instance.tuesday)
        instance.thursday = validated_data.get('thursday',instance.tuesday)
        instance.friday = validated_data.get('friday',instance.tuesday)
        instance.saturday = validated_data.get('saturday',instance.tuesday)
        instance.sunday = validated_data.get('sunday',instance.tuesday)

        instance.save()
        return instance
        # instance.name=self.emp.emp_name,

class CustApptSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Customer
        fields = ['id','cust_name','cust_email','cust_code','cust_nric']


    def to_representation(self, instance):
       
        mapped_object = {'id':instance.pk,'cust_name':instance.cust_name if instance.cust_name else "",
        'cust_phone1': instance.cust_phone2 if instance.cust_phone2 else "",
        'cust_email': instance.cust_email if instance.cust_email else "",
        'cust_code': instance.cust_code if instance.cust_code else "",
        'cust_nric': instance.cust_nric if instance.cust_nric else ""}
        return mapped_object    

   
           
class ApptTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = ApptType
        fields = ['id','appt_type_desc','appt_type_code']


class TmpItemHelperSerializer(serializers.ModelSerializer):

    class Meta:
        model = TmpItemHelper
        fields = ['id','helper_id','helper_name','wp1','appt_fr_time','appt_to_time','add_duration']

class FocReasonSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FocReason
        fields = ['id','foc_reason_ldesc']

class TreatmentApptSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)

    class Meta:
        model = Treatment
        fields = ['id']



class AppointmentSortSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='pk',required=False)
    emp_ids = serializers.SerializerMethodField()

    def get_emp_ids(self, obj):
        return None 

    class Meta:
        model = Employee
        fields = ['id', 'display_name','emp_ids'] 
        extra_kwargs = {'emp_ids': {'required': True}}


class CustomerFormControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerFormControl
        fields = ['id','field_name','display_field_name','visible_in_registration', 'visible_in_listing','visible_in_profile','mandatory']
        read_only_fields = ('field_name','display_field_name')

class RewardPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RewardPolicy
        fields = '__all__'


class RedeemPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = RedeemPolicy
        fields = '__all__'


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'

