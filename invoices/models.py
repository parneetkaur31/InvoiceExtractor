from django.db import models

# Create your models here.

class Invoice(models.Model):

    pdf_name = models.CharField(max_length=255)

    invoice_no = models.CharField(max_length=100, null=True, blank=True)
    invoice_date = models.CharField(max_length=100, null=True, blank=True)

    irn = models.CharField(max_length=200, null=True, blank=True)

    order_id = models.CharField(max_length=100, null=True, blank=True)
    order_date = models.CharField(max_length=100, null=True, blank=True)

    title = models.TextField(null=True, blank=True)

    hsn_sac = models.CharField(max_length=100, null=True, blank=True)

    quantity = models.CharField(max_length=50, null=True, blank=True)

    imei_serial = models.CharField(max_length=200, null=True, blank=True)

    total = models.CharField(max_length=100, null=True, blank=True)

    grand_total = models.CharField(max_length=100, null=True, blank=True)

    sold_by_address = models.TextField(null=True, blank=True)

    gstin = models.CharField(max_length=100, null=True, blank=True)

    bill_to_address = models.TextField(null=True, blank=True)

    ship_to_address = models.TextField(null=True, blank=True)

    status = models.CharField(max_length=20, default="pending")

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