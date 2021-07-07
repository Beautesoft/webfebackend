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
    path('api/userlist/', views.UsersList.as_view(), name='userlist'), #
    path('api/paytable/', views.PaytableListAPIView.as_view(), name='paytable'),
    path('api/customerreceiptprint/', views.CustomerReceiptPrintList.as_view(), name='customerreceiptprint'),
    path('api/source/', views.SourceAPI.as_view(), name='source'),
    path('api/state/', views.StateAPI.as_view(), name='state'),
    path('api/country/', views.CountryAPI.as_view(), name='country'),
    path('api/language/', views.LanguageAPI.as_view(), name='language'),
    path('api/securities/', views.SecuritiesAPIView.as_view(), name='securities'),
    path('api/schedulehour/', views.ScheduleHourAPIView.as_view(), name='schedulehour'),
    path('api/custappt/', views.CustApptAPI.as_view(), name='custappt'),
    path('api/appttype/', views.ApptTypeAPIView.as_view(), name='appttype'),
    path('api/focreason/', views.FocReasonAPIView.as_view(), name='focreason'),
    # path('api/updatetable/', views.UpdateTablesAPIView.as_view(), name='updatetable'),
    path('api/treatmentpackages/', views.TreatmentApptAPI.as_view(), name='treatmentpackages'),
    path('api/appointmentsort/', views.AppointmentSortAPIView.as_view(), name='appointmentsort'),
    path('api/appttreatmentdonehistory/', views.ApptTreatmentDoneHistoryAPI.as_view(), name='appttreatmentdonehistory'),
    path('api/upcomingappointment/', views.UpcomingAppointmentAPIView.as_view(), name='upcomingappointment'),
    path('api/blockreason/', views.BlockReasonAPIView.as_view(), name='blockreason'),
    path('api/appointmentlistpdf/', views.AppointmentListPdf.as_view(), name='appointmentlistpdf'),
    path('api/dayendlist/', views.DayEndListAPIView.as_view(), name='dayendlist'),
    path('api/appointmentlog/', views.AppointmentLogAPIView.as_view(), name='appointmentlog'),
    path('api/custapptupcoming/', views.CustApptUpcomingAPIView.as_view(), name='custapptupcoming'),
    path('api/attendancestaff/', views.AttendanceStaffsAPIView.as_view(), name='attendancestaff'),
    path('api/meta/race/', views.meta_race, name='meta_race'),
    path('api/meta/nationality/', views.meta_nationality, name='meta_nationality'),
    path('api/meta/religion/', views.meta_religious, name='meta_religious'),
    path('api/meta/country/', views.meta_country, name='meta_country'),
    path('api/WorkScheduleMonth/', views.MonthlyWorkSchedule.as_view(), name='WorkScheduleMonth'),
    path('api/MonthlyAllSchedule/', views.MonthlyAllSchedule.as_view(), name='MonthlyAllSchedule'),
    path('api/WorkScheduleHours/', views.schedule_hours, name='WorkScheduleHours'),
    path('api/SkillsItemTypeList/', views.SkillsItemTypeList, name='SkillsItemTypeList'),
    path('api/SkillsView/', views.SkillsView.as_view(), name='SkillsView'),
    path('api/PhotoDiagnosis/', views.PhotoDiagnosis.as_view(), name='PhotoDiagnosis'),
    path('api/DiagnosisCompare/', views.DiagnosisCompareView.as_view(), name='DiagnosisCompare'),


    path('api/EmployeeSkills/', views.EmployeeSkillView.as_view(), name='EmployeeSkillView'),
    path('api/CustomerFormSettings/', views.CustomerFormSettingsView.as_view(), name='CustomerFormSettingsView'),
    path('api/CustomerFormSettings/details', views.CustomerFormSettings, name='CustomerFormSettingsDetails'),
    # path('api/RewardPolicy/', views.RewardPolicyView.as_view(), name='RewardPolicyView'),
    # path('api/RedeemPolicy/', views.RedeemPolicyView.as_view(), name='RedeemPolicyView'),
    path('api/EmployeeSecuritySettings/', views.EmployeeSecuritySettings.as_view(), name='EmployeeSecuritySettings'),
    path('api/IndividualEmpSettings/<int:emp_no>', views.IndividualEmpSettings.as_view(), name='IndividualEmpSettings'),
    path('api/MultiLanguage/', views.MultiLanguage, name='MultiLanguage'),
    path('api/EmployeeLevels/', views.EmployeeLevels, name='EmployeeLevels'),
    path('api/DailySales/', views.DailySalesView.as_view(), name='DailySales'),
    path('api/DailySalesSummery/', views.DailySalesSummeryView.as_view(), name='DailySalesSummeryView'),
    path('api/MonthlySalesSummery/', views.MonthlySalesSummeryView.as_view(), name='MonthlySalesSummeryView'),
    path('api/DailySalesBySite/', views.DailySalesSummeryBySiteView.as_view(), name='DailySalesSummeryBySiteView'),
    path('api/MonthlySalesBySite/', views.MonthlySalesSummeryBySiteView.as_view(), name='MonthlySalesSummeryBySiteView'),
    path('api/DailySalesByConsultant/', views.DailySalesSummeryByConsultantView.as_view(), name='DailySalesSummeryByConsultantView'),
    path('api/ServicesByOutlet/', views.ServicesByOutletView.as_view(), name='ServicesByOutletView'),
    path('api/ProductByOutlet/', views.ProductByOutletView.as_view(), name='ProductByOutletView'),
    path('api/RankingByOutlet/', views.RankingByOutletView.as_view(), name='RankingByOutletView'),
    path('api/ServicesByConsultant/', views.ServicesByConsultantView.as_view(), name='ServicesByConsultantView'),
    path('api/site_group_list/', views.site_group_list, name='site_group_list'),


    path('api/temp_login', views.temp_login, name='temp_login'),



    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)