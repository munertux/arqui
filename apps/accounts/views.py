from django.conf import settings
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from apps.accounts.forms import PasswordResetRequestForm, PasswordResetConfirmForm
from apps.accounts.models import PasswordResetCode


class PasswordResetRequestView(FormView):
    template_name = 'account/password_reset_request.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('accounts:password_reset_confirm')

    def form_valid(self, form):
        user, code = form.save()
        subject = 'Código para restablecer tu contraseña'
        message = (
            'Hola,\n\n'
            'Recibimos una solicitud para restablecer tu contraseña en SIESE.\n'
            f'Tu código de verificación es: {code.code}\n\n'
            'El código vence en 15 minutos. Si no solicitaste este cambio, puedes ignorar este correo.\n\n'
            'Equipo SIESE'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
        messages.success(self.request, 'Te enviamos un código a tu correo electrónico. Revisa tu bandeja de entrada o spam.')
        self.request.session['reset_email'] = user.email
        return super().form_valid(form)


class PasswordResetConfirmView(FormView):
    template_name = 'account/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('account_login')

    def get_initial(self):
        initial = super().get_initial()
        email = self.request.session.get('reset_email')
        if email:
            initial['email'] = email
        return initial

    def form_valid(self, form):
        user, reset_code = form.get_user_and_code()
        password = form.cleaned_data['password1']
        try:
            validate_password(password, user)
        except ValidationError as exc:
            form.add_error('password1', exc)
            return self.form_invalid(form)
        user.set_password(password)
        user.save(update_fields=['password'])
        reset_code.is_used = True
        reset_code.save(update_fields=['is_used'])
        messages.success(self.request, 'Contraseña actualizada correctamente. Ahora puedes iniciar sesión.')
        return super().form_valid(form)
