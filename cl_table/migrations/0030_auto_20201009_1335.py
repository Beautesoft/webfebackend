# Generated by Django 3.0.7 on 2020-10-09 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0029_city_cnrefund_commtype_country_creditnote_customerclass_days_empsocso_emptype_gender_itemstatus_mari'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='city',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='cnrefund',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='cnrefund',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='commtype',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='commtype',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='phonecode',
            field=models.CharField(blank=True, db_column='phoneCode', max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='creditnote',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='creditnote',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='customerclass',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customerclass',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='days',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='days',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='empsocso',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='empsocso',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='emptype',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='emptype',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='gender',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='gender',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='itemstatus',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='itemstatus',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='maritalstatus',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='maritalstatus',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='nationality',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='nationality',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='prepaidaccount',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='prepaidaccount',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='races',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='religious',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='religious',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='reversedtl',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='reversedtl',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='reversehdr',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='reversehdr',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='source',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='state',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='state',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='commtype',
            name='comm_type_active',
            field=models.BooleanField(db_column='Comm_Type_Active', default=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='creditnote',
            name='status',
            field=models.CharField(blank=True, choices=[('open', 'OPEN'), ('close', 'CLOSE')], db_column='Status', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='customerclass',
            name='class_isactive',
            field=models.BooleanField(blank=True, db_column='Class_Isactive', default=True, null=True),
        ),
        migrations.AlterField(
            model_name='days',
            name='itm_isactive',
            field=models.BooleanField(db_column='ITM_ISACTIVE', default=True),
        ),
        migrations.AlterField(
            model_name='emptype',
            name='type_isactive',
            field=models.BooleanField(blank=True, db_column='TYPE_ISACTIVE', default=True, null=True),
        ),
        migrations.AlterField(
            model_name='gender',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='itemstatus',
            name='itm_isactive',
            field=models.BooleanField(db_column='itm_IsActive', default=True),
        ),
        migrations.AlterField(
            model_name='maritalstatus',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='nationality',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='active_deposit_bonus',
            field=models.BooleanField(db_column='Active_Deposit_Bonus', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='edit_date',
            field=models.DateTimeField(db_column='Edit_Date', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='exp_status',
            field=models.BooleanField(db_column='EXP_STATUS', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='has_deposit',
            field=models.BooleanField(db_column='HAS_DEPOSIT', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='isvoucher',
            field=models.BooleanField(db_column='ISVOUCHER', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='line_no',
            field=models.BigIntegerField(db_column='Line_No', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='outstanding',
            field=models.FloatField(db_column='Outstanding', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='pp_no',
            field=models.CharField(db_column='PP_NO', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='pp_type',
            field=models.CharField(db_column='PP_TYPE', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='remain',
            field=models.FloatField(db_column='REMAIN', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='site_code',
            field=models.CharField(db_column='SITE_CODE', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='status',
            field=models.BooleanField(db_column='STATUS', null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='topup_no',
            field=models.CharField(db_column='TopUp_No', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='prepaidaccount',
            name='use_amt',
            field=models.FloatField(db_column='USE_AMT', null=True),
        ),
        migrations.AlterField(
            model_name='races',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='religious',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='source_code',
            field=models.CharField(db_column='Source_Code', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='source_isactive',
            field=models.BooleanField(db_column='Source_IsActive', default=True),
        ),
        migrations.AlterField(
            model_name='state',
            name='itm_isactive',
            field=models.BooleanField(default=True),
        ),
    ]
