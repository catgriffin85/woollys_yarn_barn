from django import forms
from .models import Stock, Category


class StockForm(forms.ModelForm):

    class Meta:
        model = Stock
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names

        required_fields = ['category', 'sku', 'name', 'description', 'price', 'rating', 'image']

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
            field.required = field_name in required_fields
