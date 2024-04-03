import django_filters
from .models import *

class EvaluationFilter(django_filters.FilterSet):
    REQUIRES_LESS_TASK_FOR_CREDIT= [
        ('True', 'Yes'),
        ('False', 'No'),
    ]
    requires_less_task_for_credit = django_filters.ChoiceFilter(choices=REQUIRES_LESS_TASK_FOR_CREDIT)

    PREDICTED_SENTIMENT_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
    ]
    predicted_sentiment = django_filters.ChoiceFilter(choices=PREDICTED_SENTIMENT_CHOICES, label='Polarity')


    # Define choices for academic_year field dynamically
    academic_year = django_filters.ChoiceFilter(choices=[], label='Academic Year')

    SEMESTER_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
    ]
    semester = django_filters.ChoiceFilter(choices=SEMESTER_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices for academic_year dynamically from the database
        academic_years = LikertEvaluation.objects.order_by('academic_year').values_list('academic_year', flat=True).distinct()
        academic_year_choices = [(year, year) for year in academic_years]
        self.filters['academic_year'].extra['choices'] = academic_year_choices

    class Meta: 
        model = LikertEvaluation
        fields =  ('requires_less_task_for_credit', 'predicted_sentiment' , 'academic_year', 'semester')