from django.contrib import admin

# Register your models here.
from zalo01.models import *

admin.site.register(UserInfo)
admin.site.register(IdInfo)
admin.site.register(Server)
admin.site.register(PhoneInfo)
admin.site.register(OpenVpn)
admin.site.register(Phone_Operation_Log)
