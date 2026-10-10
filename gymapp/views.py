from datetime import date
import calendar

from django.db import transaction
from django.db.models import Sum, Q
from django.db.models import Sum, Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import (
    User,
    MemberProfile,
    MembershipPlan,
    Trainer,
    Payment,
    Attendance,
    Equipment,
    Enquiry,
    WorkoutPlan,
    Feedback,
)


# ============================================================
# HELPER - ADMIN SECURITY
# ============================================================

def admin_only(request):
    return (
        request.user.is_authenticated
        and getattr(request.user, 'role', None) == 'ADMIN'
    )


# ============================================================
# PUBLIC HOME
# ============================================================

def home(request):

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and mobile and message:

            Enquiry.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                message=message
            )

            messages.success(
                request,
                'Your enquiry has been submitted successfully!'
            )

            return redirect('home')

        messages.error(
            request,
            'Please fill in all fields.'
        )

    return render(request, 'home.html')


# ============================================================
# ABOUT
# ============================================================

def about(request):
    return render(request, 'about.html')


# ============================================================
# ADMIN LOGIN
# ============================================================

def admin_login_view(request):

    if request.user.is_authenticated:

        if getattr(request.user, 'role', None) == 'ADMIN':
            return redirect('admin_dashboard')

        return redirect('member_dashboard')

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:

            messages.error(
                request,
                'Please enter username and password.'
            )

            return render(
                request,
                'admin_login.html'
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if getattr(user, 'role', None) == 'ADMIN':

                login(request, user)

                messages.success(
                    request,
                    f'Welcome back, {user.username}!'
                )

                return redirect('admin_dashboard')

            messages.error(
                request,
                'You do not have administrator permissions.'
            )

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(
        request,
        'admin_login.html'
    )


# ============================================================
# MEMBER LOGIN
# ============================================================

def member_login_view(request):

    if request.user.is_authenticated:

        if getattr(request.user, 'role', None) == 'ADMIN':
            return redirect('admin_dashboard')

        return redirect('member_dashboard')

    if request.method == 'POST':

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:

            messages.error(
                request,
                'Please enter username and password.'
            )

            return render(
                request,
                'member_login.html'
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if getattr(user, 'role', None) == 'MEMBER':

                login(request, user)

                messages.success(
                    request,
                    f'Welcome, {user.username}!'
                )

                return redirect('member_dashboard')

            messages.error(
                request,
                'Please use the administrator login.'
            )

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(
        request,
        'member_login.html'
    )


# ============================================================
# LOGOUT
# ============================================================

@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        'You have been logged out successfully.'
    )

    return redirect('home')


# ============================================================
# ADMIN DASHBOARD
# ============================================================

@login_required
def admin_dashboard(request):

    if not admin_only(request):

        messages.error(
            request,
            'You do not have permission to access the admin dashboard.'
        )

        return redirect('member_dashboard')

    today = timezone.localdate()

    total_members = MemberProfile.objects.count()

    active_members = MemberProfile.objects.filter(
        membership_start__lte=today,
        membership_end__gte=today
    ).count()

    expired_members = MemberProfile.objects.filter(
        membership_end__lt=today
    ).count()

    total_trainers = Trainer.objects.count()

    total_plans = MembershipPlan.objects.count()

    total_equipment = Equipment.objects.count()

    active_equipment = Equipment.objects.filter(
        is_active=True
    ).count()

    today_attendance = Attendance.objects.filter(
        date=today
    ).count()

    total_attendance = Attendance.objects.count()

    total_payments = Payment.objects.count()

    today_revenue = Payment.objects.filter(
        status='PAID',
        payment_date=today
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_revenue = Payment.objects.filter(
        status='PAID'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    pending_payments = Payment.objects.filter(
        status='PENDING'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_enquiries = Enquiry.objects.count()

    new_enquiries = Enquiry.objects.filter(
        status='NEW'
    ).count()

    recent_members = MemberProfile.objects.select_related(
        'user',
        'plan',
        'trainer'
    ).order_by('-id')[:5]

    recent_payments = Payment.objects.select_related(
        'member',
        'plan'
    ).order_by(
        '-payment_date',
        '-id'
    )[:5]

    recent_attendance = Attendance.objects.select_related(
        'member'
    ).order_by(
        '-date',
        '-time_in'
    )[:5]

    recent_enquiries = Enquiry.objects.order_by(
        '-created_at'
    )[:5]

    context = {
        'total_members': total_members,
        'active_members': active_members,
        'expired_members': expired_members,

        'total_trainers': total_trainers,

        'total_plans': total_plans,

        'total_equipment': total_equipment,
        'active_equipment': active_equipment,

        'today_attendance': today_attendance,
        'total_attendance': total_attendance,

        'total_payments': total_payments,
        'today_revenue': today_revenue,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,

        'total_enquiries': total_enquiries,
        'new_enquiries': new_enquiries,

        'recent_members': recent_members,
        'recent_payments': recent_payments,
        'recent_attendance': recent_attendance,
        'recent_enquiries': recent_enquiries,

        'today': today,
    }

    return render(
        request,
        'admin_dashboard.html',
        context
    )


# ============================================================
# MEMBER DASHBOARD
# ============================================================

@login_required
def member_dashboard(request):

    # --------------------------------------------------------
    # ADMIN REDIRECT
    # --------------------------------------------------------

    if getattr(request.user, 'role', None) == 'ADMIN':

        return redirect(
            'admin_dashboard'
        )

    # --------------------------------------------------------
    # MEMBER SECURITY
    # --------------------------------------------------------

    if getattr(request.user, 'role', None) != 'MEMBER':

        messages.error(
            request,
            'You do not have permission to access the member dashboard.'
        )

        return redirect(
            'home'
        )

    # --------------------------------------------------------
    # FIND MEMBER PROFILE
    # --------------------------------------------------------

    try:

        member = MemberProfile.objects.select_related(
            'user',
            'plan',
            'trainer'
        ).get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:

        # ----------------------------------------------------
        # AUTOMATICALLY CREATE PROFILE
        # ----------------------------------------------------

        member = MemberProfile.objects.create(
            user=request.user,
            full_name=request.user.username,
            mobile=''
        )

        messages.info(
            request,
            'Your member profile has been created. Please complete your profile.'
        )

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    today = timezone.localdate()

    # --------------------------------------------------------
    # MEMBERSHIP STATUS
    # --------------------------------------------------------

    if member.membership_end:

        if member.membership_end >= today:
            membership_status = 'Active'
        else:
            membership_status = 'Expired'

    else:

        membership_status = 'No Membership'

    # --------------------------------------------------------
    # PAYMENTS
    # --------------------------------------------------------

    payments = Payment.objects.filter(
        member=member
    ).select_related(
        'plan'
    ).order_by(
        '-payment_date',
        '-id'
    )

    total_paid = payments.filter(
        status='PAID'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # --------------------------------------------------------
    # ATTENDANCE
    # --------------------------------------------------------

    attendance = Attendance.objects.filter(
        member=member
    ).order_by(
        '-date',
        '-time_in'
    )

    total_attendance = attendance.count()

    # --------------------------------------------------------
    # WORKOUT PLANS
    # --------------------------------------------------------

    workout_plans = WorkoutPlan.objects.filter(
        member=member
    ).order_by(
        '-created_at'
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context = {
        'member': member,
        'membership': member,
        'membership_status': membership_status,

        'payments': payments[:5],
        'all_payments': payments,
        'total_paid': total_paid,

        'attendance': attendance[:10],
        'all_attendance': attendance,
        'total_attendance': total_attendance,

        'workout_plans': workout_plans[:5],
        'all_workout_plans': workout_plans,

        'today': today,
    }

    return render(
        request,
        'member_dashboard.html',
        context
    )
# ============================================================
# MEMBER WORKOUT PLANS
# ============================================================

@login_required
def member_workout_plans(request):

    # Admin should go to admin dashboard
    if getattr(request.user, 'role', None) == 'ADMIN':
        return redirect('admin_dashboard')

    # Only members can access this page
    if getattr(request.user, 'role', None) != 'MEMBER':
        messages.error(
            request,
            'You do not have permission to access workout plans.'
        )
        return redirect('home')

    # Find member profile
    try:
        member = MemberProfile.objects.get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:
        messages.warning(
            request,
            'Your member profile has not been created yet.'
        )
        return redirect('member_dashboard')

    # Get all workout plans assigned to this member
    workout_plans = WorkoutPlan.objects.filter(
        member=member
    ).order_by(
        '-created_at'
    )

    context = {
        'member': member,
        'workout_plans': workout_plans,
    }

    return render(
        request,
        'member_workout_plans.html',
        context
    )

# ============================================================
# MEMBERS LIST
# ============================================================

@login_required
def members_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'You do not have permission to access this page.'
        )

        return redirect('member_dashboard')

    today = timezone.localdate()

    members = MemberProfile.objects.select_related(
        'user',
        'plan',
        'trainer'
    ).order_by('-id')

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        members = members.filter(
            Q(full_name__icontains=search) |
            Q(mobile__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search)
        )

    status = request.GET.get(
        'status',
        ''
    ).strip()

    if status == 'active':

        members = members.filter(
            membership_end__gte=today
        )

    elif status == 'expired':

        members = members.filter(
            membership_end__lt=today
        )

    plan_id = request.GET.get(
        'plan',
        ''
    ).strip()

    if plan_id:

        members = members.filter(
            plan_id=plan_id
        )

    plans = MembershipPlan.objects.all().order_by(
        'name'
    )

    context = {
        'members': members,
        'plans': plans,
        'search': search,
        'status': status,
        'selected_plan': plan_id,
        'today': today,
    }

    return render(
        request,
        'members.html',
        context
    )


# ============================================================
# ADD MEMBER
# ============================================================

@login_required
def add_member(request):

    if not admin_only(request):

        messages.error(
            request,
            'You do not have permission to add members.'
        )

        return redirect(
            'member_dashboard'
        )

    plans = MembershipPlan.objects.all().order_by(
        'name'
    )

    trainers = Trainer.objects.all().order_by(
        'name'
    )

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        age = request.POST.get(
            'age'
        ) or None

        gender = request.POST.get(
            'gender'
        ) or None

        address = request.POST.get(
            'address',
            ''
        ).strip()

        plan_id = request.POST.get(
            'plan'
        ) or None

        trainer_id = request.POST.get(
            'trainer'
        ) or None

        membership_start = request.POST.get(
            'membership_start'
        ) or None

        membership_end = request.POST.get(
            'membership_end'
        ) or None

        # ----------------------------------------------------
        # REQUIRED VALIDATION
        # ----------------------------------------------------

        if not username or not password or not full_name or not mobile:

            messages.error(
                request,
                'Username, password, full name and mobile are required.'
            )

            return render(
                request,
                'add_member.html',
                {
                    'plans': plans,
                    'trainers': trainers,
                    'form_data': request.POST,
                }
            )

        # ----------------------------------------------------
        # USERNAME CHECK
        # ----------------------------------------------------

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'This username already exists. Please choose another username.'
            )

            return render(
                request,
                'add_member.html',
                {
                    'plans': plans,
                    'trainers': trainers,
                    'form_data': request.POST,
                }
            )

        # ----------------------------------------------------
        # MOBILE CHECK
        # ----------------------------------------------------

        if not mobile.isdigit() or len(mobile) != 10:

            messages.error(
                request,
                'Mobile number must contain exactly 10 digits.'
            )

            return render(
                request,
                'add_member.html',
                {
                    'plans': plans,
                    'trainers': trainers,
                    'form_data': request.POST,
                }
            )

        # ----------------------------------------------------
        # AGE CHECK
        # ----------------------------------------------------

        if age:

            try:

                age = int(age)

                if age <= 0:
                    raise ValueError

            except ValueError:

                messages.error(
                    request,
                    'Please enter a valid age.'
                )

                return render(
                    request,
                    'add_member.html',
                    {
                        'plans': plans,
                        'trainers': trainers,
                        'form_data': request.POST,
                    }
                )

        # ----------------------------------------------------
        # PLAN
        # ----------------------------------------------------

        plan = None

        if plan_id:

            plan = get_object_or_404(
                MembershipPlan,
                id=plan_id
            )

        # ----------------------------------------------------
        # TRAINER
        # ----------------------------------------------------

        trainer = None

        if trainer_id:

            trainer = get_object_or_404(
                Trainer,
                id=trainer_id
            )

        # ----------------------------------------------------
        # START DATE
        # ----------------------------------------------------

        start_date = None

        if membership_start:

            try:

                start_date = date.fromisoformat(
                    membership_start
                )

            except ValueError:

                messages.error(
                    request,
                    'Invalid membership start date.'
                )

                return render(
                    request,
                    'add_member.html',
                    {
                        'plans': plans,
                        'trainers': trainers,
                        'form_data': request.POST,
                    }
                )

        # ----------------------------------------------------
        # END DATE
        # ----------------------------------------------------

        end_date = None

        if membership_end:

            try:

                end_date = date.fromisoformat(
                    membership_end
                )

            except ValueError:

                messages.error(
                    request,
                    'Invalid membership end date.'
                )

                return render(
                    request,
                    'add_member.html',
                    {
                        'plans': plans,
                        'trainers': trainers,
                        'form_data': request.POST,
                    }
                )

        elif start_date and plan:

            month = (
                start_date.month
                - 1
                + plan.duration_months
            )

            year = (
                start_date.year
                + month // 12
            )

            month = (
                month % 12
                + 1
            )

            day = min(
                start_date.day,
                calendar.monthrange(
                    year,
                    month
                )[1]
            )

            end_date = date(
                year,
                month,
                day
            )

        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='MEMBER'
        )

        # ----------------------------------------------------
        # CREATE MEMBER PROFILE
        # ----------------------------------------------------

        MemberProfile.objects.create(
            user=user,
            full_name=full_name,
            mobile=mobile,
            age=age,
            gender=gender,
            address=address,
            plan=plan,
            trainer=trainer,
            membership_start=start_date,
            membership_end=end_date
        )

        messages.success(
            request,
            f'Member "{full_name}" added successfully.'
        )

        return redirect(
            'members_list'
        )

    return render(
        request,
        'add_member.html',
        {
            'plans': plans,
            'trainers': trainers,
        }
    )


# ============================================================
# MEMBER DETAIL
# ============================================================

@login_required
def member_detail(request, member_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    member = get_object_or_404(
        MemberProfile.objects.select_related(
            'user',
            'plan',
            'trainer'
        ),
        id=member_id
    )

    payments = Payment.objects.filter(
        member=member
    ).select_related(
        'plan'
    ).order_by(
        '-payment_date',
        '-id'
    )

    attendance = Attendance.objects.filter(
        member=member
    ).order_by(
        '-date',
        '-time_in'
    )

    workout_plans = WorkoutPlan.objects.filter(
        member=member
    ).order_by(
        '-created_at'
    )

    feedbacks = Feedback.objects.filter(
        member=member
    ).order_by(
        '-created_at'
    )

    total_paid = payments.filter(
        status='PAID'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_attendance = attendance.count()

    today = timezone.localdate()

    if member.membership_end:

        if member.membership_end >= today:
            membership_status = 'Active'
        else:
            membership_status = 'Expired'

    else:

        membership_status = 'No Membership'

    monthly_attendance = attendance.filter(
        date__year=today.year,
        date__month=today.month
    ).count()

    context = {
        'member': member,
        'payments': payments,
        'attendance': attendance,
        'attendance_history': attendance,

        'total_paid': total_paid,
        'total_attendance': total_attendance,
        'monthly_attendance': monthly_attendance,

        'membership_status': membership_status,

        'workout_plans': workout_plans,
        'feedbacks': feedbacks,
    }

    return render(
        request,
        'member_detail.html',
        context
    )


# ============================================================
# EDIT MEMBER
# ============================================================

@login_required
def edit_member(request, member_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    member = get_object_or_404(
        MemberProfile.objects.select_related(
            'user',
            'plan',
            'trainer'
        ),
        id=member_id
    )

    plans = MembershipPlan.objects.all().order_by(
        'name'
    )

    trainers = Trainer.objects.all().order_by(
        'name'
    )

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        full_name = request.POST.get(
            'full_name',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        age = request.POST.get(
            'age'
        ) or None

        gender = request.POST.get(
            'gender'
        ) or None

        address = request.POST.get(
            'address',
            ''
        ).strip()

        plan_id = request.POST.get(
            'plan'
        ) or None

        trainer_id = request.POST.get(
            'trainer'
        ) or None

        membership_start = request.POST.get(
            'membership_start'
        ) or None

        membership_end = request.POST.get(
            'membership_end'
        ) or None

        password = request.POST.get(
            'password',
            ''
        )

        if not username or not full_name or not mobile:

            messages.error(
                request,
                'Username, full name and mobile are required.'
            )

            return render(
                request,
                'edit_member.html',
                {
                    'member': member,
                    'plans': plans,
                    'trainers': trainers,
                }
            )

        if not mobile.isdigit() or len(mobile) != 10:

            messages.error(
                request,
                'Mobile number must contain exactly 10 digits.'
            )

            return render(
                request,
                'edit_member.html',
                {
                    'member': member,
                    'plans': plans,
                    'trainers': trainers,
                }
            )

        if User.objects.filter(
            username=username
        ).exclude(
            id=member.user.id
        ).exists():

            messages.error(
                request,
                'This username is already being used.'
            )

            return render(
                request,
                'edit_member.html',
                {
                    'member': member,
                    'plans': plans,
                    'trainers': trainers,
                }
            )

        # ----------------------------------------------------
        # USER
        # ----------------------------------------------------

        member.user.username = username
        member.user.email = email

        if password:
            member.user.set_password(password)

        member.user.save()

        # ----------------------------------------------------
        # PLAN
        # ----------------------------------------------------

        plan = None

        if plan_id:

            plan = get_object_or_404(
                MembershipPlan,
                id=plan_id
            )

        # ----------------------------------------------------
        # TRAINER
        # ----------------------------------------------------

        trainer = None

        if trainer_id:

            trainer = get_object_or_404(
                Trainer,
                id=trainer_id
            )

        # ----------------------------------------------------
        # DATES
        # ----------------------------------------------------

        start_date = None
        end_date = None

        if membership_start:

            try:

                start_date = date.fromisoformat(
                    membership_start
                )

            except ValueError:

                messages.error(
                    request,
                    'Invalid membership start date.'
                )

                return render(
                    request,
                    'edit_member.html',
                    {
                        'member': member,
                        'plans': plans,
                        'trainers': trainers,
                    }
                )

        if membership_end:

            try:

                end_date = date.fromisoformat(
                    membership_end
                )

            except ValueError:

                messages.error(
                    request,
                    'Invalid membership end date.'
                )

                return render(
                    request,
                    'edit_member.html',
                    {
                        'member': member,
                        'plans': plans,
                        'trainers': trainers,
                    }
                )

        # ----------------------------------------------------
        # UPDATE PROFILE
        # ----------------------------------------------------

        member.full_name = full_name
        member.mobile = mobile
        member.age = age
        member.gender = gender
        member.address = address
        member.plan = plan
        member.trainer = trainer
        member.membership_start = start_date
        member.membership_end = end_date

        member.save()

        messages.success(
            request,
            f'Member "{full_name}" updated successfully.'
        )

        return redirect(
            'member_detail',
            member_id=member.id
        )

    return render(
        request,
        'edit_member.html',
        {
            'member': member,
            'plans': plans,
            'trainers': trainers,
        }
    )

# ============================================================
# DELETE MEMBER
# ============================================================

@login_required
def delete_member(request, member_id):

    # Only admins can delete members
    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    # Get member
    member = get_object_or_404(
        MemberProfile,
        id=member_id
    )

    if request.method == 'POST':

        member_name = member.full_name

        try:

            with transaction.atomic():

                # ------------------------------------------------
                # DELETE MEMBER'S RELATED RECORDS FIRST
                # ------------------------------------------------

                Payment.objects.filter(
                    member=member
                ).delete()

                Attendance.objects.filter(
                    member=member
                ).delete()

                WorkoutPlan.objects.filter(
                    member=member
                ).delete()

                Feedback.objects.filter(
                    member=member
                ).delete()

                # ------------------------------------------------
                # DELETE MEMBER PROFILE
                # ------------------------------------------------

                user = member.user

                member.delete()

                # ------------------------------------------------
                # DELETE LOGIN USER
                # ------------------------------------------------

                user.delete()

            messages.success(
                request,
                f'Member "{member_name}" deleted successfully.'
            )

            return redirect(
                'members_list'
            )

        except Exception as e:

            messages.error(
                request,
                f'Unable to delete member: {e}'
            )

            return redirect(
                'members_list'
            )

    # GET request → confirmation page
    return render(
        request,
        'delete_member.html',
        {
            'member': member
        }
    )

# ============================================================
# DEACTIVATE MEMBER
# ============================================================

@login_required
def deactivate_member(request, member_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    member = get_object_or_404(
        MemberProfile,
        id=member_id
    )

    member.user.is_active = False
    member.user.save()

    messages.success(
        request,
        f'Member "{member.full_name}" has been deactivated.'
    )

    return redirect(
        'members_list'
    )


# ============================================================
# MEMBERSHIP PLANS - LIST
# ============================================================

@login_required
def plans_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    plans = MembershipPlan.objects.all().order_by(
        'name'
    )

    return render(
        request,
        'plans.html',
        {
            'plans': plans
        }
    )


# ============================================================
# ADD PLAN
# ============================================================

@login_required
def add_plan(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        fee = request.POST.get(
            'fee'
        )

        duration_months = request.POST.get(
            'duration_months'
        )

        description = request.POST.get(
            'description',
            ''
        ).strip()

        if not name or not fee or not duration_months:

            messages.error(
                request,
                'Please fill in all required fields.'
            )

            return render(
                request,
                'add_plan.html'
            )

        MembershipPlan.objects.create(
            name=name,
            fee=fee,
            duration_months=duration_months,
            description=description
        )

        messages.success(
            request,
            f'Membership plan "{name}" created successfully.'
        )

        return redirect(
            'plans_list'
        )

    return render(
        request,
        'add_plan.html'
    )


# ============================================================
# PLAN DETAIL
# ============================================================

@login_required
def plan_detail(request, plan_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    plan = get_object_or_404(
        MembershipPlan,
        id=plan_id
    )

    members = MemberProfile.objects.filter(
        plan=plan
    ).select_related(
        'user',
        'trainer'
    ).order_by(
        'full_name'
    )

    payments = Payment.objects.filter(
        plan=plan
    ).select_related(
        'member'
    ).order_by(
        '-payment_date'
    )

    return render(
        request,
        'plan_detail.html',
        {
            'plan': plan,
            'members': members,
            'payments': payments,
        }
    )


# ============================================================
# EDIT PLAN
# ============================================================

@login_required
def edit_plan(request, plan_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    plan = get_object_or_404(
        MembershipPlan,
        id=plan_id
    )

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        fee = request.POST.get(
            'fee'
        )

        duration_months = request.POST.get(
            'duration_months'
        )

        description = request.POST.get(
            'description',
            ''
        ).strip()

        if not name or not fee or not duration_months:

            messages.error(
                request,
                'Please fill in all required fields.'
            )

            return render(
                request,
                'edit_plan.html',
                {
                    'plan': plan
                }
            )

        plan.name = name
        plan.fee = fee
        plan.duration_months = duration_months
        plan.description = description

        plan.save()

        messages.success(
            request,
            f'Membership plan "{name}" updated successfully.'
        )

        return redirect(
            'plans_list'
        )

    return render(
        request,
        'edit_plan.html',
        {
            'plan': plan
        }
    )


# ============================================================
# DELETE PLAN
# ============================================================

@login_required
def delete_plan(request, plan_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    plan = get_object_or_404(
        MembershipPlan,
        id=plan_id
    )

    if request.method == 'POST':

        plan_name = plan.name

        plan.delete()

        messages.success(
            request,
            f'Membership plan "{plan_name}" deleted successfully.'
        )

        return redirect(
            'plans_list'
        )

    return render(
        request,
        'delete_plan.html',
        {
            'plan': plan
        }
    )


# ============================================================
# PAYMENTS LIST
# ============================================================

@login_required
def payments_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    payments = Payment.objects.select_related(
        'member',
        'plan'
    ).order_by(
        '-payment_date',
        '-id'
    )

    total_revenue = Payment.objects.filter(
        status='PAID'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    pending_amount = Payment.objects.filter(
        status='PENDING'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    return render(
        request,
        'payments.html',
        {
            'payments': payments,
            'total_revenue': total_revenue,
            'pending_amount': pending_amount,
        }
    )


# ============================================================
# ADD PAYMENT
# ============================================================

@login_required
def add_payment(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    members = MemberProfile.objects.select_related(
        'user',
        'plan'
    ).order_by(
        'full_name'
    )

    plans = MembershipPlan.objects.all().order_by(
        'name'
    )

    if request.method == 'POST':

        member_id = request.POST.get('member')
        plan_id = request.POST.get('plan')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        mode = request.POST.get('mode')
        status = request.POST.get('status')
        notes = request.POST.get(
            'notes',
            ''
        ).strip()

        if not member_id or not amount or not payment_date or not mode or not status:

            messages.error(
                request,
                'Please fill all required fields.'
            )

        else:

            try:

                member = MemberProfile.objects.get(
                    id=member_id
                )

                plan = None

                if plan_id:

                    plan = MembershipPlan.objects.get(
                        id=plan_id
                    )

                Payment.objects.create(
                    member=member,
                    plan=plan,
                    amount=amount,
                    payment_date=payment_date,
                    mode=mode,
                    status=status,
                    notes=notes
                )

                messages.success(
                    request,
                    'Payment added successfully.'
                )

                return redirect(
                    'payments_list'
                )

            except MemberProfile.DoesNotExist:

                messages.error(
                    request,
                    'Selected member does not exist.'
                )

            except MembershipPlan.DoesNotExist:

                messages.error(
                    request,
                    'Selected membership plan does not exist.'
                )

    return render(
        request,
        'add_payment.html',
        {
            'members': members,
            'plans': plans,
        }
    )


# ============================================================
# PAYMENT DETAIL
# ============================================================

@login_required
def payment_detail(request, payment_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    payment = get_object_or_404(
        Payment.objects.select_related(
            'member',
            'plan'
        ),
        id=payment_id
    )

    return render(
        request,
        'payment_detail.html',
        {
            'payment': payment
        }
    )


# ============================================================
# EDIT PAYMENT
# ============================================================

@login_required
def edit_payment(request, payment_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    members = MemberProfile.objects.all().order_by(
        'full_name'
    )

    plans = MembershipPlan.objects.all().order_by(
        'name'
    )

    if request.method == 'POST':

        member_id = request.POST.get('member')
        plan_id = request.POST.get('plan')
        amount = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        mode = request.POST.get('mode')
        status = request.POST.get('status')
        notes = request.POST.get(
            'notes',
            ''
        ).strip()

        if not member_id or not amount or not payment_date or not mode or not status:

            messages.error(
                request,
                'Please fill all required fields.'
            )

        else:

            try:

                payment.member = MemberProfile.objects.get(
                    id=member_id
                )

                if plan_id:

                    payment.plan = MembershipPlan.objects.get(
                        id=plan_id
                    )

                else:

                    payment.plan = None

                payment.amount = amount
                payment.payment_date = payment_date
                payment.mode = mode
                payment.status = status
                payment.notes = notes

                payment.save()

                messages.success(
                    request,
                    'Payment updated successfully.'
                )

                return redirect(
                    'payments_list'
                )

            except MemberProfile.DoesNotExist:

                messages.error(
                    request,
                    'Selected member does not exist.'
                )

            except MembershipPlan.DoesNotExist:

                messages.error(
                    request,
                    'Selected plan does not exist.'
                )

    return render(
        request,
        'edit_payment.html',
        {
            'payment': payment,
            'members': members,
            'plans': plans,
        }
    )


# ============================================================
# DELETE PAYMENT
# ============================================================

@login_required
def delete_payment(request, payment_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    payment = get_object_or_404(
        Payment,
        id=payment_id
    )

    if request.method == 'POST':

        payment.delete()

        messages.success(
            request,
            'Payment deleted successfully.'
        )

        return redirect(
            'payments_list'
        )

    return render(
        request,
        'delete_payment.html',
        {
            'payment': payment
        }
    )


# ============================================================
# ATTENDANCE LIST
# ============================================================

@login_required
def attendance_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    attendances = Attendance.objects.select_related(
        'member',
        'member__user',
        'member__plan',
        'member__trainer'
    ).order_by(
        '-date',
        '-time_in'
    )

    search = request.GET.get(
        'search',
        ''
    ).strip()

    if search:

        attendances = attendances.filter(
            Q(member__full_name__icontains=search) |
            Q(member__mobile__icontains=search) |
            Q(member__user__username__icontains=search)
        )

    selected_date = request.GET.get(
        'date',
        ''
    ).strip()

    if selected_date:

        attendances = attendances.filter(
            date=selected_date
        )

    today = timezone.localdate()

    today_attendance = Attendance.objects.filter(
        date=today
    ).count()

    total_members = MemberProfile.objects.count()

    current_month_attendance = Attendance.objects.filter(
        date__year=today.year,
        date__month=today.month
    ).count()

    return render(
        request,
        'attendance.html',
        {
            'attendances': attendances,
            'today_attendance': today_attendance,
            'total_members': total_members,
            'current_month_attendance': current_month_attendance,
            'search': search,
            'selected_date': selected_date,
            'today': today,
        }
    )

# ============================================================
# MEMBER ATTENDANCE
# ============================================================

@login_required
def member_attendance(request):

    # Admin should use admin attendance page
    if getattr(request.user, 'role', None) == 'ADMIN':
        return redirect('attendance_list')

    # Only members can access this page
    if getattr(request.user, 'role', None) != 'MEMBER':
        messages.error(
            request,
            'You do not have permission to access attendance.'
        )
        return redirect('home')

    # Find logged-in member profile
    try:
        member = MemberProfile.objects.get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:

        messages.error(
            request,
            'Your member profile has not been created yet.'
        )

        return redirect('member_dashboard')

    # Get only this member's attendance
    attendances = Attendance.objects.filter(
        member=member
    ).order_by(
        '-date',
        '-time_in'
    )

    # Total attendance
    total_attendance = attendances.count()

    # Today's attendance
    today = timezone.localdate()

    today_attendance = attendances.filter(
        date=today
    ).count()

    # Current month attendance
    current_month_attendance = attendances.filter(
        date__year=today.year,
        date__month=today.month
    ).count()

    return render(
        request,
        'member_attendance.html',
        {
            'member': member,
            'attendances': attendances,
            'total_attendance': total_attendance,
            'today_attendance': today_attendance,
            'current_month_attendance': current_month_attendance,
            'today': today,
        }
    )
# ============================================================
# MARK ATTENDANCE
# ============================================================

@login_required
def mark_attendance(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    members = MemberProfile.objects.select_related(
        'user',
        'plan'
    ).order_by(
        'full_name'
    )

    if request.method == 'POST':

        member_id = request.POST.get('member')

        if not member_id:

            messages.error(
                request,
                'Please select a member.'
            )

            return redirect(
                'mark_attendance'
            )

        member = get_object_or_404(
            MemberProfile,
            id=member_id
        )

        today = timezone.localdate()

        attendance, created = Attendance.objects.get_or_create(
            member=member,
            date=today,
            defaults={
                'time_in': timezone.localtime().time()
            }
        )

        if created:

            messages.success(
                request,
                f'Attendance marked for {member.full_name}.'
            )

        else:

            messages.warning(
                request,
                f'{member.full_name} is already marked present today.'
            )

        return redirect(
            'attendance_list'
        )

    return render(
        request,
        'mark_attendance.html',
        {
            'members': members
        }
    )


# ============================================================
# ATTENDANCE DETAIL
# ============================================================

@login_required
def attendance_detail(request, attendance_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    attendance = get_object_or_404(
        Attendance.objects.select_related(
            'member',
            'member__user',
            'member__plan',
            'member__trainer'
        ),
        id=attendance_id
    )

    return render(
        request,
        'attendance_detail.html',
        {
            'attendance': attendance
        }
    )


# ============================================================
# DELETE ATTENDANCE
# ============================================================

@login_required
def delete_attendance(request, attendance_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    attendance = get_object_or_404(
        Attendance,
        id=attendance_id
    )

    if request.method == 'POST':

        member_name = attendance.member.full_name

        attendance.delete()

        messages.success(
            request,
            f'Attendance record for {member_name} was deleted successfully.'
        )

        return redirect(
            'attendance_list'
        )

    return redirect(
        'attendance_detail',
        attendance_id=attendance.id
    )


# ============================================================
# TRAINERS LIST
# ============================================================

@login_required
def trainers_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    trainers = Trainer.objects.all().order_by(
        'name'
    )

    return render(
        request,
        'trainers.html',
        {
            'trainers': trainers
        }
    )


# ============================================================
# ADD TRAINER
# ============================================================

@login_required
def add_trainer(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        specialization = request.POST.get(
            'specialization',
            ''
        ).strip()

        shift_timing = request.POST.get(
            'shift_timing',
            ''
        ).strip()

        if not name or not mobile or not specialization or not shift_timing:

            messages.error(
                request,
                'Please fill in all fields.'
            )

            return render(
                request,
                'add_trainer.html'
            )

        Trainer.objects.create(
            name=name,
            mobile=mobile,
            specialization=specialization,
            shift_timing=shift_timing
        )

        messages.success(
            request,
            f'Trainer "{name}" added successfully.'
        )

        return redirect(
            'trainers_list'
        )

    return render(
        request,
        'add_trainer.html'
    )


# ============================================================
# TRAINER DETAIL
# ============================================================

@login_required
def trainer_detail(request, trainer_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    trainer = get_object_or_404(
        Trainer,
        id=trainer_id
    )

    assigned_members = MemberProfile.objects.filter(
        trainer=trainer
    ).select_related(
        'user',
        'plan'
    ).order_by(
        'full_name'
    )

    return render(
        request,
        'trainer_detail.html',
        {
            'trainer': trainer,
            'assigned_members': assigned_members,
            'members': assigned_members,
            'total_members': assigned_members.count(),
        }
    )


# ============================================================
# EDIT TRAINER
# ============================================================

@login_required
def edit_trainer(request, trainer_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    trainer = get_object_or_404(
        Trainer,
        id=trainer_id
    )

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        specialization = request.POST.get(
            'specialization',
            ''
        ).strip()

        shift_timing = request.POST.get(
            'shift_timing',
            ''
        ).strip()

        if not name or not mobile or not specialization or not shift_timing:

            messages.error(
                request,
                'Please fill in all fields.'
            )

            return render(
                request,
                'edit_trainer.html',
                {
                    'trainer': trainer
                }
            )

        trainer.name = name
        trainer.mobile = mobile
        trainer.specialization = specialization
        trainer.shift_timing = shift_timing

        trainer.save()

        messages.success(
            request,
            f'Trainer "{name}" updated successfully.'
        )

        return redirect(
            'trainer_detail',
            trainer_id=trainer.id
        )

    return render(
        request,
        'edit_trainer.html',
        {
            'trainer': trainer
        }
    )


# ============================================================
# DELETE TRAINER
# ============================================================

@login_required
def delete_trainer(request, trainer_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    trainer = get_object_or_404(
        Trainer,
        id=trainer_id
    )

    if request.method == 'POST':

        trainer_name = trainer.name

        trainer.delete()

        messages.success(
            request,
            f'Trainer "{trainer_name}" deleted successfully.'
        )

        return redirect(
            'trainers_list'
        )

    return render(
        request,
        'delete_trainer.html',
        {
            'trainer': trainer
        }
    )


# ============================================================
# EQUIPMENT LIST
# ============================================================

@login_required
def equipment_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    equipments = Equipment.objects.all().order_by(
        'name'
    )

    return render(
        request,
        'equipment.html',
        {
            'equipments': equipments,
            'equipment': equipments,
        }
    )


# ============================================================
# ADD EQUIPMENT
# ============================================================

@login_required
def add_equipment(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        units = request.POST.get(
            'units'
        )

        price = request.POST.get(
            'price'
        )

        purchase_date = request.POST.get(
            'purchase_date'
        ) or None

        if not name or not units or not price:

            messages.error(
                request,
                'Name, units and price are required.'
            )

            return render(
                request,
                'add_equipment.html'
            )

        Equipment.objects.create(
            name=name,
            units=units,
            price=price,
            purchase_date=purchase_date
        )

        messages.success(
            request,
            f'Equipment "{name}" added successfully.'
        )

        return redirect(
            'equipment_list'
        )

    return render(
        request,
        'add_equipment.html'
    )


# ============================================================
# EQUIPMENT DETAIL
# ============================================================

@login_required
def equipment_detail(request, equipment_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    equipment = get_object_or_404(
        Equipment,
        id=equipment_id
    )

    return render(
        request,
        'equipment_detail.html',
        {
            'equipment': equipment
        }
    )


# ============================================================
# EDIT EQUIPMENT
# ============================================================

@login_required
def edit_equipment(request, equipment_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    equipment = get_object_or_404(
        Equipment,
        id=equipment_id
    )

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        units = request.POST.get(
            'units'
        )

        price = request.POST.get(
            'price'
        )

        purchase_date = request.POST.get(
            'purchase_date'
        ) or None

        if not name or not units or not price:

            messages.error(
                request,
                'Name, units and price are required.'
            )

            return render(
                request,
                'edit_equipment.html',
                {
                    'equipment': equipment
                }
            )

        equipment.name = name
        equipment.units = units
        equipment.price = price
        equipment.purchase_date = purchase_date

        equipment.save()

        messages.success(
            request,
            f'Equipment "{name}" updated successfully.'
        )

        return redirect(
            'equipment_detail',
            equipment_id=equipment.id
        )

    return render(
        request,
        'edit_equipment.html',
        {
            'equipment': equipment
        }
    )


# ============================================================
# DELETE EQUIPMENT
# ============================================================

@login_required
def delete_equipment(request, equipment_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    equipment = get_object_or_404(
        Equipment,
        id=equipment_id
    )

    if request.method == 'POST':

        equipment_name = equipment.name

        equipment.delete()

        messages.success(
            request,
            f'Equipment "{equipment_name}" deleted successfully.'
        )

        return redirect(
            'equipment_list'
        )

    return render(
        request,
        'delete_equipment.html',
        {
            'equipment': equipment
        }
    )


# ============================================================
# TOGGLE EQUIPMENT
# ============================================================

@login_required
def toggle_equipment(request, equipment_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    equipment = get_object_or_404(
        Equipment,
        id=equipment_id
    )

    if request.method == 'POST':

        equipment.is_active = not equipment.is_active

        equipment.save(
            update_fields=[
                'is_active'
            ]
        )

        if equipment.is_active:

            messages.success(
                request,
                f'"{equipment.name}" has been activated.'
            )

        else:

            messages.warning(
                request,
                f'"{equipment.name}" has been deactivated.'
            )

    return redirect(
        'equipment_list'
    )


# ============================================================
# ENQUIRIES LIST
# ============================================================

@login_required
def enquiries_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    enquiries = Enquiry.objects.all().order_by(
        '-created_at'
    )

    new_count = enquiries.filter(
        status='NEW'
    ).count()

    seen_count = enquiries.filter(
        status='SEEN'
    ).count()

    resolved_count = enquiries.filter(
        status='RESOLVED'
    ).count()

    return render(
        request,
        'enquiries.html',
        {
            'enquiries': enquiries,
            'new_count': new_count,
            'seen_count': seen_count,
            'resolved_count': resolved_count,
        }
    )


# ============================================================
# ENQUIRY DETAIL
# ============================================================

@login_required
def enquiry_detail(request, enquiry_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    if enquiry.status == 'NEW':

        enquiry.status = 'SEEN'

        enquiry.save(
            update_fields=[
                'status'
            ]
        )

    return render(
        request,
        'enquiry_detail.html',
        {
            'enquiry': enquiry
        }
    )


# ============================================================
# UPDATE ENQUIRY STATUS
# ============================================================

@login_required
def update_enquiry_status(request, enquiry_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    if request.method == 'POST':

        status = request.POST.get(
            'status'
        )

        valid_statuses = [
            choice[0]
            for choice in Enquiry.ENQUIRY_STATUS_CHOICES
        ]

        if status in valid_statuses:

            enquiry.status = status

            enquiry.save(
                update_fields=[
                    'status'
                ]
            )

            messages.success(
                request,
                'Enquiry status updated successfully.'
            )

        else:

            messages.error(
                request,
                'Invalid enquiry status.'
            )

    return redirect(
        'enquiry_detail',
        enquiry_id=enquiry.id
    )


# ============================================================
# DELETE ENQUIRY
# ============================================================

@login_required
def delete_enquiry(request, enquiry_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    enquiry = get_object_or_404(
        Enquiry,
        id=enquiry_id
    )

    if request.method == 'POST':

        enquiry_name = enquiry.name

        enquiry.delete()

        messages.success(
            request,
            f'Enquiry from "{enquiry_name}" deleted successfully.'
        )

        return redirect(
            'enquiries_list'
        )

    return render(
        request,
        'delete_enquiry.html',
        {
            'enquiry': enquiry
        }
    )


# ============================================================
# WORKOUT PLANS LIST
# ============================================================

@login_required
def workout_plans_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    workout_plans = WorkoutPlan.objects.select_related(
        'member'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'workout_plans.html',
        {
            'workout_plans': workout_plans
        }
    )


# ============================================================
# ADD WORKOUT PLAN
# ============================================================

@login_required
def add_workout_plan(request):

    if not admin_only(request):

        messages.error(
            request,
            'Only administrators can add workout plans.'
        )

        return redirect(
            'member_dashboard'
        )

    members = MemberProfile.objects.all().order_by(
        'full_name'
    )

    if request.method == 'POST':

        member_id = request.POST.get(
            'member'
        )

        title = request.POST.get(
            'title',
            ''
        ).strip()

        description = request.POST.get(
            'description',
            ''
        ).strip()

        duration_weeks = request.POST.get(
            'duration_weeks'
        )

        if not member_id or not title or not duration_weeks:

            messages.error(
                request,
                'Please fill in all required fields.'
            )

            return render(
                request,
                'add_workout_plan.html',
                {
                    'members': members
                }
            )

        try:

            duration_weeks = int(
                duration_weeks
            )

            if duration_weeks <= 0:
                raise ValueError

            member = get_object_or_404(
                MemberProfile,
                id=member_id
            )

            WorkoutPlan.objects.create(
                member=member,
                title=title,
                description=description,
                duration_weeks=duration_weeks
            )

            messages.success(
                request,
                'Workout plan added successfully.'
            )

            return redirect(
                'workout_plans_list'
            )

        except ValueError:

            messages.error(
                request,
                'Duration must be a valid positive number of weeks.'
            )

    return render(
        request,
        'add_workout_plan.html',
        {
            'members': members
        }
    )


# ============================================================
# DELETE WORKOUT PLAN
# ============================================================

@login_required
def delete_workout_plan(request, plan_id):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    workout_plan = get_object_or_404(
        WorkoutPlan,
        id=plan_id
    )

    if request.method == 'POST':

        plan_title = getattr(
            workout_plan,
            'title',
            'Workout Plan'
        )

        workout_plan.delete()

        messages.success(
            request,
            f'Workout plan "{plan_title}" deleted successfully.'
        )

        return redirect(
            'workout_plans_list'
        )

    return render(
        request,
        'delete_workout_plan.html',
        {
            'workout_plan': workout_plan
        }
    )


# ============================================================
# FEEDBACK LIST
# ============================================================

@login_required
def feedback_list(request):

    if not admin_only(request):

        messages.error(
            request,
            'Admin access required.'
        )

        return redirect('member_dashboard')

    feedbacks = Feedback.objects.select_related(
        'member'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'feedback.html',
        {
            'feedbacks': feedbacks
        }
    )


# ============================================================
# ADD FEEDBACK
# ============================================================

@login_required
def add_feedback(request):

    if getattr(request.user, 'role', None) != 'MEMBER':

        if getattr(request.user, 'role', None) == 'ADMIN':

            return redirect(
                'admin_dashboard'
            )

        messages.error(
            request,
            'Member access required.'
        )

        return redirect(
            'home'
        )

    member = get_object_or_404(
        MemberProfile,
        user=request.user
    )

    if request.method == 'POST':

        feedback_text = request.POST.get(
            'feedback',
            ''
        ).strip()

        if not feedback_text:

            messages.error(
                request,
                'Please enter your feedback.'
            )

            return render(
                request,
                'add_feedback.html'
            )

        Feedback.objects.create(
            member=member,
            feedback=feedback_text
        )

        messages.success(
            request,
            'Feedback submitted successfully.'
        )

        return redirect(
            'member_dashboard'
        )

    return render(
        request,
        'add_feedback.html'
    )


# ============================================================
# MEMBER PROFILE
# ============================================================

@login_required
def member_profile(request):

    if getattr(request.user, 'role', None) != 'MEMBER':

        messages.error(
            request,
            'Only members can access their profile.'
        )

        return redirect(
            'admin_dashboard'
        )

    try:

        member = MemberProfile.objects.select_related(
            'user',
            'plan',
            'trainer'
        ).get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:

        # Create missing profile automatically
        member = MemberProfile.objects.create(
            user=request.user,
            full_name=request.user.username,
            mobile=''
        )

        messages.info(
            request,
            'Your member profile has been created. Please complete your profile.'
        )

    context = {
        'member': member,
        'today': timezone.localdate(),
    }

    return render(
        request,
        'member_profile.html',
        context
    )
# ============================================================
# MEMBER - EDIT PROFILE
# ============================================================

@login_required
def edit_member_profile(request):

    # Only members can edit their profile
    if getattr(request.user, 'role', None) != 'MEMBER':

        messages.error(
            request,
            'Only members can edit their profile.'
        )

        if getattr(request.user, 'role', None) == 'ADMIN':
            return redirect('admin_dashboard')

        return redirect('home')

    # Find member profile
    try:

        member = MemberProfile.objects.get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:

        messages.error(
            request,
            'Your member profile has not been created yet.'
        )

        return redirect('member_dashboard')

    # Handle form submission
    if request.method == 'POST':

        member.mobile = request.POST.get(
            'mobile',
            ''
        ).strip()

        member.age = request.POST.get(
            'age'
        ) or None

        member.gender = request.POST.get(
            'gender',
            ''
        ).strip()

        member.address = request.POST.get(
            'address',
            ''
        ).strip()

        member.save()

        messages.success(
            request,
            'Your profile has been updated successfully.'
        )

        return redirect('member_profile')

    context = {
        'member': member,
    }

    return render(
        request,
        'edit_member_profile.html',
        context
    )
# ============================================================
# MEMBER - CHANGE PASSWORD
# ============================================================

@login_required
def change_member_password(request):

    # Only members can change their password
    if getattr(request.user, 'role', None) != 'MEMBER':

        messages.error(
            request,
            'Only members can change their password.'
        )

        if getattr(request.user, 'role', None) == 'ADMIN':
            return redirect('admin_dashboard')

        return redirect('home')

    # Create password change form
    if request.method == 'POST':

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            # Keep the member logged in
            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                'Your password has been changed successfully.'
            )

            return redirect('member_profile')

    else:

        form = PasswordChangeForm(
            request.user
        )

    context = {
        'form': form,
    }

    return render(
        request,
        'change_member_password.html',
        context
    )
# ============================================================
# MEMBER WORKOUT PLANS
# ============================================================

@login_required
def member_workout_plans(request):

    # Admin users should use the admin workout plan page
    if getattr(request.user, 'role', None) == 'ADMIN':
        return redirect('workout_plans_list')

    # Only members can access this page
    if getattr(request.user, 'role', None) != 'MEMBER':
        messages.error(
            request,
            'You do not have permission to access this page.'
        )
        return redirect('home')

    # Find the logged-in member profile
    try:
        member = MemberProfile.objects.select_related(
            'user',
            'plan',
            'trainer'
        ).get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:

        messages.warning(
            request,
            'Your member profile has not been created yet.'
        )

        return redirect('member_dashboard')

    # Get ONLY this member's workout plans
    workout_plans = WorkoutPlan.objects.filter(
        member=member
    ).order_by(
        '-created_at'
    )

    context = {
        'member': member,
        'workout_plans': workout_plans,
    }

    return render(
        request,
        'member_workout_plans.html',
        context
    )

    # ============================================================
# ADD WORKOUT PLAN
# ============================================================

@login_required
def add_workout_plan(request):

    # Only admin can add workout plans
    if getattr(request.user, 'role', None) != 'ADMIN':
        messages.error(
            request,
            'Admin access required.'
        )
        return redirect('member_dashboard')

    members = MemberProfile.objects.select_related(
        'user'
    ).order_by(
        'full_name'
    )

    if request.method == 'POST':

        member_id = request.POST.get('member')
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        duration_weeks = request.POST.get('duration_weeks')

        # Validation
        if not member_id or not title or not duration_weeks:
            messages.error(
                request,
                'Please fill in all required fields.'
            )

            return render(
                request,
                'add_workout_plan.html',
                {
                    'members': members,
                    'form_data': request.POST
                }
            )

        try:
            member = MemberProfile.objects.get(
                id=member_id
            )

            duration_weeks = int(duration_weeks)

            if duration_weeks <= 0:
                raise ValueError

        except (
            MemberProfile.DoesNotExist,
            ValueError,
            TypeError
        ):
            messages.error(
                request,
                'Please enter valid workout plan details.'
            )

            return render(
                request,
                'add_workout_plan.html',
                {
                    'members': members,
                    'form_data': request.POST
                }
            )

        # Create workout plan
        WorkoutPlan.objects.create(
            member=member,
            title=title,
            description=description,
            duration_weeks=duration_weeks
        )

        messages.success(
            request,
            f'Workout plan "{title}" assigned successfully.'
        )

        return redirect('workout_plans_list')

    return render(
        request,
        'add_workout_plan.html',
        {
            'members': members
        }
    )

# ============================================================
# ADMIN WORKOUT PLANS
# ============================================================

@login_required
def workout_plans_list(request):

    # Only admin can access this page
    if getattr(request.user, 'role', None) != 'ADMIN':
        messages.error(
            request,
            'Admin access required.'
        )
        return redirect('member_dashboard')

    workout_plans = WorkoutPlan.objects.select_related(
        'member',
        'member__user'
    ).order_by(
        '-created_at'
    )

    context = {
        'workout_plans': workout_plans,
    }

    return render(
        request,
        'workout_plans_list.html',
        context
    )
# ============================================================
# MEMBER FEEDBACK
# ============================================================

@login_required
def member_feedback(request):

    # Only members can submit feedback
    if getattr(request.user, 'role', None) != 'MEMBER':

        messages.error(
            request,
            'Only members can submit feedback.'
        )

        if getattr(request.user, 'role', None) == 'ADMIN':
            return redirect('admin_dashboard')

        return redirect('home')

    # Get the member profile
    try:

        member = MemberProfile.objects.get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:

        messages.error(
            request,
            'Your member profile has not been created yet.'
        )

        return redirect('member_dashboard')

    # Submit feedback
    if request.method == 'POST':

        message = request.POST.get(
            'message',
            ''
        ).strip()

        if not message:

            messages.error(
                request,
                'Please enter your feedback.'

            )

        else:

            Feedback.objects.create(
                member=member,
                message=message
            )

            messages.success(
                request,
                'Your feedback has been submitted successfully.'
            )

            return redirect('member_feedback')

    # Get previous feedback
    feedbacks = Feedback.objects.filter(
        member=member
    ).order_by(
        '-created_at'
    )

    context = {
        'member': member,
        'feedbacks': feedbacks,
    }

    return render(
        request,
        'member_feedback.html',
        context
    )

# ============================================================
# ADMIN - FEEDBACK MANAGEMENT
# ============================================================

@login_required
def feedback_list(request):

    # Only admins can access
    if getattr(request.user, 'role', None) != 'ADMIN':

        messages.error(
            request,
            'Admin access required.'
        )

        if getattr(request.user, 'role', None) == 'MEMBER':
            return redirect('member_dashboard')

        return redirect('home')

    # Get all feedback
    feedbacks = Feedback.objects.select_related(
        'member',
        'member__user'
    ).order_by(
        '-created_at'
    )

    context = {
        'feedbacks': feedbacks,
    }

    return render(
        request,
        'feedback_list.html',
        context
    )


# ============================================================
# ADMIN - DELETE FEEDBACK
# ============================================================

@login_required
def delete_feedback(request, feedback_id):

    # Only admins can delete
    if getattr(request.user, 'role', None) != 'ADMIN':

        messages.error(
            request,
            'Admin access required.'
        )

        if getattr(request.user, 'role', None) == 'MEMBER':
            return redirect('member_dashboard')

        return redirect('home')

    # Only allow POST deletion
    if request.method != 'POST':

        messages.error(
            request,
            'Invalid request.'
        )

        return redirect('feedback_list')

    feedback = get_object_or_404(
        Feedback,
        id=feedback_id
    )

    feedback.delete()

    messages.success(
        request,
        'Feedback deleted successfully.'
    )

    return redirect('feedback_list')

    # ============================================================
# MEMBER ATTENDANCE
# ============================================================

@login_required
def member_attendance(request):

    # Admin should use admin attendance page
    if getattr(request.user, 'role', None) == 'ADMIN':
        return redirect('attendance_list')

    # Only members can access this page
    if getattr(request.user, 'role', None) != 'MEMBER':
        messages.error(
            request,
            'You do not have permission to access attendance.'
        )
        return redirect('home')

    # Find member profile
    try:
        member = MemberProfile.objects.get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:
        messages.warning(
            request,
            'Your member profile has not been created yet.'
        )
        return redirect('member_dashboard')

    # Get only this member's attendance
    attendance = Attendance.objects.filter(
        member=member
    ).order_by(
        '-date',
        '-time_in'
    )

    context = {
        'member': member,
        'attendance': attendance,
        'total_attendance': attendance.count(),
    }

    return render(
        request,
        'member_attendance.html',
        context
    )
# ============================================================
# MEMBER PAYMENTS
# ============================================================

@login_required
def member_payments(request):

    # Admin should use the admin payments page
    if getattr(request.user, 'role', None) == 'ADMIN':
        return redirect('payments_list')

    # Only members can access this page
    if getattr(request.user, 'role', None) != 'MEMBER':
        messages.error(
            request,
            'You do not have permission to access payments.'
        )
        return redirect('home')

    # Find member profile
    try:
        member = MemberProfile.objects.get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:
        messages.warning(
            request,
            'Your member profile has not been created yet.'
        )
        return redirect('member_dashboard')

    # Get only this member's payments
    payments = Payment.objects.filter(
        member=member
    ).select_related(
        'plan'
    ).order_by(
        '-payment_date',
        '-id'
    )

    # Calculate total paid amount
    total_paid = payments.filter(
        status='PAID'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'member': member,
        'payments': payments,
        'total_paid': total_paid,
    }

    return render(
        request,
        'member_payments.html',
        context
    )
# ============================================================
# MEMBER MEMBERSHIP
# ============================================================

@login_required
def member_membership(request):

    # Only members can access this page
    if getattr(request.user, 'role', None) != 'MEMBER':

        messages.error(
            request,
            'Only members can access the membership page.'
        )

        if getattr(request.user, 'role', None) == 'ADMIN':
            return redirect('admin_dashboard')

        return redirect('home')

    # Find logged-in member profile
    try:

        member = MemberProfile.objects.get(
            user=request.user
        )

    except MemberProfile.DoesNotExist:

        messages.warning(
            request,
            'Your member profile has not been created yet.'
        )

        return redirect('member_dashboard')

    # Current date
    today = timezone.localdate()

    # Default membership information
    membership_status = 'No Membership'
    days_remaining = 0

    # Check membership
    if member.plan and member.membership_start and member.membership_end:

        if member.membership_end >= today:

            membership_status = 'Active'

            days_remaining = (
                member.membership_end - today
            ).days

        else:

            membership_status = 'Expired'

            days_remaining = 0

    # Get member payments
    payments = Payment.objects.filter(
        member=member
    ).order_by(
        '-payment_date'
    )

    # Total amount paid
    total_paid = payments.filter(
        status='PAID'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {

        'member': member,

        'membership_status': membership_status,

        'days_remaining': days_remaining,

        'today': today,

        'payments': payments,

        'total_paid': total_paid,

    }

    return render(
        request,
        'member_membership.html',
        context
    )
@login_required
def change_password(request):

    if request.method == "POST":

        form = PasswordChangeForm(
            request.user,
            request.POST
        )

        if form.is_valid():

            user = form.save()

            # Keep the user logged in after changing password
            update_session_auth_hash(
                request,
                user
            )

            messages.success(
                request,
                "Your password has been changed successfully."
            )

            return redirect("member_profile")

    else:

        form = PasswordChangeForm(
            request.user
        )

    return render(
        request,
        "change_password.html",
        {
            "form": form
        }
    )