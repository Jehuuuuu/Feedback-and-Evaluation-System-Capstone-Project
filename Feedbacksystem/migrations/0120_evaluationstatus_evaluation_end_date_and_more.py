# Generated by Django 5.0.7 on 2024-11-19 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0119_alter_likertevaluation_admin_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationstatus',
            name='evaluation_end_date',
            field=models.DateField(default='2024-11-20'),
        ),
        migrations.AddField(
            model_name='evaluationstatus',
            name='evaluation_release_date',
            field=models.DateField(default='2024-11-20'),
        ),
    ]
