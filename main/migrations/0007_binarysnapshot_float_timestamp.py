# Generated by Django 4.2.5 on 2023-10-04 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_user_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='binarysnapshot',
            name='float_timestamp',
            field=models.FloatField(default=0),
        ),
    ]
