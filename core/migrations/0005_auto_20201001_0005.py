# Generated by Django 3.1.1 on 2020-09-30 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_recipe'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='time',
            new_name='time_minutes',
        ),
    ]
