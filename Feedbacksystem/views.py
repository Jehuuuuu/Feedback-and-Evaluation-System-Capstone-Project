from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Feedbacksystem.models import Course, Section, SectionSubjectFaculty, Faculty, Department, Student, Subject, LikertEvaluation, EvaluationStatus
from .forms import TeacherForm, StudentForm, CourseForm, SectionForm, SectionSubjectFacultyForm, SubjectForm, StudentRegistrationForm, StudentLoginForm, LikertEvaluationForm, FacultyRegistrationForm, FacultyLoginForm, EvaluationStatusForm, DepartmentForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg
from django.http import Http404
from .utils import load_prediction_models, single_prediction
from .filters import EvaluationFilter

# Create your views here.

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
                registration_form.save()
                messages.success(request, 'Registration successful!')
                return redirect('signin')  # Redirect to the home page or any desired URL after successful registration

    context = {'registration_form': registration_form, 'login_form': login_form,}
    
    return render(request, 'pages/login.html', context)

def studentlogout(request):
    logout(request)
    return redirect('signin')

def home(request):
    evaluation_status = EvaluationStatus.objects.first()
    student = Student.objects.filter(student_number=request.user.username).first()  
    context = {'evaluation_status': evaluation_status, 'student': student, }
    return render(request, 'pages/home.html', context)
    



def faculty(request):
    faculty = Faculty.objects.all()  
    context = {'faculty': faculty}

    return render(request, 'pages/faculty.html', context)

def department(request):
    department = Department.objects.all()
    context = {'department': department}

    return render(request, 'pages/departments.html', context)

def view_department(request, pk):
    department = Department.objects.get(pk=pk)
    faculties = department.faculty_set.all()  # Retrieve all faculties in the department

    context = {
        'department': department,
        'faculties': faculties
    }

    return render(request, 'pages/view_department.html', context)

def admin(request):
    student = Student.objects.all()
    course = Course.objects.all()
    section = Section.objects.all()
    faculty = Faculty.objects.all()
    subject = Subject.objects.all()
    user = User.objects.all()

    total_students = student.count()
    total_courses = course.count()
    total_sections = section.count()
    total_faculty = faculty.count()
    total_subject = subject.count()
    total_user = user.count()

    evaluation_status = EvaluationStatus.objects.first()  # Assuming there's only one status entry

    context = {'student': student, 
               'course': course,
               'section': section,
               'faculty': faculty,
               'subject': subject,
                'user': user,
                'evaluation_status': evaluation_status,
               'total_students': total_students,
                'total_courses': total_courses,
                'total_sections': total_sections,
                'total_faculty': total_faculty,
                'total_subject': total_subject,
                'total_user': total_user
                }
    return render(request, 'pages/admin.html', context)


def admin_evaluation_status(request):
    evaluation_status = EvaluationStatus.objects.first()  # Assuming there's only one status entry
    if request.method == 'POST':
        form = EvaluationStatusForm(request.POST, instance=evaluation_status)
        if form.is_valid():
            form.save()
            return redirect('admin')
    else:
        form = EvaluationStatusForm(instance=evaluation_status)
    return render(request, 'pages/admin_evaluation_status.html', {'form': form})

def facultyeval(request):
    evaluation_status = EvaluationStatus.objects.first()
    student = Student.objects.filter(student_number=request.user.username).first()
    section_subjects_faculty = SectionSubjectFaculty.objects.filter(section=student.Section)
    
    return render(request, 'pages/facultyeval.html', {'student': student, 'section_subjects_faculty': section_subjects_faculty, 'evaluation_status': evaluation_status})

