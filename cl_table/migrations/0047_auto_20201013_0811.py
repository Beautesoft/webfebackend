# Generated by Django 3.0.7 on 2020-10-13 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0046_auto_20201012_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='Stock_PIC',
            field=models.ImageField(null=True, upload_to='img'),
        ),
        migrations.AddField(
            model_name='stock',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='procedure',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='sutiable_for',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='tax',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='stock',
            name='treatment_details',
            field=models.TextField(null=True),
        ),
    ]
