from django.urls import path
from .import views 
from .views import course_create, course_update, course_delete, lesson_create, lesson_update, lesson_delete
from .views import register, user_login, user_logout
from .views import profile
from django.contrib.auth import views as auth_views
from .views import CourseListView, CourseDetailView, CourseCreateView
from .views import CourseListAPI, CourseDetailAPI
from .views import EnrollStudentAPI

urlpatterns = [
    path("", views.home, name="home"),
    path("courses/", views.course_list, name="course_list"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),
    path('create/', course_create, name='course_create'),
    path('<int:course_id>/update/', course_update, name='course_update'),
    path('<int:course_id>/delete/', course_delete, name='course_delete'),
    path('lesson/create/', lesson_create, name='lesson_create'),
    path('lesson/<int:lesson_id>/update/', lesson_update, name='lesson_update'),
    path('lesson/<int:lesson_id>/delete/', lesson_delete, name='lesson_delete'),  
    path('enroll/', views.enroll_student, name='enroll_student'),
    path('courses/<int:course_id>/students/', views.student_list, name='student_list'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path("profile/", profile, name="profile"),
    path('password_change/', 
        auth_views.PasswordChangeView.as_view(template_name='courses/password_change.html'), 
        name='password_change'
    ),
    path('password_change/done/', 
        auth_views.PasswordChangeDoneView.as_view(template_name='courses/password_change_done.html'), 
        name='password_change_done'
    ),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(template_name='courses/password_reset.html'),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='courses/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='courses/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='courses/password_reset_complete.html'),
        name='password_reset_complete'
    ),
    path('courses/list/', CourseListView.as_view(), name='course_list'),
    path('create/', CourseCreateView.as_view(), name='course_create'),
    path('api/courses/', CourseListAPI.as_view(), name='api_course_list'),
    path('api/courses/<int:pk>/', CourseDetailAPI.as_view(), name='api_course_detail'),
    path('api/enroll/', EnrollStudentAPI.as_view(), name='api_enroll_student'),
]

