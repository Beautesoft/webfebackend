# from cl_table.models import Securitycontrollist
#
# start = 0
#
# qs = Securitycontrollist.objects.filter(seq=start)
# for obj in qs:
#     print("*",obj.controlname)
#     qs1 = Securitycontrollist.objects.filter(controlparent=obj.controlname, seq= start + 1)
#     for obj1 in qs1:
#         print("\t|_",obj1.controlname)
#         qs2 = Securitycontrollist.objects.filter(controlparent=obj1.controlname,seq = start +2)
#         for obj2 in qs2:
#             print("\t\t|_",obj2.controlname)
#             qs3 = Securitycontrollist.objects.filter(controlparent= obj2.controlname,seq= start+3)
#             for obj3 in qs3:
#                 print("\t\t\t|_",obj3.controlname)

# import csv
#
# from cl_table.models import Multilanguage
#
# fields = ['id','english','zh_sg']
# lan_qs = Multilanguage.objects.all().values(*fields)
#
# with open("multi_language_words.csv", 'w') as csvfile:
#     # creating a csv dict writer object
#     writer = csv.DictWriter(csvfile, fieldnames=fields)
#
#     # writing headers (field names)
#     writer.writeheader()
#
#     # writing data rows
#     writer.writerows(list(lan_qs))

# from cl_table.models import CustomerFormControl
#
# s = []
#
# for o in CustomerFormControl.objects.all():
#     s.append({
#         "field_name": o.field_name,
#         "display_field_name": o.display_field_name,
#         "col_width": "-",
#         "order": "-",
#     })
#
# print(s)

# import csv
#
# from cl_table.models import MultiLanguageWord, Language
#
# with open("multi_language_words.csv",'r') as file:
#     x = csv.DictReader(file)
#     for i in x:
#         code = i['id']
#         l = Language.objects.get(itm_id=2) # chines
#         c = MultiLanguageWord(language=l,wordCode=code,word=i['zh_sg'])
#         c.save()
#         l1 = Language.objects.get(itm_id=3) # english
#         e = MultiLanguageWord(language=l1,wordCode=code,word=i['english'])
#         e.save()
#         print(i)
