# Generated by Django 4.2 on 2023-08-12 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simplevocab', '0012_alter_vocabentry_definition_override_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vocabentry',
            name='definition_override',
            field=models.TextField(blank=True, default='', max_length=999, null=True, verbose_name='Your Definition'),
        ),
        migrations.AlterField(
            model_name='vocabentry',
            name='discovery_context',
            field=models.TextField(blank=True, default='', max_length=999, null=True, verbose_name='Discovery Context'),
        ),
        migrations.AlterField(
            model_name='vocabentry',
            name='discovery_source',
            field=models.TextField(max_length=999, verbose_name='Discovery Source'),
        ),
        migrations.AlterField(
            model_name='vocabentry',
            name='etymology_override',
            field=models.TextField(blank=True, default='', max_length=999, null=True, verbose_name='Your Etymology'),
        ),
        migrations.AlterField(
            model_name='vocabentry',
            name='examples_override',
            field=models.TextField(blank=True, default='', max_length=999, null=True, verbose_name='Your Examples'),
        ),
        migrations.AlterField(
            model_name='vocabentry',
            name='synonyms_override',
            field=models.TextField(blank=True, default='', max_length=999, null=True, verbose_name='Your Synonyms'),
        ),
        migrations.AlterField(
            model_name='word',
            name='definition',
            field=models.TextField(max_length=999),
        ),
        migrations.AlterField(
            model_name='word',
            name='etymology',
            field=models.TextField(max_length=999),
        ),
        migrations.AlterField(
            model_name='word',
            name='examples',
            field=models.TextField(max_length=999),
        ),
        migrations.AlterField(
            model_name='word',
            name='synonyms',
            field=models.TextField(max_length=999),
        ),
    ]
