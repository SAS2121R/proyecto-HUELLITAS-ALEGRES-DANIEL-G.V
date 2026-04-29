from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0003_proveedor_data_preserve'),
    ]

    operations = [
        # Remove old CharField proveedor
        migrations.RemoveField(
            model_name='producto',
            name='proveedor',
        ),
        # Rename proveedor_new FK to proveedor
        migrations.RenameField(
            model_name='producto',
            old_name='proveedor_new',
            new_name='proveedor',
        ),
    ]