# Generated by Django 5.1 on 2024-10-16 10:56

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('myapp', '0002_delete_todoitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='MP3File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('transcription_text', models.TextField(blank=True, null=True)),
                ('duration', models.FloatField(blank=True, null=True)),
                ('transcription_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('related_to_depression', models.BooleanField(default=False)),
                ('found_keywords', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
