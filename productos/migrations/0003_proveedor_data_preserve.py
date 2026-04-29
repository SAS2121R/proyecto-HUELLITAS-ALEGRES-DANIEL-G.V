from django.db import migrations, models


def create_proveedores_and_link(apps, schema_editor):
    """Create Proveedor objects from unique proveedor strings and link Producto FKs."""
    Proveedor = apps.get_model('proveedores', 'Proveedor')
    Producto = apps.get_model('productos', 'Producto')

    # Get all unique non-empty proveedor strings
    proveedor_names = set(
        Producto.objects.exclude(proveedor='')
        .values_list('proveedor', flat=True)
        .distinct()
    )

    # Create Proveedor objects
    proveedor_map = {}
    for name in proveedor_names:
        prov, _ = Proveedor.objects.get_or_create(nombre=name)
        proveedor_map[name] = prov

    # Link each Producto to its Proveedor via proveedor_new FK
    for producto in Producto.objects.exclude(proveedor=''):
        prov = proveedor_map.get(producto.proveedor)
        if prov:
            producto.proveedor_new = prov
            producto.save(update_fields=['proveedor_new'])


def reverse_migration(apps, schema_editor):
    """Reverse: set proveedor string from FK if it exists."""
    Producto = apps.get_model('productos', 'Producto')
    for producto in Producto.objects.select_related('proveedor_new').all():
        if producto.proveedor_new:
            producto.proveedor = producto.proveedor_new.nombre
            producto.save(update_fields=['proveedor'])


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_alter_producto_options_producto_categoria_and_more'),
        ('proveedores', '0001_initial'),
    ]

    operations = [
        # Step 1: Add temporary FK field
        migrations.AddField(
            model_name='producto',
            name='proveedor_new',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                to='proveedores.proveedor',
                verbose_name='Proveedor',
            ),
        ),
        # Step 2: Data migration — preserve old strings as Proveedor objects
        migrations.RunPython(create_proveedores_and_link, reverse_migration),
    ]