from django.contrib.auth import forms, get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(forms.UserCreationForm):

    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])

class FormularioRegistro(UserCreationForm):
    
    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'telefono',
        ]
        labels = {
            'username': 'Nombre de usuario',
             'first_name': 'Nombre',
             'last_name': 'Apellidos',
             'email': 'Correo',
             'telefono': 'Teléfono',
        }