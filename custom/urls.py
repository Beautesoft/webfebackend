from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views



# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'jobtitle', views.JobTitleViewset)
router.register(r'room', views.RoomViewset)
router.register(r'comboservices', views.ComboServicesViewset)
router.register(r'category', views.CategoryViewset)
router.register(r'type', views.TypeViewset)
router.register(r'itemcart', views.itemCartViewset)
router.register(r'voucher', views.VoucherRecordViewset)
router.register(r'empcartlist', views.EmployeeCartAPI)
router.register(r'pospackagedeposit', views.PosPackagedepositViewset)
router.register(r'smtpsettings', views.SmtpSettingsViewset)
router.register(r'cartpopup', views.CartPopupViewset)
router.register(r'cartservicecourse', views.CartServiceCourseViewset)


# router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/receiptpdf/', views.ReceiptPdfGeneration.as_view(), name='receiptpdf'),
    path('api/receiptpdfsend/', views.ReceiptPdfSend.as_view(), name='receiptpdfsend'),
    path('api/paymentremarks/', views.PaymentRemarksAPIView.as_view(), name='paymentremarks'),
    path('api/holditemsetup/', views.HolditemSetupAPIView.as_view(), name='holditemsetup'),
    path('api/cartitemdelete/', views.CartItemDeleteAPIView.as_view(), name='cartitemdelete'),
    path('api/exchangeproduct/', views.ExchangeProductAPIView.as_view(), name='exchangeproduct'),
    path('api/exchangeproductconfirm/', views.ExchangeProductConfirmAPIView.as_view(), name='exchangeproductconfirm'),
    path('api/coursetmp/', views.CourseTmpAPIView.as_view(), name='coursetmp'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
