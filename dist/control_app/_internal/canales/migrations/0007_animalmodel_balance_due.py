# Generated by Django 4.2.6 on 2023-10-18 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canales', '0006_animalmodel_payments'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalmodel',
            name='balance_due',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
