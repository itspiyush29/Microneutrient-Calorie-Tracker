# Generated by Django 4.1 on 2022-11-17 03:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0003_rename_password_userprofile_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]