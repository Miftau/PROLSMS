from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('client_admin', 'Client Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    institution = models.ForeignKey('ClientInstitution', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)

class ClientInstitution(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    theme_color = models.CharField(max_length=7, default='#000000')  # e.g. #ff0000
    subscription_tier = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('ParentProfile', on_delete=models.SET_NULL, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    academic_history = models.TextField(blank=True)

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qualifications = models.TextField(blank=True)

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20)

class Course(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(ClientInstitution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.name}"

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True)
    students = models.ManyToManyField(StudentProfile)
    schedule = models.TextField(blank=True)  # JSON or formatted schedule text

    def __str__(self):
        return f"{self.name} ({self.course.code})"

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Grade(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class LessonContent(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True)
    content = models.TextField()  # Can later be extended to rich text or files
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AttendanceRecord(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'classroom', 'date')

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=255)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    visible_to = models.ManyToManyField(User, related_name='announcements')
    scheduled_for = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class FeeInvoice(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    description = models.TextField(blank=True)
    issued_date = models.DateField(auto_now_add=True)
    paid = models.BooleanField(default=False)

class Payment(models.Model):
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=50)  # e.g., bank, online, cash

    def __str__(self):
        return f"Payment of {self.amount_paid} for {self.invoice.id}"

class PaymentPlan(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    number_of_installments = models.PositiveIntegerField()
    start_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} for {self.student.user.get_full_name()}"

class PaymentInstallment(models.Model):
    plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='installments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    invoice = models.OneToOneField(FeeInvoice, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Installment of {self.amount} due {self.due_date}"

class SupportTicket(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    )
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_tickets')
    subject = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.status}"

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    responded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response by {self.responder.username} on {self.responded_at}"

class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.title

class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=[('multiple_choice', 'Multiple Choice'), ('true_false', 'True/False')])

    def __str__(self):
        return self.question_text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text

class StudentResponse(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    answer_text = models.TextField(null=True, blank=True)  # For open-ended questions

    def __str__(self):
        return f"Response by {self.student.user.username} for {self.question}"

class SubscriptionPlan(models.Model):
    objects = None
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.PositiveIntegerField()  # e.g. 1 month, 3 months
    features = models.TextField()  # Features included in the plan
    
    max_students = models.PositiveIntegerField(default=100)
    max_teachers = models.PositiveIntegerField(default=10)
    max_parents = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.name

class ClientSubscription(models.Model):
    objects = None
    client_institution = models.ForeignKey(ClientInstitution, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.client_institution.name} - {self.plan.name}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.message[:40]}"



