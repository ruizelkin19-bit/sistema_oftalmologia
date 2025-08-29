from django import forms
from .models import Factura
from decimal import Decimal, ROUND_HALF_UP
from num2words import num2words


class FacturaForm(forms.ModelForm):
    iva_aplica = forms.BooleanField(
        required=False,
        label="Aplicar IVA",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    total = forms.DecimalField(
        label='Total a pagar',
        max_digits=12,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )

    class Meta:
        model = Factura
        fields = [
            'forma_pago',
            'subtotal',
            'descuento',
            'iva_aplica',
            'impuestos',
            'copago',
            'cuota_moderadora',
            'bonos',
            'observaciones',
            'valor_letras',
        ]
        widgets = {
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
            'subtotal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'descuento': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'impuestos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'copago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cuota_moderadora': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'bonos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Observaciones adicionales de la factura...'
            }),
            'valor_letras': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ['descuento', 'copago', 'cuota_moderadora', 'bonos']:
            self.fields[f].required = False
        self.fields['total'].widget.attrs['readonly'] = True
        self.fields['valor_letras'].widget.attrs['readonly'] = True
        self.fields['impuestos'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        subtotal = cleaned_data.get('subtotal') or Decimal('0.00')
        descuento = cleaned_data.get('descuento') or Decimal('0.00')
        copago = cleaned_data.get('copago') or Decimal('0.00')
        cuota_moderadora = cleaned_data.get('cuota_moderadora') or Decimal('0.00')
        bonos = cleaned_data.get('bonos') or Decimal('0.00')
        iva_aplica = cleaned_data.get('iva_aplica')

        # 🔹 Calcular impuestos y total, solo para mostrar en el formulario
        impuestos = (subtotal - descuento) * Decimal('0.19') if iva_aplica else Decimal('0.00')
        impuestos = impuestos.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total = (subtotal - descuento) + impuestos - (copago + cuota_moderadora + bonos)
        total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        # 🔹 Guardar los valores exactos en cleaned_data
        cleaned_data['impuestos'] = impuestos
        cleaned_data['total'] = total
        cleaned_data['valor_letras'] = (num2words(total, lang='es') + " MONEDA LEGAL").upper() if total > 0 else ""

        return cleaned_data
