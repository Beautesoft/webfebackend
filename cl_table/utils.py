import re,string,random
from django.apps import apps
from django.db.models import Max


def code_generator(size=4,chars=string.ascii_letters + string.digits):
    code = ''
    for i in range(size):
        code += random.choice(chars)
    return code

def create_temp_diagnosis_code():
    code = code_generator()
    Diagnosis = apps.get_model(app_label='cl_table', model_name='Diagnosis')
    qs = Diagnosis.objects.filter(diagnosis_code=code).exists()
    if qs:
        return create_temp_diagnosis_code()
    return code

def get_next_diagnosis_code():
    Diagnosis = apps.get_model(app_label='cl_table', model_name='Diagnosis')
    curr_pk = Diagnosis.objects.all().aggregate(Max('sys_code'))['sys_code__max']
    return "%6d" % curr_pk + 1
