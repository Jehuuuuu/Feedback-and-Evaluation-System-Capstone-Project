from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Feedbacksystem.models import Course, Section, SectionSubjectFaculty, Faculty, Department, Student, Subject, LikertEvaluation, EvaluationStatus, Event, SchoolEventModel, FacultyEvaluationQuestions, SchoolEventQuestions, WebinarSeminarModel, WebinarSeminarQuestions, StakeholderFeedbackModel, StakeholderFeedbackQuestions
from .forms import TeacherForm, StudentForm, CourseForm, SectionForm, SectionSubjectFacultyForm, SubjectForm, StudentRegistrationForm, StudentLoginForm, LikertEvaluationForm, FacultyRegistrationForm, FacultyLoginForm, EvaluationStatusForm, DepartmentForm, EventCreationForm, SchoolEventForm, WebinarSeminarForm, StudentProfileForm, EditQuestionForm, EditSchoolEventQuestionForm,  WebinarSeminarForm, EditWebinarSeminarQuestionForm, StakeholderFeedbackForm
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg, Value
from django.http import Http404
from .utils import load_prediction_models, single_prediction
from .filters import EvaluationFilter, FacultyFilter, StudentFilter, UserFilter, EventFilter, SectionFilter, SubjectFilter, StakeholderFilter, LikertEvaluationFilter
from .resources import StudentResource
from tablib import Dataset
from django.contrib.auth.decorators import login_required
from .decorators import allowed_users
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
import json
from django.core.exceptions import ObjectDoesNotExist
import csv
from django.utils import timezone
from django.db.models.functions import Concat
import qrcode
from django.utils.timezone import now
from datetime import timedelta
from collections import defaultdict
from statistics import mean
from django.db import models  # Add this import at the top

ITEMS_PER_PAGE = 5
            # ------------------------------------------------------
            #                Login-Page Views
            # ------------------------------------------------------
def signin(request):
    registration_form = StudentRegistrationForm()
    login_form = StudentLoginForm()

    if request.method == 'POST':

        if 'signin' in request.POST:
            # Handle login form submission
            login_form = StudentLoginForm(request.POST)
            if login_form.is_valid():
               student_number = login_form.cleaned_data['student_number']
               password = login_form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=student_number, password=password)

            if user is not None:
                # Login the user
                login(request, user)
                return redirect('home')  # Redirect to the home page or any desired URL after successful login
            else:

                try:
                        user = User.objects.get(username=student_number)
                except User.DoesNotExist:
                        messages.error(request, 'Student number is not registered.')
                
                else:
                        messages.error(request, 'Invalid password.')
               
              
        elif 'register' in request.POST:
            # Handle registration form submission
            registration_form = StudentRegistrationForm(request.POST)
            if registration_form.is_valid():
                user = registration_form.save()
                group = Group.objects.get(name = 'student')
                user.groups.add(group)
                messages.success(request, 'Registration successful!')
                return redirect('signin')  # Redirect to the home page or any desired URL after successful registration
            else:
                messages.success(request, 'Student with this student number does not exist. Please contact the admin to create an account.')
                return redirect('signin')                                      

    context = {'registration_form': registration_form, 'login_form': login_form,}
    
    return render(request, 'pages/login.html', context)

def adminlogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")
            return render(request, 'pages/adminlogin.html', {})

        if user.is_superuser:
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('admin')
            else:
                messages.error(request, "Incorrect Password")
        else:
            messages.error(request, "You are not authorized to log in as an admin")


    context = {}
    return render(request, 'pages/adminlogin.html', context)


def facultylogin(request):
    registration_form = FacultyRegistrationForm()
    login_form = FacultyLoginForm()

    if request.method == 'POST':

        if 'signin' in request.POST:
            # Handle login form submission
            login_form = FacultyLoginForm(request.POST)
            if login_form.is_valid():
               email = login_form.cleaned_data['email']
               password = login_form.cleaned_data['password']

            # Authenticate the user
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Login the user
                login(request, user)
                return redirect('facultydashboard')  # Redirect to the home page or any desired URL after successful login
            else:

                try:
                        user = User.objects.get(username=email)
                except User.DoesNotExist:
                        messages.error(request, 'Your email is not registered.')
                
                else:
                        messages.error(request, 'Invalid password.')
               
              
        elif 'register' in request.POST:
            # Handle registration form submission
            registration_form = FacultyRegistrationForm(request.POST)
            if registration_form.is_valid():
                user = registration_form.save()
                group = Group.objects.get(name = 'faculty')
                user.groups.add(group)
                messages.success(request, 'Registration successful!')
                return redirect('facultylogin')  # Redirect to the home page or any desired URL after successful registration
            else:
                messages.error(request, 'Faculty with this email does not exist. Please contact the admin to create an account.')
                return redirect('facultylogin') 

    context = {'registration_form': registration_form, 'login_form': login_form,}
    
    return render(request, 'pages/facultylogin.html', context)

def stakeholder_feedback_form(request):
    questions = StakeholderFeedbackQuestions.objects.all()
    form = StakeholderFeedbackForm()
    if request.method == 'POST':
        form = StakeholderFeedbackForm(request.POST)
        if form.is_valid():
                 # Process the evaluation form
            name = form.cleaned_data['name']
            agency = form.cleaned_data['agency']
            email = form.cleaned_data['email']
            purpose = form.cleaned_data['purpose']
            date = form.cleaned_data['date']
            staff = form.cleaned_data['staff']
            courtesy = form.cleaned_data['courtesy']
            quality = form.cleaned_data['quality']
            timeliness = form.cleaned_data['timeliness']
            efficiency = form.cleaned_data['efficiency']
            cleanliness = form.cleaned_data['cleanliness']
            comfort = form.cleaned_data['comfort']
            suggestions_and_comments = form.cleaned_data['suggestions_and_comments']
            # Save the data to database
            form = StakeholderFeedbackModel(
                name=name,
                agency=agency,
                email=email,
                purpose=purpose,
                date=date,
                staff=staff,
                courtesy=courtesy,
                quality=quality,
                timeliness=timeliness,
                efficiency=efficiency,
                cleanliness=cleanliness,
                comfort=comfort,
                suggestions_and_comments=suggestions_and_comments,
            )           
            form.save()
            print(questions)
            messages.success(request, 'Form Submitted Successfully')
            return redirect('signin')
    context = {'questions': questions, 'form': form}

    return render(request, 'pages/stakeholder_feedback_form.html', context)

def makeqrcode(destination_url):
    image = qrcode.make(destination_url)
    name = "stakeholderform.jpg"
    path = 'Feedbacksystem/static/images/'  
    image.save(path + name)

def get_code(request):
    if request.method == 'GET':
        destination_url = "http://127.0.0.1:8000/stakeholder_feedback_form"
        makeqrcode(destination_url)

        return render(request, 'pages/qrcode.html')


            # ------------------------------------------------------
            #                Student-Page Views
            # ------------------------------------------------------


