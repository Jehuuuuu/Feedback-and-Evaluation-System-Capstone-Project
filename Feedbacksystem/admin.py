from django.contrib import admin
from .models import Student, Subject, Faculty, Course, Department, Feedback, Section, SectionSubjectFaculty, LikertEvaluation
# Register your models here.
class SectionSubjectFacultyInline(admin.TabularInline):
    model = Section.subjects.through

class SectionAdmin(admin.ModelAdmin):
    inlines = [SectionSubjectFacultyInline]

    
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(Faculty)
admin.site.register(Course)
admin.site.register(Department)
admin.site.register(Feedback)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionSubjectFaculty)
admin.site.register(LikertEvaluation)