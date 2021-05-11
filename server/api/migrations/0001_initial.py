# Generated by Django 2.2.14 on 2021-05-08 20:58

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
                ('puntuacion', models.IntegerField(blank=True, default=0, null=True)),
                ('finalizada', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Pregunta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pregunta', models.CharField(max_length=255)),
                ('categoria', models.CharField(choices=[('IN', 'Informativa'), ('DG', 'DIGEFE'), ('EX', 'Extranormativa')], max_length=2)),
                ('tipo', models.CharField(choices=[('audi', 'Audio'), ('nume', 'Numerica'), ('opci', 'Opciones')], default='audi', max_length=4)),
                ('respuesta_ok', models.CharField(max_length=255, null=True)),
                ('opciones', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=25), blank=True, null=True, size=None)),
            ],
        ),
        migrations.CreateModel(
            name='Sucursal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('numero', models.CharField(max_length=10)),
                ('departamento', models.CharField(max_length=20)),
                ('bardrio', models.CharField(max_length=20)),
                ('direccion', models.CharField(max_length=100)),
                ('telefono', models.CharField(max_length=50, unique=True)),
                ('celular', models.CharField(max_length=50)),
                ('razon_social', models.CharField(max_length=50)),
                ('rut', models.CharField(max_length=12)),
                ('negocio_anexo', models.CharField(max_length=20)),
                ('tipo_de_acceso', models.CharField(max_length=30)),
                ('esta_habilitado', models.BooleanField(default=False)),
                ('ciudad', models.CharField(max_length=40)),
                ('coord_lat', models.FloatField(null=True)),
                ('coord_lng', models.FloatField(null=True)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respuesta', models.CharField(max_length=128)),
                ('notas', models.TextField(blank=True, max_length=256, null=True)),
                ('audio', models.FileField(blank=True, null=True, upload_to='audios_de_respuesta/')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificacion', models.DateTimeField(auto_now=True)),
                ('auditoria', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Auditoria')),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Pregunta')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(max_length=255)),
                ('tipo', models.CharField(choices=[('JR', 'Junior'), ('MID', 'Mid-level'), ('SR', 'Senior')], max_length=3)),
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
                ('asignado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('pregunta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Pregunta')),
                ('reporta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reportado', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='auditoria',
            name='sucursal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Sucursal'),
        ),
        migrations.AddField(
            model_name='auditoria',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
