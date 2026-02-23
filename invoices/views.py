import os
from django.shortcuts import render
from django.conf import settings
import pandas as pd
from django.http import HttpResponse
from .pdf_utils import extract_text_from_pdf
from .rule_engine import extract_fields, REQUIRED_FIELDS
from .models import Invoice
from .ai_extractor import extract_with_ai
from .rule_engine import learn_rule_from_text
from .models import ExtractionRule


def upload_files(request):

    if request.method == "POST":

        files = request.FILES.getlist('pdfs')

        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")

        extracted_data = []

        for file in files:

            file_path = os.path.join(upload_dir, file.name)

            # Save file
            with open(file_path, 'wb+') as dest:
                for chunk in file.chunks():
                    dest.write(chunk)

            # Extract text
            text = extract_text_from_pdf(file_path)

            fields = extract_fields(text)

            missing = [f for f in REQUIRED_FIELDS if not fields.get(f)]

            # 🔽 AI FALLBACK (only if needed)
            if missing:
                ai_fields = extract_with_ai(text)

                if ai_fields:
                    fields.update(ai_fields)

                    # 🧠 AUTO-LEARN RULES
                    for field, value in ai_fields.items():
                        rule_data = learn_rule_from_text(field, value, text)

                        if rule_data:
                            ExtractionRule.objects.create(
                                template_id="generic",
                                field_name=rule_data["field_name"],
                                anchor=rule_data["anchor"],
                                regex=rule_data["regex"],
                                active=True,
                            )


            Invoice.objects.create(
                pdf_name=file.name,
                invoice_no=fields.get("invoice_no"),
                invoice_date=fields.get("invoice_date"),
                order_id=fields.get("order_id"),
                gstin=fields.get("gstin"),
                grand_total=fields.get("grand_total"),
            )

            extracted_data.append({
                "name": file.name,
                "fields": fields,
                "preview": text[:1000]
            })

        return render(request, "invoices/success.html", {
            "results": extracted_data
        })

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
