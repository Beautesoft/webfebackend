# Generated by Django 3.0.7 on 2020-10-13 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0054_auto_20201013_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='item_pingying',
            field=models.CharField(blank=True, db_column='Item_PingYing', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='procedure',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='process_remark',
            field=models.CharField(blank=True, db_column='Process_Remark', max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='sutiable_for',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='tax',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='treatment_details',
            field=models.TextField(blank=True, null=True),
        ),
    ]
