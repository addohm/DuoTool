# Generated by Django 2.1.5 on 2019-02-18 09:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='duolingousers',
            name='last_update',
            field=models.DateField(blank=True, null=True),
        ),
    ]