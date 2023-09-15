from django.contrib import admin
from django.urls import path, include
from . import views
from .views import PostUpdateView, PostListView, UserPostListView

urlpatterns=[
	path('', PostListView.as_view(), name='home'),
	path('post/new/', views.create_post, name='post-create'),
	path('invoice/new/', views.save_invoice, name='save_invoice'),
	path('invoice/<int:pk>/', views.post_detail, name='post-detail'),
	path('invoice/<int:pk>/update/', PostUpdateView.as_view(), name='invoice-update'),
	path('product/<int:pk>/delete/', views.product_delete, name='product-delete'),
	path('product/<int:pk>/update/', views.product_update, name='product-update'),
	path('stock/new/', views.newStockItem, name='newStockItem'),
	path('stock-sell/new/', views.newSellStockItem, name='newSellStockItem'),
	path('stock-item/<int:pk>/delete/', views.stock_item_delete, name='stock_item_delete'),
	path('sold-item/<int:pk>/delete/', views.sell_stock_item_delete, name='sell_stock_item_delete'),
	path('product/<int:pk>/update/', views.product_update, name='product-update'),
	path('search/', views.search, name='search'),
	path('invoices/', views.invoices.as_view(), name='invoices'),
	path('products/', views.products.as_view(), name='products'),
	path('dashboard/', views.dashboard.as_view(), name='dashboard'),
    path('dashboard/table_a/', views.dashboard.as_view(), {'table': 'a'}, name='table_a'),
    path('dashboard/table_b/', views.dashboard.as_view(), {'table': 'b'}, name='table_b'),
]