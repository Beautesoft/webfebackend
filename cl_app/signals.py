from django.db.models.signals import pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
# from .models import Site_Group, Item_SiteList

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