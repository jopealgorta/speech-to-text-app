# Generated by Django 2.2.14 on 2021-06-09 22:17

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Auditoria',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('finalizada', models.BooleanField(default=False)),
                ('aprobada', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.CharField(max_length=255)),
                ('seccion', models.CharField(choices=[('Afuera', 'Afuera'), ('Adentro', 'Adentro'), ('Caja', 'Caja')], default='Afuera', max_length=7)),
                ('categoria', models.CharField(choices=[('Informativa', 'Informativa'), ('DIGEFE', 'DIGEFE'), ('Extranormativa', 'Extranormativa')], max_length=14)),
                ('tipo', models.CharField(choices=[('Audio', 'Audio'), ('Numerica', 'Numerica'), ('Opciones', 'Opciones')], default='Audio', max_length=8)),
                ('respuesta_correcta', models.CharField(max_length=255, null=True)),
                ('opciones', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=25), blank=True, null=True, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('numero_de_sag', models.CharField(max_length=10)),
                ('departamento', models.CharField(max_length=20)),
                ('barrio', models.CharField(max_length=20)),
                ('direccion', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=50, unique=True)),
                ('celular', models.CharField(max_length=50)),
                ('razon_social', models.CharField(max_length=50)),
                ('rut', models.CharField(max_length=12)),
                ('negocio_anexo', models.CharField(max_length=20)),
                ('tipo_de_acceso', models.CharField(max_length=30)),
                ('esta_habilitado', models.BooleanField(default=False)),
                ('ciudad', models.CharField(max_length=40)),
                ('coord_lat', models.FloatField(blank=True, null=True)),
                ('coord_lng', models.FloatField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('ultimo_responsable', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ultima_sucursal', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respuesta', models.CharField(blank=True, max_length=128, null=True)),
                ('notas', models.TextField(blank=True, null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('auditoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Auditoria')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Pregunta')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=255)),
                ('tipo', models.CharField(choices=[('Audio', 'Audio'), ('Image', 'Image')], max_length=5)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('respuesta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Respuesta')),
            ],
        ),
        migrations.CreateModel(
            name='Incidente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accion', models.CharField(max_length=255)),
                ('asignado', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incidentes_asignados', to=settings.AUTH_USER_MODEL)),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Pregunta')),
                ('reporta', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incidentes_reportados', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='auditoria',
            name='sucursal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sucursal'),
        ),
    ]
