from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Avg
from notifications.models import Notification 
# Create your models here.

class Course(models.Model):
   name = models.CharField(max_length=100)
   
   updated = models.DateTimeField(auto_now = True, null=True, blank = True)
   created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

   class Meta:
        ordering = ['name']

   def __str__(self):
        return self.name
    
    
    


    
class Department(models.Model):
    name = models.CharField(max_length=100)
    email_sent = models.BooleanField(default=False)  # New field to track email sent status

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Faculty(models.Model):
    user = models.OneToOneField(User, null = True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=9)
    email = models.EmailField(unique=True)
    contact_number = models.CharField(max_length  = 11)
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank = True) 
    email_sent = models.BooleanField(default=False)  # New field to track email sent status

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    class Meta:
        ordering = ['-updated', '-created']
        
    def __str__(self):
        return f"{self.first_name} {self. last_name}"
    
    def delete(self, *args, **kwargs):
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)


    def average_rating(self):
        evaluation_status = EvaluationStatus.objects.first()
        current_academic_year = evaluation_status.academic_year 
        current_semester = evaluation_status.semester

        evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=self, academic_year=current_academic_year, semester=current_semester)
        
        if evaluations.exists():
            fields_to_average = [
                'command_and_knowledge_of_the_subject',
                'depth_of_mastery',
                'practice_in_respective_discipline',
                'up_to_date_knowledge',
                'integrates_subject_to_practical_circumstances',
                'organizes_the_subject_matter',
                'provides_orientation_on_course_content',
                'efforts_of_class_preparation',
                'summarizes_main_points',
                'monitors_online_class',
                'holds_interest_of_students',
                'provides_relevant_feedback',
                'encourages_participation',
                'shows_enthusiasm',
                'shows_sense_of_humor',
                'teaching_methods',
                'flexible_learning_strategies',
                'student_engagement',
                'clear_examples',
                'focused_on_objectives',
                'starts_with_motivating_activities',
                'speaks_in_clear_and_audible_manner',
                'uses_appropriate_medium_of_instruction',
                'establishes_online_classroom_environment',
                'observes_proper_classroom_etiquette',
                'uses_time_wisely',
                'gives_ample_time_for_students_to_prepare',
                'updates_the_students_of_their_progress',
                'demonstrates_leadership_and_professionalism',
                'understands_possible_distractions',
                'sensitivity_to_student_culture',
                'responds_appropriately',
                'assists_students_on_concerns',
                'guides_the_students_in_accomplishing_tasks',
                'extends_consideration_to_students',
            ]
            
            # Fetch and sum up the values of these fields for each evaluation
            ratings = []
            for field in fields_to_average:
                ratings.extend(evaluations.values_list(field, flat=True))

            # Filter out None values and calculate average
            ratings = [rating for rating in ratings if rating is not None]

            if ratings:
                average_rating = sum(ratings) / len(ratings)
                return round(average_rating, 2)
        
        return 0.0

    @property
    def get_rating_category(self):
        avg_rating = self.average_rating()  # Call the method here
        if avg_rating is not None:
            if 1.0 <= avg_rating <= 1.49:
                return "Poor"
            elif 1.5 <= avg_rating <= 2.49:
                return "Unsatisfactory"
            elif 2.5 <= avg_rating <= 3.49:
                return "Satisfactory"
            elif 3.5 <= avg_rating <= 4.49:
                return "Very Satisfactory"
            elif 4.5 <= avg_rating <= 5.0:
                return "Outstanding"
        return "No Rating"
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
class Subject(models.Model):
    subject_code = models.CharField(max_length=10)
    subject_name = models.CharField(max_length=100)  
    
    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    class Meta:
        ordering = ['subject_code', 'subject_name']

    def __str__(self):
        return f"{self.subject_code} {self. subject_name}"



class Section(models.Model):
    name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    subjects = models.ManyToManyField(Subject, through="SectionSubjectFaculty")

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name 

