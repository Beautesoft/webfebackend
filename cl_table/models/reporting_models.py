from django.db import models
from django.utils import timezone


# for KPI (those models are
class ItemSitelist_Reporting(models.Model):
    itemsite_id = models.BigAutoField(db_column='ItemSite_ID', primary_key=True)  
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=20,unique=True)  
    itemsite_desc = models.CharField(db_column='ItemSite_Desc', max_length=60, blank=True, null=True)  
    itemsite_type = models.CharField(db_column='ItemSite_Type', max_length=10, blank=True, null=True)  
    item_purchasedept = models.CharField(db_column='Item_PurchaseDept', max_length=20, blank=True, null=True)  
    itemsite_address = models.CharField(db_column='ItemSite_Address', max_length=255, blank=True, null=True)  
    itemsite_postcode = models.CharField(db_column='ItemSite_Postcode', max_length=20, blank=True, null=True)  
    itemsite_city = models.CharField(db_column='ItemSite_City', max_length=50, blank=True, null=True)  
    itemsite_state = models.CharField(db_column='ItemSite_State', max_length=50, blank=True, null=True)  
    itemsite_country = models.CharField(db_column='ItemSite_Country', max_length=50, blank=True, null=True)  
    itemsite_phone1 = models.CharField(db_column='ItemSite_Phone1', max_length=50, blank=True, null=True)  
    itemsite_phone2 = models.CharField(db_column='ItemSite_Phone2', max_length=50, blank=True, null=True)  
    itemsite_fax = models.CharField(db_column='ItemSite_Fax', max_length=50, blank=True, null=True)  
    itemsite_email = models.CharField(db_column='ItemSite_Email', max_length=50, blank=True, null=True)  
    itemsite_user = models.CharField(db_column='ItemSite_User', max_length=50, blank=True, null=True)  
    itemsite_date = models.DateTimeField(db_column='ItemSite_Date', blank=True, null=True)  
    itemsite_time = models.DateTimeField(db_column='ItemSite_Time', blank=True, null=True)  
    itemsite_isactive = models.BooleanField(db_column='ItemSite_Isactive')  
    itemsite_refcode = models.CharField(db_column='ITEMSITE_REFCODE', max_length=20, blank=True, null=True)  
    site_group = models.CharField(db_column='Site_Group', max_length=50, blank=True, null=True)  
    site_is_gst = models.BooleanField(db_column='SITE_IS_GST')  
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  
    heartbeat = models.DateTimeField(db_column='HeartBeat', blank=True, null=True)  
    systemlog_mdpl_update = models.BooleanField(db_column='SystemLog_MDPL_Update')  
    ratings = models.CharField(db_column='Ratings', max_length=40, blank=True, null=True)  
    pic_path = models.TextField(db_column='pic_Path', blank=True, null=True)  
    qrcode = models.CharField(db_column='QRCode', max_length=40, blank=True, null=True)  
    is_kpi_show = models.BooleanField(db_column='IS_KPI_SHOW', blank=True, null=True)  
    service_selection = models.BooleanField(db_column='Service Selection', blank=True, null=True)
    service_text = models.BooleanField(db_column='Service Text', blank=True, null=True)
    is_nric = models.BooleanField(blank=True, null=True)
    is_automember = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    itemsite_cityid_id = models.BigIntegerField(db_column='ItemSite_Cityid_id', blank=True, null=True)  
    itemsite_stateid_id = models.BigIntegerField(db_column='ItemSite_Stateid_id', blank=True, null=True)  
    itemsite_countryid_id = models.BigIntegerField(db_column='ItemSite_Countryid_id', blank=True, null=True)  
    itemsite_userid_id = models.BigIntegerField(db_column='ItemSite_Userid_id', blank=True, null=True)  
    site_groupid_id = models.BigIntegerField(db_column='Site_Groupid_id', blank=True, null=True)  
    geolink = models.CharField(max_length=200, blank=True, null=True)
    weekdays_timing = models.CharField(max_length=20, blank=True, null=True)
    weekend_timing = models.CharField(max_length=20, blank=True, null=True)
    holliday_timing = models.CharField(max_length=20, blank=True, null=True)
    picpath = models.CharField(max_length=400, blank=True, null=True)
    sitedbconnectionurl = models.CharField(db_column='siteDbConnectionUrl', max_length=100, blank=True, null=True)  
    closed_on = models.TextField(db_column='Closed_on', blank=True, null=True)  
    owner = models.CharField(db_column='Owner', max_length=300, blank=True, null=True)  
    skills_list = models.CharField(max_length=400, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Item_SiteList'


class Customer_Reporting(models.Model):
    cust_no = models.AutoField(db_column='Cust_No', primary_key=True,)  
    cust_code = models.CharField(db_column='Cust_code',unique=True, max_length=255)  
    join_status = models.BooleanField(db_column='Join_status')  
    cust_joindate = models.DateTimeField(db_column='Cust_JoinDate', blank=True, null=True)  
    cust_name = models.CharField(db_column='Cust_name', max_length=255, blank=True, null=True)  
    cust_ccid = models.FloatField(db_column='Cust_CCID', blank=True, null=True)  
    cust_ctyid = models.FloatField(db_column='Cust_CTYID', blank=True, null=True)  
    exp_status = models.BooleanField(db_column='Exp_Status')  
    cust_expirydate = models.DateTimeField(db_column='Cust_ExpiryDate', blank=True, null=True)  
    cust_birthyear = models.FloatField(db_column='Cust_BirthYear', blank=True, null=True)  
    cust_birthmonth = models.FloatField(db_column='Cust_BirthMonth', blank=True, null=True)  
    cust_birthday = models.FloatField(db_column='Cust_BirthDay', blank=True, null=True)  
    cust_sex = models.CharField(db_column='Cust_Sex', max_length=255, blank=True, null=True)  
    cust_address = models.CharField(db_column='Cust_address', max_length=255, blank=True, null=True)  
    cust_address1 = models.CharField(db_column='Cust_address1', max_length=255, blank=True, null=True)  
    cust_phone1 = models.CharField(db_column='Cust_phone1', max_length=255, blank=True, null=True)  
    cust_pager = models.CharField(db_column='Cust_Pager', max_length=255, blank=True, null=True)  
    cust_phone2 = models.CharField(db_column='Cust_phone2', max_length=255, blank=True, null=True)  
    cust_email = models.CharField(db_column='Cust_email', max_length=255, blank=True, null=True)  
    cust_maillist = models.BooleanField(db_column='Cust_MailList')  
    cust_defaultlist = models.BooleanField(db_column='Cust_DefaultList')  
    cust_blacklist = models.BooleanField(db_column='Cust_BlackList')  
    cust_occupation = models.CharField(db_column='Cust_Occupation', max_length=255, blank=True, null=True)  
    cust_company = models.CharField(db_column='Cust_Company', max_length=255, blank=True, null=True)  
    cust_ofsaddr1 = models.CharField(db_column='Cust_OfsAddr1', max_length=255, blank=True, null=True)  
    cust_ofsaddr2 = models.CharField(db_column='Cust_OfsAddr2', max_length=255, blank=True, null=True)  
    cust_phoneo = models.CharField(db_column='Cust_phoneO', max_length=255, blank=True, null=True)  
    cust_ofsfax = models.CharField(db_column='Cust_OfsFax', max_length=255, blank=True, null=True)  
    cust_remark = models.CharField(db_column='Cust_Remark', max_length=1000, blank=True, null=True)  
    cust_nric = models.CharField(db_column='Cust_nric', max_length=255, blank=True, null=True)  
    cust_credit = models.DecimalField(db_column='Cust_Credit', max_digits=19, decimal_places=4, blank=True, null=True)  
    cust_membershipfee = models.DecimalField(db_column='Cust_MembershipFee', max_digits=19, decimal_places=4, blank=True, null=True)  
    cust_membershipused = models.DecimalField(db_column='Cust_MembershipUsed', max_digits=19, decimal_places=4, blank=True, null=True)  
    cust_membership = models.CharField(db_column='Cust_Membership', max_length=255, blank=True, null=True)  
    cust_activeyn = models.CharField(db_column='Cust_ActiveYN', max_length=255, blank=True, null=True)  
    cust_address2 = models.CharField(db_column='Cust_address2', max_length=255, blank=True, null=True)  
    cust_address3 = models.CharField(db_column='Cust_address3', max_length=255, blank=True, null=True)  
    dob_status = models.BooleanField(db_column='DOB_status')  
    cust_dob = models.DateTimeField(db_column='Cust_DOB', blank=True, null=True)  
    cust_marital = models.CharField(db_column='Cust_marital', max_length=255, blank=True, null=True)  
    cust_race = models.CharField(db_column='Cust_race', max_length=255, blank=True, null=True)  
    cust_sexes = models.CharField(db_column='Cust_sexes', max_length=255, blank=True, null=True)  
    cust_religion = models.CharField(db_column='Cust_religion', max_length=255, blank=True, null=True)  
    cust_nationality = models.CharField(db_column='Cust_nationality', max_length=255, blank=True, null=True)  
    cust_isactive = models.BooleanField(db_column='Cust_isactive')  
    cust_stylist = models.CharField(db_column='Cust_Stylist', max_length=255, blank=True, null=True)  
    cust_stylistname = models.CharField(db_column='Cust_Stylistname', max_length=255, blank=True, null=True)  
    cust_shampoo = models.CharField(db_column='Cust_Shampoo', max_length=255, blank=True, null=True)  
    cust_conditioner = models.CharField(db_column='Cust_Conditioner', max_length=255, blank=True, null=True)  
    cust_prods = models.CharField(db_column='Cust_Prods', max_length=255, blank=True, null=True)  
    cust_pic = models.CharField(db_column='Cust_PIC', max_length=255, blank=True, null=True)  
    cust_vipdiscper = models.CharField(db_column='CUST_VIPDISCPER', max_length=255, blank=True, null=True)  
    cust_vipdisc = models.CharField(db_column='CUST_VIPDISC', max_length=255, blank=True, null=True)  
    cust_city = models.CharField(db_column='Cust_City', max_length=255, blank=True, null=True)  
    cust_interest = models.CharField(db_column='Cust_Interest', max_length=255, blank=True, null=True)  
    cust_salaryrange = models.CharField(db_column='Cust_SalaryRange', max_length=255, blank=True, null=True)  
    cust_postcode = models.CharField(db_column='Cust_PostCode', max_length=255, blank=True, null=True)  
    allergy = models.CharField(db_column='Allergy', max_length=255, blank=True, null=True)  
    cust_address4 = models.CharField(db_column='Cust_address4', max_length=255, blank=True, null=True)  
    mcust_code = models.CharField(db_column='MCust_Code', max_length=50, blank=True, null=True)  
    cust_type = models.CharField(db_column='Cust_Type', max_length=10, blank=True, null=True)  
    voucher_no = models.CharField(db_column='Voucher_No', max_length=50, blank=True, null=True)  
    cust_servicetype = models.CharField(db_column='Cust_ServiceType', max_length=100, blank=True, null=True)  
    cust_class = models.CharField(db_column='Cust_Class', max_length=20, blank=True, null=True)  
    age_range0 = models.BooleanField(db_column='Age_Range0')  
    age_range1 = models.BooleanField(db_column='Age_Range1')  
    age_range2 = models.BooleanField(db_column='Age_Range2')  
    age_range3 = models.BooleanField(db_column='Age_Range3')  
    age_range4 = models.BooleanField(db_column='Age_Range4')  
    cust_source = models.CharField(db_column='Cust_Source', max_length=100, blank=True, null=True)  
    cust_refer = models.CharField(db_column='Cust_Refer', max_length=50, blank=True, null=True)  
    cust_age = models.CharField(db_column='Cust_Age', max_length=50, blank=True, null=True)  
    cust_password = models.CharField(db_column='Cust_Password', max_length=50, blank=True, null=True)  
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  
    modified_date = models.DateTimeField(db_column='Modified_date', blank=True, null=True)  
    cust_cardno = models.CharField(db_column='Cust_CardNo', max_length=20, blank=True, null=True)  
    issue_date = models.DateTimeField(db_column='Issue_Date', blank=True, null=True)  
    cust_point = models.FloatField(db_column='Cust_Point')  
    iscorporate = models.BooleanField(db_column='IsCorporate')  
    cust_linkcode = models.CharField(db_column='Cust_LinkCode', max_length=20, blank=True, null=True)  
    corporatecust = models.CharField(db_column='CorporateCust', max_length=50)  
    dateofreg = models.DateTimeField(db_column='DateofReg', blank=True, null=True)  
    create_logno = models.CharField(db_column='Create_LogNo', max_length=50, blank=True, null=True)  
    create_date = models.DateTimeField(db_column='Create_Date', blank=True, null=True)  
    modify_date = models.DateTimeField(db_column='Modify_Date', blank=True, null=True)  
    modify_logno = models.CharField(db_column='Modify_LogNo', max_length=50, blank=True, null=True)  
    referby = models.CharField(db_column='ReferBy', max_length=60, blank=True, null=True)  
    cust_referby_code = models.CharField(db_column='Cust_ReferBy_Code', max_length=20, blank=True, null=True)  
    cust_state = models.CharField(db_column='Cust_State', max_length=20, blank=True, null=True)  
    cust_country = models.CharField(db_column='Cust_Country', max_length=20, blank=True, null=True)  
    cust_group = models.CharField(db_column='Cust_Group', max_length=20, blank=True, null=True)  
    cust_title = models.CharField(db_column='Cust_Title', max_length=20, blank=True, null=True)  
    cust_pic_b = models.BinaryField(db_column='Cust_Pic_B', blank=True, null=True)  
    cust_group2 = models.CharField(db_column='Cust_Group2', max_length=50, blank=True, null=True)  
    cust_group3 = models.CharField(db_column='Cust_Group3', max_length=50, blank=True, null=True)  
    skin_type = models.CharField(db_column='Skin_Type', max_length=50, blank=True, null=True)  
    product_group = models.CharField(db_column='Product_Group', max_length=50, blank=True, null=True)  
    anniversary = models.DateTimeField(db_column='Anniversary', blank=True, null=True)  
    phone4 = models.CharField(max_length=50, blank=True, null=True)
    staff_service = models.CharField(db_column='Staff_Service', max_length=225, blank=True, null=True)  
    cust_weight = models.CharField(db_column='Cust_Weight', max_length=10, blank=True, null=True)  
    cust_height = models.CharField(db_column='Cust_Height', max_length=10, blank=True, null=True)  
    cust_agegroup = models.CharField(db_column='Cust_AgeGroup', max_length=10, blank=True, null=True)  
    cust_sn = models.CharField(db_column='Cust_SN', max_length=30, blank=True, null=True)  
    cust_language = models.CharField(db_column='Cust_Language', max_length=50, blank=True, null=True)  
    cust_location = models.CharField(db_column='Cust_Location', max_length=50, blank=True, null=True)  
    custclass_changedate = models.DateTimeField(db_column='CustClass_ChangeDate', blank=True, null=True)  
    cardexpiry_date = models.DateTimeField(db_column='CardExpiry_Date', blank=True, null=True)  
    or_key = models.CharField(db_column='OR_KEY', max_length=20, blank=True, null=True)  
    clonecustcode = models.CharField(db_column='CloneCustCode', max_length=200, blank=True, null=True)  
    sgn_block = models.CharField(db_column='Sgn_Block', max_length=255, blank=True, null=True)  
    sgn_unitno = models.CharField(db_column='Sgn_UnitNo', max_length=255, blank=True, null=True)  
    sgn_street = models.CharField(db_column='Sgn_Street', max_length=255, blank=True, null=True)  
    externalvipprofile = models.BooleanField(db_column='ExternalVipProfile')  
    custallowsendsms = models.BooleanField(db_column='CustAllowSendSMS')  
    potential_cust = models.BooleanField()
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  
    cb_trmt = models.FloatField(db_column='CB_TRMT', blank=True, null=True)  
    cb_cn = models.FloatField(db_column='CB_CN', blank=True, null=True)  
    cb_pp = models.FloatField(db_column='CB_PP', blank=True, null=True)  
    cust_used_point = models.FloatField(db_column='Cust_Used_Point', blank=True, null=True)  
    cust_bal_point = models.FloatField(db_column='Cust_Bal_Point', blank=True, null=True)  
    productusedpoints = models.FloatField(db_column='ProductUsedPoints', blank=True, null=True)  
    serviceusedpoints = models.FloatField(db_column='ServiceUsedPoints', blank=True, null=True)  
    productpoints = models.FloatField(db_column='ProductPoints', blank=True, null=True)  
    servicepoints = models.FloatField(db_column='ServicePoints', blank=True, null=True)  
    brandusedpoints = models.FloatField(db_column='BrandUsedPoints', blank=True, null=True)  
    brandpoints = models.FloatField(db_column='BrandPoints', blank=True, null=True)  
    pdpastatus = models.BooleanField(db_column='pdpaStatus', blank=True, null=True)  
    fcmtoken = models.CharField(db_column='FCMToken', max_length=255, blank=True, null=True)  
    nickname = models.CharField(db_column='NickName', max_length=100, blank=True, null=True)  
    modifiedby = models.CharField(db_column='modifiedBy', max_length=100, blank=True, null=True)  
    cust_consultant = models.CharField(max_length=20, blank=True, null=True)
    cust_consultantname = models.CharField(db_column='cust_consultantName', max_length=50, blank=True, null=True)  
    cust_point_value = models.FloatField(db_column='Cust_Point_Value', blank=True, null=True)  
    appt_remark = models.CharField(db_column='Appt_Remark', max_length=1000, blank=True, null=True)  
    testsafe = models.CharField(max_length=20, blank=True, null=True)
    encryptedic = models.BinaryField(db_column='EncryptedIC', blank=True, null=True)  
    encryptedphone = models.BinaryField(db_column='EncryptedPhone', blank=True, null=True)  
    isimported = models.BooleanField(db_column='IsImported', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Customer'


class Employee_Reporting(models.Model):
    emp_no = models.AutoField(db_column='Emp_no', primary_key=True)  
    emp_code = models.CharField(db_column='Emp_code', max_length=20, blank=True, null=True, unique=True)  
    emp_name = models.CharField(db_column='Emp_name', max_length=60, blank=True, null=True)  
    emp_nric = models.CharField(db_column='Emp_nric', max_length=20, blank=True, null=True)  
    emp_sexes = models.CharField(db_column='Emp_sexes', max_length=50, blank=True, null=True)  
    emp_marital = models.CharField(db_column='Emp_marital', max_length=50, blank=True, null=True)  
    emp_race = models.CharField(db_column='Emp_race', max_length=20, blank=True, null=True)  
    emp_religion = models.CharField(db_column='Emp_religion', max_length=20, blank=True, null=True)  
    emp_phone1 = models.CharField(db_column='Emp_phone1', max_length=20, blank=True, null=True)  
    emp_phone2 = models.CharField(db_column='Emp_phone2', max_length=20, blank=True, null=True)  
    emp_nationality = models.CharField(db_column='Emp_nationality', max_length=40, blank=True, null=True)  
    emp_address = models.CharField(db_column='Emp_address', max_length=255, blank=True, null=True)  
    emp_jobpost = models.CharField(db_column='Emp_jobpost', max_length=40, blank=True, null=True)  
    emp_isactive = models.BooleanField(db_column='Emp_isactive')  
    emp_emer = models.CharField(db_column='Emp_emer', max_length=60, blank=True, null=True)  
    emp_emerno = models.CharField(db_column='Emp_emerno', max_length=20, blank=True, null=True)  
    emp_salary = models.FloatField(db_column='Emp_salary', blank=True, null=True)  
    emp_commission_type = models.CharField(db_column='Emp_Commission_Type', max_length=20, blank=True, null=True)  
    emp_dob = models.DateTimeField(db_column='Emp_DOB', blank=True, null=True)  
    emp_joindate = models.DateTimeField(db_column='Emp_JoinDate', blank=True, null=True)  
    emp_email = models.CharField(db_column='Emp_email', max_length=40, blank=True, null=True)  
    emp_socso = models.CharField(db_column='Emp_SOCSO', max_length=20, blank=True, null=True)  
    emp_epf = models.CharField(db_column='Emp_EPF', max_length=20, blank=True, null=True)  
    emp_target = models.FloatField(db_column='Emp_Target', blank=True, null=True)  
    emp_targetbas = models.IntegerField(db_column='Emp_TargetBas', blank=True, null=True)  
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=10, blank=True, null=True)  
    emp_barcode = models.CharField(db_column='Emp_Barcode', max_length=20, blank=True, null=True)  
    emp_barcode2 = models.CharField(db_column='Emp_Barcode2', max_length=20, blank=True, null=True)  
    emp_leaveday = models.CharField(db_column='Emp_LeaveDay', max_length=50, blank=True, null=True)  
    emp_pic = models.TextField(db_column='Emp_PIC', blank=True, null=True)  
    annual_leave = models.IntegerField(db_column='Annual_Leave', blank=True, null=True)  
    marriage_leave = models.IntegerField(db_column='Marriage_Leave', blank=True, null=True)  
    compassiolnate_leave = models.IntegerField(db_column='Compassiolnate_leave', blank=True, null=True)  
    national_service = models.IntegerField(db_column='National_Service', blank=True, null=True)  
    maternity_leave = models.IntegerField(db_column='Maternity_Leave', blank=True, null=True)  
    unpay_leave = models.IntegerField(db_column='Unpay_Leave', blank=True, null=True)  
    mc_leave = models.IntegerField(db_column='MC_Leave', blank=True, null=True)  
    emergency_leave = models.IntegerField(db_column='Emergency_Leave', blank=True, null=True)  
    emp_isboss = models.BooleanField(db_column='Emp_IsBoss', blank=True, null=True)  
    itemsite_refcode = models.CharField(db_column='ITEMSITE_REFCODE', max_length=20, blank=True, null=True)  
    emp_type = models.CharField(db_column='EMP_TYPE', max_length=20, blank=True, null=True)  
    emp_refcode = models.CharField(db_column='EMP_REFCODE', max_length=20, blank=True, null=True)  
    display_name = models.CharField(db_column='Display_Name', max_length=20, blank=True, null=True)  
    show_in_appt = models.BooleanField(db_column='Show_In_Appt')  
    emp_address1 = models.CharField(db_column='Emp_address1', max_length=255, blank=True, null=True)  
    emp_address2 = models.CharField(db_column='Emp_address2', max_length=255, blank=True, null=True)  
    emp_address3 = models.CharField(db_column='Emp_address3', max_length=255, blank=True, null=True)  
    age_range0 = models.BooleanField(db_column='Age_Range0')  
    age_range1 = models.BooleanField(db_column='Age_Range1')  
    age_range2 = models.BooleanField(db_column='Age_Range2')  
    age_range3 = models.BooleanField(db_column='Age_Range3')  
    age_range4 = models.BooleanField(db_column='Age_Range4')  
    type_code = models.CharField(db_column='Type_Code', max_length=20, blank=True, null=True)  
    emp_address4 = models.CharField(db_column='Emp_address4', max_length=255, blank=True, null=True)  
    attn_password = models.CharField(db_column='Attn_Password', max_length=50, blank=True, null=True)  
    max_disc = models.FloatField(db_column='Max_Disc', blank=True, null=True)  
    disc_type = models.BooleanField(db_column='Disc_Type', blank=True, null=True)  
    disc_amt = models.FloatField(db_column='Disc_Amt', blank=True, null=True)  
    ep_allow = models.BooleanField(db_column='EP_Allow', blank=True, null=True)  
    ep_amttype = models.BooleanField(db_column='EP_AmtType', blank=True, null=True)  
    ep_startdate = models.DateTimeField(db_column='EP_StartDate', blank=True, null=True)  
    ep_discamt = models.FloatField(db_column='EP_DiscAmt', blank=True, null=True)  
    ep_amt = models.FloatField(db_column='EP_Amt', blank=True, null=True)  
    bonus_level = models.CharField(db_column='Bonus_Level', max_length=50, blank=True, null=True)  
    bonus_scale_code = models.CharField(db_column='Bonus_Scale_Code', max_length=50, blank=True, null=True)  
    has_product_comm = models.BooleanField(db_column='Has_Product_Comm', blank=True, null=True)  
    ser_level = models.CharField(db_column='Ser_Level', max_length=50, blank=True, null=True)  
    ser_scale_code = models.CharField(db_column='Ser_Scale_Code', max_length=50, blank=True, null=True)  
    treat_level = models.CharField(db_column='Treat_Level', max_length=50, blank=True, null=True)  
    treat_scale_code = models.CharField(db_column='Treat_Scale_code', max_length=50, blank=True, null=True)  
    emp_target_bonus = models.FloatField(db_column='Emp_Target_Bonus', blank=True, null=True)  
    extra_percent = models.FloatField(db_column='Extra_Percent', blank=True, null=True)  
    site_code = models.CharField(db_column='Site_Code', max_length=10, blank=True, null=True)  
    emp_pic_b = models.BinaryField(db_column='Emp_Pic_B', blank=True, null=True)  
    getsms = models.BooleanField(db_column='GetSMS')  
    emp_comm = models.BooleanField(db_column='Emp_Comm', blank=True, null=True)  
    show_in_sales = models.BooleanField(db_column='Show_In_Sales')  
    show_in_trmt = models.BooleanField(db_column='Show_In_Trmt')  
    emp_edit_date = models.DateTimeField(db_column='Emp_Edit_Date', blank=True, null=True)  
    emp_seq_webappt = models.IntegerField(db_column='Emp_Seq_WebAppt', blank=True, null=True)  
    leave_bal = models.IntegerField(db_column='Leave_bal', blank=True, null=True)  
    leave_taken = models.IntegerField(db_column='Leave_taken', blank=True, null=True)  
    employeeapptype = models.CharField(db_column='employeeAppType', max_length=40, blank=True, null=True)  
    skillset = models.CharField(max_length=40, blank=True, null=True)
    fcmtoken = models.TextField(db_column='FCMToken', blank=True, null=True)  
    notificationsetting = models.BooleanField(db_column='notificationSetting', blank=True, null=True)  
    defaultsitecode = models.CharField(db_column='defaultSiteCode', max_length=10, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'Employee'


# class Stock_Reporting(models.Model):
#     item_no = models.AutoField(db_column='Item_no',primary_key=True)  
#     item_code = models.CharField(max_length=20, blank=True, null=True)
#     itm_icid = models.FloatField(db_column='Itm_ICID', blank=True, null=True)  
#     itm_code = models.CharField(db_column='Itm_Code', max_length=20, blank=True, null=True)  
#     item_div = models.CharField(db_column='Item_Div', max_length=20, blank=True, null=True)  
#     item_dept = models.CharField(db_column='Item_Dept', max_length=20, blank=True, null=True)  
#     item_class = models.CharField(db_column='Item_Class', max_length=20, blank=True, null=True)  
#     item_barcode = models.CharField(db_column='Item_Barcode', max_length=20, blank=True, null=True)  
#     onhand_cst = models.FloatField(db_column='ONHAND_CST', blank=True, null=True)  
#     item_margin = models.FloatField(db_column='Item_Margin', blank=True, null=True)  
#     item_isactive = models.BooleanField()
#     item_name = models.CharField(db_column='Item_Name', max_length=40, blank=True, null=True)  
#     item_abbc = models.CharField(db_column='Item_abbc', max_length=60, blank=True, null=True)  
#     item_desc = models.CharField(db_column='Item_Desc', max_length=60, blank=True, null=True)  
#     cost_price = models.DecimalField(db_column='COST_PRICE', max_digits=19, decimal_places=4, blank=True, null=True)  
#     item_price = models.DecimalField(db_column='Item_Price', max_digits=19, decimal_places=4, blank=True, null=True)  
#     onhand_qty = models.FloatField(db_column='ONHAND_QTY', blank=True, null=True)  
#     itm_promotionyn = models.CharField(db_column='Itm_PromotionYN', max_length=20, blank=True, null=True)  
#     itm_disc = models.FloatField(db_column='Itm_Disc', blank=True, null=True)  
#     itm_commission = models.FloatField(db_column='Itm_Commission', blank=True, null=True)  
#     item_type = models.CharField(db_column='Item_Type', max_length=20, blank=True, null=True)  
#     itm_duration = models.FloatField(db_column='Itm_Duration', blank=True, null=True)  
#     item_price2 = models.FloatField(db_column='Item_Price2', blank=True, null=True)  
#     item_price3 = models.FloatField(db_column='Item_Price3', blank=True, null=True)  
#     item_price4 = models.FloatField(db_column='Item_Price4', blank=True, null=True)  
#     item_price5 = models.FloatField(db_column='Item_Price5', blank=True, null=True)  
#     itm_remark = models.CharField(db_column='Itm_Remark', max_length=100, blank=True, null=True)  
#     itm_value = models.CharField(db_column='Itm_Value', max_length=10, blank=True, null=True)  
#     itm_expiredate = models.DateTimeField(db_column='Itm_ExpireDate', blank=True, null=True)  
#     itm_status = models.CharField(db_column='Itm_Status', max_length=10, blank=True, null=True)  
#     item_minqty = models.IntegerField(blank=True, null=True)
#     item_maxqty = models.IntegerField(blank=True, null=True)
#     item_onhandcost = models.CharField(db_column='item_OnHandCost', max_length=20, blank=True, null=True)  
#     item_barcode1 = models.CharField(db_column='item_Barcode1', max_length=20, blank=True, null=True)  
#     item_barcode2 = models.CharField(db_column='item_Barcode2', max_length=20, blank=True, null=True)  
#     item_barcode3 = models.CharField(db_column='item_Barcode3', max_length=20, blank=True, null=True)  
#     item_marginamt = models.FloatField(blank=True, null=True)
#     item_date = models.DateTimeField(blank=True, null=True)
#     item_time = models.DateTimeField(blank=True, null=True)
#     item_moddate = models.DateTimeField(db_column='item_ModDate', blank=True, null=True)  
#     item_modtime = models.DateTimeField(db_column='item_ModTime', blank=True, null=True)  
#     item_createuser = models.CharField(max_length=60, blank=True, null=True)
#     item_supp = models.CharField(max_length=10, blank=True, null=True)
#     item_parentcode = models.CharField(db_column='Item_Parentcode', max_length=20, blank=True, null=True)  
#     item_color = models.CharField(max_length=10, blank=True, null=True)
#     item_sizepack = models.CharField(db_column='item_SizePack', max_length=10, blank=True, null=True)  
#     item_size = models.CharField(db_column='item_Size', max_length=10, blank=True, null=True)  
#     item_season = models.CharField(db_column='item_Season', max_length=10, blank=True, null=True)  
#     item_fabric = models.CharField(max_length=10, blank=True, null=True)
#     item_brand = models.CharField(db_column='item_Brand', max_length=10, blank=True, null=True)  
#     lstpo_ucst = models.FloatField(db_column='LSTPO_UCST', blank=True, null=True)  
#     lstpo_no = models.CharField(db_column='LSTPO_NO', max_length=20, blank=True, null=True)  
#     lstpo_date = models.DateTimeField(db_column='LSTPO_Date', blank=True, null=True)  
#     item_havechild = models.BooleanField(db_column='item_haveChild')  
#     value_applytochild = models.BooleanField(db_column='Value_ApplyToChild')  
#     package_disc = models.FloatField(db_column='Package_Disc', blank=True, null=True)  
#     have_package_disc = models.BooleanField(db_column='Have_Package_Disc')  
#     pic_path = models.CharField(db_column='PIC_Path', max_length=255, blank=True, null=True)  
#     item_foc = models.BooleanField(db_column='Item_FOC')  
#     item_uom = models.CharField(db_column='Item_UOM', max_length=20, blank=True, null=True)  
#     mixbrand = models.BooleanField(db_column='MIXBRAND')  
#     serviceretail = models.BooleanField(db_column='SERVICERETAIL', blank=True, null=True)  
#     item_range = models.CharField(db_column='Item_Range', max_length=20, blank=True, null=True)  
#     commissionable = models.BooleanField(db_column='Commissionable', blank=True, null=True)  
#     trading = models.BooleanField(db_column='Trading', blank=True, null=True)  
#     cust_replenish_days = models.CharField(db_column='Cust_Replenish_Days', max_length=10, blank=True, null=True)  
#     cust_advance_days = models.CharField(db_column='Cust_Advance_Days', max_length=10, blank=True, null=True)  
#     salescomm = models.CharField(db_column='SalesComm', max_length=20, blank=True, null=True)  
#     workcomm = models.CharField(db_column='WorkComm', max_length=20, blank=True, null=True)  
#     reminder_active = models.BooleanField(db_column='Reminder_Active', blank=True, null=True)  
#     disclimit = models.FloatField(db_column='DiscLimit', blank=True, null=True)  
#     disctypeamount = models.BooleanField(db_column='DiscTypeAmount', blank=True, null=True)  
#     autocustdisc = models.BooleanField(db_column='AutoCustDisc')  
#     reorder_active = models.BooleanField(db_column='ReOrder_Active', blank=True, null=True)  
#     reorder_minqty = models.FloatField(db_column='ReOrder_MinQty', blank=True, null=True)  
#     service_expire_active = models.BooleanField(db_column='Service_Expire_Active')  
#     service_expire_month = models.FloatField(db_column='Service_Expire_Month', blank=True, null=True)  
#     treatment_limit_active = models.BooleanField(db_column='Treatment_Limit_Active')  
#     treatment_limit_count = models.FloatField(db_column='Treatment_Limit_Count', blank=True, null=True)  
#     limitservice_flexionly = models.BooleanField(db_column='LimitService_FlexiOnly')  
#     salescommpoints = models.FloatField(db_column='SalesCommPoints', blank=True, null=True)  
#     workcommpoints = models.FloatField(db_column='WorkCommPoints', blank=True, null=True)  
#     item_price_floor = models.FloatField(db_column='Item_Price_Floor', blank=True, null=True)  
#     voucher_value = models.FloatField(db_column='Voucher_Value', blank=True, null=True)  
#     voucher_value_is_amount = models.BooleanField(db_column='Voucher_Value_Is_Amount')  
#     voucher_valid_period = models.CharField(db_column='Voucher_Valid_Period', max_length=20, blank=True, null=True)  
#     prepaid_value = models.FloatField(db_column='Prepaid_Value', blank=True, null=True)  
#     prepaid_sell_amt = models.FloatField(db_column='Prepaid_Sell_Amt', blank=True, null=True)  
#     prepaid_valid_period = models.CharField(db_column='Prepaid_Valid_Period', max_length=20, blank=True, null=True)  
#     membercardnoaccess = models.BooleanField(db_column='MemberCardNoAccess', blank=True, null=True)  
#     rpt_code = models.CharField(db_column='Rpt_Code', max_length=20, blank=True, null=True)  
#     is_gst = models.BooleanField(db_column='IS_GST')  
#     account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  
#     stock_pic_b = models.BinaryField(db_column='Stock_PIC_B', blank=True, null=True)  
#     is_open_prepaid = models.BooleanField(db_column='IS_OPEN_PREPAID')  
#     appt_wd_min = models.FloatField(db_column='Appt_WD_Min', blank=True, null=True)  
#     service_cost = models.FloatField(db_column='Service_Cost', blank=True, null=True)  
#     service_cost_percent = models.BooleanField(db_column='Service_Cost_Percent')  
#     sync_guid = models.CharField(db_column='Sync_GUID', max_length=36)  
#     sync_clientindex = models.IntegerField(db_column='Sync_ClientIndex', blank=True, null=True)  
#     sync_lstupd = models.DateTimeField(db_column='Sync_LstUpd', blank=True, null=True)  
#     account_code_td = models.CharField(db_column='Account_Code_TD', max_length=20, blank=True, null=True)  
#     sync_clientindexstring = models.TextField(db_column='Sync_ClientIndexString', blank=True, null=True)  
#     voucher_isvalid_until_date = models.BooleanField(db_column='Voucher_IsValid_Until_Date')  
#     voucher_valid_until_date = models.DateTimeField(db_column='Voucher_Valid_Until_Date', blank=True, null=True)  
#     workcommholder = models.CharField(max_length=6, blank=True, null=True)
#     equipmentcost = models.FloatField(blank=True, null=True)
#     postatus = models.BooleanField(blank=True, null=True)
#     gst_item_code = models.CharField(db_column='GST_Item_Code', max_length=20, blank=True, null=True)  
#     istnc = models.BooleanField(db_column='isTnc', blank=True, null=True)  
#     consultantcomm = models.BooleanField(db_column='ConsultantComm', blank=True, null=True)  
#     t1_tax_code = models.CharField(db_column='T1_Tax_Code', max_length=20, blank=True, null=True)  
#     is_have_tax = models.BooleanField(db_column='IS_HAVE_TAX')  
#     t2_tax_code = models.CharField(db_column='T2_Tax_Code', max_length=20, blank=True, null=True)  
#     is_allow_foc = models.BooleanField(db_column='IS_ALLOW_FOC')  
#     vilidity_from_date = models.DateTimeField(db_column='Vilidity_From_Date', blank=True, null=True)  
#     vilidity_to_date = models.DateTimeField(db_column='Vilidity_To_date', blank=True, null=True)  
#     vilidity_from_time = models.DateTimeField(db_column='Vilidity_From_Time', blank=True, null=True)  
#     vilidity_to_time = models.DateTimeField(db_column='Vilidity_To_Time', blank=True, null=True)  
#     prepaid_disc_type = models.CharField(db_column='Prepaid_Disc_Type', max_length=20, blank=True, null=True)  
#     prepaid_disc_percent = models.FloatField(db_column='Prepaid_Disc_Percent', blank=True, null=True)  
#     srv_duration = models.FloatField(db_column='Srv_Duration', blank=True, null=True)  
#     voucher_template_name = models.CharField(db_column='Voucher_Template_Name', max_length=50, blank=True, null=True)  
#     autoproportion = models.BooleanField(db_column='AutoProportion')  
#     expiry_days = models.IntegerField(blank=True, null=True)
#     smsprimary = models.IntegerField(blank=True, null=True)
#     smssecondary = models.IntegerField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'Stock'



class PayGroup_Reporting(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  
    pay_group_code = models.CharField(db_column='PAY_GROUP_CODE', max_length=20,unique=True)  
    pay_group_pic = models.BinaryField(db_column='PAY_GROUP_PIC', blank=True, null=True)  
    seq = models.IntegerField(db_column='SEQ', blank=True, null=True)  
    iscreditcard = models.BooleanField(db_column='IsCreditCard', blank=True, null=True)  
    excel_col_seq = models.FloatField(db_column='Excel_Col_Seq', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'PAY_GROUP'



class Paytable_Reporting(models.Model):
    GT_GROUP = [
        ('GT1', 'GT1'),
        ('GT2', 'GT2'),
    ]

    pay_code = models.CharField(max_length=10, blank=True, null=True,unique=True)
    pay_description = models.CharField(max_length=50, blank=True, null=True)
    pay_group =  models.ForeignKey(PayGroup_Reporting,db_column='pay_group',to_field='pay_group_code',db_constraint=False,related_name='pay_table_related', on_delete=models.PROTECT,null=True)
    # pay_group = models.CharField(max_length=15, blank=True, null=True)
    pay_id = models.AutoField(primary_key=True)
    pay_isactive = models.BooleanField()
    gt_group = models.CharField(db_column='GT_Group', max_length=50, blank=True, null=True)  
    rw_usebp = models.BooleanField(db_column='RW_useBP')  
    iscomm = models.BooleanField(db_column='IsComm')  
    show_in_report = models.BooleanField(db_column='Show_In_Report')  
    bank_charges = models.FloatField(db_column='Bank_Charges', default=0)
    eps = models.FloatField(db_column='EPS', blank=True, null=True)  
    sequence = models.IntegerField(db_column='Sequence', blank=True, null=True)  
    voucher_payment_control = models.BooleanField(db_column='Voucher_Payment_Control')  
    pay_type_pic = models.BinaryField(db_column='PAY_TYPE_PIC', blank=True, null=True)  
    pay_is_gst = models.BooleanField(db_column='PAY_IS_GST')  
    creditcardcharges = models.DecimalField(db_column='CreditCardCharges', max_digits=18, decimal_places=2)  
    onlinepaymentcharges = models.DecimalField(db_column='OnlinePaymentCharges', max_digits=18, decimal_places=2)  
    iscreditcard = models.BooleanField(db_column='IsCreditCard', blank=True, null=True)  
    isonlinepayment = models.BooleanField(db_column='IsOnlinePayment', blank=True, null=True)  
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  
    account_mapping = models.BooleanField(db_column='Account_Mapping', blank=True, null=True)  
    open_cashdrawer = models.BooleanField(db_column='Open_CashDrawer')  
    isvoucher_extvoucher = models.BooleanField(db_column='IsVoucher_ExtVoucher')  
    iscustapptpromo = models.BooleanField(db_column='IsCustApptPromo')  
    excel_col_seq = models.FloatField(db_column='Excel_Col_Seq', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'PAYTABLE'



class PosHaud_Reporting(models.Model):
    SA_STATUS = [
        ('SA', 'SA'), #SA-Sales
        ('VT', 'VT'), # VT-Void Transaction
        ('SU', 'SU'), # SU-Suspend
    ]

    SA_TRANSACNO_TYPE = [
        ('Receipt', 'Receipt'),
        ('Redeem Service', 'Redeem Service'),
        ('Non Sales', 'Non Sales'),
        ('Void Transaction','Void Transaction')
    ]

    mac_code = models.CharField(max_length=15, blank=True, null=True)
    cas_name = models.CharField(max_length=60, blank=True, null=True)
    cas_logno = models.CharField( max_length=20)
    sa_transacno = models.CharField(max_length=20,unique=True)
    sa_date = models.DateTimeField(blank=True, null=True, default=timezone.now, editable=False)
    sa_time = models.DateTimeField(blank=True, null=True, default=timezone.now, editable=False)
    sa_postdate = models.DateTimeField(blank=True, null=True)
    sa_status = models.CharField(max_length=5, blank=True, null=True,choices=SA_STATUS)
    sa_remark = models.CharField(max_length=50, blank=True, null=True)
    sa_totamt = models.FloatField(blank=True, null=True)
    sa_totqty = models.IntegerField(db_column='sa_totQty', blank=True, null=True)  
    sa_totdisc = models.FloatField(blank=True, null=True)
    sa_totgst = models.FloatField(blank=True, null=True)
    sa_totservice = models.FloatField(blank=True, null=True)
    sa_amtret = models.FloatField(blank=True, null=True)
    sa_staffno = models.ForeignKey(Employee_Reporting,to_field='emp_code',db_column='sa_staffno', on_delete=models.PROTECT, null=True,db_constraint=False,related_name='pos_haud_related')
    # sa_staffno = models.CharField(max_length=100, blank=True, null=True)
    sa_staffname = models.CharField(max_length=600, blank=True, null=True)
    sa_custno = models.ForeignKey(Customer_Reporting,to_field='cust_code',db_column='sa_custno', on_delete=models.PROTECT,  null=True,db_constraint=False,related_name='pos_haud_related')
    # sa_custno = models.CharField(max_length=20, null=True)
    sa_custname = models.CharField(max_length=60, blank=True, null=True)
    sa_reason = models.IntegerField(db_column='sa_Reason', blank=True, null=True)  
    sa_discuser = models.CharField(db_column='sa_DiscUser', max_length=50, blank=True, null=True)  
    sa_discno = models.CharField(max_length=10, blank=True, null=True)
    sa_discdesc = models.CharField(max_length=20, blank=True, null=True)
    sa_discvalue = models.FloatField(blank=True, null=True)
    sa_discamt = models.FloatField(blank=True, null=True)
    sa_disctotal = models.FloatField(db_column='sa_discTotal', blank=True, null=True)  
    itemsite_code  = models.ForeignKey(ItemSitelist_Reporting,db_column='ItemSite_Code',to_field='itemsite_code', on_delete=models.PROTECT, null=True, db_constraint=False,related_name='pos_haud_related')
    # itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=10, null=True)  
    sa_cardno = models.CharField(db_column='sa_CardNo', max_length=20, blank=True, null=True)  
    seat_no = models.CharField(db_column='Seat_No', max_length=10, blank=True, null=True)  
    sa_depositamt = models.FloatField(db_column='sa_depositAmt', blank=True, null=True)  
    sa_chargeamt = models.FloatField(db_column='sa_chargeAmt', blank=True, null=True)  
    isvoid = models.BooleanField(db_column='IsVoid')  
    void_refno = models.CharField(db_column='Void_RefNo', max_length=20, blank=True, null=True)  
    payment_remarks = models.CharField(db_column='Payment_Remarks', max_length=100, blank=True, null=True)  
    next_payment = models.CharField(db_column='Next_Payment', max_length=20, blank=True, null=True)  
    next_appt = models.CharField(db_column='Next_Appt', max_length=20, blank=True, null=True)  
    sa_transacamt = models.FloatField(db_column='sa_TransacAmt', blank=True, null=True)  
    appt_time = models.CharField(db_column='Appt_Time', max_length=10, blank=True, null=True)  
    hold_item = models.BooleanField(db_column='Hold_Item', blank=True, null=True)  
    sa_discecard = models.FloatField(db_column='sa_discECard', blank=True, null=True)  
    holditemqty = models.IntegerField(db_column='HoldItemQty')  
    walkin = models.BooleanField(db_column='WalkIn')  
    cust_sig = models.BinaryField(db_column='Cust_Sig', blank=True, null=True)  
    sa_round = models.FloatField(db_column='sa_Round', blank=True, null=True)  
    balance_point = models.FloatField(db_column='Balance_Point', blank=True, null=True)  
    total_outstanding = models.FloatField(db_column='Total_Outstanding', blank=True, null=True)  
    total_itemhold_qty = models.FloatField(db_column='Total_ItemHold_Qty', blank=True, null=True)  
    total_prepaid_amt = models.FloatField(db_column='Total_Prepaid_Amt', blank=True, null=True)  
    total_voucher_avalable = models.FloatField(db_column='Total_Voucher_Avalable', blank=True, null=True)  
    total_course_summary = models.CharField(db_column='Total_Course_Summary', max_length=20, blank=True, null=True)  
    total_cn_amt = models.FloatField(db_column='Total_CN_Amt', blank=True, null=True)  
    previous_pts = models.FloatField(db_column='Previous_pts', blank=True, null=True)  
    today_pts = models.FloatField(db_column='Today_pts', blank=True, null=True)  
    total_balance_pts = models.FloatField(db_column='Total_Balance_pts', blank=True, null=True)  
    trans_user_login = models.ForeignKey('cl_table.Fmspw',db_column='Trans_User_Login',to_field='pw_userlogin', on_delete=models.PROTECT,null=True, db_constraint=False,related_name='pos_haud_related')
    # trans_user_login = models.CharField(db_column='Trans_User_Login', max_length=20, blank=True, null=True)  
    sync_lstupd = models.DateTimeField(db_column='Sync_LstUpd')  
    sync_clientindex = models.IntegerField(db_column='Sync_ClientIndex', blank=True, null=True)  
    sync_guid = models.CharField(db_column='Sync_GUID', max_length=36)  
    sa_transacno_ref = models.CharField(db_column='SA_TransacNo_Ref', max_length=20, blank=True, null=True)  
    sa_transacno_type = models.CharField(db_column='SA_TransacNo_Type', max_length=20, choices=SA_TRANSACNO_TYPE,blank=True, null=True)  
    cust_sig_path = models.CharField(db_column='Cust_Sig_Path', max_length=250, blank=True, null=True)  
    trans_reason = models.CharField(db_column='Trans_Reason', max_length=200, blank=True, null=True)  
    trans_remark = models.CharField(db_column='Trans_Remark', max_length=200, blank=True, null=True)  
    trans_rw_point_ratio = models.FloatField(db_column='Trans_RW_Point_Ratio', blank=True, null=True)  
    sa_trans_do_no = models.CharField(db_column='SA_Trans_DO_No', max_length=20, blank=True, null=True)  
    sa_transacno_title = models.CharField(db_column='SA_TransacNo_Title', max_length=50, blank=True, null=True)  
    sync_clientindexstring = models.TextField(db_column='Sync_ClientIndexString', blank=True, null=True)  
    issuestrans_user_login = models.CharField(db_column='IssuesTrans_User_Login', max_length=20, blank=True, null=True)  
    transignurl = models.TextField(db_column='tranSignUrl', blank=True, null=True)  
    onlinepurchase = models.BooleanField(db_column='onlinePurchase', blank=True, null=True)  
    smsout = models.BooleanField(db_column='smsOut', blank=True, null=True)  
    emailout = models.BooleanField(db_column='emailOut', blank=True, null=True)  
    smstdout = models.BooleanField(db_column='smsTDOut', blank=True, null=True)  
    smsinvoiceout = models.BooleanField(db_column='smsInvoiceOut', blank=True, null=True)  
    emailtdout = models.BooleanField(db_column='emailTDOut', blank=True, null=True)  
    emailinvoiceout = models.BooleanField(db_column='emailInvoiceOut', blank=True, null=True)  
    paymentdone = models.BooleanField(db_column='paymentDone', blank=True, null=True)  
    smspaymentout = models.BooleanField(db_column='smsPaymentOut', blank=True, null=True)  
    emailpaymentout = models.BooleanField(db_column='emailPaymentOut', blank=True, null=True)  
    prevdate = models.DateTimeField(db_column='PrevDate', blank=True, null=True)  
    loginuser = models.CharField(db_column='loginUser', max_length=200, blank=True, null=True)  
    updateddatetime = models.DateTimeField(db_column='updatedDateTime', blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'pos_haud'
        unique_together = (('cas_logno', 'sa_transacno', 'sa_custno', 'itemsite_code'),)

class PosTaud_Reporting(models.Model):
    pay_no = models.AutoField(primary_key=True)
    mac_code = models.CharField(max_length=15, blank=True, null=True)
    sa_date = models.DateTimeField(blank=True, null=True)
    sa_time = models.DateTimeField(blank=True, null=True)
    sa_transacno = models.ForeignKey(PosHaud_Reporting,db_column='sa_transacno',to_field='sa_transacno',db_constraint=False,related_name='pos_taud_related', on_delete=models.PROTECT, null=True)
    # sa_transacno = models.CharField(max_length=20)
    cas_logno = models.CharField(max_length=20)
    pay_group = models.ForeignKey(PayGroup_Reporting,db_column='pay_group',to_field='pay_group_code',db_constraint=False,related_name='pos_taud_related', on_delete=models.PROTECT, null=True)
    # pay_group = models.CharField(max_length=40, blank=True, null=True)
    pay_type = models.ForeignKey(Paytable_Reporting,db_column='pay_type',to_field='pay_code',db_constraint=False,related_name='pos_taud_related', on_delete=models.PROTECT,null=True)
    # pay_type = models.CharField(max_length=30, blank=True, null=True)
    pay_desc = models.CharField(db_column='pay_Desc', max_length=200, blank=True, null=True)  
    pay_tendamt = models.FloatField(blank=True, null=True)
    pay_tendrate = models.FloatField(blank=True, null=True)
    pay_tendcurr = models.CharField(max_length=10, blank=True, null=True)
    pay_amt = models.FloatField(blank=True, null=True)
    pay_amtrate = models.FloatField(blank=True, null=True)
    pay_amtcurr = models.CharField(max_length=10, blank=True, null=True)
    pay_rem1 = models.CharField(max_length=200, blank=True, null=True)
    pay_rem2 = models.CharField(max_length=200, blank=True, null=True)
    pay_rem3 = models.CharField(max_length=200, blank=True, null=True)
    pay_rem4 = models.CharField(max_length=200, blank=True, null=True)
    pay_status = models.BooleanField()
    pay_actamt = models.FloatField(blank=True, null=True)
    itemsite_code = models.ForeignKey(ItemSitelist_Reporting,db_column='ItemSIte_Code',to_field='itemsite_code',db_constraint=False,related_name='pos_taud_related', on_delete=models.PROTECT, null=True)
    # itemsite_code = models.CharField(db_column='ItemSIte_Code', max_length=10)  
    paychange = models.FloatField(db_column='PayChange', blank=True, null=True)  
    dt_lineno = models.IntegerField()
    pay_gst_amt_collect = models.FloatField(db_column='Pay_GST_Amt_Collect', blank=True, null=True)  
    pay_gst = models.FloatField(db_column='PAY_GST', blank=True, null=True)  
    posdaudlineno = models.CharField(db_column='POSDAUDLineNo', max_length=4000, blank=True, null=True)  
    posdaudlineamountassign = models.CharField(db_column='posdaudLineAmountAssign', max_length=4000, blank=True, null=True)  
    posdaudlineamountused = models.FloatField(db_column='posdaudLineAmountUsed', blank=True, null=True)  
    onlinepurchase = models.BooleanField(db_column='onlinePurchase', blank=True, null=True)  
    voucher_name = models.CharField(db_column='Voucher_Name', max_length=100, blank=True, null=True)  
    paypal_id = models.CharField(db_column='paypal_Id', max_length=250, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'pos_taud'
        unique_together = (('sa_transacno', 'cas_logno', 'itemsite_code', 'dt_lineno'),)


class PosDaud_Reporting(models.Model):

    DT_STATUS = [
        ('SA', 'SA'), # SA-Sales
        ('VT', 'VT'), # VT-Void Transaction
        ('SU', 'SU'), # SU-Suspend
        ('EX', 'EX'),
    ]

    RECORD_DETAIL_TYPE = [
        ('SERVICE', 'SERVICE'),
        ('PRODUCT', 'PRODUCT'),
        ('PREPAID', 'PREPAID'),
        ('VOUCHER', 'VOUCHER'),
        ('PACKAGE', 'PACKAGE'),
        ('TD', 'TD'),
        ('TP SERVICE', 'TP SERVICE'),
        ('TP PRODUCT', 'TP PRODUCT'),
        ('TP PREPAID', 'TP PREPAID'),
    ]

    dt_no = models.AutoField(primary_key=True)
    mac_code = models.CharField(max_length=15, blank=True, null=True)
    sa_date = models.DateTimeField(blank=True, null=True)
    sa_time = models.DateTimeField(blank=True, null=True)
    cas_logno = models.CharField(max_length=20)
    sa_transacno = models.ForeignKey(PosHaud_Reporting,db_column='sa_transacno',to_field='sa_transacno',db_constraint=False,related_name='pos_daud_related', on_delete=models.PROTECT, null=True)
    # sa_transacno = models.CharField(max_length=20)
    dt_status = models.CharField(max_length=5, blank=True,choices=DT_STATUS, null=True)
    # dt_itemno = models.ForeignKey(Stock_Reporting,to_field='item_code',db_column='dt_itemno',related_name='pos_daud_related',db_constraint=False, on_delete=models.CASCADE,  null=True)
    dt_itemno = models.CharField(max_length=20, blank=True, null=True) # FK to Stock.item_code + '0000' WTF
    dt_itemdesc = models.CharField(max_length=200)
    dt_price = models.FloatField(blank=True, null=True)
    dt_promoprice = models.FloatField(db_column='dt_PromoPrice', blank=True, null=True)  
    dt_amt = models.FloatField(blank=True, null=True)
    dt_qty = models.IntegerField(blank=True, null=True)
    dt_discamt = models.FloatField(db_column='dt_discAmt', blank=True, null=True)  
    dt_discpercent = models.FloatField(db_column='dt_discPercent', blank=True, null=True)  
    dt_discdesc = models.CharField(db_column='dt_discDesc', max_length=20, blank=True, null=True)  
    dt_discno = models.CharField(max_length=10, blank=True, null=True)
    dt_remark = models.CharField(max_length=60, blank=True, null=True)
    dt_staffno = models.ForeignKey(Employee_Reporting,to_field='emp_code',db_column='dt_staffno',related_name='pos_daud_related',db_constraint=False,  on_delete=models.PROTECT,  null=True)
    # dt_staffno = models.CharField(db_column='dt_Staffno', max_length=100, blank=True, null=True)  
    dt_staffname = models.CharField(db_column='dt_StaffName', max_length=600, blank=True, null=True)  
    dt_reason = models.IntegerField(db_column='dt_Reason', blank=True, null=True)  
    dt_discuser = models.CharField(db_column='dt_DiscUser', max_length=50, blank=True, null=True)  
    dt_combocode = models.CharField(db_column='dt_ComboCode', max_length=20, blank=True, null=True)  
    itemsite_code = models.ForeignKey(ItemSitelist_Reporting,db_column='ItemSIte_Code',to_field='itemsite_code',db_constraint=False,related_name='pos_daud_related', on_delete=models.PROTECT,  null=True)
    # itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=10)  
    dt_lineno = models.IntegerField(db_column='dt_LineNo')  
    dt_stockupdate = models.CharField(db_column='dt_StockUpdate', max_length=20, blank=True, null=True)  
    dt_stockremark = models.CharField(db_column='dt_StockRemark', max_length=200, blank=True, null=True)  
    dt_uom = models.CharField(db_column='dt_UOM', max_length=20, blank=True, null=True)  
    isfoc = models.BooleanField(db_column='IsFoc')  
    item_remarks = models.CharField(db_column='Item_Remarks', max_length=500, blank=True, null=True)  
    next_payment = models.CharField(db_column='Next_Payment', max_length=20, blank=True, null=True)  
    next_appt = models.CharField(db_column='Next_Appt', max_length=20, blank=True, null=True)  
    dt_transacamt = models.FloatField(db_column='dt_TransacAmt', blank=True, null=True)  
    dt_deposit = models.FloatField(blank=True, null=True)
    appt_time = models.CharField(db_column='Appt_Time', max_length=10, blank=True, null=True)  # Should be convert to time field
    hold_item_out = models.BooleanField(db_column='Hold_Item_Out')  
    issue_date = models.DateTimeField(db_column='Issue_Date', blank=True, null=True)  
    hold_item = models.BooleanField(db_column='Hold_Item')  
    holditemqty = models.IntegerField(db_column='HoldItemQty', blank=True, null=True)  
    st_ref_treatmentcode = models.CharField(db_column='ST_Ref_TreatmentCode', max_length=20)  
    item_status_code = models.CharField(db_column='Item_Status_Code', max_length=50, blank=True, null=True)  
    first_trmt_done = models.BooleanField(db_column='First_Trmt_Done')  
    first_trmt_done_staff_code = models.CharField(db_column='First_Trmt_Done_Staff_Code', max_length=200, blank=True, null=True)  
    first_trmt_done_staff_name = models.CharField(db_column='First_Trmt_Done_Staff_Name', max_length=200, blank=True, null=True)  
    record_detail_type = models.CharField(db_column='Record_Detail_Type', max_length=50, blank=True, null=True)  
    trmt_done_staff_code = models.CharField(db_column='Trmt_Done_Staff_Code', max_length=200, blank=True, null=True)  
    trmt_done_staff_name = models.CharField(db_column='Trmt_Done_Staff_Name', max_length=200, blank=True, null=True)  
    trmt_done_id = models.CharField(db_column='Trmt_Done_ID', max_length=50, blank=True, null=True)  
    trmt_done_type = models.CharField(db_column='Trmt_Done_Type', max_length=50, blank=True, null=True)  
    topup_service_trmt_code = models.CharField(db_column='TopUp_Service_Trmt_Code', max_length=50, blank=True, null=True)  
    topup_product_treat_code = models.CharField(db_column='TopUp_Product_Treat_Code', max_length=50, blank=True, null=True)  
    topup_prepaid_trans_code = models.CharField(db_column='TopUp_Prepaid_Trans_Code', max_length=50, blank=True, null=True)  
    topup_prepaid_type_code = models.CharField(db_column='TopUp_Prepaid_Type_Code', max_length=50, blank=True, null=True)  
    voucher_link_cust = models.BooleanField(db_column='Voucher_Link_Cust')  
    voucher_no = models.CharField(db_column='Voucher_No', max_length=50, blank=True, null=True)  
    update_prepaid_bonus = models.BooleanField(db_column='Update_Prepaid_Bonus')  
    deduct_commission = models.BooleanField(db_column='Deduct_Commission')  
    deduct_comm_refline = models.IntegerField(db_column='Deduct_comm_refLine', blank=True, null=True)  
    gst_amt_collect = models.FloatField(db_column='GST_Amt_Collect', blank=True, null=True)  
    topup_prepaid_pos_trans_lineno = models.IntegerField(db_column='TopUp_Prepaid_POS_Trans_LineNo', blank=True, null=True)  
    open_pp_uid_ref = models.CharField(db_column='OPEN_PP_UID_REF', max_length=50, blank=True, null=True)  
    compound_code = models.CharField(db_column='COMPOUND_CODE', max_length=50, blank=True, null=True)  
    topup_outstanding = models.FloatField(db_column='TopUp_Outstanding', blank=True, null=True)  
    earnedpoints = models.DecimalField(db_column='earnedPoints', max_digits=18, decimal_places=2, blank=True, null=True)  
    earnedtype = models.CharField(db_column='earnedType', max_length=100, blank=True, null=True)  
    redeempoints = models.DecimalField(db_column='redeemPoints', max_digits=18, decimal_places=2, blank=True, null=True)  
    redeemtype = models.CharField(db_column='redeemType', max_length=100, blank=True, null=True)  
    t1_tax_code = models.CharField(db_column='T1_Tax_Code', max_length=20, blank=True, null=True)  
    t1_tax_amt = models.FloatField(db_column='T1_Tax_Amt', blank=True, null=True)  
    t2_tax_code = models.CharField(db_column='T2_Tax_Code', max_length=20, blank=True, null=True)  
    t2_tax_amt = models.FloatField(db_column='T2_Tax_Amt', blank=True, null=True)  
    dt_grossamt = models.CharField(db_column='dt_GrossAmt', max_length=20, blank=True, null=True)  

    class Meta:
        managed = False
        db_table = 'pos_daud'
        unique_together = (('cas_logno', 'sa_transacno', 'dt_itemdesc', 'itemsite_code', 'dt_lineno', 'st_ref_treatmentcode'),)


class Multistaff_Reporting(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.ForeignKey(PosHaud_Reporting,db_column='sa_transacno',to_field='sa_transacno',db_constraint=False,related_name='multistaff_related', on_delete=models.PROTECT, null=True)
    item_code = models.CharField(db_column='Item_Code', max_length=20)  # Field name made lowercase.
    emp_code = models.ForeignKey(Employee_Reporting,to_field='emp_code',db_column='emp_code', on_delete=models.PROTECT, null=True,db_constraint=False,related_name='multistaff_related')
    ratio = models.FloatField(db_column='Ratio')  # Field name made lowercase.
    salesamt = models.FloatField(db_column='SalesAmt')  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=20)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete')  # Field name made lowercase.
    role = models.CharField(db_column='Role', max_length=50)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='Dt_LineNo')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'multistaff'
        unique_together = (('sa_transacno', 'item_code', 'emp_code', 'role', 'dt_lineno'),)


class Stock_Reporting(models.Model):
    item_no = models.AutoField(db_column='Item_no',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(max_length=20,unique=True, blank=True, null=True)
    itm_icid = models.FloatField(db_column='Itm_ICID', blank=True, null=True)  # Field name made lowercase.
    itm_code = models.CharField(db_column='Itm_Code', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    item_div = models.CharField(db_column='Item_Div', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    item_dept = models.CharField(db_column='Item_Dept', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    item_class = models.CharField(db_column='Item_Class', max_length=20, blank=True,
                                  null=True)  # Field name made lowercase.
    item_barcode = models.CharField(db_column='Item_Barcode', max_length=20, blank=True,
                                    null=True)  # Field name made lowercase.
    onhand_cst = models.FloatField(db_column='ONHAND_CST', blank=True, null=True)  # Field name made lowercase.
    item_margin = models.FloatField(db_column='Item_Margin', blank=True, null=True)  # Field name made lowercase.
    item_isactive = models.BooleanField()
    item_name = models.CharField(db_column='Item_Name', max_length=40, blank=True,
                                 null=True)  # Field name made lowercase.
    item_abbc = models.CharField(db_column='Item_abbc', max_length=60, blank=True,
                                 null=True)  # Field name made lowercase.
    item_desc = models.CharField(db_column='Item_Desc', max_length=60, blank=True,
                                 null=True)  # Field name made lowercase.
    cost_price = models.DecimalField(db_column='COST_PRICE', max_digits=19, decimal_places=4, blank=True,
                                     null=True)  # Field name made lowercase.
    item_price = models.DecimalField(db_column='Item_Price', max_digits=19, decimal_places=4, blank=True,
                                     null=True)  # Field name made lowercase.
    onhand_qty = models.FloatField(db_column='ONHAND_QTY', blank=True, null=True)  # Field name made lowercase.
    itm_promotionyn = models.CharField(db_column='Itm_PromotionYN', max_length=20, blank=True,
                                       null=True)  # Field name made lowercase.
    itm_disc = models.FloatField(db_column='Itm_Disc', blank=True, null=True)  # Field name made lowercase.
    itm_commission = models.FloatField(db_column='Itm_Commission', blank=True, null=True)  # Field name made lowercase.
    item_type = models.CharField(db_column='Item_Type', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    itm_duration = models.FloatField(db_column='Itm_Duration', blank=True, null=True)  # Field name made lowercase.
    item_price2 = models.FloatField(db_column='Item_Price2', blank=True, null=True)  # Field name made lowercase.
    item_price3 = models.FloatField(db_column='Item_Price3', blank=True, null=True)  # Field name made lowercase.
    item_price4 = models.FloatField(db_column='Item_Price4', blank=True, null=True)  # Field name made lowercase.
    item_price5 = models.FloatField(db_column='Item_Price5', blank=True, null=True)  # Field name made lowercase.
    itm_remark = models.CharField(db_column='Itm_Remark', max_length=100, blank=True,
                                  null=True)  # Field name made lowercase.
    itm_value = models.CharField(db_column='Itm_Value', max_length=10, blank=True,
                                 null=True)  # Field name made lowercase.
    itm_expiredate = models.DateTimeField(db_column='Itm_ExpireDate', blank=True,
                                          null=True)  # Field name made lowercase.
    itm_status = models.CharField(db_column='Itm_Status', max_length=10, blank=True,
                                  null=True)  # Field name made lowercase.
    item_minqty = models.IntegerField(blank=True, null=True)
    item_maxqty = models.IntegerField(blank=True, null=True)
    item_onhandcost = models.CharField(db_column='item_OnHandCost', max_length=20, blank=True,
                                       null=True)  # Field name made lowercase.
    item_barcode1 = models.CharField(db_column='item_Barcode1', max_length=20, blank=True,
                                     null=True)  # Field name made lowercase.
    item_barcode2 = models.CharField(db_column='item_Barcode2', max_length=20, blank=True,
                                     null=True)  # Field name made lowercase.
    item_barcode3 = models.CharField(db_column='item_Barcode3', max_length=20, blank=True,
                                     null=True)  # Field name made lowercase.
    item_marginamt = models.FloatField(blank=True, null=True)
    item_date = models.DateTimeField(blank=True, null=True)
    item_time = models.DateTimeField(blank=True, null=True)
    item_moddate = models.DateTimeField(db_column='item_ModDate', blank=True, null=True)  # Field name made lowercase.
    item_modtime = models.DateTimeField(db_column='item_ModTime', blank=True, null=True)  # Field name made lowercase.
    item_createuser = models.CharField(max_length=60, blank=True, null=True)
    item_supp = models.CharField(max_length=10, blank=True, null=True)
    item_parentcode = models.CharField(db_column='Item_Parentcode', max_length=20, blank=True,
                                       null=True)  # Field name made lowercase.
    item_color = models.CharField(max_length=10, blank=True, null=True)
    item_sizepack = models.CharField(db_column='item_SizePack', max_length=10, blank=True,
                                     null=True)  # Field name made lowercase.
    item_size = models.CharField(db_column='item_Size', max_length=10, blank=True,
                                 null=True)  # Field name made lowercase.
    item_season = models.CharField(db_column='item_Season', max_length=10, blank=True,
                                   null=True)  # Field name made lowercase.
    item_fabric = models.CharField(max_length=10, blank=True, null=True)
    item_brand = models.CharField(db_column='item_Brand', max_length=10, blank=True,
                                  null=True)  # Field name made lowercase.
    lstpo_ucst = models.FloatField(db_column='LSTPO_UCST', blank=True, null=True)  # Field name made lowercase.
    lstpo_no = models.CharField(db_column='LSTPO_NO', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    lstpo_date = models.DateTimeField(db_column='LSTPO_Date', blank=True, null=True)  # Field name made lowercase.
    item_havechild = models.BooleanField(db_column='item_haveChild')  # Field name made lowercase.
    value_applytochild = models.BooleanField(db_column='Value_ApplyToChild')  # Field name made lowercase.
    package_disc = models.FloatField(db_column='Package_Disc', blank=True, null=True)  # Field name made lowercase.
    have_package_disc = models.BooleanField(db_column='Have_Package_Disc')  # Field name made lowercase.
    pic_path = models.CharField(db_column='PIC_Path', max_length=255, blank=True,
                                null=True)  # Field name made lowercase.
    item_foc = models.BooleanField(db_column='Item_FOC')  # Field name made lowercase.
    item_uom = models.CharField(db_column='Item_UOM', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    mixbrand = models.BooleanField(db_column='MIXBRAND')  # Field name made lowercase.
    serviceretail = models.BooleanField(db_column='SERVICERETAIL', blank=True, null=True)  # Field name made lowercase.
    item_range = models.CharField(db_column='Item_Range', max_length=20, blank=True,
                                  null=True)  # Field name made lowercase.
    commissionable = models.BooleanField(db_column='Commissionable', blank=True,
                                         null=True)  # Field name made lowercase.
    trading = models.BooleanField(db_column='Trading', blank=True, null=True)  # Field name made lowercase.
    cust_replenish_days = models.CharField(db_column='Cust_Replenish_Days', max_length=10, blank=True,
                                           null=True)  # Field name made lowercase.
    cust_advance_days = models.CharField(db_column='Cust_Advance_Days', max_length=10, blank=True,
                                         null=True)  # Field name made lowercase.
    salescomm = models.CharField(db_column='SalesComm', max_length=20, blank=True,
                                 null=True)  # Field name made lowercase.
    workcomm = models.CharField(db_column='WorkComm', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    reminder_active = models.BooleanField(db_column='Reminder_Active', blank=True,
                                          null=True)  # Field name made lowercase.
    disclimit = models.FloatField(db_column='DiscLimit', blank=True, null=True)  # Field name made lowercase.
    disctypeamount = models.BooleanField(db_column='DiscTypeAmount', blank=True,
                                         null=True)  # Field name made lowercase.
    autocustdisc = models.BooleanField(db_column='AutoCustDisc')  # Field name made lowercase.
    reorder_active = models.BooleanField(db_column='ReOrder_Active', blank=True,
                                         null=True)  # Field name made lowercase.
    reorder_minqty = models.FloatField(db_column='ReOrder_MinQty', blank=True, null=True)  # Field name made lowercase.
    service_expire_active = models.BooleanField(db_column='Service_Expire_Active')  # Field name made lowercase.
    service_expire_month = models.FloatField(db_column='Service_Expire_Month', blank=True,
                                             null=True)  # Field name made lowercase.
    treatment_limit_active = models.BooleanField(db_column='Treatment_Limit_Active')  # Field name made lowercase.
    treatment_limit_count = models.FloatField(db_column='Treatment_Limit_Count', blank=True,
                                              null=True)  # Field name made lowercase.
    limitservice_flexionly = models.BooleanField(db_column='LimitService_FlexiOnly')  # Field name made lowercase.
    salescommpoints = models.FloatField(db_column='SalesCommPoints', blank=True,
                                        null=True)  # Field name made lowercase.
    workcommpoints = models.FloatField(db_column='WorkCommPoints', blank=True, null=True)  # Field name made lowercase.
    item_price_floor = models.FloatField(db_column='Item_Price_Floor', blank=True,
                                         null=True)  # Field name made lowercase.
    voucher_value = models.FloatField(db_column='Voucher_Value', blank=True, null=True)  # Field name made lowercase.
    voucher_value_is_amount = models.BooleanField(db_column='Voucher_Value_Is_Amount')  # Field name made lowercase.
    voucher_valid_period = models.CharField(db_column='Voucher_Valid_Period', max_length=20, blank=True,
                                            null=True)  # Field name made lowercase.
    prepaid_value = models.FloatField(db_column='Prepaid_Value', blank=True, null=True)  # Field name made lowercase.
    prepaid_sell_amt = models.FloatField(db_column='Prepaid_Sell_Amt', blank=True,
                                         null=True)  # Field name made lowercase.
    prepaid_valid_period = models.CharField(db_column='Prepaid_Valid_Period', max_length=20, blank=True,
                                            null=True)  # Field name made lowercase.
    membercardnoaccess = models.BooleanField(db_column='MemberCardNoAccess', blank=True,
                                             null=True)  # Field name made lowercase.
    rpt_code = models.CharField(db_column='Rpt_Code', max_length=20, blank=True,
                                null=True)  # Field name made lowercase.
    is_gst = models.BooleanField(db_column='IS_GST')  # Field name made lowercase.
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True,
                                    null=True)  # Field name made lowercase.
    stock_pic_b = models.BinaryField(db_column='Stock_PIC_B', blank=True, null=True)  # Field name made lowercase.
    is_open_prepaid = models.BooleanField(db_column='IS_OPEN_PREPAID')  # Field name made lowercase.
    appt_wd_min = models.FloatField(db_column='Appt_WD_Min', blank=True, null=True)  # Field name made lowercase.
    service_cost = models.FloatField(db_column='Service_Cost', blank=True, null=True)  # Field name made lowercase.
    service_cost_percent = models.BooleanField(db_column='Service_Cost_Percent')  # Field name made lowercase.
    sync_guid = models.CharField(db_column='Sync_GUID', max_length=36)  # Field name made lowercase.
    sync_clientindex = models.IntegerField(db_column='Sync_ClientIndex', blank=True,
                                           null=True)  # Field name made lowercase.
    sync_lstupd = models.DateTimeField(db_column='Sync_LstUpd', blank=True, null=True)  # Field name made lowercase.
    account_code_td = models.CharField(db_column='Account_Code_TD', max_length=20, blank=True,
                                       null=True)  # Field name made lowercase.
    sync_clientindexstring = models.TextField(db_column='Sync_ClientIndexString', blank=True,
                                              null=True)  # Field name made lowercase.
    voucher_isvalid_until_date = models.BooleanField(
        db_column='Voucher_IsValid_Until_Date')  # Field name made lowercase.
    voucher_valid_until_date = models.DateTimeField(db_column='Voucher_Valid_Until_Date', blank=True,
                                                    null=True)  # Field name made lowercase.
    workcommholder = models.CharField(max_length=6, blank=True, null=True)
    equipmentcost = models.FloatField(blank=True, null=True)
    postatus = models.BooleanField(blank=True, null=True)
    gst_item_code = models.CharField(db_column='GST_Item_Code', max_length=20, blank=True,
                                     null=True)  # Field name made lowercase.
    istnc = models.BooleanField(db_column='isTnc', blank=True, null=True)  # Field name made lowercase.
    consultantcomm = models.BooleanField(db_column='ConsultantComm', blank=True,
                                         null=True)  # Field name made lowercase.
    t1_tax_code = models.CharField(db_column='T1_Tax_Code', max_length=20, blank=True,
                                   null=True)  # Field name made lowercase.
    is_have_tax = models.BooleanField(db_column='IS_HAVE_TAX')  # Field name made lowercase.
    t2_tax_code = models.CharField(db_column='T2_Tax_Code', max_length=20, blank=True,
                                   null=True)  # Field name made lowercase.
    is_allow_foc = models.BooleanField(db_column='IS_ALLOW_FOC')  # Field name made lowercase.
    vilidity_from_date = models.DateTimeField(db_column='Vilidity_From_Date', blank=True,
                                              null=True)  # Field name made lowercase.
    vilidity_to_date = models.DateTimeField(db_column='Vilidity_To_date', blank=True,
                                            null=True)  # Field name made lowercase.
    vilidity_from_time = models.DateTimeField(db_column='Vilidity_From_Time', blank=True,
                                              null=True)  # Field name made lowercase.
    vilidity_to_time = models.DateTimeField(db_column='Vilidity_To_Time', blank=True,
                                            null=True)  # Field name made lowercase.
    prepaid_disc_type = models.CharField(db_column='Prepaid_Disc_Type', max_length=20, blank=True,
                                         null=True)  # Field name made lowercase.
    prepaid_disc_percent = models.FloatField(db_column='Prepaid_Disc_Percent', blank=True,
                                             null=True)  # Field name made lowercase.
    srv_duration = models.FloatField(db_column='Srv_Duration', blank=True, null=True)  # Field name made lowercase.
    voucher_template_name = models.CharField(db_column='Voucher_Template_Name', max_length=50, blank=True,
                                             null=True)  # Field name made lowercase.
    autoproportion = models.BooleanField(db_column='AutoProportion')
    expiry_days = models.IntegerField(blank=True, null=True)
    smsprimary = models.IntegerField(blank=True, null=True)
    smssecondary = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Stock'


class Treatment_Reporting(models.Model):

    STATUS = [
        ('Open', 'Open'),
        ('Done', 'Done'),
        ('Cancel','Cancel'),
    ]

    RECORD_STATUS = [
        ('PENDING', 'PENDING'),
    ]

    SA_STATUS = [
        ('SA', 'SA'), #SA-Sales
        ('VOID', 'VOID'), # VT-Void Transaction
        ('SU', 'SU'), # SU-Suspend
    ]

    sys_code = models.AutoField(db_column='Sys_Code', primary_key=True)
    treatment_code = models.CharField(db_column='Treatment_Code', max_length=20, null=True)
    course = models.CharField(db_column='Course', max_length=255, blank=True, null=True)
    times = models.CharField(db_column='Times', max_length=10, blank=True, null=True)
    treatment_no = models.CharField(db_column='Treatment_No', max_length=10, blank=True, null=True)
    price = models.FloatField(db_column='Price', blank=True, null=True)
    treatment_date = models.DateTimeField(db_column='Treatment_Date', blank=True, null=True)
    next_appt = models.DateTimeField(db_column='Next_Appt', blank=True, null=True)
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)
    cust_code = models.ForeignKey(Customer_Reporting,db_column='cust_code',to_field='cust_code', on_delete=models.PROTECT,  null=True,db_constraint=False,related_name='treatment_related')
    # cust_code = models.CharField(db_column='Cust_Code', max_length=50, blank=True, null=True)
    status = models.CharField(db_column='Status',choices=STATUS, max_length=50, blank=True, null=True, default='open')
    unit_amount = models.FloatField(db_column='Unit_Amount', blank=True, null=True)
    item_code = models.ForeignKey(Stock_Reporting,db_column='Item_Code',to_field='item_code',db_constraint=False,related_name='treatment_related', on_delete=models.PROTECT,  null=True)
    # item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)
    treatment_parentcode = models.CharField(db_column='Treatment_ParentCode', max_length=20, blank=True, null=True)
    prescription = models.CharField(db_column='Prescription', max_length=255, blank=True, null=True)
    allergy = models.CharField(db_column='Allergy', max_length=255, blank=True, null=True)
    sa_transacno = models.CharField(max_length=20, blank=True, null=True)
    sa_status = models.CharField(max_length=5,choices=SA_STATUS, blank=True, null=True)
    record_status = models.CharField(db_column='Record_Status',choices=RECORD_STATUS, max_length=10, blank=True, null=True)
    appt_time = models.DateTimeField(db_column='Appt_Time', blank=True, null=True)
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)
    duration = models.IntegerField(db_column='Duration', blank=True, null=True)
    hold_item = models.CharField(db_column='Hold_Item', max_length=50, blank=True, null=True)
    transaction_time = models.DateTimeField(db_column='Transaction_Time', blank=True, null=True)
    dt_lineno = models.IntegerField(db_column='dt_LineNo', blank=True, null=True)
    expiry = models.DateTimeField(db_column='Expiry', blank=True, null=True)
    lpackage = models.BooleanField(db_column='lPackage')
    package_code = models.CharField(db_column='Package_Code', max_length=50, blank=True, null=True)
    site_code = models.ForeignKey(ItemSitelist_Reporting,db_column='site_code',to_field='itemsite_code',db_constraint=False,related_name='treatment_related', on_delete=models.PROTECT, null=True)
    # site_code = models.CharField(db_column='Site_Code', max_length=50)
    type = models.CharField(db_column='Type', max_length=50, blank=True, null=True)
    treatment_limit_times = models.FloatField(db_column='Treatment_Limit_Times', blank=True, null=True)
    treatment_count_done = models.FloatField(db_column='Treatment_Count_Done', blank=True, null=True)
    treatment_history_last_modify = models.DateTimeField(db_column='Treatment_History_Last_Modify', blank=True, null=True)
    service_itembarcode = models.CharField(db_column='Service_ItemBarcode', max_length=20, blank=True, null=True)
    isfoc = models.BooleanField(db_column='isFOC', blank=True, null=True)
    # Trmt_Room_Codeid  = models.ForeignKey('custom.Room', on_delete=models.PROTECT,null=True)
    trmt_room_code = models.CharField(db_column='Trmt_Room_Code', max_length=20, blank=True, null=True)
    trmt_is_auto_proportion = models.BooleanField(db_column='Trmt_Is_Auto_Proportion')
    smsout = models.IntegerField(db_column='smsOut', blank=True, null=True)
    emailout = models.BooleanField(db_column='emailOut', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Treatment'
        unique_together = (('treatment_code', 'site_code'),)


class ReportSettings(models.Model):
    report = models.CharField(max_length=100,unique=True)
    settingsData = models.CharField(max_length=8000,default='{}')