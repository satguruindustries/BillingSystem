from django import forms
from .models import Product,invoice,InvoiceItem,Stock,SellStock

class NewProductForm(forms.ModelForm):
	class Meta:
		model = Product
		fields = ['name','hsn', 'rate', 'cgst', 'sgst', 'unit']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = invoice
        fields = ['cust_name', 'cust_add', 'cust_place', 'cust_gstin', 'invoice_num', 'date', 'freight_charges', 'grand_total']

    products = forms.ModelMultipleChoiceField(queryset=Product.objects.all())
    freight_charges = forms.DecimalField(max_digits=10, decimal_places=2)
    grand_total = forms.DecimalField(max_digits=10, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].queryset = Product.objects.all()
    
    # Add a custom method to set the initial value of 'products' field in update
    def set_product_initial(self, invoice_item_instance):
        if invoice_item_instance.product:
            self.fields['products'].initial = invoice_item_instance.product.id
        else:
            self.fields['products'].initial = None
   

class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['quantity', 'rate', 'total']

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['date', 'quantity', 'transfer']
    products = forms.ModelMultipleChoiceField(queryset=Product.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].queryset = Product.objects.all()

class SellStockForm(forms.ModelForm):
    class Meta:
        model = SellStock
        fields = ['date', 'quantity']
    products = forms.ModelMultipleChoiceField(queryset=Product.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['products'].queryset = Product.objects.all()
