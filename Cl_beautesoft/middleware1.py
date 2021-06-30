import django.utils.timezone
from pytz import timezone
from django.http import HttpResponse

# class TimezoneMiddleware:
#     def process_request(self, request, response):
#         print(request,"request")
#         # response = get_response(request)
#         # print(response,"response")
#         # Put logic here to choose timezone based on domain.
#         if request.META['HTTP_HOST'] == '103.253.15.184:8000':
#             tz = timezone('Asia/Singapore')
#         else:
#             print("else")
#             tz = timezone('Asia/Kolkata')
#             print(tz,"tz")

#         if tz:
#             django.utils.timezone.activate(tz)
#         else:
#             django.utils.timezone.deactivate()
#         return response
    


def open_access_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "*"
        return response
    return middleware