class SectionSubjectFaculty(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subjects = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    class Meta:
        ordering = ['faculty__last_name']
        
    def __str__(self):
        return f"{self.faculty.first_name} {self.faculty.last_name}"
 



class Student(models.Model):
    STUDENT_STATUS_CHOICES = [
        ('Regular', 'Regular'),  
        ('Irregular', 'Irregular'), 
    ]
    user = models.OneToOneField(User, null = True, blank=True, on_delete=models.CASCADE)
    student_number = models.CharField(max_length=9, primary_key=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank = True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length = 64)  
    age = models.IntegerField()
    sex = models.CharField(max_length=6)
    contact_no = models.CharField(max_length  = 11)
    status = models.CharField(max_length=20, choices=STUDENT_STATUS_CHOICES, default='Regular')
    profile_picture = models.ImageField(upload_to='profile_picture/', null=True, blank = True)
    Course = models.ForeignKey(Course, on_delete=models.CASCADE) 
    Section = models.ForeignKey(Section, on_delete=models.CASCADE) 

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)
  
    class Meta:
        ordering = ['-updated', '-created'] 
    
    def delete(self, *args, **kwargs):
        # Delete the associated user before deleting the student
        if self.user:
            self.user.delete()
        super().delete(*args, **kwargs)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class EvaluationStatus(models.Model):
    academic_year = models.CharField(max_length=50)
    SEMESTER_CHOICES = (
        ('1st', '1st'),
        ('2nd', '2nd'),
    )
    semester = models.CharField(max_length=5, choices=SEMESTER_CHOICES)
    EVALUATION_STATUS_CHOICES = [
        ('In Progress', 'In Progress'),
        ('Closed', 'Closed'),
    ]
    evaluation_status = models.CharField(
        max_length=12,
        choices=EVALUATION_STATUS_CHOICES,
        default='In Progress'
    )   
    evaluation_end_date = models.DateField(default='2024-11-20')
    evaluation_release_date = models.DateField(default='2024-11-20')

    def __str__(self):
        return f"{self.academic_year} - {self.semester}"

 
