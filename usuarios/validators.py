"""Validadores personalizados para Huellitas Alegres.

HU#1 criterio: la contraseña debe tener al menos 8 caracteres y contener
una combinación de letras, números y caracteres especiales.
"""

import re
from django.core.exceptions import ValidationError


class ComplexityPasswordValidator:
    """Valida que la contraseña contenga letras, números y caracteres especiales.

    Cumple el criterio de aceptación de HU#1:
    «al menos 8 caracteres y contenga una combinación de letras, números
    y caracteres especiales para mejorar la seguridad».
    """

    def validate(self, password, user=None):
        errors = []

        if not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]', password):
            errors.append(
                ValidationError(
                    'La contraseña debe contener al menos una letra.',
                    code='password_no_letter',
                )
            )

        if not re.search(r'\d', password):
            errors.append(
                ValidationError(
                    'La contraseña debe contener al menos un número.',
                    code='password_no_digit',
                )
            )

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]', password):
            errors.append(
                ValidationError(
                    'La contraseña debe contener al menos un carácter especial (!@#$%&* etc.).',
                    code='password_no_special',
                )
            )

        if errors:
            raise ValidationError(errors)

    def get_help_text(self):
        return (
            'La contraseña debe contener al menos una letra, un número '
            'y un carácter especial.'
        )