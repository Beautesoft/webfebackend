# Generated by Django 3.0.7 on 2020-10-19 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0067_auto_20201019_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='favorites',
            field=models.IntegerField(blank=True, db_column='Favorites', null=True),
        ),
    ]
