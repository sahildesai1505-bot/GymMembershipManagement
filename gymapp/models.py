from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


# ============================================================
# CUSTOM USER
# ============================================================

class User(AbstractUser):
    """
    Custom user model for the gym management system.
    """

    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='MEMBER'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# ============================================================
# MEMBERSHIP PLAN
# ============================================================

class MembershipPlan(models.Model):
    name = models.CharField(
        max_length=100
    )

    fee = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    duration_months = models.PositiveIntegerField()

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f"{self.name} - ${self.fee} "
            f"for {self.duration_months} month(s)"
        )


# ============================================================
# TRAINER
# ============================================================

class Trainer(models.Model):
    name = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=10
    )

    specialization = models.CharField(
        max_length=200
    )

    shift_timing = models.CharField(
        max_length=200
    )

    def __str__(self):
        return f"{self.name} - {self.specialization}"


# ============================================================
# MEMBER PROFILE
# ============================================================

class MemberProfile(models.Model):

    GENDER_CHOICES = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other')
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )

    full_name = models.CharField(
        max_length=100
    )

    mobile = models.CharField(
        max_length=10
    )

    age = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        null=True,
        blank=True
    )

    address = models.TextField(
        null=True,
        blank=True
    )

    join_date = models.DateField(
        default=timezone.now
    )

    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )

    membership_start = models.DateField(
        null=True,
        blank=True
    )

    membership_end = models.DateField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.user.username}"


# ============================================================
# EQUIPMENT
# ============================================================

class Equipment(models.Model):

    name = models.CharField(
        max_length=100
    )

    units = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    purchase_date = models.DateField(
        default=timezone.now
    )

    is_active = models.BooleanField(
        default=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.units} available"


# ============================================================
# PAYMENT
# ============================================================

class Payment(models.Model):

    PAYMENT_MODE_CHOICES = (
        ('CASH', 'Cash'),
        ('ONLINE', 'Online'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('PAID', 'Paid'),
        ('PENDING', 'Pending'),
    )

    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    plan = models.ForeignKey(
        MembershipPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    payment_date = models.DateField(
        default=timezone.now
    )

    mode = models.CharField(
        max_length=50,
        choices=PAYMENT_MODE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES
    )

    notes = models.TextField(
        blank=True
    )

    def __str__(self):
        return (
            f"Payment of ${self.amount} "
            f"by {self.member.full_name} "
            f"on {self.payment_date}"
        )


# ============================================================
# ATTENDANCE
# ============================================================

class Attendance(models.Model):

    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    date = models.DateField(
        default=timezone.now
    )

    time_in = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('member', 'date')

    def __str__(self):
        return (
            f"{self.member.full_name} - "
            f"{self.date} - "
            f"{self.time_in}"
        )


# ============================================================
# ENQUIRY
# ============================================================

class Enquiry(models.Model):

    ENQUIRY_STATUS_CHOICES = (
        ('NEW', 'New'),
        ('SEEN', 'Seen'),
        ('RESOLVED', 'Resolved'),
    )

    name = models.CharField(
        max_length=100
    )

    email = models.EmailField()

    mobile = models.CharField(
        max_length=10
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=ENQUIRY_STATUS_CHOICES,
        default='NEW'
    )

    def __str__(self):
        return (
            f"Enquiry from {self.name} - "
            f"{self.email} - "
            f"Status: {self.status}"
        )


# ============================================================
# WORKOUT PLAN
# ============================================================

class WorkoutPlan(models.Model):

    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )

    title = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    duration_weeks = models.PositiveIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.title} - "
            f"Created at: {self.created_at}"
        )


# ============================================================
# FEEDBACK
# ============================================================

class Feedback(models.Model):

    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Feedback from "
            f"{self.member.full_name} - "
            f"Created at: {self.created_at}"
        )