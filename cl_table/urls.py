from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views



urlpatterns = [
    path('api/login', views.UserLoginAPIView.as_view(), name='login'),
    path('api/logout', views.UserLogoutAPIView.as_view(), name='logout'),
    path('api/employeebranchwise', views.EmployeeList.as_view(), name='employee-branch'),
    path('api/skills', views.ServicesListAPIView.as_view(), name='skills'),
    path('api/shiftlist', views.ShiftListAPIView.as_view(), name='shiftlist'),
    path('api/customers/all/', views.CustomerListAPIView.as_view(), name='customer_all'),
    path('api/bookingstatus/', views.AppointmentBookingStatusList.as_view(), name='bookingstatus'),
    path('api/branchlist/', views.ItemSiteListAPIView.as_view(), name='branchlist'),
    path('api/branchlogin/', views.ItemSiteListAPIViewLogin.as_view(), name='branchlogin'),
    path('api/treatmentstock/<int:pk>/', views.StockDetail.as_view(), name='treatmentstock'),
    path('api/staffsavailable/', views.StaffsAvailable.as_view(), name='staffsavailable'),
    path('api/userlist/', views.UsersList.as_view(), name='userlist'),
    path('api/paytable/', views.PaytableListAPIView.as_view(), name='paytable'),
    path('api/customerreceiptprint/', views.CustomerReceiptPrintList.as_view(), name='customerreceiptprint'),
    path('api/source/', views.SourceAPI.as_view(), name='source'),
    path('api/securities/', views.SecuritiesAPIView.as_view(), name='securities'),
    path('api/schedulehour/', views.ScheduleHourAPIView.as_view(), name='schedulehour'),
    path('api/custappt/', views.CustApptAPI.as_view(), name='custappt'),
    path('api/appttype/', views.ApptTypeAPIView.as_view(), name='appttype'),
    path('api/focreason/', views.FocReasonAPIView.as_view(), name='focreason'),
    # path('api/updatetable/', views.UpdateTablesAPIView.as_view(), name='updatetable'),
    path('api/treatmentpackages/', views.TreatmentApptAPI.as_view(), name='treatmentpackages'),
    path('api/appointmentsort/', views.AppointmentSortAPIView.as_view(), name='appointmentsort'),
    path('api/meta/race/', views.meta_race, name='meta_race'),
    path('api/meta/nationality/', views.meta_nationality, name='meta_nationality'),
    path('api/meta/religion/', views.meta_religious, name='meta_religious'),
    path('api/meta/country/', views.meta_country, name='meta_country'),
    path('api/WorkScheduleMonth/', views.MonthlyWorkSchedule.as_view(), name='WorkScheduleMonth'),
    path('api/WorkScheduleHours/', views.schedule_hours, name='WorkScheduleHours'),

    path('api/EmployeeSkills/', views.EmployeeSkillView, name='EmployeeSkillView'),



    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)