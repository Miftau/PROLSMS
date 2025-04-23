from rest_framework import serializers
from .models import *

# === Reuse ===
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'institution']

# === Institutions & Profiles ===
class ClientInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientInstitution
        fields = '__all__'

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = StudentProfile
        fields = '__all__'

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = TeacherProfile
        fields = '__all__'

class ParentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = ParentProfile
        fields = '__all__'

# === Academics ===
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class LessonContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContent
        fields = '__all__'

# === Attendance ===
class AttendanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

# === Communication ===
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

# === Finance ===
class FeeInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeInvoice
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentInstallment
        fields = '__all__'

class PaymentPlanSerializer(serializers.ModelSerializer):
    installments = PaymentInstallmentSerializer(many=True, read_only=True)

    class Meta:
        model = PaymentPlan
        fields = '__all__'

# === Support System ===
class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = '__all__'

class TicketResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketResponse
        fields = '__all__'
