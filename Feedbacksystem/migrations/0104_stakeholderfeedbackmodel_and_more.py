# Generated by Django 5.0.7 on 2024-10-04 16:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0103_remove_schooleventmodel_quality_of_the_activity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='StakeholderFeedbackModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('agency', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('purpose', models.CharField(blank=True, max_length=100, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('staff', models.CharField(blank=True, max_length=100, null=True)),
                ('courtesy', models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'), (2, 'Fair'), (1, 'Poor')])),
                ('quality', models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'), (2, 'Fair'), (1, 'Poor')])),
                ('timeliness', models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'), (2, 'Fair'), (1, 'Poor')])),
                ('efficiency', models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'), (2, 'Fair'), (1, 'Poor')])),
                ('cleanliness', models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'), (2, 'Fair'), (1, 'Poor')])),
                ('comfort', models.IntegerField(choices=[(5, 'Excellent'), (4, 'Very Satisfactory'), (3, 'Satisfactory'), (2, 'Fair'), (1, 'Poor')])),
                ('suggestions_and_comments', models.TextField()),
                ('academic_year', models.CharField(blank=True, max_length=50, null=True)),
                ('semester', models.CharField(blank=True, max_length=50, null=True)),
                ('average_rating', models.FloatField(blank=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'ordering': ['-updated', '-created'],
            },
        ),
        migrations.CreateModel(
            name='StakeholderFeedbackQuestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
            ],
        ),
    ]
