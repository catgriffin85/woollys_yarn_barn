from django import forms
from .models import Stock, Category


class StockDetails(forms.ModelForm):
    WEIGHT_CHOICES = [
        ('dk', 'Double Knitting'),
        ('aran', 'Aran'),
        ('chunky', 'Chunky'),
        ('super_chunky', 'Super Chunky'),
    ]

    COLOUR_CHOICES = [
        ('blue', 'Blue'),
        ('pink', 'Pink'),
        ('green', 'Green'),
        ('white', 'White'),
        ('black', 'Black'),
        ('grey', 'Grey'),
        ('yellow', 'Yellow'),
    ]

    SIZE_CHOICES = [
        ('3mm', '3mm'),
        ('4mm', '4mm'),
        ('4.5mm', '4.5mm'),
        ('5mm', '5mm'),
        ('6mm', '6mm'),
        ('7mm', '7mm'),
        ('8mm', '8mm'),
    ]

    weight = forms.ChoiceField(
        choices=WEIGHT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control rounded-0'})
    )

    colour = forms.ChoiceField(
        choices=COLOUR_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control rounded-0'})
    )

    size = forms.ChoiceField(
        choices=SIZE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control rounded-0'})
    )

    class Meta:
        model = Stock
        fields = [
            'category', 'sku', 'name', 'description',
            'weight', 'colour', 'size',
            'price', 'image'
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': 0.01}),
            'image': forms.ClearableFileInput(),
        }


class StockForm(forms.ModelForm):

    class Meta:
        model = Stock
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]

        self.fields['category'].choices = friendly_names

        required_fields = ['category', 'sku', 'name', 'description', 'price', 'image']

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'
            field.required = field_name in required_fields