class LikertEvaluation(models.Model):
    EVALUATION_STATUS_CHOICES = [
        ('pending', 'Pending'),  # Evaluation is pending
        ('evaluated', 'Evaluated'),  # Evaluation has been completed
    ]
    THE_COURSE_SHOULD = [
        ('Require less task for the credit', 'Require less task for the credit'),  # Evaluation is pending
        ('Require more task for the credit', 'Require more task for the credit'),  # Evaluation has been completed
    ]
    ADMIN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved to Department Head', 'Approved to Department Head'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected',),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    section_subject_faculty = models.ForeignKey(SectionSubjectFaculty, on_delete=models.CASCADE)

    #SUBJECT MATTER CONTENT
    command_and_knowledge_of_the_subject = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    depth_of_mastery = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    practice_in_respective_discipline = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    up_to_date_knowledge = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    integrates_subject_to_practical_circumstances = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    #ORGANIZATION
    organizes_the_subject_matter = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    provides_orientation_on_course_content = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    efforts_of_class_preparation = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    summarizes_main_points = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    monitors_online_class = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    #TEACHER-STUDENT RAPPORT
    holds_interest_of_students =models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    provides_relevant_feedback = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    encourages_participation = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    shows_enthusiasm = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    shows_sense_of_humor = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])

    #TEACHING METHODS
    teaching_methods = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    flexible_learning_strategies = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    student_engagement = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    clear_examples = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    focused_on_objectives = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    #PRESENTATION
    starts_with_motivating_activities = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    speaks_in_clear_and_audible_manner = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    uses_appropriate_medium_of_instruction = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    establishes_online_classroom_environment = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    observes_proper_classroom_etiquette = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    # CLASSROOM MANAGEMENT
    uses_time_wisely = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    gives_ample_time_for_students_to_prepare = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    updates_the_students_of_their_progress = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    demonstrates_leadership_and_professionalism = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    understands_possible_distractions = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])

    #SENSITIVITY and SUPPORT to STUDENTS
    sensitivity_to_student_culture = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    responds_appropriately = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    assists_students_on_concerns = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    guides_the_students_in_accomplishing_tasks = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    extends_consideration_to_students = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    

    requires_less_task_for_credit = models.CharField(
        max_length=50,
        choices=THE_COURSE_SHOULD
    )
    strengths_of_the_faculty = models.TextField()
    other_suggestions_for_improvement = models.TextField()
    comments = models.TextField()
    predicted_sentiment = models.CharField(max_length=50)
    admin_status = models.CharField(
        max_length=30,
        choices=ADMIN_STATUS_CHOICES,
        default='Pending'
    
    )  


    academic_year = models.CharField(max_length=50, null=True, blank=True)
    semester = models.CharField(max_length=50, null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EVALUATION_STATUS_CHOICES, default='pending')

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)


    def calculate_average_rating(self):
        fields_to_average = [
            'command_and_knowledge_of_the_subject',
            'depth_of_mastery',
            'practice_in_respective_discipline',
            'up_to_date_knowledge',
            'integrates_subject_to_practical_circumstances',
            'organizes_the_subject_matter',
            'provides_orientation_on_course_content',
            'efforts_of_class_preparation',
            'summarizes_main_points',
            'monitors_online_class',
            'holds_interest_of_students',
            'provides_relevant_feedback',
            'encourages_participation',
            'shows_enthusiasm',
            'shows_sense_of_humor',
            'teaching_methods',
            'flexible_learning_strategies',
            'student_engagement',
            'clear_examples',
            'focused_on_objectives',
            'starts_with_motivating_activities',
            'speaks_in_clear_and_audible_manner',
            'uses_appropriate_medium_of_instruction',
            'establishes_online_classroom_environment',
            'observes_proper_classroom_etiquette',
            'uses_time_wisely',
            'gives_ample_time_for_students_to_prepare',
            'updates_the_students_of_their_progress',
            'demonstrates_leadership_and_professionalism',
            'understands_possible_distractions',
            'sensitivity_to_student_culture',
            'responds_appropriately',
            'assists_students_on_concerns',
            'guides_the_students_in_accomplishing_tasks',
            'extends_consideration_to_students',
        ]

        # Filter out None values and calculate average
        ratings = [getattr(self, field) for field in fields_to_average if getattr(self, field) is not None]
        
         # Convert ratings to integers
        ratings = [int(rating) for rating in ratings]

        average_rating = sum(ratings) / len(ratings) if ratings else None
        return round(average_rating, 2) 


    def calculate_category_averages(self):
        categories = {
            'Subject Matter Content': [
                'command_and_knowledge_of_the_subject',
                'depth_of_mastery',
                'practice_in_respective_discipline',
                'up_to_date_knowledge',
                'integrates_subject_to_practical_circumstances',
            ],
            'Organization': [
                'organizes_the_subject_matter',
                'provides_orientation_on_course_content',
                'efforts_of_class_preparation',
                'summarizes_main_points',
                'monitors_online_class',
            ],
            'Teacher-Student Rapport': [
                'holds_interest_of_students',
                'provides_relevant_feedback',
                'encourages_participation',
                'shows_enthusiasm',
                'shows_sense_of_humor',
            ],
            'Teaching Methods': [
                'teaching_methods',
                'flexible_learning_strategies',
                'student_engagement',
                'clear_examples',
                'focused_on_objectives',
            ],
            'Presentation': [
                'starts_with_motivating_activities',
                'speaks_in_clear_and_audible_manner',
                'uses_appropriate_medium_of_instruction',
                'establishes_online_classroom_environment',
                'observes_proper_classroom_etiquette',
            ],
            'Classroom Management': [
                'uses_time_wisely',
                'gives_ample_time_for_students_to_prepare',
                'updates_the_students_of_their_progress',
                'demonstrates_leadership_and_professionalism',
                'understands_possible_distractions',
            ],
            'Sensitivity and Support to Students': [
                'sensitivity_to_student_culture',
                'responds_appropriately',
                'assists_students_on_concerns',
                'guides_the_students_in_accomplishing_tasks',
                'extends_consideration_to_students',
            ]
        }

        category_averages = {}
        for category, fields in categories.items():
            ratings = [getattr(self, field) for field in fields if getattr(self, field) is not None]
            ratings = [int(rating) for rating in ratings]  # Ensure ratings are integers
            category_averages[category] = round(sum(ratings) / len(ratings), 2) if ratings else None

        return category_averages

    def sentiment_label(self):
        if self.predicted_sentiment == 1:
            return 'Positive'
        else:
            return 'Negative'
    
    def save(self, *args, **kwargs):
        # Get the current evaluation status
        evaluation_status = EvaluationStatus.objects.first()
        # Check for existing evaluation for the same faculty
        if not LikertEvaluation.objects.filter(
            user=self.user,
            section_subject_faculty=self.section_subject_faculty, # Assuming 'faculty' field exists
            academic_year=evaluation_status.academic_year,  # Add academic year condition
            semester=evaluation_status.semester  # Add semester condition
        ).exists():
            self.status = "evaluated"  # Set status only if no prior evaluation exists
        if evaluation_status:
            self.academic_year = evaluation_status.academic_year
            self.semester = evaluation_status.semester
            self.average_rating = self.calculate_average_rating()
        super().save(*args, **kwargs)


    def get_rating_category(self):
        if self.average_rating is not None:
            if 1.0 <= self.average_rating <= 1.99:
                return "Poor"
            elif 2.0 <= self.average_rating <= 2.99:
                return "Unsatisfactory"
            elif 3.0 <= self.average_rating <= 3.99:
                return "Satisfactory"
            elif 4.0 <= self.average_rating <= 4.99:
                return "Very Satisfactory"
            elif 5.0 <= self.average_rating <= 5.0:
                return "Outstanding"
        return "No Rating"
    
    class Meta:
        ordering = ['-updated', '-created']
    

    def __str__(self):
       return f"{self.section_subject_faculty.subjects} - {self.section_subject_faculty.faculty} - {self.comments}"



