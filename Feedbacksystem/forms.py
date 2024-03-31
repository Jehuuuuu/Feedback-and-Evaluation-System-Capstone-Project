from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Faculty, Student, Course, Section, SectionSubjectFaculty, Subject, EvaluationStatus, Department
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

class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'     

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

class EvaluationStatusForm(ModelForm):
    class Meta:
        model = EvaluationStatus
        fields = '__all__'

class StudentRegistrationForm(UserCreationForm):
    student_number = forms.CharField(max_length=9)

    class Meta:
        model = User
        fields = ('student_number', 'password1', 'password2')

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

class FacultyRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ( 'email', 'password1', 'password2')

    def clean_faculty_email(self):
        email = self.cleaned_data['email']

        # Check if the student number exists in the database
        existing_student = Faculty.objects.filter(email=email).first()

        if not existing_student:
            raise ValidationError("Faculy with this email does not exist. Please contact the admin to create an account.")

        return email

    def save(self, commit=True):
        # Save the user first
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']

        # Associate the user with the faculty record
        user.student = Faculty.objects.get(email=self.cleaned_data['email'])

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

class FacultyLoginForm(forms.Form):
    email = forms.EmailField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class LikertEvaluationForm(forms.Form):
    command_and_knowledge_of_the_subject = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
                                 
    depth_of_mastery = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    practice_in_respective_discipline = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    up_to_date_knowledge = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    integrates_subject_to_practical_circumstances = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    organizes_the_subject_matter = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    provides_orientation_on_course_content = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    efforts_of_class_preparation = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    summarizes_main_points = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    monitors_online_class = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))

    holds_interest_of_students = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    provides_relevant_feedback = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    encourages_participation = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    shows_enthusiasm = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    shows_sense_of_humor = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))

    teaching_methods = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    flexible_learning_strategies = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    student_engagement = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    clear_examples = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    focused_on_objectives = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))

    starts_with_motivating_activities = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    speaks_in_clear_and_audible_manner = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    uses_appropriate_medium_of_instruction = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    establishes_online_classroom_environment = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    observes_proper_classroom_etiquette = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))

    uses_time_wisely = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    gives_ample_time_for_students_to_prepare = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    updates_the_students_of_their_progress = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    demonstrates_leadership_and_professionalism = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    understands_possible_distractions = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))

    sensitivity_to_student_culture = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    responds_appropriately = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    assists_students_on_concerns = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    guides_the_students_in_accomplishing_tasks = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    extends_consideration_to_students = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],
                               widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    CREDIT_TASK_CHOICES = (
        (True, 'Require less task for the credit'),
        (False, 'Require more task for the credit')
    )

    credit_task_preference = forms.ChoiceField(
        label='The course should:',
        choices=CREDIT_TASK_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}),

    )

    strengths_of_the_faculty = forms.CharField(required=False,widget=forms.TextInput(attrs={'size': 60}))  # Adjust size as needed
    other_suggestions_for_improvement = forms.CharField(required=False,widget=forms.TextInput(attrs={'size': 60}))  # Adjust size as needed
    comments = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 60}))  # Adjust size as needed

LikertEvaluationFormSet = formset_factory(LikertEvaluationForm, extra=1)