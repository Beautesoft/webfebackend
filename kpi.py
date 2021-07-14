class DailySalesSummeryBySiteView(APIView):
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

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True). \
                exclude(itemsite_code__icontains="HQ"). \
                values_list('itemsite_code', 'itemsite_desc')
        print(site_code_list)
        if _siteCodes:
            site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        _q_sitecode = list(site_code_list.values_list('itemsite_code', flat=True))


        sales_qs = DailysalesdataSummary.objects.filter(sitecode__in=_q_sitecode,business_date__range=[start_date,end_date])

        data_list = []
        site_total_dict = {}

        for i, date in enumerate(date_range):
            row_dict = {"id":i+1 ,"date":date.strftime("%d/%m/%Y")}
            # _amount = {"GT1":0, "GT2": 0, "BOTH": 0}
            _amount = 0
            for site in site_code_list:
                try:
                    sale_obj = sales_qs.get(sitecode=site[0], business_date=date)
                    # total = sale_obj.get_total_amount[sales_setting]
                    total = sale_obj.sales_gt1_withgst if sale_obj.sales_gt1_withgst else 0
                except Exception as e:
                    total = 0
                _amount += total
                _outlet = site[1]
                row_dict[_outlet] = round(total,2)
                site_total_dict[_outlet] = round(site_total_dict.get(_outlet,0) + total,2)
            row_dict["total"] = round(_amount,2)
            data_list.append(row_dict)
        # data_list.append(site_total_dict)
        responseData = {"data":data_list, "chart":site_total_dict}
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class MonthlySalesSummeryBySiteView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        try:
            s_year = int(request.GET.get("syear"))
            e_year = int(request.GET.get("eyear"))
            s_month = int(request.GET.get("smonth"))
            e_month = int(request.GET.get("emonth"))
            start_date = datetime.datetime(year=s_year, month=s_month, day=1)
            end_date = datetime.datetime(year=e_year, month=e_month + 1, day=1)

            month_list = list(rrule.rrule(rrule.MONTHLY, dtstart=start_date, until=end_date))
        except:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "syear, eyear, smonth and emonth query parameters are mandatory.",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True). \
                exclude(itemsite_code__icontains="HQ"). \
                values_list('itemsite_code', 'itemsite_desc')

        if _siteCodes:
            site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        _q_sitecode = list(site_code_list.values_list('itemsite_code', flat=True))


        sales_qs = DailysalesdataSummary.objects.filter(sitecode__in=_q_sitecode,business_date__range=[start_date,end_date])
        data_list = []
        site_total_dict = {}
        for i, curr_month in enumerate(month_list):
            row_dict = {'id':i+1, 'month':curr_month.strftime("%b, %Y")}
            _amount = 0
            try:
                for site in site_code_list:
                    next_month = month_list[i+1]
                    _tot = sales_qs.filter(business_date__range=[curr_month, next_month],sitecode=site[0]).aggregate(Sum('sales_gt1_withgst')) # index 0 is site code
                    total = _tot['sales_gt1_withgst__sum'] if type(_tot['sales_gt1_withgst__sum']) == float else 0
                    row_dict[_outlet] = round(total,2)
                    _amount += total
                    _outlet = site[1] # index 1 is outlet name
                    site_total_dict[_outlet] = round(site_total_dict.get(_outlet, 0) + total, 2)
            except IndexError:
                continue
            row_dict['total'] = _amount
            data_list.append(row_dict)
            responseData = {"data": data_list, "chart": site_total_dict}
        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class DailySalesSummeryByConsultantView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):

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

        # filters
        _siteCodes = request.GET.get("siteCodes")
        _siteGroup = request.GET.get("siteGroup")
        if _siteGroup and _siteCodes:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "siteCodes and siteGroup query parameters can't use in sametime", 'error': True, "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
                exclude(itemsite_code__icontains="HQ").\
                values_list('itemsite_code', flat=True)

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)
        site_code_q = ', '.join(['\''+str(code)+'\'' for code in site_code_list])
        raw_q = f"SELECT MAX(e.display_name) Consultant, " \
                        f"cast(SUM(pd.dt_deposit/100*ms.ratio) AS decimal(9,2)) amount, " \
                        f"pd.ItemSite_Code AS siteCode, MAX(e.emp_name) FullName " \
                f"FROM pos_daud pd " \
                f"INNER JOIN multistaff ms ON pd.sa_transacno = ms.sa_transacno and pd.dt_lineno = ms.dt_lineno " \
                f"LEFT JOIN employee e on ms.emp_code = e.emp_code " \
                f"WHERE pd.ItemSite_Code IN ({site_code_q})" \
                f"AND pd.sa_date BETWEEN '{start_date}' AND '{end_date}' " \
                f"GROUP BY ms.emp_code, pd.ItemSite_Code " \
                f"ORDER BY Amount DESC"

        with connection.cursor() as cursor:
            cursor.execute(raw_q)
            raw_qs = cursor.fetchall()
            desc = cursor.description
            # responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]
            # for row in raw_qs:
            data_list = []
            site_total_dict = {}
            for i,row in enumerate(raw_qs):
                _d = dict(zip([col[0] for col in desc], row))
                _d['id'] = i+1
                data_list.append(_d)
                site_total_dict[_d['Consultant']] = round(site_total_dict.get(_d['Consultant'], 0) + _d['amount'], 2)

            responseData = {"data": data_list, "chart": site_total_dict}
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
            return Response(result, status=status.HTTP_200_OK)




