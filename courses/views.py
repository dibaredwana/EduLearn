from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Lesson, Student, Enrollment
from .forms import CourseForm, LessonForm  
from django.contrib import messages
from .forms import CourseEnrollmentForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CourseSerializer

def home(request):
    context = {}
    return render(request, "courses/home.html", context)

# View to list all courses
@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, "courses/course_list.html", {"courses": courses})

# View to display course details along with its lessons
@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    student = None
    completed_lessons = []

    # Get student by email (from query param or use auth system later)
    student_email = request.GET.get("student_email")
    if student_email:
        try:
            student = Student.objects.get(email=student_email)
            completed_lessons = student.completed_lessons.all()
        except Student.DoesNotExist:
            student = None
            completed_lessons = []
    else:
        completed_lessons = []  # fallback

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'student': student,
        'completed_lessons': completed_lessons,
    })

# Create Course
@login_required
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Course created successfully!")
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'courses/course_form.html', {'form': form})

# Update Course
@login_required
def course_update(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/course_form.html', {'form': form})

# Delete Course
@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

# Create Lesson
@login_required
def lesson_create(request):
    course_id = request.GET.get('course_id')
    course = None
    if course_id:
        course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            if course:
                lesson.course = course
            lesson.save()
            messages.success(request, "Lesson created successfully!")
            return redirect('course_detail', course_id=course.id if course else None)
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {'form': form, 'course': course})


# Update Lesson
@login_required
def lesson_update(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated successfully!")
            return redirect('course_list')
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {'form': form})

# Delete Lesson
@login_required
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == "POST":
        lesson.delete()
        messages.success(request, "Lesson deleted successfully!")
        return redirect('course_list')
    return render(request, 'courses/lesson_confirm_delete.html', {'lesson': lesson})

@login_required
def enroll_student(request):
    if request.method == 'POST':
        form = CourseEnrollmentForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data['course']
            student_email = form.cleaned_data['student_email']
            student_name = form.cleaned_data['student_name']
            
            # Check for existing enrollment to avoid duplicates.
            existing = Enrollment.objects.filter(course=course, student_email=student_email).first()
            if existing:
                enrollment = existing
                reenrolled = True
            else:
                enrollment = form.save()
                reenrolled = False

            # Ensure a Student object exists and add it to the course.
            student, created = Student.objects.get_or_create(
                email=student_email,
                defaults={'name': student_name}
            )
            # Add student to the course's many-to-many field if not already added.
            if student not in course.students.all():
                course.students.add(student)

            return render(request, 'courses/enrollment_success.html', {
                'student': enrollment,
                'course': course,
                'reenrolled': reenrolled
            })
    else:
        form = CourseEnrollmentForm()
    
    return render(request, 'courses/enroll_student.html', {'form': form})

@login_required
def student_list(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    students = course.students.all()
    return render(request, 'courses/student_list.html', {'course': course, 'students': students})

@login_required
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('/')
    else:
        form = UserCreationForm()  # This handles GET requests

    return render(request, 'courses/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    # Always return an HttpResponse
    return render(request, 'courses/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('/')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
        
    return render(request, 'courses/profile.html', {'form': form})

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'

class CourseCreateView(CreateView):
    model = Course
    fields = ['title', 'description', 'duration', 'thumbnail']
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('course_list')

class CourseListAPI(APIView):
    def get(self, request):
        courses = Course.objects.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailAPI(APIView):
    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
        
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class EnrollStudentAPI(APIView):
    def post(self, request):
        student_email = request.data.get('email')
        course_id = request.data.get('course_id')

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        student, created = Student.objects.get_or_create(email=student_email)
        student.enrolled_courses.add(course)

        return Response({'message': f'{student.email} has been enrolled in {course.title}'})
