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
	path('search/', views.search, name='search'),
	path('invoices/', views.invoices.as_view(), name='invoices'),
	path('products/', views.products.as_view(), name='products'),
]