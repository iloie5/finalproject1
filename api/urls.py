from django.urls import path
from . import views
from . import auth_views

urlpatterns = [
    # Product endpoints
    path('products/', views.ProductListCreateAPIView.as_view()),
    path('products/info/', views.ProductInfoAPIView.as_view()),
    path('products/<int:product_id>/', views.ProductDetailAPIView.as_view()),
    
    # Order endpoints
    path('orders/', views.OrderListAPIView.as_view()),
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='order-create'),
    path('orders/<uuid:order_id>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('orders/<uuid:order_id>/items/', views.OrderItemCreateAPIView.as_view(), name='order-item-create'),
    path('order-items/<int:pk>/', views.OrderItemDetailAPIView.as_view(), name='order-item-detail'),
    path('user-orders/', views.UserOrderListAPIView.as_view(), name='user-orders'),
    
    # Authentication endpoints
    path('auth/register/', auth_views.UserRegistrationView.as_view(), name='register'),
    path('auth/verify-email/', auth_views.verify_email, name='verify-email'),
    path('auth/resend-verification/', auth_views.resend_verification, name='resend-verification'),
    path('auth/password-reset-request/', auth_views.password_reset_request, name='password-reset-request'),
    path('auth/password-reset-confirm/', auth_views.password_reset_confirm, name='password-reset-confirm'),
    path('auth/profile/', auth_views.user_profile, name='user-profile'),
    path('auth/change-password/', auth_views.change_password, name='change-password'),
]
