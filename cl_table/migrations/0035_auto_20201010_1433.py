# Generated by Django 3.0.7 on 2020-10-10 14:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0034_images'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='Appt_Created_Byid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Fmspw'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='Appt_typeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ApptType'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='Source_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Source'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='cust_noid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Customer'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='emp_noid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='customer',
            name='Cust_sexesid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Gender'),
        ),
        migrations.AddField(
            model_name='employee',
            name='Emp_LeaveDayid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Days'),
        ),
        migrations.AddField(
            model_name='employee',
            name='Emp_maritalid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Maritalstatus'),
        ),
        migrations.AddField(
            model_name='employee',
            name='Emp_nationalityid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Nationality'),
        ),
        migrations.AddField(
            model_name='employee',
            name='Emp_raceid',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Races'),
        ),
        migrations.AddField(
            model_name='employee',
            name='Emp_religionid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Religious'),
        ),
        migrations.AddField(
            model_name='employee',
            name='Emp_sexesid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Gender'),
        ),
        migrations.AddField(
            model_name='employee',
            name='shift',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='staff', to='cl_table.Attendance2'),
        ),
        migrations.AddField(
            model_name='employee',
            name='skills',
            field=models.ManyToManyField(blank=True, to='cl_table.Stock'),
        ),
        migrations.AddField(
            model_name='fmspw',
            name='Emp_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='posdaud',
            name='dt_Staffnoid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='posdaud',
            name='dt_itemnoid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cl_table.Stock'),
        ),
        migrations.AddField(
            model_name='poshaud',
            name='sa_custnoid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Customer'),
        ),
        migrations.AddField(
            model_name='poshaud',
            name='sa_staffnoid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Employee'),
        ),
        migrations.AddField(
            model_name='poshaud',
            name='trans_user_loginid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Fmspw'),
        ),
        migrations.AddField(
            model_name='postaud',
            name='billed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Fmspw'),
        ),
        migrations.AddField(
            model_name='postaud',
            name='pay_groupid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.PayGroup'),
        ),
        migrations.AddField(
            model_name='postaud',
            name='pay_typeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Paytable'),
        ),
        migrations.AddField(
            model_name='stock',
            name='Item_Classid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemClass'),
        ),
        migrations.AddField(
            model_name='stock',
            name='Item_Deptid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemDept'),
        ),
        migrations.AddField(
            model_name='stock',
            name='Item_Divid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemDiv'),
        ),
        migrations.AddField(
            model_name='stock',
            name='Item_Rangeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemRange'),
        ),
        migrations.AddField(
            model_name='stock',
            name='Item_Typeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemType'),
        ),
        migrations.AddField(
            model_name='stock',
            name='Itm_Statusid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemStatus'),
        ),
        migrations.AddField(
            model_name='stock',
            name='item_Brandid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemBrand'),
        ),
        migrations.AddField(
            model_name='stock',
            name='item_Seasonid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemSeason'),
        ),
        migrations.AddField(
            model_name='stock',
            name='item_SizePackid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemSizepack'),
        ),
        migrations.AddField(
            model_name='stock',
            name='item_Sizeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemSize'),
        ),
        migrations.AddField(
            model_name='stock',
            name='item_colorid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemColor'),
        ),
        migrations.AddField(
            model_name='stock',
            name='item_fabricid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.ItemFabric'),
        ),
        migrations.AddField(
            model_name='tmpitemhelper',
            name='Source_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Source'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='Cust_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Customer'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='Item_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Stock'),
        ),
        migrations.AddField(
            model_name='treatment',
            name='treatment_master',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Treatment_Master'),
        ),
        migrations.AddField(
            model_name='treatmentaccount',
            name='Cust_Codeid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Customer'),
        ),
        migrations.AddField(
            model_name='treatmentaccount',
            name='User_Nameid',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Fmspw'),
        ),
        migrations.AddField(
            model_name='treatmentaccount',
            name='treatment_master',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='cl_table.Treatment_Master'),
        ),
    ]
