from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, InvoiceViewSet, InvoiceItemViewSet, download_invoice_pdf, send_invoice_email, login_status
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register(r'clients', ClientViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoice-items', InvoiceItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('invoices/<int:invoice_id>/pdf/', download_invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:pk>/send/', send_invoice_email, name='send-invoice-email'),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/status/", login_status),
]