@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def home(request):
    user = request.user
    is_president = request.user.groups.filter(name='society president').exists()  # Check if the user is in the "student" group
    evaluation_status = EvaluationStatus.objects.first()
    student = Student.objects.filter(student_number=request.user.username).first() 
    courses = student.Course 
    #pending events to display
    events = Event.objects.filter(course_attendees=courses).distinct()  # Get events related to those courses
    # Get evaluated event IDs by the current user
     # Get evaluated event IDs by the current user for SchoolEventModel
    evaluated_school_event_ids = SchoolEventModel.objects.filter(user=user).values_list('event_id', flat=True)
    
    # Get evaluated event IDs by the current user for WebinarSeminarModel
    evaluated_webinar_event_ids = WebinarSeminarModel.objects.filter(user=user).values_list('event_id', flat=True)

    # Combine evaluated event IDs from both models
    evaluated_event_ids = list(evaluated_school_event_ids) + list(evaluated_webinar_event_ids)
    
    # Exclude events that have been evaluated
    current_time = timezone.now()
    upcoming_events = events.filter(date__gt=current_time, evaluation_status=False)  
    past_events = events.filter(date__lt=current_time, evaluation_status=False)  
    unevaluated_events = events.exclude(id__in=evaluated_event_ids).exclude(id__in=past_events).exclude(id__in=upcoming_events) 


    #faculty evaluated count
       # Fetch section subjects faculty based on the student's section
    section_subjects_faculty = SectionSubjectFaculty.objects.filter(section=student.Section)

    # Count the total number of unique faculty members
    total_faculty = section_subjects_faculty.values('faculty').distinct().count()
   
    pending_count = 0
    completed_count = 0

    # Iterate over each section_subject_faculty and check if evaluation exists
    for section_subject_faculty in section_subjects_faculty:
        try:
            # Check if the user has submitted an evaluation for this faculty
            evaluation_status = EvaluationStatus.objects.first()
            LikertEvaluation.objects.get(user=request.user, section_subject_faculty=section_subject_faculty, academic_year=evaluation_status.academic_year,
            semester=evaluation_status.semester)
            completed_count += 1  # Increment completed count if evaluation exists
        except:
            pass 
      
    #pagination
    paginator = Paginator(unevaluated_events, 4) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'evaluation_status': evaluation_status, 'student': student, 'unevaluated_events': unevaluated_events, 'page_obj': page_obj, 'completed_count': completed_count, 'total_faculty': total_faculty, 'is_president': is_president}
    return render(request, 'pages/home.html', context)
    

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def student_profile(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    user = request.user
    user_groups = user.groups.all()
    is_president = request.user.groups.filter(name='society president').exists()
    # Example of checking if the user is in a specific group, e.g., "society president"
    is_society_president = user_groups.filter(name="society president").exists()
    evaluation_status = EvaluationStatus.objects.first()
    section_subjects_faculty = SectionSubjectFaculty.objects.filter(section=student.Section)

        # Create an empty dictionary to store evaluation status for each faculty
    evaluation_status_list = []

    # Iterate over each section_subject_faculty
    for section_subject_faculty in section_subjects_faculty:
        try:
            # Check if the user has submitted an evaluation for this faculty  
            evaluation = LikertEvaluation.objects.get(user=request.user, section_subject_faculty=section_subject_faculty, academic_year=evaluation_status.academic_year,
            semester=evaluation_status.semester)
            evaluation_status_list.append((section_subject_faculty.subjects, section_subject_faculty.faculty, evaluation.status))
            print(evaluation_status_list)  # Debugging line to check if it's defined

        except LikertEvaluation.DoesNotExist:
            # If evaluation doesn't exist, set status to 'Pending'
            evaluation_status_list.append((section_subject_faculty.subjects, section_subject_faculty.faculty, 'Pending'))
            
    context = {'student': student, 'section_subjects_faculty': section_subjects_faculty, 'evaluation_status_list': evaluation_status_list, 'is_society_president': is_society_president, 'is_president': is_president}
    return render(request, 'pages/student_profile.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def edit_student_profile(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    user = request.user.student
    is_president = request.user.groups.filter(name='society president').exists()
    form = StudentProfileForm(instance = user)
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            form.save(commit=True)  # Ensure commit is set to True to save to the database
            messages.success(request, 'Profile Updated Successfully')
            return redirect('student_profile')

    return render(request, 'pages/edit_student_profile.html', {'student': student, 'form': form, 'is_president': is_president})


@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def facultyeval(request):
    evaluation_status = EvaluationStatus.objects.first()
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()
    section_subjects_faculty = SectionSubjectFaculty.objects.filter(section=student.Section)
    
    return render(request, 'pages/facultyeval.html', {'student': student, 'section_subjects_faculty': section_subjects_faculty, 'evaluation_status': evaluation_status, 'is_president': is_president})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def evaluate_subject_faculty(request,pk):
    section_subject_faculty = get_object_or_404(SectionSubjectFaculty, pk=pk)
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()
    section_subjects_faculty = SectionSubjectFaculty.objects.filter(section=student.Section)
    questions = FacultyEvaluationQuestions.objects.all().order_by('order')
    user = request.user
    evaluation_status = EvaluationStatus.objects.first()
    user_evaluations = LikertEvaluation.objects.filter(
        user=request.user,
        section_subject_faculty=section_subject_faculty,
        academic_year=evaluation_status.academic_year,
        semester=evaluation_status.semester
    )
   
    if request.method == 'POST':
        form = LikertEvaluationForm(request.POST)
        if form.is_valid():
            # Process the evaluation form
            command_and_knowledge_of_the_subject = form.cleaned_data['command_and_knowledge_of_the_subject']
            depth_of_mastery = form.cleaned_data['depth_of_mastery']
            practice_in_respective_discipline = form.cleaned_data['practice_in_respective_discipline']
            up_to_date_knowledge = form.cleaned_data['up_to_date_knowledge']
            integrates_subject_to_practical_circumstances = form.cleaned_data['integrates_subject_to_practical_circumstances']

            organizes_the_subject_matter = form.cleaned_data['organizes_the_subject_matter']
            provides_orientation_on_course_content = form.cleaned_data['provides_orientation_on_course_content']
            efforts_of_class_preparation = form.cleaned_data['efforts_of_class_preparation']
            summarizes_main_points = form.cleaned_data['summarizes_main_points']
            monitors_online_class = form.cleaned_data['monitors_online_class']

            holds_interest_of_students = form.cleaned_data['holds_interest_of_students']
            provides_relevant_feedback = form.cleaned_data['provides_relevant_feedback']
            encourages_participation = form.cleaned_data['encourages_participation']
            shows_enthusiasm = form.cleaned_data['shows_enthusiasm']
            shows_sense_of_humor = form.cleaned_data['shows_sense_of_humor']

            teaching_methods = form.cleaned_data['teaching_methods']
            flexible_learning_strategies = form.cleaned_data['flexible_learning_strategies']
            student_engagement = form.cleaned_data['student_engagement']
            clear_examples = form.cleaned_data['clear_examples']
            focused_on_objectives = form.cleaned_data['focused_on_objectives']

            starts_with_motivating_activities = form.cleaned_data['starts_with_motivating_activities']
            speaks_in_clear_and_audible_manner = form.cleaned_data['speaks_in_clear_and_audible_manner']
            uses_appropriate_medium_of_instruction = form.cleaned_data['uses_appropriate_medium_of_instruction']
            establishes_online_classroom_environment = form.cleaned_data['establishes_online_classroom_environment']
            observes_proper_classroom_etiquette = form.cleaned_data['observes_proper_classroom_etiquette']

            uses_time_wisely = form.cleaned_data['uses_time_wisely']
            gives_ample_time_for_students_to_prepare = form.cleaned_data['gives_ample_time_for_students_to_prepare']
            updates_the_students_of_their_progress = form.cleaned_data['updates_the_students_of_their_progress']
            demonstrates_leadership_and_professionalism = form.cleaned_data['demonstrates_leadership_and_professionalism']
            understands_possible_distractions = form.cleaned_data['understands_possible_distractions']

            sensitivity_to_student_culture = form.cleaned_data['sensitivity_to_student_culture']
            responds_appropriately = form.cleaned_data['responds_appropriately']
            assists_students_on_concerns = form.cleaned_data['assists_students_on_concerns']
            guides_the_students_in_accomplishing_tasks = form.cleaned_data['guides_the_students_in_accomplishing_tasks']
            extends_consideration_to_students = form.cleaned_data['extends_consideration_to_students']


           # Extract the cleaned data from the form
            credit_task_preference = form.cleaned_data['credit_task_preference']
            
            # Convert the choice to a boolean value
            requires_less_task_for_credit = credit_task_preference == 'True'

            strengths_of_the_faculty = form.cleaned_data['strengths_of_the_faculty']
            other_suggestions_for_improvement =  form.cleaned_data['other_suggestions_for_improvement']
            comments = form.cleaned_data['comments']
            predicted_sentiment = single_prediction(comments)

          
            # Save the data to the database
            # Create the LikertEvaluation instance
            evaluation_instance = LikertEvaluation(
                section_subject_faculty=section_subject_faculty,
                user=user,
                command_and_knowledge_of_the_subject=command_and_knowledge_of_the_subject,
                depth_of_mastery=depth_of_mastery,
                practice_in_respective_discipline=practice_in_respective_discipline,
                up_to_date_knowledge=up_to_date_knowledge,
                integrates_subject_to_practical_circumstances=integrates_subject_to_practical_circumstances,
                organizes_the_subject_matter=organizes_the_subject_matter,
                provides_orientation_on_course_content=provides_orientation_on_course_content,
                efforts_of_class_preparation=efforts_of_class_preparation,
                summarizes_main_points=summarizes_main_points,
                monitors_online_class=monitors_online_class,
                holds_interest_of_students=holds_interest_of_students,
                provides_relevant_feedback=provides_relevant_feedback,
                encourages_participation=encourages_participation,
                shows_enthusiasm=shows_enthusiasm,
                shows_sense_of_humor=shows_sense_of_humor,
                teaching_methods=teaching_methods,
                flexible_learning_strategies=flexible_learning_strategies,
                student_engagement=student_engagement,
                clear_examples=clear_examples,
                focused_on_objectives=focused_on_objectives,
                starts_with_motivating_activities=starts_with_motivating_activities,
                speaks_in_clear_and_audible_manner=speaks_in_clear_and_audible_manner,
                uses_appropriate_medium_of_instruction=uses_appropriate_medium_of_instruction,
                establishes_online_classroom_environment=establishes_online_classroom_environment,
                observes_proper_classroom_etiquette=observes_proper_classroom_etiquette,
                uses_time_wisely=uses_time_wisely,
                gives_ample_time_for_students_to_prepare=gives_ample_time_for_students_to_prepare,
                updates_the_students_of_their_progress=updates_the_students_of_their_progress,
                demonstrates_leadership_and_professionalism=demonstrates_leadership_and_professionalism,
                understands_possible_distractions=understands_possible_distractions,
                sensitivity_to_student_culture=sensitivity_to_student_culture,
                responds_appropriately=responds_appropriately,
                assists_students_on_concerns=assists_students_on_concerns,
                guides_the_students_in_accomplishing_tasks=guides_the_students_in_accomplishing_tasks,
                extends_consideration_to_students=extends_consideration_to_students,
                requires_less_task_for_credit=requires_less_task_for_credit,
                strengths_of_the_faculty=strengths_of_the_faculty,
                other_suggestions_for_improvement=other_suggestions_for_improvement,
                comments=comments,
                predicted_sentiment=predicted_sentiment
            )

            # Attempt to save the instance
            try:
                evaluation_instance.save()
                messages.success(request, 'Evaluation submitted successfully.')
                return redirect('facultyeval')  # Redirect to a success page
            except Exception as e:
                # If the save fails, print the error message and return a failure message
                print(f"Error saving evaluation: {e}")
                messages.error(request, 'Failed to submit evaluation. Please try again.')

        else:
            # If the form is invalid, print form errors
            print(form.errors)
            messages.error(request, 'There was an error with your submission. Please check your input.')

    else:
        form = LikertEvaluationForm()
    context = { 'form': form, 'section_subject_faculty': section_subject_faculty, 'section_subjects_faculty': section_subjects_faculty, 'student': student, 'questions': questions, 'user_evaluations':user_evaluations, 'is_president': is_president}
    return render(request, 'pages/evaluate_subject_faculty.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def eventhub(request):
    user = request.user
    is_president = request.user.groups.filter(name='society president').exists()
    student = Student.objects.filter(student_number=request.user.username).first()
    courses = student.Course  # Get all courses the student is enrolled in
    events = Event.objects.filter(course_attendees=courses).distinct()  # Get events related to those courses
      # Get evaluated event IDs by the current user
     # Get evaluated event IDs by the current user for SchoolEventModel
    evaluated_school_event_ids = SchoolEventModel.objects.filter(user=user).values_list('event_id', flat=True)
    
    # Get evaluated event IDs by the current user for WebinarSeminarModel
    evaluated_webinar_event_ids = WebinarSeminarModel.objects.filter(user=user).values_list('event_id', flat=True)

    # Combine evaluated event IDs from both models
    evaluated_event_ids = list(evaluated_school_event_ids) + list(evaluated_webinar_event_ids)
     # Get current time
    current_time = timezone.now()
    upcoming_events = events.filter(date__gt=current_time, evaluation_status=False)  # Events in the future
    # Past events with closed evaluation
    past_events = events.filter(date__lt=current_time, evaluation_status=False)  # Past events with evaluation closed   
    # Exclude events that have been evaluated
    unevaluated_events = events.exclude(id__in=evaluated_event_ids).exclude(id__in=past_events).exclude(id__in=upcoming_events).order_by('-date') 
    return render(request, 'pages/eventhub.html', {'student': student, 'unevaluated_events': unevaluated_events, 'past_events': past_events, 'upcoming_events': upcoming_events, 'is_president': is_president})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def eventhub_upcoming(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()
    courses = student.Course  # Get all courses the student is enrolled in
    events = Event.objects.filter(course_attendees=courses).distinct()  # Get events related to those courses
    
    current_time = timezone.now()
    upcoming_events = events.filter(date__gt=current_time, evaluation_status=False)  # Events in the future

    return render(request, 'pages/eventhub_upcoming.html', {'student': student,'upcoming_events': upcoming_events, 'is_president': is_president})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def eventhub_evaluated(request):
    user = request.user
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()
    courses = student.Course  # Get all courses the student is enrolled in
    events = Event.objects.filter(course_attendees=courses).distinct()  # Get events related to those courses
      # Get evaluated event IDs by the current user
     # Get evaluated event IDs by the current user for SchoolEventModel
    evaluated_school_event_ids = SchoolEventModel.objects.filter(user=user).values_list('event_id', flat=True)
    
    # Get evaluated event IDs by the current user for WebinarSeminarModel
    evaluated_webinar_event_ids = WebinarSeminarModel.objects.filter(user=user).values_list('event_id', flat=True)

    # Combine evaluated event IDs from both models
    evaluated_event_ids = list(evaluated_school_event_ids) + list(evaluated_webinar_event_ids)
    
    # Exclude events that have been evaluated
    evaluated_events = events.filter(id__in=evaluated_event_ids).order_by('-date')[:10]
    return render(request, 'pages/eventhub_evaluated.html', {'student': student, 'evaluated_events': evaluated_events, 'is_president': is_president})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def eventhub_closed(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()
    courses = student.Course  # Get all courses the student is enrolled in
    events = Event.objects.filter(course_attendees=courses).distinct()  # Get events related to those courses

    # Get current time
    current_time = timezone.now()
    # Past events with closed evaluation
    past_events = events.filter(date__lt=current_time, evaluation_status=False)  # Past events with evaluation closed   
    return render(request, 'pages/eventhub_closed.html', {'student': student, 'past_events': past_events, 'is_president': is_president})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def event_detail(request, pk):
    user = request.user
    is_president = request.user.groups.filter(name='society president').exists()  
    student = Student.objects.filter(student_number=request.user.username).first()
    event = Event.objects.get(pk=pk)
    questions = SchoolEventQuestions.objects.all().order_by('order')
    if event.event_type.name == 'School Event':
        form = SchoolEventForm()
        if request.method == 'POST':
            form = SchoolEventForm(request.POST)
            if form.is_valid():
                 # Process the evaluation form
                meeting_expectation = form.cleaned_data['meeting_expectation']
                attainment_of_the_objectives = form.cleaned_data['attainment_of_the_objectives']
                topics_discussed = form.cleaned_data['topics_discussed']
                input_presentation = form.cleaned_data['input_presentation']
                management_team = form.cleaned_data['management_team']
                venue_and_physical_arrangement = form.cleaned_data['venue_and_physical_arrangement']
                overall_assessment = form.cleaned_data['overall_assessment']
                suggestions_and_comments = form.cleaned_data['suggestions_and_comments']
                # Save the data to database
                form = SchoolEventModel(
                    user=user,
                    event=event,
                    meeting_expectation=meeting_expectation,
                    attainment_of_the_objectives=attainment_of_the_objectives,
                    topics_discussed=topics_discussed,
                    input_presentation=input_presentation,
                    management_team=management_team,
                    venue_and_physical_arrangement=venue_and_physical_arrangement,
                    overall_assessment=overall_assessment,
                    suggestions_and_comments=suggestions_and_comments,
                )
                form.save()
            messages.success(request, 'Evaluation submitted successfully.')
            return redirect('eventhub')
        return render(request, 'pages/school_event_form.html', context = {'event': event, 'form': form, 'student': student, 'questions': questions, 'is_president': is_president})
    
    elif event.event_type.name == 'Webinar/Seminar':
        questions = WebinarSeminarQuestions.objects.all().order_by('order')
        form = WebinarSeminarForm()  # Assuming WebinarSeminarForm is similar to SchoolEventForm
        if request.method == 'POST':
            form = WebinarSeminarForm(request.POST)
            if form.is_valid():
                # Process Webinar/Seminar evaluation
                relevance_of_the_activity = form.cleaned_data['relevance_of_the_activity']

                quality_of_the_activity = form.cleaned_data['quality_of_the_activity']

                timeliness = form.cleaned_data['timeliness']

                suggestions_and_comments = form.cleaned_data['suggestions_and_comments']

                attainment_of_the_objective = form.cleaned_data['attainment_of_the_objective']

                appropriateness_of_the_topic_to_attain_the_objective = form.cleaned_data['appropriateness_of_the_topic_to_attain_the_objective']

                appropriateness_of_the_searching_methods_used = form.cleaned_data['appropriateness_of_the_searching_methods_used']
                
                topics_to_be_included = form.cleaned_data['topics_to_be_included']

                appropriateness_of_the_topic_in_the_present_time = form.cleaned_data['appropriateness_of_the_topic_in_the_present_time']

                usefulness_of_the_topic_discusssed_in_the_activity = form.cleaned_data['usefulness_of_the_topic_discusssed_in_the_activity']

                appropriateness_of_the_searching_methods = form.cleaned_data['appropriateness_of_the_searching_methods']

                displayed_a_thorough_knowledge_of_the_topic = form.cleaned_data['displayed_a_thorough_knowledge_of_the_topic']

                thoroughly_explained_and_processed_the_learning_activities_throughout_the_training = form.cleaned_data['thoroughly_explained_and_processed_the_learning_activities_throughout_the_training']

                able_to_create_a_good_learning_environment = form.cleaned_data['able_to_create_a_good_learning_environment']

                able_to_manage_her_time_well = form.cleaned_data['able_to_manage_her_time_well']

                demonstrated_keenness_to_the_participant_needs = form.cleaned_data['demonstrated_keenness_to_the_participant_needs']

                timeliness_or_suitability_of_service = form.cleaned_data['timeliness_or_suitability_of_service']

                overall_satisfaction = form.cleaned_data['overall_satisfaction']

                # Save the data to the database
                form = WebinarSeminarModel(
                    user=user,
                    
                    event=event,

                    relevance_of_the_activity=relevance_of_the_activity,
                    
                    quality_of_the_activity=quality_of_the_activity,

                    timeliness=timeliness,

                    suggestions_and_comments=suggestions_and_comments,

                    attainment_of_the_objective=attainment_of_the_objective,

                    appropriateness_of_the_topic_to_attain_the_objective = appropriateness_of_the_topic_to_attain_the_objective,

                    appropriateness_of_the_searching_methods_used=appropriateness_of_the_searching_methods_used,

                    topics_to_be_included=topics_to_be_included,

                    appropriateness_of_the_topic_in_the_present_time=appropriateness_of_the_topic_in_the_present_time,

                    usefulness_of_the_topic_discusssed_in_the_activity=usefulness_of_the_topic_discusssed_in_the_activity,

                    appropriateness_of_the_searching_methods=appropriateness_of_the_searching_methods,

                    displayed_a_thorough_knowledge_of_the_topic=displayed_a_thorough_knowledge_of_the_topic,

                    thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=thoroughly_explained_and_processed_the_learning_activities_throughout_the_training,

                    able_to_create_a_good_learning_environment=able_to_create_a_good_learning_environment,

                    able_to_manage_her_time_well=able_to_manage_her_time_well,

                    demonstrated_keenness_to_the_participant_needs=demonstrated_keenness_to_the_participant_needs,

                    timeliness_or_suitability_of_service=timeliness_or_suitability_of_service,

                    overall_satisfaction=overall_satisfaction,
                )
                form.save()
                messages.success(request, 'Evaluation submitted successfully.')
                return redirect('eventhub')

        return render(request, 'pages/webinar_seminar_form.html', context={'event': event, 'form': form, 'student': student, 'questions': questions, 'is_president': is_president})
    else:
        # Handle other event types
        pass

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def about(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()  
    return render(request, 'pages/about.html', {'student': student, 'is_president': is_president})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def contactUs(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()  
    return render(request, 'pages/contactUs.html', {'student': student, 'is_president': is_president})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['student', 'society president'])
def suggestionbox(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    return render(request, 'pages/suggestionbox.html', {'student': student})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['society president'])
def society_president_events(request):
     user = request.user
     student = Student.objects.filter(student_number=request.user.username).first()
     is_president = request.user.groups.filter(name='society president').exists()     
     event = Event.objects.filter(author=user).order_by('-updated')
     form = EventCreationForm()
     if request.method == 'POST':
        form = EventCreationForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.author = request.user  # Set the author to the currently logged-in user
            form.save()
            #event = form.save(commit=False)
            #event.published_by = faculty 
            #event.save()

            return redirect('society_president_events')
        else:
            # Print form errors for debugging
            print(form.errors)
           
     context = {'event': event, 'student': student, 'form':form, 'is_president': is_president}
     return render(request, 'pages/society_president_events.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['society president'])
def president_view_event_evaluations(request, pk):
    student = Student.objects.filter(student_number=request.user.username).first()
    is_president = request.user.groups.filter(name='society president').exists()    
    event = get_object_or_404(Event, pk=pk)
        # Filter evaluations from both SchoolEventModel and WebinarSeminarModel
    school_event_evaluations = list(SchoolEventModel.objects.filter(event=event))
    webinar_seminar_evaluations = list(WebinarSeminarModel.objects.filter(event=event))

    # Combine the results into one list
    evaluations = school_event_evaluations + webinar_seminar_evaluations
    
    paginator = Paginator(evaluations, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'event': event,
        'evaluations': evaluations,
        'student':student,
        'is_president': is_president,
        'page_obj': page_obj
    }

    return render(request, 'pages/president_view_event_evaluations.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['society president'])
def view_society_president_event_evaluations(request, pk):
    # Try to get the event from SchoolEventModel or WebinarSeminarModel
    try:
        event_form_details = SchoolEventModel.objects.get(pk=pk)
        event_type = 'school_event'
    except SchoolEventModel.DoesNotExist:
        try:
            event_form_details = WebinarSeminarModel.objects.get(pk=pk)
            event_type = 'webinar_event'
        except WebinarSeminarModel.DoesNotExist:
            # If no event is found in either model, handle the error
            return HttpResponse("Event not found.")

    # Render different templates based on the event type
    if event_type == 'school_event':
        questions = SchoolEventQuestions.objects.all().order_by('order')

        excellent_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=5
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=5
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=5
        ).count()

        very_satisfactory_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=4
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=4
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=4
        ).count()

        satisfactory_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=3
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=3
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=3
        ).count()

        fair_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=2
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=2
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=2
        ).count()

        poor_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=1
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=1
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=1
        ).count()

        template_name = 'pages/view_society_president_schoolevent_evaluations.html'
        
    elif event_type == 'webinar_event':
        questions = WebinarSeminarQuestions.objects.all().order_by('order')

        excellent_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=5
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=5
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=5
        ).count()

        very_satisfactory_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=4
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=4
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=4
        ).count()

        satisfactory_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=3
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=3
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=3
        ).count()

        fair_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=2
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=2
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=2
        ).count()

        poor_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=1
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=1
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=1
        ).count()

       
        template_name = 'pages/view_society_president_webinar_evaluations.html'
    else:
        return HttpResponse("Invalid event type.")


    return render(request, template_name, {'event_form_details': event_form_details, 'faculty': faculty, 'questions': questions, 'excellent_count': excellent_count, 'very_satisfactory_count': very_satisfactory_count, 'satisfactory_count': satisfactory_count, 'fair_count': fair_count, 'poor_count': poor_count})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['society president'])