def eventhub(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    return render(request, 'pages/eventhub.html', {'student': student})

def suggestionbox(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    return render(request, 'pages/suggestionbox.html', {'student': student})

def contactUs(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    return render(request, 'pages/contactUs.html', {'student': student})

def about(request):
    student = Student.objects.filter(student_number=request.user.username).first()
    return render(request, 'pages/about.html', {'student': student})

def courses(request):
    course = Course.objects.all()
    student = Student.objects.all()
    
    total_students = student.count()
    context = {'course': course,
               'total_students': total_students,
              'student': student}
   

   
    return render(request, 'pages/courses.html',  context)
def student_profile(request):
    student = Student.objects.filter(student_number=request.user.username).first()

    section_subjects_faculty = SectionSubjectFaculty.objects.filter(section=student.Section)

    context = {'student': student, 'section_subjects_faculty': section_subjects_faculty}
    return render(request, 'pages/student_profile.html', context)


def sections(request):
    section = Section.objects.all()
    context = {'section': section}
   
    return render(request, 'pages/sections.html',  context)

def addteacher(request):
    form = TeacherForm()
    if request.method == 'POST':
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('faculty')

    context = {'form': form}
    return render(request, 'pages/addteacher.html', context)

def editteacher(request, pk):
    faculty = Faculty.objects.get(pk=pk)
    form = TeacherForm(instance=faculty)
    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            return redirect('faculty')

    context = {'form':form}
    return render(request, 'pages/editteacher.html', context)

def deleteTeacher(request, pk):
    faculty = Faculty.objects.get(pk=pk)
    if request.method == 'POST':
            faculty.delete()
            return redirect('faculty')

    return render(request, 'pages/delete.html', {'obj':faculty})


def add_department(request):
    form = DepartmentForm()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department')

    context = {'form': form}
    return render(request, 'pages/add_department.html', context)

def students(request):
    students = Student.objects.all()
    context = {'students': students}
   
    return render(request, 'pages/students.html',  context)

def addstudent(request):
    form = StudentForm()
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=True)  # Ensure commit is set to True to save to the database
            return redirect('students')

    context = {'form': form}
    return render(request, 'pages/addstudent.html', context)

def editstudent(request, pk):
    student = Student.objects.get(pk=pk)
    form = StudentForm(instance=student)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('students')

    context = {'form':form}
    return render(request, 'pages/editstudent.html', context)

def deleteStudent(request, pk):
    student = Student.objects.get(pk=pk)
    if request.method == 'POST':
            student.delete()
            return redirect('students')

    return render(request, 'pages/delete.html', {'obj':student})

def addcourse(request):
    form = CourseForm()
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('courses')

    context = {'form': form}
    return render(request, 'pages/addcourse.html', context)

def editcourse(request, pk):
    
    course = Course.objects.get(pk=pk)

    form = CourseForm(instance=course)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses')

    context = {'form':form, 'course': course}
    return render(request, 'pages/editcourse.html', context)

def deleteCourse(request, pk):
    course = Course.objects.get(pk=pk)
    if request.method == 'POST':
            course.delete()
            return redirect('courses')

    return render(request, 'pages/delete.html', {'obj':course})

def addsection(request):
    form = SectionForm()
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sections')

    context = {'form': form}
    return render(request, 'pages/addsection.html', context)

def editsection(request, pk):
    
    section = Section.objects.get(pk=pk)

    form = SectionForm(instance=section)
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            return redirect('sections')

    context = {'form':form}
    return render(request, 'pages/editsection.html', context)

def deleteSection(request, pk):
    section = Section.objects.get(pk=pk)
    if request.method == 'POST':
            section.delete()
            return redirect('sections')

    return render(request, 'pages/delete.html', {'obj':section})

def addsub_section(request, pk):
    section = get_object_or_404(Section, pk=pk) #get the primary key of the selected section
    form = SectionSubjectFacultyForm(initial={'section': section}) # pass the instance of the section attribute to the section that is selected to add subjects
    if request.method == 'POST':
        form = SectionSubjectFacultyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('section_details', pk=pk)

    context = {'form': form}
    return render(request, 'pages/addsub_section.html', context)


def section_details(request, pk):
    section = Section.objects.get(pk=pk)
    subjects_faculty = SectionSubjectFaculty.objects.filter(section=section)
    return render(request, 'pages/section_details.html', {'section': section, 'subjects_faculty': subjects_faculty})

def view_evaluation_form(request, pk):
    faculty_evaluation_form = LikertEvaluation.objects.get(pk=pk)

    return render(request, 'pages/view_evaluation_form.html', {'faculty_evaluation_form': faculty_evaluation_form})


def subjects(request):
    subject = Subject.objects.all()
    context = {'subject': subject}
    return render(request, 'pages/subjects.html', context)

def addsubject(request):
    form = SubjectForm()
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('subjects')

    context = {'form': form}
    return render(request, 'pages/addsubject.html', context)

def editsubject(request, pk):
    
    subject = Subject.objects.get(pk=pk)

    form = SubjectForm(instance=subject)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subjects')

    context = {'form':form}
    return render(request, 'pages/editsubject.html', context)

def deleteSubject(request, pk):
    subject = Subject.objects.get(pk=pk)
    if request.method == 'POST':
            subject.delete()
            return redirect('subjects')

    return render(request, 'pages/delete.html', {'obj':subject})

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

def adminlogout(request):
    logout(request)
    return redirect('adminlogin')

def adminregister(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create a user without saving it to the database
            user = form.save(commit=False)
            
            # Set the user as a superuser
            user.is_superuser = True
            
            # Save the user to the database
            user.save()
            
            messages.success(request, 'Superuser registration successful!')
            return redirect('adminlogin')
        else:
            messages.error(request, 'An error occurred during registration. Please try again.')
 
    return render(request, 'pages/adminregister.html', {'form': form})

def evaluate_subject_faculty(request,pk):
    section_subject_faculty = get_object_or_404(SectionSubjectFaculty, pk=pk)
    student = Student.objects.filter(student_number=request.user.username).first()
    section_subjects_faculty = SectionSubjectFaculty.objects.filter(section=student.Section)
    
   
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
            form = LikertEvaluation(
                section_subject_faculty=section_subject_faculty,
                command_and_knowledge_of_the_subject=command_and_knowledge_of_the_subject,
                depth_of_mastery=depth_of_mastery,
                practice_in_respective_discipline=practice_in_respective_discipline,
                up_to_date_knowledge=up_to_date_knowledge,
                integrates_subject_to_practical_circumstances=integrates_subject_to_practical_circumstances,
                
                organizes_the_subject_matter=organizes_the_subject_matter,
                provides_orientation_on_course_content = provides_orientation_on_course_content,
                efforts_of_class_preparation = efforts_of_class_preparation,
                summarizes_main_points = summarizes_main_points,
                monitors_online_class = monitors_online_class,
                
                holds_interest_of_students= holds_interest_of_students,
                provides_relevant_feedback = provides_relevant_feedback,
                encourages_participation = encourages_participation,
                shows_enthusiasm = shows_enthusiasm,
                shows_sense_of_humor = shows_sense_of_humor,

                teaching_methods = teaching_methods,
                flexible_learning_strategies = flexible_learning_strategies,
                student_engagement = student_engagement,
                clear_examples = clear_examples,
                focused_on_objectives = focused_on_objectives,

                starts_with_motivating_activities = starts_with_motivating_activities,
                speaks_in_clear_and_audible_manner = speaks_in_clear_and_audible_manner,
                uses_appropriate_medium_of_instruction = uses_appropriate_medium_of_instruction,
                establishes_online_classroom_environment = establishes_online_classroom_environment,
                observes_proper_classroom_etiquette = observes_proper_classroom_etiquette,

                uses_time_wisely = uses_time_wisely,
                gives_ample_time_for_students_to_prepare = gives_ample_time_for_students_to_prepare,
                updates_the_students_of_their_progress = updates_the_students_of_their_progress,
                demonstrates_leadership_and_professionalism = demonstrates_leadership_and_professionalism,
                understands_possible_distractions = understands_possible_distractions,
                                
                sensitivity_to_student_culture = sensitivity_to_student_culture,
                responds_appropriately = responds_appropriately,
                assists_students_on_concerns = assists_students_on_concerns,
                guides_the_students_in_accomplishing_tasks = guides_the_students_in_accomplishing_tasks,
                extends_consideration_to_students = extends_consideration_to_students,

                requires_less_task_for_credit = requires_less_task_for_credit,
                strengths_of_the_faculty = strengths_of_the_faculty,
                other_suggestions_for_improvement = other_suggestions_for_improvement,
                comments=comments,
                predicted_sentiment=predicted_sentiment
            )
            form.save()
            
            return redirect('facultyeval')  # Redirect to a success page
        messages.success(request, 'Evaluation submitted successfully.')
    else:
        form = LikertEvaluationForm()
        context = { 'form': form, 'section_subject_faculty': section_subject_faculty, 'section_subjects_faculty': section_subjects_faculty
    }
    return render(request, 'pages/evaluate_subject_faculty.html', context)

def evaluations(request):
    evaluation = LikertEvaluation.objects.all()
    total_evaluations = evaluation.count()

    faculty_evaluation_filter = EvaluationFilter(request.GET, queryset=evaluation)
    evaluation = faculty_evaluation_filter.qs

    context = {'evaluation': evaluation,'total_evaluations': total_evaluations, 'faculty_evaluation_filter': faculty_evaluation_filter}
    return render(request, 'pages/evaluations.html', context)

def facultyevaluations(request, pk):
    teacher = get_object_or_404(Faculty, pk=pk)
    teacher_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=teacher)

    avg_rating = teacher_evaluations.aggregate(Avg('average_rating'))['average_rating__avg'] #get the average of the aggregated field based on the specified queryset

    context = {'teacher': teacher, 'teacher_evaluations':  teacher_evaluations, 'avg_rating': avg_rating}

    return render(request, 'pages/facultyevaluations.html', context)

def deleteEvaluation(request, pk):
    evaluation = LikertEvaluation.objects.get(pk=pk)
    if request.method == 'POST':
            evaluation.delete()
            return redirect('evaluations')

    return render(request, 'pages/delete.html', {'obj':evaluation})

def deleteSub_Section(request, pk):
    subject = SectionSubjectFaculty.objects.get(pk=pk)
    if request.method == 'POST':
            subject.delete()
            return redirect('section_details', pk=pk)

    return render(request, 'pages/delete.html', {'obj':subject})

def facultydashboard(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()    
    context = {'faculty': faculty}
    return render(request, 'pages/facultydashboard.html', context)

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
                registration_form.save()
                messages.success(request, 'Registration successful!')
                return redirect('facultylogin')  # Redirect to the home page or any desired URL after successful registration

    context = {'registration_form': registration_form, 'login_form': login_form,}
    
    return render(request, 'pages/facultylogin.html', context)

def facultyprofile(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()    
    context = {'faculty': faculty}
    return render(request, 'pages/facultyprofile.html', context)
   
    
def facultyfeedbackandevaluations(request):
    faculty = Faculty.objects.filter(email=request.user.username).first()       
    email = request.user.email

    try:
        # Query the Faculty model using the email address
        teacher = Faculty.objects.get(email=email)
    except Faculty.DoesNotExist:
        # Handle the case where the faculty with the given email does not exist
        raise Http404("Faculty does not exist for the logged-in user")

    # Now you have the faculty object, you can proceed with further processing
    # For example, fetching evaluations related to this faculty

    # Assuming you have the necessary logic to fetch evaluations
    teacher_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=teacher)

    # Calculate average rating or any other necessary processing
    avg_rating = teacher_evaluations.aggregate(Avg('rating'))['rating__avg']

    context = {'faculty': faculty, 'teacher': teacher, 'teacher_evaluations': teacher_evaluations, 'avg_rating': avg_rating}

    return render(request, 'pages/facultyfeedbackandevaluations.html', context)