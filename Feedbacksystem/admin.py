from django.contrib import admin
from .models import Student, Subject, Faculty, Course, Department, Section, SectionSubjectFaculty, LikertEvaluation, EvaluationStatus, Event, TypeOfEvent, SchoolEventModel, WebinarSeminarModel, FacultyEvaluationQuestions, SchoolEventQuestions, WebinarSeminarQuestions, StakeholderFeedbackModel, StakeholderFeedbackQuestions, Message, PeertoPeerEvaluation, PeertoPeerEvaluationQuestions, StakeholderAgency, Attendance
from import_export.admin import ImportExportModelAdmin
# Register your models here.
class SectionSubjectFacultyInline(admin.TabularInline):
    model = Section.subjects.through

class SectionAdmin(admin.ModelAdmin):
    inlines = [SectionSubjectFacultyInline]

@admin.register(Student)
class StudentsAdmin(ImportExportModelAdmin):
    list_display = ('student_number', 'last_name', 'middle_name', 'first_name', 'email', 'birthdate','gender', 'contact_no', 'status', 'Course', 'Section')

    

admin.site.register(Subject)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionSubjectFaculty)
admin.site.register(LikertEvaluation)
admin.site.register(EvaluationStatus)
admin.site.register(Event)
admin.site.register(TypeOfEvent)
admin.site.register(WebinarSeminarModel)
admin.site.register(SchoolEventModel)
admin.site.register(FacultyEvaluationQuestions)
admin.site.register(SchoolEventQuestions)
admin.site.register(WebinarSeminarQuestions)
admin.site.register(StakeholderFeedbackModel)
admin.site.register(StakeholderFeedbackQuestions)
admin.site.register(Message)
admin.site.register(PeertoPeerEvaluation)
admin.site.register(PeertoPeerEvaluationQuestions)
admin.site.register(StakeholderAgency)
admin.site.register(Attendance)