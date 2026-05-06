from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0006_configuracionclinica'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='is_disponible',
            field=models.BooleanField(
                default=True,
                help_text='Solo aplica para Domiciliarios. Desmárcalo si el domiciliario no está disponible (moto en taller, enfermo, etc.).',
                verbose_name='Disponible para entregas',
            ),
        ),
    ]