from django.contrib import admin
from .models import Product,invoice,InvoiceItem

admin.site.register(Product)
admin.site.register(invoice)
admin.site.register(InvoiceItem)