@api_view(['GET', ])
def site_group_list(request):
    qs = SiteGroup.objects.filter(is_active=True).values('id','code','description')
    response_data = {
        "groups": list(qs),
        "message": "Listed successfuly"
    }
    result = {'status': status.HTTP_200_OK, "message": "Login Successful", 'error': False, 'data': response_data}
    return Response(result, status=status.HTTP_200_OK)



class RankingByOutletView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        """
            query parm: start: datetime string(2021-01-01T00:00:00)
                        in: day, week, month
                        type: sales, service, product, prepaid
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

        _in = request.GET.get('in','')
        if _in.lower()=='day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower()=='week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower()=='month':
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
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True). \
                exclude(itemsite_code__icontains="HQ"). \
                values_list('itemsite_code','itemsite_desc')

        if _siteCodes:
            site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        _q_sitecode = list(site_code_list.values_list('itemsite_code', flat=True))

        _type = request.GET.get('type','').lower()
        if _type == "sales":
            amount = Sum("sales_gt1_gst")
        elif _type == "service":
            amount = Sum("servicesales_gt1")
        elif _type == "product":
            amount = Sum("productsales_gt1")
        elif _type == "prepaid":
            amount = Sum("prepaidsales_gt1")
        else:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "type query parameters are mandatory. (sales,service,product,prepaid)",
                      'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


        sales_qs = DailysalesdataSummary.objects.filter(sitecode__in=_q_sitecode,
                                                        business_date__range=[start, end])\
            .values('sitecode').annotate(amount=amount).order_by('-amount')

        prev_sales_qs = DailysalesdataSummary.objects.filter(
            sitecode__in=_q_sitecode,
            business_date__range=[_pre_start, start]) \
            .values('sitecode').annotate(amount=amount).order_by('-amount')

        prev_rank_dict = {}
        for i, _s in enumerate(prev_sales_qs):
            prev_rank_dict[_s["sitecode"]] = [i + 1,_s['amount']]

        responseData = []
        for i,sale in enumerate(sales_qs):
            _outlet = site_code_list.get(itemsite_code=sale['sitecode'])[1]
            _curr_rank = i+1
            prev_dict = prev_rank_dict.get(sale['sitecode'],[len(_q_sitecode),0])
            try:
                responseData.append({
                    "id": _curr_rank,
                    "rank": _curr_rank,
                    "rankDif": prev_dict[0] - _curr_rank, #should calc
                    "prevValue": round(prev_dict[1], 2),
                    # "siteCode": sale['sitecode'],
                    "outlet": _outlet,
                    "amount": round(sale['amount'],2),
                    "startDate": start.date().strftime("%d/%m/%Y")
                })
            except Exception as e:
                print(e)
                continue

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)


class ServicesByConsultantView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
        """
            query parm: start: datetime string(2021-01-01T00:00:00)
                        in: day, week, month
                        order: sales, service, product, prepaid
        """

        _in = request.GET.get('in','')
        if _in.lower()=='day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower()=='week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower()=='month':
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
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True). \
                exclude(itemsite_code__icontains="HQ"). \
                values_list('itemsite_code', 'itemsite_desc')

        if _siteCodes:
            site_code_list = site_code_list.filter(itemsite_code__in=_siteCodes.split(","))
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        _q_sitecode = list(site_code_list.values_list('itemsite_code', flat=True))

        #order by filter
        _order = request.GET.get("order","count")
        if _order not in ['amount','count','average']:
            result = {'status': status.HTTP_400_BAD_REQUEST,
                      'message': "order query parameters should be one of these ('amount','count','average')", 'error': True,
                      "data": None}
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


        sales_qs = DailysalestdSummary.objects.filter(sitecode__in=_q_sitecode,
                                                      business_date__range=[start, end]) \
                            .values('helper_code').annotate(amount=Sum('daily_share_amount'),
                                         count=Sum('daily_share_count'),
                                         average=Sum('daily_share_amount')/Sum('daily_share_count')).order_by('-'+_order)
        prev_sales_qs = DailysalestdSummary.objects.filter(sitecode__in=_q_sitecode,
                                                      business_date__range=[_pre_start, start]) \
                            .values('helper_code').annotate(amount=Sum('daily_share_amount'),
                                         count=Sum('daily_share_count'),
                                         average=Sum('daily_share_amount')/Sum('daily_share_count')).order_by('-'+_order)

        prev_rank_dict = {}
        for i, _s in enumerate(prev_sales_qs):
            prev_rank_dict[_s["helper_code"]] = [i + 1,_s[_order]]


        responseData = []
        for i, sale in enumerate(sales_qs):
            # _outlet = site_code_list.get(itemsite_code=sale['sitecode'])[1]
            _curr_rank = i + 1
            try:
                staff_name = Employee.objects.filter(emp_code=sale['helper_code']).values('emp_name').first()['emp_name']
                prv_dict = prev_rank_dict.get(sale['helper_code'], [0,0])
                responseData.append({
                    "id": _curr_rank,
                    "rank": _curr_rank,
                    # "empCode": sale['helper_code'],
                    "consultant": staff_name,
                    "rankDif": prv_dict[0] - _curr_rank,  # should calc
                    "prevValue": round(prv_dict[1],2),
                    # "SiteCode": sale['sitecode'],
                    # "Outlet": _outlet,
                    "amount": round(sale['amount'],2),
                    "count": sale['count'],
                    "average": round(sale['average'],2),
                    "startDate": start.date()

                })
            except Exception as e:
                print(e)

        result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": responseData}
        return Response(result, status=status.HTTP_200_OK)



class SalesByConsultantView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated & authenticated_only]

    def get(self,request):
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

        _in = request.GET.get('in','')
        if _in.lower()=='day':
            _delta = datetime.timedelta(days=1)
        elif _in.lower()=='week':
            _delta = datetime.timedelta(days=14)
        elif _in.lower()=='month':
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
        else:
            site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True). \
                exclude(itemsite_code__icontains="HQ"). \
                values_list('itemsite_code', flat=True)

        if _siteCodes:
            site_code_list = _siteCodes.split(",")
        elif _siteGroup:
            site_code_list = site_code_list.filter(site_group=_siteGroup)

        site_code_q = ', '.join(['\''+str(code)+'\'' for code in site_code_list])

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

        raw_q = "SELECT MAX(e.display_name) consultant, " \
                "cast(SUM(pd.dt_deposit/100*ms.ratio) AS decimal(9,2)) amount, " \
                "ms.emp_code AS empCode, " \
                "MAX(e.emp_name) AS fullName " \
                "FROM pos_daud pd " \
                "INNER JOIN multistaff ms ON pd.sa_transacno = ms.sa_transacno and pd.dt_lineno = ms.dt_lineno " \
                "LEFT JOIN employee e on ms.emp_code = e.emp_code " \
                "WHERE pd.ItemSite_Code IN ({0})" \
                "AND pd.sa_date BETWEEN '{1}' AND '{2}' " \
                "GROUP BY ms.emp_code " \
                "ORDER BY amount DESC"

        # #previous qs
        _prev_dict = {}
        with connection.cursor() as cursor:
            cursor.execute(raw_q.format(site_code_q,_pre_start,start))
            raw_qs = cursor.fetchall()
            desc = cursor.description
            for i, row in enumerate(raw_qs):
                _d = dict(zip([col[0] for col in desc], row))
                _prev_dict[_d['empCode']] = [i+1,_d['amount']]


        with connection.cursor() as cursor:
            cursor.execute(raw_q.format(site_code_q,start,end))
            raw_qs = cursor.fetchall()
            desc = cursor.description
            # responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]
            # for row in raw_qs:
            data_list = []
            site_total_dict = {}
            for i, row in enumerate(raw_qs):
                _prev = _prev_dict.get(_d['empCode'], [0,0]) #todo: this index 0 value should be change to emp list length
                _curr_rank = i + 1
                _d = dict(zip([col[0] for col in desc], row))
                _d['id'] = i + 1
                _d['rank'] = i + 1
                _d['rankDif'] = 0
                data_list.append({
                    "id" : _curr_rank,
                    "rank": _curr_rank,
                    "rankDif": _prev[0]- _curr_rank,
                    "prevValue": round(_prev[1], 2),
                    "fullName": _d['fullName'],
                    "consultant": _d['consultant'],
                    "amount": _d['amount'],
                    # "empCode": _d['empCode'],
                })
                # print(_d)

            # responseData = {"data": data_list}
            result = {'status': status.HTTP_200_OK, 'message': "success", 'error': False, "data": data_list}
            return Response(result, status=status.HTTP_200_OK)
