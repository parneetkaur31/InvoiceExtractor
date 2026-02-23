from django.db import models

# Create your models here.

class Invoice(models.Model):
    pdf_name = models.CharField(max_length=255)
    invoice_no = models.CharField(max_length=100, blank=True, null=True)
    invoice_date = models.CharField(max_length=50, blank=True, null=True)
    order_id = models.CharField(max_length=100, blank=True, null=True)
    gstin = models.CharField(max_length=20, blank=True, null=True)
    grand_total = models.CharField(max_length=50, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.pdf_name


class ExtractionRule(models.Model):
    template_id = models.CharField(max_length=150)
    field_name = models.CharField(max_length=50)
    anchor = models.CharField(max_length=200)
    regex = models.TextField()
    success_count = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.template_id} - {self.field_name}"