"""Formularios administrativos para marcos legales."""

from django import forms

from .models import LegalFramework


class LegalFrameworkForm(forms.ModelForm):
    """Formulario para crear y actualizar marcos legales."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_input = "w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition"
        checkbox_input = "h-4 w-4 text-solar-yellow border-gray-300 rounded focus:ring-solar-orange"

        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', checkbox_input)
            elif isinstance(widget, (forms.Textarea, forms.TextInput, forms.URLInput, forms.NumberInput, forms.Select)):
                existing = widget.attrs.get('class', '')
                widget.attrs['class'] = f"{base_input} {existing}".strip()
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)

    class Meta:
        model = LegalFramework
        fields = [
            'title',
            'document_type',
            'document_number',
            'year',
            'issuing_entity',
            'official_url',
            'summary',
            'main_objective',
            'benefits_companies',
            'benefits_citizens',
            'is_active',
        ]
