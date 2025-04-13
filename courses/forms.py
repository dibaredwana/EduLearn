from django import forms
from .models import Course, Lesson, Student, Enrollment
from django. contrib. auth. models import User

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'duration', 'thumbnail']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['course', 'title', 'content']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class CourseEnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course', 'student_name', 'student_email']

    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        student_email = cleaned_data.get('student_email')

        if course and student_email:
            if Enrollment.objects.filter(course=course, student_email=student_email).exists():
                raise forms.ValidationError("This email is already enrolled in the selected course.")
        return cleaned_data

class UserUpdateForm(forms. ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {'username': forms.TextInput(attrs = {'class': 'form−control'}),'email': forms.EmailInput(attrs = {'class': 'form−control'}),
}
