# Generated by Django 4.2.7 on 2024-04-07 11:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0058_alter_typeofevent_school_event_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schoolevent',
            name='name',
        ),
        migrations.RemoveField(
            model_name='webinarseminar',
            name='name',
        ),
    ]