def president_edit_event_evaluations(request, pk):
    event = Event.objects.get(pk=pk)
    form = EventCreationForm(instance=event)
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save(commit=True)
            return redirect('society_president_events')

           
    context = {'event': event, 'form':form}
    return render(request, 'pages/president_edit_event_evaluations.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['society president'])
def president_delete_event_evaluations(request, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
            event.delete()
            return redirect('society_president_events')

    return render(request, 'pages/delete.html', {'obj':event})

def studentlogout(request):
    logout(request)
    return redirect('signin')


            # ------------------------------------------------------
            #                Admin-Page Views
            # ------------------------------------------------------


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def admin(request):
    student = Student.objects.all()
    course = Course.objects.all()
    section = Section.objects.all()
    faculty = Faculty.objects.all()
    subject = Subject.objects.all()
    user = User.objects.all()
    departments = Department.objects.all()

    total_students = student.count()
    total_courses = course.count()
    total_sections = section.count()
    total_faculty = faculty.count()
    total_subject = subject.count()
    total_user = user.count()

    evaluation_status = EvaluationStatus.objects.first()  # Assuming there's only one status entry
    
    
    if request.method == 'POST':
        form = EvaluationStatusForm(request.POST, instance=evaluation_status)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status updated successfully')
    else:
        form = EvaluationStatusForm(instance=evaluation_status)
    
 # Filter the evaluations based on the selected academic year and semester
    filterset = LikertEvaluationFilter(request.GET, queryset=LikertEvaluation.objects.all())

    # Apply filtering and collect data
       # Check if any filters are applied, or it's the "All" option
    if not request.GET or (request.GET.get('academic_year') == '' and request.GET.get('semester') == ''):
        # If no filters, get all-time statistics
        data = LikertEvaluation.objects.all()
    else:
        # Otherwise, apply the filters
        data = filterset.qs

    positive_count = data.filter(predicted_sentiment='Positive').count()
    negative_count = data.filter(predicted_sentiment='Negative').count()

    # Prepare data for Chart.js
    chart_data = {
        'labels': ['Positive', 'Negative'],
        'data': [positive_count, negative_count],
    }

    context = {'student': student, 
               'course': course,
               'section': section,
               'faculty': faculty,
               'subject': subject,
               'departments': departments,
                'user': user,
                'form': form,
                'evaluation_status': evaluation_status,
               'total_students': total_students,
                'total_courses': total_courses,
                'total_sections': total_sections,
                'total_faculty': total_faculty,
                'total_subject': total_subject,
                'total_user': total_user,
                'data': data,
                'chart_data': chart_data,
                'filterset': filterset
                }
    return render(request, 'pages/admin.html', context)

def evaluation_response_chart_data(request):
    # Retrieve data from the model
    evaluations = LikertEvaluation.objects.all()

    # Process data to get total responses per academic year and semester
    data = {}
    for evaluation in evaluations:
        key = f"{evaluation.academic_year} - {evaluation.semester}"
        if key in data:
            data[key] += 1
        else:
            data[key] = 1

    # Convert data to a format suitable for JSON serialization
    chart_data = {
        'labels': list(data.keys()),
        'data': list(data.values()),
    }

    return JsonResponse(chart_data)

def department_response_chart_data(request):
    # Get all departments
    departments = Department.objects.all()

    # Prepare data for chart
    department_labels = []
    department_data = []

    for department in departments:
        # Get all faculty members in this department
        faculty_list = Faculty.objects.filter(department=department)

        # Initialize counters for positive and negative evaluations
        total_positive = 0
        total_negative = 0

        for faculty in faculty_list:
            # Get total evaluations for this faculty
            total_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=faculty).count()

            # Get positive and negative evaluations for this faculty
            positive_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=faculty, predicted_sentiment="Positive").count()
            negative_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=faculty, predicted_sentiment="Negative").count()

            # Add the positive and negative evaluations to department totals
            total_positive += positive_evaluations
            total_negative += negative_evaluations

        # Add department name to labels
        department_labels.append(department.name)

        # Add positive and negative evaluation counts to data
        department_data.append([total_positive, total_negative])

    # Prepare JSON response with labels and data
    chart_data = {
        'labels': department_labels,
        'data': department_data,
    }

    return JsonResponse(chart_data)

