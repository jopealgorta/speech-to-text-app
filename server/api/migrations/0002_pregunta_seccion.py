# Generated by Django 2.2.14 on 2021-05-12 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pregunta',
            name='seccion',
            field=models.CharField(choices=[('AF', 'Afuera'), ('AD', 'Adentro'), ('CA', 'Caja')], default='AF', max_length=2),
        ),
    ]
