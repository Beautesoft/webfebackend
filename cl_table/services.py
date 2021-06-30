from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from custom.models import ItemCart, RoundSales, VoucherRecord, PosPackagedeposit
from .serializers import PosdaudSerializer
from .models import (Employee,  Fmspw, Customer, Treatment, Stock, Appointment,ItemDept, ControlNo, 
Treatment_Master,ItemClass,Paytable,PosTaud,PayGroup,PosDaud,PosHaud,GstSetting,PayGroup,TreatmentAccount, 
ItemStatus,Source,ApptType, ItemHelper, Multistaff, DepositType, TmpItemHelper, PosDisc, FocReason, Holditemdetail,
DepositAccount,PrepaidAccount,PrepaidAccountCondition,VoucherCondition,ItemUom,Title,PackageHdr,PackageDtl,
ItemBatch,Stktrn,ItemUomprice,Tmptreatment,ExchangeDtl)
from datetime import date, timedelta, datetime
import datetime
from django.utils import timezone
from custom.views import get_in_val
from cl_app.utils import general_error_response
from dateutil.relativedelta import relativedelta
from cl_app.models import ItemSitelist
from django.db.models import Q

def customeraccount(cust_obj, site):
   
    tr_outstanding = 0.0; pr_outstanding = 0.0; pe_outstanding = 0.0

    treat_ids = TreatmentAccount.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code, type='Deposit', 
    outstanding__gt = 0).order_by('pk')

    for i in treat_ids:
        acc_ids = TreatmentAccount.objects.filter(ref_transacno=i.sa_transacno,
        treatment_parentcode=i.treatment_parentcode,site_code=i.site_code).order_by('id').last()

        if acc_ids and acc_ids.outstanding:   
            tr_outstanding += acc_ids.outstanding

    depo_ids = DepositAccount.objects.filter(cust_code=cust_obj.cust_code,site_code=site.itemsite_code, type='Deposit', 
    outstanding__gt=0).order_by('pk')        
            
    for j in depo_ids:
        dacc_ids = DepositAccount.objects.filter(ref_transacno=j.sa_transacno,
        ref_productcode=j.treat_code,site_code=j.site_code).order_by('id').last()
        if dacc_ids and dacc_ids.outstanding:
            pr_outstanding += dacc_ids.outstanding

    pre_ids = PrepaidAccount.objects.filter(site_code=site.itemsite_code,cust_code=cust_obj.cust_code,
    sa_status__in=['DEPOSIT','SA'],outstanding__gt = 0).only('site_code','cust_code','sa_status').order_by('pk') 
    for k in pre_ids:
        last_acc_ids = PrepaidAccount.objects.filter(pp_no=k.pp_no,
        site_code=k.site_code,status=True,line_no=k.line_no).only('pp_no','site_code','status','line_no').last()
        
        if last_acc_ids and last_acc_ids.outstanding:
            pe_outstanding += last_acc_ids.outstanding

    value = tr_outstanding + pr_outstanding + pe_outstanding
    return "{:.2f}".format(value)    


