from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Faculty, Student, Course, Section, SectionSubjectFaculty, Subject
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.forms import formset_factory
class TeacherForm(ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__'

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = ['student_number', 'name',  'profile_picture', 'age', 'sex', 'Course', 'Section']

        

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__' 

class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = ['name']

class SectionSubjectFacultyForm(ModelForm):
    class Meta:
        model = SectionSubjectFaculty
        fields = '__all__'  

class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'    

class StudentRegistrationForm(UserCreationForm):
    student_number = forms.CharField(max_length=9)

    class Meta:
        model = User
        fields = ( 'student_number', 'password1', 'password2')

    def clean_student_number(self):
        student_number = self.cleaned_data['student_number']

        # Check if the student number exists in the database
        existing_student = Student.objects.filter(student_number=student_number).first()

        if not existing_student:
            raise ValidationError("Student with this student number does not exist. Please contact the admin to create an account.")

        return student_number

    def save(self, commit=True):
        # Save the user first
        user = super().save(commit=False)

        user.username = self.cleaned_data['student_number']

        # Associate the user with the existing student record
        user.student = Student.objects.get(student_number=self.cleaned_data['student_number'])

        if commit:
            user.save()

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set help_text to an empty string for each field
        for field_name in self.fields:
            self.fields[field_name].help_text = ''

class StudentLoginForm(forms.Form):
    student_number = forms.CharField(max_length=9)
    password = forms.CharField(widget=forms.PasswordInput)

class LikertEvaluationForm(forms.Form):
    rating = forms.ChoiceField(choices=[(1, '1 - Poor'), (2, '2 - Below Average'), (3, '3 - Average'),
                                        (4, '4 - Good'), (5, '5 - Outstanding')],
                               widget=forms.RadioSelect)
    comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

LikertEvaluationFormSet = formset_factory(LikertEvaluationForm, extra=1)