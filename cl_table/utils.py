import re,string,random
# from django.apps import apps
# from django.db.models import Max
from django.db.models import QuerySet, Model, ForeignObject
from django.db.models.expressions import Col, Func
from django.db.models.sql.constants import INNER
from django.db.models.sql.datastructures import Join
from django.db.models.options import Options


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


def model_joiner(queryset: QuerySet, to_model: Model, relations: tuple, from_model: Model = None,select:list=[]):
    """
     this function will facilitate complex JOIN clauses into the FROM entry.
     For example, the SQL generated could be
        LEFT OUTER JOIN "sometable" T1 ON ("othertable"."sometable_id1" = "sometable"."id1"
                                        AND "othertable"."sometable_id2" = "sometable"."id2")

        model_joiner(qs,SomeTable,(('sometable_id1', 'sometable_id1'), ('sometable_id2', 'sometable_id2'),),select=['some_field',])
    :param queryset: the queryset from parent model.
    :param to_model: the table that other end
    :param relations: the relationship fields as array of 2-tuples
    :param from_model: the parent model. can be none.
    :param select: the fields from other table. can be none.
    :return: queryset
    """
    if from_model is None:
        _alias = queryset.query.get_initial_alias()
        from_model = queryset.model
    else:
        _alias = from_model._meta.db_table

    _to_table_name = to_model._meta.db_table
    _fk = ForeignObject(to=to_model, on_delete=False, from_fields=[None],
                        to_fields=[None])

    _fk.opts = Options(from_model._meta)
    _fk.opts.model = from_model
    _fk.get_joining_columns = lambda : relations

    _join = Join(_to_table_name,from_model._meta.db_table,_to_table_name,INNER,_fk,True)
    queryset.query.join(_join)
    if select:
        _annotate_dict = {}
        for sel in select:
            _field = to_model._meta.get_field(sel)
            _annotate_dict[to_model.__name__+'__'+sel] = Col(_to_table_name,_field)

        queryset = queryset.annotate(**_annotate_dict)

    return queryset

# """SELECT
# SUBSTR(your_column, 0, LENGTH(your_column) - 1)
# FROM your_table;"""


class SUBSTR(Func):
    function = 'SUBSTR'

class LENGTH(Func):
    function = 'LEN'