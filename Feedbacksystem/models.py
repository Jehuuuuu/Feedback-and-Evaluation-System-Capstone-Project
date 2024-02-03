from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Course(models.Model):
   name = models.CharField(max_length=100)
   
   def __str__(self):
        return self.name
    

    


    
class Department(models.Model):
    name = models.CharField(max_length=100, null=True, blank = True)

    def __str__(self):
        return self.name
    

   


class Faculty(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank = True)
    last_name = models.CharField(max_length=100, null=True, blank = True)
    gender = models.CharField(max_length=9)
    email = models.EmailField(max_length=100)
    contact_number = models.IntegerField(null=True, blank = True)
    profile_picture = models.ImageField(upload_to='profile_picture/', blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank = True) 
    
    updated = models.DateTimeField(auto_now = True, null=True, blank = True)
    created = models.DateTimeField(auto_now_add = True, null=True, blank = True)

    class Meta:
        ordering = ['-updated', '-created']
        
    def __str__(self):
        return f"{self.first_name} {self. last_name}"

class Subject(models.Model):
    subject_code = models.CharField(max_length=10)
    subject_name = models.CharField(max_length=100)  
    



    def __str__(self):
        return self.subject_code



class Section(models.Model):
    name = models.CharField(max_length=50)
    subjects = models.ManyToManyField(Subject, through="SectionSubjectFaculty")

    def __str__(self):
        return self.name 

class SectionSubjectFaculty(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subjects = models.ForeignKey(Subject, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.section} - {self. subjects} - {self. faculty}"
 



class Student(models.Model):

    student_number = models.CharField(max_length=9, primary_key=True)
    name = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_picture/', null=True, blank = True)
    age = models.IntegerField(null=True, blank = True)
    sex = models.CharField(max_length=6, null=True, blank = True)
    Course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank = True) 
    Section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True, blank = True) 

  


    def __str__(self):
        return self.name
    
  
class LikertEvaluation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    section_subject_faculty = models.ForeignKey(SectionSubjectFaculty, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(1, 'Strongly Disagree'), (2, 'Disagree'), (3, 'Neutral'),
                                          (4, 'Agree'), (5, 'Strongly Agree')])
    comments = models.TextField()

    def __str__(self):
       return f"{self. section_subject_faculty} - {self. rating} - {self. comments}"


class Feedback(models.Model):

    Faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    Subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  
    Feedback_Comment = models.TextField()
    date_Submitted = models.DateField(auto_now=True)

  