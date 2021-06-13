import re,string,random
# from django.apps import apps
# from django.db.models import Max

from cl_table.models import Fmspw, Securitylevellist


def code_generator(size=4,chars=string.ascii_letters + string.digits):
    code = ''
    for i in range(size):
        code += random.choice(chars)
    return code

# def create_temp_diagnosis_code():
#     code = code_generator()
#     Diagnosis = apps.get_model(app_label='cl_table', model_name='Diagnosis')
#     qs = Diagnosis.objects.filter(diagnosis_code=code).exists()
#     if qs:
#         return create_temp_diagnosis_code()
#     return code
#
# def get_next_diagnosis_code():
#     Diagnosis = apps.get_model(app_label='cl_table', model_name='Diagnosis')
#     curr_pk = Diagnosis.objects.all().aggregate(Max('sys_code'))['sys_code__max']
#     return "%6d" % curr_pk + 1

from cl_table.models import Fmspw, Securitylevellist


class PermissionValidator:
    def __init__(self,auth_user,permissions:list,nested=False):
        """
        :param auth_user: request.user
        :param permission: permission list Eg. ['mnuEmpDtl','mnuCustomer','mnuDiagnosis'] (from Securitycontrollist.controlname)
        :param nested: TODO if nested is true control parent permissions considered.
        """
        self.auth_user = auth_user
        self.permissions = permissions
        self.nested = nested

    def is_allow(self):
        """
        :return: true if the user have permission else false
        """
        self.no_permission = None
        fmspw = Fmspw.objects.filter(user=self.auth_user, pw_isactive=True).first()
        if not fmspw:
            self.error = "fmspw object doesn't exists"
            return False
        user_level = fmspw.LEVEL_ItmIDid
        self.sec_level_qs = Securitylevellist.objects.filter(level_itemid=user_level.level_code,
                                                             controlstatus=True,
                                                             controlname__in=self.permissions)
        self.no_permission = set(self.permissions) - set(self.sec_level_qs.values_list('controlname', flat=True))
        # self.no_permission_qs = self.sec_level_qs.exclude(controlname__in=self.permissions)
        # if self.sec_level_qs.count() > self.no_permission_qs.count():
        #     return True
        if self.sec_level_qs.exists():
            return True
        self.error = "user hasn't any permissions"
        return False
