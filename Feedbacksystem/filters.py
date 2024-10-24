from tokenize import group
import django_filters
from .models import *
from django_filters import CharFilter
from django import forms
from django.db.models import Q
from django.contrib.auth.models import Group

class EvaluationFilter(django_filters.FilterSet):
     # Foreign key field filter
    section_subject_faculty = django_filters.ModelChoiceFilter(
    field_name='section_subject_faculty__faculty',  # Field name of the foreign key
    queryset=Faculty.objects.all(),  # Queryset of SectionSubjectFaculty objects
    label='Faculty',  # Label for the filter field
    widget=forms.Select(attrs={'class': 'form-control'})

    )
      # Adding the subject category filter
    subject = django_filters.ModelChoiceFilter(
        field_name='section_subject_faculty__subjects',  # This is the related field path
        queryset=Subject.objects.all(),
        label='Subject',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    PREDICTED_SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
    ]

    predicted_sentiment = django_filters.ChoiceFilter(
         choices=PREDICTED_SENTIMENT_CHOICES, 
         label='Polarity', 
         widget=forms.Select(attrs={'class': 'form-control'})
    )


    # Define choices for academic_year field dynamically
    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',
                                                widget=forms.Select(attrs={'class': 'form-control'})
)

    SEMESTER_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
    ]
    semester = django_filters.ChoiceFilter(
         choices=SEMESTER_CHOICES, 
         widget=forms.Select(attrs={'class': 'form-control'})
)
    
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices for academic_year dynamically from the database
        academic_years = LikertEvaluation.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        self.filters['academic_year'].extra['choices'] = academic_year_choices
 
 
    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )

    # Other filters...

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(section_subject_faculty__faculty__first_name__icontains=value) |
            Q(section_subject_faculty__faculty__last_name__icontains=value) |
            Q(section_subject_faculty__subjects__subject_name__icontains=value) |
            Q(comments__icontains=value) |
            Q(predicted_sentiment__icontains=value) |
            Q(academic_year__icontains=value) |
            Q(semester__icontains=value)     
        )



class Meta: 
        model = LikertEvaluation
        fields =  ('section_subject_faculty', 'subject',  'predicted_sentiment' , 'academic_year', 'semester', 'search')


class FacultyFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
    method='filter_search',
    label='',
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search...'
    })
    )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value) |
            Q(contact_number__icontains=value) |     
            Q(department__name__icontains=value)     
        )

    class Meta: 
        model = Faculty
        fields =  ('department', 'gender', 'search')


class StudentFilter(django_filters.FilterSet):
    Section = django_filters.ModelChoiceFilter(
    queryset=Section.objects.all(),
    label='Section',
    widget=forms.Select(attrs={'class': 'form-control'})) # Add Bootstrap class for styling
    
    STATUS_CHOICES = [
        ('Regular', 'Regular'),
        ('Irregular', 'Irregular'),
    ]

    status = django_filters.ChoiceFilter(
        field_name='status',
        choices=STATUS_CHOICES,  # Directly specify the two choices
        label='Status',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(student_number__icontains=value) |   
            Q(first_name__icontains=value) |  
            Q(last_name__icontains=value) | 
            Q(email__icontains=value) |   
            Q(contact_no__icontains=value) |   
            Q(age__icontains=value) | 
            Q(status__icontains=value)   |
            Q(Section__name__icontains=value)   
        )

    class Meta: 
        model = Student
        fields = ['Section', 'status', 'search']  # Ensure this is a list of valid model fields

class UserFilter(django_filters.FilterSet):
    groups = django_filters.ModelChoiceFilter(
    queryset=Group.objects.all(),
    label='Role',
    widget=forms.Select(attrs={'class': 'form-control'})) # Add Bootstrap class for styling

    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) |   
             Q(groups__name__icontains=value)   
        )


    class Meta: 
        model = User
        fields = ['groups', 'search']  # Ensure this is a list of valid model fields

class EventFilter(django_filters.FilterSet):
    course_attendees = django_filters.ModelMultipleChoiceFilter(
        queryset=Course.objects.all(),  # Dynamically fetch choices
        label='Course Attendees',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    department_attendees = django_filters.ModelMultipleChoiceFilter(
        queryset=Department.objects.all(),  # Dynamically fetch choices
        label='Department Attendees',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    # Define choices for academic_year field dynamically
    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',
    widget=forms.Select(attrs={'class': 'form-control'})
)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices for academic_year dynamically from the database
        academic_years = Event.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        self.filters['academic_year'].extra['choices'] = academic_year_choices

    SEMESTER_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
    ]
    semester = django_filters.ChoiceFilter(
         choices=SEMESTER_CHOICES, 
         widget=forms.Select(attrs={'class': 'form-control'})
)
    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )

    # Other filters...

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value)  
        )



    class Meta: 
        model = Event
        fields =  ('course_attendees', 'department_attendees', 'evaluation_status', 'academic_year', 'semester', 'search')

class SectionFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )

    # Other filters...

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)  
        )
    
    class Meta:
        model = Section
        fields = ('name','search')

class SubjectFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )

    # Other filters...

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(subject_code__icontains=value)  |
            Q(subject_name__icontains=value)  
        )
    
    class Meta:
        model = Subject
        fields = ('subject_code', 'subject_name', 'search')

class StakeholderFilter(django_filters.FilterSet):
        # Define choices for academic_year field dynamically
    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',
                                                widget=forms.Select(attrs={'class': 'form-control'})
)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices for academic_year dynamically from the database
        academic_years = StakeholderFeedbackModel.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        self.filters['academic_year'].extra['choices'] = academic_year_choices
    SEMESTER_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
    ]
    semester = django_filters.ChoiceFilter(
         choices=SEMESTER_CHOICES, 
         widget=forms.Select(attrs={'class': 'form-control'})
)
   
    
    
    search = django_filters.CharFilter(
        method='filter_search',
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name=value)  |
            Q(agency=value)  |
            Q(email=value)  |
            Q(purpose=value)  |
            Q(date=value)  |
            Q(staff=value)  
        )
    
    class Meta:
        model = StakeholderFeedbackModel
        fields = ('academic_year', 'semester', 'search')

class LikertEvaluationFilter(django_filters.FilterSet):
    SEMESTER_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
    ]

    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year', empty_label='All',  # Set 'All' as the default
                                                widget=forms.Select(attrs={'class': 'form-control'}))
    semester = django_filters.ChoiceFilter(choices=SEMESTER_CHOICES, label='Semester', empty_label='All',
                                           widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = LikertEvaluation
        fields = ['academic_year', 'semester']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices for academic_year dynamically from the database
        academic_years = LikertEvaluation.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        self.filters['academic_year'].extra['choices'] = academic_year_choices
