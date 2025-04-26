from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *
from lsms.subscription_view import (
    UpgradeSubscriptionView, CancelSubscriptionView, RenewSubscriptionView
)
from django.contrib.auth import views as auth_views
from .subscription_view import InitializeFlutterwavePaymentView, flutterwave_callback_view
from .dashboard_views import SubscriptionDashboardView
from .client_views import dashboard_view, subscribe_view
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin



urlpatterns = [
    path('', index_view, name='index'),
    path('accounts/signup/', signup_view, name='signup'),
    path('api/', include('lsms.api_urls')),
    path('admin/', admin.site.urls),
    path(
        'activate/<uidb64>/<token>/',
        activate_account,
        name='activate'
    ),
]


urlpatterns += [
    path('subscriptions/upgrade/', UpgradeSubscriptionView.as_view(), name='upgrade-subscription'),
    path('subscriptions/cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    path('subscriptions/renew/', RenewSubscriptionView.as_view(), name='renew-subscription'),
]

urlpatterns += [
    path('subscriptions/initiate-flutterwave/', InitializeFlutterwavePaymentView.as_view(), name='initiate-flutterwave'),
    path('flutterwave/callback/', flutterwave_callback_view, name='flutterwave-callback'),
]

urlpatterns += [
    path('dashboard/subscription/', SubscriptionDashboardView.as_view(), name='subscription-dashboard'),
    path('dashboard/', dashboard_redirect, name='dashboard-redirect'),

]

app_name = 'lsms'

urlpatterns += [
    path('client/dashboard/', dashboard_view, name='dashboard-view'),
    path('client/subscribe/', subscribe_view, name='subscribe-view'),
]
urlpatterns += [
    path('dashboard/teacher/', teacher_dashboard, name='teacher-dashboard'),
    path('dashboard/parent/', parent_dashboard, name='parent-dashboard'),
    path('dashboard/student/', student_dashboard, name='student-dashboard'),
    path('accounts/signup/', signup_view, name='signup'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('accounts/resend-activation/', resend_activation_email, name='resend-activation'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)