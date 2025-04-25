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

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'institutions', ClientInstitutionViewSet)
router.register(r'students', StudentProfileViewSet)
router.register(r'teachers', TeacherProfileViewSet)
router.register(r'parents', ParentProfileViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'lesson-content', LessonContentViewSet)
router.register(r'attendance', AttendanceRecordViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'announcements', AnnouncementViewSet)
router.register(r'fee-invoices', FeeInvoiceViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'payment-plans', PaymentPlanViewSet)
router.register(r'payment-installments', PaymentInstallmentViewSet)
router.register(r'support-tickets', SupportTicketViewSet)
router.register(r'ticket-responses', TicketResponseViewSet)
router.register(r'exams', ExamViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'student-responses', StudentResponseViewSet)
router.register(r'subscription-plans', SubscriptionPlanViewSet)
router.register(r'client-subscriptions', ClientSubscriptionViewSet)


urlpatterns = [
    path('', include(router.urls)),
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
    path('', index_view, name='index'),

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

