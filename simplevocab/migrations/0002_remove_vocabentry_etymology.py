# Generated by Django 4.2 on 2023-05-04 16:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simplevocab', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vocabentry',
            name='etymology',
        ),
    ]
