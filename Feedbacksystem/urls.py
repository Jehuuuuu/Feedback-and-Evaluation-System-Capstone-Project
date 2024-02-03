from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.signin, name="signin"),
    path('studentlogout', views.studentlogout, name='studentlogout'),
    path('home', views.home, name="home"),
    path('student_profile', views.student_profile, name="student_profile"),
    path('faculty', views.faculty, name="faculty"),
    path('administrator', views.admin, name="admin"),
    path('facultyeval', views.facultyeval, name="facultyeval"),
    path('eventhub', views.eventhub, name="eventhub"),
    path('suggestionbox', views.suggestionbox, name="suggestionbox"),
    path('contactUs', views.contactUs, name="contactUs"),
    path('about', views.about, name="about"),
    path('courses', views.courses, name="courses"),
    path('sections', views.sections, name="sections"),
    path('addteacher', views.addteacher, name="addteacher"),
    path('editteacher/<int:pk>/', views.editteacher, name="editteacher"),
    path('deleteTeacher/<int:pk>/', views.deleteTeacher, name="deleteTeacher"),
    path('sectiondetails/<int:pk>/', views.section_details, name='section_details'),
    path('students', views.students, name='students'),
    path('addstudent', views.addstudent, name='addstudent'),
    path('addcourse', views.addcourse, name='addcourse'),
    path('deleteStudent/<int:pk>/', views.deleteStudent, name="deleteStudent"),
    path('deleteCourse/<int:pk>/', views.deleteCourse, name="deleteCourse"),
    path('editstudent/<int:pk>/', views.editstudent, name='editstudent'),
    path('editcourse/<int:pk>/', views.editcourse, name='editcourse'),
    path('addsection', views.addsection, name='addsection'),
    path('editsection/<int:pk>/', views.editsection, name='editsection'),
    path('deleteSection/<int:pk>/', views.deleteSection, name='deleteSection'),
    path('addsub_section', views.addsub_section, name='addsub_section'),
    path('subjects', views.subjects, name='subjects'),
    path('addsubject', views.addsubject, name='addsubject'),
    path('editsubject/<int:pk>/', views.editsubject, name='editsubject'),
    path('deleteSubject/<int:pk>/', views.deleteSubject, name='deleteSubject'),
    path('adminlogin', views.adminlogin, name='adminlogin'),
    path('adminlogout', views.adminlogout, name='adminlogout'),
    path('adminregister', views.adminregister, name='adminregister'),
    path('evaluate/<int:pk>/', views.evaluate_subject_faculty, name='evaluate_subject_faculty'),
    path('evaluations', views.evaluations, name='evaluations'),
    path('facultyevaluations/<int:pk>/', views.facultyevaluations, name='facultyevaluations'),
    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)