# Generated by Django 3.2 on 2023-03-08 22:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='name',
            field=models.CharField(default=2, max_length=30),
            preserve_default=False,
        ),
    ]
