# Generated by Django 5.0.7 on 2024-11-27 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0126_faculty_email_sent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='webinarseminarmodel',
            name='thoroughly_explained_and_processed_the_learning_activities_throughout_the_training',
        ),
        migrations.AddField(
            model_name='webinarseminarmodel',
            name='explained_activities',
            field=models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'), (2, 'Less than expected'), (1, 'Much less than expected')], db_column='explained_activities', default=1),
            preserve_default=False,
        ),
    ]
