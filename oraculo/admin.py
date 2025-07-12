# oraculo/admin.py
from django.contrib import admin
from .models import DataTreinamento, Pergunta, Treinamentos

admin.site.register(Treinamentos)
admin.site.register(DataTreinamento)
admin.site.register(Pergunta)