# Generated by Django 4.2.7 on 2024-04-07 11:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0055_rename_type_of_event_typeofevent_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relevance_of_the_activity', models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'), (2, 'Less than expected'), (1, 'Much less than expected')])),
                ('quality_of_the_activity', models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'), (2, 'Less than expected'), (1, 'Much less than expected')])),
                ('timeliness', models.IntegerField(choices=[(5, 'Greatly exceeded expectations'), (4, 'Exceeded expectations'), (3, 'Matched expectations'), (2, 'Less than expected'), (1, 'Much less than expected')])),
                ('suggestions_and_comments', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='typeofevent',
            name='school_event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Feedbacksystem.schoolevent'),
        ),
    ]