class TypeOfEvent(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Event(models.Model):
    title = models.CharField(max_length = 200)
    date = models.DateField()
    time = models.CharField(max_length = 50)
    location = models.CharField(max_length = 200)
    event_picture = models.ImageField(upload_to='event_picture/', null=True, blank = True) 
    event_type = models.ForeignKey(TypeOfEvent, on_delete=models.CASCADE) 
    course_attendees = models.ManyToManyField(Course, blank=True)  
    department_attendees = models.ManyToManyField(Department, blank=True)  
    description = models.TextField(null=True, blank = True)
    author = models.ForeignKey(User, on_delete=models.CASCADE) 
    evaluation_status = models.BooleanField(default=False)
    ADMIN_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    admin_status = models.CharField(
        max_length=12,
        choices=ADMIN_STATUS_CHOICES,
        default='Pending'
    )   
    evaluation_end_datetime = models.DateTimeField(null=True, blank=True)  # End date and time
    academic_year = models.CharField(max_length=50, null=True, blank=True)
    semester = models.CharField(max_length=50, null=True, blank=True)
    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    class Meta:
        ordering = ['-date', '-updated', '-created']

    def __str__(self):
        return f"{self.title}"
    
    def check_evaluation_status(self):
        if self.evaluation_end_datetime and timezone.now() >= self.evaluation_end_datetime:
            self.evaluation_status = False
            self.save()
            
    def get_author_name(self):
        # Check if the author is a faculty member
        if hasattr(self.author, 'faculty'):
            return self.author.faculty.full_name()
        # Check if the author is a student
        elif hasattr(self.author, 'student'):
            return self.author.student.full_name()
        # Default to username if neither faculty nor student
        return self.author.username

    def save(self, *args, **kwargs):
        # Get the current evaluation status
        evaluation_status = EvaluationStatus.objects.first()
        if evaluation_status:
            self.academic_year = evaluation_status.academic_year
            self.semester = evaluation_status.semester
        super().save(*args, **kwargs)

    @property
    def evaluation_identifier(self):
        return "Ongoing" if self.evaluation_status else "Closed"
    
   

class SchoolEventModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    event = models.ForeignKey(Event, on_delete=models.CASCADE) 
    # Overall Evaluation
    meeting_expectation = models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Fair'), (1, 'Poor')])
    attainment_of_the_objectives = models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Fair'), (1, 'Poor')])
    topics_discussed = models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Fair'), (1, 'Poor')])
    input_presentation = models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Fair'), (1, 'Poor')])
    management_team = models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Fair'), (1, 'Poor')])
    venue_and_physical_arrangement = models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Fair'), (1, 'Poor')])
    overall_assessment = models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Fair'), (1, 'Poor')])
    
    suggestions_and_comments = models.TextField()
    predicted_sentiment = models.CharField(max_length=50)

    academic_year = models.CharField(max_length=50, null=True, blank=True)
    semester = models.CharField(max_length=50, null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    def calculate_average_rating(self):
        fields_to_average = [
            'meeting_expectation',
            'attainment_of_the_objectives',
            'topics_discussed',
            'input_presentation',
            'management_team',
            'venue_and_physical_arrangement',
            'overall_assessment'
        ]
         # Filter out None values and calculate average
        ratings = [getattr(self, field) for field in fields_to_average if getattr(self, field) is not None]
        
         # Convert ratings to integers
        ratings = [int(rating) for rating in ratings]

        average_rating = sum(ratings) / len(ratings) if ratings else None
        return round(average_rating, 2) 

    
    def get_rating_category(self):
        if self.average_rating is not None:
            if 1.0 <= self.average_rating <= 1.99:
                return "Poor"
            elif 2.0 <= self.average_rating <= 2.99:
                return "Unsatisfactory"
            elif 3.0 <= self.average_rating <= 3.99:
                return "Satisfactory"
            elif 4.0 <= self.average_rating <= 4.99:
                return "Very Satisfactory"
            elif 5.0 <= self.average_rating <= 5.0:
                return "Outstanding"
        return "No Rating"

    def save(self, *args, **kwargs):
        # Get the current evaluation status
        evaluation_status = EvaluationStatus.objects.first()
        if evaluation_status:
            self.academic_year = evaluation_status.academic_year
            self.semester = evaluation_status.semester
            self.average_rating = self.calculate_average_rating()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.event.title

class WebinarSeminarModel(models.Model):  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE) 
    # Overall Evaluation
    relevance_of_the_activity = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    quality_of_the_activity = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    timeliness = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    
    suggestions_and_comments = models.TextField()

    # Procedure and Content
    attainment_of_the_objective = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    appropriateness_of_the_topic_to_attain_the_objective = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    appropriateness_of_the_searching_methods_used = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])

    topics_to_be_included = models.TextField()

    # Suitability of the present time
    appropriateness_of_the_topic_in_the_present_time = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    usefulness_of_the_topic_discusssed_in_the_activity = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    appropriateness_of_the_searching_methods = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    #Speaker Evaluation 
    displayed_a_thorough_knowledge_of_the_topic = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    explained_activities = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')], db_column='explained_activities')
    able_to_create_a_good_learning_environment = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    able_to_manage_her_time_well = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    demonstrated_keenness_to_the_participant_needs = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])

    timeliness_or_suitability_of_service = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    overall_satisfaction = models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'),
                                        (2, 'Less than expected'), (1, 'Much less than expected')])
    
    academic_year = models.CharField(max_length=50, null=True, blank=True)
    semester = models.CharField(max_length=50, null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)
    predicted_sentiment = models.CharField(max_length=50)

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    def calculate_average_rating(self):
        fields_to_average = [
            'relevance_of_the_activity',
            'quality_of_the_activity',
            'timeliness', 
            'attainment_of_the_objective',
            'appropriateness_of_the_topic_to_attain_the_objective',
            'appropriateness_of_the_searching_methods_used',
            'appropriateness_of_the_topic_in_the_present_time',
            'usefulness_of_the_topic_discusssed_in_the_activity',
            'appropriateness_of_the_searching_methods',
            'displayed_a_thorough_knowledge_of_the_topic',
            'thoroughly_explained_and_processed_the_learning_activities_throughout_the_training',
            'able_to_create_a_good_learning_environment',
            'able_to_manage_her_time_well',
            'demonstrated_keenness_to_the_participant_needs',
            'timeliness_or_suitability_of_service',
            'overall_satisfaction',
        ]
         # Filter out None values and calculate average
        ratings = [getattr(self, field) for field in fields_to_average if getattr(self, field) is not None]
        
         # Convert ratings to integers
        ratings = [int(rating) for rating in ratings]

        average_rating = sum(ratings) / len(ratings) if ratings else None
        return round(average_rating, 2) 
    
    
    def get_rating_category(self):
        if self.average_rating is not None:
            if 1.0 <= self.average_rating <= 1.99:
                return "Poor"
            elif 2.0 <= self.average_rating <= 2.99:
                return "Unsatisfactory"
            elif 3.0 <= self.average_rating <= 3.99:
                return "Satisfactory"
            elif 4.0 <= self.average_rating <= 4.99:
                return "Very Satisfactory"
            elif 5.0 <= self.average_rating <= 5.0:
                return "Outstanding"
        return "No Rating"

    def save(self, *args, **kwargs):
        # Get the current evaluation status
        evaluation_status = EvaluationStatus.objects.first()
        if evaluation_status:
            self.academic_year = evaluation_status.academic_year
            self.semester = evaluation_status.semester
            self.average_rating = self.calculate_average_rating()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.event.title

