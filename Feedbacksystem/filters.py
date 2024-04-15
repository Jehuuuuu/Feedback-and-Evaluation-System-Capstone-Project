import django_filters
from .models import *
from django_filters import CharFilter
from django import forms

class EvaluationFilter(django_filters.FilterSet):
     # Foreign key field filter
    section_subject_faculty = django_filters.ModelChoiceFilter(
    field_name='section_subject_faculty',  # Field name of the foreign key
    queryset=SectionSubjectFaculty.objects.all(),  # Queryset of SectionSubjectFaculty objects
    label='Faculty',  # Label for the filter field
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
    
    comments = CharFilter(field_name = 'comments', lookup_expr='icontains', label = 'Comments', 
                          widget=forms.TextInput(attrs={'class': 'form-control'})
)

class Meta: 
        model = LikertEvaluation
        fields =  ('section_subject_faculty',  'predicted_sentiment' , 'academic_year', 'semester', 'comments')
  