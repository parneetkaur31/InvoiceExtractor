from django.urls import path
from .views import upload_files, export_excel

urlpatterns = [
    path('', upload_files),
    path('export/', export_excel),
]
