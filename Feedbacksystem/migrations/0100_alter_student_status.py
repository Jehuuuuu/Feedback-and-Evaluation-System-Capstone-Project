# Generated by Django 5.0.7 on 2024-10-01 07:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0099_webinarseminarmodel_academic_year_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='status',
            field=models.CharField(choices=[('regular', 'Regular'), ('irregular', 'Irregular')], default='regular', max_length=20),
        ),
    ]