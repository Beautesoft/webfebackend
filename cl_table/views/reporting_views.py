import datetime
import json
import os
from copy import copy

from dateutil import relativedelta
from django.db import connection
from django.db.models import Sum, Case, When, F, Value, Subquery, OuterRef, Q, Count
from django.db.models.expressions import Col
from django.db.models.sql.constants import LOUTER
from django.db.models.sql.datastructures import Join
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from Cl_beautesoft.settings import BASE_DIR, REPORT_SETTINGS_PATH
from cl_app.models import ItemSitelist
from cl_table.models import ItemSitelist_Reporting, PosHaud_Reporting, PosTaud_Reporting, PosDaud_Reporting, \
    Multistaff_Reporting, Treatment_Reporting, Stock_Reporting, Customer_Reporting, PayGroup_Reporting
from cl_table.serializers import DepartmentReport
from cl_table.utils import model_joiner, SUBSTR, LENGTH


class SalesDailyReporting(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        """
            query parm: start: datetime string(2021-01-01T00:00:00)
                        in: day, week, month
        """

        # try:
        #     start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
        #     end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
        #     date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        # except:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,
        #               'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
        #               'error': True,
        #               "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        _in = request.GET.get('in', '')
        if _in.lower() == 'day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower() == 'week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower() == 'month':
            _delta = relativedelta.relativedelta(months=1)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "in query parameters are mandatory. (day,week,month)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        start = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
        _pre_start = start - _delta
        end = start + _delta
        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        elif _siteGroup or _siteCodes:
            if _siteCodes:
                site_code_list = _siteCodes.split(",")
            elif _siteGroup:
                site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True, site_group=_siteGroup). \
                    exclude(itemsite_code__icontains="HQ"). \
                    values_list('itemsite_code', flat=True)
            _s = ', '.join(['\'' + str(code) + '\'' for code in site_code_list])
            site_code_q = f"AND pos_haud.ItemSite_Code IN ({_s})"
        else:
            site_code_q = ""

        pay_group_q = ""

        # _type = request.GET.get('type','').lower()
        # if _type == "sales":
        #     amount = Sum("sales_gt1_gst")
        # elif _type == "service":
        #     amount = Sum("servicesales_gt1")
        # elif _type == "product":
        #     amount = Sum("productsales_gt1")
        # elif _type == "prepaid":
        #     amount = Sum("prepaidsales_gt1")
        # else:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,
        #               'message': "type query parameters are mandatory. (sales,service,product,prepaid)",
        #               'error': True,
        #               "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        raw_q = """
                    SELECT
                        (select distinct Itemsite_Desc from item_sitelist where itemSite_Code=pos_haud.ItemSite_Code) [Outlet],
                        pos_haud.ItemSite_Code [site1],
                        paytable.gt_group [PayGroup],
                        pos_taud.pay_Desc [payTypes],
                        Convert(nvarchar,pos_haud.sa_date,103) [payDate],
                        pos_haud.SA_TransacNo_Ref [InvoiceRef],
                        pos_haud.sa_custno [customerCode],
                        pos_haud.sa_custname [customer],
                        isnull(pos_daud.dt_itemdesc,'') [ItemName],
            
                        case when (select isactive from GST_Setting)=1
                            then
                                sum(round(
                                        pos_taud.pay_actamt
                                          -( Case When pos_taud.pay_type='CN'
                                                Then (pos_taud.pay_actamt)
                                                Else 0 End
                                            )
                                          - ( CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0
                                                Then 0
                                              Else pos_taud.PAY_GST End
                                            )
                                          - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0
                                                                                                Then 0
                                                                                                Else pos_taud.PAY_GST End
                                                                        )
                                              )/100  +0 ,
                                        3)
                                    )
                            else
                                sum( pos_taud.pay_actamt
                                        -( Case When pos_taud.pay_type='CN'
                                                Then (pos_taud.pay_actamt)
                                                Else 0
                                            End
                                        )
                                    )
                        end [beforeGST],
            
                        sum(Convert(Decimal(19,3),
                                    Case When pos_taud.pay_type='CN'
                                        Then pos_taud.PAY_GST
                                        else ( CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0
                                                    Then 0
                                                    Else pos_taud.PAY_GST
                                                End
                                            )
                                    end
                                    )) [GST],
            
                        sum(pos_taud.pay_actamt-( Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End ))   [afterGST]
            
                    FROM pos_haud
                    INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno
                    INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code
                    INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE
                    Left JOIN pos_daud ON pos_daud.sa_transacno=pos_taud.sa_transacno And pos_taud.dt_lineno=pos_daud.dt_LineNo
                    Where convert(datetime,convert(varchar,pos_haud.sa_date,103),103) BETWEEN '{0}' AND '{1}' 
                      and paytable.pay_code in (select pay_code from paytable)
                      and pos_haud.isVoid!=1 and pos_haud.sa_depositAmt > 0 {2} {3} -- 2 site 3 paygroup
                    group by pos_haud.sa_date,pos_taud.pay_Desc,pos_haud.ItemSite_Code,paytable.gt_group,pos_haud.SA_TransacNo_Ref,pos_haud.sa_custno,
                             pos_haud.sa_custname,pos_daud.dt_itemdesc
                    order by pos_haud.ItemSite_Code,pos_haud.sa_date,pos_taud.pay_Desc
                    """

        raw_q = raw_q.format(start, end, site_code_q, pay_group_q)
        print(raw_q)
        # # #previous qs
        # _prev_dict = {}
        # with connection.cursor() as cursor:
        #     cursor.execute(raw_q.format(site_code_q,_pre_start,start))
        #     raw_qs = cursor.fetchall()
        #     desc = cursor.description
        #     for i, row in enumerate(raw_qs):
        #         _d = dict(zip([col[0] for col in desc], row))
        #         _prev_dict[_d['empCode']] = [i+1,_d['amount']]

        query_dict = {}
        with connection.cursor() as cursor:
            cursor.execute(raw_q)
            raw_qs = cursor.fetchall()
            desc = cursor.description
            # responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]
            # for row in raw_qs:
            # data_list = []
            # site_total_dict = {}
            for i, row in enumerate(raw_qs):
                _d = dict(zip([col[0] for col in desc], row))
                outlet_dict = query_dict.get(_d['Outlet'], {})
                pay_dict = outlet_dict.get(_d['payTypes'], {"payType": _d['payTypes']})
                trans_list = pay_dict.get('transactions', [])
                trans_list.append(_d)

                pay_sum_bGST = pay_dict.get('amount_before_gst', 0)
                pay_sum_bGST += _d['beforeGST']
                pay_dict['amount_before_gst'] = round(pay_sum_bGST, 2)

                pay_sum_GST = pay_dict.get('amount_gst', 0)
                pay_sum_GST += _d['GST']
                pay_dict['amount_gst'] = round(pay_sum_GST, 2)

                pay_sum_aGST = pay_dict.get('amount_after_gst', 0)
                pay_sum_aGST += _d['afterGST']
                pay_dict['amount_after_gst'] = round(pay_sum_aGST, 2)

                pay_dict['transactions'] = trans_list
                outlet_dict[_d['payTypes']] = pay_dict
                query_dict[_d['Outlet']] = outlet_dict

            responseData = []

            for k, v in query_dict.items():
                _pay_list = []
                _site_aGST, _site_GST, _site_bGST = 0, 0, 0
                for k1, v1 in v.items():
                    _pay_list.append(v1)
                    _site_aGST += v1['amount_after_gst']
                    _site_GST += v1['amount_gst']
                    _site_bGST += v1['amount_before_gst']
                _row_dict = {
                    "outlet": k,
                    "pay_types": _pay_list,
                    "amount_before_gst": round(_site_bGST, 2),
                    "amount_gst": round(_site_GST, 2),
                    "amount_after_gst": round(_site_aGST, 2),
                }
                responseData.append(_row_dict)

            # responseData = {"data": data_list}
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)


class CollectionByOutletView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        # sales_setting = request.GET.get("setting","GT1")
        # if not sales_setting in ["GT1","GT2","BOTH"]:
        #     result = {'status': status.HTTP_400_BAD_REQUEST, 'message': "settings query parameter must be GT1 or GT2 or BOTH ", 'error': True, "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
            date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        site_list_qs = ItemSitelist_Reporting.objects.filter(itemsite_isactive=True)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        elif _siteCodes:
            site_list_qs = site_list_qs.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_list_qs = site_list_qs.filter(site_group=_siteGroup)

        site_list = []

        for site in site_list_qs:
            data_dict = {"siteCode":site.itemsite_code, "outlet":site.itemsite_desc, "dateList": []}
            for date in date_range:
                trans_qs = site.pos_haud_related.filter(sa_date=date)
            print(trans_qs)
        responseData = {}
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)

class DailyCollectionReportAPI(APIView):
    def get(self, request):
        """
            query parm: start: datetime string(2021-01-01T00:00:00)
                        in: day, week, month
        """

        # try:
        #     start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
        #     end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
        #     date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        # except:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,
        #               'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
        #               'error': True,
        #               "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        _in = request.GET.get('in', '')
        if _in.lower() == 'day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower() == 'week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower() == 'month':
            _delta = relativedelta.relativedelta(months=1)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "in query parameters are mandatory. (day,week,month)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        start = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
        _pre_start = start - _delta
        end = start + _delta
        # filters
        # site
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist_Reporting.objects.filter(itemsite_isactive=True) #. \
                # exclude(itemsite_code__icontains="HQ"). \
                # values('itemsite_code', 'itemsite_desc')

        if _siteCodes:
            site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)
        # pay group
        _payGroups = request.GET.get("payGroups","").split(",")




        responseData = []

        # for site in site_code_list:
        #     trans_qs = site.pos_haud_related.all()
        #     # print(list(trans_qs))
        #     _data_dict = {}
        #     for trans in trans_qs:
        #         _pay_dict = _data_dict.get(trans.)
        # q = PosHaud_Reporting.objects.prefetch_related('pos_taud_related')
        site_dict = {}
        # x = PosTaud_Reporting.objects.filter(sa_transacno__sa_date__range=[start, end]).query.join()
        payment_qs = PosTaud_Reporting.objects.filter(sa_transacno__sa_date__range=[start, end],sa_transacno__itemsite_code__in=site_code_list).\
            extra(tables=['pos_daud'],
                  where=['pos_daud.sa_transacno=pos_taud.sa_transacno','pos_taud.dt_lineno=pos_daud.dt_LineNo'],
                  select={"itemName":'pos_daud.dt_itemdesc'}).\
            values('sa_transacno','sa_transacno__itemsite_code','sa_transacno__sa_date',
                   'sa_transacno__sa_transacno_ref','sa_transacno__sa_custno','sa_transacno__sa_custname',
                   'sa_transacno__itemsite_code__itemsite_desc','pay_type',
                   'pay_type__bank_charges','pay_group','dt_lineno','itemName').\
            annotate(
                beforeGST=Sum(
                            Case(When(pay_type='CN',then=Value(0)),default=F('pay_actamt')) *
                            Case(When(pay_type__bank_charges__isnull=False,then=Value(1)-F('pay_type__bank_charges')/Value(100)),default=1)
                            ),
                GST=Sum(
                        # Case(When(pay_type='CN',then=F('pay_gst')),When(pay_actamt=F('pay_gst'),then=0),default=F('pay_gst'))
                        Case(When(pay_gst__isnull=False,then=F('pay_gst')),default=0)
                        ),
                afterGST=Sum(
                            Case(When(pay_type='CN',then=Value(0)),default=F('pay_actamt')),
                             ),
                    )
        print(payment_qs.query.__str__())
        for payment in payment_qs:
            transsacNo = payment['sa_transacno']
            # _item_obj = PosDaud_Reporting.objects.filter(dt_lineno=payment['dt_lineno'],sa_transacno=transsacNo).values('dt_itemdesc').first()
            _site = site_dict.get(payment['sa_transacno__itemsite_code'],{})
            _pay = _site.get(payment['pay_type'],[])
            _pay.append({
                "Outlet": payment['sa_transacno__itemsite_code__itemsite_desc'],
                "site1": payment['sa_transacno__itemsite_code'],
                "PayGroup": payment['pay_group'],
                "payTypes": payment['pay_type'],
                "payDate": payment['sa_transacno__sa_date'],
                "InvoiceRef": payment['sa_transacno__sa_transacno_ref'],
                "customerCode": payment['sa_transacno__sa_custno'],
                "customer":  payment['sa_transacno__sa_custname'],
                # "ItemName": _item_obj['dt_itemdesc'] if _item_obj else "",
                "ItemName": payment['itemName'],
                "beforeGST": payment['beforeGST'],
                "GST": payment['GST'],
                "afterGST": payment['afterGST']
            })
            _site[payment['pay_type']] = _pay
            site_dict[payment['sa_transacno__itemsite_code']] = _site

        print(site_dict)

        responseData = site_dict
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class StaffPerformanceAPI(APIView):
    def get(self,request):
        """
        Staff perfomance api will return individual employee performance for a day
            | Payment Date | Invoice ref. | Customer | Customer ref. | Item Name | Payment Amount |
        :param request:
        :return:
        """
        _in = request.GET.get('in', '')
        if _in.lower() == 'day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower() == 'week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower() == 'month':
            _delta = relativedelta.relativedelta(months=1)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "in query parameters are mandatory. (day,week,month)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        start = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
        _pre_start = start - _delta
        end = start + _delta
        # filters
        # site
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist_Reporting.objects.filter(itemsite_isactive=True)  # . \
            # exclude(itemsite_code__icontains="HQ"). \
            # values('itemsite_code', 'itemsite_desc')

        item_filter_dict = {
            "sa_transacno__sa_date__range":[start, end],
                            }
        if _siteCodes:
            item_filter_dict["sa_transacno__itemsite_code__in"] = _siteCodes.split(",")
            # site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            item_filter_dict["sa_transacno__itemsite_code__site_group"] = _siteGroup
            # site_code_list = site_code_list.filter(site_group=_siteGroup)

        items_qs = PosDaud_Reporting.objects.filter(**item_filter_dict)\
            .values('sa_transacno__sa_date','sa_transacno__itemsite_code','sa_transacno__itemsite_code__itemsite_desc',
                'sa_transacno__sa_transacno_ref','sa_transacno__sa_custno__cust_name','sa_transacno__sa_custno__cust_refer',
                'dt_itemdesc'
                )
        items_qs = model_joiner(items_qs,
                                Multistaff_Reporting,
                                (('sa_transacno', 'sa_transacno'), ('dt_lineno', 'dt_lineno'),),select=['ratio','emp_code'])\
            .filter(Multistaff_Reporting__ratio__isnull=False,sa_transacno__sa_custno__isnull=False)

        _staffCode = request.GET.get("staffCode")

        if _staffCode:
            items_qs.filter(Multistaff_Reporting__emp_code=_staffCode)

        items_qs = items_qs.annotate(
                                        date=F('sa_transacno__sa_date'),
                                        outlet=F('sa_transacno__itemsite_code__itemsite_desc'),
                                        invoiceRef=F('sa_transacno__sa_transacno_ref'),
                                        customerName=F('sa_transacno__sa_custno__cust_name'),
                                        customerRef=F('sa_transacno__sa_custno__cust_refer'),
                                        item=F('dt_itemdesc'),
                                        total = Sum(F('dt_deposit') /
                                                        (100 * F('Multistaff_Reporting__ratio'))
                                                  )
                                    ).values('date','outlet','invoiceRef','customerName','customerRef','item','total')

        print(items_qs.query.__str__())

        responseData = items_qs
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class SalesByDepartment(APIView):
    def get(self,request):
        """
        filter: Dept, Site, Show old bill, show non sales
                Staff perfomance api will return individual employee performance for a day
                    |  Date | Dept | Invoice No. | Item Desc | Discount | Qty | Amount |
                :param request:
                :return:
                """
        _in = request.GET.get('in', '')
        if _in.lower() == 'day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower() == 'week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower() == 'month':
            _delta = relativedelta.relativedelta(months=1)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "in query parameters are mandatory. (day,week,month)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        start = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
        _pre_start = start - _delta
        end = start + _delta
        # filters
        # site
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist_Reporting.objects.filter(itemsite_isactive=True)  # . \
            # exclude(itemsite_code__icontains="HQ"). \
            # values('itemsite_code', 'itemsite_desc')

        if _siteCodes:
            site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        payment_qs = PosTaud_Reporting.objects.filter(sa_transacno__sa_date__range=[start,end])\
            .values('sa_transacno','pay_type__gt_group')\
            .annotate(amount=Sum('pay_actamt')).values_list('sa_transacno','pay_type__gt_group','amount')

        pay_dict = {}
        _temp = {'GT1':0,'GT2':0}
        for pay in payment_qs:
            _dict= pay_dict.get(pay[0],_temp)
            _dict[pay[1]]=pay[2]
            pay_dict[pay[0]] = _dict

        print("payament:",pay_dict)


        qs = PosHaud_Reporting.objects.filter(sa_date__range=[start,end])
        qs = model_joiner(qs,PosDaud_Reporting,(('sa_transacno','sa_transacno'),),
                          select=['dt_lineno','record_detail_type','topup_service_trmt_code','dt_itemno',
                                  'record_detail_type','dt_deposit','dt_discamt','dt_qty'])
        # qs = qs.values('sa_date','itemsite_code','sa_transacno_ref',)
        treatment_sub_qs = Treatment_Reporting.objects.filter(
            treatment_parentcode=OuterRef('PosDaud_Reporting__topup_service_trmt_code'))\
                                                    .values('service_itembarcode').distinct()[:1]
        qs = qs.annotate(item_code=Case(When(PosDaud_Reporting__record_detail_type='TP SERVICE',
                                            then=Subquery(treatment_sub_qs),
                                            ),
                                       default=F('PosDaud_Reporting__dt_itemno')
                                       ),
                         itemDesc=Subquery(Stock_Reporting.objects.annotate(treat_item_code=F('item_code')+'0000')
                                           .filter(treat_item_code=OuterRef('item_code'))
                                           .values('item_name').distinct()[:1]),
                         record_detail_type = F('PosDaud_Reporting__record_detail_type'),
                         Qty=Case(When(Q(PosDaud_Reporting__record_detail_type='TP SERVICE') | Q(PosDaud_Reporting__record_detail_type='TP PRODUCT'),
                                       then=Value(0)
                                       ),
                                  default=F('PosDaud_Reporting__dt_qty')
                                  ),
                         deposit = F('PosDaud_Reporting__dt_deposit'),
                         discount= F('PosDaud_Reporting__dt_discamt'),
                         # GT1_actamt=Subquery(PosTaud_Reporting.objects.filter(
                         #                        sa_transacno=OuterRef('sa_transacno'), pay_type__gt_group='GT1'
                         #                        ).values('sa_transacno').annotate(val=Sum('pay_actamt')).values('val')[:1]
                         #                    ),
                         # GT2_actamt=Subquery(PosTaud_Reporting.objects.filter(
                         #                        sa_transacno=OuterRef('sa_transacno'), pay_type__gt_group='GT2'
                         #                        ).values('sa_transacno').annotate(val=Sum('pay_actamt')).values('val')[:1]
                         #                    ),
                         # Ttl_actamt=Subquery(PosTaud_Reporting.objects.filter(
                         #                         sa_transacno=OuterRef('sa_transacno')
                         #                         ).values('sa_transacno').annotate(val=Sum('pay_actamt')).values('val')[:1]
                         #                    ),
                         # Pay_OldBill=Subquery(PosTaud_Reporting.objects.filter(
                         #                         sa_transacno=OuterRef('sa_transacno'), pay_type='OB'
                         #                         ).values('sa_transacno').annotate(val=Count('pay_actamt')).values('val')[:1]
                         #                    ),

                         )

        qs = qs.values('sa_date','itemsite_code','sa_transacno','sa_transacno_ref','deposit','discount',
                       'item_code','itemDesc','Qty','record_detail_type', #'Pay_OldBill', #'GT1_actamt','GT2_actamt','Ttl_actamt'
                       )

        _oldBil = request.GET.get("oldBil","NO")
        if _oldBil.upper() == "YES":
            qs = qs.filter(Q(Pay_OldBill=0)|Q(Pay_OldBill__isnull=True))
        elif _oldBil.upper() != "NO":
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "oldBil query parameter valid inputs is YES or NO ", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        print(qs.query)

        _showNoneSale = request.GET.get("showNoneSale","NO")
        if _showNoneSale.upper()=="YES":
            _showNoneSale = True
        elif _showNoneSale.upper() == "NO":
            _showNoneSale = False
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "showNoneSale query parameter valid inputs is YES or NO ", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


        responseData = []
        for res in qs:
            gt1 = round(pay_dict.get('sa_transacno',_temp)['GT1'],2)
            gt2 = round(pay_dict.get('sa_transacno',_temp)['GT2'],2)
            tot = gt1 + gt2
            try:
                GT1_proportion_amt = gt1/tot*res['deposit']
            except:
                GT1_proportion_amt = 0

            try:
                GT2_proportion_amt = gt2/tot*res['deposit']
            except:
                GT2_proportion_amt = 0

            res["Amount"] = GT1_proportion_amt + GT2_proportion_amt if _showNoneSale else GT1_proportion_amt
            res["GT1_proportion_amt"] = GT1_proportion_amt
            res["GT2_proportion_amt"] = GT2_proportion_amt

            responseData.append(res)
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class DailyInvoiceReport(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        """
            query parm: start: datetime string(2021-01-01T00:00:00)
                        in: day, week, month
        """

        # try:
        #     start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
        #     end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
        #     date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        # except:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,
        #               'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
        #               'error': True,
        #               "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        _in = request.GET.get('in', '')
        if _in.lower() == 'day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower() == 'week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower() == 'month':
            _delta = relativedelta.relativedelta(months=1)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "in query parameters are mandatory. (day,week,month)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        start = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
        _pre_start = start - _delta
        end = start + _delta
        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        elif _siteGroup or _siteCodes:
            if _siteCodes:
                site_code_list = _siteCodes.split(",")
            elif _siteGroup:
                site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True, site_group=_siteGroup). \
                    exclude(itemsite_code__icontains="HQ"). \
                    values_list('itemsite_code', flat=True)
            _s = ', '.join(['\'' + str(code) + '\'' for code in site_code_list])
            site_code_q = f"AND pos_haud.ItemSite_Code IN ({_s})"
            site_code_q_2 = f"where item_sitelist.ItemSite_Code In ({_s})"
        else:
            site_code_q = ""
            site_code_q_2 = ""

        pay_group_q = ""

        # _type = request.GET.get('type','').lower()
        # if _type == "sales":
        #     amount = Sum("sales_gt1_gst")
        # elif _type == "service":
        #     amount = Sum("servicesales_gt1")
        # elif _type == "product":
        #     amount = Sum("productsales_gt1")
        # elif _type == "prepaid":
        #     amount = Sum("prepaidsales_gt1")
        # else:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,
        #               'message': "type query parameters are mandatory. (sales,service,product,prepaid)",
        #               'error': True,
        #               "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        raw_q = """
        Select X.payDate,X.customer,X.invoiceRef,[payRef],[CustRef],            
        X.payTypes [payTypes],      
        (case when X.[isVoid]=1 then 'Voided Sales'  when X.[Group]='GT1' and X.[isVoid]=0 and isnull(SUM(X.total),0)<>0 then 'Sales' 
        when ((X.[Group]='GT2' and X.[isVoid]=0) or (isnull(SUM(X.total),0)=0)) then 'Non-Sales' else '' end) as SalesGroup,      
        X.ItemSite_Code [siteCode],      
        X.ItemSite_Desc [siteName],      
        isnull(SUM(X.amt),0) [amt],      
        isnull(SUM(X.payCN),0) [payCN],      
        isnull(SUM(X.payContra),0) [payContra],      
        isnull(SUM(X.grossAmt),0) [grossAmt],   
        isnull(SUM(X.taxes),0) [taxes],  
        isnull(SUM(X.gstRate),0) [gstRate],            
        isnull(SUM(X.grossAmt),0)-isnull(SUM(X.taxes),0) [netAmt],      
        isnull(SUM(X.BankCharges),0) [BankCharges],      
        isnull(SUM(X.comm),0) [comm],      
        isnull(SUM(X.grossAmt),0)-isnull(SUM(X.taxes),0)-isnull(SUM(X.BankCharges),0) total        
        from (      
        SELECT              
        convert (varchar,pos_haud.sa_date,103)[payDate],       
        Customer.Cust_name [customer],        
        pos_haud.SA_TransacNo_Ref [invoiceRef],       
        pos_haud.isVoid,      
        pos_haud.sa_remark,      
        --pos_haud.sa_transacno [payRef],      
        pos_haud.sa_staffname [payRef],      
        Customer.Cust_Refer [CustRef],      
        pos_taud.pay_Desc [payTypes],       
        pos_taud.pay_actamt  [amt] ,       
        0 [payContra],      
        paytable.GT_Group [Group],      
        Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End  [payCN],      
        pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )   [grossAmt],      
           
         case when ((Select top 1 site_is_gst from item_sitelist {0})=1) then  
         (case when ((paytable.GT_Group='GT2' and pos_haud.[isVoid]=0) or       
        (isnull(round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-       
        (CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) -       
        (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else 
        (pos_taud.pay_actamt/107)*7 End) )/100  +0 , 3),0)=0)) then 0 else Convert(Decimal(19,3),(pos_taud.pay_actamt/107)*7) end)  
           else  
           0   
           end     
           [taxes],  
        
        Convert(Decimal(19,3),Case When pos_taud.pay_type='CN' Then pos_taud.PAY_GST else (CASE When 
        (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) end) [gstRate],      
              
        round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then 
        (pos_taud.pay_actamt) Else 0 End )- (CASE When (pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) , 3) [netAmt],      
              
        
              
        0 [comm],      
        round((isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 
        Else (pos_taud.pay_actamt/107)*7 End ))/100 ,3) as [BankCharges],      
        round(pos_taud.pay_actamt-(Case When pos_taud.pay_type='CN' Then (pos_taud.pay_actamt) Else 0 End )-(CASE When 
        (pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End)  - (isnull(bank_charges,0) * (pos_taud.pay_actamt - CASE When (pos_taud.pay_actamt-pos_taud.PAY_GST)=0 Then 0 Else (pos_taud.pay_actamt/107)*7 End) )/100  +0 , 3) [total],      
        pos_haud.ItemSite_Code,Item_SiteList.ItemSite_Desc      
        FROM pos_haud       
        INNER JOIN pos_taud ON pos_haud.sa_transacno = pos_taud.sa_transacno         
        INNER JOIN Customer ON pos_haud.sa_custno = Customer.Cust_code       
        INNER JOIN Item_SiteList ON pos_haud.ItemSite_Code = Item_SiteList.ItemSite_Code       
        INNER JOIN paytable ON pos_taud.PAY_TYPE=paytable.PAY_CODE      
        Where pos_haud.sa_date BETWEEN '{1}' and '{2}' 
        {3} --Site      
        )X      
        Group By X.payDate,X.customer,X.invoiceRef,X.payTypes,X.ItemSite_Code,X.ItemSite_Desc,[payRef],
        [CustRef],X.[Group],X.isVoid,X.sa_remark 
        """

        raw_q = raw_q.format(site_code_q_2,start, end, site_code_q)
        print(raw_q)

        with connection.cursor() as cursor:
            cursor.execute(raw_q)
            raw_qs = cursor.fetchall()
            desc = cursor.description
            responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class TreatmentDone(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self, request):
        """
            query parm: start: datetime string(2021-01-01T00:00:00)
                        in: day, week, month
        """

        # try:
        #     start_date = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d").date()
        #     end_date = datetime.datetime.strptime(request.GET.get("end"), "%Y-%m-%d").date()
        #     date_range = [start_date + datetime.timedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]
        # except:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,
        #               'message': "start and end query parameters are mandatory. format is YYYY-MM-DD",
        #               'error': True,
        #               "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        _in = request.GET.get('in', '')
        if _in.lower() == 'day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower() == 'week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower() == 'month':
            _delta = relativedelta.relativedelta(months=1)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "in query parameters are mandatory. (day,week,month)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        start = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
        _pre_start = start - _delta
        end = start + _delta
        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        elif _siteGroup or _siteCodes:
            if _siteCodes:
                site_code_list = _siteCodes.split(",")
            elif _siteGroup:
                site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True, site_group=_siteGroup). \
                    exclude(itemsite_code__icontains="HQ"). \
                    values_list('itemsite_code', flat=True)
            _s = ', '.join(['\'' + str(code) + '\'' for code in site_code_list])
            site_code_q = f"AND pos_haud.ItemSite_Code IN ({_s})"
        else:
            site_code_q = ""

        pay_group_q = ""

        # _type = request.GET.get('type','').lower()
        # if _type == "sales":
        #     amount = Sum("sales_gt1_gst")
        # elif _type == "service":
        #     amount = Sum("servicesales_gt1")
        # elif _type == "product":
        #     amount = Sum("productsales_gt1")
        # elif _type == "prepaid":
        #     amount = Sum("prepaidsales_gt1")
        # else:
        #     result = {'status': status.HTTP_400_BAD_REQUEST,
        #               'message': "type query parameters are mandatory. (sales,service,product,prepaid)",
        #               'error': True,
        #               "data": None}
        #     return Response(result, status=status.HTTP_400_BAD_REQUEST)

        raw_q = """
                SELECT   distinct            
                Convert(Date,pos_haud.sa_date,103) AS [invoiceDate],              
                Convert(Date,Treatment_Account.sa_date,103) AS [usageDate],              
                pos_haud_1.SA_TransacNo_Ref AS [usageRef],              
                pos_haud.SA_TransacNo_Ref AS [invoiceRef],            
                pos_haud.ItemSIte_Code as [Site_Code],               
                Item_SiteList.ItemSite_Desc AS [site],             
                Customer.Cust_name [custName],              
                isnull(Customer.Cust_Refer,'') [custRef],              
                Treatment_Account.User_Name [createdBy],             
                (item_Class.itm_desc) [category],             
                isnull((Item_Range.itm_desc),'')  [subCategory],                
                Treatment_account.Description [itemName],             
                Treatment.Service_ItemBarcode [skuCode],             
                isnull(Treatment.Duration,0) 
                [duration],             
                Treatment_Account.Qty [usageQty],             
                -1*Treatment_Account.Amount [unitValue],             
                isnull(Item_Helper.Helper_Name,'') [therapists],                
                (Select Count(*) from Item_Helper Where Helper_transacno=Treatment_Account.sa_transacno And Line_No=Treatment_Account.dt_LineNo)  [numTherapists],             
                '' [SerPtType],                
                isnull((Select distinct Item_Helper.WP1 from Item_Helper t1 Where t1.Helper_transacno=Treatment_Account.sa_transacno  
                And t1.Line_No=Treatment_Account.dt_LineNo and t1.Helper_Name=Item_Helper.Helper_Name),'')  [SerPt],                
                '' [remarks]                
                FROM Treatment_Account INNER JOIN                   
                pos_haud ON Treatment_Account.sa_transacno = pos_haud.sa_transacno INNER JOIN          
                Item_Helper On Item_Helper.Helper_transacno=Treatment_Account.sa_transacno And   Item_Helper.Line_No=Treatment_Account.dt_LineNo  
                INNER JOIN               
                pos_haud AS pos_haud_1 ON Treatment_Account.sa_transacno = pos_haud_1.sa_transacno INNER JOIN             
                Customer ON Treatment_Account.Cust_Code = Customer.Cust_code INNER JOIN             
                Treatment ON Treatment.Treatment_ParentCode=Treatment_Account.Treatment_ParentCode And Treatment.status='Done' INNER JOIN             
                Item_SiteList ON pos_haud_1.ItemSite_Code=Item_SiteList.ItemSite_Code INNER JOIN             
                Stock ON Stock.item_code+'0000'=Treatment.Service_ItemBarcode INNER JOIN             
                item_Class ON item_Class.itm_code=Stock.Item_Class INNER JOIN             
                Item_Range ON Item_Range.itm_code=Stock.Item_Range             
                WHERE (Treatment_Account.Type <> 'Deposit')             
                And pos_haud.sa_date BETWEEN '{0}' AND '{1}'
                {2} --Site                    
                order by therapists  
        """

        raw_q = raw_q.format(start, end, site_code_q)
        print(raw_q)

        with connection.cursor() as cursor:
            cursor.execute(raw_q)
            raw_qs = cursor.fetchall()
            desc = cursor.description
            responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class CustomerBirthday(APIView):
    def get(self,request):
        """
        filter: Dept, Site, Show old bill, show non sales
                Staff perfomance api will return individual employee performance for a day
                    |  Date | Dept | Invoice No. | Item Desc | Discount | Qty | Amount |
                :param request:
                :return:
                """
        _in = request.GET.get('in', '')
        if _in.lower() == 'day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower() == 'week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower() == 'month':
            _delta = relativedelta.relativedelta(months=1)
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "in query parameters are mandatory. (day,week,month)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        start = datetime.datetime.strptime(request.GET.get("start"), "%Y-%m-%d")
        _pre_start = start - _delta
        end = start + _delta
        # filters
        # site
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist_Reporting.objects.filter(itemsite_isactive=True)  # . \
            # exclude(itemsite_code__icontains="HQ"). \
            # values('itemsite_code', 'itemsite_desc')

        if _siteCodes:
            site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        qs = Customer_Reporting.objects.filter(dob_status=True,cust_isactive=True)
        qs = model_joiner(qs,Treatment_Reporting,(('cust_code','cust_code'),),
                          select=['treatment_code','treatment_date','sa_status','status']
                          )
        qs = qs.filter(Treatment_Reporting__treatment_date__range=[start,end],Treatment_Reporting__sa_status='SA',Treatment_Reporting__status="Done")
        qs = qs.values('cust_code','cust_name','cust_dob','dob_status','cust_isactive').annotate(t_count=Count('Treatment_Reporting__treatment_code'))

        print(qs)
        print(qs.query)
        responseData=qs
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)



class ReportSettingsView(APIView):
    def get(self,request,path):
        file_path = os.path.join(REPORT_SETTINGS_PATH, path + ".json")

        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("{}")

        with open(file_path,"r") as f:
            obj = json.load(f)
            responseData = obj
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)

    def post(self,request,path):
        file_path = os.path.join(REPORT_SETTINGS_PATH, path + ".json")
        req_obj = request.data

        with open(file_path,"w") as f:
            str_data = json.dumps(req_obj)
            f.write(str_data)
            responseData = req_obj
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)



@api_view(['GET', ])
def pay_group_list(request):
    qs = PayGroup_Reporting.objects.all().values_list('pay_group_code',flat=True)
    response_data = list(qs)
    result = {'status': status.HTTP_200_OK, "message": "Login Successful", 'error': False, 'data': response_data}
    return Response(result, status=status.HTTP_200_OK)