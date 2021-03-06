# Generated by Django 3.0.7 on 2020-10-09 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cl_table', '0002_auto_20201009_0716'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('appt_id', models.AutoField(db_column='Appt_id', primary_key=True, serialize=False)),
                ('cust_no', models.CharField(blank=True, max_length=20, null=True)),
                ('appt_date', models.DateTimeField(blank=True, db_column='Appt_date', null=True)),
                ('appt_fr_time', models.DateTimeField(blank=True, db_column='Appt_Fr_time', null=True)),
                ('appt_type', models.CharField(blank=True, db_column='Appt_type', max_length=20, null=True)),
                ('appt_phone', models.CharField(blank=True, db_column='Appt_phone', max_length=20, null=True)),
                ('appt_noperson', models.IntegerField(blank=True, db_column='Appt_noperson', null=True)),
                ('appt_remark', models.CharField(blank=True, db_column='Appt_remark', max_length=250, null=True)),
                ('emp_no', models.CharField(blank=True, max_length=10, null=True)),
                ('emp_name', models.CharField(blank=True, max_length=80, null=True)),
                ('appt_isactive', models.BooleanField(db_column='Appt_Isactive')),
                ('cust_name', models.CharField(blank=True, db_column='Cust_name', max_length=60, null=True)),
                ('appt_code', models.CharField(blank=True, db_column='Appt_code', max_length=50, null=True)),
                ('appt_worktype_no', models.IntegerField(blank=True, db_column='Appt_WorkType_No', null=True)),
                ('appt_est_time', models.CharField(blank=True, db_column='Appt_Est_Time', max_length=10, null=True)),
                ('appt_est_cost', models.FloatField(blank=True, db_column='Appt_Est_Cost', null=True)),
                ('appt_status', models.CharField(blank=True, db_column='Appt_Status', max_length=20, null=True)),
                ('appt_to_time', models.DateTimeField(blank=True, db_column='Appt_To_time', null=True)),
                ('sa_transacno', models.CharField(blank=True, max_length=20, null=True)),
                ('appt_created_by', models.CharField(blank=True, db_column='Appt_Created_By', max_length=50, null=True)),
                ('appt_created_date', models.DateTimeField(blank=True, db_column='Appt_Created_Date', null=True)),
                ('appt_created_time', models.DateTimeField(blank=True, db_column='Appt_Created_Time', null=True)),
                ('itemsite_code', models.CharField(blank=True, db_column='ItemSite_Code', max_length=20, null=True)),
                ('remind_user', models.BooleanField(db_column='Remind_User')),
                ('arrive_time', models.CharField(blank=True, db_column='Arrive_time', max_length=20, null=True)),
                ('isend_time', models.BooleanField(db_column='IsEnd_Time')),
                ('end_time', models.CharField(blank=True, db_column='End_Time', max_length=20, null=True)),
                ('walkin', models.BooleanField(db_column='WalkIn')),
                ('new', models.BooleanField(db_column='New')),
                ('ref_code', models.CharField(blank=True, db_column='Ref_Code', max_length=20, null=True)),
                ('appt_comfirm', models.BooleanField(db_column='Appt_Comfirm')),
                ('appt_cancel', models.BooleanField(db_column='Appt_Cancel')),
                ('duration', models.CharField(blank=True, db_column='Duration', max_length=10, null=True)),
                ('reason', models.CharField(blank=True, db_column='Reason', max_length=50, null=True)),
                ('room_code', models.CharField(blank=True, db_column='Room_Code', max_length=10, null=True)),
                ('booking', models.BooleanField(db_column='Booking')),
                ('update_status', models.IntegerField(db_column='Update_Status')),
                ('waiting', models.BooleanField(db_column='Waiting')),
                ('mac_code', models.CharField(blank=True, db_column='Mac_Code', max_length=4, null=True)),
                ('refmac_code', models.CharField(blank=True, db_column='RefMac_Code', max_length=4, null=True)),
                ('make_staff', models.CharField(blank=True, db_column='Make_Staff', max_length=50, null=True)),
                ('source_code', models.CharField(blank=True, db_column='Source_Code', max_length=50, null=True)),
                ('is_hq', models.BooleanField(db_column='IS_HQ')),
                ('is_consultant', models.BooleanField(db_column='IS_Consultant')),
                ('is_missconsultant', models.BooleanField(db_column='IS_MISSConsultant')),
                ('is_enrollment', models.BooleanField(db_column='IS_Enrollment')),
                ('is_noshow', models.BooleanField(db_column='IS_NoShow')),
                ('cust_refer', models.CharField(blank=True, db_column='Cust_Refer', max_length=50, null=True)),
                ('is_missconsultantb', models.BooleanField(db_column='IS_MISSConsultantB')),
                ('modified_lock', models.BooleanField(db_column='Modified_Lock')),
                ('isarrive', models.BooleanField(blank=True, db_column='IsArrive', null=True)),
                ('lastmincancel', models.BooleanField(db_column='LastMinCancel')),
                ('sms_text', models.TextField(blank=True, db_column='SMS_Text', null=True)),
                ('equipment_id', models.IntegerField(blank=True, null=True)),
                ('email_text', models.CharField(blank=True, db_column='Email_Text', max_length=200, null=True)),
                ('onlineappointment', models.BooleanField()),
                ('requesttherapist', models.BooleanField(db_column='requestTherapist')),
                ('new_remark', models.CharField(blank=True, db_column='New_Remark', max_length=800, null=True)),
                ('item_code', models.CharField(blank=True, db_column='item_Code', max_length=20, null=True)),
                ('treatmentid', models.CharField(blank=True, db_column='treatmentId', max_length=20, null=True)),
                ('smsforconfirm', models.BooleanField(blank=True, db_column='smsForConfirm', null=True)),
                ('treatmentcode', models.CharField(blank=True, db_column='treatmentCode', max_length=40, null=True)),
                ('handledon', models.DateTimeField(blank=True, db_column='HandledOn', null=True)),
            ],
            options={
                'db_table': 'Appointment',
            },
        ),
    ]
