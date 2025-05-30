# Generated by Django 4.2.7 on 2024-04-02 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0050_remove_student_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='contact_no',
            field=models.CharField(default=1, max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='email',
            field=models.EmailField(default=1, max_length=64),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.CharField(default=1, max_length=15),
            preserve_default=False,
        ),
    ]
