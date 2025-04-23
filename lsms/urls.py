from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

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

urlpatterns = [
    path('', include(router.urls)),
]
