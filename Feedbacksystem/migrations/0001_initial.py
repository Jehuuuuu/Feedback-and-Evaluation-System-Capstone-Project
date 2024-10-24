# Generated by Django 4.2.7 on 2024-01-16 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('profile_picture', models.ImageField(blank=True, upload_to='profile_picture/')),
                ('gender', models.CharField(max_length=9)),
                ('email', models.EmailField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_Number', models.CharField(max_length=9)),
                ('name', models.CharField(max_length=100)),
                ('profile_picture', models.ImageField(blank=True, upload_to='profile_picture/')),
                ('gender', models.CharField(max_length=9)),
                ('email', models.EmailField(max_length=100)),
                ('year_Level', models.CharField(max_length=9, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_code', models.CharField(max_length=10)),
                ('subject_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Feedback_Comment', models.TextField()),
                ('date_Submitted', models.DateField(auto_now=True)),
                ('Faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.faculty')),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.student')),
                ('Subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.subject')),
            ],
        ),
        migrations.CreateModel(
            name='Evaluation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('average_rating', models.IntegerField()),
                ('date_Submitted', models.DateField(auto_now=True)),
                ('Faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.faculty')),
                ('Student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.student')),
                ('Subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.subject')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.question')),
            ],
        ),
    ]
