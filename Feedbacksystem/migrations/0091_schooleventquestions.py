# Generated by Django 5.0.7 on 2024-09-11 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Feedbacksystem', '0090_delete_schooleventquestions'),
    ]

    operations = [
        migrations.CreateModel(
            name='SchoolEventQuestions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
                ('order', models.IntegerField(default=0)),
            ],
        ),
    ]