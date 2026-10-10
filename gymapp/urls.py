from django.urls import path
from . import views


urlpatterns = [

    # ============================================================
    # PUBLIC PAGES
    # ============================================================

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'about/',
        views.about,
        name='about'
    ),


    # ============================================================
    # AUTHENTICATION
    # ============================================================

    path(
        'admin-login/',
        views.admin_login_view,
        name='admin_login'
    ),

    path(
        'member-login/',
        views.member_login_view,
        name='member_login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),


    # ============================================================
    # DASHBOARDS
    # ============================================================

    path(
        'dashboard/admin/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'dashboard/member/',
        views.member_dashboard,
        name='member_dashboard'
    ),


    # ============================================================
    # MEMBERS
    # ============================================================

    path(
        'members/',
        views.members_list,
        name='members_list'
    ),

    path(
        'members/add/',
        views.add_member,
        name='add_member'
    ),

    path(
        'members/<int:member_id>/',
        views.member_detail,
        name='member_detail'
    ),

    path(
        'members/<int:member_id>/edit/',
        views.edit_member,
        name='edit_member'
    ),

    path(
        'members/<int:member_id>/delete/',
        views.delete_member,
        name='delete_member'
    ),

    path(
        'members/<int:member_id>/deactivate/',
        views.deactivate_member,
        name='deactivate_member'
    ),


    # ============================================================
    # MEMBER PROFILE
    # ============================================================

    path(
        'profile/',
        views.member_profile,
        name='member_profile'
    ),

    path(
        'profile/edit/',
        views.edit_member_profile,
        name='edit_member_profile'
    ),

    path(
        'profile/change-password/',
        views.change_password,
        name='change_password'
    ),


    # ============================================================
    # MEMBERSHIP PLANS
    # ============================================================

    path(
        'plans/',
        views.plans_list,
        name='plans_list'
    ),

    path(
        'plans/add/',
        views.add_plan,
        name='add_plan'
    ),

    path(
        'plans/<int:plan_id>/',
        views.plan_detail,
        name='plan_detail'
    ),

    path(
        'plans/<int:plan_id>/edit/',
        views.edit_plan,
        name='edit_plan'
    ),

    path(
        'plans/<int:plan_id>/delete/',
        views.delete_plan,
        name='delete_plan'
    ),


    # ============================================================
    # PAYMENTS - ADMIN
    # ============================================================

    path(
        'payments/',
        views.payments_list,
        name='payments_list'
    ),

    path(
        'payments/add/',
        views.add_payment,
        name='add_payment'
    ),

    path(
        'payments/<int:payment_id>/',
        views.payment_detail,
        name='payment_detail'
    ),

    path(
        'payments/<int:payment_id>/edit/',
        views.edit_payment,
        name='edit_payment'
    ),

    path(
        'payments/<int:payment_id>/delete/',
        views.delete_payment,
        name='delete_payment'
    ),


    # ============================================================
    # PAYMENTS - MEMBER
    # ============================================================

    path(
        'member/payments/',
        views.member_payments,
        name='member_payments'
    ),


    # ============================================================
    # ATTENDANCE - ADMIN
    # ============================================================

    path(
        'attendance/',
        views.attendance_list,
        name='attendance_list'
    ),

    path(
        'attendance/mark/',
        views.mark_attendance,
        name='mark_attendance'
    ),

    path(
        'attendance/<int:attendance_id>/',
        views.attendance_detail,
        name='attendance_detail'
    ),

    path(
        'attendance/<int:attendance_id>/delete/',
        views.delete_attendance,
        name='delete_attendance'
    ),


    # ============================================================
    # ATTENDANCE - MEMBER
    # ============================================================

    path(
        'member/attendance/',
        views.member_attendance,
        name='member_attendance'
    ),


    # ============================================================
    # TRAINERS
    # ============================================================

    path(
        'trainers/',
        views.trainers_list,
        name='trainers_list'
    ),

    path(
        'trainers/add/',
        views.add_trainer,
        name='add_trainer'
    ),

    path(
        'trainers/<int:trainer_id>/',
        views.trainer_detail,
        name='trainer_detail'
    ),

    path(
        'trainers/<int:trainer_id>/edit/',
        views.edit_trainer,
        name='edit_trainer'
    ),

    path(
        'trainers/<int:trainer_id>/delete/',
        views.delete_trainer,
        name='delete_trainer'
    ),


    # ============================================================
    # EQUIPMENT
    # ============================================================

    path(
        'equipment/',
        views.equipment_list,
        name='equipment_list'
    ),

    path(
        'equipment/add/',
        views.add_equipment,
        name='add_equipment'
    ),

    path(
        'equipment/<int:equipment_id>/',
        views.equipment_detail,
        name='equipment_detail'
    ),

    path(
        'equipment/<int:equipment_id>/edit/',
        views.edit_equipment,
        name='edit_equipment'
    ),

    path(
        'equipment/<int:equipment_id>/delete/',
        views.delete_equipment,
        name='delete_equipment'
    ),

    path(
        'equipment/<int:equipment_id>/toggle/',
        views.toggle_equipment,
        name='toggle_equipment'
    ),


    # ============================================================
    # ENQUIRIES
    # ============================================================

    path(
        'enquiries/',
        views.enquiries_list,
        name='enquiries_list'
    ),

    path(
        'enquiries/<int:enquiry_id>/',
        views.enquiry_detail,
        name='enquiry_detail'
    ),

    path(
        'enquiries/<int:enquiry_id>/status/',
        views.update_enquiry_status,
        name='update_enquiry_status'
    ),

    path(
        'enquiries/<int:enquiry_id>/delete/',
        views.delete_enquiry,
        name='delete_enquiry'
    ),


    # ============================================================
    # WORKOUT PLANS - ADMIN
    # ============================================================

    path(
        'workout-plans/',
        views.workout_plans_list,
        name='workout_plans_list'
    ),

    path(
        'workout-plans/add/',
        views.add_workout_plan,
        name='add_workout_plan'
    ),

    path(
        'workout-plans/<int:plan_id>/delete/',
        views.delete_workout_plan,
        name='delete_workout_plan'
    ),


    # ============================================================
    # WORKOUT PLANS - MEMBER
    # ============================================================

    path(
        'member/workout-plans/',
        views.member_workout_plans,
        name='member_workout_plans'
    ),


    # ============================================================
    # FEEDBACK - MEMBER
    # ============================================================

    path(
        'feedback/',
        views.member_feedback,
        name='member_feedback'
    ),


    # ============================================================
    # FEEDBACK - ADMIN
    # ============================================================

    path(
        'feedback/list/',
        views.feedback_list,
        name='feedback_list'
    ),

    path(
        'feedback/delete/<int:feedback_id>/',
        views.delete_feedback,
        name='delete_feedback'
    ),


    # ============================================================
    # MEMBER MEMBERSHIP
    # ============================================================

    path(
        'member/membership/',
        views.member_membership,
        name='member_membership'
    ),

]