from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/<int:course_id>/', views.checkout, name='checkout'),
    path('yookassa/webhook/', views.yookassa_webhook, name='yookassa_webhook'),
    path('yookassa/success/', views.yookassa_success, name='yookassa_success'),
    path('yookassa/cancel/', views.yookassa_cancel, name='yookassa_cancel'),
]