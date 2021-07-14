from datetime import datetime
from multiprocessing import connection

from django.test import TestCase

# Create your tests here.
from cl_app.models import ItemSitelist
from cl_table.models import PosDaud

# start_date = datetime(2021,6,1)
# end_date = datetime(2021,6,10)
#
# site_code_list = ItemSitelist.objects.filter(itemsite_isactive=True).\
#                 exclude(itemsite_code__icontains="HQ").\
#                 values_list('itemsite_code', flat=True)
# site_code_q = ', '.join(['\''+str(code)+'\'' for code in site_code_list])
#
#
# raw_q = f"SELECT MAX(e.display_name) Consultant, " \
#                         f"cast(SUM(pd.dt_deposit/100*ms.ratio) AS decimal(9,2)) amount, " \
#                         f"pd.ItemSite_Code AS siteCode, MAX(e.emp_name) FullName " \
#                 f"FROM pos_daud pd " \
#                 f"INNER JOIN multistaff ms ON pd.sa_transacno = ms.sa_transacno and pd.dt_lineno = ms.dt_lineno " \
#                 f"LEFT JOIN employee e on ms.emp_code = e.emp_code " \
#                 f"WHERE pd.ItemSite_Code IN ({site_code_q})" \
#                 f"AND pd.sa_date BETWEEN '{start_date}' AND '{end_date}' " \
#                 f"GROUP BY ms.emp_code, pd.ItemSite_Code " \
#                 f"ORDER BY Amount DESC"
#
# with connection.cursor() as cursor:
#     cursor.execute(raw_q)
#     raw_qs = cursor.fetchall()
#     desc = cursor.description
#     responseData = [dict(zip([col[0] for col in desc], row)) for row in raw_qs]
#     # for row in raw_qs:
#
# # sales_qs = PosDaud.objects.filter(itemsite_code__in=site_code_list,sa_date__range=[start_date,end_date]).exclude(record_detail_type__startswith='TD')
# raw_pos_q = ""
# sales_qs = PosDaud.objects.filter(itemsite_code__in=site_code_list,sa_date__range=[start_date,end_date]).exclude(record_detail_type__startswith='TD')


from cl_table.models import PosHaud, PosDaud

import datetime
s = datetime.datetime(2021,6,1)
e = datetime.datetime(2021,6,10)
h = PosHaud.objects.filter(sa_date__range=[s,e])

from django.db.models import OuterRef, Subquery

