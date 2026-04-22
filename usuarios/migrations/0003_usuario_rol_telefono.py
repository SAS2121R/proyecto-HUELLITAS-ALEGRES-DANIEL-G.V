# Migration: Add telefono and rol FK to Usuario
# Two-step: first add fields (rol nullable), assign Cliente, then make rol non-nullable

from django.db import migrations, models
import django.db.models
import django.utils.timezone


def assign_cliente_rol(apps, schema_editor):
    """Assign Cliente role to all existing users who don't have one."""
    Usuario = apps.get_model('usuarios', 'Usuario')
    Rol = apps.get_model('usuarios', 'Rol')
    cliente_rol = Rol.objects.get(nombre='Cliente')
    Usuario.objects.filter(rol__isnull=True).update(rol=cliente_rol)


def reverse_assign_rol(apps, schema_editor):
    """Reverse: no-op (can't un-assign roles meaningfully)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_rol'),
    ]

    operations = [
        # Step 1: Add telefono (blank=True, no issue)
        migrations.AddField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(blank=True, default='', max_length=15, verbose_name='Teléfono'),
        ),
        # Step 2: Add rol as nullable first (to allow existing rows)
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='usuarios.rol',
                verbose_name='Rol',
                related_name='usuarios',
            ),
        ),
        # Step 3: Assign Cliente role to existing users
        migrations.RunPython(assign_cliente_rol, reverse_assign_rol),
        # Step 4: Make rol non-nullable
        migrations.AlterField(
            model_name='usuario',
            name='rol',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='usuarios.rol',
                verbose_name='Rol',
                related_name='usuarios',
            ),
        ),
    ]