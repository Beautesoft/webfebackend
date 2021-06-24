from django.db import models, transaction
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User, Group
from django.utils import timezone
# Create your models here.

#intial

#Final

class City(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'City'

    def __str__(self):
        return str(self.itm_desc)            
    
class State(models.Model):
    itm_id = models.AutoField(db_column='itm_ID', primary_key=True)  # Field name made lowercase.
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'State'

    def __str__(self):
        return str(self.itm_desc)

class Country(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    phonecode = models.CharField(db_column='phoneCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Country'

    def __str__(self):
        return str(self.itm_desc) 

class CustomerClass(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    class_code = models.CharField(db_column='Class_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    class_desc = models.CharField(db_column='Class_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    class_isactive = models.BooleanField(db_column='Class_Isactive', blank=True, null=True,default=True)  # Field name made lowercase.
    class_product = models.FloatField(db_column='Class_Product')  # Field name made lowercase.
    class_service = models.FloatField(db_column='Class_Service')  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Customer_Class'

    def __str__(self):
        return str(self.class_desc)

    @property
    def choice_dict(self):
        """
        this property method for generate FE choice dropdowns
        :return:
        """
        return {"value": self.id, "label": self.class_desc}

class CustomerTitle(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    itm_code = models.CharField(db_column='ITM_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itm_desc = models.CharField(db_column='ITM_DESC', max_length=20, blank=True, null=True)  # Field name made lowercase.
    seq = models.FloatField(db_column='SEQ')  # Field name made lowercase.
    isactive = models.BooleanField(db_column='ISACTIVE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Customer_Title'

    @property
    def choice_dict(self):
        """
        this property method for generate FE choice dropdowns
        :return:
        """
        return {"value": self.id, "label": self.itm_desc}

    
class Source(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    source_code = models.CharField(db_column='Source_Code',  max_length=20, null=True)  # Field name made lowercase.
    source_desc = models.CharField(db_column='Source_Desc', max_length=100, blank=True, null=True)  # Field name made lowercase.
    source_isactive = models.BooleanField(db_column='Source_IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Source'
        unique_together = (('source_code'),)

    def __str__(self):
        return str(self.source_desc)

    @property
    def choice_dict(self):
        """
        this property method for generate FE choice dropdowns
        :return:
        """
        return {"value": self.id, "label": self.source_desc}

class ItemStatus(models.Model):
    itm_id = models.AutoField(primary_key=True)
    status_code = models.CharField(db_column='Status_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status_desc = models.CharField(db_column='Status_Desc', max_length=255, blank=True, null=True)  # Field name made lowercase.
    status_short_desc = models.CharField(db_column='Status_Short_Desc', max_length=255, blank=True, null=True)  # Field name made lowercase.
    itm_isactive = models.BooleanField(db_column='itm_IsActive',default=True)  # Field name made lowercase.
    status_group_code = models.CharField(db_column='Status_Group_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'item_status'

    def __str__(self):
        return str(self.status_short_desc)    
    

class Gender(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_name = models.CharField(max_length=20, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    itm_code = models.CharField(db_column='ITM_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Gender'

    def __str__(self):
        return str(self.itm_name)

    @property
    def choice_dict(self):
        """
        this property method for generate FE choice dropdowns
        :return:
        """
        return {"value": self.itm_id, "label": self.itm_name}


class Maritalstatus(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_name = models.CharField(max_length=20, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    itm_code = models.IntegerField(db_column='ITM_CODE', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'MaritalStatus'

    def __str__(self):
        return str(self.itm_name)
    

class Races(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_name = models.CharField(max_length=20, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    itm_code = models.CharField(db_column='ITM_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Races'

    def __str__(self):
        return str(self.itm_name)    

class Religious(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_name = models.CharField(max_length=20, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    itm_code = models.CharField(db_column='ITM_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Religious'

    def __str__(self):
        return str(self.itm_name)    

class Nationality(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_name = models.CharField(max_length=50, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    itm_code = models.CharField(db_column='ITM_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'NATIONALITY'

    def __str__(self):
        return str(self.itm_name)    

class CommType(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    comm_type_code = models.CharField(db_column='Comm_Type_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    comm_type_desc = models.CharField(db_column='Comm_Type_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comm_type_active = models.BooleanField(db_column='Comm_Type_Active',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Comm_Type'

    def __str__(self):
        return str(self.comm_type_desc)    

class EmpSocso(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    emp_code = models.CharField(db_column='Emp_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    emp_socso_employee = models.FloatField(db_column='Emp_SOCSO_Employee', blank=True, null=True)  # Field name made lowercase.
    emp_socso_employer = models.FloatField(db_column='Emp_SOCSO_Employer', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Emp_SOCSO'

    def __str__(self):
        return str(self.emp_code)    

class Days(models.Model):
    itm_id = models.AutoField(db_column='ITM_ID', primary_key=True)  # Field name made lowercase.
    itm_code = models.CharField(db_column='ITM_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itm_name = models.CharField(db_column='ITM_NAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itm_isactive = models.BooleanField(db_column='ITM_ISACTIVE',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'DAYS'

    def __str__(self):
        return str(self.itm_name)    

class EmpType(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    type_code = models.CharField(db_column='TYPE_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    type_desc = models.CharField(db_column='TYPE_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    type_isactive = models.BooleanField(db_column='TYPE_ISACTIVE', blank=True, null=True,default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'EMP_TYPE'

    def __str__(self):
        return str(self.type_desc) 

#New Table

class Treatment_Master(models.Model):
    

    STATUS = [
        ('Open', 'Open'),
        ('Done', 'Done'),
        ('Cancel','Cancel'),
    ]

    RECORD_STATUS = [
        ('Pending', 'PENDING'),
    ]
    
    SA_STATUS = [
        ('SA', 'SA'), #SA-Sales
        ('VT', 'VT'), # VT-Void Transaction
        ('SU', 'SU'), # SU-Suspend
    ]

    id = models.AutoField(primary_key=True)  # Field name made lowercase.
    treatment_code = models.CharField(db_column='Treatment_Code',  max_length=20,null=True, blank=True)  # Field name made lowercase.
    course = models.CharField(db_column='Course', max_length=255, blank=True, null=True)  # Field name made lowercase.
    times = models.CharField(db_column='Times', max_length=10, blank=True, null=True)  # Field name made lowercase.
    treatment_no = models.CharField(db_column='Treatment_No', max_length=10, blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.
    treatment_date = models.DateTimeField(db_column='Treatment_Date',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    next_appt = models.DateTimeField(db_column='Next_Appt', blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    Cust_Codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 
    cust_code = models.CharField(db_column='Cust_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status',choices=STATUS, max_length=50, blank=True, null=True,default='open')  # Field name made lowercase.
    unit_amount = models.DecimalField(max_digits=19,decimal_places=14,db_column='Unit_Amount', blank=True, null=True)  # Field name made lowercase.
    Item_Codeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT, null=True) 
    item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    treatment_parentcode = models.CharField(db_column='Treatment_ParentCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    prescription = models.CharField(db_column='Prescription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    allergy = models.CharField(db_column='Allergy', max_length=255, blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20, blank=True, null=True)
    sa_status = models.CharField(max_length=5,choices=SA_STATUS, blank=True, null=True)
    record_status = models.CharField(db_column='Record_Status',choices=RECORD_STATUS, max_length=10, blank=True, null=True)  # Field name made lowercase.
    appt_time = models.DateTimeField(db_column='Appt_Time', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)  # Field name made lowercase.
    duration = models.IntegerField(db_column='Duration', blank=True, null=True)  # Field name made lowercase.
    hold_item = models.CharField(db_column='Hold_Item', max_length=50, blank=True, null=True)  # Field name made lowercase.
    transaction_time = models.DateTimeField(db_column='Transaction_Time', blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', blank=True, null=True)  # Field name made lowercase.
    expiry = models.DateTimeField(db_column='Expiry', blank=True, null=True)  # Field name made lowercase.
    lpackage = models.BooleanField(db_column='lPackage',null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, null=True, blank=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    treatment_limit_times = models.FloatField(db_column='Treatment_Limit_Times', blank=True, null=True)  # Field name made lowercase.
    treatment_count_done = models.FloatField(db_column='Treatment_Count_Done', blank=True, null=True)  # Field name made lowercase.
    treatment_history_last_modify = models.DateTimeField(db_column='Treatment_History_Last_Modify', blank=True, null=True)  # Field name made lowercase.
    service_itembarcode = models.CharField(db_column='Service_ItemBarcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    isfoc = models.BooleanField(db_column='isFOC', blank=True, null=True)  # Field name made lowercase.
    Trmt_Room_Codeid  = models.ForeignKey('custom.Room', on_delete=models.PROTECT,null=True)
    trmt_room_code = models.CharField(db_column='Trmt_Room_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    trmt_is_auto_proportion = models.BooleanField(db_column='Trmt_Is_Auto_Proportion', null=True)  # Field name made lowercase.
    smsout = models.BooleanField(db_column='smsOut', blank=True, null=True)  # Field name made lowercase.
    emailout = models.BooleanField(db_column='emailOut', blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    Item_Class = models.ForeignKey('cl_table.ItemClass', on_delete=models.PROTECT, null=True)
    cus_requests =  models.CharField(max_length=900, null=True)
    emp_no = models.ManyToManyField('cl_table.Employee',  blank=True)
    treatment_details = models.TextField(null=True)
    procedure = models.TextField(null=True)
    products_used =  models.CharField(max_length=100,null=True)
    recurring_appointment = models.CharField(max_length=100,null=True)
    PIC = models.ImageField(upload_to='img', null=True)
    Appointment = models.ForeignKey('cl_table.Appointment',related_name='master', on_delete=models.PROTECT,null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    add_duration = models.TimeField(null=True)
    is_payment = models.BooleanField(default=False,null=True)
    appt_remark = models.CharField(db_column='Appt_remark', max_length=1950,null=True)  # Field name made lowercase.
    requesttherapist = models.BooleanField(db_column='requestTherapist',  null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Treatment_Master'
        # unique_together = (('treatment_code', 'site_code'),)

    
    def __str__(self):
        return str(self.course)         


class Treatment(models.Model):
    
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

    sys_code = models.AutoField(db_column='Sys_Code', primary_key=True)  # Field name made lowercase.
    treatment_code = models.CharField(db_column='Treatment_Code', max_length=20, null=True)  # Field name made lowercase.
    course = models.CharField(db_column='Course', max_length=255, blank=True, null=True)  # Field name made lowercase.
    times = models.CharField(db_column='Times', max_length=10, blank=True, null=True)  # Field name made lowercase.
    treatment_no = models.CharField(db_column='Treatment_No', max_length=10, blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.
    treatment_date = models.DateTimeField(db_column='Treatment_Date',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    next_appt = models.DateTimeField(db_column='Next_Appt', blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    Cust_Codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True) 
    cust_code = models.CharField(db_column='Cust_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status',choices=STATUS, max_length=50, blank=True, null=True, default='open')  # Field name made lowercase.
    unit_amount = models.FloatField(db_column='Unit_Amount', blank=True, null=True)  # Field name made lowercase.
    Item_Codeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT, null=True) 
    item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    treatment_parentcode = models.CharField(db_column='Treatment_ParentCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    prescription = models.CharField(db_column='Prescription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    allergy = models.CharField(db_column='Allergy', max_length=255, blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20, blank=True, null=True)
    sa_status = models.CharField(max_length=5,choices=SA_STATUS, blank=True, null=True)
    record_status = models.CharField(db_column='Record_Status',choices=RECORD_STATUS, max_length=10, blank=True, null=True)  # Field name made lowercase.
    appt_time = models.DateTimeField(db_column='Appt_Time', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)  # Field name made lowercase.
    duration = models.IntegerField(db_column='Duration', blank=True, null=True)  # Field name made lowercase.
    hold_item = models.CharField(db_column='Hold_Item', max_length=50, blank=True, null=True)  # Field name made lowercase.
    transaction_time = models.DateTimeField(db_column='Transaction_Time', blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', blank=True, null=True)  # Field name made lowercase.
    expiry = models.DateTimeField(db_column='Expiry', blank=True, null=True)  # Field name made lowercase.
    lpackage = models.BooleanField(db_column='lPackage', null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    treatment_limit_times = models.FloatField(db_column='Treatment_Limit_Times', blank=True, null=True)  # Field name made lowercase.
    treatment_count_done = models.FloatField(db_column='Treatment_Count_Done', blank=True, null=True)  # Field name made lowercase.
    treatment_history_last_modify = models.DateTimeField(db_column='Treatment_History_Last_Modify', blank=True, null=True)  # Field name made lowercase.
    service_itembarcode = models.CharField(db_column='Service_ItemBarcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isfoc = models.BooleanField(db_column='isFOC', blank=True, null=True)  # Field name made lowercase.
    Trmt_Room_Codeid  = models.ForeignKey('custom.Room', on_delete=models.PROTECT,null=True)
    trmt_room_code = models.CharField(db_column='Trmt_Room_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    trmt_is_auto_proportion = models.BooleanField(db_column='Trmt_Is_Auto_Proportion', null=True)  # Field name made lowercase.
    smsout = models.BooleanField(db_column='smsOut', blank=True, null=True)  # Field name made lowercase.
    emailout = models.BooleanField(db_column='emailOut', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    treatment_master = models.ForeignKey('cl_table.Treatment_Master', on_delete=models.PROTECT, null=True)
    Appointment = models.ForeignKey('cl_table.Appointment', on_delete=models.PROTECT,null=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    add_duration = models.TimeField(null=True)
    is_payment = models.BooleanField(default=False,null=True)
    treatment_account = models.ForeignKey('cl_table.TreatmentAccount', on_delete=models.PROTECT, null=True)
    helper_ids = models.ManyToManyField('cl_table.TmpItemHelper', related_name='tmpitemhelper', blank=True)


    class Meta:
        db_table = 'Treatment'
        # unique_together = (('treatment_code', 'site_code'),)

    def __str__(self):
        return str(self.course)      

class Employee(models.Model):
    
    # CHECK = [
    #     ('YES', 'YES'),
    #     ('NO', 'NO'),
    # ]
    emp_no = models.AutoField(db_column='Emp_no', primary_key=True)  # Field name made lowercase.
    emp_code = models.CharField(db_column='Emp_code', max_length=20, unique=True)  # Field name made lowercase.
    emp_name = models.CharField(db_column='Emp_name', max_length=60, blank=True, null=True)  # Field name made lowercase.
    emp_nric = models.CharField(db_column='Emp_nric', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Emp_sexesid  = models.ForeignKey(Gender, on_delete=models.PROTECT, null=True) #, null=True
    emp_sexes = models.CharField(db_column='Emp_sexes', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Emp_maritalid = models.ForeignKey(Maritalstatus, on_delete=models.PROTECT, null=True)
    emp_marital = models.CharField(db_column='Emp_marital', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Emp_raceid = models.ForeignKey(Races, on_delete=models.PROTECT, null=True, blank=True)
    emp_race = models.CharField(db_column='Emp_race', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Emp_religionid  = models.ForeignKey(Religious, on_delete=models.PROTECT, null=True)
    emp_religion = models.CharField(db_column='Emp_religion', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_phone1 = models.CharField(db_column='Emp_phone1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_phone2 = models.CharField(db_column='Emp_phone2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Emp_nationalityid  = models.ForeignKey(Nationality, on_delete=models.PROTECT, null=True)
    emp_nationality = models.CharField(db_column='Emp_nationality', max_length=40, blank=True, null=True)  # Field name made lowercase.
    emp_address = models.CharField(db_column='Emp_address', max_length=255, blank=True, null=True)  # Field name made lowercase.
    emp_jobpost = models.CharField(db_column='Emp_jobpost', max_length=40, blank=True, null=True)  # Field name made lowercase.
    emp_isactive = models.BooleanField(db_column='Emp_isactive',default=True)  # Field name made lowercase.
    emp_emer = models.CharField(db_column='Emp_emer', max_length=60, blank=True, null=True)  # Field name made lowercase.
    emp_emerno = models.CharField(db_column='Emp_emerno', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_salary = models.FloatField(db_column='Emp_salary', blank=True, null=True)  # Field name made lowercase.
    # Emp_Commission_Typeid = models.ForeignKey(CommType, on_delete=models.PROTECT, null=True)
    emp_commission_type = models.CharField(db_column='Emp_Commission_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_dob = models.DateField(db_column='Emp_DOB', blank=True, null=True)  # Field name made lowercase.
    emp_joindate = models.DateField(db_column='Emp_JoinDate', blank=True, null=True)  # Field name made lowercase.
    emp_email = models.EmailField(db_column='Emp_email', max_length=40, blank=True, null=True)  # Field name made lowercase.
    # Emp_SOCSOid = models.ForeignKey(EmpSocso, on_delete=models.PROTECT, null=True)
    emp_socso = models.CharField(db_column='Emp_SOCSO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_epf = models.CharField(db_column='Emp_EPF', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_target = models.FloatField(db_column='Emp_Target', blank=True, null=True)  # Field name made lowercase.
    emp_targetbas = models.IntegerField(db_column='Emp_TargetBas', blank=True, null=True)  # Field name made lowercase.
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    emp_barcode = models.CharField(db_column='Emp_Barcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_barcode2 = models.CharField(db_column='Emp_Barcode2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Emp_LeaveDayid = models.ForeignKey(Days, on_delete=models.PROTECT, null=True)
    emp_leaveday = models.CharField(db_column='Emp_LeaveDay', max_length=50, blank=True, null=True)  # Field name made lowercase.
    emp_pic = models.ImageField(db_column='Emp_PIC', blank=True, null=True,upload_to='img')  # Field name made lowercase.
    annual_leave = models.IntegerField(db_column='Annual_Leave', blank=True, null=True)  # Field name made lowercase.
    marriage_leave = models.IntegerField(db_column='Marriage_Leave', blank=True, null=True)  # Field name made lowercase.
    compassiolnate_leave = models.IntegerField(db_column='Compassiolnate_leave', blank=True, null=True)  # Field name made lowercase.
    national_service = models.IntegerField(db_column='National_Service', blank=True, null=True)  # Field name made lowercase.
    maternity_leave = models.IntegerField(db_column='Maternity_Leave', blank=True, null=True)  # Field name made lowercase.
    unpay_leave = models.IntegerField(db_column='Unpay_Leave', blank=True, null=True)  # Field name made lowercase.
    mc_leave = models.IntegerField(db_column='MC_Leave', blank=True, null=True)  # Field name made lowercase.
    emergency_leave = models.IntegerField(db_column='Emergency_Leave', blank=True, null=True)  # Field name made lowercase.
    emp_isboss = models.BooleanField(db_column='Emp_IsBoss', blank=True, null=True)  # Field name made lowercase.
    itemsite_refcode = models.CharField(db_column='ITEMSITE_REFCODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    EMP_TYPEid = models.ForeignKey('custom.EmpLevel', on_delete=models.PROTECT, null=True) #, null=True
    emp_type = models.CharField(db_column='EMP_TYPE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_refcode = models.CharField(db_column='EMP_REFCODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    display_name = models.CharField(db_column='Display_Name', max_length=20, blank=True, null=True)  # Field name made lowercase.
    show_in_appt = models.BooleanField(db_column='Show_In_Appt',null=True, default=False)  # Field name made lowercase.
    emp_address1 = models.CharField(db_column='Emp_address1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    emp_address2 = models.CharField(db_column='Emp_address2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    emp_address3 = models.CharField(db_column='Emp_address3', max_length=255, blank=True, null=True)  # Field name made lowercase.
    emp_remarks = models.CharField(db_column='Emp_remarks', max_length=500, blank=True, null=True)  # Field name made lowercase.
    age_range0 = models.BooleanField(db_column='Age_Range0', null=True)  # Field name made lowercase.
    age_range1 = models.BooleanField(db_column='Age_Range1', null=True)  # Field name made lowercase.
    age_range2 = models.BooleanField(db_column='Age_Range2', null=True)  # Field name made lowercase.
    age_range3 = models.BooleanField(db_column='Age_Range3', null=True)  # Field name made lowercase.
    age_range4 = models.BooleanField(db_column='Age_Range4', null=True)  # Field name made lowercase.
    type_code = models.CharField(db_column='Type_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_address4 = models.CharField(db_column='Emp_address4', max_length=255, blank=True, null=True)  # Field name made lowercase.
    attn_password = models.CharField(db_column='Attn_Password', max_length=50, blank=True, null=True)  # Field name made lowercase.
    max_disc = models.FloatField(db_column='Max_Disc', blank=True, null=True)  # Field name made lowercase.
    disc_type = models.BooleanField(db_column='Disc_Type', blank=True, null=True)  # Field name made lowercase.
    disc_amt = models.FloatField(db_column='Disc_Amt', blank=True, null=True)  # Field name made lowercase.
    ep_allow = models.BooleanField(db_column='EP_Allow', blank=True, null=True)  # Field name made lowercase.
    ep_amttype = models.BooleanField(db_column='EP_AmtType', blank=True, null=True)  # Field name made lowercase.
    ep_startdate = models.DateTimeField(db_column='EP_StartDate', blank=True, null=True)  # Field name made lowercase.
    ep_discamt = models.FloatField(db_column='EP_DiscAmt', blank=True, null=True)  # Field name made lowercase.
    ep_amt = models.FloatField(db_column='EP_Amt', blank=True, null=True)  # Field name made lowercase.
    bonus_level = models.CharField(db_column='Bonus_Level', max_length=50, blank=True, null=True)  # Field name made lowercase.
    bonus_scale_code = models.CharField(db_column='Bonus_Scale_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    has_product_comm = models.BooleanField(db_column='Has_Product_Comm', blank=True, null=True)  # Field name made lowercase.
    ser_level = models.CharField(db_column='Ser_Level', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ser_scale_code = models.CharField(db_column='Ser_Scale_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    treat_level = models.CharField(db_column='Treat_Level', max_length=50, blank=True, null=True)  # Field name made lowercase.
    treat_scale_code = models.CharField(db_column='Treat_Scale_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    emp_target_bonus = models.FloatField(db_column='Emp_Target_Bonus', blank=True, null=True)  # Field name made lowercase.
    extra_percent = models.FloatField(db_column='Extra_Percent', blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist',related_name='staff_emp', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    emp_pic_b = models.BinaryField(db_column='Emp_Pic_B', blank=True, null=True)  # Field name made lowercase.
    getsms = models.BooleanField(db_column='GetSMS',null=True)  # Field name made lowercase.
    emp_comm = models.BooleanField(db_column='Emp_Comm', blank=True, null=True)  # Field name made lowercase.
    show_in_sales = models.BooleanField(db_column='Show_In_Sales', null=True, default=False)  # Field name made lowercase.
    show_in_trmt = models.BooleanField(db_column='Show_In_Trmt', null=True, default=False)  # Field name made lowercase.
    emp_edit_date = models.DateTimeField(db_column='Emp_Edit_Date', blank=True, null=True)  # Field name made lowercase.
    emp_seq_webappt = models.IntegerField(db_column='Emp_Seq_WebAppt', blank=True, null=True)  # Field name made lowercase.
    leave_bal = models.IntegerField(db_column='Leave_bal', blank=True, null=True)  # Field name made lowercase.
    leave_taken = models.IntegerField(db_column='Leave_taken', blank=True, null=True)  # Field name made lowercase.
    employeeapptype = models.CharField(db_column='employeeAppType', max_length=40, blank=True, null=True)  # Field name made lowercase.
    skillset = models.CharField(max_length=40, blank=True, null=True)
    fcmtoken = models.TextField(db_column='FCMToken', blank=True, null=True)  # Field name made lowercase.
    notificationsetting = models.BooleanField(db_column='notificationSetting', blank=True, null=True)  # Field name made lowercase.
    treat_exp_day_limit = models.IntegerField(db_column='Treat_Exp_Day_Limit', blank=True, null=True)  # Field name made lowercase.
    otp = models.CharField(max_length=20, blank=True, null=True)
    fullname = models.CharField(max_length=100, blank=True, null=True)
    defaultSiteCodeid = models.ForeignKey('cl_app.ItemSitelist',related_name='staff', on_delete=models.PROTECT, null=True)
    defaultsitecode = models.CharField(db_column='defaultSiteCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    queue_no = models.IntegerField(db_column='Queue_No', null=True)  # Field name made lowercase.
    emp_pic_b1 = models.CharField(db_column='Emp_Pic_B1', max_length=250, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    skills = models.ManyToManyField('cl_table.Stock',  blank=True)
    shift = models.ForeignKey('cl_table.Attendance2',related_name='staff', on_delete=models.PROTECT,null=True)
    skills_list = models.CharField(max_length=1000, null=True)
    is_login = models.BooleanField(db_column='Login', blank=True, null=True)  # Field name made lowercase.
    pw_password = models.CharField(db_column='PW_Password', max_length=15,  null=True)  #, blank=True, null=True Field name made lowercase.
    LEVEL_ItmIDid = models.ForeignKey('cl_table.Securities', on_delete=models.PROTECT,null=True) #,null=True,blank=True
    emp_country = models.ForeignKey('cl_table.Country', on_delete=models.PROTECT,null=True) #,null=True,blank=True


    class Meta:
        db_table = 'Employee'
        # unique_together = [['emp_name','emp_phone1']]

    def __str__(self):
        return str(self.emp_name)

    @property
    def choice_dict(self):
        """
        this property method for generate FE choice dropdowns
        :return:
        """
        return {"value": self.emp_no, "label": self.emp_name}

class Securities(models.Model):
    level_itmid = models.AutoField(db_column='LEVEL_ItmID', primary_key=True)  # Field name made lowercase.
    level_name = models.CharField(db_column='LEVEL_Name', max_length=40, blank=True, null=True)  # Field name made lowercase.
    level_description = models.CharField(db_column='LEVEL_Description', max_length=60, blank=True, null=True)  # Field name made lowercase.
    level_permitappointment = models.BooleanField(db_column='LEVEL_PermitAppointment',default=False)  # Field name made lowercase.
    level_permitcrm = models.BooleanField(db_column='LEVEL_PermitCrm',default=False)  # Field name made lowercase.
    level_permitcreditor = models.BooleanField(db_column='LEVEL_PermitCreditor',default=False)  # Field name made lowercase.
    level_permitstaff = models.BooleanField(db_column='LEVEL_PermitStaff',default=False)  # Field name made lowercase.
    level_permituserlogin = models.BooleanField(db_column='LEVEL_PermitUserLogin',default=False)  # Field name made lowercase.
    level_permitstockitem = models.BooleanField(db_column='LEVEL_PermitStockItem',default=False)  # Field name made lowercase.
    level_permitsecurity = models.BooleanField(db_column='LEVEL_PermitSecurity',default=False)  # Field name made lowercase.
    level_permitsendmail = models.BooleanField(db_column='LEVEL_PermitSendmail',default=False)  # Field name made lowercase.
    level_permitinventory = models.BooleanField(db_column='LEVEL_PermitInventory',default=False)  # Field name made lowercase.
    level_permitanalysis = models.BooleanField(db_column='LEVEL_PermitAnalysis',default=False)  # Field name made lowercase.
    level_permitmaintain = models.BooleanField(db_column='LEVEL_PermitMaintain',default=False)  # Field name made lowercase.
    level_permitpos = models.BooleanField(db_column='LEVEL_PermitPOS',default=False)  # Field name made lowercase.
    level_isactive = models.BooleanField(db_column='LEVEL_Isactive',default=True)  # Field name made lowercase.
    level_permitpaytable = models.BooleanField(db_column='LEVEL_PermitPaytable',default=False)  # Field name made lowercase.
    level_permitforex = models.BooleanField(db_column='LEVEL_PermitForex',default=False)  # Field name made lowercase.
    level_permitdiv = models.BooleanField(db_column='LEVEL_PermitDiv',default=False)  # Field name made lowercase.
    level_permitdiscount = models.BooleanField(db_column='LEVEL_PermitDiscount',default=False)  # Field name made lowercase.
    level_permitdept = models.BooleanField(db_column='LEVEL_PermitDept',default=False)  # Field name made lowercase.
    level_permitclass = models.BooleanField(db_column='LEVEL_PermitClass',default=False)  # Field name made lowercase.
    level_permitpromo = models.BooleanField(db_column='LEVEL_PermitPromo',default=False)  # Field name made lowercase.
    level_permitattendance = models.BooleanField(db_column='LEVEL_PermitAttendance',default=False)  # Field name made lowercase.
    level_permitstkreceive = models.BooleanField(db_column='LEVEL_PermitStkReceive',default=False)  # Field name made lowercase.
    level_permitstkadj = models.BooleanField(db_column='LEVEL_PermitStkAdj',default=False)  # Field name made lowercase.
    level_permitstktrans = models.BooleanField(db_column='LEVEL_PermitStkTrans',default=False)  # Field name made lowercase.
    level_permitstkwriteoff = models.BooleanField(db_column='LEVEL_PermitStkWriteOff',default=False)  # Field name made lowercase.
    level_permitstkquery = models.BooleanField(db_column='LEVEL_PermitStkQuery',default=False)  # Field name made lowercase.
    level_permitstktk = models.BooleanField(db_column='LEVEL_PermitStkTK',default=False)  # Field name made lowercase.
    level_permitstkvar = models.BooleanField(db_column='LEVEL_PermitStkVar',default=False)  # Field name made lowercase.
    level_code = models.CharField(max_length=50, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Securities'

    def __str__(self):
        return str(self.level_name)    

class Securitycontrollist(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    controlname = models.CharField(db_column='ControlName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    controldesc = models.CharField(db_column='ControlDesc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    controlindex = models.IntegerField(db_column='ControlIndex', blank=True, null=True)  # Field name made lowercase.
    controlparent = models.CharField(db_column='ControlParent', max_length=50, blank=True, null=True)  # Field name made lowercase.
    control_status = models.BooleanField(db_column='Control_Status', blank=True, null=True)  # Field name made lowercase.
    seq = models.IntegerField(db_column='SEQ', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SecurityControlList'


class Securitylevellist(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    controlname = models.CharField(db_column='ControlName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    controldesc = models.CharField(db_column='ControlDesc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    controlparent = models.CharField(db_column='ControlParent', max_length=50, blank=True, null=True)  # Field name made lowercase.
    controlindex = models.IntegerField(db_column='ControlIndex', blank=True, null=True)  # Field name made lowercase.
    controlstatus = models.BooleanField(db_column='ControlStatus')  # Field name made lowercase.
    level_itemid = models.CharField(db_column='Level_ItemID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    seq = models.CharField(db_column='SEQ', max_length=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'SecurityLevelList'

class MenuSecurity(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    security_level_code = models.CharField(db_column='SECURITY_LEVEL_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    security_level_desc = models.CharField(db_column='SECURITY_LEVEL_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    is_active = models.BooleanField(db_column='IS_ACTIVE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Menu_Security'


class MenuSecuritylevellist(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    security_level_code = models.CharField(db_column='SECURITY_LEVEL_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    menu_list = models.CharField(db_column='MENU_LIST', max_length=100, blank=True, null=True)  # Field name made lowercase.
    menu_active = models.BooleanField(db_column='MENU_ACTIVE')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Menu_SecurityLevelList'



class Fmspw(models.Model):
    pw_id = models.AutoField(db_column='PW_ID', primary_key=True)  # Field name made lowercase.
    pw_userlogin = models.CharField(db_column='PW_UserLogin', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pw_password = models.CharField(db_column='PW_Password', max_length=15, blank=True, null=True)  # Field name made lowercase.
    flgdisc = models.BooleanField(default=False)
    LEVEL_ItmIDid = models.ForeignKey(Securities, on_delete=models.PROTECT,null=True) #,null=True,blank=True
    level_itmid = models.IntegerField(db_column='LEVEL_ItmID', blank=True, null=True)  # Field name made lowercase.
    pw_isactive = models.BooleanField(db_column='PW_Isactive',default=True)  # Field name made lowercase.
    level_desc = models.CharField(db_column='Level_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Emp_Codeid  = models.ForeignKey(Employee, on_delete=models.PROTECT,null=True)
    emp_code = models.CharField(db_column='Emp_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    flgphy = models.BooleanField(db_column='flgPHY',default=False)  # Field name made lowercase.
    flggrn = models.BooleanField(db_column='flgGRN',default=False)  # Field name made lowercase.
    flgadj = models.BooleanField(db_column='flgADJ',default=False)  # Field name made lowercase.
    flgtfr = models.BooleanField(db_column='flgTFR',default=False)  # Field name made lowercase.
    flgdelart = models.BooleanField(db_column='flgDelArt',default=False)  # Field name made lowercase.
    flgmclock = models.BooleanField(db_column='flgMClock',default=False)  # Field name made lowercase.
    lallowflgdelart = models.BooleanField(db_column='lallowFlgDelArt',default=False)  # Field name made lowercase.
    flgopendrawer = models.BooleanField(default=False)
    flgexchange = models.BooleanField(db_column='flgExchange',default=False)  # Field name made lowercase.
    flgrevtrm = models.BooleanField(db_column='flgRevTrm',default=False)  # Field name made lowercase.
    flgvoid = models.BooleanField(db_column='flgVoid',default=False)  # Field name made lowercase.
    flgrefund = models.BooleanField(db_column='flgRefund',default=False)  # Field name made lowercase.
    flgemail = models.BooleanField(db_column='flgEmail',default=False)  # Field name made lowercase.
    flgcustadd = models.BooleanField(db_column='flgCustAdd', blank=True, null=True,default=False)  # Field name made lowercase.
    flgviewcost = models.BooleanField(db_column='flgViewCost', blank=True, null=True,default=False)  # Field name made lowercase.
    flgfoc = models.BooleanField(db_column='flgFOC',default=False)  # Field name made lowercase.
    flgappt = models.BooleanField(db_column='flgAppt',default=False)  # Field name made lowercase.
    flgexpire = models.BooleanField(db_column='flgExpire',default=False)  # Field name made lowercase.
    flgviewath = models.BooleanField(db_column='flgViewAth',default=False)  # Field name made lowercase.
    flgaddath = models.BooleanField(db_column='flgAddAth',default=False)  # Field name made lowercase.
    flgeditath = models.BooleanField(db_column='flgEditAth',default=False)  # Field name made lowercase.
    flgrefundpp = models.BooleanField(db_column='flgRefundPP',default=False)  # Field name made lowercase.
    flgrefundcn = models.BooleanField(db_column='flgRefundCN',default=False)  # Field name made lowercase.
    flgattn = models.BooleanField(db_column='flgAttn',default=False)  # Field name made lowercase.
    flgchangeexpirydate = models.BooleanField(db_column='flgChangeExpiryDate',default=False)  # Field name made lowercase.
    flgoutletrequest = models.BooleanField(db_column='flgOutletRequest',default=False)  # Field name made lowercase.
    flgstockusagememo = models.BooleanField(db_column='flgStockUsageMemo',default=False)  # Field name made lowercase.
    flgappteditath = models.BooleanField(db_column='flgApptEditAth',default=False)  # Field name made lowercase.
    flgchangeunitprice = models.BooleanField(db_column='flgChangeUnitPrice',default=False)  # Field name made lowercase.
    flgoveridearstaff = models.BooleanField(db_column='flgOverideARStaff',default=False)  # Field name made lowercase.
    flgluckydraw = models.BooleanField(db_column='flgLuckyDraw',default=False)  # Field name made lowercase.
    flgaccountinterface = models.BooleanField(db_column='flgAccountInterface',default=False)  # Field name made lowercase.
    flgvoidcurrentday = models.BooleanField(db_column='flgVoidCurrentDay',default=False)  # Field name made lowercase.
    flgcallmodule = models.BooleanField(db_column='flgCallModule',default=False)  # Field name made lowercase.
    flggiftmodule = models.BooleanField(db_column='flgGiftModule',default=False)  # Field name made lowercase.
    flgcalldatechange = models.BooleanField(db_column='flgCallDateChange',default=False)  # Field name made lowercase.
    flgallowinsufficent = models.BooleanField(db_column='flgAllowInsufficent',default=False)  # Field name made lowercase.
    flgallowcardusage = models.BooleanField(db_column='flgAllowCardUsage',default=False)  # Field name made lowercase.
    flgallowblockappointment = models.BooleanField(db_column='flgAllowBlockAppointment',default=False)  # Field name made lowercase.
    flgalldayendsettlement = models.BooleanField(db_column='flgAllDayEndSettlement', blank=True, null=True,default=False)  # Field name made lowercase.
    flgallcom = models.BooleanField(db_column='flgAllCom', blank=True, null=True,default=False)  # Field name made lowercase.
    flgallowtdexpiryservice = models.BooleanField(db_column='flgAllowTDExpiryService',default=False)  # Field name made lowercase.
    flghmsetting = models.BooleanField(db_column='flgHMSetting', blank=True, null=True,default=False)  # Field name made lowercase.
    salon_code = models.CharField(db_column='Salon_Code', max_length=40, null=True)  #New Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True) #
    loginsite = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT,null=True) #, null=True, blank=True
    flgsales = models.BooleanField(db_column='flgSales', null=True,default=False)  # Field name made lowercase.

    class Meta:
        db_table = 'FMSPW'
    
    def __str__(self):
        return str(self.pw_userlogin) 

class Customer(models.Model):
    cust_no = models.AutoField(db_column='Cust_No', primary_key=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_code', max_length=255,null=True)  # Field name made lowercase.
    join_status = models.BooleanField(db_column='Join_status',null=True)  # Field name made lowercase.
    cust_joindate = models.DateTimeField(db_column='Cust_JoinDate', blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_name', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_ccid = models.FloatField(db_column='Cust_CCID', blank=True, null=True)  # Field name made lowercase.
    cust_ctyid = models.FloatField(db_column='Cust_CTYID', blank=True, null=True)  # Field name made lowercase.
    exp_status = models.BooleanField(db_column='Exp_Status',null=True)  # Field name made lowercase.
    cust_expirydate = models.DateTimeField(db_column='Cust_ExpiryDate', blank=True, null=True)  # Field name made lowercase.
    cust_birthyear = models.FloatField(db_column='Cust_BirthYear', blank=True, null=True)  # Field name made lowercase.
    cust_birthmonth = models.FloatField(db_column='Cust_BirthMonth', blank=True, null=True)  # Field name made lowercase.
    cust_birthday = models.FloatField(db_column='Cust_BirthDay', blank=True, null=True)  # Field name made lowercase.
    cust_sex = models.CharField(db_column='Cust_Sex', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_address = models.CharField(db_column='Cust_address', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_address1 = models.CharField(db_column='Cust_address1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_phone1 = models.CharField(db_column='Cust_phone1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_pager = models.CharField(db_column='Cust_Pager', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_phone2 = models.CharField(db_column='Cust_phone2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_email = models.EmailField(db_column='Cust_email', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_maillist = models.BooleanField(db_column='Cust_MailList',null=True)  # Field name made lowercase.
    cust_defaultlist = models.BooleanField(db_column='Cust_DefaultList',null=True)  # Field name made lowercase.
    cust_blacklist = models.BooleanField(db_column='Cust_BlackList',null=True)  # Field name made lowercase.
    cust_occupation = models.CharField(db_column='Cust_Occupation', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_company = models.CharField(db_column='Cust_Company', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_ofsaddr1 = models.CharField(db_column='Cust_OfsAddr1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_ofsaddr2 = models.CharField(db_column='Cust_OfsAddr2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_phoneo = models.CharField(db_column='Cust_phoneO', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_ofsfax = models.CharField(db_column='Cust_OfsFax', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_remark = models.CharField(db_column='Cust_Remark', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    cust_nric = models.CharField(db_column='Cust_nric', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_credit = models.DecimalField(db_column='Cust_Credit', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    cust_membershipfee = models.DecimalField(db_column='Cust_MembershipFee', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    cust_membershipused = models.DecimalField(db_column='Cust_MembershipUsed', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    cust_membership = models.CharField(db_column='Cust_Membership', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_activeyn = models.CharField(db_column='Cust_ActiveYN', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_address2 = models.CharField(db_column='Cust_address2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_address3 = models.CharField(db_column='Cust_address3', max_length=255, blank=True, null=True)  # Field name made lowercase.
    dob_status = models.BooleanField(db_column='DOB_status',null=True)  # Field name made lowercase.
    cust_dob = models.DateField(db_column='Cust_DOB', blank=True, null=True)  # Field name made lowercase.
    cust_marital = models.CharField(db_column='Cust_marital', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_race = models.CharField(db_column='Cust_race', max_length=255, blank=True, null=True)  # Field name made lowercase.
    Cust_sexesid = models.ForeignKey(Gender, on_delete=models.PROTECT,null=True) #, null=True
    cust_sexes = models.CharField(db_column='Cust_sexes', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_religion = models.CharField(db_column='Cust_religion', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_nationality = models.CharField(db_column='Cust_nationality', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_isactive = models.BooleanField(db_column='Cust_isactive',default=True)  # Field name made lowercase.
    cust_stylist = models.CharField(db_column='Cust_Stylist', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_stylistname = models.CharField(db_column='Cust_Stylistname', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_shampoo = models.CharField(db_column='Cust_Shampoo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_conditioner = models.CharField(db_column='Cust_Conditioner', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_prods = models.CharField(db_column='Cust_Prods', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_pic = models.CharField(db_column='Cust_PIC', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_vipdiscper = models.CharField(db_column='CUST_VIPDISCPER', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_vipdisc = models.CharField(db_column='CUST_VIPDISC', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_city = models.CharField(db_column='Cust_City', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_interest = models.CharField(db_column='Cust_Interest', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_salaryrange = models.CharField(db_column='Cust_SalaryRange', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_postcode = models.CharField(db_column='Cust_PostCode', max_length=255, blank=True, null=True)  # Field name made lowercase.
    allergy = models.CharField(db_column='Allergy', max_length=255, blank=True, null=True)  # Field name made lowercase.
    cust_address4 = models.CharField(db_column='Cust_address4', max_length=255, blank=True, null=True)  # Field name made lowercase.
    mcust_code = models.CharField(db_column='MCust_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_type = models.CharField(db_column='Cust_Type', max_length=10, blank=True, null=True)  # Field name made lowercase.
    voucher_no = models.CharField(db_column='Voucher_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_servicetype = models.CharField(db_column='Cust_ServiceType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    Cust_Classid = models.ForeignKey(CustomerClass, on_delete=models.PROTECT, null=True)
    Cust_titleid = models.ForeignKey(CustomerTitle, on_delete=models.PROTECT, null=True)
    cust_class = models.CharField(db_column='Cust_Class', max_length=20, blank=True, null=True)  # Field name made lowercase.
    age_range0 = models.BooleanField(db_column='Age_Range0',null=True)  # Field name made lowercase.
    age_range1 = models.BooleanField(db_column='Age_Range1',null=True)  # Field name made lowercase.
    age_range2 = models.BooleanField(db_column='Age_Range2',null=True)  # Field name made lowercase.
    age_range3 = models.BooleanField(db_column='Age_Range3',null=True)  # Field name made lowercase.
    age_range4 = models.BooleanField(db_column='Age_Range4',null=True)  # Field name made lowercase.
    Cust_Sourceid  = models.ForeignKey(Source, on_delete=models.PROTECT, null=True, blank=True)
    cust_source = models.CharField(db_column='Cust_Source', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cust_refer = models.CharField(db_column='Cust_Refer', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_age = models.CharField(db_column='Cust_Age', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_password = models.CharField(db_column='Cust_Password', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT,null=True) #, null=True, blank=True
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    modified_date = models.DateTimeField(db_column='Modified_date', blank=True, null=True)  # Field name made lowercase.
    cust_cardno = models.CharField(db_column='Cust_CardNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    issue_date = models.DateTimeField(db_column='Issue_Date', blank=True, null=True)  # Field name made lowercase.
    cust_point = models.FloatField(db_column='Cust_Point',null=True)  # Field name made lowercase.
    iscorporate = models.BooleanField(db_column='IsCorporate',null=True)  # Field name made lowercase.
    cust_linkcode = models.CharField(db_column='Cust_LinkCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    corporatecust = models.CharField(db_column='CorporateCust', max_length=50,null=True)  # Field name made lowercase.
    dateofreg = models.DateTimeField(db_column='DateofReg', blank=True, null=True)  # Field name made lowercase.
    create_logno = models.CharField(db_column='Create_LogNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    create_date = models.DateTimeField(db_column='Create_Date', blank=True, null=True)  # Field name made lowercase.
    modify_date = models.DateTimeField(db_column='Modify_Date', blank=True, null=True)  # Field name made lowercase.
    modify_logno = models.CharField(db_column='Modify_LogNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    referby = models.CharField(db_column='ReferBy', max_length=60, blank=True, null=True)  # Field name made lowercase.
    cust_referby_code = models.CharField(db_column='Cust_ReferBy_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_state = models.CharField(db_column='Cust_State', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_country = models.CharField(db_column='Cust_Country', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_group = models.CharField(db_column='Cust_Group', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_title = models.CharField(db_column='Cust_Title', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_pic_b = models.BinaryField(db_column='Cust_Pic_B', blank=True, null=True)  # Field name made lowercase.
    cust_group2 = models.CharField(db_column='Cust_Group2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_group3 = models.CharField(db_column='Cust_Group3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    skin_type = models.CharField(db_column='Skin_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    product_group = models.CharField(db_column='Product_Group', max_length=50, blank=True, null=True)  # Field name made lowercase.
    anniversary = models.DateTimeField(db_column='Anniversary', blank=True, null=True)  # Field name made lowercase.
    phone4 = models.CharField(max_length=50, blank=True, null=True)
    staff_service = models.CharField(db_column='Staff_Service', max_length=225, blank=True, null=True)  # Field name made lowercase.
    cust_weight = models.CharField(db_column='Cust_Weight', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cust_height = models.CharField(db_column='Cust_Height', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cust_agegroup = models.CharField(db_column='Cust_AgeGroup', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cust_sn = models.CharField(db_column='Cust_SN', max_length=30, blank=True, null=True)  # Field name made lowercase.
    cust_language = models.CharField(db_column='Cust_Language', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_location = models.CharField(db_column='Cust_Location', max_length=50, blank=True, null=True)  # Field name made lowercase.
    custclass_changedate = models.DateTimeField(db_column='CustClass_ChangeDate', blank=True, null=True)  # Field name made lowercase.
    cardexpiry_date = models.DateTimeField(db_column='CardExpiry_Date', blank=True, null=True)  # Field name made lowercase.
    or_key = models.CharField(db_column='OR_KEY', max_length=20, blank=True, null=True)  # Field name made lowercase.
    clonecustcode = models.CharField(db_column='CloneCustCode', max_length=200, blank=True, null=True)  # Field name made lowercase.
    sgn_block = models.CharField(db_column='Sgn_Block', max_length=255, blank=True, null=True)  # Field name made lowercase.
    sgn_unitno = models.CharField(db_column='Sgn_UnitNo', max_length=255, blank=True, null=True)  # Field name made lowercase.
    sgn_street = models.CharField(db_column='Sgn_Street', max_length=255, blank=True, null=True)  # Field name made lowercase.
    externalvipprofile = models.BooleanField(db_column='ExternalVipProfile',null=True)  # Field name made lowercase.
    custallowsendsms = models.BooleanField(db_column='CustAllowSendSMS',null=True)  # Field name made lowercase.
    potential_cust = models.BooleanField(null=True)
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cb_trmt = models.FloatField(db_column='CB_TRMT', blank=True, null=True)  # Field name made lowercase.
    cb_cn = models.FloatField(db_column='CB_CN', blank=True, null=True)  # Field name made lowercase.
    cb_pp = models.FloatField(db_column='CB_PP', blank=True, null=True)  # Field name made lowercase.
    cust_point_value = models.FloatField(db_column='Cust_Point_Value', blank=True, null=True)  # Field name made lowercase.
    appt_remark = models.CharField(db_column='Appt_Remark', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    pronetocomplain = models.BooleanField(db_column='ProneToComplain', blank=True, null=True,default=False)  # Field name made lowercase.
    customersign = models.BinaryField(db_column='customerSign', blank=True, null=True)  # Field name made lowercase.
    issensitiveskin = models.BooleanField(db_column='isSensitiveSkin', blank=True, null=True)  # Field name made lowercase.
    iseczema = models.BooleanField(db_column='isEczema', blank=True, null=True)  # Field name made lowercase.
    patientno = models.CharField(db_column='PatientNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    passport = models.CharField(db_column='Passport', max_length=50, blank=True, null=True)  # Field name made lowercase.
    medicalhistory = models.TextField(db_column='medicalHistory', blank=True, null=True)  # Field name made lowercase.
    cust_fb = models.CharField(db_column='cust_FB', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_used_point = models.FloatField(db_column='Cust_Used_Point', blank=True, null=True)  # Field name made lowercase.
    cust_bal_point = models.FloatField(db_column='Cust_Bal_Point', blank=True, null=True)  # Field name made lowercase.
    productusedpoints = models.FloatField(db_column='ProductUsedPoints', blank=True, null=True)  # Field name made lowercase.
    serviceusedpoints = models.FloatField(db_column='ServiceUsedPoints', blank=True, null=True)  # Field name made lowercase.
    productpoints = models.FloatField(db_column='ProductPoints', blank=True, null=True)  # Field name made lowercase.
    servicepoints = models.FloatField(db_column='ServicePoints', blank=True, null=True)  # Field name made lowercase.
    brandusedpoints = models.FloatField(db_column='BrandUsedPoints', blank=True, null=True)  # Field name made lowercase.
    brandpoints = models.FloatField(db_column='BrandPoints', blank=True, null=True)  # Field name made lowercase.
    pdpastatus = models.BooleanField(db_column='pdpaStatus', blank=True, null=True)  # Field name made lowercase.
    fcmtoken = models.CharField(db_column='FCMToken', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nickname = models.CharField(db_column='NickName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    modifiedby = models.CharField(db_column='modifiedBy', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cust_therapist_id = models.ForeignKey('cl_table.Employee', on_delete=models.PROTECT,null=True,related_name='customer_therapist')
    cust_consultant_id = models.ForeignKey('cl_table.Employee', on_delete=models.PROTECT,null=True,related_name='customer_consultant')
    cust_consultant = models.CharField(max_length=20, blank=True, null=True)
    cust_consultantname = models.CharField(db_column='cust_consultantName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    residencetype = models.CharField(db_column='residenceType', max_length=20, blank=True, null=True)  # Field name made lowercase.
    customerpassword = models.CharField(db_column='customerPassword', max_length=50, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    last_visit =  models.DateTimeField(null=True)
    upcoming_appointments = models.CharField(max_length=1000, null=True)
    prepaid_card = models.FloatField( null=True)
    creditnote =  models.FloatField( null=True)
    voucher_available =  models.CharField(max_length=1000, null=True)
    oustanding_payment = models.FloatField(null=True)

    cardno1 = models.CharField(max_length=20, blank=True, null=True)
    cardno2 = models.CharField(max_length=20, blank=True, null=True)
    cardno3 = models.CharField(max_length=20, blank=True, null=True)
    cardno4 = models.CharField(max_length=20, blank=True, null=True)
    cardno5 = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'Customer'
        unique_together = (('cust_code','cust_email','cust_phone1','cust_phone2'),)
        # unique_together = (('cust_code'),)


    def __str__(self):
        return str(self.cust_name) 

class Images(models.Model):

    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    services = models.ForeignKey('cl_table.Stock', on_delete=models.CASCADE, blank=True, null=True)
    item_sitelist = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.CASCADE,blank=True, null=True)
    image = models.ImageField(upload_to='img')

    class Meta:
        db_table = 'Images'


    def __str__(self):
        return str(self.image.name) 

class TreatmentAccount(models.Model):
    
    TYPE = [
        ('Deposit', 'Deposit'),
        ('Top Up', 'Top Up'),
        ('Sales','Sales'),
    ]

    SA_STATUS = [
        ('SA', 'SA'), # SA-Sales
        ('VOID', 'VOID'), # VT-Void Transaction
        ('SU', 'SU'), # SU-Suspend
    ]

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    Cust_Codeid = models.ForeignKey(Customer, on_delete=models.PROTECT,  null=True)
    cust_code = models.CharField(db_column='Cust_Code',  max_length=20, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    description = models.CharField(db_column='Description', max_length=100, null=True)  # Field name made lowercase.
    ref_no = models.CharField(db_column='Ref_No', max_length=20, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=10, blank=True, null=True, choices=TYPE)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    balance = models.FloatField(db_column='Balance', null=True)  # Field name made lowercase.
    user_name = models.CharField(db_column='User_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    User_Nameid  = models.ForeignKey(Fmspw, on_delete=models.PROTECT,  null=True)
    sa_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    ref_transacno = models.CharField(db_column='Ref_Transacno', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20,null=True)
    qty = models.IntegerField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    outstanding = models.FloatField(db_column='Outstanding', blank=True, null=True)  # Field name made lowercase.
    deposit = models.FloatField(db_column='Deposit', blank=True, null=True)  # Field name made lowercase.
    treatment_parentcode = models.CharField(db_column='Treatment_ParentCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    treatment_code = models.CharField(db_column='Treatment_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cas_logno = models.CharField(max_length=20, blank=True, null=True)
    sa_status = models.CharField(max_length=5, blank=True, null=True,choices=SA_STATUS)
    mac_code = models.CharField(max_length=15, blank=True, null=True)
    cas_name = models.CharField(max_length=60, blank=True, null=True)
    sa_staffno = models.CharField(max_length=100, null=True)
    sa_staffname = models.CharField(max_length=600, blank=True, null=True)
    next_paydate = models.DateTimeField(db_column='Next_PayDate', blank=True, null=True)  # Field name made lowercase.
    hasduedate = models.BooleanField(db_column='HasDueDate', null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', null=True)  # Field name made lowercase.
    lpackage = models.BooleanField(db_column='lPackage', null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, null=True)  # Field name made lowercase.
    treat_code = models.CharField(db_column='Treat_Code', max_length=50, null=True)  # Field name made lowercase.
    focreason = models.TextField(db_column='focReason', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    treatment_master = models.ForeignKey('cl_table.Treatment_Master', on_delete=models.PROTECT, null=True)
    itemcart = models.ForeignKey('custom.ItemCart', on_delete=models.PROTECT,null=True)

    class Meta:
        db_table = 'Treatment_Account'
        # unique_together = (('cust_code', 'description', 'ref_no', 'balance', 'sa_transacno', 'sa_staffno', 'dt_lineno', 'site_code', 'treat_code'),)
    
    def __str__(self):
        return str(self.description)

class CreditNote(models.Model):
    STATUS = [
        ('OPEN', 'OPEN'),
        ('CLOSE', 'CLOSE'),
    ]

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(db_column='sa_Date', blank=True, null=True,auto_now_add=True)  # Field name made lowercase.
    treatment_code = models.CharField(db_column='Treatment_Code', max_length=20)  # Field name made lowercase.
    treatment_name = models.CharField(db_column='Treatment_Name', max_length=200, blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    treatment_parentcode = models.CharField(db_column='Treatment_ParentCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=10, blank=True, null=True,choices=STATUS)  # Field name made lowercase.
    credit_code = models.CharField(db_column='Credit_Code', max_length=20)  # Field name made lowercase.
    balance = models.FloatField(db_column='Balance', blank=True, null=True)  # Field name made lowercase.
    deposit_type = models.CharField(db_column='Deposit_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50)  # Field name made lowercase.
    treat_code = models.CharField(db_column='Treat_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Credit_Note'
        # unique_together = (('treatment_code', 'credit_code', 'site_code'),)

    def __str__(self):
        return str(self.credit_code)

class ReverseHdr(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    reverse_no = models.CharField(db_column='Reverse_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reverse_date = models.DateTimeField(db_column='Reverse_Date', blank=True, null=True,auto_now_add=True)  # Field name made lowercase.
    reverse_time = models.DateTimeField(db_column='Reverse_Time', blank=True, null=True,auto_now_add=True)  # Field name made lowercase.
    staff_code = models.CharField(db_column='Staff_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    staff_name = models.CharField(db_column='Staff_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    has_adjustment = models.BooleanField(db_column='Has_Adjustment', blank=True, null=True)  # Field name made lowercase.
    adjustment_value = models.FloatField(db_column='Adjustment_Value', blank=True, null=True)  # Field name made lowercase.
    credit_note_amt = models.FloatField(db_column='Credit_Note_Amt', blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=50, blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=50, blank=True, null=True)  # Field name made lowercase.
    total_balance = models.FloatField(db_column='Total_Balance', blank=True, null=True)  # Field name made lowercase.
    ref_creditnote = models.CharField(db_column='Ref_CreditNote', max_length=20, blank=True, null=True)  # Field name made lowercase.
    reason1 = models.CharField(db_column='Reason1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason2 = models.CharField(db_column='Reason2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason3 = models.CharField(db_column='Reason3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason4 = models.CharField(db_column='Reason4', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reason_adj_value1 = models.FloatField(db_column='Reason_Adj_Value1', blank=True, null=True)  # Field name made lowercase.
    reason_adj_value2 = models.FloatField(db_column='Reason_Adj_Value2', blank=True, null=True)  # Field name made lowercase.
    reason_adj_value3 = models.FloatField(db_column='Reason_Adj_Value3', blank=True, null=True)  # Field name made lowercase.
    reason_adj_value4 = models.FloatField(db_column='Reason_Adj_Value4', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Reverse_Hdr'

    def __str__(self):
        return str(self.reverse_no)    

class ReverseDtl(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    treatment_no = models.CharField(db_column='Treatment_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    treatment_desc = models.CharField(db_column='Treatment_Desc', max_length=250, blank=True, null=True)  # Field name made lowercase.
    treatment_price = models.FloatField(db_column='Treatment_Price', blank=True, null=True)  # Field name made lowercase.
    transac_no = models.CharField(db_column='Transac_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    reverse_no = models.CharField(db_column='Reverse_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Reverse_Dtl'

    def __str__(self):
        return str(self.treatment_desc)

class CnRefund(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    rfn_trans_no = models.CharField(db_column='RFN_Trans_No', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cn_no = models.CharField(db_column='CN_No', max_length=20, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    staff_code = models.CharField(db_column='Staff_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    transac_no = models.CharField(db_column='Transac_No', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rfn_date = models.DateTimeField(db_column='RFN_Date', blank=True, null=True)  # Field name made lowercase.
    rfn_before_amt = models.FloatField(db_column='RFN_Before_Amt', blank=True, null=True)  # Field name made lowercase.
    rfn_adjust_amt = models.FloatField(db_column='RFN_Adjust_Amt', blank=True, null=True)  # Field name made lowercase.
    rfn_new_amt = models.FloatField(db_column='RFN_New_Amt', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'CN_Refund'

    def __str__(self):
        return str(self.rfn_trans_no)

class PrepaidAccount(models.Model):
    SA_STATUS = [
        ('DEPOSIT', 'DEPOSIT'),
        ('TOPUP', 'TOPUP'),
        ('SA','SA'),
        ('VT','VT'),
    ]

    id = models.BigAutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    pp_no = models.CharField(db_column='PP_NO',  max_length=50, null=True)  # Field name made lowercase.
    pp_type = models.CharField(db_column='PP_TYPE', max_length=50, null=True)  # Field name made lowercase.
    pp_desc = models.CharField(db_column='PP_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(db_column='SA_DATE', blank=True, null=True,auto_now_add=True)  # Field name made lowercase.
    start_date = models.DateTimeField(db_column='START_DATE', blank=True, null=True,auto_now_add=True)  # Field name made lowercase.
    exp_date = models.DateTimeField(db_column='EXP_DATE', blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='CUST_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='CUST_NAME', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pp_amt = models.FloatField(db_column='PP_AMT', blank=True, null=True)  # Field name made lowercase.
    pp_bonus = models.FloatField(db_column='PP_BONUS', blank=True, null=True)  # Field name made lowercase.
    pp_total = models.FloatField(db_column='PP_TOTAL', blank=True, null=True)  # Field name made lowercase.
    transac_no = models.CharField(db_column='TRANSAC_NO', max_length=50)  # Field name made lowercase.
    item_no = models.CharField(db_column='ITEM_NO', max_length=50)  # Field name made lowercase.
    use_amt = models.FloatField(db_column='USE_AMT', null=True)  # Field name made lowercase.
    remain = models.FloatField(db_column='REMAIN', null=True)  # Field name made lowercase.
    ref1 = models.CharField(db_column='REF1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ref2 = models.CharField(db_column='REF2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    status = models.BooleanField(db_column='STATUS', null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='SITE_CODE', max_length=50, null=True)  # Field name made lowercase.
    sa_status = models.CharField(db_column='SA_STATUS', max_length=50, blank=True, null=True,choices=SA_STATUS)  # Field name made lowercase.
    exp_status = models.BooleanField(db_column='EXP_STATUS', null=True)  # Field name made lowercase.
    voucher_no = models.CharField(db_column='VOUCHER_NO', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isvoucher = models.BooleanField(db_column='ISVOUCHER', null=True)  # Field name made lowercase.
    has_deposit = models.BooleanField(db_column='HAS_DEPOSIT', null=True)  # Field name made lowercase.
    topup_amt = models.FloatField(db_column='TopUp_AMT', blank=True, null=True)  # Field name made lowercase.
    outstanding = models.FloatField(db_column='Outstanding', null=True)  # Field name made lowercase.
    active_deposit_bonus = models.BooleanField(db_column='Active_Deposit_Bonus', null=True)  # Field name made lowercase.
    topup_no = models.CharField(db_column='TopUp_No', max_length=50, null=True)  # Field name made lowercase.
    topup_date = models.DateTimeField(db_column='TopUp_Date', blank=True, null=True)  # Field name made lowercase.
    line_no = models.BigIntegerField(db_column='Line_No', null=True)  # Field name made lowercase.
    edit_date = models.DateTimeField(db_column='Edit_Date', null=True,auto_now_add=True)  # Field name made lowercase.
    cas_logno = models.CharField(db_column='Cas_LogNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    staff_name = models.CharField(db_column='Staff_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    staff_no = models.CharField(db_column='Staff_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pp_type2 = models.CharField(db_column='PP_TYPE2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    condition_type1 = models.CharField(db_column='Condition_TYPE1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    pos_daud_lineno = models.IntegerField(db_column='POS_DAUD_LineNo', blank=True, null=True)  # Field name made lowercase.
    mac_uid_ref = models.CharField(db_column='MAC_UID_Ref', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lpackage = models.BooleanField(db_column='lPackage')  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    package_code_lineno = models.IntegerField(db_column='Package_Code_LineNo', blank=True, null=True)  # Field name made lowercase.
    prepaid_disc_type = models.CharField(db_column='Prepaid_Disc_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    prepaid_disc_percent = models.FloatField(db_column='Prepaid_Disc_Percent', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    Cust_Codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True)
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    Item_Codeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT, null=True) 
    item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    
    class Meta:
        db_table = 'Prepaid_Account'
        # unique_together = (('pp_no', 'pp_type', 'transac_no', 'item_no', 'use_amt', 'remain', 'site_code', 'topup_no', 'line_no', 'edit_date'),)

    def __str__(self):
        return str(self.pp_no)

class DepositAccount(models.Model):
    TYPE = [
        ('Deposit', 'Deposit'),
        ('Top Up', 'Top Up'),
        ('CANCEL', 'CANCEL'),
    ]

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code',  max_length=20, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    type = models.CharField(db_column='Type', max_length=10, blank=True, null=True,choices=TYPE)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    balance = models.FloatField(db_column='Balance', blank=True, null=True)  # Field name made lowercase.
    user_name = models.CharField(db_column='User_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sa_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    qty = models.IntegerField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    outstanding = models.FloatField(db_column='Outstanding', blank=True, null=True)  # Field name made lowercase.
    deposit = models.FloatField(db_column='Deposit', blank=True, null=True)  # Field name made lowercase.
    cas_logno = models.CharField(max_length=20, blank=True, null=True)
    mac_code = models.CharField(max_length=20, blank=True, null=True)
    cas_name = models.CharField(max_length=60, blank=True, null=True)
    sa_staffno = models.CharField(max_length=50, blank=True, null=True)
    sa_staffname = models.CharField(max_length=60, blank=True, null=True)
    deposit_type = models.CharField(db_column='Deposit_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(db_column='sa_Transacno', max_length=50, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.
    ref_code = models.CharField(db_column='Ref_Code', max_length=100, null=True)  # Field name made lowercase.
    sa_status = models.CharField(db_column='SA_STATUS', max_length=50, blank=True, null=True)  # Field name made lowercase.
    item_barcode = models.CharField(db_column='Item_Barcode', max_length=50, null=True)  # Field name made lowercase.
    item_description = models.CharField(db_column='Item_Description', max_length=80, blank=True, null=True)  # Field name made lowercase.
    treat_code = models.CharField(db_column='Treat_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    void_link = models.CharField(db_column='Void_Link', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lpackage = models.BooleanField(db_column='lPackage', null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    Cust_Codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT, null=True)
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, null=True)  # Field name made lowercase.
    Item_Codeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT, null=True) 
    item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ref_transacno = models.CharField(db_column='Ref_Transacno', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ref_productcode = models.CharField(db_column='Ref_ProductCode', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Deposit_Account'
        # unique_together = (('cust_code', 'sa_transacno', 'ref_code', 'item_barcode', 'dt_lineno'),)

    def __str__(self):
        return str(self.treat_code)

class PrepaidAccountCondition(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    pp_no = models.CharField(db_column='PP_NO',  max_length=50, null=True)  # Field name made lowercase.
    pp_type = models.CharField(db_column='PP_TYPE', max_length=50, null=True)  # Field name made lowercase.
    pp_desc = models.CharField(db_column='PP_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    p_itemtype = models.CharField(db_column='P_ItemType', max_length=50, null=True)  # Field name made lowercase.
    item_code = models.CharField(max_length=20, null=True)
    conditiontype1 = models.CharField(db_column='ConditionType1', max_length=20, null=True)  # Field name made lowercase.
    conditiontype2 = models.CharField(db_column='ConditionType2', max_length=20, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    rate = models.CharField(db_column='Rate', max_length=20, blank=True, null=True)  # Field name made lowercase.
    membercardnoaccess = models.BooleanField(db_column='MemberCardNoAccess', null=True)  # Field name made lowercase.
    use_amt = models.FloatField(db_column='Use_Amt', blank=True, null=True)  # Field name made lowercase.
    remain = models.FloatField(db_column='Remain', blank=True, null=True)  # Field name made lowercase.
    pos_daud_lineno = models.FloatField(db_column='POS_Daud_LineNo', null=True)  # Field name made lowercase.
    system_remark = models.CharField(db_column='System_Remark', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lpackage = models.BooleanField(db_column='lPackage', null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    package_code_lineno = models.IntegerField(db_column='Package_Code_LineNo', blank=True, null=True)  # Field name made lowercase.
    creditvalueshared = models.BooleanField(db_column='CreditValueShared', null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Prepaid_Account_Condition'
        # unique_together = (('pp_no', 'pp_type', 'p_itemtype', 'item_code', 'conditiontype1', 'conditiontype2', 'pos_daud_lineno'),)

    def __str__(self):
        return str(self.pp_no)

class VoucherCondition(models.Model):
    itemid = models.AutoField(db_column='ItemID',primary_key=True)  # Field name made lowercase.
    p_itemtype = models.CharField(db_column='P_ItemType', max_length=14, blank=True, null=True)  # Field name made lowercase.
    item_code = models.CharField(max_length=20, blank=True, null=True)
    conditiontype1 = models.CharField(db_column='ConditionType1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    conditiontype2 = models.CharField(db_column='ConditionType2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    amount = models.DecimalField(db_column='Amount', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    rate = models.CharField(db_column='Rate', max_length=10, blank=True, null=True)  # Field name made lowercase.
    membercardnoaccess = models.BooleanField(db_column='MemberCardNoAccess', blank=True, null=True)  # Field name made lowercase.
    # line_no = models.IntegerField(db_column='Line_No', blank=True, null=True)  # Field name made lowercase.
    # isactive = models.BooleanField(db_column='IsActive')  # Field name made lowercase.

    class Meta:
        db_table = 'Voucher_condition' 

    def __str__(self):
        return str(self.item_code)           

class ItemUom(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    uom_code = models.CharField(db_column='UOM_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    uom_desc = models.CharField(db_column='UOM_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    uom_user = models.CharField(db_column='UOM_User', max_length=20, blank=True, null=True)  # Field name made lowercase.
    uom_date = models.DateTimeField(db_column='UOM_Date', blank=True, null=True)  # Field name made lowercase.
    uom_time = models.DateTimeField(db_column='UOM_Time', blank=True, null=True)  # Field name made lowercase.
    uom_isactive = models.BooleanField(db_column='UOM_Isactive', blank=True, null=True, default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_UOM'   

    def __str__(self):
        return str(self.uom_code)

class Holditemdetail(models.Model):
    STATUS = [
        ('OPEN', 'OPEN'),
        ('CLOSE', 'CLOSE'),
        ('VOID', 'VOID'),
    ]
    
    hi_no = models.AutoField(db_column='HI_no',primary_key=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    sa_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    cas_logno = models.CharField(db_column='Cas_LogNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemsite_code = models.CharField(db_column='ItemSite_Code',  max_length=50, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(db_column='sa_TransacNo', max_length=50, null=True)  # Field name made lowercase.
    transacamt = models.FloatField(db_column='TRANSACAMT', blank=True, null=True)  # Field name made lowercase.
    itemno = models.CharField(db_column='ItemNo', max_length=50, null=True)  # Field name made lowercase.
    hi_staffno = models.CharField(db_column='HI_staffNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hi_itemdesc = models.CharField(db_column='HI_ItemDesc', max_length=200, blank=True, null=True)  # Field name made lowercase.
    hi_price = models.FloatField(db_column='HI_Price', blank=True, null=True)  # Field name made lowercase.
    hi_amt = models.FloatField(db_column='HI_Amt', blank=True, null=True)  # Field name made lowercase.
    hi_qty = models.IntegerField(db_column='HI_Qty', blank=True, null=True)  # Field name made lowercase.
    hi_discamt = models.FloatField(db_column='HI_discAmt', blank=True, null=True)  # Field name made lowercase.
    hi_discpercent = models.FloatField(db_column='HI_discPercent', blank=True, null=True)  # Field name made lowercase.
    hi_discdesc = models.CharField(db_column='HI_discDesc', max_length=100, blank=True, null=True)  # Field name made lowercase.
    hi_staffname = models.CharField(db_column='HI_StaffName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hi_lineno = models.IntegerField(db_column='HI_LineNo', null=True)  # Field name made lowercase.
    hi_uom = models.CharField(db_column='HI_UOM', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hold_item = models.BooleanField(db_column='Hold_Item', null=True)  # Field name made lowercase.
    hi_deposit = models.FloatField(db_column='HI_deposit', blank=True, null=True)  # Field name made lowercase.
    holditemqty = models.IntegerField(db_column='HoldItemQty', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=50, blank=True, null=True,choices=STATUS)  # Field name made lowercase.
    sa_custno = models.CharField(db_column='sa_CustNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sa_custname = models.CharField(db_column='sa_Custname', max_length=50, blank=True, null=True)  # Field name made lowercase.
    history_line = models.IntegerField(db_column='History_Line', null=True)  # Field name made lowercase.
    hold_type = models.CharField(db_column='Hold_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    product_issues_no = models.CharField(db_column='Product_Issues_No', max_length=20, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'HoldItemDetail'
        # unique_together = (('itemsite_code', 'sa_transacno', 'itemno', 'hi_lineno', 'product_issues_no'),)
    
    def __str__(self):
        return str(self.hi_itemdesc)

class Customervoucher(models.Model):
    id = models.AutoField(primary_key=True)  # Field name made lowercase.
    customermobile = models.CharField(db_column='customerMobile', max_length=20, null=True)  # Field name made lowercase.
    firstname = models.CharField(db_column='firstName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='lastName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    outletname = models.CharField(db_column='outletName', max_length=20, blank=True, null=True)  # Field name made lowercase.
    vouchertype = models.CharField(db_column='voucherType', max_length=200, blank=True, null=True)  # Field name made lowercase.
    voucheramounttype = models.CharField(db_column='voucherAmountType', max_length=200, blank=True, null=True)  # Field name made lowercase.
    voucheramount = models.IntegerField(db_column='voucherAmount', blank=True, null=True)  # Field name made lowercase.
    promocode = models.CharField(db_column='promoCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(max_length=200, blank=True, null=True)
    redeemdate = models.DateTimeField(db_column='redeemDate', blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(max_length=20, blank=True, null=True)
    voucher_no = models.CharField(max_length=20, blank=True, null=True)
    voucher_name = models.CharField(max_length=20, blank=True, null=True)
    sitecode = models.CharField(db_column='siteCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'CustomerVoucher'
    
    def __str__(self):
        return str(self.voucher_name)

class PosHaud(models.Model):
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
    cas_logno = models.CharField( max_length=20, null=True)
    sa_transacno = models.CharField(max_length=20, null=True)
    sa_date = models.DateTimeField(blank=True, null=True, default=timezone.now, editable=False)
    sa_time = models.DateTimeField(blank=True, null=True, default=timezone.now, editable=False)
    sa_postdate = models.DateTimeField(blank=True, null=True)
    sa_status = models.CharField(max_length=5, blank=True, null=True,choices=SA_STATUS)
    sa_remark = models.CharField(max_length=50, blank=True, null=True)
    sa_totamt = models.FloatField(blank=True, null=True)
    sa_totqty = models.IntegerField(db_column='sa_totQty', blank=True, null=True)  # Field name made lowercase.
    sa_totdisc = models.FloatField(blank=True, null=True)
    sa_totgst = models.FloatField(blank=True, null=True)
    sa_totservice = models.FloatField(blank=True, null=True)
    sa_amtret = models.FloatField(blank=True, null=True)
    sa_staffnoid = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True)
    sa_staffno = models.CharField(max_length=100, blank=True, null=True)
    sa_staffname = models.CharField(max_length=600, blank=True, null=True)
    sa_custnoid = models.ForeignKey(Customer, on_delete=models.PROTECT,  null=True)
    sa_custno = models.CharField(max_length=20, null=True)
    sa_custname = models.CharField(max_length=60, blank=True, null=True)
    sa_reason = models.IntegerField(db_column='sa_Reason', blank=True, null=True)  # Field name made lowercase.
    sa_discuser = models.CharField(db_column='sa_DiscUser', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sa_discno = models.CharField(max_length=10, blank=True, null=True)
    sa_discdesc = models.CharField(max_length=20, blank=True, null=True)
    sa_discvalue = models.FloatField(blank=True, null=True)
    sa_discamt = models.FloatField(blank=True, null=True)
    sa_disctotal = models.FloatField(db_column='sa_discTotal', blank=True, null=True)  # Field name made lowercase.
    ItemSite_Codeid  = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=10, null=True)  # Field name made lowercase.
    sa_cardno = models.CharField(db_column='sa_CardNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    seat_no = models.CharField(db_column='Seat_No', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sa_depositamt = models.FloatField(db_column='sa_depositAmt', blank=True, null=True)  # Field name made lowercase.
    sa_chargeamt = models.FloatField(db_column='sa_chargeAmt', blank=True, null=True)  # Field name made lowercase.
    isvoid = models.BooleanField(db_column='IsVoid', null=True,default=False)  # Field name made lowercase.
    void_refno = models.CharField(db_column='Void_RefNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    payment_remarks = models.CharField(db_column='Payment_Remarks', max_length=100, blank=True, null=True)  # Field name made lowercase.
    next_payment = models.CharField(db_column='Next_Payment', max_length=20, blank=True, null=True)  # Field name made lowercase.
    next_appt = models.CharField(db_column='Next_Appt', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_transacamt = models.FloatField(db_column='sa_TransacAmt', blank=True, null=True)  # Field name made lowercase.
    appt_time = models.TimeField(db_column='Appt_Time', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hold_item = models.BooleanField(db_column='Hold_Item', blank=True, null=True)  # Field name made lowercase.
    sa_discecard = models.FloatField(db_column='sa_discECard', blank=True, null=True)  # Field name made lowercase.
    holditemqty = models.IntegerField(db_column='HoldItemQty', null=True)  # Field name made lowercase.
    walkin = models.BooleanField(db_column='WalkIn', null=True)  # Field name made lowercase.
    cust_sig = models.BinaryField(db_column='Cust_Sig', blank=True, null=True)  # Field name made lowercase.
    sa_round = models.FloatField(db_column='sa_Round', blank=True, null=True)  # Field name made lowercase.
    balance_point = models.FloatField(db_column='Balance_Point', blank=True, null=True)  # Field name made lowercase.
    total_outstanding = models.FloatField(db_column='Total_Outstanding', blank=True, null=True)  # Field name made lowercase.
    total_itemhold_qty = models.FloatField(db_column='Total_ItemHold_Qty', blank=True, null=True)  # Field name made lowercase.
    total_prepaid_amt = models.FloatField(db_column='Total_Prepaid_Amt', blank=True, null=True)  # Field name made lowercase.
    total_voucher_avalable = models.FloatField(db_column='Total_Voucher_Avalable', blank=True, null=True)  # Field name made lowercase.
    total_course_summary = models.CharField(db_column='Total_Course_Summary', max_length=20, blank=True, null=True)  # Field name made lowercase.
    total_cn_amt = models.FloatField(db_column='Total_CN_Amt', blank=True, null=True)  # Field name made lowercase.
    previous_pts = models.FloatField(db_column='Previous_pts', blank=True, null=True)  # Field name made lowercase.
    today_pts = models.FloatField(db_column='Today_pts', blank=True, null=True)  # Field name made lowercase.
    total_balance_pts = models.FloatField(db_column='Total_Balance_pts', blank=True, null=True)  # Field name made lowercase.
    trans_user_loginid = models.ForeignKey('cl_table.Fmspw', on_delete=models.PROTECT,null=True)
    trans_user_login = models.CharField(db_column='Trans_User_Login', max_length=20, blank=True, null=True)  # Field name made lowercase.
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno_ref = models.CharField(db_column='SA_TransacNo_Ref', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_transacno_type = models.CharField(db_column='SA_TransacNo_Type', max_length=20, choices=SA_TRANSACNO_TYPE,blank=True, null=True)  # Field name made lowercase.
    cust_sig_path = models.CharField(db_column='Cust_Sig_Path', max_length=250, blank=True, null=True)  # Field name made lowercase.
    trans_reason = models.CharField(db_column='Trans_Reason', max_length=200, blank=True, null=True)  # Field name made lowercase.
    trans_remark = models.CharField(db_column='Trans_Remark', max_length=200, blank=True, null=True)  # Field name made lowercase.
    trans_rw_point_ratio = models.FloatField(db_column='Trans_RW_Point_Ratio', blank=True, null=True)  # Field name made lowercase.
    sa_trans_do_no = models.CharField(db_column='SA_Trans_DO_No', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_transacno_title = models.CharField(db_column='SA_TransacNo_Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    issuestrans_user_login = models.CharField(db_column='IssuesTrans_User_Login', max_length=20, blank=True, null=True)  # Field name made lowercase.
    trans_packagecode = models.CharField(db_column='Trans_PackageCode', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    trans_value = models.FloatField(db_column='Trans_Value', blank=True, null=True)  # Field name made lowercase.
    trans_pay = models.FloatField(db_column='Trans_Pay', blank=True, null=True)  # Field name made lowercase.
    trans_outstanding = models.FloatField(db_column='Trans_Outstanding', blank=True, null=True)  # Field name made lowercase.
    used_pts = models.FloatField(db_column='Used_pts', blank=True, null=True)  # Field name made lowercase.
    earn_pts = models.FloatField(db_column='Earn_pts', blank=True, null=True)  # Field name made lowercase.
    expire_soon_date_1 = models.DateTimeField(db_column='Expire_Soon_Date_1', blank=True, null=True)  # Field name made lowercase.
    expire_soon_point_1 = models.FloatField(db_column='Expire_Soon_Point_1', blank=True, null=True)  # Field name made lowercase.
    expire_soon_date_2 = models.DateTimeField(db_column='Expire_Soon_Date_2', blank=True, null=True)  # Field name made lowercase.
    expire_soon_point_2 = models.FloatField(db_column='Expire_Soon_Point_2', blank=True, null=True)  # Field name made lowercase.
    expire_soon_date_3 = models.DateTimeField(db_column='Expire_Soon_Date_3', blank=True, null=True)  # Field name made lowercase.
    expire_soon_point_3 = models.FloatField(db_column='Expire_Soon_Point_3', blank=True, null=True)  # Field name made lowercase.
    expire_soon_date_4 = models.DateTimeField(db_column='Expire_Soon_Date_4', blank=True, null=True)  # Field name made lowercase.
    expire_soon_point_4 = models.FloatField(db_column='Expire_Soon_Point_4', blank=True, null=True)  # Field name made lowercase.
    expire_soon_date_5 = models.DateTimeField(db_column='Expire_Soon_Date_5', blank=True, null=True)  # Field name made lowercase.
    expire_soon_point_5 = models.FloatField(db_column='Expire_Soon_Point_5', blank=True, null=True)  # Field name made lowercase.
    expire_soon_remark = models.CharField(db_column='Expire_Soon_Remark', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    expire_soon_remark_point = models.FloatField(db_column='Expire_Soon_Remark_Point', blank=True, null=True)  # Field name made lowercase.
    transignurl = models.TextField(db_column='tranSignUrl', blank=True, null=True)  # Field name made lowercase.
    onlinepurchase = models.BooleanField(db_column='onlinePurchase', blank=True, null=True)  # Field name made lowercase.
    deliverystatus = models.IntegerField(db_column='deliveryStatus', blank=True, null=True)  # Field name made lowercase.
    deliveryaddress = models.IntegerField(db_column='deliveryAddress', blank=True, null=True)  # Field name made lowercase.
    smsout = models.BooleanField(db_column='smsOut', blank=True, null=True)  # Field name made lowercase.
    smstdout = models.BooleanField(db_column='smsTDOut', blank=True, null=True)  # Field name made lowercase.
    smsinvoiceout = models.BooleanField(db_column='smsInvoiceOut', blank=True, null=True)  # Field name made lowercase.
    emailtdout = models.BooleanField(db_column='emailTDOut', blank=True, null=True)  # Field name made lowercase.
    emailinvoiceout = models.BooleanField(db_column='emailInvoiceOut', blank=True, null=True)  # Field name made lowercase.
    paymentdone = models.BooleanField(db_column='paymentDone', blank=True, null=True)  # Field name made lowercase.
    smspaymentout = models.BooleanField(db_column='smsPaymentOut', blank=True, null=True)  # Field name made lowercase.
    emailpaymentout = models.BooleanField(db_column='emailPaymentOut', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(default=timezone.now, editable=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    Appointment = models.ForeignKey('cl_table.Appointment', on_delete=models.PROTECT,null=True)
    cart_id = models.CharField(max_length=20, null=True)

    class Meta:
        db_table = 'pos_haud'
        # unique_together = (('cas_logno', 'sa_transacno', 'sa_custno', 'itemsite_code'),)

    def __str__(self):
        return str(self.cas_name)
    

class PosDaud(models.Model):
    
    DT_STATUS = [
        ('SA', 'SA'), # SA-Sales
        ('VT', 'VT'), # VT-Void Transaction
        ('SU', 'SU'), # SU-Suspend
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
    sa_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    sa_time = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    cas_logno = models.CharField( max_length=20, blank=True,  null=True)
    sa_transacno = models.CharField(max_length=20,blank=True, null=True)
    dt_status = models.CharField(max_length=5, blank=True,choices=DT_STATUS, null=True)
    dt_itemnoid = models.ForeignKey('cl_table.Stock', on_delete=models.CASCADE,  null=True)
    dt_itemno = models.CharField(max_length=20, blank=True, null=True)
    dt_itemdesc = models.CharField(max_length=200, blank=True,  null=True)
    dt_price = models.FloatField(blank=True, null=True)
    dt_promoprice = models.FloatField(db_column='dt_PromoPrice', blank=True, null=True)  # Field name made lowercase.
    dt_amt = models.FloatField(blank=True, null=True)
    dt_qty = models.IntegerField(blank=True, null=True)
    dt_discamt = models.FloatField(db_column='dt_discAmt', blank=True, null=True)  # Field name made lowercase.
    dt_discpercent = models.FloatField(db_column='dt_discPercent', blank=True, null=True)  # Field name made lowercase.
    dt_discdesc = models.CharField(db_column='dt_discDesc', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dt_discno = models.CharField(max_length=10, blank=True, null=True)
    dt_remark = models.CharField(max_length=60, blank=True, null=True)
    dt_Staffnoid = models.ForeignKey(Employee, on_delete=models.PROTECT,  null=True)
    dt_staffno = models.CharField(db_column='dt_Staffno', max_length=100, blank=True, null=True)  # Field name made lowercase.
    dt_staffname = models.CharField(db_column='dt_StaffName', max_length=600, blank=True, null=True)  # Field name made lowercase.
    dt_reason = models.IntegerField(db_column='dt_Reason', blank=True, null=True)  # Field name made lowercase.
    dt_discuser = models.CharField(db_column='dt_DiscUser', max_length=50, blank=True, null=True)  # Field name made lowercase.
    dt_combocode = models.CharField(db_column='dt_ComboCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ItemSite_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT,  null=True)
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=10,blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo',blank=True, null=True)  # Field name made lowercase.
    dt_stockupdate = models.CharField(db_column='dt_StockUpdate', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dt_stockremark = models.CharField(db_column='dt_StockRemark', max_length=200, blank=True, null=True)  # Field name made lowercase.
    dt_uom = models.CharField(db_column='dt_UOM', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isfoc = models.BooleanField(db_column='IsFoc', blank=True, null=True)  # Field name made lowercase.
    item_remarks = models.CharField(db_column='Item_Remarks', max_length=500, blank=True, null=True)  # Field name made lowercase.
    next_payment = models.CharField(db_column='Next_Payment', max_length=20, blank=True, null=True)  # Field name made lowercase.
    next_appt = models.CharField(db_column='Next_Appt', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dt_transacamt = models.FloatField(db_column='dt_TransacAmt', blank=True, null=True)  # Field name made lowercase.
    dt_deposit = models.FloatField(blank=True, null=True)
    appt_time = models.TimeField(db_column='Appt_Time', max_length=10, blank=True, null=True)  # Field name made lowercase.
    hold_item_out = models.BooleanField(db_column='Hold_Item_Out',blank=True, null=True)  # Field name made lowercase.
    issue_date = models.DateTimeField(db_column='Issue_Date', blank=True, null=True)  # Field name made lowercase.
    hold_item = models.BooleanField(db_column='Hold_Item',blank=True, null=True)  # Field name made lowercase.
    holditemqty = models.IntegerField(db_column='HoldItemQty', blank=True, null=True)  # Field name made lowercase.
    st_ref_treatmentcode = models.CharField(db_column='ST_Ref_TreatmentCode', max_length=500, blank=True, null=True)  # Field name made lowercase.
    item_status_code = models.CharField(db_column='Item_Status_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    first_trmt_done = models.BooleanField(db_column='First_Trmt_Done',blank=True,  null=True)  # Field name made lowercase.
    first_trmt_done_staff_code = models.CharField(db_column='First_Trmt_Done_Staff_Code', max_length=200, blank=True, null=True)  # Field name made lowercase.
    first_trmt_done_staff_name = models.CharField(db_column='First_Trmt_Done_Staff_Name', max_length=200, blank=True, null=True)  # Field name made lowercase.
    record_detail_type = models.CharField(db_column='Record_Detail_Type', max_length=50,choices=RECORD_DETAIL_TYPE, blank=True, null=True)  # Field name made lowercase.
    trmt_done_staff_code = models.CharField(db_column='Trmt_Done_Staff_Code', max_length=200, blank=True, null=True)  # Field name made lowercase.
    trmt_done_staff_name = models.CharField(db_column='Trmt_Done_Staff_Name', max_length=200, blank=True, null=True)  # Field name made lowercase.
    trmt_done_id = models.CharField(db_column='Trmt_Done_ID', max_length=50, blank=True, null=True)  # Field name made lowercase.
    trmt_done_type = models.CharField(db_column='Trmt_Done_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    topup_service_trmt_code = models.CharField(db_column='TopUp_Service_Trmt_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    topup_product_treat_code = models.CharField(db_column='TopUp_Product_Treat_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    topup_prepaid_trans_code = models.CharField(db_column='TopUp_Prepaid_Trans_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    topup_prepaid_type_code = models.CharField(db_column='TopUp_Prepaid_Type_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    voucher_link_cust = models.BooleanField(db_column='Voucher_Link_Cust',blank=True, null=True)  # Field name made lowercase.
    voucher_no = models.CharField(db_column='Voucher_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    update_prepaid_bonus = models.BooleanField(db_column='Update_Prepaid_Bonus',blank=True,  null=True)  # Field name made lowercase.
    deduct_commission = models.BooleanField(db_column='Deduct_Commission',blank=True, null=True)  # Field name made lowercase.
    deduct_comm_refline = models.IntegerField(db_column='Deduct_comm_refLine', blank=True, null=True)  # Field name made lowercase.
    gst_amt_collect = models.FloatField(db_column='GST_Amt_Collect', blank=True, null=True)  # Field name made lowercase.
    topup_prepaid_pos_trans_lineno = models.IntegerField(db_column='TopUp_Prepaid_POS_Trans_LineNo', blank=True, null=True)  # Field name made lowercase.
    open_pp_uid_ref = models.CharField(db_column='OPEN_PP_UID_REF', max_length=50, blank=True, null=True)  # Field name made lowercase.
    compound_code = models.CharField(db_column='COMPOUND_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    topup_outstanding = models.FloatField(db_column='TopUp_Outstanding', blank=True, null=True)  # Field name made lowercase.
    t1_tax_code = models.CharField(db_column='T1_Tax_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    t1_tax_amt = models.FloatField(db_column='T1_Tax_Amt', blank=True, null=True)  # Field name made lowercase.
    t2_tax_code = models.CharField(db_column='T2_Tax_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    t2_tax_amt = models.FloatField(db_column='T2_Tax_Amt', blank=True, null=True)  # Field name made lowercase.
    dt_grossamt = models.CharField(db_column='dt_GrossAmt', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dt_topup_old_outs_amt = models.FloatField(db_column='dt_TopUp_Old_Outs_Amt', blank=True, null=True)  # Field name made lowercase.
    dt_topup_new_outs_amt = models.FloatField(db_column='dt_TopUp_New_Outs_Amt', blank=True, null=True)  # Field name made lowercase.
    dt_td_tax_amt = models.FloatField(db_column='dt_TD_Tax_Amt', blank=True, null=True)  # Field name made lowercase.
    earnedpoints = models.DecimalField(db_column='earnedPoints', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    earnedtype = models.CharField(db_column='earnedType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    redeempoints = models.DecimalField(db_column='redeemPoints', max_digits=18, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    redeemtype = models.CharField(db_column='redeemType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    trmt_bal = models.FloatField(db_column='Trmt_Bal', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    Appointment = models.ForeignKey('cl_table.Appointment', on_delete=models.PROTECT,null=True )
    itemcart = models.ForeignKey('custom.ItemCart', on_delete=models.PROTECT,null=True)
    staffs = models.CharField(db_column='Staffs', max_length=300, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'pos_daud'
        # unique_together = (('cas_logno', 'sa_transacno', 'dt_itemdesc', 'itemsite_code', 'dt_lineno', 'st_ref_treatmentcode'),)
    
    def __str__(self):
        return str(self.sa_transacno)

class PosTaud(models.Model):
    pay_no = models.AutoField(primary_key=True)
    mac_code = models.CharField(max_length=15, blank=True, null=True)
    sa_date = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    sa_time = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    sa_transacno = models.CharField( max_length=20,blank=True,  null=True)
    cas_logno = models.CharField(max_length=20,blank=True, null=True)
    pay_groupid = models.ForeignKey('cl_table.PayGroup', on_delete=models.PROTECT, null=True)
    pay_group = models.CharField(max_length=40, blank=True, null=True)
    pay_typeid = models.ForeignKey('cl_table.PAYTABLE', on_delete=models.PROTECT,null=True)
    pay_type = models.CharField(max_length=30, blank=True, null=True)
    pay_desc = models.CharField(db_column='pay_Desc', max_length=200, blank=True, null=True)  # Field name made lowercase.
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
    pay_status = models.BooleanField(blank=True,null=True)
    pay_actamt = models.FloatField(blank=True, null=True)
    ItemSIte_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    itemsite_code = models.CharField(db_column='ItemSIte_Code', max_length=10, null=True)  # Field name made lowercase.
    paychange = models.FloatField(db_column='PayChange', blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField( null=True)
    pay_gst_amt_collect = models.FloatField(db_column='Pay_GST_Amt_Collect', blank=True, null=True)  # Field name made lowercase.
    pay_gst = models.FloatField(db_column='PAY_GST', blank=True, null=True)  # Field name made lowercase.
    posdaudlineno = models.CharField(db_column='POSDAUDLineNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    posdaudlineamountassign = models.CharField(db_column='posdaudLineAmountAssign', max_length=500, blank=True, null=True)  # Field name made lowercase.
    posdaudlineamountused = models.FloatField(db_column='posdaudLineAmountUsed', blank=True, null=True)  # Field name made lowercase.
    voucher_name = models.CharField(db_column='Voucher_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    pp_bal = models.FloatField(db_column='PP_Bal', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    billed_by = models.ForeignKey(Fmspw, on_delete=models.PROTECT, null=True)
    subtotal = models.FloatField( null=True)
    tax = models.FloatField( null=True)
    discount_amt = models.FloatField( null=True)
    billable_amount = models.FloatField( null=True)
    Appointment = models.ForeignKey('cl_table.Appointment', on_delete=models.PROTECT, blank=True, null=True)
    credit_debit = models.BooleanField(default=False,  null=True)
    points = models.BooleanField(default=False,  null=True)
    prepaid = models.BooleanField(default=False,  null=True)
    pay_premise = models.BooleanField(default=False, null=True)
    is_voucher = models.BooleanField(default=False, null=True)
    voucher_no = models.CharField(db_column='Voucher_No', max_length=50,  null=True)  # Field name made lowercase.
    voucher_amt = models.FloatField( null=True)


    class Meta:
        db_table = 'pos_taud'
        # unique_together = (('sa_transacno', 'cas_logno', 'itemsite_code', 'dt_lineno'),)

    def __str__(self):
        return str(self.sa_transacno)

class DepositType(models.Model):
    sys_id = models.AutoField(db_column='Sys_ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField( max_length=20,null=True)
    pay_group = models.CharField(db_column='Pay_Group', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pay_type = models.CharField(db_column='Pay_Type', max_length=30, blank=True, null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    card_no = models.CharField(max_length=200,null=True)
    pay_desc = models.CharField(max_length=100,null=True)
    pay_tendcurr = models.CharField(max_length=10, blank=True, null=True)
    pay_tendrate = models.FloatField(blank=True, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pos_taud_lineno = models.IntegerField(db_column='POS_TAUD_LineNo',null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Deposit_Type'
        # unique_together = (('sa_transacno', 'card_no', 'pay_desc', 'pos_taud_lineno'),)

    def __str__(self):
        return str(self.sa_transacno)

class Multistaff(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField(db_column='sa_transacNo',  max_length=20, null=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20, null=True)  # Field name made lowercase.
    emp_code = models.CharField(db_column='Emp_Code', max_length=20, null=True)  # Field name made lowercase.
    ratio = models.FloatField(db_column='Ratio', null=True)  # Field name made lowercase.
    salesamt = models.FloatField(db_column='SalesAmt', null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=20, null=True)  # Field name made lowercase.
    isdelete = models.BooleanField(db_column='IsDelete', null=True)  # Field name made lowercase.
    role = models.CharField(db_column='Role', max_length=50, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='Dt_LineNo', null=True)  # Field name made lowercase.
    level_group_code = models.CharField(db_column='Level_group_code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'MultiStaff'
        # unique_together = (('sa_transacno', 'item_code', 'emp_code', 'role', 'dt_lineno'),)

    def __str__(self):
        return str(self.emp_code)

class ItemHelper(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code',  max_length=20, null=True)  # Field name made lowercase.
    item_name = models.CharField(db_column='Item_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    line_no = models.IntegerField(db_column='Line_No', null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20, null=True)
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    helper_name = models.CharField(db_column='Helper_Name', max_length=600, blank=True, null=True)  # Field name made lowercase.
    helper_code = models.CharField(db_column='Helper_Code', max_length=200, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField( null=True,auto_now=True)
    site_code = models.CharField(db_column='Site_code', max_length=10, null=True)  # Field name made lowercase.
    cas_logno = models.CharField(db_column='Cas_logno', max_length=20, blank=True, null=True)  # Field name made lowercase.
    share_amt = models.FloatField(db_column='Share_Amt', blank=True, null=True)  # Field name made lowercase.
    helper_transacno = models.CharField(db_column='Helper_transacno', max_length=20, null=True)  # Field name made lowercase.
    system_remark = models.CharField(db_column='System_Remark', max_length=100, blank=True, null=True)  # Field name made lowercase.
    wp1 = models.FloatField(db_column='WP1', blank=True, null=True)  # Field name made lowercase.
    wp2 = models.FloatField(db_column='WP2', blank=True, null=True)  # Field name made lowercase.
    wp3 = models.FloatField(db_column='WP3', blank=True, null=True)  # Field name made lowercase.
    td_type_code = models.CharField(db_column='TD_Type_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    td_type_short_desc = models.CharField(db_column='TD_Type_Short_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_helper'
        # unique_together = (('item_code', 'line_no', 'sa_transacno', 'helper_code', 'sa_date', 'site_code', 'helper_transacno'),)
    
    def __str__(self):
        return str(self.item_name)

class TmpItemHelper(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_name = models.CharField(db_column='Item_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    line_no = models.IntegerField(db_column='Line_No', blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20, blank=True, null=True)
    amount = models.FloatField(db_column='Amount', blank=True, null=True)  # Field name made lowercase.
    helper_name = models.CharField(db_column='Helper_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    helper_code = models.CharField(db_column='Helper_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    wp1 = models.FloatField(db_column='WP1', blank=True, null=True)  # Field name made lowercase.
    wp2 = models.FloatField(db_column='WP2', blank=True, null=True)  # Field name made lowercase.
    wp3 = models.FloatField(db_column='WP3', blank=True, null=True)  # Field name made lowercase.
    mac_uid_ref = models.CharField(db_column='MAC_UID_Ref', max_length=50, blank=True, null=True)  # Field name made lowercase.
    td_type_code = models.CharField(db_column='TD_Type_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    td_type_short_desc = models.CharField(db_column='TD_Type_Short_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    itemcart = models.ForeignKey('custom.ItemCart', on_delete=models.PROTECT,null=True, blank=True)
    helper_id = models.ForeignKey(Employee, on_delete=models.PROTECT,null=True)
    appt_fr_time = models.TimeField(db_column='Appt_Fr_time', null=True)  # Field name made lowercase.
    appt_to_time = models.TimeField(db_column='Appt_To_time', null=True)  # Field name made lowercase.
    add_duration = models.TimeField(null=True)
    Room_Codeid  = models.ForeignKey('custom.Room', on_delete=models.PROTECT,null=True)
    Source_Codeid = models.ForeignKey(Source, on_delete=models.PROTECT,null=True)
    new_remark = models.CharField(db_column='New_Remark', max_length=800, null=True)  # Field name made lowercase.
    times = models.CharField(db_column='Times', max_length=10, blank=True, null=True)  # Field name made lowercase.
    treatment_no = models.CharField(db_column='Treatment_No', max_length=10, blank=True, null=True)  # Field name made lowercase.
    workcommpoints = models.FloatField(db_column='WorkCommPoints', blank=True, null=True,default=0.0)  # Field name made lowercase.
    treatment = models.ForeignKey('cl_table.Treatment', on_delete=models.PROTECT,null=True, blank=True)


    class Meta:
        db_table = 'Tmp_Item_helper'
    
    # def __str__(self):
    #     return str(self.item_name)    

class ReceiptAr(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    receipt_no = models.CharField(db_column='Receipt_no', max_length=20, null=True)  # Field name made lowercase.
    invoice_no = models.CharField(db_column='Invoice_No', max_length=20,null=True)  # Field name made lowercase.
    receipt_date = models.DateTimeField(db_column='Receipt_Date',null=True)  # Field name made lowercase.
    amount = models.FloatField(db_column='aMOUNT', blank=True, null=True)  # Field name made lowercase.
    emp_code = models.CharField(db_column='Emp_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_name = models.CharField(db_column='Emp_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Receipt_AR'
    
    def __str__(self):
        return str(self.receipt_no)    

class PosDisc(models.Model):
    id = models.AutoField(primary_key=True)
    sa_transacno = models.CharField(max_length=50,null=True)
    dt_itemno = models.CharField(db_column='dt_ItemNo', max_length=50,null=True)  # Field name made lowercase.
    disc_amt = models.FloatField(db_column='Disc_Amt', blank=True, null=True)  # Field name made lowercase.
    disc_percent = models.FloatField(db_column='Disc_Percent', blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo',null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=200, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50,null=True)  # Field name made lowercase.
    dt_date = models.DateTimeField(db_column='dt_Date',null=True,auto_now_add=True)  # Field name made lowercase.
    dt_status = models.CharField(max_length=50,null=True)
    dt_auto = models.BooleanField(db_column='dt_Auto',null=True)  # Field name made lowercase.
    line_no = models.IntegerField(db_column='Line_no',null=True)  # Field name made lowercase.
    disc_user = models.CharField(db_column='Disc_User', max_length=250, blank=True, null=True)  # Field name made lowercase.
    lnow = models.BooleanField(db_column='lNow',null=True)  # Field name made lowercase.
    dt_price = models.FloatField(db_column='dt_Price', blank=True, null=True)  # Field name made lowercase.
    istransdisc = models.BooleanField(db_column='IsTransDisc',null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Pos_Disc'
    
    def __str__(self):
        return str(self.dt_itemno)
    
class PayGroup(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    pay_group_code = models.CharField(db_column='PAY_GROUP_CODE', max_length=20, null=True)  # Field name made lowercase.
    pay_group_pic = models.BinaryField(db_column='PAY_GROUP_PIC', blank=True, null=True)  # Field name made lowercase.
    seq = models.IntegerField(db_column='SEQ', blank=True, null=True)  # Field name made lowercase.
    iscreditcard = models.BooleanField(db_column='IsCreditCard', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'PAY_GROUP'
    
    def __str__(self):
        return str(self.pay_group_code)    
    
class Paytable(models.Model):
    GT_GROUP = [
        ('GT1', 'GT1'),
        ('GT2', 'GT2'),
    ]
    
    pay_code = models.CharField(max_length=10, blank=True, null=True)
    pay_description = models.CharField(max_length=50, blank=True, null=True)
    pay_groupid =  models.ForeignKey('cl_table.PayGroup', on_delete=models.PROTECT,null=True)
    pay_group = models.CharField(max_length=15, blank=True, null=True)
    pay_id = models.AutoField(primary_key=True)
    pay_isactive = models.BooleanField(default=True)
    gt_group = models.CharField(db_column='GT_Group', max_length=50, blank=True, null=True,choices=GT_GROUP)  # Field name made lowercase.
    rw_usebp = models.BooleanField(db_column='RW_useBP', null=True)  # Field name made lowercase.
    iscomm = models.BooleanField(db_column='IsComm', null=True)  # Field name made lowercase.
    show_in_report = models.BooleanField(db_column='Show_In_Report', null=True)  # Field name made lowercase.
    bank_charges = models.FloatField(db_column='Bank_Charges', blank=True, null=True)  # Field name made lowercase.
    eps = models.FloatField(db_column='EPS', blank=True, null=True)  # Field name made lowercase.
    sequence = models.IntegerField(db_column='Sequence', blank=True, null=True)  # Field name made lowercase.
    voucher_payment_control = models.BooleanField(db_column='Voucher_Payment_Control', null=True)  # Field name made lowercase.
    pay_type_pic = models.BinaryField(db_column='PAY_TYPE_PIC', blank=True, null=True)  # Field name made lowercase.
    pay_is_gst = models.BooleanField(db_column='PAY_IS_GST', null=True)  # Field name made lowercase.
    creditcardcharges = models.DecimalField(db_column='CreditCardCharges', max_digits=18, decimal_places=2, null=True)  # Field name made lowercase.
    onlinepaymentcharges = models.DecimalField(db_column='OnlinePaymentCharges', max_digits=18, decimal_places=2, null=True)  # Field name made lowercase.
    iscreditcard = models.BooleanField(db_column='IsCreditCard', blank=True, null=True)  # Field name made lowercase.
    isonlinepayment = models.BooleanField(db_column='IsOnlinePayment', blank=True, null=True)  # Field name made lowercase.
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    account_mapping = models.BooleanField(db_column='Account_Mapping', blank=True, null=True)  # Field name made lowercase.
    open_cashdrawer = models.BooleanField(db_column='Open_CashDrawer', null=True)  # Field name made lowercase.
    iscustapptpromo = models.BooleanField(db_column='IsCustApptPromo', null=True)  # Field name made lowercase.
    isvoucher_extvoucher = models.BooleanField(db_column='IsVoucher_ExtVoucher', null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'PAYTABLE'
    
    def __str__(self):
        return str(self.pay_code)

class ItemDept(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_status = models.BooleanField(default=True)
    itm_seq = models.IntegerField(db_column='ITM_SEQ', blank=True, null=True)  # Field name made lowercase.
    allowcashsales = models.BooleanField(db_column='AllowCashSales', null=True)  # Field name made lowercase.
    itm_showonsales = models.BooleanField(db_column='ITM_ShowOnSales', null=True)  # Field name made lowercase.
    isfirsttrial = models.BooleanField(db_column='IsFirstTrial', blank=True, null=True)  # Field name made lowercase.
    is_voucher = models.BooleanField(db_column='Is_Voucher', null=True)  # Field name made lowercase.
    is_prepaid = models.BooleanField(db_column='Is_Prepaid', null=True)  # Field name made lowercase.
    is_package = models.BooleanField(db_column='Is_Package', null=True)  # Field name made lowercase.
    is_retailproduct = models.BooleanField(db_column='Is_RetailProduct', null=True)  # Field name made lowercase.
    is_salonproduct = models.BooleanField(db_column='Is_SalonProduct', null=True)  # Field name made lowercase.
    validity_period = models.IntegerField(db_column='Validity_Period', blank=True, null=True)  # Field name made lowercase.
    is_service = models.BooleanField(db_column='Is_Service', null=True)  # Field name made lowercase.
    dept_pic_b = models.BinaryField(db_column='Dept_PIC_B', blank=True, null=True)  # Field name made lowercase.
    is_compound = models.BooleanField(db_column='Is_Compound', null=True)  # Field name made lowercase.
    dept_pic = models.CharField(db_column='Dept_PIC', max_length=100, blank=True, null=True)  # Field name made lowercase.
    vilidity_from_date = models.DateTimeField(db_column='Vilidity_From_Date', blank=True, null=True)  # Field name made lowercase.
    vilidity_to_date = models.DateTimeField(db_column='Vilidity_To_date', blank=True, null=True)  # Field name made lowercase.
    vilidity_from_time = models.DateTimeField(db_column='Vilidity_From_Time', blank=True, null=True)  # Field name made lowercase.
    vilidity_to_time = models.DateTimeField(db_column='Vilidity_To_Time', blank=True, null=True)  # Field name made lowercase.
    process_remark = models.CharField(db_column='Process_Remark', max_length=250, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    deptpic = models.ImageField(upload_to='img', null=True)

    class Meta:
        db_table = 'Item_Dept'

    def __str__(self):
        return str(self.itm_desc)

class ItemRange(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_desc = models.CharField(max_length=100, blank=True, null=True)
    itm_status = models.BooleanField(blank=True, null=True,default=True)
    itm_seq = models.IntegerField(db_column='itm_SEQ', blank=True, null=True)  # Field name made lowercase.
    itm_brand = models.CharField(max_length=20, blank=True, null=True)
    itm_Deptid  = models.ForeignKey(ItemDept, on_delete=models.PROTECT, null=True)
    itm_dept = models.CharField(db_column='itm_Dept', max_length=10, blank=True, null=True)  # Field name made lowercase.
    isproduct = models.BooleanField(db_column='isProduct', null=True)  # Field name made lowercase.
    pic_path = models.CharField(db_column='PIC_Path', max_length=255, blank=True, null=True)  # Field name made lowercase.
    prepaid_for_product = models.BooleanField(db_column='Prepaid_For_Product',null=True)  # Field name made lowercase.
    prepaid_for_service = models.BooleanField(db_column='Prepaid_For_Service',null=True)  # Field name made lowercase.
    prepaid_for_all = models.BooleanField(db_column='Prepaid_For_All',null=True)  # Field name made lowercase.
    isservice = models.BooleanField(db_column='IsService',null=True)  # Field name made lowercase.
    isvoucher = models.BooleanField(db_column='IsVoucher',null=True)  # Field name made lowercase.
    isprepaid = models.BooleanField(db_column='IsPrepaid',null=True)  # Field name made lowercase.
    iscompound = models.BooleanField(db_column='IsCompound',null=True)  # Field name made lowercase.
    process_remark = models.CharField(db_column='Process_Remark', max_length=250, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Range'

    def __str__(self):
        return str(self.itm_desc)     

class ItemClass(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    itm_seq = models.IntegerField(db_column='ITM_SEQ', blank=True, null=True)  # Field name made lowercase.
    process_remark = models.CharField(db_column='Process_Remark', max_length=250, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'item_Class'

    def __str__(self):
        return str(self.itm_desc) 

class ItemDiv(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_isactive = models.BooleanField(default=True)
    itm_seq = models.IntegerField(db_column='ITM_SEQ', null=True)  # Field name made lowercase.
    status_code = models.CharField(db_column='Status_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    process_remark = models.CharField(db_column='Process_Remark', max_length=250, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Div'

    def __str__(self):
        return str(self.itm_desc)

class ItemType(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_name = models.CharField(max_length=40, blank=True, null=True)
    itm_removable = models.BooleanField(db_column='ITM_REMOVABLE', null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'item_type'

    def __str__(self):
        return str(self.itm_name)

class ItemColor(models.Model):
    color_id = models.AutoField(db_column='Color_ID', primary_key=True)  # Field name made lowercase.
    color_code = models.CharField(db_column='Color_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    color_desc = models.CharField(db_column='Color_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    color_shortdesc = models.CharField(db_column='Color_ShortDesc', max_length=10, blank=True, null=True)  # Field name made lowercase.
    color_user = models.CharField(db_column='Color_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    color_date = models.DateTimeField(db_column='Color_Date', blank=True, null=True)  # Field name made lowercase.
    color_time = models.DateTimeField(db_column='Color_Time', blank=True, null=True)  # Field name made lowercase.
    color_isactive = models.BooleanField(db_column='Color_Isactive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Color'
    
    def __str__(self):
        return str(self.color_desc)
           
class ItemSizepack(models.Model):
    sizepack_id = models.AutoField(db_column='SizePack_ID', primary_key=True)  # Field name made lowercase.
    sizepack_code = models.CharField(db_column='SizePack_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sizepack_desc = models.CharField(db_column='SizePack_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sizepack_shortdesc = models.CharField(db_column='SizePack_ShortDesc', max_length=10, blank=True, null=True)  # Field name made lowercase.
    sizepack_user = models.CharField(db_column='SizePack_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sizepack_date = models.DateTimeField(db_column='SizePack_Date', blank=True, null=True)  # Field name made lowercase.
    sizepack_time = models.DateTimeField(db_column='SizePack_Time', blank=True, null=True)  # Field name made lowercase.
    sizepack_isactive = models.BooleanField(db_column='SizePack_Isactive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_SizePack'
    
    def __str__(self):
        return str(self.SizePack_Desc)
         
class ItemSize(models.Model):
    size_id = models.AutoField(db_column='Size_ID', primary_key=True)  # Field name made lowercase.
    sizepack_code = models.CharField(db_column='SizePack_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    size_code = models.CharField(db_column='Size_Code', max_length=6, blank=True, null=True)  # Field name made lowercase.
    size_desc = models.CharField(db_column='Size_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    size_shortdesc = models.CharField(db_column='Size_ShortDesc', max_length=10, blank=True, null=True)  # Field name made lowercase.
    size_unit = models.CharField(db_column='Size_Unit', max_length=50, blank=True, null=True)  # Field name made lowercase.
    size_width = models.CharField(db_column='Size_Width', max_length=50, blank=True, null=True)  # Field name made lowercase.
    size_height = models.CharField(db_column='Size_Height', max_length=50, blank=True, null=True)  # Field name made lowercase.
    size_tickness = models.CharField(db_column='Size_Tickness', max_length=50, blank=True, null=True)  # Field name made lowercase.
    size_lenght = models.CharField(db_column='Size_Lenght', max_length=50, blank=True, null=True)  # Field name made lowercase.
    size_user = models.CharField(db_column='Size_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    size_date = models.DateTimeField(db_column='Size_Date', blank=True, null=True)  # Field name made lowercase.
    size_time = models.DateTimeField(db_column='Size_Time', blank=True, null=True)  # Field name made lowercase.
    size_isactive = models.BooleanField(db_column='Size_Isactive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Size'
    
    def __str__(self):
        return str(self.size_desc)    

class ItemSeason(models.Model):
    season_id = models.AutoField(db_column='Season_ID', primary_key=True)  # Field name made lowercase.
    season_code = models.CharField(db_column='Season_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    season_desc = models.CharField(db_column='Season_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    season_shortdesc = models.CharField(db_column='Season_ShortDesc', max_length=10, blank=True, null=True)  # Field name made lowercase.
    season_user = models.CharField(db_column='Season_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    season_date = models.DateTimeField(db_column='Season_Date', blank=True, null=True)  # Field name made lowercase.
    season_time = models.DateTimeField(db_column='Season_Time', blank=True, null=True)  # Field name made lowercase.
    season_isactive = models.BooleanField(db_column='Season_Isactive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'item_Season'
    
    def __str__(self):
        return str(self.season_desc)

class ItemFabric(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_status = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Fabric'
    
    def __str__(self):
        return str(self.itm_desc)    

class ItemBrand(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_code = models.CharField(max_length=10, blank=True, null=True)
    itm_desc = models.CharField(max_length=40, blank=True, null=True)
    itm_status = models.BooleanField(default=True)
    itm_seq = models.IntegerField(db_column='ITM_SEQ', blank=True, null=True)  # Field name made lowercase.
    pic_path = models.CharField(db_column='PIC_PATH', max_length=256, blank=True, null=True)  # Field name made lowercase.
    voucher_for_sales = models.BooleanField(db_column='Voucher_For_Sales', null=True)  # Field name made lowercase.
    voucher_brand = models.BooleanField(db_column='Voucher_Brand', null=True)  # Field name made lowercase.
    retail_product_brand = models.BooleanField(db_column='Retail_Product_Brand', null=True)  # Field name made lowercase.
    prepaid_brand = models.BooleanField(db_column='Prepaid_Brand', null=True)  # Field name made lowercase.
    process_remark = models.CharField(db_column='Process_Remark', max_length=250, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Brand'

    def __str__(self):
        return str(self.itm_desc) 
    
class VoucherValidperiod(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    voucher_valid_code = models.CharField(db_column='Voucher_Valid_Code', max_length=20, null=True)  # Field name made lowercase.
    voucher_valid_desc = models.CharField(db_column='Voucher_Valid_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    voucher_valid_days = models.FloatField(db_column='Voucher_Valid_Days', blank=True, null=True)  # Field name made lowercase.
    voucher_valid_isactive = models.BooleanField(db_column='Voucher_Valid_IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Voucher_ValidPeriod'

    def __str__(self):
        return str(self.voucher_valid_desc)
           
class PrepaidValidperiod(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    prepaid_valid_code = models.CharField(db_column='Prepaid_Valid_Code', max_length=20, null=True)  # Field name made lowercase.
    prepaid_valid_desc = models.CharField(db_column='Prepaid_Valid_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    prepaid_valid_days = models.FloatField(db_column='Prepaid_Valid_Days', blank=True, null=True)  # Field name made lowercase.
    prepaid_valid_isactive = models.BooleanField(db_column='Prepaid_Valid_IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Prepaid_ValidPeriod'
    
    def __str__(self):
        return str(self.prepaid_valid_code)

class Stock(models.Model):
    item_no = models.AutoField(db_column='Item_no',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(max_length=20, blank=True, null=True)
    itm_icid = models.FloatField(db_column='Itm_ICID', blank=True, null=True)  # Field name made lowercase.
    itm_code = models.CharField(db_column='Itm_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Item_Divid = models.ForeignKey(ItemDiv, on_delete=models.PROTECT,null=True)
    item_div = models.CharField(db_column='Item_Div', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Item_Deptid = models.ForeignKey(ItemDept, on_delete=models.PROTECT,null=True)
    item_dept = models.CharField(db_column='Item_Dept', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Item_Classid = models.ForeignKey(ItemClass, on_delete=models.PROTECT, null=True)
    item_class = models.CharField(db_column='Item_Class', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_barcode = models.CharField(db_column='Item_Barcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    onhand_cst = models.FloatField(db_column='ONHAND_CST', blank=True, null=True)  # Field name made lowercase.
    item_margin = models.FloatField(db_column='Item_Margin', blank=True, null=True)  # Field name made lowercase.
    item_isactive = models.BooleanField(default=True)
    item_name = models.CharField(db_column='Item_Name', max_length=60, blank=True, null=True)  # Field name made lowercase.
    item_abbc = models.CharField(db_column='Item_abbc', max_length=60, blank=True, null=True)  # Field name made lowercase.
    item_desc = models.CharField(db_column='Item_Desc', max_length=60, blank=True, null=True)  # Field name made lowercase.
    cost_price = models.DecimalField(db_column='COST_PRICE', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    item_price = models.DecimalField(db_column='Item_Price', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    onhand_qty = models.FloatField(db_column='ONHAND_QTY', blank=True, null=True)  # Field name made lowercase.
    itm_promotionyn = models.CharField(db_column='Itm_PromotionYN', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itm_disc = models.FloatField(db_column='Itm_Disc', blank=True, null=True)  # Field name made lowercase.
    itm_commission = models.FloatField(db_column='Itm_Commission', blank=True, null=True)  # Field name made lowercase.
    Item_Typeid = models.ForeignKey(ItemType, on_delete=models.PROTECT,null=True)
    item_type = models.CharField(db_column='Item_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itm_duration = models.FloatField(db_column='Itm_Duration', blank=True, null=True)  # Field name made lowercase.
    item_price2 = models.FloatField(db_column='Item_Price2', blank=True, null=True)  # Field name made lowercase.
    item_price3 = models.FloatField(db_column='Item_Price3', blank=True, null=True)  # Field name made lowercase.
    item_price4 = models.FloatField(db_column='Item_Price4', blank=True, null=True)  # Field name made lowercase.
    item_price5 = models.FloatField(db_column='Item_Price5', blank=True, null=True)  # Field name made lowercase.
    itm_remark = models.CharField(db_column='Itm_Remark', max_length=100, blank=True, null=True)  # Field name made lowercase.
    itm_value = models.CharField(db_column='Itm_Value', max_length=10, blank=True, null=True)  # Field name made lowercase.
    itm_expiredate = models.DateTimeField(db_column='Itm_ExpireDate', blank=True, null=True)  # Field name made lowercase.
    # Itm_Statusid = models.ForeignKey('cl_table.ItemStatus', on_delete=models.PROTECT,null=True,)
    itm_status = models.CharField(db_column='Itm_Status', max_length=10, blank=True, null=True)  # Field name made lowercase.
    item_minqty = models.IntegerField(blank=True, null=True)
    item_maxqty = models.IntegerField(blank=True, null=True)
    item_onhandcost = models.CharField(db_column='item_OnHandCost', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_barcode1 = models.CharField(db_column='item_Barcode1', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_barcode2 = models.CharField(db_column='item_Barcode2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_barcode3 = models.CharField(db_column='item_Barcode3', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_marginamt = models.FloatField(blank=True, null=True)
    item_date = models.DateTimeField(blank=True, null=True)
    item_time = models.DateTimeField(blank=True, null=True)
    item_moddate = models.DateTimeField(db_column='item_ModDate', blank=True, null=True)  # Field name made lowercase.
    item_modtime = models.DateTimeField(db_column='item_ModTime', blank=True, null=True)  # Field name made lowercase.
    item_createuser = models.CharField(max_length=60, blank=True, null=True)
    item_supp = models.CharField(max_length=10, blank=True, null=True)
    item_parentcode = models.CharField(db_column='Item_Parentcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    # item_colorid = models.ForeignKey(ItemColor, on_delete=models.PROTECT,null=True)
    item_color = models.CharField(max_length=10, blank=True, null=True)
    # item_SizePackid = models.ForeignKey(ItemSizepack, on_delete=models.PROTECT,null=True)
    item_sizepack = models.CharField(db_column='item_SizePack', max_length=10, blank=True, null=True)  # Field name made lowercase.
    # item_Sizeid = models.ForeignKey(ItemSize, on_delete=models.PROTECT,null=True)
    item_size = models.CharField(db_column='item_Size', max_length=10, blank=True, null=True)  # Field name made lowercase.
    # item_Seasonid = models.ForeignKey(ItemSeason, on_delete=models.PROTECT,null=True)
    item_season = models.CharField(db_column='item_Season', max_length=10, blank=True, null=True)  # Field name made lowercase.
    # item_fabricid = models.ForeignKey(ItemFabric, on_delete=models.PROTECT,null=True)
    item_fabric = models.CharField(max_length=10, blank=True, null=True)
    # item_Brandid = models.ForeignKey(ItemBrand, on_delete=models.PROTECT,null=True)
    item_brand = models.CharField(db_column='item_Brand', max_length=10, blank=True, null=True)  # Field name made lowercase.
    lstpo_ucst = models.FloatField(db_column='LSTPO_UCST', blank=True, null=True)  # Field name made lowercase.
    lstpo_no = models.CharField(db_column='LSTPO_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    lstpo_date = models.DateTimeField(db_column='LSTPO_Date', blank=True, null=True)  # Field name made lowercase.
    item_havechild = models.BooleanField(db_column='item_haveChild', null=True)  # Field name made lowercase.
    value_applytochild = models.BooleanField(db_column='Value_ApplyToChild', null=True)  # Field name made lowercase.
    package_disc = models.FloatField(db_column='Package_Disc', blank=True, null=True)  # Field name made lowercase.
    have_package_disc = models.BooleanField(db_column='Have_Package_Disc', null=True)  # Field name made lowercase.
    pic_path = models.CharField(db_column='PIC_Path', max_length=255, blank=True, null=True)  # Field name made lowercase.
    item_foc = models.BooleanField(db_column='Item_FOC', null=True)  # Field name made lowercase.
    item_uom = models.CharField(db_column='Item_UOM', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mixbrand = models.BooleanField(db_column='MIXBRAND', null=True)  # Field name made lowercase.
    serviceretail = models.BooleanField(db_column='SERVICERETAIL', blank=True, null=True)  # Field name made lowercase.
    Item_Rangeid = models.ForeignKey(ItemRange, on_delete=models.PROTECT, null=True)
    item_range = models.CharField(db_column='Item_Range', max_length=20, blank=True, null=True)  # Field name made lowercase.
    commissionable = models.BooleanField(db_column='Commissionable', blank=True, null=True)  # Field name made lowercase.
    trading = models.BooleanField(db_column='Trading', blank=True, null=True)  # Field name made lowercase.
    cust_replenish_days = models.CharField(db_column='Cust_Replenish_Days', max_length=10, blank=True, null=True)  # Field name made lowercase.
    cust_advance_days = models.CharField(db_column='Cust_Advance_Days', max_length=10, blank=True, null=True)  # Field name made lowercase.
    salescomm = models.CharField(db_column='SalesComm', max_length=20, blank=True, null=True)  # Field name made lowercase.
    workcomm = models.CharField(db_column='WorkComm', max_length=20, blank=True, null=True)  # Field name made lowercase.
    reminder_active = models.BooleanField(db_column='Reminder_Active', blank=True, null=True)  # Field name made lowercase.
    disclimit = models.FloatField(db_column='DiscLimit', blank=True, null=True)  # Field name made lowercase.
    disctypeamount = models.BooleanField(db_column='DiscTypeAmount', blank=True, null=True)  # Field name made lowercase.
    autocustdisc = models.BooleanField(db_column='AutoCustDisc', null=True)  # Field name made lowercase.
    reorder_active = models.BooleanField(db_column='ReOrder_Active', blank=True, null=True)  # Field name made lowercase.
    reorder_minqty = models.FloatField(db_column='ReOrder_MinQty', blank=True, null=True)  # Field name made lowercase.
    service_expire_active = models.BooleanField(db_column='Service_Expire_Active', null=True)  # Field name made lowercase.
    service_expire_month = models.FloatField(db_column='Service_Expire_Month', blank=True, null=True)  # Field name made lowercase.
    treatment_limit_active = models.BooleanField(db_column='Treatment_Limit_Active', null=True)  # Field name made lowercase.
    treatment_limit_count = models.FloatField(db_column='Treatment_Limit_Count', blank=True, null=True)  # Field name made lowercase.
    limitservice_flexionly = models.BooleanField(db_column='LimitService_FlexiOnly', null=True)  # Field name made lowercase.
    salescommpoints = models.FloatField(db_column='SalesCommPoints', blank=True, null=True)  # Field name made lowercase.
    workcommpoints = models.FloatField(db_column='WorkCommPoints', blank=True, null=True)  # Field name made lowercase.
    item_price_floor = models.FloatField(db_column='Item_Price_Floor', blank=True, null=True)  # Field name made lowercase.
    voucher_value = models.FloatField(db_column='Voucher_Value', blank=True, null=True)  # Field name made lowercase.
    voucher_value_is_amount = models.BooleanField(db_column='Voucher_Value_Is_Amount', null=True)  # Field name made lowercase.
    voucher_valid_period = models.CharField(db_column='Voucher_Valid_Period', max_length=20, blank=True, null=True)  # Field name made lowercase.
    prepaid_value = models.FloatField(db_column='Prepaid_Value', blank=True, null=True)  # Field name made lowercase.
    prepaid_sell_amt = models.FloatField(db_column='Prepaid_Sell_Amt', blank=True, null=True)  # Field name made lowercase.
    prepaid_valid_period = models.CharField(db_column='Prepaid_Valid_Period', max_length=20, blank=True, null=True)  # Field name made lowercase.
    membercardnoaccess = models.BooleanField(db_column='MemberCardNoAccess', blank=True, null=True)  # Field name made lowercase.
    rpt_code = models.CharField(db_column='Rpt_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    is_gst = models.BooleanField(db_column='IS_GST', null=True)  # Field name made lowercase.
    account_code = models.CharField(db_column='Account_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    stock_pic_b = models.BinaryField(db_column='Stock_PIC_B', blank=True, null=True)  # Field name made lowercase.
    is_open_prepaid = models.BooleanField(db_column='IS_OPEN_PREPAID', null=True)  # Field name made lowercase.
    appt_wd_min = models.FloatField(db_column='Appt_WD_Min', blank=True, null=True)  # Field name made lowercase.
    service_cost = models.FloatField(db_column='Service_Cost', blank=True, null=True)  # Field name made lowercase.
    service_cost_percent = models.BooleanField(db_column='Service_Cost_Percent', null=True)  # Field name made lowercase.
    account_code_td = models.CharField(db_column='Account_Code_TD', max_length=20, blank=True, null=True)  # Field name made lowercase.
    voucher_isvalid_until_date = models.BooleanField(db_column='Voucher_IsValid_Until_Date', null=True)  # Field name made lowercase.
    voucher_valid_until_date = models.DateTimeField(db_column='Voucher_Valid_Until_Date', blank=True, null=True)  # Field name made lowercase.
    workcommholder = models.CharField(max_length=6, blank=True, null=True)
    equipmentcost = models.FloatField(blank=True, null=True)
    postatus = models.BooleanField(blank=True, null=True)
    gst_item_code = models.CharField(db_column='GST_Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    is_have_tax = models.BooleanField(db_column='IS_HAVE_TAX', null=True)  # Field name made lowercase.
    sst_item_code = models.CharField(db_column='SST_Item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    is_allow_foc = models.BooleanField(db_column='IS_ALLOW_FOC', null=True)  # Field name made lowercase.
    vilidity_from_date = models.DateTimeField(db_column='Vilidity_From_Date', blank=True, null=True)  # Field name made lowercase.
    vilidity_to_date = models.DateTimeField(db_column='Vilidity_To_date', blank=True, null=True)  # Field name made lowercase.
    vilidity_from_time = models.DateTimeField(db_column='Vilidity_From_Time', blank=True, null=True)  # Field name made lowercase.
    vilidity_to_time = models.DateTimeField(db_column='Vilidity_To_Time', blank=True, null=True)  # Field name made lowercase.
    t1_tax_code = models.CharField(db_column='T1_Tax_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    t2_tax_code = models.CharField(db_column='T2_Tax_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    prepaid_disc_type = models.CharField(db_column='Prepaid_Disc_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    prepaid_disc_percent = models.FloatField(db_column='Prepaid_Disc_Percent', blank=True, null=True)  # Field name made lowercase.
    srv_duration = models.FloatField(db_column='Srv_Duration', blank=True, null=True)  # Field name made lowercase.
    istnc = models.BooleanField(db_column='isTnc', blank=True, null=True)  # Field name made lowercase.
    voucher_template_name = models.CharField(db_column='Voucher_Template_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    autoproportion = models.BooleanField(db_column='AutoProportion', null=True)  # Field name made lowercase.
    item_pingying = models.CharField(db_column='Item_PingYing', max_length=250,  null=True,blank=True)  # New Field name made lowercase.
    process_remark = models.CharField(db_column='Process_Remark', max_length=250,  null=True,blank=True)  #New Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    sutiable_for = models.CharField(max_length=100,  null=True,blank=True)
    description = models.TextField( null=True,blank=True)
    treatment_details = models.TextField(null=True,blank=True)
    procedure = models.TextField(null=True,blank=True)
    Stock_PIC = models.ImageField(upload_to='img',null=True)
    tax = models.FloatField(null=True,blank=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Stock'

    def __str__(self):
        return str(self.item_desc)

class Skillstaff(models.Model):
    id = models.BigAutoField(db_column='Id', primary_key=True)  # Field name made lowercase.
    sitecode = models.CharField(db_column='siteCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    staffcode = models.CharField(db_column='staffCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itemcode = models.CharField(db_column='itemCode', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'skillstaff'



class ItemStocklist(models.Model):
    itemstocklist_id = models.AutoField(db_column='ItemStockList_ID', primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='Item_Code', max_length=20, null=True)  # Field name made lowercase.
    item_barcode = models.CharField(db_column='Item_Barcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    onhand_qty = models.IntegerField(db_column='ONHAND_QTY', blank=True, null=True)  # Field name made lowercase.
    itemstocklist_minqty = models.IntegerField(db_column='ItemStockList_MinQty', blank=True, null=True)  # Field name made lowercase.
    itemstocklist_maxqty = models.IntegerField(db_column='ItemStockList_MaxQty', blank=True, null=True)  # Field name made lowercase.
    onhand_cst = models.FloatField(db_column='ONHAND_CST', blank=True, null=True)  # Field name made lowercase.
    itemstocklist_onhandcost = models.FloatField(db_column='ItemStockList_OnHandCost', blank=True, null=True)  # Field name made lowercase.
    itemstocklist_unit = models.CharField(db_column='ItemStockList_Unit', max_length=10, blank=True, null=True)  # Field name made lowercase.
    itemstocklist_user = models.CharField(db_column='ItemStockList_User', max_length=10, blank=True, null=True)  # Field name made lowercase.
    itemstocklist_datetime = models.DateTimeField(db_column='ItemStockList_DateTime', blank=True, null=True)  # Field name made lowercase.
    itemstocklist_remark = models.CharField(db_column='ItemStockList_Remark', max_length=10, blank=True, null=True)  # Field name made lowercase.
    itemstocklist_posted = models.BooleanField(db_column='ItemStockList_Posted', blank=True, null=True)  # Field name made lowercase.
    itemstocklist_status = models.BooleanField(db_column='ItemStockList_Status', blank=True, null=True)  # Field name made lowercase.
    lstpo_ucst = models.FloatField(db_column='LSTPO_UCST', blank=True, null=True)  # Field name made lowercase.
    lstpo_no = models.CharField(db_column='LSTPO_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    lstpo_date = models.DateTimeField(db_column='LSTPO_DATE', blank=True, null=True)  # Field name made lowercase.
    cost_price = models.FloatField(db_column='COST_PRICE', blank=True, null=True)  # Field name made lowercase.
    itm_seq = models.DecimalField(db_column='ITM_SEQ', max_digits=18, decimal_places=0, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_StockList'

    def __str__(self):
        return str(self.item_code)

class ItemLink(models.Model):
    itm_id = models.AutoField(db_column='Itm_ID',primary_key=True)  # Field name made lowercase.
    link_code = models.CharField(db_column='LINK_CODE', max_length=20, null=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='ITEM_CODE', max_length=20, null=True)  # Field name made lowercase.
    link_desc = models.CharField(db_column='LINK_DESC', max_length=40, blank=True, null=True)  # Field name made lowercase.
    link_factor = models.FloatField(db_column='LINK_FACTOR', blank=True, null=True)  # Field name made lowercase.
    link_type = models.CharField(db_column='LINK_TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    itm_isactive = models.BooleanField(db_column='Itm_IsActive', blank=True, null=True,default=True)  # Field name made lowercase.
    rpt_code_status = models.BooleanField(db_column='Rpt_Code_Status', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Item_Link'

    def __str__(self):
        return str(self.link_code)

class ItemBatch(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='ITEM_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='SITE_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    batch_no = models.CharField(db_column='BATCH_NO', max_length=30, blank=True, null=True)  # Field name made lowercase.
    uom = models.CharField(db_column='UOM', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qty = models.FloatField(db_column='QTY', blank=True, null=True)  # Field name made lowercase.
    exp_date = models.DateTimeField(db_column='EXP_DATE', blank=True, null=True)  # Field name made lowercase.
    batch_cost = models.FloatField(db_column='BATCH_COST', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'ITEM_BATCH'

    def __str__(self):
        return str(self.batch_no)

class Stktrn(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    trn_post = models.DateTimeField(db_column='TRN_POST', auto_now=True, null=True)  # Field name made lowercase.
    trn_no = models.FloatField(db_column='TRN_NO', blank=True, null=True)  # Field name made lowercase.
    trn_date = models.DateTimeField(db_column='TRN_DATE', auto_now=True, null=True)  # Field name made lowercase.
    post_time = models.CharField(db_column='POST_TIME', max_length=6, blank=True, null=True)  # Field name made lowercase.
    aperiod = models.FloatField(db_column='APERIOD', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.CharField(db_column='ITEMCODE', max_length=15, blank=True, null=True)  # Field name made lowercase.
    store_no = models.CharField(db_column='STORE_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tstore_no = models.CharField(db_column='TSTORE_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fstore_no = models.CharField(db_column='FSTORE_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    trn_docno = models.CharField(db_column='TRN_DOCNO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    trn_type = models.CharField(db_column='TRN_TYPE', max_length=10, blank=True, null=True)  # Field name made lowercase.
    trn_db_qty = models.FloatField(db_column='TRN_DB_QTY', blank=True, null=True)  # Field name made lowercase.
    trn_cr_qty = models.FloatField(db_column='TRN_CR_QTY', blank=True, null=True)  # Field name made lowercase.
    trn_qty = models.FloatField(db_column='TRN_QTY', blank=True, null=True)  # Field name made lowercase.
    trn_balqty = models.FloatField(db_column='TRN_BALQTY', blank=True, null=True)  # Field name made lowercase.
    trn_balcst = models.FloatField(db_column='TRN_BALCST', blank=True, null=True)  # Field name made lowercase.
    trn_amt = models.FloatField(db_column='TRN_AMT', blank=True, null=True)  # Field name made lowercase.
    trn_cost = models.FloatField(db_column='TRN_COST', blank=True, null=True)  # Field name made lowercase.
    trn_ref = models.CharField(db_column='TRN_REF', max_length=8, blank=True, null=True)  # Field name made lowercase.
    hq_update = models.BooleanField(db_column='HQ_UPDATE', null=True)  # Field name made lowercase.
    line_no = models.FloatField(db_column='LINE_NO', blank=True, null=True)  # Field name made lowercase.
    item_uom = models.CharField(db_column='Item_UOM', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_batch = models.CharField(db_column='Item_Batch', max_length=20, blank=True, null=True)  # Field name made lowercase.
    mov_type = models.CharField(db_column='Mov_type', max_length=10, blank=True, null=True)  # Field name made lowercase.
    item_batch_cost = models.FloatField(db_column='Item_Batch_Cost', blank=True, null=True)  # Field name made lowercase.
    stock_in = models.BooleanField(db_column='Stock_In', blank=True, null=True)  # Field name made lowercase.
    trans_package_line_no = models.FloatField(db_column='TRANS_PACKAGE_LINE_NO', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Stktrn'

    def __str__(self):
        return str(self.trn_no)

class TreatmentProtocol(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='ITEM_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    protocol_detail = models.TextField(db_column='Protocol_Detail', blank=True, null=True)  # Field name made lowercase.
    protocol_duration = models.TextField(db_column='Protocol_Duration', blank=True, null=True)  # Field name made lowercase.
    line_no = models.IntegerField(db_column='Line_No', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='ISACTIVE',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Treatment_Protocol'    
    def __str__(self):
        return str(self.item_code)    

class ItemUomprice(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='ITEM_CODE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    item_uom = models.CharField(db_column='ITEM_UOM', max_length=20, blank=True, null=True)  # Field name made lowercase.
    uom_desc = models.CharField(db_column='UOM_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    uom_unit = models.FloatField(db_column='UOM_UNIT', blank=True, null=True)  # Field name made lowercase.
    item_uom2 = models.CharField(db_column='ITEM_UOM2', max_length=20, blank=True, null=True)  # Field name made lowercase.
    uom2_desc = models.CharField(db_column='UOM2_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    item_price = models.FloatField(db_column='ITEM_PRICE', blank=True, null=True)  # Field name made lowercase.
    item_cost = models.FloatField(db_column='ITEM_COST', blank=True, null=True)  # Field name made lowercase.
    min_margin = models.FloatField(db_column='MIN_MARGIN', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)  # Field name made lowercase.
    item_uomprice_seq = models.FloatField(db_column='Item_UOMPrice_SEQ', blank=True, null=True)  # Field name made lowercase.
    delete_user = models.CharField(db_column='Delete_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    delete_date = models.DateTimeField(db_column='Delete_Date', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'ITEM_UOMPRICE'
    
    def __str__(self):
        return str(self.item_code)
    
class PackageDtl(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=60, blank=True, null=True)  # Field name made lowercase.
    cost = models.FloatField(db_column='Cost', blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.
    discount = models.CharField(db_column='Discount', max_length=50, blank=True, null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    qty = models.IntegerField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    uom = models.CharField(db_column='UOM', max_length=50, blank=True, null=True)  # Field name made lowercase.
    package_barcode = models.CharField(db_column='Package_Barcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    disc_percent = models.IntegerField(db_column='Disc_Percent', blank=True, null=True)  # Field name made lowercase.
    unit_price = models.FloatField(db_column='Unit_Price', blank=True, null=True)  # Field name made lowercase.
    ttl_uprice = models.FloatField(db_column='Ttl_UPrice', blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50)  # Field name made lowercase.
    line_no = models.IntegerField(db_column='Line_no', blank=True, null=True)  # Field name made lowercase.
    service_expire_active = models.BooleanField(db_column='Service_Expire_Active', null=True)  # Field name made lowercase.
    service_expire_month = models.FloatField(db_column='Service_Expire_Month', blank=True, null=True)  # Field name made lowercase.
    treatment_limit_active = models.BooleanField(db_column='Treatment_Limit_Active', null=True)  # Field name made lowercase.
    treatment_limit_count = models.FloatField(db_column='Treatment_Limit_Count', blank=True, null=True)  # Field name made lowercase.
    limitservice_flexionly = models.BooleanField(db_column='LimitService_FlexiOnly', null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Package_Dtl'
    
    def __str__(self):
        return str(self.code)

class PackageHdr(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=60, blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.
    discount = models.CharField(db_column='Discount', max_length=50, blank=True, null=True)  # Field name made lowercase.
    date_created = models.DateTimeField(db_column='Date_Created', blank=True, null=True)  # Field name made lowercase.
    time_created = models.DateTimeField(db_column='Time_Created', blank=True, null=True)  # Field name made lowercase.
    user_name = models.CharField(db_column='User_Name', max_length=20, blank=True, null=True)  # Field name made lowercase.
    package_barcode = models.CharField(db_column='Package_Barcode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    unit_price = models.FloatField(db_column='Unit_Price', blank=True, null=True)  # Field name made lowercase.
    from_date = models.DateTimeField(db_column='From_date', blank=True, null=True)  # Field name made lowercase.
    to_date = models.DateTimeField(db_column='To_date', blank=True, null=True)  # Field name made lowercase.
    from_time = models.DateTimeField(db_column='From_Time', blank=True, null=True)  # Field name made lowercase.
    to_time = models.DateTimeField(db_column='To_Time', blank=True, null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    manual_disc = models.BooleanField(db_column='Manual_disc', blank=True, null=True)  # Field name made lowercase.
    istdt = models.BooleanField(db_column='IsTDT', blank=True, null=True)  # Field name made lowercase.
    apptlimit = models.IntegerField(db_column='ApptLimit', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Package_Hdr'

    def __str__(self):
        return str(self.code)

class PrepaidOpenCondition(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    p_itemtype = models.CharField(db_column='P_ItemType', max_length=20, null=True)  # Field name made lowercase.
    item_code = models.CharField(max_length=20, null=True)
    conditiontype1 = models.CharField(db_column='ConditionType1', max_length=20, null=True)  # Field name made lowercase.
    conditiontype2 = models.CharField(db_column='ConditionType2', max_length=20, null=True)  # Field name made lowercase.
    prepaid_value = models.FloatField(db_column='Prepaid_Value', blank=True, null=True)  # Field name made lowercase.
    prepaid_sell_amt = models.FloatField(db_column='Prepaid_Sell_Amt', blank=True, null=True)  # Field name made lowercase.
    prepaid_valid_period = models.CharField(db_column='Prepaid_Valid_Period', max_length=20, null=True)  # Field name made lowercase.
    rate = models.CharField(db_column='Rate', max_length=10, null=True)  # Field name made lowercase.
    membercardnoaccess = models.BooleanField(db_column='MemberCardNoAccess', null=True)  # Field name made lowercase.
    uid = models.CharField(db_column='UID', max_length=36, null=True)  # Field name made lowercase.
    mac_uid_ref = models.CharField(db_column='MAC_UID_Ref', max_length=50, blank=True, null=True)  # Field name made lowercase.
    pp_uid_ref = models.CharField(db_column='PP_UID_Ref', max_length=50, blank=True, null=True)  # Field name made lowercase.
    creditvalueshared = models.BooleanField(db_column='CreditValueShared')  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Prepaid_Open_Condition'

    def __str__(self):
        return str(self.P_ItemType)

class ScheduleHour(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    itm_code = models.CharField(db_column='itm_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itm_desc = models.CharField(db_column='itm_Desc', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fromtime = models.DateTimeField(db_column='FromTime', blank=True, null=True)  # Field name made lowercase.
    totime = models.DateTimeField(db_column='ToTime', blank=True, null=True)  # Field name made lowercase.
    offday = models.BooleanField(db_column='OFFDAY', null=True)  # Field name made lowercase.
    itm_isactive = models.BooleanField(db_column='ITM_ISACTIVE', blank=True, null=True,default=True)  # Field name made lowercase.
    itm_type = models.CharField(max_length=50, blank=True, null=True)
    itm_color = models.CharField(db_column='itm_Color', max_length=50, blank=True, null=True)  # Field name made lowercase.
    timeframe = models.CharField(db_column='TimeFrame', max_length=20, null=True)  # Field name made lowercase.
    shortDesc = models.CharField(db_column='shortDesc', max_length=20, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Schedule_Hour'

    def __str__(self):
        return str(self.itm_code) 

class ScheduleMonth(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    Emp_Codeid = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True)
    emp_code = models.CharField(db_column='Emp_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itm_date = models.DateTimeField(db_column='itm_Date', blank=True, null=True)  # Field name made lowercase.
    itm_Typeid = models.ForeignKey(ScheduleHour, on_delete=models.PROTECT, null=True)
    itm_type = models.CharField(db_column='itm_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    ledit = models.BooleanField(db_column='lEdit', null=True)  # Field name made lowercase.
    ledittype = models.CharField(db_column='lEditType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    User_Nameid = models.ForeignKey(Fmspw, on_delete=models.PROTECT, null=True)
    user_name = models.CharField(db_column='User_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    datetime = models.DateTimeField(db_column='DateTime', blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    totalappointments = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time9 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time930 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time10 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time1030 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time11 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time1130 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time12 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time1230 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time01 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time0130 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time02 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time0230 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time03 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time0330 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time04 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time0430 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time05 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time0530 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time06 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time0630 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time07 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    time0730 = models.IntegerField(null=True,blank=True)  #New Field name made lowercase.
    comments = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Schedule_Month'

    def __str__(self):
        return str(self.emp_code)     

class Workschedule(models.Model):
    id = models.AutoField(db_column='Id',primary_key=True)  # Field name made lowercase.
    name = models.CharField(db_column='Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    monday = models.CharField(db_column='Monday', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tuesday = models.CharField(db_column='Tuesday', max_length=20, blank=True, null=True)  # Field name made lowercase.
    wednesday = models.CharField(db_column='Wednesday', max_length=20, blank=True, null=True)  # Field name made lowercase.
    thursday = models.CharField(db_column='Thursday', max_length=20, blank=True, null=True)  # Field name made lowercase.
    friday = models.CharField(db_column='Friday', max_length=20, blank=True, null=True)  # Field name made lowercase.
    saturday = models.CharField(db_column='Saturday', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sunday = models.CharField(db_column='Sunday', max_length=20, blank=True, null=True)  # Field name made lowercase.
    emp_code = models.CharField(db_column='Emp_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    is_alternative = models.BooleanField(db_column='is_alter',default=False)

    class Meta:
        db_table = 'WorkSchedule'

    def __str__(self):
        return str(self.name)

class AttnType(models.Model):
    attn_id = models.AutoField(db_column='Attn_id', primary_key=True)  # Field name made lowercase.
    attn_code = models.CharField(db_column='Attn_code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    attn_desc = models.CharField(db_column='Attn_desc', max_length=40, blank=True, null=True)  # Field name made lowercase.
    attn_isactive = models.BooleanField(db_column='Attn_isactive',default=True)  # Field name made lowercase.
    attn_mov_in = models.CharField(db_column='Attn_Mov_In', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attn_seq = models.FloatField(db_column='Attn_Seq', blank=True, null=True)  # Field name made lowercase.
    attn_spec_in = models.BooleanField(db_column='Attn_Spec_In', null=True)  # Field name made lowercase.
    attn_spec_out = models.BooleanField(db_column='Attn_Spec_Out', null=True)  # Field name made lowercase.
    show_when_norecord = models.BooleanField(db_column='Show_When_NoRecord', null=True)  # Field name made lowercase.
    show_when_workin_on = models.BooleanField(db_column='Show_When_WorkIn_On', null=True)  # Field name made lowercase.
    show_when_workout_on = models.BooleanField(db_column='Show_When_WorkOut_On', null=True)  # Field name made lowercase.
    show_when_breakin_on = models.BooleanField(db_column='Show_When_BreakIn_On', null=True)  # Field name made lowercase.
    show_when_breakout_on = models.BooleanField(db_column='Show_When_BreakOut_On', null=True)  # Field name made lowercase.
    show_when_lunchin_on = models.BooleanField(db_column='Show_When_LunchIn_On', null=True)  # Field name made lowercase.
    show_when_lunchout_on = models.BooleanField(db_column='Show_When_LunchOut_On', null=True)  # Field name made lowercase.
    show_when_dinnerin_on = models.BooleanField(db_column='Show_When_DinnerIn_On', null=True)  # Field name made lowercase.
    show_when_dinnerout_on = models.BooleanField(db_column='Show_When_DinnerOut_On', null=True)  # Field name made lowercase.
    show_when_specialin_on = models.BooleanField(db_column='Show_When_SpecialIn_On', null=True)  # Field name made lowercase.
    show_when_specialout_on = models.BooleanField(db_column='Show_When_SpecialOut_On', null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Attn_Type'

    def __str__(self):
        return str(self.attn_desc)

class Attendance2(models.Model):
    attn_id = models.AutoField(db_column='Attn_ID',primary_key=True)  # Field name made lowercase.
    Attn_Emp_codeid   = models.ForeignKey('cl_table.Employee', on_delete=models.PROTECT, null=True) #, null=True
    attn_emp_code = models.CharField(db_column='Attn_Emp_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Attn_Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True) #, null=True, blank=True
    attn_site_code = models.CharField(db_column='Attn_Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attn_macno = models.CharField(db_column='Attn_MacNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attn_type = models.CharField(db_column='Attn_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attn_date = models.DateTimeField(db_column='Attn_Date', auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    attn_time = models.DateTimeField(db_column='Attn_Time',auto_now_add=True,  blank=True, null=True)  # Field name made lowercase.
    attn_remark = models.CharField(db_column='Attn_Remark', max_length=50, blank=True, null=True)  # Field name made lowercase.
    attn_mov_in = models.IntegerField(db_column='Attn_Mov_In', null=True)  # Field name made lowercase.
    create_date = models.DateTimeField(db_column='Create_date',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    create_time = models.DateTimeField(db_column='Create_time',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    missing_clock = models.BooleanField(db_column='Missing_Clock', null=True)  # Field name made lowercase.
    verify_code = models.CharField(db_column='Verify_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    verify_name = models.CharField(db_column='Verify_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    verify_reason = models.CharField(db_column='Verify_Reason', max_length=200, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Attendance2'

    def __str__(self):
        return str(self.attn_time) +" "+ "to" +" "+str(self.attn_mov_in)

class EmpSitelist(models.Model):
    id = models.BigAutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    Emp_Codeid  = models.ForeignKey(Employee, on_delete=models.PROTECT, null=True)
    emp_code = models.CharField(db_column='Emp_Code', max_length=20, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT,  null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=20, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Emp_SiteList'
        unique_together = (('emp_code', 'site_code'),)

    def __str__(self):
        return str(self.emp_code)

class ApptType(models.Model):
    appt_type_id = models.AutoField(db_column='Appt_type_id', primary_key=True)  # Field name made lowercase.
    appt_type_desc = models.CharField(db_column='Appt_type_desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    appt_type_code = models.CharField(db_column='Appt_type_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    appt_type_isactive = models.BooleanField(db_column='Appt_type_Isactive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Appt_Type'

    def __str__(self):
        return str(self.appt_type_desc)  

class Appointment(models.Model):
    
    STATUS = [
        ('Booking', 'Booking'),
        ('Waiting', 'Waiting List'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Arrived', 'Arrived'),
        ('Done', 'Done'),
        ('LastMinCancel', 'Cancelled Last Minute'),
        ('Late', 'Late'),
        ('No Show', 'No Show'),
    ]

    SEC_STATUS = [
        ("Rescheduled", "Rescheduled" ),
        ("Notified Once", "Notified Once"),
        ("Notified Twice", "Notified Twice"),
    ]

    appt_id = models.AutoField(db_column='Appt_id', primary_key=True)  # Field name made lowercase.
    cust_noid =  models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    cust_no = models.CharField(max_length=20, blank=True, null=True)
    appt_date = models.DateField(db_column='Appt_date', blank=True, null=True)  # Field name made lowercase.
    appt_fr_time = models.TimeField(db_column='Appt_Fr_time', blank=True, null=True)  # Field name made lowercase.
    Appt_typeid = models.ForeignKey(ApptType, on_delete=models.PROTECT, null=True)
    appt_type = models.CharField(db_column='Appt_type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    appt_phone = models.CharField(db_column='Appt_phone', max_length=20, blank=True, null=True)  # Field name made lowercase.
    appt_noperson = models.IntegerField(db_column='Appt_noperson', blank=True, null=True)  # Field name made lowercase.
    appt_remark = models.CharField(db_column='Appt_remark', max_length=250, blank=True, null=True)  # Field name made lowercase.
    emp_noid = models.ForeignKey(Employee, on_delete=models.PROTECT,  null=True)
    emp_no = models.CharField(max_length=10, blank=True, null=True)
    emp_name = models.CharField(max_length=80, blank=True, null=True)
    appt_isactive = models.BooleanField(db_column='Appt_Isactive',default=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_name', max_length=60, blank=True, null=True)  # Field name made lowercase.
    appt_code = models.CharField(db_column='Appt_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    appt_worktype_no = models.IntegerField(db_column='Appt_WorkType_No', blank=True, null=True)  # Field name made lowercase.
    appt_est_time = models.CharField(db_column='Appt_Est_Time', max_length=10, blank=True, null=True)  # Field name made lowercase.
    appt_est_cost = models.FloatField(db_column='Appt_Est_Cost', blank=True, null=True)  # Field name made lowercase.
    appt_status = models.CharField(db_column='Appt_Status', max_length=20,choices=STATUS,default='Booking', blank=True, null=True)  # Field name made lowercase.
    appt_to_time = models.TimeField(db_column='Appt_To_time', blank=True, null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=40, blank=True, null=True)
    Appt_Created_Byid = models.ForeignKey(Fmspw, on_delete=models.PROTECT,null=True)
    appt_created_by = models.CharField(db_column='Appt_Created_By', max_length=50, blank=True, null=True)  # Field name made lowercase.
    appt_created_date = models.DateTimeField(db_column='Appt_Created_Date', blank=True, null=True, auto_now_add=True)  # Field name made lowercase.
    appt_created_time = models.DateTimeField(db_column='Appt_Created_Time', blank=True, null=True, auto_now_add=True)  # Field name made lowercase.
    ItemSite_Codeid  = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True )
    itemsite_code = models.CharField(db_column='ItemSite_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remind_user = models.BooleanField(db_column='Remind_User', null=True)  # Field name made lowercase.
    arrive_time = models.CharField(db_column='Arrive_time', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isend_time = models.BooleanField(db_column='IsEnd_Time', null=True)  # Field name made lowercase.
    end_time = models.CharField(db_column='End_Time', max_length=20, blank=True, null=True)  # Field name made lowercase.
    walkin = models.BooleanField(db_column='WalkIn', null=True)  # Field name made lowercase.
    new = models.BooleanField(db_column='New', null=True)  # Field name made lowercase.
    ref_code = models.CharField(db_column='Ref_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    appt_comfirm = models.BooleanField(db_column='Appt_Comfirm', null=True)  # Field name made lowercase.
    appt_cancel = models.BooleanField(db_column='Appt_Cancel', null=True)  # Field name made lowercase.
    duration = models.CharField(db_column='Duration', max_length=10, blank=True, null=True)  # Field name made lowercase.
    reason = models.CharField(db_column='Reason', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Room_Codeid  = models.ForeignKey('custom.Room', on_delete=models.PROTECT,null=True)
    room_code = models.CharField(db_column='Room_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    booking = models.BooleanField(db_column='Booking', null=True)  # Field name made lowercase.
    update_status = models.IntegerField(db_column='Update_Status', null=True)  # Field name made lowercase.
    waiting = models.BooleanField(db_column='Waiting', null=True)  # Field name made lowercase.
    mac_code = models.CharField(db_column='Mac_Code', max_length=4, blank=True, null=True)  # Field name made lowercase.
    refmac_code = models.CharField(db_column='RefMac_Code', max_length=4, blank=True, null=True)  # Field name made lowercase.
    make_staff = models.CharField(db_column='Make_Staff', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Source_Codeid = models.ForeignKey(Source, on_delete=models.PROTECT,null=True)
    source_code = models.CharField(db_column='Source_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    is_hq = models.BooleanField(db_column='IS_HQ', null=True)  # Field name made lowercase.
    is_consultant = models.BooleanField(db_column='IS_Consultant', null=True)  # Field name made lowercase.
    is_missconsultant = models.BooleanField(db_column='IS_MISSConsultant', null=True)  # Field name made lowercase.
    is_enrollment = models.BooleanField(db_column='IS_Enrollment', null=True)  # Field name made lowercase.
    is_noshow = models.BooleanField(db_column='IS_NoShow', null=True)  # Field name made lowercase.
    cust_refer = models.CharField(db_column='Cust_Refer', max_length=50, blank=True, null=True)  # Field name made lowercase.
    is_missconsultantb = models.BooleanField(db_column='IS_MISSConsultantB', null=True)  # Field name made lowercase.
    modified_lock = models.BooleanField(db_column='Modified_Lock', null=True)  # Field name made lowercase.
    isarrive = models.BooleanField(db_column='IsArrive', blank=True, null=True)  # Field name made lowercase.
    lastmincancel = models.BooleanField(db_column='LastMinCancel', null=True)  # Field name made lowercase.
    sms_text = models.TextField(db_column='SMS_Text', blank=True, null=True)  # Field name made lowercase.
    equipment_id = models.IntegerField(blank=True, null=True)
    email_text = models.CharField(db_column='Email_Text', max_length=200, blank=True, null=True)  # Field name made lowercase.
    onlineappointment = models.BooleanField(null=True)
    requesttherapist = models.BooleanField(db_column='requestTherapist', null=True)  # Field name made lowercase.
    new_remark = models.CharField(db_column='New_Remark', max_length=800, blank=True, null=True)  # Field name made lowercase.
    islate = models.BooleanField(db_column='isLate', null=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='item_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    treatmentid = models.CharField(db_column='treatmentId', max_length=20, blank=True, null=True)  # Field name made lowercase.
    smsforconfirm = models.BooleanField(db_column='smsForConfirm', blank=True, null=True)  # Field name made lowercase.
    treatmentcode = models.CharField(db_column='treatmentCode', max_length=40, blank=True, null=True)  # Field name made lowercase.
    handledon = models.DateTimeField(db_column='HandledOn', blank=True, null=True)  # Field name made lowercase.
    isnotifiedonce = models.BooleanField(db_column='isNotifiedOnce', blank=True, null=True)  # Field name made lowercase.
    isnotifiedtwice = models.BooleanField(db_column='isNotifiedTwice', blank=True, null=True)  # Field name made lowercase.
    numberofappointments = models.IntegerField(db_column='numberOfAppointments', null=True) # New field
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    sec_status  = models.CharField(max_length=25,choices=SEC_STATUS, null=True, blank=True)
    remark_pts  = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'Appointment'

    def __str__(self):
        return str(self.appt_code)

class Appointmentdetails(models.Model):
    apptid = models.BigAutoField(db_column='ApptId',primary_key=True)  # Field name made lowercase.
    appt_code = models.CharField(db_column='Appt_code', max_length=50, null=True)  # Field name made lowercase.
    linenumber = models.IntegerField(db_column='lineNumber', blank=True, null=True)  # Field name made lowercase.
    itemcode = models.CharField(db_column='itemCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='itemName', max_length=40, blank=True, null=True)  # Field name made lowercase.
    unitprice = models.FloatField(db_column='unitPrice', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True,default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'AppointmentDetails'

    def __str__(self):
        return str(self.itemname)


class Title(models.Model):
    id = models.BigAutoField(primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title1 = models.CharField(db_column='Comp_Title1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title2 = models.CharField(db_column='Comp_Title2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title3 = models.CharField(db_column='Comp_Title3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title4 = models.CharField(db_column='Comp_Title4', max_length=50, blank=True, null=True)  # Field name made lowercase.
    footer_1 = models.CharField(db_column='Footer_1', max_length=50, blank=True, null=True)  # Field name made lowercase.
    footer_2 = models.CharField(db_column='Footer_2', max_length=50, blank=True, null=True)  # Field name made lowercase.
    footer_3 = models.CharField(db_column='Footer_3', max_length=50, blank=True, null=True)  # Field name made lowercase.
    footer_4 = models.CharField(db_column='Footer_4', max_length=50, blank=True, null=True)  # Field name made lowercase.
    rec_detail = models.IntegerField(db_column='REC_DETAIL', blank=True, null=True)  # Field name made lowercase.
    rec_qty = models.IntegerField(db_column='REC_QTY', blank=True, null=True)  # Field name made lowercase.
    rec_price = models.IntegerField(db_column='REC_PRICE', blank=True, null=True)  # Field name made lowercase.
    rec_amt = models.IntegerField(db_column='REC_AMT', blank=True, null=True)  # Field name made lowercase.
    rec_title = models.IntegerField(db_column='REC_TITLE', blank=True, null=True)  # Field name made lowercase.
    rec_maintitle = models.IntegerField(db_column='REC_MAINTITLE', blank=True, null=True)  # Field name made lowercase.
    rec_print = models.IntegerField(db_column='REC_PRINT', blank=True, null=True)  # Field name made lowercase.
    coll_title = models.IntegerField(db_column='COLL_TITLE', blank=True, null=True)  # Field name made lowercase.
    coll_detail = models.IntegerField(db_column='COLL_DETAIL', blank=True, null=True)  # Field name made lowercase.
    coll_qty = models.IntegerField(db_column='COLL_QTY', blank=True, null=True)  # Field name made lowercase.
    coll_amt = models.IntegerField(db_column='COLL_AMT', blank=True, null=True)  # Field name made lowercase.
    coll_maintitle = models.IntegerField(db_column='COLL_MAINTITLE', blank=True, null=True)  # Field name made lowercase.
    coll_print = models.IntegerField(db_column='COLL_PRINT', blank=True, null=True)  # Field name made lowercase.
    daily_title = models.IntegerField(db_column='DAILY_TITLE', blank=True, null=True)  # Field name made lowercase.
    daily_detail = models.IntegerField(db_column='DAILY_DETAIL', blank=True, null=True)  # Field name made lowercase.
    daily_qty = models.IntegerField(db_column='DAILY_QTY', blank=True, null=True)  # Field name made lowercase.
    daily_amt = models.IntegerField(db_column='DAILY_AMT', blank=True, null=True)  # Field name made lowercase.
    daily_maintitle = models.IntegerField(db_column='DAILY_MAINTITLE', blank=True, null=True)  # Field name made lowercase.
    daily_print = models.IntegerField(db_column='DAILY_PRINT', blank=True, null=True)  # Field name made lowercase.
    hr_title = models.IntegerField(db_column='HR_TITLE', blank=True, null=True)  # Field name made lowercase.
    hr_time = models.IntegerField(db_column='HR_TIME', blank=True, null=True)  # Field name made lowercase.
    hr_qty = models.IntegerField(db_column='HR_QTY', blank=True, null=True)  # Field name made lowercase.
    hr_amt = models.IntegerField(db_column='HR_AMT', blank=True, null=True)  # Field name made lowercase.
    hr_maintitle = models.IntegerField(db_column='HR_MAINTITLE', blank=True, null=True)  # Field name made lowercase.
    hr_print = models.IntegerField(db_column='HR_PRINT', blank=True, null=True)  # Field name made lowercase.
    not_item = models.IntegerField(db_column='NOT_ITEM', blank=True, null=True)  # Field name made lowercase.
    not_qty = models.IntegerField(db_column='NOT_QTY', blank=True, null=True)  # Field name made lowercase.
    not_amt = models.IntegerField(db_column='NOT_AMT', blank=True, null=True)  # Field name made lowercase.
    not_title = models.IntegerField(db_column='NOT_TITLE', blank=True, null=True)  # Field name made lowercase.
    not_maintitle = models.IntegerField(db_column='NOT_MAINTITLE', blank=True, null=True)  # Field name made lowercase.
    not_print = models.IntegerField(db_column='NOT_PRINT', blank=True, null=True)  # Field name made lowercase.
    pay_title = models.IntegerField(db_column='PAY_TITLE', blank=True, null=True)  # Field name made lowercase.
    pay_detail = models.IntegerField(db_column='PAY_DETAIL', blank=True, null=True)  # Field name made lowercase.
    pay_qty = models.IntegerField(db_column='PAY_QTY', blank=True, null=True)  # Field name made lowercase.
    pay_amt = models.IntegerField(db_column='PAY_AMT', blank=True, null=True)  # Field name made lowercase.
    pay_maintitle = models.IntegerField(db_column='PAY_MAINTITLE', blank=True, null=True)  # Field name made lowercase.
    pay_print = models.IntegerField(db_column='PAY_PRINT', blank=True, null=True)  # Field name made lowercase.
    auto_detail = models.IntegerField(db_column='AUTO_DETAIL', blank=True, null=True)  # Field name made lowercase.
    auto_qty = models.IntegerField(db_column='AUTO_QTY', blank=True, null=True)  # Field name made lowercase.
    auto_price = models.IntegerField(db_column='AUTO_PRICE', blank=True, null=True)  # Field name made lowercase.
    auto_amt = models.IntegerField(db_column='AUTO_AMT', blank=True, null=True)  # Field name made lowercase.
    auto_title = models.IntegerField(db_column='AUTO_TITLE', blank=True, null=True)  # Field name made lowercase.
    auto_maintitle = models.IntegerField(db_column='AUTO_MAINTITLE', blank=True, null=True)  # Field name made lowercase.
    auto_print = models.IntegerField(db_column='AUTO_PRINT', blank=True, null=True)  # Field name made lowercase.
    product_license = models.CharField(db_column='Product_License', max_length=20, blank=True, null=True)  # Field name made lowercase.
    rno = models.IntegerField(db_column='RNo', blank=True, null=True)  # Field name made lowercase.
    rinvdesc = models.IntegerField(db_column='RInvDesc', blank=True, null=True)  # Field name made lowercase.
    rcoutstanding = models.IntegerField(db_column='RCOutStanding', blank=True, null=True)  # Field name made lowercase.
    rtopup = models.IntegerField(db_column='RTopUp', blank=True, null=True)  # Field name made lowercase.
    rnoutstanding = models.IntegerField(db_column='RNOutStanding', blank=True, null=True)  # Field name made lowercase.
    ritem = models.IntegerField(db_column='RItem', blank=True, null=True)  # Field name made lowercase.
    rup = models.IntegerField(db_column='RUP', blank=True, null=True)  # Field name made lowercase.
    rdis = models.IntegerField(db_column='RDIS', blank=True, null=True)  # Field name made lowercase.
    rnp = models.IntegerField(db_column='RNP', blank=True, null=True)  # Field name made lowercase.
    rqty = models.IntegerField(db_column='RQTY', blank=True, null=True)  # Field name made lowercase.
    rdp = models.IntegerField(db_column='RDP', blank=True, null=True)  # Field name made lowercase.
    ramt = models.IntegerField(db_column='RAmt', blank=True, null=True)  # Field name made lowercase.
    rfooter = models.IntegerField(db_column='RFooter', blank=True, null=True)  # Field name made lowercase.
    rsubfoot = models.IntegerField(db_column='RSubFoot', blank=True, null=True)  # Field name made lowercase.
    rheaderfoot = models.IntegerField(db_column='RHeaderFoot', blank=True, null=True)  # Field name made lowercase.
    rcndesc = models.IntegerField(db_column='RCNDesc', blank=True, null=True)  # Field name made lowercase.
    rcnamt = models.IntegerField(db_column='RCNAmt', blank=True, null=True)  # Field name made lowercase.
    cpl = models.IntegerField(db_column='CPL', blank=True, null=True)  # Field name made lowercase.
    rinvline1 = models.IntegerField(db_column='RInvLine1', blank=True, null=True)  # Field name made lowercase.
    rinvline2 = models.IntegerField(db_column='RInvLine2', blank=True, null=True)  # Field name made lowercase.
    rinvoice = models.IntegerField(db_column='RInvoice', blank=True, null=True)  # Field name made lowercase.
    rpaymode = models.IntegerField(db_column='RPaymode', blank=True, null=True)  # Field name made lowercase.
    ramount = models.IntegerField(db_column='RAmount', blank=True, null=True)  # Field name made lowercase.
    rtotamount = models.IntegerField(db_column='RTotAmount', blank=True, null=True)  # Field name made lowercase.
    rinvline3 = models.IntegerField(db_column='RInvLine3', blank=True, null=True)  # Field name made lowercase.
    logo_transaction = models.TextField(db_column='LOGO_Transaction', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    trans_logo = models.BinaryField(db_column='Trans_Logo', blank=True, null=True)  # Field name made lowercase.
    trans_h1 = models.CharField(db_column='Trans_H1', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_h2 = models.CharField(db_column='Trans_H2', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_promo1 = models.CharField(db_column='Trans_Promo1', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_promo2 = models.CharField(db_column='Trans_Promo2', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_footer1 = models.CharField(db_column='Trans_Footer1', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_footer2 = models.CharField(db_column='Trans_Footer2', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_footer3 = models.CharField(db_column='Trans_Footer3', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_footer4 = models.CharField(db_column='Trans_Footer4', max_length=500, blank=True, null=True)  # Field name made lowercase.
    trans_message1 = models.CharField(db_column='Trans_Message1', max_length=500, blank=True, null=True)  # Field name made lowercase.
    gst_reg_no = models.CharField(db_column='GST_REG_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    comp_title5 = models.CharField(db_column='Comp_Title5', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title6 = models.CharField(db_column='Comp_Title6', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title7 = models.CharField(db_column='Comp_Title7', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title8 = models.CharField(db_column='Comp_Title8', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title9 = models.CharField(db_column='Comp_Title9', max_length=50, blank=True, null=True)  # Field name made lowercase.
    comp_title10 = models.CharField(db_column='Comp_Title10', max_length=50, blank=True, null=True)  # Field name made lowercase.
    company_reg_no = models.CharField(db_column='COMPANY_REG_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    subrpt_show_title = models.BooleanField(db_column='SubRpt_Show_Title', null=True)  # Field name made lowercase.
    subrpt_show_footer = models.BooleanField(db_column='SubRpt_Show_Footer', null=True)  # Field name made lowercase.
    subrpt_show_gst_summary = models.BooleanField(db_column='SubRpt_Show_GST_Summary', null=True)  # Field name made lowercase.
    subrpt_show_footer_tax = models.BooleanField(db_column='SubRpt_Show_Footer_Tax', null=True)  # Field name made lowercase.
    subrpt_show_footer_trmt_available = models.BooleanField(db_column='SubRpt_Show_Footer_Trmt_Available', null=True)  # Field name made lowercase.
    subrpt_show_footer_cust_sign = models.BooleanField(db_column='SubRpt_Show_Footer_Cust_Sign', null=True)  # Field name made lowercase.
    subrpt_show_footerremark = models.BooleanField(db_column='SubRpt_Show_FooterRemark', null=True)  # Field name made lowercase.
    gst_start_datetime = models.DateTimeField(db_column='GST_Start_DateTime', blank=True, null=True)  # Field name made lowercase.
    gst_end_datetime = models.DateTimeField(db_column='GST_End_DateTime', blank=True, null=True)  # Field name made lowercase.
    sst_salestax_reg_no = models.CharField(db_column='SST_SalesTax_REG_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sst_servicetax_reg_no = models.CharField(db_column='SST_ServiceTax_REG_NO', max_length=20, blank=True, null=True)  # Field name made lowercase.
    subrpt_show_footer_sst = models.BooleanField(db_column='SubRpt_Show_Footer_SST', null=True)  # Field name made lowercase.
    subrpt_show_tax_summary_sst = models.BooleanField(db_column='SubRpt_Show_Tax_Summary_SST', null=True)  # Field name made lowercase.
    subrpt_show_footer_tax_sst = models.BooleanField(db_column='SubRpt_Show_Footer_Tax_SST', null=True)  # Field name made lowercase.
    subrpt_show_footer_trmt_available_sst = models.BooleanField(db_column='SubRpt_Show_Footer_Trmt_Available_SST', null=True)  # Field name made lowercase.
    subrpt_show_footer_cust_sign_sst = models.BooleanField(db_column='SubRpt_Show_Footer_Cust_Sign_SST', null=True)  # Field name made lowercase.
    subrpt_show_footerremark_sst = models.BooleanField(db_column='SubRpt_Show_FooterRemark_SST', null=True)  # Field name made lowercase.
    sst_start_datetime = models.DateTimeField(db_column='SST_Start_DateTime', blank=True, null=True)  # Field name made lowercase.
    sst_end_datetime = models.DateTimeField(db_column='SST_End_DateTime', blank=True, null=True)  # Field name made lowercase.
    print_logo_position_x = models.FloatField(db_column='Print_Logo_Position_X', blank=True, null=True)  # Field name made lowercase.
    print_logo_position_y = models.FloatField(db_column='Print_Logo_Position_Y', blank=True, null=True)  # Field name made lowercase.
    logourl = models.TextField(db_column='logoUrl', blank=True, null=True)  # Field name made lowercase.
    receipttemplate = models.CharField(db_column='ReceiptTemplate', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    logo_pic = models.ImageField(upload_to='img',null=True)

    class Meta:
        db_table = 'Title'

    def __str__(self):
        return str(self.title)


class ControlNo(models.Model):
    control_no = models.CharField(max_length=50, blank=True, null=True)
    control_prefix = models.CharField(max_length=50, blank=True, null=True)
    control_description = models.CharField(max_length=50, blank=True, null=True)
    control_id = models.AutoField(primary_key=True)
    controldate = models.DateField(db_column='CONTROLDATE', max_length=20, blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    mac_code = models.CharField(db_column='Mac_Code', max_length=4, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Control_No'

    def __str__(self):
        return str(self.control_no)


class Systemloginlog(models.Model):
    id = models.AutoField(primary_key=True)
    log_type = models.CharField(db_column='Log_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    log_datetime = models.DateTimeField(db_column='Log_DateTime', blank=True, null=True)  # Field name made lowercase.
    log_user = models.CharField(db_column='Log_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    log_process = models.CharField(db_column='Log_Process', max_length=50, blank=True, null=True)  # Field name made lowercase.
    log_message = models.CharField(db_column='Log_Message', max_length=3000, blank=True, null=True)  # Field name made lowercase.
    mac_uid_ref = models.CharField(db_column='MAC_UID_Ref', max_length=50, blank=True, null=True)  # Field name made lowercase.
    log_terminalcode = models.CharField(db_column='Log_TerminalCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'SystemLoginLog'

    def __str__(self):
        return str(self.log_type)

class Systemlog(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    log_type = models.CharField(db_column='Log_Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    log_datetime = models.DateTimeField(db_column='Log_DateTime', blank=True, null=True)  # Field name made lowercase.
    log_user = models.CharField(db_column='Log_User', max_length=50, blank=True, null=True)  # Field name made lowercase.
    log_process = models.CharField(db_column='Log_Process', max_length=50, blank=True, null=True)  # Field name made lowercase.
    log_message = models.CharField(db_column='Log_Message', max_length=3000, blank=True, null=True)  # Field name made lowercase.
    log_site_code = models.CharField(db_column='Log_Site_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'SystemLog'

    def __str__(self):
        return str(self.log_type)

class FocReason(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    foc_reason_code = models.CharField(db_column='FOC_Reason_Code', max_length=20, null=True)  # Field name made lowercase.
    foc_reason_sdesc = models.CharField(db_column='FOC_Reason_SDesc', max_length=20, blank=True, null=True)  # Field name made lowercase.
    foc_reason_ldesc = models.CharField(db_column='FOC_Reason_LDesc', max_length=20, blank=True, null=True)  # Field name made lowercase.
    foc_reason_isactive = models.BooleanField(db_column='FOC_Reason_IsActive',default=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'FOC_Reason'

    def __str__(self):
        return str(self.foc_reason_code)    

class Systemsetup(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=100, blank=True, null=True)  # Field name made lowercase.
    value_name = models.CharField(db_column='Value_name', max_length=200, blank=True, null=True)  # Field name made lowercase.
    value_data = models.CharField(db_column='Value_data', max_length=300, blank=True, null=True)  # Field name made lowercase.
    limit_choice = models.CharField(db_column='Limit_choice', max_length=100, blank=True, null=True)  # Field name made lowercase.
    long_remarks = models.CharField(db_column='Long_Remarks', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    short_remarks = models.CharField(db_column='Short_Remarks', max_length=300, blank=True, null=True)  # Field name made lowercase.
    use_function = models.CharField(db_column='Use_Function', max_length=100, blank=True, null=True)  # Field name made lowercase.
    create_datetime = models.DateTimeField(db_column='Create_DateTime',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    edit_datetime = models.DateTimeField(db_column='Edit_DateTime',auto_now_add=True, blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'SystemSetup'

    def __str__(self):
        return str(self.Title)     

class GstSetting(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    item_code = models.CharField(db_column='ITEM_CODE', max_length=50, blank=True, null=True)  # Field name made lowercase.
    item_desc = models.CharField(db_column='ITEM_DESC', max_length=50, blank=True, null=True)  # Field name made lowercase.
    item_value = models.FloatField(db_column='ITEM_VALUE', blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='ISACTIVE', blank=True, null=True,default=True)  # Field name made lowercase.
    item_seq = models.FloatField(db_column='ITEM_SEQ', blank=True, null=True)  # Field name made lowercase.
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_exclusive = models.BooleanField(null=True)

    class Meta:
        db_table = 'GST_Setting'

    def __str__(self):
        return str(self.item_code)     


class CustomerFormControl(models.Model):
    id = models.AutoField(primary_key=True)
    field_name = models.CharField(db_column='fieldName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    display_field_name = models.CharField(db_column='displayFieldName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    visible_in_registration = models.BooleanField(db_column='visibleInRegistration')  # Field name made lowercase.
    visible_in_listing = models.BooleanField(db_column='visibleInListing')  # Field name made lowercase.
    visible_in_profile = models.BooleanField(db_column='visibleInProfile')  # Field name made lowercase.
    editable = models.BooleanField()
    mandatory = models.BooleanField()
    order = models.IntegerField()
    col_width = models.IntegerField(default=6)
    isActive = models.BooleanField(db_column='isActive')  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist',db_column='Site_Codeid_id',related_name='customer_form_control', on_delete=models.PROTECT, null=True)


    class Meta:
        db_table = 'customerFormControl'

    def __str__(self):
        return str(self.field_name)



class RewardPolicy(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    reward_code = models.CharField(db_column='Reward_Code', max_length=20)  # Field name made lowercase.
    cust_type = models.CharField(db_column='Cust_Type', max_length=20)  # Field name made lowercase.
    cur_value = models.FloatField(db_column='Cur_Value')  # Field name made lowercase.
    point_value = models.FloatField(db_column='Point_Value')  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive')  # Field name made lowercase.
    reward_item_type = models.CharField(db_column='Reward_Item_Type', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Reward_Policy'


class RedeemPolicy(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    redeem_code = models.CharField(db_column='Redeem_Code', max_length=20)  # Field name made lowercase.
    cust_type = models.CharField(db_column='Cust_Type', max_length=20)  # Field name made lowercase.
    cur_value = models.FloatField(db_column='Cur_Value')  # Field name made lowercase.
    point_value = models.FloatField(db_column='Point_Value')  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Redeem_Policy'


class Diagnosis(models.Model):
    sys_code = models.AutoField(db_column='Sys_Code', primary_key=True)  # Field name made lowercase.
    diagnosis_date = models.DateTimeField(db_column='Diagnosis_Date', blank=True, null=True)  # Field name made lowercase.
    next_appt = models.DateTimeField(db_column='Next_Appt', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=255, blank=True, null=True)  # Field name made lowercase.
    homecare = models.CharField(db_column='HomeCare', max_length=255, blank=True, null=True)  # Field name made lowercase.
    pic_path = models.CharField(db_column='PIC_path', max_length=255, blank=True, null=True)  # Field name made lowercase.
    date_pic_take = models.DateTimeField(db_column='Date_Pic_Take', blank=True, null=True)  # Field name made lowercase.
    treatment_code = models.CharField(db_column='Treatment_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code', max_length=50)  # Field name made lowercase.
    cust_no = models.ForeignKey(Customer, on_delete=models.PROTECT, null=True)
    diagnosis_code = models.CharField(db_column='Diagnosis_Code', max_length=50,blank=True, null=True)  # Field name made lowercase.
    left_desc1 = models.CharField(db_column='Left_Desc1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    left_desc2 = models.CharField(db_column='Left_Desc2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    right_desc1 = models.CharField(db_column='Right_Desc1', max_length=100, blank=True, null=True)  # Field name made lowercase.
    right_desc2 = models.CharField(db_column='Right_Desc2', max_length=100, blank=True, null=True)  # Field name made lowercase.
    treatment_name = models.CharField(db_column='Treatment_Name', max_length=50, blank=True, null=True)  # Field name made lowercase.
    remark1 = models.CharField(db_column='Remark1', max_length=200, blank=True, null=True)  # Field name made lowercase.
    remark2 = models.CharField(db_column='Remark2', max_length=200, blank=True, null=True)  # Field name made lowercase.
    remark3 = models.CharField(db_column='Remark3', max_length=200, blank=True, null=True)  # Field name made lowercase.
    remark4 = models.CharField(db_column='Remark4', max_length=200, blank=True, null=True)  # Field name made lowercase.
    remark5 = models.CharField(db_column='Remark5', max_length=200, blank=True, null=True)  # Field name made lowercase.
    remark6 = models.CharField(db_column='Remark6', max_length=200, blank=True, null=True)  # Field name made lowercase.
    pic_path = models.ImageField(db_column='PIC_path', max_length=255, blank=True, null=True,upload_to='img')
    pic_path2 = models.ImageField(db_column='PIC_Path2', max_length=255, blank=True, null=True,upload_to='img')
    pic_path3 = models.ImageField(db_column='PIC_Path3', max_length=255, blank=True, null=True,upload_to='img')
    pic_path4 = models.ImageField(db_column='PIC_Path4', max_length=255, blank=True, null=True,upload_to='img')
    pic_path5 = models.ImageField(db_column='PIC_Path5', max_length=255, blank=True, null=True,upload_to='img')
    pic_path6 = models.ImageField(db_column='PIC_Path6', max_length=255, blank=True, null=True,upload_to='img')
    pic1 = models.BinaryField(db_column='PIC1', blank=True, null=True)  # Field name made lowercase.
    pic2 = models.BinaryField(db_column='PIC2', blank=True, null=True)  # Field name made lowercase.
    pic3 = models.BinaryField(db_column='PIC3', blank=True, null=True)  # Field name made lowercase.
    pic4 = models.BinaryField(db_column='PIC4', blank=True, null=True)  # Field name made lowercase.
    pic5 = models.BinaryField(db_column='PIC5', blank=True, null=True)  # Field name made lowercase.
    pic6 = models.BinaryField(db_column='PIC6', blank=True, null=True)  # Field name made lowercase.
    # pic1 = models.ImageField(db_column='PIC1', blank=True, null=True,upload_to='img')
    # pic2 = models.ImageField(db_column='PIC2', blank=True, null=True,upload_to='img')
    # pic3 = models.ImageField(db_column='PIC3', blank=True, null=True,upload_to='img')
    # pic4 = models.ImageField(db_column='PIC4', blank=True, null=True,upload_to='img')
    # pic5 = models.ImageField(db_column='PIC5', blank=True, null=True,upload_to='img')
    # pic6 = models.ImageField(db_column='PIC6', blank=True, null=True,upload_to='img')
    site_code = models.CharField(db_column='Site_Code', max_length=50)  # Field name made lowercase.

    def save(self, *args, **kwargs):
        self.cust_code = self.cust_no.cust_code
        self.cust_name = self.cust_no.cust_name
        super(Diagnosis, self).save(*args, **kwargs)


    @property
    def get_diagnosis_code(self):
        return "%06d" % self.sys_code


    class Meta:
        # managed = False
        db_table = 'Diagnosis'
        unique_together = (('sys_code', 'cust_no', 'site_code'),)


class DiagnosisCompare(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    compare_code = models.CharField(db_column='Compare_Code', max_length=100, blank=True, null=True)  # Field name made lowercase.
    compare_remark = models.TextField(db_column='Compare_Remark', blank=True, null=True)  # Field name made lowercase.
    compare_datetime = models.DateTimeField(db_column='Compare_DateTime', blank=True, null=True)  # Field name made lowercase.
    compare_isactive = models.BooleanField(db_column='Compare_IsActive',default=True)  # Field name made lowercase.
    compare_user = models.CharField(db_column='Compare_User', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    diagnosis1_id = models.ForeignKey(Diagnosis, on_delete=models.PROTECT, null=True, related_name="diagnosis_compare_1")
    diagnosis2_id = models.ForeignKey(Diagnosis, on_delete=models.PROTECT, null=True, related_name="diagnosis_compare_2")

    class Meta:
        db_table = 'Diagnosis_Compare'

class CustomerPoint(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    transacno = models.CharField(db_column='TransacNO', max_length=20)  # Field name made lowercase.
    date = models.DateTimeField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(db_column='Username', max_length=100, blank=True, null=True)  # Field name made lowercase.
    time = models.DateTimeField(db_column='Time', blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code', max_length=100)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=20, blank=True, null=True)  # Field name made lowercase.
    refno = models.CharField(db_column='RefNo', max_length=20)  # Field name made lowercase.
    ref_source = models.CharField(db_column='Ref_Source', max_length=50)  # Field name made lowercase.
    isvoid = models.BooleanField(db_column='Isvoid')  # Field name made lowercase.
    sa_status = models.CharField(db_column='Sa_Status', max_length=10)  # Field name made lowercase.
    void_referenceno = models.CharField(db_column='void_ReferenceNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    total_point = models.FloatField(db_column='Total_Point')  # Field name made lowercase.
    now_point = models.FloatField(db_column='Now_Point', blank=True, null=True)  # Field name made lowercase.
    seq = models.IntegerField(db_column='Seq', blank=True, null=True)  # Field name made lowercase.
    remarks = models.CharField(db_column='Remarks', max_length=10, blank=True, null=True)  # Field name made lowercase.
    bal_point = models.FloatField(db_column='Bal_Point')  # Field name made lowercase.
    expired = models.BooleanField(db_column='Expired')  # Field name made lowercase.
    expired_date = models.DateTimeField(db_column='Expired_Date', blank=True, null=True)  # Field name made lowercase.
    mac_code = models.CharField(db_column='Mac_Code', max_length=100)  # Field name made lowercase.
    logno = models.CharField(db_column='LogNo', max_length=100)  # Field name made lowercase.
    approval_user = models.CharField(db_column='Approval_User', max_length=100)  # Field name made lowercase.
    cardno = models.CharField(db_column='CardNo', max_length=100)  # Field name made lowercase.
    bdate = models.DateTimeField(db_column='BDate', blank=True, null=True)  # Field name made lowercase.
    pdate = models.DateTimeField(db_column='PDate', blank=True, null=True)  # Field name made lowercase.
    expired_point = models.FloatField()
    postransactionno = models.CharField(db_column='posTransactionNo', max_length=50)  # Field name made lowercase.
    postotalamt = models.FloatField(db_column='posTotalAmt', blank=True, null=True)  # Field name made lowercase.
    locid = models.CharField(db_column='LocID', max_length=50)  # Field name made lowercase.
    mgm_refno = models.CharField(db_column='MGM_RefNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    tdate = models.CharField(db_column='TDate', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Customer_Point'
        unique_together = (('transacno', 'cust_code', 'sa_status', 'total_point', 'postransactionno', 'locid'),)

class CustomerPointDtl(models.Model):
    id = models.AutoField(db_column='Id',primary_key=True)  # Field name made lowercase.
    transacno = models.CharField(db_column='TransacNo', max_length=20)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_Code', max_length=20)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    parent_code = models.CharField(db_column='Parent_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    parent_desc = models.CharField(db_column='Parent_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    parent_display = models.CharField(db_column='Parent_Display', max_length=100, blank=True, null=True)  # Field name made lowercase.
    itm_code = models.CharField(db_column='itm_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    itm_desc = models.CharField(db_column='itm_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    point = models.FloatField(db_column='Point')  # Field name made lowercase.
    now_point = models.FloatField(db_column='Now_Point')  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True)  # Field name made lowercase.
    remark_code = models.CharField(db_column='Remark_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    remark_desc = models.CharField(db_column='Remark_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    isvoid = models.BooleanField(db_column='Isvoid')  # Field name made lowercase.
    void_referenceno = models.CharField(db_column='void_ReferenceNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isopen = models.BooleanField(db_column='IsOpen', blank=True, null=True)  # Field name made lowercase.
    qty = models.IntegerField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    total_point = models.FloatField(db_column='Total_Point', blank=True, null=True)  # Field name made lowercase.
    seq = models.IntegerField(db_column='Seq', blank=True, null=True)  # Field name made lowercase.
    sa_status = models.CharField(db_column='Sa_status', max_length=10, blank=True, null=True)  # Field name made lowercase.
    bal_acc2 = models.FloatField(db_column='Bal_Acc2', blank=True, null=True)  # Field name made lowercase.
    point_acc1 = models.FloatField(db_column='Point_Acc1', blank=True, null=True)  # Field name made lowercase.
    point_acc2 = models.FloatField(db_column='Point_Acc2', blank=True, null=True)  # Field name made lowercase.
    locid = models.CharField(db_column='LocID', max_length=50)  # Field name made lowercase.

    class Meta:
        # managed = False
        db_table = 'Customer_Point_Dtl'
        unique_together = (('transacno', 'cust_code', 'point', 'now_point', 'locid'),)


class Multilanguage(models.Model):
    id = models.AutoField(primary_key=True)
    english = models.CharField(max_length=250, blank=True, null=True)
    zh_sg = models.CharField(db_column='zh-sg', max_length=250, blank=True, null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        db_table = 'MultiLanguage'

class Language(models.Model):
    itm_id = models.AutoField(primary_key=True)
    itm_code = models.CharField(db_column='itm_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itm_desc = models.CharField(db_column='itm_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itm_isactive = models.BooleanField(db_column='itm_Isactive')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Language'


class MultiLanguageWord(models.Model):
    id = models.AutoField(primary_key=True)
    wordCode = models.IntegerField()
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    word = models.CharField(max_length=250)

    class Meta:
        db_table = 'MultiLanguageWord'
        unique_together = (('wordCode','language',),)

class DailysalesdataDetail(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sitecode = models.CharField(db_column='SiteCode', max_length=20)  # Field name made lowercase.
    sales_date = models.DateTimeField(db_column='Sales_Date')  # Field name made lowercase.
    business_date = models.DateTimeField(db_column='Business_Date')  # Field name made lowercase.
    sa_transacno = models.CharField(db_column='SA_TransacNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sa_transacno_ref = models.CharField(db_column='SA_TransacNo_Ref', max_length=20, blank=True, null=True)  # Field name made lowercase.
    version = models.CharField(db_column='Version', max_length=20, blank=True, null=True)  # Field name made lowercase.
    sales_gt1_withgst = models.FloatField(db_column='Sales_GT1_WithGST', blank=True, null=True)  # Field name made lowercase.
    sales_gt1_gst = models.FloatField(db_column='Sales_GT1_GST', blank=True, null=True)  # Field name made lowercase.
    sales_gt1_beforegst = models.FloatField(db_column='Sales_GT1_BeforeGST', blank=True, null=True)  # Field name made lowercase.
    servicesales_gt1 = models.FloatField(db_column='ServiceSales_GT1', blank=True, null=True)  # Field name made lowercase.
    productsales_gt1 = models.FloatField(db_column='ProductSales_GT1', blank=True, null=True)  # Field name made lowercase.
    prepaidsales_gt1 = models.FloatField(db_column='PrepaidSales_GT1', blank=True, null=True)  # Field name made lowercase.
    sales_gt2_withgst = models.FloatField(db_column='Sales_GT2_WithGST', blank=True, null=True)  # Field name made lowercase.
    sales_gt2_gst = models.FloatField(db_column='Sales_GT2_GST', blank=True, null=True)  # Field name made lowercase.
    sales_gt2_beforegst = models.FloatField(db_column='Sales_GT2_BeforeGST', blank=True, null=True)  # Field name made lowercase.
    servicesales_gt2 = models.FloatField(db_column='ServiceSales_GT2', blank=True, null=True)  # Field name made lowercase.
    productsales_gt2 = models.FloatField(db_column='ProductSales_GT2', blank=True, null=True)  # Field name made lowercase.
    prepaidsales_gt2 = models.FloatField(db_column='PrepaidSales_GT2', blank=True, null=True)  # Field name made lowercase.
    treatmentdoneqty = models.FloatField(db_column='TreatmentDoneQty', blank=True, null=True)  # Field name made lowercase.
    treatmentdoneamount = models.FloatField(db_column='TreatmentDoneAmount', blank=True, null=True)  # Field name made lowercase.
    lastupdate = models.DateTimeField(db_column='LastUpDate')  # Field name made lowercase.
    processlog_ref = models.CharField(db_column='ProcessLog_Ref', max_length=20, blank=True, null=True)  # Field name made lowercase.
    vouchersales_gt1 = models.FloatField(db_column='VoucherSales_GT1', blank=True, null=True)  # Field name made lowercase.
    vouchersales_gt2 = models.FloatField(db_column='VoucherSales_GT2', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'DailySalesData_Detail'
