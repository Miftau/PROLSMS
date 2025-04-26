from rest_framework.routers import DefaultRouter
from django.urls import path
from .api_views import UserViewSet, NotificationListView
from .subscription_view import InitializeFlutterwavePaymentView, flutterwave_callback_view
from .dashboard_views import SubscriptionDashboardView


router = DefaultRouter()
router.register('users', UserViewSet, basename='user')

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('subscriptions/initiate-flutterwave/', InitializeFlutterwavePaymentView.as_view(), name='initiate-flutterwave'),
    path('dashboard/subscription/', SubscriptionDashboardView.as_view(), name='subscription-dashboard'),
    path('flutterwave/callback/', flutterwave_callback_view, name='flutterwave-callback'),
]

urlpatterns += router.urls
