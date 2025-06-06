from tokenize import group
import django_filters
from .models import *
from django_filters import CharFilter
from django import forms
from django.db.models import Q, Value, CharField
from django.contrib.auth.models import Group
from django.db.models.functions import Concat
from django.db.models import Case, When, Value, CharField

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
        field_name='sectionsubjectfaculty__subjects',  # This is the related field path
        queryset=Subject.objects.none(),
        label='Subject',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    PREDICTED_SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    ]

    predicted_sentiment = django_filters.ChoiceFilter(
         field_name='predicted_sentiment',  
         choices=PREDICTED_SENTIMENT_CHOICES, 
         label='Polarity', 
         widget=forms.Select(attrs={'class': 'form-control'})
    )


    # Define choices for academic_year field dynamically
    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',
                                                widget=forms.Select(attrs={'class': 'form-control'})
    )

    SEMESTER_CHOICES = [
        ('1st Semester', '1st Semester'),
        ('2nd Semester', '2nd Semester'),
    ]

    semester = django_filters.ChoiceFilter(
         choices=SEMESTER_CHOICES, 
         widget=forms.Select(attrs={'class': 'form-control'})
    )
    
  
    def __init__(self, *args, **kwargs):

        # Populate choices for academic_year dynamically from the database
        academic_years = LikertEvaluation.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        
        semesters = LikertEvaluation.objects.order_by('semester').values_list('semester', flat=True).distinct()
        # Extract faculty from kwargs
        self.faculty = kwargs.pop('faculty', None)
        super().__init__(*args, **kwargs)
        self.filters['academic_year'].extra['choices'] = academic_year_choices
        # Update the queryset with faculty filter
        self.filters['subject'].queryset = Subject.objects.filter(
            sectionsubjectfaculty__faculty=self.faculty
        ).distinct()

        self.filters['semester'].extra['choices'] = [
            (sem, sem) for sem in semesters
        ]

        # Adding the rating category filter
    RATING_CATEGORY_CHOICES = [
        ('Poor', 'Poor'),
        ('Unsatisfactory', 'Unsatisfactory'),
        ('Satisfactory', 'Satisfactory'),
        ('Very Satisfactory', 'Very Satisfactory'),
        ('Outstanding', 'Outstanding'),
    ]

    rating_category = django_filters.ChoiceFilter(
        method='filter_rating_category',
        choices=RATING_CATEGORY_CHOICES,
        label='Rating Category',
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
            Q(section_subject_faculty__faculty__first_name__icontains=value) |
            Q(section_subject_faculty__faculty__last_name__icontains=value) |
            Q(section_subject_faculty__subjects__subject_name__icontains=value) |
            Q(comments__icontains=value) |
            Q(predicted_sentiment__icontains=value) |
            Q(academic_year__icontains=value) |
            Q(semester__icontains=value)     
        )
    
    def filter_rating_category(self, queryset, name, value):
        """
        Filters evaluations by their rating category.
        """
        category_map = {
            'Poor': (1.0, 1.99),
            'Unsatisfactory': (2.0, 2.99),
            'Satisfactory': (3.0, 3.99),
            'Very Satisfactory': (4.0, 4.99),
            'Outstanding': (5.0, 5.0),
        }
        if value in category_map:
            min_rating, max_rating = category_map[value]
            return queryset.filter(average_rating__gte=min_rating, average_rating__lte=max_rating)
        return queryset


class Meta: 
        model = LikertEvaluation
        fields =  ('section_subject_faculty', 'subject',  'predicted_sentiment' , 'academic_year', 'semester', 'search')


