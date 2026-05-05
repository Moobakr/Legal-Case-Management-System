from django.contrib import admin
from .models import Client, Lawyer, Court, LawsuitCase

# Register your models here.
admin.site.register(Client)
admin.site.register(Lawyer)
admin.site.register(Court)
admin.site.register(LawsuitCase)

