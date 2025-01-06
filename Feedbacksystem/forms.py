from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Faculty, Student, Course, Section, SectionSubjectFaculty, Subject, EvaluationStatus, Department, Event, SchoolEventModel, WebinarSeminarModel, FacultyEvaluationQuestions, SchoolEventQuestions, WebinarSeminarQuestions, LikertEvaluation, Message, PeertoPeerEvaluation, StakeholderFeedbackQuestions
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.forms import formset_factory
from django.forms.utils import ErrorList

class NoErrorList(ErrorList):
    def __str__(self):
        return ''
    def as_ul(self):
        return ''
    def as_text(self):
        return ''


class TeacherForm(ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__' 
        exclude = ['user', 'profile_picture', 'email_sent', 'is_supervisor']
        labels = {
            'last_name': 'Surname',
            'gender': 'Sex',
            'contact_number': 'Contact No.',
            'employment_status': 'Status of Employment',
            'academic_rank': 'Academic Rank',
            'date_of_employment': 'Date of Employment',
            'years_in_service': 'Years in Service',
            'no_of_workload': 'Total No. of Workload',
            'educational_attainment': 'Educational Attainment',
            'eligibility': 'Eligibility if Yes, what kind?',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),   
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),   
            'employment_status': forms.TextInput(attrs={'class': 'form-control'}),     
            'academic_rank': forms.TextInput(attrs={'class': 'form-control'}),  
            'date_of_employment': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),   
            'years_in_service': forms.TextInput(attrs={'class': 'form-control'}),     
            'department': forms.Select(attrs={'class': 'form-control'}),
            'no_of_workload': forms.TextInput(attrs={'class': 'form-control'}), 
            'educational_attainment': forms.Select(attrs={'class': 'form-control'}), 
            'eligibility': forms.TextInput(attrs={'class': 'form-control'}), 
        }

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__' 
        exclude = ['user', 'profile_picture']
        labels = {
            'last_name': 'Surname'
        }
        widgets = {
            'student_number': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'year': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'Course': forms.Select(attrs={'class': 'form-control'}),
            'Section': forms.Select(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'date_enrolled': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'school_year': forms.TextInput(attrs={'class': 'form-control'}),
            'major': forms.TextInput(attrs={'class': 'form-control'}),
            'old_or_new_student': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'birthdate': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
        }

class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'     
        exclude = ['email_sent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = '__all__' 

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class SectionForm(ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'course']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
        }

class SectionSubjectFacultyForm(ModelForm):
    class Meta:
        model = SectionSubjectFaculty
        fields = '__all__'  
        widgets = {
            'section': forms.Select(attrs={'class': 'form-control'}),
            'subjects': forms.Select(attrs={'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
        }

class SubjectForm(ModelForm):
    class Meta:
        model = Subject
        fields = '__all__'    
        widgets = {
            'subject_code': forms.TextInput(attrs={'class': 'form-control'}),
            'subject_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EvaluationStatusForm(ModelForm):
    class Meta:
        model = EvaluationStatus
        fields = '__all__'
        labels = {
            'academic_year': 'Academic Year',
            'semester': 'Semester',
            'evaluation_status': 'Evaluations Status',
            'evaluation_end_date': 'Evaluation End Date',
            'evaluation_release_date': 'Evaluation Release Date',
        }
        widgets = {
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'evaluation_status': forms.Select(attrs={'class': 'form-control'}),
            'evaluation_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'evaluation_release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class StudentRegistrationForm(UserCreationForm):
    student_number = forms.CharField(label="Student Number", widget=forms.NumberInput(attrs={'type': 'number','oninput': 'if(this.value.length > 9) this.value = this.value.slice(0, 9);'}),
                                       )
    class Meta:
        model = User
        fields = ('student_number', 'password1', 'password2')
        widgets = {
            'password1': forms.PasswordInput(attrs={'id': 'id_password1'}),
            'password2': forms.PasswordInput(attrs={'id': 'id_password2'}),
        }

    def clean_student_number(self):
        student_number = self.cleaned_data.get('student_number')

        # Check if the student number exists in the database
        existing_student = Student.objects.filter(student_number=student_number).first()

        if not existing_student:
            # If the student number does not exist, raise an error
            self.add_error('student_number', "Student with this student number does not exist. Please contact the admin to create an account.")
        else:
            # If the student exists, check if they already have a user account
            if existing_student.user:
                # If the student number is already registered, raise an error
                self.add_error('student_number', "This student number is already registered. Please login to continue.")
            else:
                # If the student number exists but is not associated with a user, associate it
                self.instance.student = existing_student

        return student_number
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        # Save the user first
        user = super().save(commit=False)

        user.username = self.cleaned_data['student_number']

        # Associate the user with the existing student record
        user.student = Student.objects.get(student_number=self.cleaned_data['student_number'])

        if commit:
            user.save()
             # Save the related student object after saving the user
            if hasattr(user, 'student') and user.student:
                user.student.save()

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set help_text to an empty string for each field
        for field_name in self.fields:
            self.fields[field_name].help_text = ''
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            
        # Suppress inline error rendering
        self.error_class = NoErrorList  

class FacultyRegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')
        widgets = {
            'password1': forms.PasswordInput(attrs={'id': 'id_password1'}),
            'password2': forms.PasswordInput(attrs={'id': 'id_password2'}),
        }


    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Check if the student number exists in the database
        existing_faculty = Faculty.objects.filter(email=email).first()

        if not existing_faculty:
            raise ValidationError("Faculty with this email does not exist. Please contact the admin to create an account.")
        else: # Check if the student number is already registered with a user 
            if existing_faculty.user: 
                self.add_error('email', "This email is already registered.") 

        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        # Save the user first
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']
        if commit:
            user.save()
            # Link the user to the corresponding Faculty record by email
            faculty = Faculty.objects.get(email=self.cleaned_data['email'])
            faculty.user = user
            faculty.save()

        return user


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set help_text to an empty string for each field
        for field_name in self.fields:
            self.fields[field_name].help_text = ''
        
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        
        self.error_class = NoErrorList  
            
            
class AdminRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'role')
        labels = {
            'username': 'Admin Username',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password1'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password2'}),
        }
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('HR admin', 'HR admin'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="User Role",
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Passwords do not match.")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

              

class StudentLoginForm(forms.Form):
    student_number = forms.CharField(
        widget=forms.NumberInput(attrs={'type': 'number','oninput': 'if(this.value.length > 9) this.value = this.value.slice(0, 9);'}),
        label="Student Number"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_password'}),
        label="Password"
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

           
class FacultyLoginForm(forms.Form):
    email = forms.EmailField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'id_password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

           
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


    requires_less_task_for_credit = forms.ChoiceField(
    choices=[('Require less task for the credit', 'Require less task for the credit'), ('Require more task for the credit', 'Require more task for the credit')],
        widget=forms.RadioSelect(attrs={'class': 'custom-choice-radio'}),

    )

    strengths_of_the_faculty = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,  # Controls the height
            'cols': 60,  # Controls the width
            'class': 'custom-text-input'
        })
    )
    other_suggestions_for_improvement = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,  # Adjust height
            'cols': 60,  # Adjust width
            'class': 'custom-text-input'
        })
    )
    other_suggestions_for_improvement = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,  # Adjust height
            'cols': 60,  # Adjust width
            'class': 'custom-text-input'
        })
    )
    comments = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 4,  # Adjust height
            'cols': 60,  # Adjust width
            'class': 'custom-text-input'
        })
    )