def invoice_deposit(self, request, depo_ids, sa_transacno, cust_obj, outstanding):
    # try:
    if self:
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        empl = fmspw.Emp_Codeid
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
        outstanding_new = 0.0
        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()

        for idx, c in enumerate(depo_ids, start=1):
            if idx == 1:
                alsales_staff = c.sales_staff.all().first()

            # print(c,"cc")
            outstanding_acc =  float(c.trans_amt) - float(c.deposit)
            controlobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
            if not controlobj:
                result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
                raise serializers.ValidationError(result)
            treatment_parentcode = "TRM"+str(controlobj.control_prefix)+str(controlobj.Site_Codeid.itemsite_code)+str(controlobj.control_no)
            
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
                dt_itemdesc = c.itemcodeid.item_name +" "+"(FOC)"
            else:
                isfoc = False  
                item_remarks = None 
                dt_itemdesc = c.itemcodeid.item_name
            dt_combocode = ""
            dt_uom = None; dt_discuser = None ; lpackage = False; package_code = None
            record_detail_type = "SERVICE"
            if c.itemcodeid.Item_Divid.itm_code == '3':
                if c.itemcodeid.item_type == 'PACKAGE':
                    record_detail_type = "PACKAGE"
                    dt_combocode = c.itemcodeid.item_code
                else:    
                    record_detail_type = "SERVICE"
                # elif c.itemcodeid.item_type == 'COURSE':  
                #     record_detail_type = "PACKAGE"
                #     lpackage = True
                #     packobj = PackageDtl.objects.filter(code=str(c.itemcodeid.item_code)+"0000",isactive=True)
                #     if packobj:
                #         package_code = packobj[0].package_code

                dt_discuser = fmspw.pw_userlogin
            elif c.itemcodeid.Item_Divid.itm_code == '1':
                dt_uom = c.item_uom.uom_code
                record_detail_type = "PRODUCT"
                dt_discuser = fmspw.pw_userlogin
            elif c.itemcodeid.Item_Divid.itm_code == '5':
                record_detail_type = "PREPAID" 
                dt_discuser = None   
            elif c.itemcodeid.Item_Divid.itm_code == '4':
                record_detail_type = "VOUCHER" 
                dt_discuser = None      

            calcgst = 0
            if gst:
                calcgst = gst.item_value
            if calcgst > 0:
                sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                if sitegst:
                    if sitegst.site_is_gst == False:
                        calcgst = 0
            # print(calcgst,"0 calcgst")
            # Yoonus Tax Chcking
            gst_amt_collect = 0
            if calcgst > 0:
                if gst.is_exclusive == True:
                    gst_amt_collect = c.deposit * (calcgst/ 100)
                    # tax_amt = deposit_amt * (gst.item_value / 100)
                    # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
                else:
                    gst_amt_collect = c.deposit * calcgst / (100+calcgst)
                    # billable_amount = "{:.2f}".format(deposit_amt)
                    # tax_amt = deposit_amt * gst.item_value / (100+gst.item_value)
                    # Yoonus
            # gst_amt_collect = c.deposit * (gst.item_value / 100)
            
            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.display_name
                    elif not sales == "":
                        sales = sales +","+ i.display_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.display_name
                    elif not service == "":
                        service = service +","+ s.display_name 


            dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid,
            dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=dt_itemdesc,dt_price=c.price,
            dt_promoprice="{:.2f}".format(float(c.discount_price)),dt_amt="{:.2f}".format(float(c.trans_amt)),dt_qty=c.quantity,
            dt_discamt="{:.2f}".format(float(totaldisc)),dt_combocode=dt_combocode,
            dt_discpercent=dt_discPercent,dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            dt_discuser=dt_discuser,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            dt_transacamt="{:.2f}".format(float(c.trans_amt)),dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,itemcart=c,
            st_ref_treatmentcode=None,record_detail_type=record_detail_type,gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
            topup_outstanding=outstanding_acc,dt_remark=c.remark,isfoc=isfoc,item_remarks=item_remarks,
            dt_uom=dt_uom,first_trmt_done=False,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
            staffs=sales +" "+"/"+" "+ service)
            #appt_time=app_obj.appt_fr_time,                
            #st_ref_treatmentcode=treatment_parentcode,

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
                multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
                emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
                dt_lineno=c.lineno)
                multi.save()
                # print(multi.id,"multi")

            if int(c.itemcodeid.item_div) == 3 and c.itemcodeid.item_type == 'PACKAGE':
                # print(c.itemcodeid.item_code,"entering package")
                packhdr_ids = PackageHdr.objects.filter(code=c.itemcodeid.item_code).first()
                if packhdr_ids:
                    packdtl_ids = PackageDtl.objects.filter(package_code=packhdr_ids.code,isactive=True)
                    if packdtl_ids:
                        for pa in packdtl_ids:
                            packdtl_code = str(pa.code)
                            itm_code = packdtl_code[:-4]
                            # print(itm_code,"itm_code2")
                            itmstock = Stock.objects.filter(item_code=itm_code,item_isactive=True).first()
                            if itmstock:
                                # print(itmstock.Item_Divid,"itm_code1")0.y
                                p = None
                                pa_ppremain = 0
                                if c.itemcodeid.prepaid_value:
                                    pa_ppremain = c.itemcodeid.prepaid_value
                                if c.is_foc == True:
                                    pa_trasac = 0
                                else:
                                    pa_trasac = pa.price * pa.qty
                                pa_deposit = pa_trasac
                                pa_outstanding_acc = 0
                                paqty = pa.qty
                                pos_ids = PosPackagedeposit.objects.filter(itemcart=c,code=pa.code)
                                if pos_ids:
                                    p = pos_ids.first()
                                    pa_trasac = p.price * p.qty
                                    pa_deposit = p.deposit_amt
                                    pa_ppremain = p.deposit_amt
                                    #outstanding_acc =  float(c.trans_amt) - float(c.deposit)
                                    pa_outstanding_acc = float(pa_trasac) - float(pa_deposit)
                                    # pa_qty = p.qty
                                # print(itmstock.Item_Divid,"itm_code")
                                if pa_trasac >= 0:
                                    if int(itmstock.Item_Divid.itm_code) == 3 and itmstock.Item_Divid.itm_desc == 'SERVICES' and itmstock.Item_Divid.itm_isactive == True:
                                        pscontrolobj = ControlNo.objects.filter(control_description__iexact="Treatment",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                        if not pscontrolobj:
                                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Treatment Control No does not exist!!",'error': True} 
                                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 
                                        
                                        patreatment_parentcode = "TRM"+str(pscontrolobj.control_prefix)+str(pscontrolobj.Site_Codeid.itemsite_code)+str(pscontrolobj.control_no)
                                        
                                        desc = "Total Service Amount : "+str("{:.2f}".format(float(pa_trasac)))
                                        
                                        # amount="{:.2f}".format(float(c.deposit)),
                                        # balance="{:.2f}".format(float(c.deposit)),deposit="{:.2f}".format(float(c.deposit))

                                        #treatment Account creation
                                        patreatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                                        description=desc,type="Deposit",amount="{:.2f}".format(float(pa_deposit)),
                                        balance="{:.2f}".format(float(pa_deposit)),User_Nameid=fmspw,
                                        user_name=fmspw.pw_userlogin,ref_transacno=sa_transacno,sa_transacno=sa_transacno,
                                        qty=paqty,outstanding="{:.2f}".format(float(pa_outstanding_acc)),deposit="{:.2f}".format(float(pa_deposit)),
                                        treatment_parentcode=patreatment_parentcode,treatment_code="",sa_status="SA",
                                        cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),dt_lineno=c.lineno,
                                        lpackage=True,package_code=packhdr_ids.code,
                                        Site_Codeid=site,site_code=site.itemsite_code,treat_code=patreatment_parentcode,itemcart=c,
                                        focreason=item_remarks)
                                        patreatacc.save()

                                        # print(treatacc.id,"Yoonustreatacc")
                                        if c.is_foc == True:
                                            courseval = itmstock.item_name +" "+"(FOC)"
                                            trisfoc_val = True
                                        else:
                                            courseval = itmstock.item_name 
                                            trisfoc_val = False
                                        
                                        expiry = None
                                        if itmstock.service_expire_active == True:
                                            month = itmstock.service_expire_month
                                            current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                                            expiry = current_date + relativedelta(months=month)

                                        # paqty = pa_qty
                                        for i in range(1,int(paqty)+1):
                                            # treat = c
                                            # Price = c.trans_amt
                                            Price = pa_trasac
                                            # Unit_Amount = Price / c.quantity
                                            Unit_Amount = Price / paqty
                                            times = str(i).zfill(2)
                                            treatment_no = str(paqty).zfill(2)

                                            # print(patreatment_parentcode,"Yoonuspatreatment")
                                            patreatmentid = Treatment(treatment_code=str(patreatment_parentcode)+"-"+str(times),
                                            treatment_parentcode=patreatment_parentcode,course=courseval,times=times,
                                            treatment_no=treatment_no,price="{:.2f}".format(float(Price)),unit_amount="{:.2f}".format(float(Unit_Amount)),Cust_Codeid=cust_obj,
                                            cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name,
                                            status="Open",item_code=str(itmstock.item_code)+"0000",Item_Codeid=itmstock,
                                            sa_transacno=sa_transacno,sa_status="SA",type="N",trmt_is_auto_proportion=False,
                                            dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,isfoc=trisfoc_val,
                                            treatment_account=patreatacc,service_itembarcode=str(itmstock.item_code)+"0000",
                                            lpackage=True,package_code=packhdr_ids.code,expiry=expiry)
                                            patreatmentid.save()

                                        if patreatacc:
                                            pscontrolobj.control_no = int(pscontrolobj.control_no) + 1
                                            pscontrolobj.save()
                                            if c.is_foc == False:
                                                if p:
                                                    p.sa_transacno = sa_transacno
                                                    p.status = "COMPLETED"
                                                    p.save()

                                    elif int(itmstock.Item_Divid.itm_code) == 1 and itmstock.Item_Divid.itm_desc == 'RETAIL PRODUCT' and itmstock.Item_Divid.itm_isactive == True:
                                        desc = "Total Product Amount : "+str("{:.2f}".format(float(pa_trasac)))
                                        #Deposit Account creation
                                        
                                        padecontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                        if not padecontrolobj:
                                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                        patreat_code = str(padecontrolobj.Site_Codeid.itemsite_code)+str(padecontrolobj.control_no)
                                        
                                        if c.is_foc == True:
                                            item_descriptionval = itmstock.item_name+" "+"(FOC)"
                                        else:
                                            item_descriptionval = itmstock.item_name
                                        # print(item_descriptionval,"item_descriptionval")
                                        
                                        # amount="{:.2f}".format(float(c.deposit)),
                                        # balance="{:.2f}".format(float(c.deposit)),deposit="{:.2f}".format(float(c.deposit))

                                        padepoacc = DepositAccount(cust_code=cust_obj.cust_code,type="Deposit",amount="{:.2f}".format(float(pa_deposit)),
                                        balance="{:.2f}".format(float(pa_deposit)),user_name=fmspw.pw_userlogin,qty=paqty,outstanding="{:.2f}".format(float(pa_outstanding_acc)),
                                        deposit="{:.2f}".format(float(pa_deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                                        deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                                        sa_status="SA",item_barcode=packdtl_code,item_description=item_descriptionval,
                                        treat_code=patreat_code,void_link=None,lpackage=True,package_code=packhdr_ids.code,
                                        dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                                        ref_transacno=sa_transacno,ref_productcode=patreat_code,Item_Codeid=itmstock,
                                        item_code=itmstock.item_code)
                                        padepoacc.save()
                                        # print(depoacc.pk,"depoacc")
                                        if padepoacc.pk:
                                            padecontrolobj.control_no = int(padecontrolobj.control_no) + 1
                                            padecontrolobj.save()
                                            if c.is_foc == False:
                                                if p:
                                                    p.sa_transacno = sa_transacno
                                                    p.status = "COMPLETED"
                                                    p.save()
                                            # p.sa_transacno = sa_transacno
                                            # p.status = "COMPLETED"
                                            # p.save()

                                        if p:
                                            if p.hold_qty and int(p.hold_qty) > 0:
                                                p_con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                                if not p_con_obj:
                                                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
                                                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                                product_issues_no = str(p_con_obj.control_prefix)+str(p_con_obj.Site_Codeid.itemsite_code)+str(p_con_obj.control_no)
                                            
                                                hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
                                                transacamt=pa_trasac,itemno=itmstock.item_code+"0000",
                                                hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                                hi_itemdesc=itmstock.item_desc,hi_price=p.unit_price,hi_amt=pa_trasac,hi_qty=p.qty,
                                                hi_discamt=p.discount,hi_discpercent=p.discount,hi_discdesc=None,
                                                hi_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                                                hi_lineno=c.lineno,hi_uom=pa.uom,hold_item=True,hi_deposit=pa_deposit,
                                                holditemqty=p.hold_qty,status="OPEN",sa_custno=cust_obj.cust_code,
                                                sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
                                                product_issues_no=product_issues_no)
                                                hold.save()
                                                # print(hold.pk,"hold")
                                                if hold.pk:
                                                    p_con_obj.control_no = int(p_con_obj.control_no) + 1
                                                    p_con_obj.save()
                                                    dtl.holditemqty = int(p.hold_qty)
                                                    dtl.save()    

                                    elif int(itmstock.Item_Divid.itm_code) == 5 and itmstock.Item_Divid.itm_desc == 'PREPAID' and itmstock.Item_Divid.itm_isactive == True:
                                        #Prepaid Account creation
                                        #exp_date need to map
                                        pprepaid_valid_period = date.today() + timedelta(int(itmstock.prepaid_valid_period))
                                        ppbonus = itmstock.prepaid_value - itmstock.prepaid_sell_amt

                                        if c.is_foc == True:
                                            ppdescval = itmstock.item_name+" "+"(FOC)"
                                            print(ppdescval,"ppdescval")
                                        else:
                                            ppdescval = itmstock.item_name
                                        
                                        #remain=c.deposit
                                        paprepacc = PrepaidAccount(pp_no=sa_transacno,pp_type=itmstock.item_range,
                                        pp_desc=ppdescval,exp_date=pprepaid_valid_period,cust_code=cust_obj.cust_code,
                                        cust_name=cust_obj.cust_name,pp_amt=itmstock.prepaid_sell_amt,pp_total=itmstock.prepaid_value,
                                        pp_bonus=ppbonus,transac_no="",item_no="",use_amt=0,remain=pa_ppremain,ref1="",
                                        ref2="",status=True,site_code=site.itemsite_code,sa_status="DEPOSIT",exp_status=True,
                                        voucher_no='',isvoucher=False,has_deposit=True,topup_amt=pa_deposit,
                                        outstanding=pa_outstanding_acc,active_deposit_bonus=True,topup_no="",topup_date=None,
                                        line_no=c.lineno,staff_name=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                                        staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        pp_type2=None,condition_type1=None,pos_daud_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,
                                        Item_Codeid=itmstock,item_code=itmstock.item_code,lpackage=True,package_code=packhdr_ids.code,
                                        package_code_lineno=p.deposit_lineno)
                                        paprepacc.save()
                                        # print(paprepacc.pk,"paprepacc")

                                        vo_obj = VoucherCondition.objects.filter(item_code=itmstock.item_code)
                                        # print(vo_obj,"vo_obj")
                                        #PrepaidAccountCondition Creation
                                        if vo_obj:  
                                            ppacc = PrepaidAccountCondition(pp_no=sa_transacno,pp_type=itmstock.item_range,
                                            pp_desc=ppdescval,p_itemtype=','.join([v.p_itemtype for v in vo_obj if v.p_itemtype]),
                                            item_code=itmstock.item_code,conditiontype1=','.join([v.conditiontype1 for v in vo_obj if v.conditiontype1]),
                                            conditiontype2=','.join([v.conditiontype2 for v in vo_obj if v.conditiontype2]),
                                            amount=vo_obj.first().amount,rate=vo_obj.first().rate,use_amt=0,remain=pa_ppremain,
                                            pos_daud_lineno=c.lineno,lpackage=True,package_code=packhdr_ids.code,package_code_lineno=p.deposit_lineno)
                                            ppacc.save()
                                            # print(ppacc.pk,"ppacc")
                                            PrepaidAccount.objects.filter(pk=paprepacc.pk).update(pp_type2=ppacc.pp_type,
                                            condition_type1=ppacc.conditiontype1)


                                        if c.is_foc == False:
                                            if p:
                                                p.sa_transacno = sa_transacno
                                                p.status = "COMPLETED"
                                                p.save()
                                        # p.sa_transacno = sa_transacno
                                        # p.status = "COMPLETED"
                                        # p.save()
    
                                    elif int(itmstock.Item_Divid.itm_code) == 4 and itmstock.Item_Divid.itm_desc == 'VOUCHER' and itmstock.Item_Divid.itm_isactive == True:
                                        pavorecontrolobj = ControlNo.objects.filter(control_description__iexact="Public Voucher",Site_Codeid__pk=fmspw.loginsite.pk).first()
                                        if not pavorecontrolobj:
                                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher Record Control No does not exist!!",'error': True} 
                                            return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                                        vouchercode = str(pavorecontrolobj.control_prefix)+str(pavorecontrolobj.Site_Codeid.itemsite_code)+str(pavorecontrolobj.control_no)
                                        
                                        if itmstock.voucher_value_is_amount == True:
                                            vopercent = 0
                                        else:
                                            if itmstock.voucher_value_is_amount == False:
                                                vopercent =itmstock.voucher_value
                                        
                                        if itmstock.voucher_valid_period:
                                            date_1 = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                                            # print(date_1,"date_1")
                                            end_date = date_1 + datetime.timedelta(days=int(itmstock.voucher_valid_period))
                                            # print(end_date,"end_date")
                                            # tod_now = datetime.now(pytz.timezone(TIME_ZONE))
                                            # print(tod_now,"tod_now")
                                            # voexpiry = tod_now + datetime.timedelta(days=c.itemcodeid.voucher_valid_period)
                                            # print(voexpiry,"voexpiry")
                                            # expiry = datetime.datetime.combine(end_date, datetime.datetime.min.time())

                                            # expiry = end_date.strftime("%d-%m-%Y")
                                            # print(expiry,"expiry") 

                                        if c.is_foc == True:
                                            vouchernameval = itmstock.item_name+" "+"(FOC)"
                                        else:
                                            vouchernameval = itmstock.item_name    
                                        
                                        #value=c.price
                                        vorec = VoucherRecord(sa_transacno=sa_transacno,voucher_name=vouchernameval,
                                        voucher_no=vouchercode,value=p.ttl_uprice,cust_codeid=cust_obj,cust_code=cust_obj.cust_code,
                                        cust_name=cust_obj.cust_name,percent=vopercent,site_codeid=site,site_code=site.itemsite_code,
                                        issued_expiry_date=end_date if end_date else None,issued_staff=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                                        onhold=0,paymenttype=None,remark=None,type_code=pavorecontrolobj.control_prefix,used=0,
                                        ref_fullvoucherno=None,ref_rangefrom=None,ref_rangeto=None,site_allocate=None,dt_lineno=c.lineno)
                                        vorec.save()
                                        if vorec.pk:
                                            pavorecontrolobj.control_no = int(pavorecontrolobj.control_no) + 1
                                            pavorecontrolobj.save()
                                            if c.is_foc == False:
                                                if p:
                                                    p.sa_transacno = sa_transacno
                                                    p.status = "COMPLETED"
                                                    p.save()
                                            # p.sa_transacno = sa_transacno
                                            # p.status = "COMPLETED"
                                            # p.save()

            
            if int(c.itemcodeid.Item_Divid.itm_code) == 3 and c.itemcodeid.Item_Divid.itm_desc == 'SERVICES' and c.itemcodeid.Item_Divid.itm_isactive == True and c.itemcodeid.item_type != "PACKAGE":
                desc = "Total Service Amount : "+str("{:.2f}".format(float(c.trans_amt)))

                #treatment Account creation
                treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                description=desc,type="Deposit",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(c.deposit)),User_Nameid=fmspw,
                user_name=fmspw.pw_userlogin,ref_transacno=sa_transacno,sa_transacno=sa_transacno,
                qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)),deposit="{:.2f}".format(float(c.deposit)),
                lpackage=lpackage,treatment_parentcode=treatment_parentcode,treatment_code="",sa_status="SA",
                cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),dt_lineno=c.lineno,
                Site_Codeid=site,site_code=site.itemsite_code,treat_code=treatment_parentcode,itemcart=c,
                focreason=item_remarks,package_code=package_code)
                treatacc.save()
                # print(treatacc.id,"treatacc")
            elif int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                desc = "Total Product Amount : "+str("{:.2f}".format(float(c.trans_amt)))
                #Deposit Account creation
                
                decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                if not decontrolobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

                treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                
                if c.is_foc == True:
                    item_descriptionval = c.itemcodeid.item_name+" "+"(FOC)"
                else:
                    item_descriptionval = c.itemcodeid.item_name
                # print(item_descriptionval,"item_descriptionval")
                depoacc = DepositAccount(cust_code=cust_obj.cust_code,type="Deposit",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(c.deposit)),user_name=fmspw.pw_userlogin,qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)),
                deposit="{:.2f}".format(float(c.deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                sa_status="SA",item_barcode=str(c.itemcodeid.item_code)+"0000",item_description=item_descriptionval,
                treat_code=treat_code,void_link=None,lpackage=None,package_code=None,
                dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                ref_transacno=sa_transacno,ref_productcode=treat_code,Item_Codeid=c.itemcodeid,
                item_code=c.itemcodeid.item_code)
                depoacc.save()
                # print(depoacc.pk,"depoacc")
                if depoacc.pk:
                    decontrolobj.control_no = int(decontrolobj.control_no) + 1
                    decontrolobj.save()

                    qtytodeduct = c.quantity
                    if c.holditemqty and int(c.holditemqty) > 0:
                        qtytodeduct = c.quantity - int(c.holditemqty)

                    if qtytodeduct > 0:
                        batchids = ItemBatch.objects.filter(site_code=site.itemsite_code,item_code=str(c.itemcodeid.item_code),
                        uom=c.item_uom.uom_code).order_by('pk').last() 
                        #ItemBatch
                        if batchids:
                            # deduct = batchids.qty - c.quantity
                            deduct = batchids.qty - qtytodeduct
                            batch = ItemBatch.objects.filter(pk=batchids.pk).update(qty=deduct,updated_at=timezone.now())
                        else:
                            batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                            batch_no="",uom=c.item_uom.uom_code,qty=-qtytodeduct,exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                            # batch_no="",uom=c.item_uom.uom_code,qty=-c.quantity,exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                            # deduct = -c.quantity
                            deduct = -qtytodeduct

                        #Stktrn
                        currenttime = timezone.now()
                        currentdate = timezone.now().date()
                   
                        post_time = str(currenttime.hour).zfill(2)+str(currenttime.minute).zfill(2)+str(currenttime.second).zfill(2)
                        stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,itemcode=str(c.itemcodeid.item_code)+"0000",
                        item_uom=c.item_uom.uom_code).order_by('pk').last() 

                        # trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-c.quantity,trn_balqty=deduct,
                        stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,itemcode=str(c.itemcodeid.item_code)+"0000",
                        store_no=site.itemsite_code,tstore_no=None,fstore_no=None,trn_docno=sa_transacno,trn_date=currentdate,
                        trn_type="SA",trn_db_qty=None,trn_cr_qty=None,trn_qty=-qtytodeduct,trn_balqty=deduct,
                        trn_balcst=stktrn_ids.trn_balcst if stktrn_ids and stktrn_ids.trn_balcst else 0,
                        trn_amt="{:.2f}".format(float(c.deposit)),trn_post=currentdate,
                        trn_cost=stktrn_ids.trn_cost if stktrn_ids and stktrn_ids.trn_cost else 0,trn_ref=None,
                        hq_update=stktrn_ids.hq_update if stktrn_ids and stktrn_ids.hq_update else 0,
                        line_no=c.lineno,item_uom=c.item_uom.uom_code,item_batch=None,mov_type=None,item_batch_cost=None,
                        stock_in=None,trans_package_line_no=None).save()

            elif int(c.itemcodeid.Item_Divid.itm_code) == 5 and c.itemcodeid.Item_Divid.itm_desc == 'PREPAID' and c.itemcodeid.Item_Divid.itm_isactive == True:
                #Prepaid Account creation
                #exp_date need to map
                prepaid_valid_period = date.today() + timedelta(int(c.itemcodeid.prepaid_valid_period))
                pp_bonus = c.itemcodeid.prepaid_value - c.itemcodeid.prepaid_sell_amt

                if c.is_foc == True:
                    pp_descval = c.itemcodeid.item_name+" "+"(FOC)"
                else:
                    pp_descval = c.itemcodeid.item_name

                if c.itemcodeid.prepaid_sell_amt == c.deposit:
                    remain=c.itemcodeid.prepaid_value
                else:
                    remain=c.deposit

                if c.is_foc == True:
                    remain=c.itemcodeid.prepaid_value

                prepacc = PrepaidAccount(pp_no=sa_transacno,pp_type=c.itemcodeid.item_range,
                pp_desc=pp_descval,exp_date=prepaid_valid_period,cust_code=cust_obj.cust_code,
                cust_name=cust_obj.cust_name[:50],pp_amt=c.itemcodeid.prepaid_sell_amt,pp_total=c.itemcodeid.prepaid_value,
                pp_bonus=pp_bonus,transac_no="",item_no="",use_amt=0,remain=remain,ref1="",
                ref2="",status=True,site_code=site.itemsite_code,sa_status="DEPOSIT",exp_status=True,
                voucher_no='',isvoucher=False,has_deposit=True,topup_amt=c.deposit,
                outstanding=outstanding_acc,active_deposit_bonus=True,topup_no="",topup_date=None,
                line_no=c.lineno,staff_name=','.join([v.display_name for v in salesstaff if v.display_name]),
                staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                pp_type2=None,condition_type1=None,pos_daud_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,
                Item_Codeid=c.itemcodeid,item_code=c.itemcodeid.item_code)
                prepacc.save()
                # print(prepacc.pk,"prepacc")

                vo_obj = VoucherCondition.objects.filter(item_code=c.itemcodeid.item_code)
                #PrepaidAccountCondition Creation
                # amount=vo_obj.first().amount,rate=vo_obj.first().rate,use_amt=0,remain=c.trans_amt,

                pp_acc = PrepaidAccountCondition(pp_no=sa_transacno,pp_type=c.itemcodeid.item_range,
                pp_desc=pp_descval,p_itemtype=','.join([v.p_itemtype for v in vo_obj if v.p_itemtype]),
                item_code=c.itemcodeid.item_code,conditiontype1=','.join([v.conditiontype1 for v in vo_obj if v.conditiontype1]),
                conditiontype2=','.join([v.conditiontype2 for v in vo_obj if v.conditiontype2]),
                amount=vo_obj.first().amount,rate=vo_obj.first().rate,use_amt=0,remain=remain,
                pos_daud_lineno=c.lineno)
                pp_acc.save()
                # print(pp_acc.pk,"pp_acc")
                PrepaidAccount.objects.filter(pk=prepacc.pk).update(pp_type2=pp_acc.pp_type,
                condition_type1=pp_acc.conditiontype1)

            elif int(c.itemcodeid.Item_Divid.itm_code) == 4 and c.itemcodeid.Item_Divid.itm_desc == 'VOUCHER' and c.itemcodeid.Item_Divid.itm_isactive == True:
                vorecontrolobj = ControlNo.objects.filter(control_description__iexact="Public Voucher",Site_Codeid__pk=fmspw.loginsite.pk).first()
                if not vorecontrolobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Voucher Record Control No does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

                voucher_code = str(vorecontrolobj.control_prefix)+str(vorecontrolobj.Site_Codeid.itemsite_code)+str(vorecontrolobj.control_no)
                
                if c.itemcodeid.voucher_value_is_amount == True:
                    vo_percent = 0
                else:
                    if c.itemcodeid.voucher_value_is_amount == False:
                        vo_percent = c.itemcodeid.voucher_value
                
                if c.itemcodeid.voucher_valid_period:
                    date_1 = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                    # print(date_1,"date_1")
                    end_date = date_1 + datetime.timedelta(days=int(c.itemcodeid.voucher_valid_period))
                    # print(end_date,"end_date")
                    # tod_now = datetime.now(pytz.timezone(TIME_ZONE))
                    # print(tod_now,"tod_now")
                    # voexpiry = tod_now + datetime.timedelta(days=c.itemcodeid.voucher_valid_period)
                    # print(voexpiry,"voexpiry")
                    # expiry = datetime.datetime.combine(end_date, datetime.datetime.min.time())

                    # expiry = end_date.strftime("%d-%m-%Y")
                    # print(expiry,"expiry") 

                if c.is_foc == True:
                    voucher_nameval = c.itemcodeid.item_name+" "+"(FOC)"
                else:
                    voucher_nameval = c.itemcodeid.item_name    

                vo_rec = VoucherRecord(sa_transacno=sa_transacno,voucher_name=voucher_nameval,
                voucher_no=voucher_code,value=c.price,cust_codeid=cust_obj,cust_code=cust_obj.cust_code,
                cust_name=cust_obj.cust_name,percent=vo_percent,site_codeid=site,site_code=site.itemsite_code,
                issued_expiry_date=end_date if end_date else None,issued_staff=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                onhold=0,paymenttype=None,remark=None,type_code=vorecontrolobj.control_prefix,used=0,
                ref_fullvoucherno=None,ref_rangefrom=None,ref_rangeto=None,site_allocate=None,dt_lineno=c.lineno,)
                vo_rec.save()
                if vo_rec.pk:
                    vorecontrolobj.control_no = int(vorecontrolobj.control_no) + 1
                    vorecontrolobj.save()

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
            discreason = None
            if int(c.itemcodeid.item_div) in [1,3] and c.itemcodeid.item_type == 'SINGLE':
                if c.pos_disc.all().exists():
                    # for d in c.disc_reason.all():
                    #     if d.r_code == '100006' and d.r_desc == 'Others':
                    #         discreason = c.discreason_txt
                    #     elif d.r_desc:
                    #         discreason = d.r_desc  
                        
                    for po in c.pos_disc.all():
                        po.sa_transacno = sa_transacno
                        po.dt_status = "SA"
                        po.dt_price = c.price
                        po.save()
                else:
                    if totaldisc == 0.0 or totalpercent == 0.0 and len(c.pos_disc.all()) == 0:
                        posdisc = PosDisc(sa_transacno=sa_transacno,dt_itemno=c.itemcodeid.item_code+"0000",disc_amt=totaldisc,
                        disc_percent=totalpercent,dt_lineno=c.lineno,remark=discreason,site_code=site.itemsite_code,
                        dt_status="SA",dt_auto=0,line_no=1,disc_user=empl.emp_code,lnow=1,dt_price=c.price,istransdisc=False)
                        posdisc.save()
                        # print(posdisc.pk,"posdisc")

                
            #HoldItemDetail creation for retail products
            if int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                if c.holditemqty and int(c.holditemqty) > 0:
                    con_obj = ControlNo.objects.filter(control_description__iexact="Product Issues",Site_Codeid__pk=fmspw.loginsite.pk).first()
                    if not con_obj:
                        result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Issues Control No does not exist!!",'error': True} 
                        raise serializers.ValidationError(result)

                    product_issues_no = str(con_obj.control_prefix)+str(con_obj.Site_Codeid.itemsite_code)+str(con_obj.control_no)
                    
                    hold = Holditemdetail(itemsite_code=site.itemsite_code,sa_transacno=sa_transacno,
                    transacamt=c.trans_amt,itemno=c.itemcodeid.item_code+"0000",
                    hi_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                    hi_itemdesc=c.itemcodeid.item_desc,hi_price=c.price,hi_amt=c.trans_amt,hi_qty=c.quantity,
                    hi_discamt=totaldisc,hi_discpercent=totalpercent,hi_discdesc=None,
                    hi_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                    hi_lineno=c.lineno,hi_uom=c.item_uom.uom_code,hold_item=True,hi_deposit=c.deposit,
                    holditemqty=c.holditemqty,status="OPEN",sa_custno=cust_obj.cust_code,
                    sa_custname=cust_obj.cust_name,history_line=1,hold_type=c.holdreason.hold_desc if c.holdreason and c.holdreason.hold_desc else None,
                    product_issues_no=product_issues_no)
                    hold.save()
                    # print(hold.pk,"hold")
                    if hold.pk:
                        con_obj.control_no = int(con_obj.control_no) + 1
                        con_obj.save()
                        dtl.holditemqty = int(c.holditemqty)
                        dtl.save()

            if '0' in str(c.quantity):
                no = str(c.quantity).split('0')
                if no[0] == '':
                    number = no[1]
                else:
                    number = c.quantity
            else:
                number = c.quantity

            dtl_st_ref_treatmentcode = "";dtl_first_trmt_done = False
            if c.itemcodeid.Item_Divid.itm_code == '3'  and c.itemcodeid.item_type != "PACKAGE":
                if c.is_foc == True:
                    course_val = c.itemcodeid.item_name +" "+"(FOC)"
                    isfoc_val = True
                else:
                    course_val = c.itemcodeid.item_name 
                    isfoc_val = False

                expiry = None
                if c.itemcodeid.service_expire_active == True:
                    month = c.itemcodeid.service_expire_month
                    current_date = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                    expiry = current_date + relativedelta(months=month)
  
                for i in range(1,int(number)+1):
                    treat = c
                    Price = c.trans_amt
                    Unit_Amount = Price / c.quantity
                    times = str(i).zfill(2)
                    treatment_no = str(c.quantity).zfill(2)

                    tmptrd_ids = Tmptreatment.objects.filter(itemcart=c,times=times).order_by('pk').first()
                    if tmptrd_ids:
                        treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
                        treatment_parentcode=treatment_parentcode,course=course_val,times=times,
                        treatment_no=treatment_no,price="{:.2f}".format(float(Price)),unit_amount="{:.2f}".format(float(Unit_Amount)),Cust_Codeid=treat.cust_noid,
                        cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
                        status="Open",item_code=str(treat.itemcodeid.item_code)+"0000",Item_Codeid=treat.itemcodeid,
                        sa_transacno=sa_transacno,sa_status="SA",type="N",trmt_is_auto_proportion=False,
                        dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,isfoc=isfoc_val,
                        treatment_account=treatacc,service_itembarcode=str(treat.itemcodeid.item_code)+"0000",
                        expiry=expiry,next_appt=tmptrd_ids.next_appt)
                    else:
                        treatmentid = Treatment(treatment_code=str(treatment_parentcode)+"-"+str(times),
                        treatment_parentcode=treatment_parentcode,course=course_val,times=times,
                        treatment_no=treatment_no,price="{:.2f}".format(float(Price)),unit_amount="{:.2f}".format(float(Unit_Amount)),Cust_Codeid=treat.cust_noid,
                        cust_code=treat.customercode,cust_name=treat.cust_noid.cust_name,
                        status="Open",item_code=str(treat.itemcodeid.item_code)+"0000",Item_Codeid=treat.itemcodeid,
                        sa_transacno=sa_transacno,sa_status="SA",type="N",trmt_is_auto_proportion=False,
                        dt_lineno=c.lineno,site_code=site.itemsite_code,Site_Codeid=site,isfoc=isfoc_val,
                        treatment_account=treatacc,service_itembarcode=str(treat.itemcodeid.item_code)+"0000",
                        expiry=expiry)
                
                    #and str(treatmentid.treatment_code) == str(treatment_parentcode)+"-"+"01"
                    if c.helper_ids.exists():
                        for h in c.helper_ids.all().filter(times=times):
                        
                            # dtl_st_ref_treatmentcode = treatment_parentcode+"-"+"01"
                                
                            treatmentid.status = "Done"
                            treatmentid.trmt_room_code = h.Room_Codeid.room_code if h.Room_Codeid else None
                            treatmentid.treatment_date = timezone.now()
                            treatmentid.save()

                            wp1 = h.workcommpoints / float(c.helper_ids.all().filter(times=times).count())
                            share_amt = float(treatmentid.unit_amount) / float(c.helper_ids.all().filter(times=times).count())

                            TmpItemHelper.objects.filter(id=h.id).update(item_code=treatment_parentcode+"-"+str(times),
                            item_name=c.itemcodeid.item_name,line_no=dtl.dt_lineno,sa_transacno=sa_transacno,
                            amount=treatmentid.unit_amount,sa_date=dtl.sa_date,site_code=site.itemsite_code,
                            wp1=wp1,wp2=0.0,wp3=0.0)

                            # Item helper create
                            helper = ItemHelper(item_code=treatment_parentcode+"-"+str(times),item_name=c.itemcodeid.item_desc,
                            line_no=dtl.dt_lineno,sa_transacno=sa_transacno,amount="{:.2f}".format(float(treatmentid.unit_amount)),
                            helper_name=h.helper_name if h.helper_name else None,helper_code=h.helper_code if h.helper_code else None,sa_date=dtl.sa_date,
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

                                treat_all = Treatment.objects.filter(sa_transacno=sa_transacno,treatment_parentcode=treatment_parentcode,site_code=site.itemsite_code)
                                length = [t.status for t in treat_all if t.status == 'Done']
                                if all([t.status for t in treat_all if t.status == 'Done']) == 'Done' and len(length) == treat_all.count():
                                    master_status = "Done"
                                else:
                                    master_status = "Open"

                                master = Treatment_Master(treatment_code=str(treatment_parentcode)+"-"+str(times),
                                treatment_parentcode=treatment_parentcode,sa_transacno=sa_transacno,
                                course=stock_obj.item_desc,times=times,treatment_no=treatment_no,
                                price=stock_obj.item_price,cust_code=cust_obj.cust_code,Cust_Codeid=cust_obj,
                                cust_name=cust_obj.cust_name,status=master_status,unit_amount=stock_obj.item_price,
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
                                appt_phone=cust_obj.cust_phone2[:20],appt_remark=stock_obj.item_desc,
                                emp_noid=h.helper_id if h.helper_id else None,emp_no=h.helper_id.emp_code if h.helper_id.emp_code else None,emp_name=h.helper_id.emp_name if h.helper_id.emp_name else None,
                                cust_name=cust_obj.cust_name,appt_code=appt_code,appt_status="Booking",
                                appt_to_time=h.appt_to_time if h.appt_to_time else None,Appt_Created_Byid=fmspw,
                                appt_created_by=fmspw.pw_userlogin,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
                                Room_Codeid=h.Room_Codeid if h.Room_Codeid else None,room_code=h.Room_Codeid.room_code if h.Room_Codeid else None,
                                Source_Codeid=h.Source_Codeid if h.Source_Codeid else None,source_code=h.Source_Codeid.source_code if h.Source_Codeid else None,
                                cust_refer=cust_obj.cust_refer,requesttherapist=False,new_remark=h.new_remark,
                                item_code=stock_obj.item_code,sa_transacno=sa_transacno,treatmentcode=str(treatment_parentcode)+"-"+str(times))
                                appt.save()

                                if appt.pk:
                                    master.Appointment = appt
                                    master.appt_time = timezone.now()
                                    master.save()
                                    ctrl_obj.control_no = int(ctrl_obj.control_no) + 1
                                    ctrl_obj.save()
                                
                        #treatment Account creation for done treatment 01
                        if c.helper_ids.all().filter(times=times).first():
                            stock_obj = c.itemcodeid
                            acc_ids = TreatmentAccount.objects.filter(ref_transacno=sa_transacno,
                            treatment_parentcode=treatment_parentcode,Site_Codeid=site).order_by('id').last()

                            td_desc = str(times)+"/"+str(c.quantity)+" "+str(stock_obj.item_name)
                            balance = acc_ids.balance - float(treatmentid.unit_amount) if acc_ids.balance else float(treatmentid.unit_amount)

                            treatacc_td = TreatmentAccount(Cust_Codeid=cust_obj,
                            cust_code=cust_obj.cust_code,ref_no=treatmentid.treatment_code,
                            description=td_desc,type='Sales',amount=-float("{:.2f}".format(float(treatmentid.unit_amount))) if treatmentid.unit_amount else 0.0,
                            balance="{:.2f}".format(float(balance)) if balance else 0.0,User_Nameid=fmspw,user_name=fmspw.pw_userlogin,
                            ref_transacno=treatmentid.sa_transacno,
                            sa_transacno=sa_transacno,qty=1,outstanding="{:.2f}".format(float(acc_ids.outstanding)),
                            deposit=None,treatment_parentcode=treatmentid.treatment_parentcode,treatment_code="",
                            sa_status="SA",cas_name=fmspw.pw_userlogin,
                            sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                            sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                            dt_lineno=c.lineno,Site_Codeid=site,site_code=site.itemsite_code,
                            treat_code=treatmentid.treatment_parentcode,itemcart=c)
                            treatacc_td.save()
                            # print(treatacc_td.id,"treatacc_td")
                            dtl_first_trmt_done = True
                            if dtl_st_ref_treatmentcode == "":
                                dtl_st_ref_treatmentcode = str(treatment_parentcode)+"-"+str(times)
                            elif not dtl_st_ref_treatmentcode == "":
                                dtl_st_ref_treatmentcode = str(dtl_st_ref_treatmentcode) +"-"+str(times)

                    
                    treatmentid.save()
                    # appt_time=treat.appt_time,Trmt_Room_Codeid=treat.Trmt_Room_Codeid,trmt_room_code=treat.trmt_room_code,
                    # print(treatmentid.id,"treatment_id")

                if treatacc and treatmentid:
                    controlobj.control_no = int(controlobj.control_no) + 1
                    controlobj.save()

                # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
                dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
                dtl.first_trmt_done = dtl_first_trmt_done
                dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
                dtl.first_trmt_done_staff_name = ','.join([v.helper_id.emp_name for v in c.helper_ids.all() if v.helper_id.emp_name])
                dtl.save()

            tmptrd_ids = Tmptreatment.objects.filter(itemcart=c).order_by('pk').delete()

        return id_lst
    # except Exception as e:
    #     invalid_message = str(e)
    #     return general_error_response(invalid_message)
    
def invoice_topup(self, request, topup_ids,sa_transacno, cust_obj, outstanding):
    # try:
    if self:
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        empl = fmspw.Emp_Codeid
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
        outstanding_new = 0.0
        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()

        for idx, c in enumerate(topup_ids, start=1):
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

            calcgst = 0
            if gst:
                calcgst = gst.item_value
            if calcgst > 0:
                sitegst = ItemSitelist.objects.filter(pk=site.pk).first()
                if sitegst:
                    if sitegst.site_is_gst == False:
                        calcgst = 0
            # print(calcgst,"0 calcgst")
            # Yoonus Tax Chcking
            gst_amt_collect = 0
            if calcgst > 0:
                if gst.is_exclusive == True:
                    gst_amt_collect = c.deposit * (calcgst / 100)
                    # tax_amt = deposit_amt * (gst.item_value / 100)
                    # billable_amount = "{:.2f}".format(deposit_amt + tax_amt)
                else:
                    gst_amt_collect = c.deposit * calcgst / (100+calcgst)
                    # billable_amount = "{:.2f}".format(deposit_amt)
                    # tax_amt = deposit_amt * gst.item_value / (100+gst.item_value)
                    # Yoonus
            # gst_amt_collect = c.deposit * (gst.item_value / 100)

            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.emp_name
                    elif not sales == "":
                        sales = sales +","+ i.emp_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.emp_name
                    elif not service == "":
                        service = service +","+ s.emp_name 
            
            

            if c.treatment_account is not None:
                topup_code = c.treatment_account.treatment_parentcode
                multi_itemcode = c.treatment_account.treatment_parentcode

                #acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment_account.ref_transacno,
                #treatment_parentcode=c.treatment_account.treatment_parentcode,Site_Codeid=site,
                #cust_code=cust_obj.cust_code).order_by('id').last()
                acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment_account.ref_transacno,
                treatment_parentcode=c.treatment_account.treatment_parentcode,
                cust_code=cust_obj.cust_code).order_by('id').last()

                outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)
                # print(outstanding_acc,"outstanding_acc")
                
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
                topup_service_trmt_code=topup_code,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                staffs = sales +" "+"/"+" "+ service)
                #appt_time=app_obj.appt_fr_time,
            
            elif c.deposit_account is not None:
                daud_ids = PosDaud.objects.filter(sa_transacno=c.deposit_account.ref_transacno,dt_itemnoid=c.itemcodeid,
                ItemSite_Codeid__pk=site.pk).order_by('pk').first()
                decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                if not decontrolobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                    raise serializers.ValidationError(result)

                treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                multi_itemcode = treat_code

                #acc_ids = DepositAccount.objects.filter(ref_transacno=c.deposit_account.sa_transacno,
                #ref_productcode=c.deposit_account.treat_code,Site_Codeid=site,type__in=('Deposit', 'Top Up'),
                #cust_code=cust_obj.cust_code).order_by('id').last()
                acc_ids = DepositAccount.objects.filter(ref_transacno=c.deposit_account.sa_transacno,
                ref_productcode=c.deposit_account.treat_code,type__in=('Deposit', 'Top Up'),
                cust_code=cust_obj.cust_code).order_by('id').last()
                
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
                topup_prepaid_trans_code="",dt_uom=daud_ids.dt_uom if daud_ids.dt_uom else '',
                item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                staffs = sales +" "+"/"+" "+ service)
                #appt_time=app_obj.appt_fr_time, 


            elif c.prepaid_account is not None:
                topup_code = c.prepaid_account.transac_no
                multi_itemcode = topup_code

                #acc_ids = PrepaidAccount.objects.filter(Site_Codeid=site,cust_code=cust_obj.cust_code,
                #pp_no=c.prepaid_account.pp_no,status=True,Item_Codeid=c.itemcodeid,
                #line_no=c.prepaid_account.line_no).order_by('id').first() #transac_no=
                #acc_ids = PrepaidAccount.objects.filter(cust_code=cust_obj.cust_code,
                #pp_no=c.prepaid_account.pp_no,status=True,
                #line_no=c.prepaid_account.line_no).order_by('id').first()
                #outstanding_acc =  float(acc_ids.outstanding) - float(c.deposit)
                outstanding_acc =  float(c.prepaid_account.outstanding) - float(c.deposit)

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
                topup_prepaid_pos_trans_lineno=c.lineno,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
                staffs = sales +" "+"/"+" "+ service)
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
                
                #treatment Account creation
                treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                description=desc,type="Top Up",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(tp_balance)),
                User_Nameid=fmspw,user_name=fmspw.pw_userlogin,ref_transacno=acc_ids.ref_transacno,sa_transacno=sa_transacno,
                qty=c.quantity,outstanding="{:.2f}".format(float(outstanding_acc)),deposit=None,
                treatment_parentcode=c.treatment_account.treatment_parentcode,treatment_code="",sa_status="SA",
                cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),dt_lineno=c.lineno,
                Site_Codeid=site,site_code=site.itemsite_code,treat_code=c.treatment_account.treatment_parentcode,itemcart=c,
                focreason=item_remarks,ref_no=sa_transacno)
                treatacc.save()
            # print(treatacc.id,"treatacc")
            elif c.deposit_account is not None:
                tp_balance = acc_ids.balance + c.deposit if acc_ids.balance else c.deposit
    
                #deposit Account creation
                depositacc = DepositAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
                description=desc,type="Top Up",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(tp_balance)),
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
                if c.itemcodeid.prepaid_valid_period != '':
                    prepaid_valid_period = timezone.now() + timedelta(int(c.itemcodeid.prepaid_valid_period))
                pp_bonus = c.itemcodeid.prepaid_value - c.itemcodeid.prepaid_sell_amt
                remain = c.prepaid_account.remain + c.deposit
                c.prepaid_account.status = False
                c.prepaid_account.save()
                outstanding = float(c.prepaid_account.outstanding) - float(c.deposit)

                # Yoonus
                if outstanding == 0:
                    remain = c.itemcodeid.prepaid_value - c.prepaid_account.use_amt

                #prepaidacc = PrepaidAccount(pp_no=c.prepaid_account.pp_no,pp_type=c.itemcodeid.item_range,
                #pp_desc=c.itemcodeid.item_name,exp_date=prepaid_valid_period,Cust_Codeid=cust_obj,
                #cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name,pp_amt=c.itemcodeid.prepaid_sell_amt,
                #pp_total=c.itemcodeid.prepaid_value, pp_bonus=pp_bonus,transac_no="",item_no="",
                #use_amt=0,remain=remain,ref1="",ref2="",status=True,site_code=site.itemsite_code,
                #sa_status="TOPUP",exp_status=True,voucher_no="",isvoucher=False,has_deposit=True,
                #topup_amt=c.deposit,outstanding=outstanding,active_deposit_bonus=False,topup_no=sa_transacno,
                #topup_date=timezone.now(),line_no=c.prepaid_account.line_no,
                #staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                #staff_name=','.join([v.display_name for v in salesstaff if v.display_name]), 
                #pp_type2=c.prepaid_account.pp_type2,condition_type1=c.prepaid_account.condition_type1,
                #pos_daud_lineno=c.prepaid_account.pos_daud_lineno,Site_Codeid=site,
                #Item_Codeid=c.itemcodeid,item_code=c.itemcodeid.item_code)
                #prepaidacc.save()
                prepaidacc = PrepaidAccount(pp_no=c.prepaid_account.pp_no,pp_type=c.prepaid_account.pp_type,
                pp_desc=c.prepaid_account.pp_desc,exp_date=c.prepaid_account.exp_date,Cust_Codeid=cust_obj,
                cust_code=cust_obj.cust_code,cust_name=cust_obj.cust_name,pp_amt=c.prepaid_account.pp_amt,
                pp_total=c.prepaid_account.pp_total,pp_bonus=c.prepaid_account.pp_bonus,transac_no="",item_no="",
                use_amt=0,remain=remain,ref1="",ref2="",status=True,site_code=site.itemsite_code,
                sa_status="TOPUP",exp_status=True,voucher_no="",isvoucher=False,has_deposit=True,
                topup_amt=c.deposit,outstanding=outstanding,active_deposit_bonus=False,topup_no=sa_transacno,
                topup_date=timezone.now(),line_no=c.prepaid_account.line_no,start_date=c.prepaid_account.start_date,
                staff_no=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                staff_name=','.join([v.display_name for v in salesstaff if v.display_name]), 
                pp_type2=c.prepaid_account.pp_type2,condition_type1=c.prepaid_account.condition_type1,
                lpackage=c.prepaid_account.lpackage,package_code=c.prepaid_account.package_code,
                pos_daud_lineno=c.prepaid_account.pos_daud_lineno,Site_Codeid=site,
                Item_Codeid=c.itemcodeid,item_code=c.itemcodeid.item_code)
                prepaidacc.save()

                acc = PrepaidAccountCondition.objects.filter(pp_no=c.prepaid_account.pp_no).update(remain=remain)

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
            #             balance = acc_ids.balance - treatmentid.unit_amount

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

        return id_lst
    # except Exception as e:
    #     invalid_message = str(e)
    #     return general_error_response(invalid_message)
    

