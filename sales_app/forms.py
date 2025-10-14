from django import forms
from .models import Invoice, Sale, Product, CashInvoice, CashSale, CashProduct


# Form for uploading a CSV file
class SalesCSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label="Select CSV file",
        help_text="CSV file with sales data. Headers: Date of Sale,Invoice No,User,Customer Name,Customer Phone,CUSTOMER NO,Item,Quantity,Unit Price,total_amount,AMT PAID,BAL TO BE PAID"
    )

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'price': forms.NumberInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500'}),
        }


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        # Remove 'discount' from fields
        fields = ['customer_name', 'customer_phone', 'date_of_sale', 'notes', 'amount_paid']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'date_of_sale': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class SaleForm(forms.ModelForm):
    # Override the 'item' field to use a Select widget that will work with Select2 tagging
    item = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = Sale
        fields = ['item', 'unit_price', 'quantity', 'discount', 'total_price']
        widgets = {
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Don't populate choices - Select2 with tags will handle this
        # Just set the initial value if editing
        if self.instance and self.instance.pk and self.instance.item:
            self.initial['item'] = self.instance.item


# === CASH DEPARTMENT FORMS ===

class CashProductForm(forms.ModelForm):
    """Form for managing cash department products with rate-based pricing"""
    class Meta:
        model = CashProduct
        fields = ['name', 'rate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500'}),
            'rate': forms.NumberInput(attrs={'class': 'w-full rounded border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500', 'step': '0.0001'}),
        }


class CashInvoiceForm(forms.ModelForm):
    """Form for cash department invoices - no balance field as these are cash transactions"""
    class Meta:
        model = CashInvoice
        fields = ['customer_name', 'customer_phone', 'date_of_sale', 'notes']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}),
            'date_of_sale': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CashSaleForm(forms.ModelForm):
    """Form for cash sale items with amount-based pricing"""
    # Override the 'item' field to use CashProduct
    item = forms.ModelChoiceField(
        queryset=CashProduct.objects.all().order_by('name'),
        empty_label="enter item...",
        required=False,
    )

    class Meta:
        model = CashSale
        fields = ['item', 'amount', 'rate', 'total_price']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'readonly': 'readonly'}),
            'total_price': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
    
    def clean_item(self):
        """Convert the selected CashProduct instance back to its name string"""
        data = self.cleaned_data['item']
        if data:
            return data.name
        return data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.item:
            try:
                product = CashProduct.objects.get(name=self.instance.item)
                self.initial['item'] = product
            except CashProduct.DoesNotExist:
                pass
