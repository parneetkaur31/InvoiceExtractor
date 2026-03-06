from django.urls import path
from .views import upload_files, export_excel
from . import views

urlpatterns = [
    path('', upload_files),
    path('export/', export_excel),
    path("status/", views.processing_status, name="status"),
]
