
# class FE_DATA_TYPES:
#     def __init__(self):
#         self.__dict__ = {
#             "TEXT": "text",
#             "NUMBER": "number",
#             "BOOL"
#         }
FE_DATA_TYPES= ("text",     # 0
                "number",   # 1
                "selection",# 2
                "boolean",  # 3
                "datetime", # 4
                "date", # 5
                )

DYNAMIC_FIELD_CHOICES = {
    "ForeignKey" : FE_DATA_TYPES[2],
    "CharField": FE_DATA_TYPES[0],
    "TextField": FE_DATA_TYPES[0],
    "DecimalField": FE_DATA_TYPES[1],
    "EmailField": FE_DATA_TYPES[0],
    "FloatField": FE_DATA_TYPES[1],
    "DateTimeField": FE_DATA_TYPES[4],
    "DateField": FE_DATA_TYPES[5],
    "BooleanField": FE_DATA_TYPES[3],
}