from django.db.models import Manager, F


class IsActiveManager(Manager):
    """"""
    def __init__(self,*args, **kwargs):
        self.is_active_field_name = kwargs.pop("active_field",None)
        self._label = kwargs.pop("label",None)
        self._value = kwargs.pop("value",None)

        super(IsActiveManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        # print(self.is_active_field_name)
        if self.is_active_field_name:
            filter_dict = {self.is_active_field_name:True}
        else:
            filter_dict = {}

        qs = super(IsActiveManager, self).get_queryset().filter(**filter_dict)

        if self._label and self._value:
            qs = qs.annotate(label=F(self._label),value=F(self._value)).values('label','value')

        return qs
