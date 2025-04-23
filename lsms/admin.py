# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, ClientInstitution,
    StudentProfile, TeacherProfile, ParentProfile,
    Course, Classroom, Assignment, Grade, LessonContent,
    AttendanceRecord, Message, Announcement,
    FeeInvoice, Payment, PaymentPlan, PaymentInstallment,
    SupportTicket, TicketResponse
)

# ========== USER & INSTITUTION ==========
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'institution', 'is_active', 'is_staff')
    list_filter = ('role', 'institution', 'is_active')
    search_fields = ('username', 'email')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Institution & Role', {'fields': ('role', 'institution')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

@admin.register(ClientInstitution)
class ClientInstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'subscription_tier', 'theme_color')
    search_fields = ('name',)

# ========== PROFILES ==========
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'parent', 'date_of_birth')
    search_fields = ('user__username', 'parent__user__username')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'qualifications')

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'contact_number')

# ========== ACADEMIC ==========
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'institution')
    search_fields = ('code', 'name')
    list_filter = ('institution',)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'course', 'teacher')
    filter_horizontal = ('students',)
    search_fields = ('name', 'course__name', 'teacher__user__username')

class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'classroom', 'due_date')
    inlines = [GradeInline]
    list_filter = ('classroom',)

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'score', 'submitted_at')

@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'teacher', 'uploaded_at')
    list_filter = ('course', 'teacher')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'classroom', 'date', 'status')
    list_filter = ('classroom', 'date', 'status')

# ========== COMMUNICATION ==========
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'receiver', 'sent_at', 'read')
    search_fields = ('subject', 'sender__username', 'receiver__username')
    list_filter = ('read',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'scheduled_for', 'created_at')
    filter_horizontal = ('visible_to',)

# ========== FINANCE ==========
class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ('student', 'amount', 'due_date', 'paid')
    list_filter = ('paid',)
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount_paid', 'payment_date', 'method')

class PaymentInstallmentInline(admin.TabularInline):
    model = PaymentInstallment
    extra = 0

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'total_amount', 'number_of_installments', 'start_date')
    inlines = [PaymentInstallmentInline]

@admin.register(PaymentInstallment)
class PaymentInstallmentAdmin(admin.ModelAdmin):
    list_display = ('plan', 'amount', 'due_date', 'paid')

# ========== SUPPORT ==========
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'submitted_by', 'priority', 'status', 'submitted_at')
    list_filter = ('priority', 'status')
    search_fields = ('subject', 'submitted_by__username')

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'responder', 'responded_at')

