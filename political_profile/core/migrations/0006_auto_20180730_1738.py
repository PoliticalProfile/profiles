# Generated by Django 2.0.7 on 2018-07-30 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20180729_2034'),
    ]

    operations = [
        migrations.AddField(
            model_name='congressman',
            name='budget_id',
            field=models.IntegerField(null=True, verbose_name='budget id'),
        ),
        migrations.AddField(
            model_name='congressman',
            name='condition',
            field=models.CharField(max_length=255, null=True, verbose_name='condition'),
        ),
    ]