class FacultyFilter(django_filters.FilterSet):
    department = django_filters.ModelChoiceFilter(
    queryset=Department.objects.all(),
    label='Department',
    widget=forms.Select(attrs={'class': 'form-control'})) # Add Bootstrap class for styling

    search = django_filters.CharFilter(
    method='filter_search',
    label='',
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search...'
    })
    )
    
    is_supervisor = django_filters.ChoiceFilter(
    label='Supervisor',
    choices=[
        ('true', 'Yes'),
        ('false', 'No')
    ],
    method='filter_is_supervisor',
    widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_is_supervisor(self, queryset, name, value):
        """
        Filters based on the 'is_supervisor' BooleanField.
        """
        if value == 'true':
            return queryset.filter(is_supervisor=True)
        elif value == 'false':
            return queryset.filter(is_supervisor=False)
        return queryset
    
    rating_category = django_filters.ChoiceFilter(
        method='filter_rating_category',
        label='Rating Category',
        choices=[
            ("Poor", "Poor"),
            ("Unsatisfactory", "Unsatisfactory"),
            ("Satisfactory", "Satisfactory"),
            ("Very Satisfactory", "Very Satisfactory"),
            ("Outstanding", "Outstanding"),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(email__icontains=value) |
            Q(contact_number__icontains=value) |     
            Q(department__name__icontains=value)     
        )
    
    def filter_rating_category(self, queryset, name, value):
            """
            Filters the queryset based on rating categories.
            """
            queryset = queryset.annotate(
                avg_rating=Avg(
                    "sectionsubjectfaculty__likertevaluation__average_rating",
                    filter=Q(
                        sectionsubjectfaculty__likertevaluation__academic_year=EvaluationStatus.objects.first().academic_year,
                        sectionsubjectfaculty__likertevaluation__semester=EvaluationStatus.objects.first().semester,
                    )
                ),
                rating_category=Case(
                    When(avg_rating__isnull=True, then=Value("No Rating")),
                    When(avg_rating__lte=1.99, then=Value("Poor")),
                    When(avg_rating__gte=2.0, avg_rating__lte=2.99, then=Value("Unsatisfactory")),
                    When(avg_rating__gte=3.0, avg_rating__lte=3.99, then=Value("Satisfactory")),
                    When(avg_rating__gte=4.0, avg_rating__lte=4.99, then=Value("Very Satisfactory")),
                    When(avg_rating__gte=5.0, avg_rating__lte=5.0, then=Value("Outstanding")),
                    output_field=CharField(),
                )
            )
            # Apply the filter
            if value:
                queryset = queryset.filter(rating_category=value)
            return queryset

    class Meta: 
        model = Faculty
        fields =  ('department', 'gender', 'search', 'is_supervisor')


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
        # Add the necessary annotations if not already in the queryset
        queryset = queryset.annotate(
            student_name=Concat(
                'student__first_name', Value(' '), 'student__last_name',
                output_field=CharField()
            ),
            faculty_name=Concat(
                'faculty__first_name', Value(' '), 'faculty__last_name',
                output_field=CharField()
            )
        )

        # Filter by username, group name, student name, or faculty name
        return queryset.filter(
            Q(username__icontains=value) |   
            Q(groups__name__icontains=value) |
            Q(student_name__icontains=value) |
            Q(faculty_name__icontains=value)
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

    EVALUATION_STATUS_CHOICES = [
        ('True', 'Ongoing'),
        ('False', 'Closed'),
    ]
    evaluation_status = django_filters.ChoiceFilter(
         choices=EVALUATION_STATUS_CHOICES, 
         widget=forms.Select(attrs={'class': 'form-control'})
)
    EVENT_TYPE_CHOICES = [
        ('1', 'School Event'),
        ('2', 'Webinar/Seminar'),
        ('3', 'Training Workshop'),
    ]
    event_type = django_filters.ChoiceFilter(
         choices=EVENT_TYPE_CHOICES, 
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
            # Annotate the queryset with the full name of the author, either as Faculty or Student
        queryset = queryset.annotate(
            author_full_name=Concat(
                'author__faculty__first_name', Value(' '), 'author__faculty__last_name',
                output_field=CharField()
            )
        ).annotate(
            student_full_name=Concat(
                'author__student__first_name', Value(' '), 'author__student__last_name',
                output_field=CharField()
            )
        )

        # Base filter criteria for other fields
        filter_criteria = (
            Q(title__icontains=value) | 
            Q(location__icontains=value) | 
            Q(date__icontains=value) |
            Q(author_full_name__icontains=value) |
            Q(student_full_name__icontains=value) |
            Q(event_type__name__icontains=value) |
            Q(time__icontains=value)
        )
        
        # Add filter for evaluation_status based on "ongoing" or "closed" input
        if value.lower() == "ongoing":
            filter_criteria |= Q(evaluation_status=True)
        elif value.lower() == "closed":
            filter_criteria |= Q(evaluation_status=False)

        # Apply the complete filter criteria to the queryset
        return queryset.filter(filter_criteria)



    class Meta: 
        model = Event
        fields =  ('course_attendees', 'department_attendees', 'evaluation_status', 'event_type', 'academic_year', 'semester', 'search')

class SchoolEventFilter(django_filters.FilterSet):
    # Define filters for predicted_sentiment, academic_year, and semester
    predicted_sentiment = django_filters.ChoiceFilter(
        field_name='predicted_sentiment',
        choices=[
            ('Positive', 'Positive'),
            ('Negative', 'Negative'),
            ('Neutral', 'Neutral'),
        ],
        label="Predicted Sentiment",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',
                                                widget=forms.Select(attrs={'class': 'form-control'})
    )
    semester = django_filters.ChoiceFilter(
        field_name='semester',
        choices=[
            ('1st Semester', '1st Semester'),
            ('2nd Semester', '2nd Semester'),
        ],
        label="Semester",
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

    rating_category = django_filters.ChoiceFilter(
        method='filter_rating_category',
        label='Rating Category',
        choices=[
            ("Poor", "Poor"),
            ("Unsatisfactory", "Unsatisfactory"),
            ("Satisfactory", "Satisfactory"),
            ("Very Satisfactory", "Very Satisfactory"),
            ("Outstanding", "Outstanding"),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(comments__icontains=value) |
            Q(predicted_sentiment__icontains=value) |
            Q(academic_year__icontains=value) |
            Q(semester__icontains=value)     
        )
    
    def filter_rating_category(self, queryset, name, value):
        """
        Filters the queryset based on the rating category.
        The rating category is determined from the 'average_rating' field of SchoolEventModel.
        """
        # Annotate each instance with a 'rating_category' based on its average_rating field.
        queryset = queryset.annotate(
            rating_category=Case(
                When(average_rating__isnull=True, then=Value("No Rating")),
                When(average_rating__lte=1.99, then=Value("Poor")),
                When(average_rating__gte=2.0, average_rating__lte=2.99, then=Value("Unsatisfactory")),
                When(average_rating__gte=3.0, average_rating__lte=3.99, then=Value("Satisfactory")),
                When(average_rating__gte=4.0, average_rating__lte=4.99, then=Value("Very Satisfactory")),
                When(average_rating__gte=5.0, then=Value("Outstanding")),
                output_field=CharField(),
            )
        )
        
        # Apply the filter if a value is provided
        if value:
            queryset = queryset.filter(rating_category=value)
        
        return queryset


    def __init__(self, *args, **kwargs):

        # Populate choices for academic_year dynamically from the database
        academic_years = SchoolEventModel.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        super().__init__(*args, **kwargs)
        self.filters['academic_year'].extra['choices'] = academic_year_choices
        # Update the queryset with faculty filter


 
    
    class Meta:
        model = SchoolEventModel
        fields = ['predicted_sentiment', 'academic_year', 'semester', 'search']

class WebinarSeminarEventFilter(django_filters.FilterSet):
    # Define filters for predicted_sentiment, academic_year, and semester
    predicted_sentiment = django_filters.ChoiceFilter(
        field_name='predicted_sentiment',
        choices=[
            ('Positive', 'Positive'),
            ('Negative', 'Negative'),
            ('Neutral', 'Neutral'),
        ],
        label="Predicted Sentiment",
         widget=forms.Select(attrs={'class': 'form-control'})
    )
    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',
                                                widget=forms.Select(attrs={'class': 'form-control'})
    )
    semester = django_filters.ChoiceFilter(
        field_name='semester',
        choices=[
            ('1st Semester', '1st Semester'),
            ('2nd Semester', '2nd Semester'),
        ],
        label="Semester",
         widget=forms.Select(attrs={'class': 'form-control'})
    )

    rating_category = django_filters.ChoiceFilter(
    method='filter_rating_category',
    label='Rating Category',
    choices=[
        ("Poor", "Poor"),
        ("Unsatisfactory", "Unsatisfactory"),
        ("Satisfactory", "Satisfactory"),
        ("Very Satisfactory", "Very Satisfactory"),
        ("Outstanding", "Outstanding"),
    ],
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
            Q(comments__icontains=value) |
            Q(predicted_sentiment__icontains=value) |
            Q(academic_year__icontains=value) |
            Q(semester__icontains=value)     
        )
    
    def filter_rating_category(self, queryset, name, value):
        """
        Filters the queryset based on the rating category.
        The rating category is determined from the 'average_rating' field of SchoolEventModel.
        """
        # Annotate each instance with a 'rating_category' based on its average_rating field.
        queryset = queryset.annotate(
            rating_category=Case(
                When(average_rating__isnull=True, then=Value("No Rating")),
                When(average_rating__lte=1.99, then=Value("Poor")),
                When(average_rating__gte=2.0, average_rating__lte=2.99, then=Value("Unsatisfactory")),
                When(average_rating__gte=3.0, average_rating__lte=3.99, then=Value("Satisfactory")),
                When(average_rating__gte=4.0, average_rating__lte=4.99, then=Value("Very Satisfactory")),
                When(average_rating__gte=5.0, then=Value("Outstanding")),
                output_field=CharField(),
            )
        )
        
        # Apply the filter if a value is provided
        if value:
            queryset = queryset.filter(rating_category=value)
        
        return queryset

    def __init__(self, *args, **kwargs):

        # Populate choices for academic_year dynamically from the database
        academic_years = WebinarSeminarModel.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        super().__init__(*args, **kwargs)
        self.filters['academic_year'].extra['choices'] = academic_year_choices
        # Update the queryset with faculty filter


    class Meta:
        model = WebinarSeminarModel
        fields = ['predicted_sentiment', 'academic_year', 'semester', 'search']
    

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

    SEMESTER_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
    ]
    semester = django_filters.ChoiceFilter(
         choices=SEMESTER_CHOICES, 
         widget=forms.Select(attrs={'class': 'form-control'})
)
   
    # Define choices for months dynamically
    month = django_filters.ChoiceFilter(
        field_name='date__month',
        label='Month',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
        # Define choices for year dynamically
    year = django_filters.ChoiceFilter(
        field_name='date__year',
        label='Year',
        choices=[],  # Will be populated dynamically
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    # Filter by agency (assuming `agency` is a ForeignKey)
    agency = django_filters.ModelChoiceFilter(
        queryset=StakeholderAgency.objects.all(),
        label='Agency',
        widget=forms.Select(attrs={'class': 'form-control'}),
    ) 
    PREDICTED_SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    ]

    predicted_sentiment = django_filters.ChoiceFilter(
         choices=PREDICTED_SENTIMENT_CHOICES, 
         label='Polarity', 
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices for academic_year dynamically from the database
        academic_years = StakeholderFeedbackModel.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        self.filters['academic_year'].extra['choices'] = academic_year_choices

        # Populate choices for months dynamically from the database
        available_months = (
            StakeholderFeedbackModel.objects
            .dates('date', 'month', order='ASC')
            .distinct()
        )
        month_choices = [(month.month, month.strftime('%B')) for month in available_months]
        self.filters['month'].extra['choices'] = month_choices

                # Populate choices for year dynamically
        available_years = (
            StakeholderFeedbackModel.objects
            .dates('date', 'year', order='ASC')
            .distinct()
        )
        year_choices = [(year.year, year.year) for year in available_years]
        self.filters['year'].extra['choices'] = year_choices



    class Meta:
        model = StakeholderFeedbackModel
        fields = ('academic_year', 'semester', 'month', 'agency', 'search')

class LikertEvaluationFilter(django_filters.FilterSet):
    SEMESTER_CHOICES = [
        ('1st Semester', '1st Semester'),
        ('2nd Semester', '2nd Semester'),
    ]

    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',   # Set 'All' as the default
                                                widget=forms.Select(attrs={'class': 'form-control'}))
    semester = django_filters.ChoiceFilter(choices=SEMESTER_CHOICES, label='Semester', 
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

class PeertoPeerEvaluationFilter(django_filters.FilterSet):
    PREDICTED_SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Neutral', 'Neutral'),
    ]

    predicted_sentiment = django_filters.ChoiceFilter(
         choices=PREDICTED_SENTIMENT_CHOICES, 
         label='Polarity', 
         widget=forms.Select(attrs={'class': 'form-control'})
    )

    rating_category = django_filters.ChoiceFilter(
    method='filter_rating_category',
    label='Rating Category',
    choices=[
        ("Poor", "Poor"),
        ("Unsatisfactory", "Unsatisfactory"),
        ("Satisfactory", "Satisfactory"),
        ("Very Satisfactory", "Very Satisfactory"),
        ("Outstanding", "Outstanding"),
    ],
    widget=forms.Select(attrs={'class': 'form-control'})
    )
    # Define choices for academic_year field dynamically
    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year',
                                                widget=forms.Select(attrs={'class': 'form-control'})
                                                )

    SEMESTER_CHOICES = [
        ('1st Semester', '1st Semester'),
        ('2nd Semester', '2nd Semester'),
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
            Q(comments__icontains=value) |
            Q(predicted_sentiment__icontains=value) |
            Q(academic_year__icontains=value) |
            Q(semester__icontains=value)     
        )
    def filter_rating_category(self, queryset, name, value):
        """
        Filters the queryset based on the rating category.
        The rating category is determined from the 'average_rating' field of SchoolEventModel.
        """
        # Annotate each instance with a 'rating_category' based on its average_rating field.
        queryset = queryset.annotate(
            rating_category=Case(
                When(average_rating__isnull=True, then=Value("No Rating")),
                When(average_rating__lte=1.99, then=Value("Poor")),
                When(average_rating__gte=2.0, average_rating__lte=2.99, then=Value("Unsatisfactory")),
                When(average_rating__gte=3.0, average_rating__lte=3.99, then=Value("Satisfactory")),
                When(average_rating__gte=4.0, average_rating__lte=4.99, then=Value("Very Satisfactory")),
                When(average_rating__gte=5.0, then=Value("Outstanding")),
                output_field=CharField(),
            )
        )
        
        # Apply the filter if a value is provided
        if value:
            queryset = queryset.filter(rating_category=value)
        
        return queryset
class Meta: 
        model = PeertoPeerEvaluation
        fields =  ( 'predicted_sentiment' , 'academic_year', 'semester', 'search')