def invoice_sales(self, request, sales_ids,sa_transacno, cust_obj, outstanding):
    # try:
    if self:
        outstanding = 0.00
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        empl = fmspw.Emp_Codeid
        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()
        id_lst = [] ; totQty = 0; discount_amt=0.0;additional_discountamt=0.0; total_disc = 0.0
        outstanding_new = 0.0
        
        for idx, c in enumerate(sales_ids, start=1):
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
            time = c.treatment.times 

            if c.is_foc == True:
                isfoc = True
                item_remarks = c.focreason.foc_reason_ldesc if c.focreason and c.focreason.foc_reason_ldesc else None 
                dt_itemdesc = str(time)+"/"+str(c.treatment.treatment_no)+" "+str(c.itemcodeid.item_name)+" "+"(FOC)" 

            else:
                isfoc = False  
                item_remarks = None 
                dt_itemdesc = str(time)+"/"+str(c.treatment.treatment_no)+" "+str(c.itemcodeid.item_name)
            
            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.emp_name
                    elif not sales == "":
                        sales = sales +","+ i.emp_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.emp_name
                    elif not service == "":
                        service = service +","+ s.emp_name 
            
            
            # dt_itemno=c.itemcodeid.item_code+"0000" if c.itemcodeid else None
            # ,topup_outstanding=
            dtl = PosDaud(sa_transacno=sa_transacno,dt_status="SA",dt_itemnoid=c.itemcodeid if c.itemcodeid else None,
            dt_itemno='',dt_itemdesc=dt_itemdesc if dt_itemdesc else None,dt_price=c.price if c.price else 0.0,
            dt_promoprice="{:.2f}".format(float(c.discount_price)) if c.discount_price else 0.0,dt_amt="{:.2f}".format(float(c.trans_amt)) if c.trans_amt else 0.0,dt_qty=c.quantity if c.quantity else 0.0,dt_discamt=0.0,
            dt_discpercent=0.0,dt_Staffnoid=service_staff if service_staff else None,dt_staffno=service_staff.emp_code if service_staff and service_staff.emp_code else None,
            dt_staffname=service_staff.emp_name if service_staff and service_staff.emp_name else None,dt_discuser=None,ItemSite_Codeid=site,
            itemsite_code=site.itemsite_code,dt_transacamt=0.0,dt_deposit=0.0,dt_lineno=c.lineno,
            itemcart=c,st_ref_treatmentcode=c.treatment.treatment_code if c.treatment.treatment_code else '',first_trmt_done=False,
            first_trmt_done_staff_code="",first_trmt_done_staff_name="",
            record_detail_type="TD",trmt_done_staff_code=','.join([v.emp_code for v in servicestaff if v.emp_code]),
            trmt_done_staff_name=','.join([v.emp_name for v in servicestaff if v.emp_name]),
            trmt_done_id=c.treatment.treatment_code if c.treatment.treatment_code else '',trmt_done_type="N",gst_amt_collect=0.0,
            dt_remark=c.remark if c.remark else '',isfoc=isfoc,item_remarks=item_remarks,
            item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
            staffs = "/"+" "+ service)
            #appt_time=app_obj.appt_fr_time,                

            dtl.save()
            # print(dtl.pk,"dtl")
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

            # .exclude(type='Sales')
            # acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            # treatment_parentcode=c.treatment.treatment_parentcode,Site_Codeid=site).order_by('id').last()
            acc_ids = TreatmentAccount.objects.filter(ref_transacno=c.treatment.sa_transacno,
            treatment_parentcode=c.treatment.treatment_parentcode).order_by('id').last()
            Balance = 0
            if acc_ids:
                # Balance = acc_ids.balance - c.treatment.unit_amount if acc_ids.balance else c.treatment.unit_amount
                Balance = acc_ids.balance - (c.treatment.unit_amount * c.quantity) if acc_ids.balance else c.treatment.unit_amount
                if acc_ids.outstanding:
                    outstanding += acc_ids.outstanding

            #treatment Account creation
            treatacc = TreatmentAccount(Cust_Codeid=cust_obj,cust_code=cust_obj.cust_code,
            description=dt_itemdesc,ref_no=c.treatment.treatment_code if c.treatment.treatment_code else '',type="Sales",
            amount=-float("{:.2f}".format(float(c.treatment.unit_amount * c.quantity ))) if c.treatment.unit_amount else 0.0,balance="{:.2f}".format(float(Balance)) if Balance else None,User_Nameid=fmspw,
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
            print(c.quantity-1,"cqty")
            for iqty in range(0, c.quantity):
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

                        # treat_all = Treatment.objects.filter(sa_transacno=c.treatment.sa_transacno,
                        # treatment_parentcode=c.treatment.treatment_parentcode,site_code=site.itemsite_code)
                        treat_all = Treatment.objects.filter(sa_transacno=c.treatment.sa_transacno,
                        treatment_parentcode=c.treatment.treatment_parentcode)
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
                        if not channel:
                            result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Channel ID does not exist!!",'error': True} 
                            raise serializers.ValidationError(result)
                       
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
                        # print(appt,"appt")

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

            if c.exchange_id:
                c.exchange_id.status = True
                c.exchange_id.fe_transacno = sa_transacno
                c.exchange_id.save()
                ExchangeDtl.objects.filter(status=False).delete()

            # print(dtl_st_ref_treatmentcode,"dtl_st_ref_treatmentcode") 
            # dtl.st_ref_treatmentcode = dtl_st_ref_treatmentcode
            # dtl.first_trmt_done = dtl_first_trmt_done
            # dtl.first_trmt_done_staff_code = ','.join([v.helper_id.emp_code for v in c.helper_ids.all() if v.helper_id.emp_code])
            # dtl.first_trmt_done_staff_name = ','.join([v.helper_id.emp_name for v in c.helper_ids.all() if v.helper_id.emp_name])
            # dtl.save()

        return id_lst    
    # except Exception as e:
    #     invalid_message = str(e)
    #     return general_error_response(invalid_message)
    

        
def invoice_exchange(self, request, exchange_ids, sa_transacno, cust_obj, outstanding):
    if self:
        fmspw = Fmspw.objects.filter(user=request.user,pw_isactive=True).first()
        site = fmspw.loginsite
        id_lst = [] 
        gst = GstSetting.objects.filter(item_code="100001",item_desc='GST',isactive=True).first()

        for idx, c in enumerate(exchange_ids, start=1):
            
            sales_staff = c.sales_staff.all().first()
            salesstaff = c.sales_staff.all()

         
            gst_amt_collect = c.deposit * (gst.item_value / 100)
            
            sales = "";service = ""
            if c.sales_staff.all():
                for i in c.sales_staff.all():
                    if sales == "":
                        sales = sales + i.display_name
                    elif not sales == "":
                        sales = sales +","+ i.display_name
            if c.service_staff.all(): 
                for s in c.service_staff.all():
                    if service == "":
                        service = service + s.display_name
                    elif not service == "":
                        service = service +","+ s.display_name 


            dtl = PosDaud(sa_transacno=sa_transacno,dt_status="EX",dt_itemnoid=c.itemcodeid,
            dt_itemno=str(c.itemcodeid.item_code)+"0000",dt_itemdesc=c.itemcodeid.item_name,dt_price=c.price,
            dt_promoprice="{:.2f}".format(float(c.discount_price)),
            dt_amt=-float("{:.2f}".format(float(c.trans_amt))),dt_qty=c.quantity,
            dt_discamt=0,dt_discpercent=0,dt_Staffnoid=sales_staff,dt_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
            dt_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
            dt_discuser=None,dt_combocode=c.itemcodeid.item_code,ItemSite_Codeid=site,itemsite_code=site.itemsite_code,
            dt_transacamt="{:.2f}".format(float(c.trans_amt)),dt_deposit="{:.2f}".format(float(c.deposit)),dt_lineno=c.lineno,itemcart=c,
            st_ref_treatmentcode=None,record_detail_type="PRODUCT",gst_amt_collect="{:.2f}".format(float(gst_amt_collect)),
            topup_outstanding=0,dt_remark=sa_transacno,isfoc=0,item_remarks="",
            dt_uom=c.item_uom.uom_code if c.item_uom else None,first_trmt_done=False,item_status_code=c.itemstatus.status_code if c.itemstatus and c.itemstatus.status_code else None,
            staffs=sales +" "+"/"+" "+ service)

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
                multi = Multistaff(sa_transacno=sa_transacno,item_code=str(c.itemcodeid.item_code)+"0000",
                emp_code=sale.emp_code,ratio=ratio,salesamt="{:.2f}".format(float(c.deposit)),type=None,isdelete=False,role=1,
                dt_lineno=c.lineno)
                multi.save()
                # print(multi.id,"multi")

            if int(c.itemcodeid.Item_Divid.itm_code) == 1 and c.itemcodeid.Item_Divid.itm_desc == 'RETAIL PRODUCT' and c.itemcodeid.Item_Divid.itm_isactive == True:
                desc = "Total Product Amount : "+str("{:.2f}".format(float(c.trans_amt)))
                #Deposit Account creation
                
                decontrolobj = ControlNo.objects.filter(control_description__iexact="Product Deposit",Site_Codeid__pk=fmspw.loginsite.pk).first()
                if not decontrolobj:
                    result = {'status': status.HTTP_400_BAD_REQUEST,"message":"Product Deposit Control No does not exist!!",'error': True} 
                    return Response(result, status=status.HTTP_400_BAD_REQUEST) 

                treat_code = str(decontrolobj.Site_Codeid.itemsite_code)+str(decontrolobj.control_no)
                
                if c.is_foc == True:
                    item_descriptionval = c.itemcodeid.item_name+" "+"(FOC)"
                else:
                    item_descriptionval = c.itemcodeid.item_name
                

                depoacc = DepositAccount(cust_code=cust_obj.cust_code,type="Exchange",amount="{:.2f}".format(float(c.deposit)),
                balance="{:.2f}".format(float(c.deposit)),user_name=fmspw.pw_userlogin,qty=c.quantity,outstanding=0,
                deposit="{:.2f}".format(float(c.deposit)),cas_name=fmspw.pw_userlogin,sa_staffno=','.join([v.emp_code for v in salesstaff if v.emp_code]),
                sa_staffname=','.join([v.emp_name for v in salesstaff if v.emp_name]),
                deposit_type="PRODUCT",sa_transacno=sa_transacno,description=desc,ref_code="",
                sa_status="EX",item_barcode=str(c.itemcodeid.item_code)+"0000",item_description=item_descriptionval,
                treat_code=treat_code,void_link=None,lpackage=None,package_code=None,
                dt_lineno=c.lineno,Cust_Codeid=cust_obj,Site_Codeid=site,site_code=site.itemsite_code,
                ref_transacno=sa_transacno,ref_productcode=treat_code,Item_Codeid=c.itemcodeid,
                item_code=c.itemcodeid.item_code)
                depoacc.save()
                # print(depoacc.pk,"depoacc")
                if depoacc.pk:
                    decontrolobj.control_no = int(decontrolobj.control_no) + 1
                    decontrolobj.save()

                #ItemBatch
                batch_ids = ItemBatch.objects.filter(site_code=site.itemsite_code,
                item_code=c.itemcodeid.item_code,uom=c.item_uom.uom_code).order_by('pk').last()
                
                if batch_ids:
                    addamt = batch_ids.qty + abs(c.quantity)
                    batch_ids.qty = addamt
                    batch_ids.updated_at = timezone.now()
                    batch_ids.save() 
                else:
                    batch_id = ItemBatch(item_code=c.itemcodeid.item_code,site_code=site.itemsite_code,
                    batch_no="",uom=c.item_uom.uom_code,qty=abs(c.quantity),exp_date=None,batch_cost=c.itemcodeid.lstpo_ucst).save()
                    addamt = abs(c.quantity)                      

                #Stktrn
                stktrn_ids = Stktrn.objects.filter(store_no=site.itemsite_code,
                itemcode=c.itemcodeid.item_code+"0000",item_uom=c.item_uom.uom_code).last() 
                # print(stktrn_ids,"stktrn_ids")

                currenttime = timezone.now()

                post_time = str(currenttime.hour)+str(currenttime.minute)+str(currenttime.second)
                itemuom_ids = ItemUomprice.objects.filter(item_code=c.itemcodeid.item_code,item_uom=c.item_uom.uom_code).order_by('pk').first()

                if stktrn_ids:
                    amt_add = stktrn_ids.trn_balqty + abs(c.quantity)

                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                    trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=abs(c.quantity),trn_balqty=amt_add,trn_balcst=0,
                    trn_amt="{:.2f}".format(float(abs(c.deposit))),
                    trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                    hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None).save()
                else:
                    stktrn_id = Stktrn(trn_no=None,post_time=post_time,aperiod=None,
                    itemcode=str(c.itemcodeid.item_code)+"0000",store_no=site.itemsite_code,
                    tstore_no=None,fstore_no=None,trn_docno=sa_transacno,
                    trn_type="EX",trn_db_qty=None,trn_cr_qty=None,
                    trn_qty=abs(c.quantity),trn_balqty=addamt,trn_balcst=0,
                    trn_amt="{:.2f}".format(float(abs(c.deposit))),
                    trn_cost=itemuom_ids.item_cost if itemuom_ids and itemuom_ids.item_cost else None,trn_ref=None,
                    hq_update=0,line_no=c.lineno,item_uom=c.item_uom.uom_code,
                    item_batch=None,mov_type=None,item_batch_cost=None,
                    stock_in=None,trans_package_line_no=None).save()

                
        return id_lst
