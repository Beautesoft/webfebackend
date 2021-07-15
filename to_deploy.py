
# cl_table/models.py
class MultiLanguageWord(models.Model):
    id = models.AutoField(primary_key=True)
    wordCode = models.IntegerField()
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    word = models.CharField(max_length=250)

    class Meta:
        db_table = 'MultiLanguageWord'
        unique_together = (('wordCode','language',),)


### only one section should deploy ###

## --------------- SECTION 1 ------------------ ###

# cl_tabel/views.py
@api_view(['GET', ])
@permission_classes((AllowAny,))
def MultiLanguage(request):
    lang_qs = Language.objects.filter(itm_isactive=True)

    responseDict = {}
    for lang in lang_qs:
        qs = MultiLanguageWord.objects.filter(language=lang).values('wordCode', 'word')
        responseDict[lang.itm_desc] = list(qs)

    response_data = {
        "language": responseDict,
        "message": "Listed successfuly"
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)

# cl_table/urls.py
path('api/MultiLanguage/', views.MultiLanguage, name='MultiLanguage'),

### ----------------- #####


### --------------------- SECTION 2 -----------------#####
# cl_tabel/views.py
@api_view(['GET', ])
@permission_classes((AllowAny,))
def MultiLanguage_list(request):
    lang_qs = Language.objects.filter(itm_isactive=True)
    qs = MultiLanguageWord.objects.all()
    responseDict = {}

    for w in qs:
        w_dict = responseDict.get(w.wordCode,{})
        w_dict[w.language.itm_desc] = w.word
        responseDict[w.wordCode] = w_dict
    # for lang in lang_qs:
    #     qs = MultiLanguageWord.objects.filter(language=lang).values('wordCode', 'word')
    #     responseDict[lang.itm_desc] = list(qs)
    resData = [val for key, val in responseDict.items()]
    response_data = {
        "language": resData,
        "message": "Listed successfuly"
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)


# cl_tabel/urls.py
path('api/MultiLanguageList/', views.MultiLanguage_list, name='MultiLanguage_list'),

### ----------------- #####


