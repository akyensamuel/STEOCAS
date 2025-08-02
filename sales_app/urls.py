from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='sales_root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('sales_entry/', views.sales_entry, name='sales_entry'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('print_daily/', views.print_daily_invoices, name='print_daily_invoices'),
    path('print_search/', views.print_search_results, name='print_search_results'),
    path('edit_sale/<int:sale_id>/', views.edit_sale, name='edit_sale'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('edit_invoice/<int:invoice_id>/', views.edit_invoice, name='edit_invoice'),
    path('receipt_print/<int:invoice_id>/', views.invoice_detail, {'print_mode': True}, name='receipt_print'),
    path('api/products/', views.product_autocomplete, name='product_autocomplete'),
    path('products/', views.products_list, name='products'),
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('api/products/', views.product_search_api, name='product_search_api'),
    path('test_debug/', views.test_debug, name='test_debug')
]