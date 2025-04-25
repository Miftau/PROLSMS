# Create your views here.
from .serializers import NotificationSerializer
from rest_framework import viewsets
from .models import *
from .serializers import *
from .permissions import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Avg, Sum, Count
from .forms import SignUpForm, ResendActivationEmailForm
from django.contrib.auth import login, get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .util.token import account_activation_token
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect



# === Core System ===
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]

class ClientInstitutionViewSet(viewsets.ModelViewSet):
    queryset = ClientInstitution.objects.all()
    serializer_class = ClientInstitutionSerializer
    permission_classes = [IsClientAdmin]

# === Profiles ===
class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    permission_classes = [IsTeacher, IsClientAdmin, IsParent, IsStudent]

class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsTeacher, IsClientAdmin]

class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsTeacher, IsClientAdmin, IsParent]

# === Academic ===
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsTeacher, IsClientAdmin]

class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsTeacher, IsClientAdmin]

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsTeacher]  # or whatever you use

    def perform_create(self, serializer):
        assignment = serializer.save()
        classroom = assignment.classroom
        for student in classroom.students.all():
            Notification.objects.create(
                recipient=student.user,
                message=f"New assignment: '{assignment.title}' for {classroom.name}",
                url=f"/student/assignments/{assignment.id}/"
            )
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"user_{User.id}",
            {
                "type": "send_notification",
                "data": {
                    "message": "New assignment posted",
                    "url": "/student/assignments/123/",
                },
            },
        )


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsTeacher, IsClientAdmin, IsParent, IsStudent]
    
    def perform_create(self, serializer):
        submission = serializer.save()
        assignment = submission.assignment
        teacher_user = assignment.classroom.teacher.user

        Notification.objects.create(
            recipient=teacher_user,
            message=f"{submission.student.user.get_full_name()} submitted '{assignment.title}'",
            url=f"/teacher/assignments/{assignment.id}/submissions/"
        )

class LessonContentViewSet(viewsets.ModelViewSet):
    queryset = LessonContent.objects.all()
    serializer_class = LessonContentSerializer
    permission_classes = [IsTeacher, IsClientAdmin, IsParent, IsStudent]

# === Attendance ===
class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsTeacher, IsClientAdmin, IsParent, IsStudent]

# === Communication ===
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsTeacher, IsClientAdmin, IsParent, IsStudent]

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [IsTeacher, IsClientAdmin, IsParent, IsStudent]
    
    def perform_create(self, serializer):
        announcement = serializer.save()
        users = announcement.visible_to.all()
        for user in users:
            Notification.objects.create(
                recipient=user,
                message=f"New Announcement: {announcement.title}",
                url=f"/announcements/{announcement.id}/"
            )


# === Finance ===
class FeeInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FeeInvoice.objects.all()
    serializer_class = FeeInvoiceSerializer
    permission_classes = [IsClientAdmin, IsParent, IsStudent]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsClientAdmin, IsParent, IsStudent]

class PaymentPlanViewSet(viewsets.ModelViewSet):
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer
    permission_classes = [IsClientAdmin, IsParent, IsStudent]

class PaymentInstallmentViewSet(viewsets.ModelViewSet):
    queryset = PaymentInstallment.objects.all()
    serializer_class = PaymentInstallmentSerializer
    permission_classes = [IsClientAdmin, IsParent, IsStudent]

# === Support System ===
class SupportTicketViewSet(viewsets.ModelViewSet):
    queryset = SupportTicket.objects.all()
    serializer_class = SupportTicketSerializer
    permission_classes = [IsClientAdmin, IsParent, IsStudent]

class TicketResponseViewSet(viewsets.ModelViewSet):
    queryset = TicketResponse.objects.all()
    serializer_class = TicketResponseSerializer
    permission_classes = [IsClientAdmin, IsParent, IsStudent]
    
class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

class StudentResponseViewSet(viewsets.ModelViewSet):
    queryset = StudentResponse.objects.all()
    serializer_class = StudentResponseSerializer
    permission_classes = [IsAuthenticated]

class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]

class ClientSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = ClientSubscription.objects.all()
    serializer_class = ClientSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

