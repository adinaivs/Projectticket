# Generated by Django 5.1.3 on 2024-12-07 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_customuser_activation_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='username',
        ),
    ]
