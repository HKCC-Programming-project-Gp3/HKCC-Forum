# Generated by Django 3.2.12 on 2022-04-07 09:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20220331_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='create_date',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False),
        ),
    ]