# Generated by Django 2.0.7 on 2018-07-30 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20180730_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposition',
            name='status',
            field=models.TextField(null=True, verbose_name='status'),
        ),
    ]