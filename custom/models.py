from django.db import models
from cl_table.models import (Treatment, Stock, ItemStatus, Customer, TmpItemHelper, FocReason,
DepositAccount,PrepaidAccount)
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# Create your models here.
#intial

#Final

class EmpLevel(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    level_code = models.CharField(db_column='Level_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    level_desc = models.CharField(db_column='Level_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    level_isactive = models.BooleanField(db_column='Level_IsActive',default=True)  # Field name made lowercase.
    level_sequence = models.IntegerField(db_column='Level_sequence', blank=True, null=True)  # Field name made lowercase.
    level_spa = models.BooleanField(db_column='Level_SPA', null=True)  # Field name made lowercase.
    mintarget = models.FloatField(db_column='MinTarget', blank=True, null=True)  # Field name made lowercase.
    fromsalary = models.FloatField(db_column='FromSalary', blank=True, null=True)  # Field name made lowercase.
    tosalary = models.FloatField(db_column='ToSalary', blank=True, null=True)  # Field name made lowercase.
    getgroupcomm = models.BooleanField(db_column='GetGroupComm', blank=True, null=True)  # Field name made lowercase.
    group_code = models.CharField(db_column='Group_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        db_table = 'Emp_Level'
    
    def __str__(self):
        return str(self.level_desc)

class Room(models.Model):
    room_code = models.CharField(db_column='Room_Code', max_length=10, blank=True, null=True)  # Field name made lowercase.
    displayname = models.CharField(db_column='DisplayName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='Isactive', blank=True, null=True,default=True)  # Field name made lowercase.
    equipment = models.CharField(db_column='Equipment', max_length=50, blank=True, null=True)  # Field name made lowercase.
    Site_Codeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    id = models.AutoField(primary_key=True)
    roomtype = models.CharField(db_column='roomType', max_length=20, blank=True, null=True)  # Field name made lowercase.
    equipmentpicturelocation = models.CharField(db_column='equipmentPictureLocation', max_length=100, blank=True, null=True)  # Field name made lowercase.
    Sequence_No = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    Room_PIC = models.ImageField(upload_to='img', null=True)

    class Meta:
        db_table = 'Room'

    def __str__(self):
        return str(self.displayname)          

# new tabel
class Combo_Services(models.Model):
    
    id = models.AutoField(primary_key=True)
    services = models.ManyToManyField(Stock, blank=True)
    unit_price = models.FloatField(db_column='Unit_Price',null=True)  # Field name made lowercase.
    Price = models.DecimalField(max_digits=5,decimal_places=2,null=True)
    discount = models.FloatField(null=True)
    updated_at  = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    Isactive = models.BooleanField(default=True)
    Site_Code = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, null=True)

    class Meta:
        db_table = 'Combo_Services'

    def __str__(self):
        services = ""
        for i in self.services.all():
            if i.item_desc:
                if services == '':
                    services += i.item_desc
                else:
                    services += ","+i.item_desc

        return str(services)

   
    @property
    def get_combo_names(self,obj):
        if obj.services.all():
            string = ""
            for i in obj.services.all():
                if string == "":
                    string = string + i.item_desc
                elif not string == "":
                    string = string +","+ i.item_desc
            return string
        else:
            return None                               

class RoundPoint(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    point = models.FloatField(db_column='Point', blank=True, null=True)  # Field name made lowercase.
    roundvalue = models.FloatField(db_column='RoundValue', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Round_Point'

    def __str__(self):
        return str(self.point) 

class RoundSales(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sales = models.FloatField(db_column='Sales', blank=True, null=True)  # Field name made lowercase.
    roundvalue = models.FloatField(db_column='RoundValue', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        db_table = 'Round_Sales'

    def __str__(self):
        return str(self.roundvalue)    

class PaymentRemarks(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    r_code = models.CharField(db_column='R_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    r_desc = models.CharField(db_column='R_Desc', max_length=100, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='IsActive',default=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'Payment_Remarks'

    def __str__(self):
        return str(self.r_desc)

class HolditemSetup(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    hold_code = models.CharField(db_column='Hold_code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    hold_desc = models.CharField(db_column='Hold_Desc', max_length=50, blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'HoldItem_Setup'

    def __str__(self):
        return str(self.hold_desc)            

class VoucherRecord(models.Model):
    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20, blank=True, null=True)
    voucher_name = models.CharField(db_column='Voucher_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    voucher_no = models.CharField(db_column='Voucher_No', max_length=50, blank=True, null=True)  # Field name made lowercase.
    value = models.FloatField(db_column='Value', blank=True, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    cust_codeid = models.ForeignKey('cl_table.Customer', on_delete=models.PROTECT,db_column='Cust_codeid',null=True)  # Field name made lowercase.
    cust_code = models.CharField(db_column='Cust_code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    cust_name = models.CharField(db_column='Cust_Name', max_length=100, blank=True, null=True)  # Field name made lowercase.
    percent = models.FloatField(db_column='Percent', blank=True, null=True)  # Field name made lowercase.
    site_codeid =  models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, db_column='Site_Codeid',null=True)  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    issued_expiry_date = models.DateTimeField(db_column='issued_Expiry_Date', blank=True, null=True)  # Field name made lowercase.
    issued_staff = models.CharField(db_column='issued_Staff', max_length=50, blank=True, null=True)  # Field name made lowercase.
    onhold = models.CharField(db_column='onHold', max_length=50, blank=True, null=True)  # Field name made lowercase.
    paymenttype = models.CharField(db_column='PaymentType', max_length=50, blank=True, null=True)  # Field name made lowercase.
    remark = models.CharField(db_column='Remark', max_length=100, blank=True, null=True)  # Field name made lowercase.
    type_code = models.CharField(max_length=50, blank=True, null=True)
    used = models.IntegerField(db_column='Used', blank=True, null=True)  # Field name made lowercase.
    ref_fullvoucherno = models.CharField(db_column='Ref_FullVoucherNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ref_rangefrom = models.CharField(db_column='Ref_RangeFrom', max_length=20, blank=True, null=True)  # Field name made lowercase.
    ref_rangeto = models.CharField(db_column='Ref_RangeTo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    site_allocate = models.CharField(db_column='Site_Allocate', max_length=20, blank=True, null=True)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    isvalid = models.BooleanField(db_column='isValid',default=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Voucher_Record'

    def __str__(self):
        return str(self.voucher_no)     

class ItemCart(models.Model):
    STATUS = [
        ("Inprogress", "Inprogress" ),
        ("Suspension", "Suspension"),
        ("Completed", "Completed"),
    ]

    CHECK = [
        ("New", "New" ),
        ("Old", "Old"),
    ]

    TYPE = [
        ('Deposit', 'Deposit'),
        ('Top Up', 'Top Up'),
        ('Sales','Sales'),
        ('VT-Deposit', 'VT-Deposit'),
        ('VT-Top Up', 'VT-Top Up'),
        ('VT-Sales','VT-Sales'),
    ]

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    phonenumber = models.CharField(db_column='phoneNumber', max_length=255, blank=True, null=True)  # Field name made lowercase.
    customercode = models.CharField(db_column='customerCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemcodeid = models.ForeignKey('cl_table.Stock', on_delete=models.PROTECT,db_column='itemCodeid', null=True)   # Field name made lowercase.
    itemcode = models.CharField(db_column='itemCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    itemdesc = models.CharField(db_column='itemDesc', max_length=500, blank=True, null=True)  # Field name made lowercase.
    quantity = models.IntegerField(blank=True, null=True)
    price = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    sitecodeid = models.ForeignKey('cl_app.ItemSitelist', on_delete=models.PROTECT, db_column='sitecodeid', null=True)  # Field name made lowercase.
    sitecode = models.CharField(db_column='siteCode', max_length=20, blank=True, null=True)  # Field name made lowercase.
    isactive = models.BooleanField(db_column='isActive', blank=True, null=True, default=True)  # Field name made lowercase.
    timstamp = models.DateTimeField(db_column='timStamp', blank=True, null=True)  # Field name made lowercase.
    redeempoint = models.FloatField(db_column='redeemPoint', blank=True, null=True)  # Field name made lowercase.
    updated_at  = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    Appointment = models.ForeignKey('cl_table.Appointment', on_delete=models.PROTECT, null=True)
    discount = models.FloatField(default=0.0,  null=True)
    discount_amt = models.FloatField(default=0.0,  null=True)
    discount_price = models.FloatField(default=0.0,  null=True)
    sales_staff = models.ManyToManyField('cl_table.Employee',related_name='sales_staff', blank=True)
    service_staff = models.ManyToManyField('cl_table.Employee',related_name='service_staff',  blank=True)
    tax = models.FloatField(  null=True)
    is_payment = models.BooleanField(default=False,null=True)
    additional_discount = models.FloatField( null=True,default=0.0)
    additional_discountamt = models.FloatField( null=True,default=0.0)
    deposit = models.FloatField(default=0.0,  null=True)
    total_price = models.FloatField(default=0.0,  null=True)
    trans_amt = models.FloatField(default=0.0,  null=True)
    itemstatus = models.ForeignKey('cl_table.ItemStatus', on_delete=models.PROTECT,null=True)
    cust_noid =  models.ForeignKey(Customer, on_delete=models.PROTECT,null=True)
    cart_id = models.CharField(max_length=20, null=True)
    cart_date = models.DateField(db_column='Cart_Date',null=True)  # Field name made lowercase.
    cart_status = models.CharField(db_column='Cart_Status', max_length=20, choices=STATUS,default='Inprogress')  # Field name made lowercase.
    lineno = models.IntegerField(db_column='LineNo',null=True)  # Field name made lowercase.
    check = models.CharField(db_column='Check', max_length=20, choices=CHECK, null=True)  # Field name made lowercase.
    ratio = models.DecimalField(max_digits=18,decimal_places=15,db_column='Ratio',null=True)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=20,  null=True)
    helper_ids = models.ManyToManyField('cl_table.TmpItemHelper', related_name='itemhelper', blank=True)
    remark = models.CharField(db_column='Remark', max_length=500, null=True)  # Field name made lowercase.
    products_used = models.ManyToManyField('cl_table.Stock',related_name='salon_product', blank=True)   # Field name made lowercase.
    disc_reason = models.ManyToManyField('custom.PaymentRemarks', blank=True)
    discreason_txt = models.CharField(max_length=500,  null=True)  # Field name made lowercase.
    focreason = models.ForeignKey('cl_table.FocReason', on_delete=models.PROTECT,null=True)
    holditemqty = models.IntegerField(db_column='HoldItemQty', null=True)  # Field name made lowercase.
    holdreason = models.ForeignKey('custom.HolditemSetup', on_delete=models.PROTECT,null=True)
    item_uom = models.ForeignKey('cl_table.ItemUom',  on_delete=models.PROTECT,null=True)
    pos_disc = models.ManyToManyField('cl_table.PosDisc', blank=True)
    auto = models.BooleanField(default=True)
    done_sessions = models.CharField(db_column='Done_Sessions', max_length=700, blank=True, null=True)
    type = models.CharField(db_column='Type', max_length=10, blank=True, null=True, choices=TYPE)  # Field name made lowercase.
    treatment_account = models.ForeignKey('cl_table.TreatmentAccount',related_name='trmtacc', on_delete=models.PROTECT,blank=True, null=True)
    treatment = models.ForeignKey('cl_table.Treatment',related_name='Treatment', on_delete=models.PROTECT,blank=True, null=True)
    deposit_account = models.ForeignKey('cl_table.DepositAccount', on_delete=models.PROTECT,blank=True, null=True)
    prepaid_account = models.ForeignKey('cl_table.PrepaidAccount', on_delete=models.PROTECT,blank=True, null=True)
    is_foc =  models.BooleanField(default=False)
    
    class Meta:
        db_table = 'item_Cart'

    def __str__(self):
        return str(self.itemdesc)   


class PosPackagedeposit(models.Model):

    STATUS = [
        ("PENDING", "PENDING" ),
        ("COMPLETED", "COMPLETED"),
    ]

    id = models.AutoField(db_column='ID',primary_key=True)  # Field name made lowercase.
    cas_logno = models.CharField(db_column='cas_logNo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    sa_date = models.DateTimeField(db_column='sa_Date', blank=True, null=True, default=timezone.now, editable=False)  # Field name made lowercase.
    sa_time = models.DateTimeField(db_column='sa_Time', blank=True, null=True, default=timezone.now, editable=False)  # Field name made lowercase.
    sa_transacno = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(db_column='Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=80, blank=True, null=True)  # Field name made lowercase.
    price = models.FloatField(db_column='Price', blank=True, null=True)  # Field name made lowercase.
    discount = models.CharField(db_column='Discount', max_length=20, blank=True, null=True)  # Field name made lowercase.
    package_code = models.CharField(db_column='Package_Code', max_length=20, blank=True, null=True)  # Field name made lowercase.
    package_description = models.CharField(db_column='Package_Description', max_length=80, blank=True, null=True)  # Field name made lowercase.
    qty = models.IntegerField(db_column='Qty', blank=True, null=True)  # Field name made lowercase.
    unit_price = models.FloatField(db_column='Unit_Price', blank=True, null=True)  # Field name made lowercase.
    ttl_uprice = models.FloatField(db_column='Ttl_Uprice')  # Field name made lowercase.
    site_code = models.CharField(db_column='Site_Code', max_length=20)  # Field name made lowercase.
    dt_lineno = models.IntegerField(db_column='dt_LineNo', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(db_column='Status', max_length=20,choices=STATUS, blank=True, null=True)  # Field name made lowercase.
    deposit_amt = models.FloatField(db_column='Deposit_Amt')  # Field name made lowercase.
    deposit_lineno = models.IntegerField(db_column='Deposit_LineNo', blank=True, null=True)  # Field name made lowercase.
    hold_qty = models.FloatField(db_column='Hold_Qty', blank=True, null=True)  # Field name made lowercase.
    itemcart = models.ForeignKey('custom.ItemCart', on_delete=models.PROTECT,null=True)
    auto = models.BooleanField(default=True)

    class Meta:
        db_table = 'POS_PackageDeposit'

    def __str__(self):
        return str(self.code)    
