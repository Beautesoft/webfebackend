from django.contrib import admin
from .models import (EmpLevel, Room, Combo_Services,ItemCart,VoucherRecord, RoundPoint, RoundSales, 
PaymentRemarks, HolditemSetup, PosPackagedeposit)

# Register your models here.
admin.site.register(EmpLevel)
admin.site.register(Room)
admin.site.register(Combo_Services)
admin.site.register(ItemCart)
admin.site.register(VoucherRecord)
admin.site.register(RoundSales)
admin.site.register(PaymentRemarks)
admin.site.register(HolditemSetup)
admin.site.register(PosPackagedeposit)
