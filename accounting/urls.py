from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounting_home, name='accounting_home'),
    path('purchaser_create/', views.purchaser_create, name='purchaser_create'),
    path('purchaser_read/', views.purchaser_read, name='purchaser_read'),
    path('purchaser_detail/<int:purchaser_id>', views.purchaser_detail, name='purchaser_detail'),
    path('purchaser_delete/<int:purchaser_id>', views.purchaser_delete, name='purchaser_delete'),
    path('new_purchase/', views.new_purchase, name='new_purchase'),
    path('purchases_read/', views.purchases_read, name='purchases_read'),
    path('make_payment/<int:purchase_id>', views.make_payment, name='make_payment'),
    path('day_purchase/', views.day_purchase, name='day_purchase'),
    path('day_purchase_aux/', views.day_purchase_aux, name='day_purchase_aux'),
    path('sale_history/', views.sale_history, name='sale_history'),
    path('records_delete/<int:record_id>', views.records_delete, name='records_delete'),
    path('payment_stats/', views.payment_stats, name='payment_stats'),
]