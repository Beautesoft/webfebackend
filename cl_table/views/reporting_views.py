import datetime

from dateutil import relativedelta
from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from cl_app.models import ItemSitelist
from cl_table.models import ItemSitelist_Reporting


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
            site_code_q = f"AND pos_haud.ItemSite_Code IN {_s}"
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