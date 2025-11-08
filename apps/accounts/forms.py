"""Formularios personalizados para la gestión de usuarios."""

from django import forms
from allauth.account.forms import SignupForm, LoginForm

from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Role, PasswordResetCode, User



class UserSignupForm(SignupForm):
    """Formulario de registro adaptado al modelo de usuario personalizado."""

    field_order = (
        "first_name",
        "last_name",
        "email",
        "password1",
        "password2",
        "phone",
        "location",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base_classes = "w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition"
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{base_classes} {css}".strip()

    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Ingresa tu nombre",
        }),
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Ingresa tu apellido",
        }),
    )
    phone = forms.CharField(
        label="Teléfono",
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Ej: +57 3001234567",
        }),
    )
    location = forms.CharField(
        label="Ubicación",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "Ciudad / Departamento",
        }),
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        if not phone:
            return phone

        import re

        pattern = re.compile(r"^[+\d][\d\s-]{6,14}$")
        if not pattern.match(phone):
            raise forms.ValidationError(
                "Ingresa un número de teléfono válido (solo dígitos, espacios o guiones)."
            )
        return phone

    def save(self, request):
        user = super().save(request)

        user.first_name = self.cleaned_data["first_name"].strip()
        user.last_name = self.cleaned_data["last_name"].strip()
        user.phone = self.cleaned_data.get("phone", "").strip()
        user.location = self.cleaned_data.get("location", "").strip()
        user.role = "client"
        user.is_email_verified = True
        user.save(update_fields=[
            "first_name",
            "last_name",
            "phone",
            "location",
            "role",
            "is_email_verified",
        ])

        try:
            client_role = Role.objects.get(slug='client', is_active=True)
            user.roles.add(client_role)
        except Role.DoesNotExist:
            pass

        return user


class UserLoginForm(LoginForm):
    """Formulario de inicio de sesión con estilos consistentes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        base_classes = "w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition"
        checkbox_classes = "h-4 w-4 text-solar-yellow border-gray-300 rounded focus:ring-solar-orange"

        login_field = self.fields.get("login")
        if login_field:
            login_field.label = "Correo electrónico"
            login_field.widget.attrs.update({
                "placeholder": "tu-correo@ejemplo.com",
                "class": base_classes,
                "autocomplete": "email",
            })

        password_field = self.fields.get("password")
        if password_field:
            password_field.label = "Contraseña"
            password_field.widget.attrs.update({
                "placeholder": "Ingresa tu contraseña",
                "class": base_classes,
                "autocomplete": "current-password",
            })

        remember_field = self.fields.get("remember")
        if remember_field:
            remember_field.widget.attrs.update({"class": checkbox_classes})


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={
        'placeholder': 'tu-correo@ejemplo.com',
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition',
    }))

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No encontramos un usuario con ese correo electrónico.')
        return email

    def save(self):
        email = self.cleaned_data['email']
        user = User.objects.get(email=email)
        user.password_reset_codes.filter(is_used=False).update(is_used=True)
        code = PasswordResetCode.objects.create(
            user=user,
            code=f"{User.objects.make_random_password(length=6, allowed_chars='0123456789')}",
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        return user, code


class PasswordResetConfirmForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition',
    }))
    code = forms.CharField(label='Código de verificación', max_length=6, widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition',
        'placeholder': 'Ingresa el código de 6 dígitos',
    }))
    password1 = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition',
    }))
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3 rounded-lg border border-gray-200 focus:outline-none focus:ring-2 focus:ring-solar-yellow focus:border-transparent transition',
    }))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned

    def clean_code(self):
        return self.cleaned_data['code'].strip()

    def get_user_and_code(self):
        email = self.cleaned_data['email'].strip().lower()
        code = self.cleaned_data['code']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError('Correo electrónico no registrado.')

        try:
            reset_code = PasswordResetCode.objects.filter(user=user, code=code).latest('created_at')
        except PasswordResetCode.DoesNotExist:
            raise forms.ValidationError('Código inválido.')

        if not reset_code.is_valid():
            raise forms.ValidationError('El código ha expirado o ya fue utilizado.')

        return user, reset_code
