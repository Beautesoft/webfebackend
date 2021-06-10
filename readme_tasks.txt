cl_table
    views.py
        CustomerFormSettingsView
        EmployeeSkillView
        SkillsItemTypeList
        schedule_hours
        MonthlyWorkSchedule
        StaffPlusViewSet
        meta_religious
        meta_nationality
        meta_race
        MonthlyWorkSchedule
        MonthlyAllSchedule
        schedule_hours
        SkillsItemTypeList
        SkillsView
        PhotoDiagnosis
        EmployeeSkillView
        CustomerFormSettingsView
        CustomerFormSettings
        RewardPolicyView
        RedeemPolicyView
        DiagnosisCompareView

    models.py
        CustomerFormControl
        Skillstaff
        MenuSecuritylevellist
        MenuSecurity
        Securitylevellist
        Securitycontrollist
        Workschedule
        CustomerTitle
        RewardPolicy
        RedeemPolicy
        Diagnosis
        DiagnosisCompare
        CustomerPoint
        CustomerPointDtl

        add emp_remarks filed into Employee table
        add emp_country into Employee table
        add shortDesc into ScheduleHour table
        add is_alternative into Workschedule table

        add property method* into CustomerClass, Source, Gender

    serializer.py
        CustomerFormControlSerializer
        StaffPlusSerializer
        CustomerClassSerializer
        CustomerPlusSerializer
        SkillSerializer
        EmpInfoSerializer
        EmpWorkScheduleSerializer
        DiagnosisCompareSerializer
        DiagnosisSerializer
        RewardPolicySerializer
        RedeemPolicySerializer

    admin.py
    configuration.py
    utils.py
    urls.py

cl_app
    models.py
        add property method* into ItemSitelist

custom
    views.py

CL_beautesoft
    urls.py


*property methods that isn't effected to db or migration, in models