def faculty_response_chart_data(request, department_id):
    # Get faculty members for the selected department
    faculty_list = Faculty.objects.filter(department_id=department_id)

    faculty_labels = []
    faculty_data = []

    for faculty in faculty_list:
        positive_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=faculty, predicted_sentiment="Positive").count()
        negative_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=faculty, predicted_sentiment="Negative").count()

        faculty_labels.append(f"{faculty.first_name} {faculty.last_name}")

        faculty_data.append([positive_evaluations, negative_evaluations])

    # Prepare JSON response for faculty chart
    chart_data = {
        'labels': faculty_labels,
        'data': faculty_data,
    }

    return JsonResponse(chart_data)



@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def adminregister(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create a user without saving it to the database
            user = form.save()
            
            # Set the user as a superuser
            user.is_superuser = True
            # Set the user role to admin
            group = Group.objects.get(name = 'admin')
            user.groups.add(group)
            # Save the user to the database
            user.save()
            
            messages.success(request, 'Admin registration successful!')
            return redirect('adminregister')
        else:
            messages.error(request, 'An error occurred during registration. Please try again.')
 
    return render(request, 'pages/adminregister.html', {'form': form})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def evaluations(request):
    evaluation = LikertEvaluation.objects.all()
    
    total_evaluations = evaluation.count()
    #filter and search
    faculty_evaluation_filter = EvaluationFilter(request.GET, queryset=evaluation)
    evaluation = faculty_evaluation_filter.qs
    

    # ordering functionality
   
    ordering = request.GET.get('ordering', "")

     
    if ordering:
        evaluation = evaluation.order_by(ordering) 

    #pagination
    page_number = request.GET.get('page', 1)
    evaluation_paginator = Paginator(evaluation, ITEMS_PER_PAGE)
   

    try:
        page = evaluation_paginator.page(page_number)
    except EmptyPage:
        page = evaluation_paginator.page(evaluation_paginator.num_pages)
 
    context = {'evaluation': page.object_list,'total_evaluations': total_evaluations, 'faculty_evaluation_filter': faculty_evaluation_filter, 'page_obj':page, 'is_paginated': True, 'paginator':evaluation_paginator,'ordering': ordering}
    return render(request, 'pages/evaluations.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def evaluations_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=faculty_evaluations.csv'

    # Create a csv writer
    writer = csv.writer(response)

    # Apply filters from the EvaluationFilter based on the request data
    evaluation_filter = EvaluationFilter(request.GET, queryset=LikertEvaluation.objects.all())

    # Get the filtered queryset
    filtered_evaluations = evaluation_filter.qs

    # Add column headings to csv file

    writer.writerow(['Subject', 'Faculty', 'Average', 'Rating', 'Overall Impression', 'Polarity', 'Academic Year', 'Semester'])

    # Loop thru and output
    for i in filtered_evaluations:
        writer.writerow([i.section_subject_faculty.subjects, i.section_subject_faculty.faculty, i.average_rating, i.get_rating_category(), i.comments, i.predicted_sentiment, i.academic_year, i.semester ])

    return response



@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def admin_view_evaluation_form(request, pk):
    faculty_evaluation_form = LikertEvaluation.objects.get(pk=pk)
    questions = FacultyEvaluationQuestions.objects.all().order_by('order')

    outstanding_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(pk=pk).filter(
        practice_in_respective_discipline=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=5
    ).count()    
    
    # Continue for other fields
    
    very_satisfactory_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=4
    ).count()    
    
    satisfactory_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=3
    ).count()    
    
    unsatisfactory_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=2
    ).count()    

    poor_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=1
    ).count()    
    

    return render(request, 'pages/admin_view_evaluation_form.html', {'faculty_evaluation_form': faculty_evaluation_form, 'faculty': faculty, 'questions': questions, 'outstanding_count': outstanding_count, 'very_satisfactory_count': very_satisfactory_count, 'satisfactory_count': satisfactory_count, 'unsatisfactory_count': unsatisfactory_count, 'poor_count': poor_count,})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def deleteEvaluation(request, pk):
    evaluation = LikertEvaluation.objects.get(pk=pk)
    if request.method == 'POST':
            evaluation.delete()
            return redirect('evaluations')

    return render(request, 'pages/delete.html', {'obj':evaluation})



@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def admin_event_list(request):
    events = Event.objects.all().order_by('-date') 
    event_filter = EventFilter(request.GET, queryset=events)
    events = event_filter.qs 
    # ordering functionality
   
    ordering = request.GET.get('ordering', "")

     
    if ordering:
        events = events.order_by(ordering) 

    paginator = Paginator(events, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,'pages/admin_event_list.html',{'events': events, 'page_obj': page_obj, 'event_filter': event_filter})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def admin_event_evaluations(request, pk):
    event = get_object_or_404(Event, pk=pk)
    # Filter evaluations from both SchoolEventModel and WebinarSeminarModel
    school_event_evaluations = list(SchoolEventModel.objects.filter(event=event))
    webinar_seminar_evaluations = list(WebinarSeminarModel.objects.filter(event=event))

    # Combine the results into one list
    evaluations = school_event_evaluations + webinar_seminar_evaluations
    
    paginator = Paginator(evaluations, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'event': event,
        'evaluations': evaluations,
        'page_obj': page_obj
    }
    return render(request, 'pages/admin_event_evaluations.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin', 'society president', 'faculty'])
