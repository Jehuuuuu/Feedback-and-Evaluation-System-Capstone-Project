# Generated by Django 4.2.7 on 2024-04-07 12:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0060_schoolevent_name_webinarseminar_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_type',
        ),
        migrations.AddField(
            model_name='event',
            name='event_type',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.typeofevent'),
            preserve_default=False,
        ),
    ]