class FacultyEvaluationQuestions(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)  # Optional field to control question order

    def __str__(self):
        return self.text
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new question
            # Calculate the next order number
            last_question = FacultyEvaluationQuestions.objects.last()
            self.order = 1 if not last_question else last_question.order + 1
        super().save(*args, **kwargs)

class PeertoPeerEvaluationQuestions(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0)  # Optional field to control question order

    def __str__(self):
        return self.text
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new question
            # Calculate the next order number
            last_question = PeertoPeerEvaluationQuestions.objects.last()
            self.order = 1 if not last_question else last_question.order + 1
        super().save(*args, **kwargs)

class SchoolEventQuestions(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0) 

    def __str__(self):
        return self.text
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new question
            # Calculate the next order number
            last_question = SchoolEventQuestions.objects.last()
            self.order = 1 if not last_question else last_question.order + 1
        super().save(*args, **kwargs)

class WebinarSeminarQuestions(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0) 

    def __str__(self):
        return self.text
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new question
            # Calculate the next order number
            last_question = WebinarSeminarQuestions.objects.last()
            self.order = 1 if not last_question else last_question.order + 1
        super().save(*args, **kwargs)

class StakeholderAgency(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class StakeholderFeedbackModel(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True) 
    agency = models.ForeignKey(StakeholderAgency, on_delete=models.CASCADE) 
    email = models.EmailField(max_length=100, null=True, blank=True) 
    purpose = models.CharField(max_length=100, null=True, blank=True) 
    date = models.DateField(null=True, blank=True) 
    staff = models.CharField(max_length=100, null=True, blank=True) 
    
    # Overall Evaluation
    courtesy = models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'),
                                        (2, 'Barely Satisfied'), (1, 'Not satisfied')])
    quality = models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'),
                                        (2, 'Barely Satisfied'), (1, 'Not satisfied')])
    timeliness = models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'),
                                        (2, 'Barely Satisfied'), (1, 'Not satisfied')])
    efficiency = models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'),
                                        (2, 'Barely Satisfied'), (1, 'Not satisfied')])
    cleanliness = models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'),
                                        (2, 'Barely Satisfied'), (1, 'Not satisfied')])
    comfort = models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'),
                                        (2, 'Barely Satisfied'), (1, 'Not satisfied')])
    
    suggestions_and_comments = models.TextField()
    predicted_sentiment = models.CharField(max_length=50)

    academic_year = models.CharField(max_length=50, null=True, blank=True)
    semester = models.CharField(max_length=50, null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    def calculate_average_rating(self):
        fields_to_average = [
            'courtesy',
            'quality',
            'timeliness',
            'efficiency',
            'cleanliness',
            'comfort',
        ]
         # Filter out None values and calculate average
        ratings = [getattr(self, field) for field in fields_to_average if getattr(self, field) is not None]
        
         # Convert ratings to integers
        ratings = [int(rating) for rating in ratings]

        average_rating = sum(ratings) / len(ratings) if ratings else None
        return round(average_rating, 2) 

    
    def get_rating_category(self):
        if self.average_rating is not None:
            if 1.0 <= self.average_rating <= 1.99:
                return "Not Satisfied"
            elif 2.0 <= self.average_rating <= 2.99:
                return "Barely Satisfied"
            elif 3.0 <= self.average_rating <= 3.99:
                return "Moderately Satisfied"
            elif 4.0 <= self.average_rating <= 4.99:
                return "Very Satisfied"
            elif 5.0 <= self.average_rating <= 5.0:
                return "Highly Satisfied"
        return "No Rating"

    def save(self, *args, **kwargs):
        # Get the current evaluation status
        evaluation_status = EvaluationStatus.objects.first()
        if evaluation_status:
            self.academic_year = evaluation_status.academic_year
            self.semester = evaluation_status.semester
            self.average_rating = self.calculate_average_rating()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated', '-created']
    def __str__(self):
        return self.name
    
class StakeholderFeedbackQuestions(models.Model):
    text = models.CharField(max_length=255)
    order = models.IntegerField(default=0) 

    def __str__(self):
        return self.text
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if it's a new question
            # Calculate the next order number
            last_question = StakeholderFeedbackQuestions.objects.last()
            self.order = 1 if not last_question else last_question.order + 1
        super().save(*args, **kwargs)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    attachment = models.FileField(upload_to='message_attachments/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} - From: {self.sender} To: {self.recipient}"

class PeertoPeerEvaluation(models.Model):
    EVALUATION_STATUS_CHOICES = [
        ('pending', 'Pending'),  # Evaluation is pending
        ('evaluated', 'Evaluated'),  # Evaluation has been completed
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    peer = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    #SUBJECT MATTER CONTENT
    command_and_knowledge_of_the_subject = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    depth_of_mastery = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    practice_in_respective_discipline = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    up_to_date_knowledge = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    integrates_subject_to_practical_circumstances = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    #ORGANIZATION
    organizes_the_subject_matter = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    provides_orientation_on_course_content = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    efforts_of_class_preparation = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    summarizes_main_points = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    monitors_online_class = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    #TEACHER-STUDENT RAPPORT
    holds_interest_of_students =models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    provides_relevant_feedback = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    encourages_participation = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    shows_enthusiasm = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    shows_sense_of_humor = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])

    #TEACHING METHODS
    teaching_methods = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    flexible_learning_strategies = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    student_engagement = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    clear_examples = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    focused_on_objectives = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    #PRESENTATION
    starts_with_motivating_activities = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    speaks_in_clear_and_audible_manner = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    uses_appropriate_medium_of_instruction = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    establishes_online_classroom_environment = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    observes_proper_classroom_etiquette = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    
    # CLASSROOM MANAGEMENT
    uses_time_wisely = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    gives_ample_time_for_students_to_prepare = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    updates_the_students_of_their_progress = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    demonstrates_leadership_and_professionalism = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    understands_possible_distractions = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])

    #SENSITIVITY and SUPPORT to STUDENTS
    sensitivity_to_student_culture = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    responds_appropriately = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    assists_students_on_concerns = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    guides_the_students_in_accomplishing_tasks = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    extends_consideration_to_students = models.IntegerField(choices=[(5, 'Outstanding'), (4, 'Very Satisfactory'), (3, 'Satisfactory'),
                                        (2, 'Unsatisfactory'), (1, 'Poor')])
    

    requires_less_task_for_credit = models.BooleanField()
    strengths_of_the_faculty = models.TextField()
    other_suggestions_for_improvement = models.TextField()
    comments = models.TextField()
    predicted_sentiment = models.CharField(max_length=50)


    academic_year = models.CharField(max_length=50, null=True, blank=True)
    semester = models.CharField(max_length=50, null=True, blank=True)
    average_rating = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=EVALUATION_STATUS_CHOICES, default='pending')

    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)


    def calculate_average_rating(self):
        fields_to_average = [
            'command_and_knowledge_of_the_subject',
            'depth_of_mastery',
            'practice_in_respective_discipline',
            'up_to_date_knowledge',
            'integrates_subject_to_practical_circumstances',
            'organizes_the_subject_matter',
            'provides_orientation_on_course_content',
            'efforts_of_class_preparation',
            'summarizes_main_points',
            'monitors_online_class',
            'holds_interest_of_students',
            'provides_relevant_feedback',
            'encourages_participation',
            'shows_enthusiasm',
            'shows_sense_of_humor',
            'teaching_methods',
            'flexible_learning_strategies',
            'student_engagement',
            'clear_examples',
            'focused_on_objectives',
            'starts_with_motivating_activities',
            'speaks_in_clear_and_audible_manner',
            'uses_appropriate_medium_of_instruction',
            'establishes_online_classroom_environment',
            'observes_proper_classroom_etiquette',
            'uses_time_wisely',
            'gives_ample_time_for_students_to_prepare',
            'updates_the_students_of_their_progress',
            'demonstrates_leadership_and_professionalism',
            'understands_possible_distractions',
            'sensitivity_to_student_culture',
            'responds_appropriately',
            'assists_students_on_concerns',
            'guides_the_students_in_accomplishing_tasks',
            'extends_consideration_to_students',
        ]

        # Filter out None values and calculate average
        ratings = [getattr(self, field) for field in fields_to_average if getattr(self, field) is not None]
        
         # Convert ratings to integers
        ratings = [int(rating) for rating in ratings]

        average_rating = sum(ratings) / len(ratings) if ratings else None
        return round(average_rating, 2) 



    def sentiment_label(self):
        if self.predicted_sentiment == 1:
            return 'Positive'
        else:
            return 'Negative'
    
    def save(self, *args, **kwargs):
        # Get the current evaluation status
        evaluation_status = EvaluationStatus.objects.first()
        # Check for existing evaluation for the same faculty
        if not PeertoPeerEvaluation.objects.filter(
            user=self.user,
            peer=self.peer, # Assuming 'faculty' field exists
            academic_year=evaluation_status.academic_year,  # Add academic year condition
            semester=evaluation_status.semester  # Add semester condition
        ).exists():
            self.status = "evaluated"  # Set status only if no prior evaluation exists
        if evaluation_status:
            self.academic_year = evaluation_status.academic_year
            self.semester = evaluation_status.semester
            self.average_rating = self.calculate_average_rating()
        super().save(*args, **kwargs)

    def get_rating_category(self):
        if self.average_rating is not None:
            if 1.0 <= self.average_rating <= 1.49:
                return "Poor"
            elif 1.5 <= self.average_rating <= 2.49:
                return "Fair"
            elif 2.5 <= self.average_rating <= 3.49:
                return "Good"
            elif 3.5 <= self.average_rating <= 4.49:
                return "Very Good"
            elif 4.5 <= self.average_rating <= 5.0:
                return "Outstanding"
        return "No Rating"

    
    class Meta:
        ordering = ['-updated', '-created']
    

    def __str__(self):
       return f"{self.peer} - {self.comments}"
