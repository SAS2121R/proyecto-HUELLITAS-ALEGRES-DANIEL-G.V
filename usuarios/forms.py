import re
from django import forms
from django.contrib.auth import get_user_model
from .models import Rol, Perfil

Usuario = get_user_model()


class RegistroForm(forms.ModelForm):
    """Formulario de registro de usuarios.
    
    R7: Captura telefono (max 15 chars, opcional)
    R8: Mapea nombre → first_name (requerido)
    R9: Validación completa del formulario
    R10: first_name obligatorio (no vacío, no solo espacios)
    R11: Validación formato telefono (regex)
    R5: Asigna rol Cliente por defecto
    """
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=6,
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Usuario
        fields = ['first_name', 'email', 'telefono']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_first_name(self):
        """R10: first_name obligatorio, no solo espacios"""
        first_name = self.cleaned_data.get('first_name', '')
        if not first_name or not first_name.strip():
            raise forms.ValidationError('El nombre es obligatorio.')
        return first_name.strip()

    def clean_telefono(self):
        """R7: max_length ya validado por model; R11: formato regex"""
        telefono = self.cleaned_data.get('telefono', '')
        if telefono and not re.match(r'^[\d\s\+\-\(\)]{0,15}$', telefono):
            raise forms.ValidationError(
                'El teléfono solo puede contener números, espacios, +, -, ( y ).'
            )
        return telefono

    def clean_password2(self):
        """R9 scenario 3: Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return password2

    def save(self, commit=True):
        """R5: Asigna rol Cliente por defecto; R8: nombre → first_name"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        # Generar username único a partir del email
        base_username = self.cleaned_data['email'].split('@')[0]
        username = base_username
        counter = 1
        while Usuario.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        user.username = username
        # R5: Asignar rol Cliente por defecto
        user.rol = Rol.objects.get(nombre='Cliente')
        if commit:
            user.save()
        return user


class RolChangeForm(forms.ModelForm):
    """Formulario para que el administrador cambie el rol de un usuario."""
    class Meta:
        model = Usuario
        fields = ['rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
        }


class PerfilForm(forms.ModelForm):
    """Formulario para editar el perfil de usuario (foto y bio)."""

    class Meta:
        model = Perfil
        fields = ['foto', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def clean_foto(self):
        from .models import MAX_PERFIL_FOTO_SIZE
        foto = self.cleaned_data.get('foto')
        if foto and hasattr(foto, 'size') and foto.size > MAX_PERFIL_FOTO_SIZE:
            raise forms.ValidationError(
                f'La foto excede el tamaño máximo permitido de {MAX_PERFIL_FOTO_SIZE // (1024*1024)} MB.'
            )
        return foto