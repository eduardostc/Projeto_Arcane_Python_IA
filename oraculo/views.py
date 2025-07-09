import django.shortcuts
from django.shortcuts import render, redirect
from .models import Treinamentos
from django_q.models import Task


def treinar_ia(request):
  if request.method == 'GET':
    tasks = Task.objects.all()
    return render(request, 'treinar_ia.html', { 'tasks': tasks })
  elif request.method == 'POST':
    site = request.POST.get('site')
    conteudo = request.POST.get('conteudo')
    documento = request.FILES.get('documento')

    treinamento = Treinamentos(
      site=site,
      conteudo=conteudo,
      documento=documento
    )
    treinamento.save()
    return redirect('treinar_ia')

