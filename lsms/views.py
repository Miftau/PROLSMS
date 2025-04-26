# Create your views here.
from datetime import timezone

from .serializers import NotificationSerializer
from rest_framework import viewsets
from lsms.models import *
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

User = get_user_model()

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
            # 1) Create inactive user
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # 2) Build activation email
            current_site = get_current_site(request)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_url = reverse('activate', kwargs={'uidb64': uid, 'token': token})
            full_link = f"http://{current_site.domain}{activation_url}"


            subject = 'Activate your LSMS account'
            message = render_to_string(
                'registration/account_activation_email.html',
                {
                    'user': user,
                    'activation_link': full_link,
                    'uid': uid,
                    'token': token,
                }
            )

            # 3) Send it
            email = EmailMessage(subject, message, to=[user.email])
            email.send(fail_silently=False)

            # 4) Show the “check your inbox” page
            return render(request, 'registration/please_confirm.html')

        # If the form isn’t valid, we fall through to re-render it with errors

    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})

def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated! 🎉")
        return redirect('dashboard-redirect')
    else:
        messages.error(request, "Activation link is invalid or has expired.")
        return render(request, 'registration/activation_invalid.html')


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