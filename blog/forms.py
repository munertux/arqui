from django import forms
from django.forms import inlineformset_factory

from .models import BlogPost, BlogImage, BlogComment, BlogReport


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['category', 'title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = "w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition"
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', base_classes)
        from .models import BlogCategory

        default_category = BlogCategory.objects.order_by('id').first()
        if default_category is None:
            default_category = BlogCategory.objects.create(name='Solar', slug='solar')

        self.fields['category'].widget = forms.HiddenInput()
        self.fields['category'].initial = default_category.pk
        self.fields['category'].required = True


BlogImageFormSet = inlineformset_factory(
    BlogPost,
    BlogImage,
    fields=['image', 'caption'],
    extra=5,
    max_num=5,
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'w-full text-sm text-gray-600'}),
        'caption': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition'}),
    }
)


class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['content', 'name', 'email']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user and user.is_authenticated:
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['email'].widget = forms.HiddenInput()
            self.fields['name'].required = False
            self.fields['email'].required = False

    def clean(self):
        cleaned = super().clean()
        if not self.user or not self.user.is_authenticated:
            if not cleaned.get('name'):
                self.add_error('name', 'Indica tu nombre para publicar el comentario.')
            if not cleaned.get('email'):
                self.add_error('email', 'Ingresa un correo electrónico para continuar.')
        return cleaned


class BlogReportForm(forms.ModelForm):
    class Meta:
        model = BlogReport
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-red-400 focus:border-transparent transition'}),
        }
