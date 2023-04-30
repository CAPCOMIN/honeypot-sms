"""student_management_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.views.generic import RedirectView

import main_app.hod_views
from main_app.EditResultView import EditResultView

from . import hod_views, staff_views, student_views, views
from django.views import static
from django.conf import settings
from django.conf.urls import url
from django.conf.urls import handler400, handler403, handler404, handler500



urlpatterns = [
    path("", views.login_page, name='login_page'),
    url(r'^static/(?P<path>.*)$', static.serve,
        {'document_root': settings.STATIC_ROOT}, name='static'),
    url(r'^media/(?P<path>.*)$', static.serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    path("get_attendance", views.get_attendance, name='get_attendance'),
    path("firebase-messaging-sw.js", views.showFirebaseJS, name='showFirebaseJS'),
    path("doLogin/", views.doLogin, name='user_login'),
    path("logout_user/", views.logout_user, name='user_logout'),
    path("admin/home/", hod_views.admin_home, name='admin_home'),
    path("staff/add", hod_views.add_staff, name='add_staff'),
    path("course/add", hod_views.add_course, name='add_course'),
    path("send_student_notification/", hod_views.send_student_notification,
         name='send_student_notification'),
    path("send_staff_notification/", hod_views.send_staff_notification,
         name='send_staff_notification'),
    path("add_session/", hod_views.add_session, name='add_session'),
    path("admin_notify_student", hod_views.admin_notify_student,
         name='admin_notify_student'),
    path("admin_notify_staff", hod_views.admin_notify_staff,
         name='admin_notify_staff'),
    path("admin_view_profile", hod_views.admin_view_profile,
         name='admin_view_profile'),

    # 计算器（命令注入）
    path("calc/", hod_views.convenient_calc, name='calc'),
    path("fin_calc/", hod_views.calculated),

    # 查询（SQL注入）
    path("search/", hod_views.search, name='search'),
    path("searchresult/", hod_views.searchResult),

    # 合影与回忆照片上传/展示
    path("group_photo/", hod_views.upload_and_show_group_photo, name='group_photo'),

    # 在线教学链接添加
    path("online_teaching_url/add", hod_views.add_online_teaching_url, name='add_online_teaching_url'),

    # 在线教学链接维护
    path("online_teaching_url/manage", hod_views.manage_online_teaching_url, name='manage_online_teaching_url'),

    # 在线教学链接删除
    path("online_teaching_url/delete/<int:id>",
         hod_views.delete_online_teaching_url, name='delete_online_teaching_url'),

    # 学生XML数据解析 (XXE)
    path("stu_data_parser", hod_views.stu_data_parser, name='stu_data_parser'),
    path("stu_data_parser_result/", hod_views.stu_data_parser_result),

    # 学生数据序列化（反序列化漏洞）
    path("serialize", hod_views.serialize_stu_parser, name='serialize'),

    # 添加奖项（CSRF漏洞）
    path("award/add", hod_views.add_award, name='add_award'),

    # 管理奖项
    path("award/manage", hod_views.manage_award, name='manage_award'),

    # 删除奖项
    path("award/delete/<int:id>", hod_views.delete_award, name='delete_award'),

    # 学生准考证号 生成/管理/删除
    path("stu_exam_num", hod_views.stu_exam_num_generate, name='stu_exam_num'),
    path("stu_exam_num/manage", hod_views.manage_stu_exam_num, name='manage_stu_exam_num'),
    path("stu_exam_num/delete/<int:id>", hod_views.delete_en, name='delete_en'),

    path(r'download/<path:filename>', hod_views.download, name="download"),

    path("check_email_availability", hod_views.check_email_availability,
         name="check_email_availability"),
    path("session/manage/", hod_views.manage_session, name='manage_session'),
    path("session/edit/<int:session_id>",
         hod_views.edit_session, name='edit_session'),
    path("student/view/feedback/", hod_views.student_feedback_message,
         name="student_feedback_message", ),
    path("staff/view/feedback/", hod_views.staff_feedback_message,
         name="staff_feedback_message", ),
    path("student/view/leave/", hod_views.view_student_leave,
         name="view_student_leave", ),
    path("staff/view/leave/", hod_views.view_staff_leave, name="view_staff_leave", ),
    path("attendance/view/", hod_views.admin_view_attendance,
         name="admin_view_attendance", ),
    path("attendance/fetch/", hod_views.get_admin_attendance,
         name='get_admin_attendance'),
    path("student/add/", hod_views.add_student, name='add_student'),
    path("subject/add/", hod_views.add_subject, name='add_subject'),
    path("staff/manage/", hod_views.manage_staff, name='manage_staff'),
    path("student/manage/", hod_views.manage_student, name='manage_student'),
    path("course/manage/", hod_views.manage_course, name='manage_course'),
    path("subject/manage/", hod_views.manage_subject, name='manage_subject'),
    path("staff/edit/<int:staff_id>", hod_views.edit_staff, name='edit_staff'),
    path("staff/delete/<int:staff_id>",
         hod_views.delete_staff, name='delete_staff'),

    path("course/delete/<int:course_id>",
         hod_views.delete_course, name='delete_course'),

    path("subject/delete/<int:subject_id>",
         hod_views.delete_subject, name='delete_subject'),

    path("session/delete/<int:session_id>",
         hod_views.delete_session, name='delete_session'),

    path("student/delete/<int:student_id>",
         hod_views.delete_student, name='delete_student'),
    path("student/edit/<int:student_id>",
         hod_views.edit_student, name='edit_student'),
    path("course/edit/<int:course_id>",
         hod_views.edit_course, name='edit_course'),
    path("subject/edit/<int:subject_id>",
         hod_views.edit_subject, name='edit_subject'),

    # Staff
    path("staff/home/", staff_views.staff_home, name='staff_home'),

    # 在线教学链接添加
    path("staff_add_online_teaching_url/add", staff_views.add_online_teaching_url,
         name='staff_add_online_teaching_url'),

    path("staff/apply/leave/", staff_views.staff_apply_leave,
         name='staff_apply_leave'),
    path("staff/feedback/", staff_views.staff_feedback, name='staff_feedback'),
    path("staff/view/profile/", staff_views.staff_view_profile,
         name='staff_view_profile'),
    path("staff/attendance/take/", staff_views.staff_take_attendance,
         name='staff_take_attendance'),
    path("staff/attendance/update/", staff_views.staff_update_attendance,
         name='staff_update_attendance'),
    path("staff/get_students/", staff_views.get_students, name='get_students'),
    path("staff/attendance/fetch/", staff_views.get_student_attendance,
         name='get_student_attendance'),
    path("staff/attendance/save/",
         staff_views.save_attendance, name='save_attendance'),
    path("staff/attendance/update/",
         staff_views.update_attendance, name='update_attendance'),
    path("staff/fcmtoken/", staff_views.staff_fcmtoken, name='staff_fcmtoken'),
    path("staff/view/notification/", staff_views.staff_view_notification,
         name="staff_view_notification"),
    path("staff/result/add/", staff_views.staff_add_result, name='staff_add_result'),
    path("staff/result/edit/", EditResultView.as_view(),
         name='edit_student_result'),
    path('staff/result/fetch/', staff_views.fetch_student_result,
         name='fetch_student_result'),

    # Student
    path("student/home/", student_views.student_home, name='student_home'),
    path("student/view/attendance/", student_views.student_view_attendance,
         name='student_view_attendance'),
    path("student/apply/leave/", student_views.student_apply_leave,
         name='student_apply_leave'),
    path("student/feedback/", student_views.student_feedback,
         name='student_feedback'),
    path("student/view/profile/", student_views.student_view_profile,
         name='student_view_profile'),
    path("student/fcmtoken/", student_views.student_fcmtoken,
         name='student_fcmtoken'),
    path("student/view/notification/", student_views.student_view_notification,
         name="student_view_notification"),
    path('student/view/result/', student_views.student_view_result,
         name='student_view_result'),
    path('favicon.ico', RedirectView.as_view(url='media/honey.png')),
]
handler404 = hod_views.page_not_found