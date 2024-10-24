from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Faculty, Student, Course, Section, SectionSubjectFaculty, Subject, EvaluationStatus, Department, Event, SchoolEventModel, WebinarSeminarModel, FacultyEvaluationQuestions, SchoolEventQuestions, WebinarSeminarQuestions, LikertEvaluation
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.forms import formset_factory
class TeacherForm(ModelForm):
    class Meta:
        model = Faculty
        fields = '__all__' 
        exclude = ['user']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__' 
        exclude = ['user', 'middle_name']
        widgets = {
            'student_number': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'age': forms.TextInput(attrs={'class': 'form-control'}),
            'sex': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_no': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'Course': forms.Select(attrs={'class': 'form-control'}),
            'Section': forms.Select(attrs={'class': 'form-control'}),
        }
class DepartmentForm(ModelForm):
    class Meta:
        model = Department
        fields = '__all__'     

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
        fields = ['name']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
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

        widgets = {
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.Select(attrs={'class': 'form-control'}),
            'evaluation_status': forms.Select(attrs={'class': 'form-control'}),

        }

class StudentRegistrationForm(UserCreationForm):
    student_number = forms.CharField(max_length=9)

    class Meta:
        model = User
        fields = ('student_number', 'password1', 'password2')

    def clean_student_number(self):
        student_number = self.cleaned_data['student_number']

        # Check if the student number exists in the database
        existing_student = Student.objects.filter(student_number=student_number).first()
        if existing_student:
                # Associate the user with the existing student record
                self.instance.student = existing_student

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
             # Save the related student object after saving the user
            if hasattr(user, 'student') and user.student:
                user.student.save()

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
        existing_faculty = Faculty.objects.filter(email=email).first()

        if not existing_faculty:
            raise ValidationError("Faculy with this email does not exist. Please contact the admin to create an account.")

        return email

    def save(self, commit=True):
        # Save the user first
        user = super().save(commit=False)

        user.username = self.cleaned_data['email']

        # Associate the user with the faculty record
        user.faculty = Faculty.objects.get(email=self.cleaned_data['email'])

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

    strengths_of_the_faculty = forms.CharField(required=False,widget=forms.TextInput(attrs={'size': 60, 'class': 'custom-text-input'}))  # Adjust size as needed
    other_suggestions_for_improvement = forms.CharField(required=False,widget=forms.TextInput(attrs={'size': 60, 'class': 'custom-text-input'}))  # Adjust size as needed
    comments = forms.CharField(required=True, widget=forms.TextInput(attrs={'size': 60, 'class': 'custom-text-input'}))  # Adjust size as needed

LikertEvaluationFormSet = formset_factory(LikertEvaluationForm, extra=1)

class DateInput(forms.DateInput):
    input_type = 'date'

class EventCreationForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'time', 'location', 'event_type','event_picture', 'description', 'course_attendees', 'department_attendees', 'evaluation_status']
        labels = {
            'course_attendees': 'Course Attendees',
            'department_attendees': 'Department Attendees',
            'evaluation_status': 'Start Evaluations',
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
            'evaluation_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

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
    thoroughly_explained_and_processed_the_learning_activities_throughout_the_training = forms.ChoiceField(choices=[(5, ''), (4, ''), (3, ''),
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

class StakeholderFeedbackForm(forms.Form):
    name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    agency = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
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
            'contact_no': forms.NumberInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        } 
        
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
       
    