from django.contrib import admin
from .models import Product,invoice,InvoiceItem,Stock,SellStock

admin.site.register(Product)
admin.site.register(invoice)
admin.site.register(InvoiceItem)
admin.site.register(Stock)
admin.site.register(SellStock)
