from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static


# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'salon', views.SalonViewset, basename='salon')
router.register(r'catalogitemdept', views.CatalogItemDeptViewset, basename='catalogitemdept')
router.register(r'servicestock', views.ServiceStockViewset, basename='servicestock')
router.register(r'retailstock', views.RetailStockListViewset, basename='retailstock')
router.register(r'packagestock', views.PackageStockViewset, basename='packagestock')
router.register(r'packagedtl', views.PackageDtlViewset, basename='packagedtl')
router.register(r'prepaidstock', views.PrepaidStockViewset, basename='prepaidstock')
router.register(r'voucherstock', views.VoucherStockViewset, basename='voucherstock')
router.register(r'catalogitemrange', views.CatalogItemRangeViewset, basename='catalogitemrange')
router.register(r'catalogsearch', views.CatalogSearchViewset, basename='catalogsearch')
router.register(r'salonsearch', views.SalonProductSearchViewset, basename='salonsearch')
router.register(r'topuptreatment', views.TopupViewset, basename='topuptreatment')
router.register(r'catalogfavorites', views.CatalogFavoritesViewset, basename='catalogfavorites')
router.register(r'treatmentdone', views.TreatmentDoneViewset, basename='treatmentdone')
router.register(r'trmttmpitemhelper', views.TrmtTmpItemHelperViewset, basename='trmttmpitemhelper')
router.register(r'topupproduct', views.TopupproductViewset, basename='topupproduct')
router.register(r'topupprepaid', views.TopupprepaidViewset, basename='topupprepaid')
router.register(r'reversal', views.ReversalListViewset, basename='reversal')
router.register(r'showbalance', views.ShowBalanceViewset, basename='showbalance')
router.register(r'reversereason', views.ReverseTrmtReasonAPIView, basename='reversereason')
router.register(r'void', views.VoidViewset, basename='void')
router.register(r'voidreason', views.VoidReasonViewset, basename='voidreason')
router.register(r'treatmentacclist', views.TreatmentAccListViewset, basename='treatmentacclist')
router.register(r'creditnotelist', views.CreditNoteListViewset, basename='creditnotelist')
router.register(r'productacclist', views.ProductAccListViewset, basename='productacclist')
router.register(r'prepaidacclist', views.PrepaidAccListViewset, basename='prepaidacclist')
router.register(r'combo', views.ComboViewset, basename='combo')
router.register(r'billing', views.BillingViewset, basename='billing')
router.register(r'prepaidpay', views.PrepaidPayViewset, basename='prepaidpay'),
router.register(r'holditem', views.HolditemdetailViewset, basename='holditem'),


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/otp/', views.ForgotPswdRequestOtpAPIView.as_view(), name='otp'),
    path('api/otpvalidate/', views.ForgotPswdOtpValidationAPIView.as_view(), name='otpvalidate'),
    path('api/passwordreset/', views.ResetPasswordAPIView.as_view(), name='passwordreset'),
    # path('api/updatestock/', views.UpdateStockAPIView.as_view(), name='updatestock'),
    path('api/receiptpdfsendsms/', views.ReceiptPdfSendSMSAPIView.as_view(), name='receiptpdfsendsms'),
    path('api/custsign/', views.CustomerSignatureAPIView.as_view(), name='custsign'),
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
    path('api/creditnotepay/', views.CreditNotePayAPIView.as_view(), name='creditnotepay'),
    path('api/voidcheck/', views.VoidCheck.as_view(), name='voidcheck'),
    path('api/voidcancel/', views.VoidCancel.as_view(), name='voidcancel'),
    # path('api/deleteapi/', views.DeleteAPIView.as_view(), name='deleteapi'),
    # path('api/controlno/', views.ControlAPIView.as_view(), name='controlno'),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
