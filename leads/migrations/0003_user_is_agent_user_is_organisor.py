# Generated by Django 4.1.5 on 2023-02-20 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0002_userprofile_agent_organisation'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_agent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='is_organisor',
            field=models.BooleanField(default=True),
        ),
    ]
