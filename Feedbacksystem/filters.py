import django_filters
from .models import *

class EvaluationFilter(django_filters.FilterSet):
    class Meta: 
        model = LikertEvaluation
        fields = ('section_subject_faculty', 'requires_less_task_for_credit', 'comments', 'predicted_sentiment' , 'academic_year', 'semester')