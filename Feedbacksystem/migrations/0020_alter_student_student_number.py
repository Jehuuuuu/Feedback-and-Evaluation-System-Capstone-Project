# Generated by Django 4.2.7 on 2024-02-02 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0019_remove_evaluation_student_remove_feedback_student_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_Number',
            field=models.CharField(max_length=9, primary_key=True, serialize=False),
        ),
    ]