LikertEvaluationFormSet = formset_factory(LikertEvaluationForm, extra=1)

class DateInput(forms.DateInput):
    input_type = 'date'

class EventCreationForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'time', 'location', 'event_type','event_picture', 'description', 'course_attendees', 'department_attendees', 'evaluation_status','evaluation_start_datetime', 'evaluation_end_datetime','requires_attendance']
        labels = {
            'course_attendees': 'Course Attendees',
            'department_attendees': 'Department Attendees',
            'evaluation_status': 'Evaluation Status',
            'requires_attendance': 'Requires Attendance (Generate QR Code)',
        }

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'date': DateInput(attrs={'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'event_picture': forms.ClearableFileInput(attrs={'class': 'form-control '}),
            'course_attendees': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'department_attendees': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'evaluation_status': forms.Select(attrs={'class': 'form-control'}),
            'evaluation_start_datetime': DateInput(attrs={'class': 'form-control'}),
            'evaluation_end_datetime': DateInput(attrs={'class': 'form-control'}),
            'requires_attendance': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        course_attendees = cleaned_data.get('course_attendees')
        department_attendees = cleaned_data.get('department_attendees')

        if not course_attendees and not department_attendees:
            raise ValidationError("You must select at least one Course or Department attendee.")

        return cleaned_data

class SchoolEventForm(forms.Form):
    meeting_expectation = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    attainment_of_the_objectives = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    topics_discussed = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    input_presentation = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    management_team = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    venue_and_physical_arrangement = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    overall_assessment = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    suggestions_and_comments = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 60, 'class': 'form-control'}))  # Adjust size as needed