def can_add_student(user):
    institution = user.institution
    subscription = ClientSubscription.objects.filter(client_institution=institution, is_active=True).latest('start_date')
    current_students = StudentProfile.objects.filter(user__institution=institution).count()
    return current_students < subscription.plan.max_students

def index_view(request):
    return render(request, 'index.html')

@login_required
def teacher_dashboard(request):
    user = request.user
    classrooms = Classroom.objects.filter(teacher__user=user)
    assignments = Assignment.objects.filter(classroom__in=classrooms)
    grades = Grade.objects.filter(assignment__in=assignments)

    # Aggregate performance data
    labels = []
    data = []
    for classroom in classrooms:
        class_grades = grades.filter(assignment__classroom=classroom)
        avg_score = class_grades.aggregate(avg=Avg('score'))['avg'] or 0
        labels.append(classroom.name)
        data.append(round(avg_score, 2))

    context = {
        'classroom_count': classrooms.count(),
        'assignment_count': assignments.count(),
        'submission_count': grades.count(),
        'performance_data': {
            'labels': labels,
            'data': data
        }
    }

    return render(request, 'lsms/teacher_dashboard.html', context)

@login_required
def parent_dashboard(request):
    parent = ParentProfile.objects.get(user=request.user)
    children_data = []

    for child in parent.studentprofile_set.all():
        grades = Grade.objects.filter(student=child).order_by('submitted_at')
        attendance = AttendanceRecord.objects.filter(student=child)
        invoices = FeeInvoice.objects.filter(student=child, paid=False)

        labels = [g.submitted_at.strftime('%b %d') for g in grades]
        data = [round(g.score, 2) for g in grades]

        children_data.append({
            'user': child.user,
            'avg_score': round(grades.aggregate(avg=Avg('score'))['avg'] or 0, 2),
            'attended_days': attendance.filter(status='present').count(),
            'total_days': attendance.count(),
            'outstanding_fees': invoices.aggregate(total=Sum('amount'))['total'] or 0,
            'grade_labels': labels,
            'grade_data': data
        })

    return render(request, 'lsms/parent_dashboard.html', {'children': children_data})

@login_required
def student_dashboard(request):
    student = StudentProfile.objects.get(user=request.user)

    grades = Grade.objects.filter(student=student).order_by('submitted_at')
    assignments = Assignment.objects.filter(classroom__students=student, due_date__gte=timezone.now()).order_by('due_date')[:5]
    announcements = Announcement.objects.filter(visible_to=student.user).order_by('-created_at')[:5]

    labels = [g.submitted_at.strftime('%b %d') for g in grades]
    data = [round(g.score, 2) for g in grades]

    return render(request, 'lsms/student_dashboard.html', {
        'assignments': assignments,
        'announcements': announcements,
        'grade_labels': labels,
        'grade_data': data,
    })

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # Send activation email
        current_site = get_current_site(request)
        mail_subject = 'Activate your LSMS account'
        message = render_to_string('registration/account_activation_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        email = EmailMessage(mail_subject, message, to=[user.email])
        email.send()

        return render(request, 'registration/please_confirm.html')  # Page to tell user to check email
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('dashboard-redirect')
    else:
        return render(request, 'registration/activation_invalid.html')
    
    User = get_user_model()

def resend_activation_email(request):
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if not user.is_active:
                    current_site = get_current_site(request)
                    mail_subject = 'Resend: Activate your LSMS account'
                    message = render_to_string('registration/account_activation_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': account_activation_token.make_token(user),
                    })
                    user.email_user(mail_subject, message)
                    messages.success(request, 'A new activation link has been sent to your email.')
                else:
                    messages.info(request, 'This account is already active.')
            except User.DoesNotExist:
                messages.error(request, 'No user found with this email.')
            return HttpResponseRedirect(reverse('resend-activation'))
    else:
        form = ResendActivationEmailForm()

    return render(request, 'registration/resend_activation.html', {'form': form})

@login_required
def dashboard_redirect(request):
    role = request.user.role
    if role == 'teacher':
        return redirect('teacher-dashboard')
    elif role == 'student':
        return redirect('student-dashboard')
    elif role == 'parent':
        return redirect('parent-dashboard')
    elif role == 'client_admin':
        return redirect('lsms:dashboard-view')  # assuming this is for client admin
    else:
        return redirect('index')