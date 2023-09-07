from django.contrib import admin
from .models import Product,invoice,InvoiceItem,Stock

admin.site.register(Product)
admin.site.register(invoice)
admin.site.register(InvoiceItem)
admin.site.register(Stock)