class WebinarSeminarForm(forms.Form):
    relevance_of_the_activity = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    quality_of_the_activity = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    timeliness = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    suggestions_and_comments = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 60, 'class': 'form-control'}))  # Adjust size as needed
    
    # Procedure and Content
    attainment_of_the_objective = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    appropriateness_of_the_topic_to_attain_the_objective = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    appropriateness_of_the_searching_methods = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    topics_to_be_included = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 60, 'class': 'form-control'}))  # Adjust size as needed
    
    # Suitability of the present time
    appropriateness_of_the_topic_in_the_present_time = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    usefulness_of_the_topic_discusssed_in_the_activity = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    appropriateness_of_the_searching_methods_used = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    #Speaker Evaluation 
    
    displayed_a_thorough_knowledge_of_the_topic = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    explained_activities = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    able_to_create_a_good_learning_environment = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    able_to_manage_her_time_well = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    demonstrated_keenness_to_the_participant_needs = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    demonstrated_keenness_to_the_participant_needs = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    timeliness_or_suitability_of_service = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    overall_satisfaction = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    
    other_comments = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 60, 'class': 'form-control'}))  # Adjust size as needed

class StakeholderFeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    agency = forms.ChoiceField(
        choices=[
            ('', 'Select Agency'),  # Default placeholder
            ('Cashier', 'Cashier'),
            ('Clinic', 'Clinic'),
            ('GAD', 'GAD'),
            ('Guidance', 'Guidance'),
            ('HRDO', 'HRDO'),
            ('Library', 'Library'),
            ('OSAS', 'OSAS'),
            ('RDE', 'RDE'),
            ('Registrar', 'Registrar'),
            ('Supply Office', 'Supply Office'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    purpose = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    staff = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    courtesy = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    quality = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    timeliness = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    efficiency = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    cleanliness = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))
    comfort = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
                                        (2, ''), (1, '')],  widget=forms.RadioSelect(attrs={'class': 'likert-horizontal custom-radio'}))

    suggestions_and_comments = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'rows': 4,  # Adjust the number of rows (height) as needed
            'cols': 60,  # Adjust the number of columns (width) as needed
            'class': 'form-control'
        })
    )
class StudentProfileForm(ModelForm):
    class Meta:
        model = Student
        fields = ['email', 'contact_no', 'profile_picture']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_no': forms.NumberInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'pattern': '[0-9]*',}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        } 
        
class FacultyProfileForm(ModelForm):
    class Meta:
        model = Faculty
        fields = ['email', 'contact_number', 'profile_picture']

        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.NumberInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'pattern': '[0-9]*',}),   
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        } 
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Update username based on email
        instance.user.username = self.cleaned_data['email']
        if commit:
            instance.save()
            instance.user.save()
        return instance
class EditQuestionForm(ModelForm):
    class Meta:
        model = FacultyEvaluationQuestions
        fields = ['text'] 
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
       
    
class EditSchoolEventQuestionForm(ModelForm):
    class Meta:
        model = SchoolEventQuestions
        fields = ['text', 'order'] 
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 
                                              'min': 1, 'max': 10 }),
        }

class EditWebinarSeminarQuestionForm(ModelForm):
    class Meta:
        model = WebinarSeminarQuestions
        fields = ['text'] 
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
       
class EditStakeholdersQuestionForm(ModelForm):
    class Meta:
        model = StakeholderFeedbackQuestions
        fields = ['text'] 
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control'}),
        }
       
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content', 'attachment']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PeertoPeerEvaluationForm(forms.Form):
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

    strengths_of_the_faculty = forms.CharField(required=False,widget=forms.TextInput(attrs={'size': 60, 'class': 'custom-text-input'}))  # Adjust size as needed
    other_suggestions_for_improvement = forms.CharField(required=False,widget=forms.TextInput(attrs={'size': 60, 'class': 'custom-text-input'}))  # Adjust size as needed
    comments = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 60, 'class': 'custom-text-input'}))  # Adjust size as needed

    PeertoPeerEvaluationFormSet = formset_factory(PeertoPeerEvaluation, extra=1)

