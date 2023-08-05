from django.contrib import admin
from django.urls import path, include
from . import views
from .views import PostUpdateView, PostListView, UserPostListView

urlpatterns=[
	path('', PostListView.as_view(), name='home'),
	path('post/new/', views.create_post, name='post-create'),
	path('invoice/new/', views.save_invoice, name='save_invoice'),
	path('invoice/<int:pk>/', views.post_detail, name='post-detail'),
	path('like/', views.like, name='post-like'),
	path('invoice/<int:pk>/update/', PostUpdateView.as_view(), name='invoice-update'),
	path('post/<int:pk>/delete/', views.post_delete, name='post-delete'),
	path('search/', views.search, name='search'),
	path('user_posts/<str:username>', UserPostListView.as_view(), name='user-posts'),
	path('explore/', views.explore_posts.as_view(), name='explore'),
	path('invoices/', views.invoices.as_view(), name='invoices'),
]