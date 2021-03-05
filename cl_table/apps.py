from django.apps import AppConfig


class ClTableConfig(AppConfig):
    name = 'cl_table'
    # This function is the only new thing in this file
    # it just imports the signal file when the app is ready
    def ready(self):
        import cl_table.signals    

