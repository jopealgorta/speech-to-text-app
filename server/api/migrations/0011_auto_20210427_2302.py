# Generated by Django 2.2.14 on 2021-04-27 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_pregunta_opciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditoria',
            name='puntuacion',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]