def eventevaluations_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=event_evaluations.csv'

    # Create a csv writer
    writer = csv.writer(response)

    # Retrieve the event ID from the request
    event_id = request.GET.get('event_id')
    event = get_object_or_404(Event, pk=event_id)

    # First, check for school events
    evaluations = SchoolEventModel.objects.filter(event=event)
    event_type = 'school_event'

    # If no school events were found, check for webinar events
    if not evaluations.exists():
        evaluations = WebinarSeminarModel.objects.filter(event=event)
        event_type = 'webinar_event'

    # If no evaluations are found at all, return an error
    if not evaluations.exists():
        return HttpResponse("No evaluations found for this event.")

    # Write the CSV headers
    writer.writerow(['Event', 'Suggestions and Comments', 'Average', 'Rating', 'Academic Year', 'Semester'])

    # Loop through and write the evaluation data
    for i in evaluations:
        writer.writerow([i.event.title, i.suggestions_and_comments, i.average_rating, i.get_rating_category(), i.academic_year, i.semester])

    return response

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def view_admin_schoolevent_evaluations(request, pk):
    # Try to get the event from SchoolEventModel or WebinarSeminarModel
    try:
        event_form_details = SchoolEventModel.objects.get(pk=pk)
        event_type = 'school_event'
    except SchoolEventModel.DoesNotExist:
        try:
            event_form_details = WebinarSeminarModel.objects.get(pk=pk)
            event_type = 'webinar_event'
        except WebinarSeminarModel.DoesNotExist:
            # If no event is found in either model, handle the error
            return HttpResponse("Event not found.")

    # Render different templates based on the event type
    if event_type == 'school_event':
        questions = SchoolEventQuestions.objects.all().order_by('order')

        excellent_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=5
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=5
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=5
        ).count()

        very_satisfactory_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=4
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=4
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=4
        ).count()

        satisfactory_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=3
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=3
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=3
        ).count()

        fair_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=2
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=2
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=2
        ).count()

        poor_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=1
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=1
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=1
        ).count()

        template_name = 'pages/view_admin_schoolevent_evaluations.html'
        
    elif event_type == 'webinar_event':
        questions = WebinarSeminarQuestions.objects.all().order_by('order')

        excellent_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=5
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=5
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=5
        ).count()

        very_satisfactory_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=4
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=4
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=4
        ).count()

        satisfactory_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=3
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=3
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=3
        ).count()

        fair_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=2
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=2
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=2
        ).count()

        poor_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=1
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=1
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=1
        ).count()

       
        template_name = 'pages/view_admin_webinar_evaluations.html'
    else:
        return HttpResponse("Invalid event type.")


    return render(request, template_name, {'event_form_details': event_form_details, 'faculty': faculty, 'questions': questions, 'excellent_count': excellent_count, 'very_satisfactory_count': very_satisfactory_count, 'satisfactory_count': satisfactory_count, 'fair_count': fair_count, 'poor_count': poor_count})


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def stakeholderevaluations(request):
    evaluations = StakeholderFeedbackModel.objects.all()

           #filter and search
    stakeholder_evaluation_filter = StakeholderFilter(request.GET, queryset=evaluations)
    evaluations = stakeholder_evaluation_filter.qs
    
       
        # ordering functionality
    ordering = request.GET.get('ordering', "")  
    if ordering:
        evaluations = evaluations.order_by(ordering) 
    
    paginator = Paginator(evaluations, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'evaluations': evaluations, 'page_obj': page_obj, 'stakeholder_evaluation_filter': stakeholder_evaluation_filter}
    return render(request, 'pages/stakeholderevaluations.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def stakeholderevaluations_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=stakeholder_evaluations.csv'

    # Create a csv writer
    writer = csv.writer(response)

    # Apply filters from the EvaluationFilter based on the request data
    evaluation_filter = StakeholderFilter(request.GET, queryset=StakeholderFeedbackModel.objects.all())

    # Get the filtered queryset
    filtered_evaluations = evaluation_filter.qs

    # Add column headings to csv file

    writer.writerow(['Name', 'Agency', 'Email Address', 'Purpose of Visit', 'Date of Visit', 'Attending Staff', 'Average', 'Rating', 'Comments/Suggestions'])

    # Loop thru and output
    for i in filtered_evaluations:
        writer.writerow([i.name, i.agency, i.email, i.purpose, i.date, i.staff, i.average_rating, i.get_rating_category(), i.suggestions_and_comments])

    return response

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def admin_view_stakeholder_form(request, pk):
    stakeholder_feedback_form = StakeholderFeedbackModel.objects.get(pk=pk)
    questions = StakeholderFeedbackQuestions.objects.all().order_by('order')

    highly_satisfied_count = StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            courtesy=5
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            quality=5
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(pk=pk).filter(
            timeliness=5
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            efficiency=5
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            cleanliness=5
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            comfort=5
        ).count()
    
    very_satisfied_count = StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            courtesy=4
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            quality=4
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(pk=pk).filter(
            timeliness=4
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            efficiency=4
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            cleanliness=4
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            comfort=4
        ).count()
    
    moderately_satisfied_count = StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            courtesy=3
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            quality=3
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(pk=pk).filter(
            timeliness=3
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            efficiency=3
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            cleanliness=3
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            comfort=3
        ).count() 
    
    barely_satisfied_count = StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            courtesy=2
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            quality=2
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(pk=pk).filter(
            timeliness=2
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            efficiency=2
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            cleanliness=2
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            comfort=2
        ).count() 
    
    not_satisfied_count = StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            courtesy=1
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            quality=1
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(pk=pk).filter(
            timeliness=1
        ).count() + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            efficiency=1
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            cleanliness=1
        ).count()  + StakeholderFeedbackModel.objects.filter(pk=pk).filter(
            comfort=1
        ).count()
    
    return render(request, 'pages/admin_view_stakeholder_form.html', {'stakeholder_feedback_form': stakeholder_feedback_form, 'questions': questions, 'highly_satisfied_count': highly_satisfied_count, 'very_satisfied_count': very_satisfied_count, 'moderately_satisfied_count': moderately_satisfied_count, 'barely_satisfied_count': barely_satisfied_count, 'not_satisfied_count': not_satisfied_count})


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def forms(request):

    return render(request, 'pages/forms.html')

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_faculty_evaluation_form(request):
    questions = FacultyEvaluationQuestions.objects.all()
    return render(request, 'pages/edit_faculty_evaluation_form.html', {'questions': questions} )

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_faculty_evaluation_form_question(request, pk):
    question = FacultyEvaluationQuestions.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditQuestionForm(request.POST, instance=question)  # Use EditQuestionForm
        if form.is_valid():
            form.save()
            messages.success(request, 'Form updated successfully')
            return redirect('edit_faculty_evaluation_form')  # Redirect to success view
    else:
        form = EditQuestionForm(instance=question)  # Pre-populate form with existing data
    context = {'form': form}
    return render(request, 'pages/edit_faculty_evaluation_form_question.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_school_event_form(request):
    questions = SchoolEventQuestions.objects.all()
    return render(request, 'pages/edit_school_event_form.html', {'questions': questions} )

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_school_event_form_question(request, pk):
    question = SchoolEventQuestions.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditSchoolEventQuestionForm(request.POST, instance=question)  # Use EditQuestionForm
        if form.is_valid():
            form.save()
            messages.success(request, 'Form updated successfully')
            return redirect('edit_school_event_form')  # Redirect to success view
    else:
        form = EditSchoolEventQuestionForm(instance=question)  # Pre-populate form with existing data
    context = {'form': form}
    return render(request, 'pages/edit_school_event_form_question.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_webinar_seminar_form(request):
    questions = WebinarSeminarQuestions.objects.all()
    return render(request, 'pages/edit_webinar_seminar_form.html', {'questions': questions} )

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_webinar_seminar_form_question(request, pk):
    question = WebinarSeminarQuestions.objects.get(pk=pk)
    if request.method == 'POST':
        form = EditWebinarSeminarQuestionForm(request.POST, instance=question)  # Use EditQuestionForm
        if form.is_valid():
            form.save()
            messages.success(request, 'Form updated successfully')
            return redirect('edit_webinar_seminar_form')  # Redirect to success view
    else:
        form = EditWebinarSeminarQuestionForm(instance=question)  # Pre-populate form with existing data
    context = {'form': form}
    return render(request, 'pages/edit_webinar_seminar_form_question.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def faculty(request):
    faculty = Faculty.objects.all()  
        #filtering functionality
    faculty_filter = FacultyFilter(request.GET, queryset=faculty)
    faculty = faculty_filter.qs

    # ordering functionality
   
    ordering = request.GET.get('ordering', "")
     
    if ordering:
        faculty = faculty.order_by(ordering) 

    form = TeacherForm()
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
             # Check for file upload
        created_count = 0
        updated_count = 0
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty added successfully')
            return redirect('faculty')
        import_faculty = request.FILES.get('facultyfile')

        if import_faculty and import_faculty.name.endswith('xlsx'):
            dataset = Dataset()
            imported_data = dataset.load(import_faculty.read(), format='xlsx')

            for data in imported_data:
                first_name = data[1]
                last_name = data[2]
                email = data[3]
                gender = data[4]
                contact_number = data[5]
                department_name = data[6]  # Replace with actual index

                department = Department.objects.filter(name=department_name).first()
                if not department:
                    messages.error(request, f"Department with name '{department_name}' not found.")
                    continue  # Skip this row if course doesn't exist

                # Update the existing student or create a new one
                faculty, created = Faculty.objects.update_or_create(
                    first_name=first_name,
                    last_name=last_name,
                    defaults={
                        'email': email,
                        'gender': gender,
                        'contact_number': contact_number,
                        'department': department,
                    }
                )
                                # Increment counters based on whether the student was created or updated
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            # After processing all data, show the success message
            if created_count > 0:
                messages.success(request, f"Created {created_count} new faculty(s).")
            if updated_count > 0:
                messages.info(request, f"Updated {updated_count} faculty(s).")

        else:
            pass
        

   
    paginator = Paginator(faculty, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'faculty': faculty, 'form': form, 'page_obj': page_obj, 'faculty_filter': faculty_filter}

    return render(request, 'pages/faculty.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def facultyevaluations(request, pk):
    teacher = get_object_or_404(Faculty, pk=pk)
    teacher_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=teacher)


    context = {'teacher': teacher, 'teacher_evaluations':  teacher_evaluations}

    return render(request, 'pages/facultyevaluations.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def editteacher(request, pk):
    faculty = Faculty.objects.get(pk=pk)
    form = TeacherForm(instance=faculty)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            messages.success(request, 'Faculty updated successfully')
            return redirect('faculty')

    context = {'form':form}
    return render(request, 'pages/editteacher.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def deleteTeacher(request, pk):
    faculty = Faculty.objects.get(pk=pk)
    if request.method == 'POST':
            faculty.delete()
            messages.success(request, 'Faculty deleted successfully')
            return redirect('faculty')

    return render(request, 'pages/delete.html', {'obj':faculty})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def department(request):
    department = Department.objects.all()
    form = DepartmentForm()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department added successfully')
            return redirect('department')
        
    paginator = Paginator(department, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'department': department, 'form': form, 'page_obj': page_obj}

    return render(request, 'pages/departments.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def view_department(request, pk):
    department = Department.objects.get(pk=pk)
    faculties = department.faculty_set.all()  # Retrieve all faculties in the department
    paginator = Paginator(faculties, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'department': department,
        'faculties': faculties,
        'page_obj': page_obj
    }

    return render(request, 'pages/view_department.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_department(request, pk):
    department = Department.objects.get(pk=pk)
    form = DepartmentForm(instance=department)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully')
            return redirect('department')

    context = {'form':form}
    return render(request, 'pages/edit_department.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def delete_department(request, pk):
    department = Department.objects.get(pk=pk)
    if request.method == 'POST':
            department.delete()
            messages.success(request, 'Department deleted successfully')
            return redirect('department')

    return render(request, 'pages/delete.html', {'obj':department})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def students(request):
        students = Student.objects.all()
        student_filter = StudentFilter(request.GET, queryset=students)
        students = student_filter.qs
        form = StudentForm()
        if request.method == 'POST':
            form = StudentForm(request.POST, request.FILES)
                # Initialize counters
            created_count = 0
            updated_count = 0
            if form.is_valid():
                form.save(commit=True)  # Ensure commit is set to True to save to the database
                messages.success(request, 'Student added successfully')
                return redirect('students')

            # Check for file upload
            new_student_file = request.FILES.get('studentfile')

            if new_student_file and new_student_file.name.endswith('xlsx'):
                dataset = Dataset()
                imported_data = dataset.load(new_student_file.read(), format='xlsx')

                for data in imported_data:
                    student_number = data[0]
                    first_name = data[1]
                    last_name = data[2]
                    email = data[3]
                    age = data[4]
                    sex = data[5]
                    contact_no = data[6]
                    status = data[7]
                    course_name = data[8]  # Replace with actual index
                    section_name = data[9]  # Replace with actual index

                    course = Course.objects.filter(name=course_name).first()
                    section = Section.objects.filter(name=section_name).first()

                    if not course:
                        messages.error(request, f"Course with name '{course_name}' not found.")
                        continue  # Skip this row if course doesn't exist

                    if not section:
                        messages.error(request, f"Section with name '{section_name}' not found.")
                        continue  # Skip this row if section doesn't exist

                    # Update the existing student or create a new one
                    student, created = Student.objects.update_or_create(
                        student_number=student_number,
                        first_name=first_name,
                        last_name=last_name,
                        defaults={
                            'email': email,
                            'age': age,
                            'sex': sex,
                            'contact_no': contact_no,
                            'status': status,
                            'Course': course,
                            'Section': section,
                        }
                    )
                                    # Increment counters based on whether the student was created or updated
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                # After processing all data, show the success message
                if created_count > 0:
                    messages.success(request, f"Created {created_count} new student(s).")
                if updated_count > 0:
                    messages.info(request, f"Updated {updated_count} student(s).")

            else:
                messages.info(request, 'Please upload a valid Excel file.')

       
        paginator = Paginator(students, 5) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'students': students, 'form': form, 'page_obj': page_obj, 'student_filter': student_filter}
        return render(request, 'pages/students.html',  context)
        

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def editstudent(request, pk):
    student = Student.objects.get(pk=pk)
    form = StudentForm(instance=student)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student updated successfully')
            return redirect('students')

    context = {'form':form}
    return render(request, 'pages/editstudent.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def deleteStudent(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == 'POST':
            student.delete()
            messages.success(request, 'Student deleted successfully')
            return redirect('students')

    return render(request, 'pages/delete.html', {'obj':student})


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def courses(request):
    course = Course.objects.all()
    student = Student.objects.all()
    
    total_students = student.count()

    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course added successfully')
            return redirect('courses')
    context = {'course': course,
               'total_students': total_students,
              'student': student,
              'form':form}
   

   
    return render(request, 'pages/courses.html',  context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def editcourse(request, pk):
    
    course = Course.objects.get(pk=pk)

    form = CourseForm(instance=course)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully')
            return redirect('courses')

    context = {'form':form, 'course': course}
    return render(request, 'pages/editcourse.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def deleteCourse(request, pk):
    course = Course.objects.get(pk=pk)
    if request.method == 'POST':
            course.delete()
            messages.success(request, 'Course deleted successfully')
            return redirect('courses')

    return render(request, 'pages/delete.html', {'obj':course})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def sections(request):
    sections = Section.objects.all()

    section_filter = SectionFilter(request.GET, queryset=sections)
    sections = section_filter.qs
    # Create a list to store section data along with student counts
    section_data = []
    
    for section in sections:
        student_count = Student.objects.filter(Section=section).count()  # Count students in each section
        section_data.append({
            'section': section,
            'student_count': student_count,
        })
    form = SectionForm()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section_name = form.cleaned_data['name']  # Assuming 'name' is the field in your form
            # Check if the section already exists
            if Section.objects.filter(name=section_name).exists():
                messages.warning(request, f"The section '{section_name}' already exists.")
            else:
                form.save()
                messages.success(request, f"The section '{section_name}' has been created successfully.")
                return redirect('sections')
   
    # Ordering functionality
    ordering = request.GET.get('ordering', "")

    if ordering == "name":  
        section_data = sorted(section_data, key=lambda x: x['section'].name)
    elif ordering == "-name":
        section_data = sorted(section_data, key=lambda x: x['section'].name, reverse=True)
    elif ordering == "student_count":
        section_data = sorted(section_data, key=lambda x: x['student_count'])
    elif ordering == "-student_count":
        section_data = sorted(section_data, key=lambda x: x['student_count'], reverse=True)

    paginator = Paginator(section_data, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'sections': sections, 'form':form, 'page_obj': page_obj, 'section_filter': section_filter }
   
    return render(request, 'pages/sections.html',  context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def editsection(request, pk):
    
    section = Section.objects.get(pk=pk)

    form = SectionForm(instance=section)
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, 'Section updated successfully')
            return redirect('sections')

    context = {'form':form}
    return render(request, 'pages/editsection.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def deleteSection(request, pk):
    section = Section.objects.get(pk=pk)
    if request.method == 'POST':
            section.delete()
            messages.success(request, 'Section deleted successfully')
            return redirect('sections')

    return render(request, 'pages/delete.html', {'obj':section})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def section_details(request, pk):
    section = Section.objects.get(pk=pk)
    section = get_object_or_404(Section, pk=pk) #get the primary key of the selected section
    form = SectionSubjectFacultyForm(initial={'section': section}) # pass the instance of the section attribute to the section that is selected to add subjects
    if request.method == 'POST':
        form = SectionSubjectFacultyForm(request.POST, request.FILES)
        created_count = 0
        updated_count = 0
         # Check for file upload
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Subject and Faculty added successfully')
            return redirect('section_details', pk=pk)
        import_subject_faculty = request.FILES.get('subjectfacultyfile')

        if import_subject_faculty and import_subject_faculty.name.endswith('xlsx'):
                dataset = Dataset()
                imported_data = dataset.load(import_subject_faculty.read(), format='xlsx')

                for data in imported_data:
                    section_name = data[0]
                    subject_name = data[1]
                    faculty_full_name = data[2]  # Concatenated first and last name

                    section = Section.objects.filter(name=section_name).first()
                    subject = Subject.objects.filter(subject_name=subject_name).first()

                    # Use Concat function to concatenate first_name and last_name in the filter
                    faculty = Faculty.objects.annotate(
                        full_name=Concat('first_name', Value(' '), 'last_name')
                    ).filter(full_name=faculty_full_name).first()


                    if not section:
                                messages.error(request, f"Section with name '{section_name}' not found.")
                                return redirect('sections')
                    
                    if not subject:
                        messages.error(request, f"Subject with name '{subject_name}' not found.")
                        break  # Skip this row if course doesn't exist

                    
                    
                    if not faculty:
                        messages.error(request, f"Faculty with name '{faculty_full_name}' not found.")
                        break  # Skip this row if section doesn't exist
                    
                    sub_faculty, created = SectionSubjectFaculty.objects.update_or_create(
                    section=section,
                    subjects=subject,
                    defaults={
                        'faculty': faculty
                    }
                )
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                # After processing all data, show the success message
                if created_count > 0:
                    messages.success(request, f"Created {created_count} new subject(s).")
                if updated_count > 0:
                    messages.info(request, f"Updated {updated_count} subject(s).")


        else:
                messages.info(request, 'Please upload a valid Excel file.')



@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def section_details(request, pk):
    section = Section.objects.get(pk=pk)
    section = get_object_or_404(Section, pk=pk) #get the primary key of the selected section
    form = SectionSubjectFacultyForm(initial={'section': section}) # pass the instance of the section attribute to the section that is selected to add subjects
    if request.method == 'POST':
        form = SectionSubjectFacultyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('section_details', pk=pk)
        
@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def section_details(request, pk):
    section = Section.objects.get(pk=pk)
    section = get_object_or_404(Section, pk=pk) #get the primary key of the selected section
    form = SectionSubjectFacultyForm(initial={'section': section}) # pass the instance of the section attribute to the section that is selected to add subjects
    if request.method == 'POST':
        form = SectionSubjectFacultyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('section_details', pk=pk)
        
    subjects_faculty = SectionSubjectFaculty.objects.filter(section=section)
    return render(request, 'pages/section_details.html', {'section': section, 'subjects_faculty': subjects_faculty, 'form': form})
    
@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def deleteSub_Section(request, pk):
    subject = SectionSubjectFaculty.objects.get(pk=pk)
    section_pk = subject.section.pk  # Get the primary key of the related section
    
    if request.method == 'POST':
            subject.delete()
            messages.success(request, 'Subject and Faculty deleted successfully')
            return redirect('section_details', pk=section_pk)

    return render(request, 'pages/delete.html', {'obj':subject})


@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def subjects(request):
    subject = Subject.objects.all()

    #filtering functionality
    subject_filter = SubjectFilter(request.GET, queryset=subject)
    subject = subject_filter.qs

    # ordering functionality  
    ordering = request.GET.get('ordering', "")

     
    if ordering:
        subject = subject.order_by(ordering) 

    #add subject form
    form = SubjectForm()
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully')
            return redirect('subjects')
    
    paginator = Paginator(subject, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'subject': subject, 'form': form, 'page_obj': page_obj, 'subject_filter': subject_filter}
    return render(request, 'pages/subjects.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def editsubject(request, pk):
    
    subject = Subject.objects.get(pk=pk)

    form = SubjectForm(instance=subject)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully')
            return redirect('subjects')

    context = {'form':form}
    return render(request, 'pages/editsubject.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def deleteSubject(request, pk):
    subject = Subject.objects.get(pk=pk)
    if request.method == 'POST':
            subject.delete()
            messages.success(request, 'Subject deleted successfully')
            return redirect('subjects')

    return render(request, 'pages/delete.html', {'obj':subject})


def adminlogout(request):
    logout(request)
    return redirect('adminlogin')

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def users(request):
# Get all users
    users = User.objects.all().order_by('-date_joined')
    user_filter = UserFilter(request.GET, queryset=users)
    users = user_filter.qs
    # Create a dictionary to store user groups
    user_groups = {}

    # Iterate over each user
    for user in users:
        # Get the groups the user belongs to
        groups = user.groups.all()
        
        # Store user groups in the dictionary with user id as key
        user_groups[user.username] = groups

    paginator = Paginator(users, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'user_groups': user_groups, 'page_obj': page_obj, 'user_filter': user_filter}
    return render(request, 'pages/users.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def edit_user_group(request, user_id):
    if request.method == 'POST':
        user = User.objects.get(username=user_id)
        group_name = request.POST.get('group_name')
        group = Group.objects.get(name=group_name)
        user.groups.clear()
        user.groups.add(group)
        messages.success(request, 'User role updated successfully.')
        return redirect('users')  # Redirect to users page after updating group
    else:
        user = User.objects.get(username=user_id)
        user_groups = user.groups.all()
        all_groups = Group.objects.all()
        context = {
            'user_id': user_id,
            'user_groups': user_groups,
            'all_groups': all_groups
        }
        return render(request, 'pages/edit_user_group.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['admin'])
def delete_user(request, user_id):
    user = User.objects.get(username=user_id)
    if request.method == 'POST':
            user.delete()
            return redirect('users')

    return render(request, 'pages/delete.html', {'obj':user})


            # ------------------------------------------------------
            #                Faculty-Page Views
            # ------------------------------------------------------


@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def facultydashboard(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()    
    evaluation_status = EvaluationStatus.objects.first()
    teacher_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=faculty)
    total_evaluations = teacher_evaluations.count()
    # Compute the average rating
    avg_rating = teacher_evaluations.aggregate(average_rating=Avg('average_rating'))['average_rating']

    # Round the average rating to one decimal point
    avg_rating = round(avg_rating, 1)

    recent_comments = teacher_evaluations.values('comments', 'predicted_sentiment')[:3]

   
     # Categorize the evaluations for Chart.js
    categories = {
        'Subject Matter Content': {
            'command_and_knowledge_of_the_subject': 0,
            'depth_of_mastery': 0,
            'practice_in_respective_discipline': 0,
            'up_to_date_knowledge': 0,
            'integrates_subject_to_practical_circumstances': 0,
        },
        'Organization': {
            'organizes_the_subject_matter': 0,
            'provides_orientation_on_course_content': 0,
            'efforts_of_class_preparation': 0,
            'summarizes_main_points': 0,
            'monitors_online_class': 0,
        },
        'Teacher-Student Rapport': {
            'holds_interest_of_students': 0,
            'provides_relevant_feedback': 0,
            'encourages_participation': 0,
            'shows_enthusiasm': 0,
            'shows_sense_of_humor': 0,
        },
        'Teaching Methods': {
            'teaching_methods': 0,
            'flexible_learning_strategies': 0,
            'student_engagement': 0,
            'clear_examples': 0,
            'focused_on_objectives': 0,
        },
        'Presentation': {
            'starts_with_motivating_activities': 0,
            'speaks_in_clear_and_audible_manner': 0,
            'uses_appropriate_medium_of_instruction': 0,
            'establishes_online_classroom_environment': 0,
            'observes_proper_classroom_etiquette': 0,
        },
        'Classroom Management': {
            'uses_time_wisely': 0,
            'gives_ample_time_for_students_to_prepare': 0,
            'updates_the_students_of_their_progress': 0,
            'demonstrates_leadership_and_professionalism': 0,
            'understands_possible_distractions': 0,
        },
        'Sensitivity and Support to Students': {
            'sensitivity_to_student_culture': 0,
            'responds_appropriately': 0,
            'assists_students_on_concerns': 0,
            'guides_the_students_in_accomplishing_tasks': 0,
            'extends_consideration_to_students': 0,
        }
    }

    count = {key: 0 for key in categories}  # Track rating counts per category

    # Populate category data from evaluations
    for evaluation in teacher_evaluations:
        # Subject Matter Content
        categories['Subject Matter Content']['command_and_knowledge_of_the_subject'] += evaluation.command_and_knowledge_of_the_subject
        categories['Subject Matter Content']['depth_of_mastery'] += evaluation.depth_of_mastery
        categories['Subject Matter Content']['practice_in_respective_discipline'] += evaluation.practice_in_respective_discipline
        categories['Subject Matter Content']['up_to_date_knowledge'] += evaluation.up_to_date_knowledge
        categories['Subject Matter Content']['integrates_subject_to_practical_circumstances'] += evaluation.integrates_subject_to_practical_circumstances
        
        count['Subject Matter Content'] += 5
        
        # Organization
        categories['Organization']['organizes_the_subject_matter'] += evaluation.organizes_the_subject_matter
        categories['Organization']['provides_orientation_on_course_content'] += evaluation.provides_orientation_on_course_content
        categories['Organization']['efforts_of_class_preparation'] += evaluation.efforts_of_class_preparation
        categories['Organization']['summarizes_main_points'] += evaluation.summarizes_main_points
        categories['Organization']['monitors_online_class'] += evaluation.monitors_online_class
        
        count['Organization'] += 5

       
        # Teacher-Student Rapport
        categories['Teacher-Student Rapport']['holds_interest_of_students'] += evaluation.holds_interest_of_students
        categories['Teacher-Student Rapport']['provides_relevant_feedback'] += evaluation.provides_relevant_feedback
        categories['Teacher-Student Rapport']['encourages_participation'] += evaluation.encourages_participation
        categories['Teacher-Student Rapport']['shows_enthusiasm'] += evaluation.shows_enthusiasm
        categories['Teacher-Student Rapport']['shows_sense_of_humor'] += evaluation.shows_sense_of_humor
        
        count['Teacher-Student Rapport'] += 5

       
        # Teaching Methods
        categories['Teaching Methods']['teaching_methods'] += evaluation.teaching_methods
        categories['Teaching Methods']['flexible_learning_strategies'] += evaluation.flexible_learning_strategies
        categories['Teaching Methods']['student_engagement'] += evaluation.student_engagement
        categories['Teaching Methods']['clear_examples'] += evaluation.clear_examples
        categories['Teaching Methods']['focused_on_objectives'] += evaluation.focused_on_objectives
        
        count['Teaching Methods'] += 5

       
        # Presentation
        categories['Presentation']['starts_with_motivating_activities'] += evaluation.starts_with_motivating_activities
        categories['Presentation']['speaks_in_clear_and_audible_manner'] += evaluation.speaks_in_clear_and_audible_manner
        categories['Presentation']['uses_appropriate_medium_of_instruction'] += evaluation.uses_appropriate_medium_of_instruction
        categories['Presentation']['establishes_online_classroom_environment'] += evaluation.establishes_online_classroom_environment
        categories['Presentation']['observes_proper_classroom_etiquette'] += evaluation.observes_proper_classroom_etiquette
        
        count['Presentation'] += 5

       
        # Classroom Management
        categories['Classroom Management']['uses_time_wisely'] += evaluation.uses_time_wisely
        categories['Classroom Management']['gives_ample_time_for_students_to_prepare'] += evaluation.gives_ample_time_for_students_to_prepare
        categories['Classroom Management']['updates_the_students_of_their_progress'] += evaluation.updates_the_students_of_their_progress
        categories['Classroom Management']['demonstrates_leadership_and_professionalism'] += evaluation.demonstrates_leadership_and_professionalism
        categories['Classroom Management']['understands_possible_distractions'] += evaluation.understands_possible_distractions
        
        count['Classroom Management'] += 5

       
        # Sensitivity and Support to Students
        categories['Sensitivity and Support to Students']['sensitivity_to_student_culture'] += evaluation.sensitivity_to_student_culture
        categories['Sensitivity and Support to Students']['responds_appropriately'] += evaluation.responds_appropriately
        categories['Sensitivity and Support to Students']['assists_students_on_concerns'] += evaluation.assists_students_on_concerns
        categories['Sensitivity and Support to Students']['guides_the_students_in_accomplishing_tasks'] += evaluation.guides_the_students_in_accomplishing_tasks
        categories['Sensitivity and Support to Students']['extends_consideration_to_students'] += evaluation.extends_consideration_to_students
        
        count['Sensitivity and Support to Students'] += 5

       

    # Calculate averages for each category
    for category, fields in categories.items():
        for field in fields:
            categories[category][field] /= len(teacher_evaluations) if teacher_evaluations else 1

    context = {
        'faculty': faculty,
        'evaluation_status': evaluation_status,
        'avg_rating': avg_rating,
        'recent_comments': recent_comments,
        'categorized_data': categories,  # Pass the categorized data to the template
        'total_evaluations': total_evaluations
    }

    return render(request, 'pages/facultydashboard.html', context)



@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def facultyprofile(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()    
    context = {'faculty': faculty}
    return render(request, 'pages/facultyprofile.html', context)
   
@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])   
def facultyfeedbackandevaluations(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()       
    email = request.user.email
    teacher_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=faculty)
    try:
        # Query the Faculty model using the email address
        teacher = Faculty.objects.get(email=email)
    except Faculty.DoesNotExist:
        # Handle the case where the faculty with the given email does not exist
        raise Http404("Faculty does not exist for the logged-in user")

    context = {'faculty': faculty, 'teacher': teacher, 'teacher_evaluations': teacher_evaluations}

    return render(request, 'pages/facultyfeedbackandevaluations.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def view_evaluation_form(request, pk):
    faculty = Faculty.objects.filter(email=request.user.username).first()
    questions = FacultyEvaluationQuestions.objects.all().order_by('order')
    faculty_evaluation_form = LikertEvaluation.objects.get(pk=pk)
    outstanding_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(pk=pk).filter(
        practice_in_respective_discipline=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=5
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=5
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=5
    ).count()    
    
    # Continue for other fields
    
    very_satisfactory_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=4
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=4
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=4
    ).count()    
    
    satisfactory_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=3
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=3
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=3
    ).count()    
    
    unsatisfactory_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=2
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=2
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=2
    ).count()    

    poor_count = LikertEvaluation.objects.filter(pk=pk).filter(
        command_and_knowledge_of_the_subject=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        depth_of_mastery=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        practice_in_respective_discipline=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        up_to_date_knowledge=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        integrates_subject_to_practical_circumstances=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        organizes_the_subject_matter=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_orientation_on_course_content=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        efforts_of_class_preparation=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        summarizes_main_points=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        monitors_online_class=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        holds_interest_of_students=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        provides_relevant_feedback=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        encourages_participation=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_enthusiasm=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        shows_sense_of_humor=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        teaching_methods=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        flexible_learning_strategies=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        student_engagement=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        clear_examples=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        focused_on_objectives=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        starts_with_motivating_activities=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        speaks_in_clear_and_audible_manner=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_appropriate_medium_of_instruction=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        establishes_online_classroom_environment=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        observes_proper_classroom_etiquette=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        uses_time_wisely=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        gives_ample_time_for_students_to_prepare=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        updates_the_students_of_their_progress=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        demonstrates_leadership_and_professionalism=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        understands_possible_distractions=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        sensitivity_to_student_culture=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        responds_appropriately=1
    ).count() + LikertEvaluation.objects.filter(pk=pk).filter(
        assists_students_on_concerns=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        guides_the_students_in_accomplishing_tasks=1
    ).count()  + LikertEvaluation.objects.filter(pk=pk).filter(
        extends_consideration_to_students=1
    ).count()    
    
    return render(request, 'pages/view_evaluation_form.html', {'faculty_evaluation_form': faculty_evaluation_form, 'faculty': faculty, 'outstanding_count': outstanding_count, 'very_satisfactory_count': very_satisfactory_count, 'satisfactory_count': satisfactory_count, 'unsatisfactory_count': unsatisfactory_count, 'poor_count': poor_count, 'questions': questions})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def faculty_event_evaluations(request):
     user = request.user
     faculty = Faculty.objects.filter(email=request.user.username).first()    
     event = Event.objects.filter(author=user).order_by('-updated')
     form = EventCreationForm()
     if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.author = request.user  # Set the author to the currently logged-in user
            form.save()
            #event = form.save(commit=False)
            #event.published_by = faculty 
            #event.save()

            return redirect('faculty_event_evaluations')
        else:
            # Print form errors for debugging
            print(form.errors)
           
     context = {'event': event, 'faculty': faculty, 'form':form}
     return render(request, 'pages/faculty_event_evaluations.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def view_faculty_event_evaluations(request, pk):
    faculty = Faculty.objects.filter(email=request.user.username).first()  
    event = get_object_or_404(Event, pk=pk)
    # Filter evaluations from both SchoolEventModel and WebinarSeminarModel
    school_event_evaluations = list(SchoolEventModel.objects.filter(event=event))
    webinar_seminar_evaluations = list(WebinarSeminarModel.objects.filter(event=event))

    # Combine the results into one list
    evaluations = school_event_evaluations + webinar_seminar_evaluations
    
    paginator = Paginator(evaluations, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'faculty': faculty,
        'event': event,
        'evaluations': evaluations,
        'page_obj': page_obj
    }
    return render(request, 'pages/view_faculty_event_evaluations.html', context)


@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def faculty_view_event_evaluations(request, pk):
     # Try to get the event from SchoolEventModel or WebinarSeminarModel
    try:
        event_form_details = SchoolEventModel.objects.get(pk=pk)
        event_type = 'school_event'
    except SchoolEventModel.DoesNotExist:
        try:
            event_form_details = WebinarSeminarModel.objects.get(pk=pk)
            event_type = 'webinar_event'
        except WebinarSeminarModel.DoesNotExist:
            # If no event is found in either model, handle the error
            return HttpResponse("Event not found.")

    # Render different templates based on the event type
    if event_type == 'school_event':
        faculty = Faculty.objects.filter(email=request.user.username).first()  
        questions = SchoolEventQuestions.objects.all().order_by('order')

        excellent_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=5
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=5
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=5
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=5
        ).count()

        very_satisfactory_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=4
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=4
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=4
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=4
        ).count()

        satisfactory_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=3
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=3
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=3
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=3
        ).count()

        fair_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=2
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=2
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=2
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=2
        ).count()

        poor_count = SchoolEventModel.objects.filter(pk=pk).filter(
            meeting_expectation=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            attainment_of_the_objectives=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(pk=pk).filter(
            topics_discussed=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            input_presentation=1
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            management_team=1
        ).count()  + SchoolEventModel.objects.filter(pk=pk).filter(
            venue_and_physical_arrangement=1
        ).count() + SchoolEventModel.objects.filter(pk=pk).filter(
            overall_assessment=1
        ).count()

        template_name = 'pages/view_faculty_schoolevent_evaluations.html'
        
    elif event_type == 'webinar_event':
        faculty = Faculty.objects.filter(email=request.user.username).first()  
        questions = WebinarSeminarQuestions.objects.all().order_by('order')

        excellent_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=5
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=5
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=5
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=5
        ).count()

        very_satisfactory_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=4
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=4
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=4
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=4
        ).count()

        satisfactory_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=3
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=3
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=3
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=3
        ).count()

        fair_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=2
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=2
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=2
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=2
        ).count()

        poor_count = WebinarSeminarModel.objects.filter(pk=pk).filter(
            relevance_of_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(pk=pk).filter(
            quality_of_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness=1
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            attainment_of_the_objective=1
        ).count()  + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_to_attain_the_objective=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods_used=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_topic_in_the_present_time=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            usefulness_of_the_topic_discusssed_in_the_activity=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            appropriateness_of_the_searching_methods=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            displayed_a_thorough_knowledge_of_the_topic=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            thoroughly_explained_and_processed_the_learning_activities_throughout_the_training=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_create_a_good_learning_environment=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            able_to_manage_her_time_well=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            demonstrated_keenness_to_the_participant_needs=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            timeliness_or_suitability_of_service=1
        ).count() + WebinarSeminarModel.objects.filter(pk=pk).filter(
            overall_satisfaction=1
        ).count()

       
        template_name = 'pages/view_faculty_webinar_evaluations.html'
    else:
        return HttpResponse("Invalid event type.")


    return render(request, template_name, {'event_form_details': event_form_details, 'faculty': faculty, 'questions': questions, 'excellent_count': excellent_count, 'very_satisfactory_count': very_satisfactory_count, 'satisfactory_count': satisfactory_count, 'fair_count': fair_count, 'poor_count': poor_count})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def edit_faculty_events(request, pk):
    faculty = Faculty.objects.filter(email=request.user.username).first()    
    event = Event.objects.get(pk=pk)
    form = EventCreationForm(instance=event)
    if request.method == 'POST':
        form = EventCreationForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save(commit=True)
            return redirect('faculty_event_evaluations')

           
    context = {'event': event, 'faculty': faculty, 'form':form}
    return render(request, 'pages/edit_faculty_events.html', context)

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def delete_faculty_events(request, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
            event.delete()
            return redirect('faculty_event_evaluations')

    return render(request, 'pages/delete.html', {'obj':event})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def faculty_events(request):
    user = request.user
    faculty = Faculty.objects.filter(email=request.user.username).first()   
    faculty_department = faculty.department  # Get the department the faculty is a part of
    events = Event.objects.filter(department_attendees=faculty_department).distinct()  # Get events related to those department
    # Get evaluated event IDs by the current user
     # Get evaluated event IDs by the current user for SchoolEventModel
    evaluated_school_event_ids = SchoolEventModel.objects.filter(user=user).values_list('event_id', flat=True)
    
    # Get evaluated event IDs by the current user for WebinarSeminarModel
    evaluated_webinar_event_ids = WebinarSeminarModel.objects.filter(user=user).values_list('event_id', flat=True)

    # Combine evaluated event IDs from both models
    evaluated_event_ids = list(evaluated_school_event_ids) + list(evaluated_webinar_event_ids)
     # Get current time
    current_time = timezone.now()
    upcoming_events = events.filter(date__gt=current_time, evaluation_status=False)  # Events in the future
    # Past events with closed evaluation
    past_events = events.filter(date__lt=current_time, evaluation_status=False)  # Past events with evaluation closed   
    # Exclude events that have been evaluated
    unevaluated_events = events.exclude(id__in=evaluated_event_ids).exclude(id__in=past_events).exclude(id__in=upcoming_events).order_by('-date') 
    return render(request, 'pages/faculty_events.html', {'faculty': faculty, 'unevaluated_events': unevaluated_events, 'past_events': past_events, 'upcoming_events': upcoming_events})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def faculty_events_upcoming(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()  
    department = faculty.department  # Get the department the faculty is a part of
    events = Event.objects.filter(department_attendees=department).distinct()  # Get events related to those department
    
    current_time = timezone.now()
    upcoming_events = events.filter(date__gt=current_time, evaluation_status=False)  # Events in the future

    return render(request, 'pages/faculty_events_upcoming.html', {'faculty': faculty,'upcoming_events': upcoming_events})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def faculty_events_evaluated(request):
    user = request.user
    faculty = Faculty.objects.filter(email=request.user.username).first()  
    department = faculty.department  # Get the department the faculty is a part of
    events = Event.objects.filter(department_attendees=department).distinct()  # Get events related to those department
      # Get evaluated event IDs by the current user
     # Get evaluated event IDs by the current user for SchoolEventModel
    evaluated_school_event_ids = SchoolEventModel.objects.filter(user=user).values_list('event_id', flat=True)
    
    # Get evaluated event IDs by the current user for WebinarSeminarModel
    evaluated_webinar_event_ids = WebinarSeminarModel.objects.filter(user=user).values_list('event_id', flat=True)

    # Combine evaluated event IDs from both models
    evaluated_event_ids = list(evaluated_school_event_ids) + list(evaluated_webinar_event_ids)
    
    # Exclude events that have been evaluated
    evaluated_events = events.filter(id__in=evaluated_event_ids).order_by('-date')[:10]
    return render(request, 'pages/faculty_events_evaluated.html', {'faculty': faculty, 'evaluated_events': evaluated_events})

@login_required(login_url='signin')
@allowed_users(allowed_roles=['faculty'])
def faculty_events_closed(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()  
    department = faculty.department  # Get the department the faculty is a part of
    events = Event.objects.filter(department_attendees=department).distinct()  # Get events related to those department

    # Get current time
    current_time = timezone.now()
    # Past events with closed evaluation
    past_events = events.filter(date__lt=current_time, evaluation_status=False)  # Past events with evaluation closed   
    return render(request, 'pages/faculty_events_closed.html', {'faculty': faculty, 'past_events': past_events})
