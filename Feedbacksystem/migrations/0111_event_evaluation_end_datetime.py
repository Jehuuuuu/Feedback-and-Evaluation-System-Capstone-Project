# Generated by Django 5.0.7 on 2024-11-06 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0110_alter_event_admin_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='evaluation_end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
