# Generated by Django 4.2.7 on 2024-03-31 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0043_remove_likertevaluation_requires_more_task_for_credit_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-updated', '-created']},
        ),
        migrations.AlterModelOptions(
            name='department',
            options={'ordering': ['-updated', '-created']},
        ),
        migrations.AlterModelOptions(
            name='likertevaluation',
            options={'ordering': ['-updated', '-created']},
        ),
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ['-updated', '-created']},
        ),
        migrations.AlterModelOptions(
            name='student',
            options={'ordering': ['-updated', '-created']},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ['-updated', '-created']},
        ),
        migrations.AddField(
            model_name='student',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='student',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]