# Generated by Django 5.0.7 on 2024-10-05 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0104_stakeholderfeedbackmodel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stakeholderfeedbackmodel',
            name='cleanliness',
            field=models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'), (2, 'Barely Satisfied'), (1, 'Not satisfied')]),
        ),
        migrations.AlterField(
            model_name='stakeholderfeedbackmodel',
            name='comfort',
            field=models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'), (2, 'Barely Satisfied'), (1, 'Not satisfied')]),
        ),
        migrations.AlterField(
            model_name='stakeholderfeedbackmodel',
            name='courtesy',
            field=models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'), (2, 'Barely Satisfied'), (1, 'Not satisfied')]),
        ),
        migrations.AlterField(
            model_name='stakeholderfeedbackmodel',
            name='efficiency',
            field=models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'), (2, 'Barely Satisfied'), (1, 'Not satisfied')]),
        ),
        migrations.AlterField(
            model_name='stakeholderfeedbackmodel',
            name='quality',
            field=models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'), (2, 'Barely Satisfied'), (1, 'Not satisfied')]),
        ),
        migrations.AlterField(
            model_name='stakeholderfeedbackmodel',
            name='timeliness',
            field=models.IntegerField(choices=[(5, 'Highly satisfied'), (4, 'Very satisfied'), (3, 'Moderately satisfied'), (2, 'Barely Satisfied'), (1, 'Not satisfied')]),
        ),
    ]
