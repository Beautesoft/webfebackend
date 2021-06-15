from django.db.models.signals import pre_delete, post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
# from cl_app.models import Site_Group, Item_SiteList
from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver
from cl_table.models import Diagnosis, DiagnosisCompare, Employee, Fmspw, RewardPolicy, RedeemPolicy


# from cl_app.models import LoggedInUser

# @receiver(pre_delete, sender=Site_Group, dispatch_uid='Site_Group_signal')
# def log_deleted_site_group(sender, instance, using, **kwargs):
#     print(instance,"instance***")
#     # d = Deleted()
#     # d.question = instance.id
#     # d.dt = datetime.datetime.now() 
#     # d.save()    

# @receiver(post_delete)
# def site_group_post_delete(sender, instance, *args, **kwargs):
#     print(sender,"sender rdhfd")
    # if sender == Comment:
    #     # do something    



# @receiver(user_logged_in)
# def on_user_logged_in(sender, request, **kwargs):
#     # print(sender,"sender")
#     # print(request,"request")
#     # print(kwargs,"kwargs")
#     # print(request.session.session_key,"Signals")
#     LoggedInUser.objects.get_or_create(user=kwargs.get('user'))


# @receiver(user_logged_out)
# def on_user_logged_out(sender, **kwargs):
#     LoggedInUser.objects.filter(user=kwargs.get('user')).delete()

@receiver(post_save,sender=Diagnosis)
def diagnosis_code_gen(sender, instance, created, **kwargs):
    if created:
        instance.diagnosis_code = "%06d" % instance.sys_code
        instance.save()

@receiver(post_save,sender=DiagnosisCompare)
def diagnosis_code_gen(sender, instance, created, **kwargs):
    if created:
        instance.compare_code = "%06d" % instance.id
        instance.save()

@receiver(post_save,sender=RewardPolicy)
def reward_code_gen(sender, instance, created, **kwargs):
    if created:
        instance.reward_code = "%06d" % instance.id
        instance.save()

@receiver(post_save,sender=RedeemPolicy)
def redeem_code_gen(sender, instance, created, **kwargs):
    if created:
        instance.redeem_code = "%06d" % instance.id
        instance.save()


@receiver(post_save,sender=Employee)
def employee_fmspw_related(sender, instance, created, **kwargs):
    _Fmspw = Fmspw.objects.filter(Emp_Codeid=instance).first()
    if _Fmspw:
        _Fmspw.flgsales = instance.show_in_sales
        _Fmspw.flgappt = instance.show_in_appt
        _Fmspw.save()