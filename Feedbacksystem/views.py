from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Feedbacksystem.models import Course, Section, SectionSubjectFaculty, Faculty, Student, Subject, LikertEvaluation
from .forms import TeacherForm, StudentForm, CourseForm, SectionForm, SectionSubjectFacultyForm, SubjectForm, StudentRegistrationForm, StudentLoginForm, LikertEvaluationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Avg

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
    student = Student.objects.filter(student_number=request.user.username).first()

    
    
    context = {'student': student}
    return render(request, 'pages/home.html', context)
    



def faculty(request):
    faculty = Faculty.objects.all()
    context = {'faculty': faculty}

    return render(request, 'pages/faculty.html', context)

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
    context = {'student': student, 
               'course': course,
               'section': section,
               'faculty': faculty,
               'subject': subject,
                'user': user,

               'total_students': total_students,
                'total_courses': total_courses,
                'total_sections': total_sections,
                'total_faculty': total_faculty,
                'total_subject': total_subject,
                'total_user': total_user
                }
    return render(request, 'pages/admin.html', context)

def facultyeval(request):
    return render(request, 'pages/facultyeval.html')

def eventhub(request):
    return render(request, 'pages/eventhub.html')

def suggestionbox(request):
    return render(request, 'pages/suggestionbox.html')

def contactUs(request):
    return render(request, 'pages/contactUs.html')

def about(request):
    return render(request, 'pages/about.html')

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

def section_details(request, pk):
    section = Section.objects.get(pk=pk)
    subjects_faculty = SectionSubjectFaculty.objects.filter(section=section)
    return render(request, 'pages/section_details.html', {'section': section, 'subjects_faculty': subjects_faculty})

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

def addsub_section(request):
    form = SectionSubjectFacultyForm()
    if request.method == 'POST':
        form = SectionSubjectFacultyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sections')

    context = {'form': form}
    return render(request, 'pages/addsub_section.html', context)


def section_details(request, pk):
    section = Section.objects.get(pk=pk)
    subjects_faculty = SectionSubjectFaculty.objects.filter(section=section)
    return render(request, 'pages/section_details.html', {'section': section, 'subjects_faculty': subjects_faculty})

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
    if request.method == 'POST':
        form = LikertEvaluationForm(request.POST)
        if form.is_valid():
            # Process the evaluation form
            rating = form.cleaned_data['rating']
            comments = form.cleaned_data['comments']

            # Save the data to the database
            form = LikertEvaluation(
                student=request.user.student,
                section_subject_faculty=section_subject_faculty,
                rating=rating,
                comments=comments
            )
            form.save()

            return redirect('student_profile')  # Redirect to a success page or wherever you want
    else:
        form = LikertEvaluationForm()
        context = { 'form': form, 'section_subject_faculty': section_subject_faculty,
    }
    return render(request, 'pages/evaluate_subject_faculty.html', context)

def evaluations(request):
    evaluation = LikertEvaluation.objects.all()
    context = {'evaluation': evaluation}

    return render(request, 'pages/evaluations.html', context)

def facultyevaluations(request, pk):
    teacher = get_object_or_404(Faculty, pk=pk)
    teacher_evaluations = LikertEvaluation.objects.filter(section_subject_faculty__faculty=teacher)

    avg_rating = teacher_evaluations.aggregate(Avg('rating'))['rating__avg']

    context = {'teacher': teacher, 'teacher_evaluations':  teacher_evaluations, 'avg_rating': avg_rating}

    return render(request, 'pages/facultyevaluations.html', context)

    