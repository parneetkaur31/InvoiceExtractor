from dataclasses import fields
import os
import gc
import threading
from importlib.resources import files
from django.shortcuts import render
from django.conf import settings
import pandas as pd
from django.http import HttpResponse, JsonResponse
from .pdf_utils import extract_text_from_pdf
from .rule_engine import extract_fields, REQUIRED_FIELDS
from .models import Invoice
from .ai_extractor import extract_with_ai
from .rule_engine import learn_rule_from_text
from .models import ExtractionRule


def upload_files(request):

    if request.method == "POST":

        files = request.FILES.getlist('pdfs')

        # 🚨 Limit files for Render free tier
        if len(files) > 10:
            return HttpResponse("Maximum 10 files per upload on demo server.")

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
        os.makedirs(upload_dir, exist_ok=True)

        file_paths = []

        for file in files:
            file_path = os.path.join(upload_dir, file.name)

            with open(file_path, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            file_paths.append(file_path)

        # 🚀 Start background processing
        threading.Thread(
            target=process_files_background,
            args=(file_paths,),
            daemon=True
        ).start()

        return HttpResponse("Files uploaded. Processing started in background.")

    return render(request, "invoices/upload.html")



def export_excel(request):

    qs = Invoice.objects.all().values(
        "pdf_name",
        "invoice_no",
        "invoice_date",
        "order_id",
        "gstin",
        "grand_total",
    )

    df = pd.DataFrame(qs)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

    response['Content-Disposition'] = 'attachment; filename=invoices.xlsx'

    df.to_excel(response, index=False)

    return response



def process_files_background(file_paths):

    for file_path in file_paths:
        try:
            text = extract_text_from_pdf(file_path)
            fields = extract_fields(text)

            # 🔹 AI fallback if rule-based misses invoice_no
            if not fields.get("invoice_no"):
                ai_fields = extract_with_ai(text)
                fields.update(ai_fields)

            invoice = Invoice.objects.create(
                pdf_name=os.path.basename(file_path),
                invoice_no=fields.get("invoice_no"),
                invoice_date=fields.get("invoice_date"),
                order_id=fields.get("order_id"),
                gstin=fields.get("gstin"),
                grand_total=fields.get("grand_total"),
            )

            invoice.status = "done"
            invoice.save()

            # free memory
            del text

        except Exception as e:
            print("Error processing:", file_path, e)

    
def processing_status(request):

    total = Invoice.objects.count()
    done = Invoice.objects.filter(status="done").count()

    return JsonResponse({
        "processed": done,
        "total": total
    })