from django.db.models.signals import post_save
from django.dispatch import receiver
from core.settings import BASE_DIR
from .models import Treinamentos
from .utils import gerar_documentos
from django_q.tasks import async_task

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
import os
from django.conf import settings

@receiver(post_save, sender=Treinamentos)
def signals_treinamento_ia(sender, instance, created, **kwargs):
    if created:
        async_task(task_treinar_ia, instance.id)        


def task_treinar_ia(instance_id):
    treinamentos = Treinamentos.objects.get(id=instance_id)
    documentos = gerar_documentos(treinamentos)

    if not documentos:
        return
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documentos)
    embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

    # Define o nome da pasta local onde nosso banco de dados vetorial será salvo.
    db_path = settings.BASE_DIR / "banco_faiss"
    # Verifica se o banco de dados já existe para não ter que recriá-lo do zero toda vez.
    if os.path.exists(db_path):
        # Se a pasta já existe, carrega o banco de dados localmente.
        # Ele usa o 'embeddings' para entender como interpretar os vetores.
        vectordb = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        # Adiciona os novos chunks (do documento atual) ao banco de dados já existente.
        vectordb.add_documents(chunks)
    else:
        # Se a pasta não existe, cria um banco de dados FAISS completamente novo.
        # Ele faz isso a partir dos nossos pedaços de texto (chunks) e suas representações numéricas (embeddings).
        vectordb = FAISS.from_documents(chunks, embeddings)
    # Salva o estado atual do banco de dados (seja ele novo ou atualizado) na pasta local.
    # Isso garante que na próxima execução, ele possa ser carregado rapidamente.
    vectordb.save_local(db_path)