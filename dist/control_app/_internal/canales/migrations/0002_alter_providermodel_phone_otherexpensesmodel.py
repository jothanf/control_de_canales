# Generated by Django 4.2.6 on 2023-10-17 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('canales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='providermodel',
            name='phone',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='OtherExpensesModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50)),
                ('price', models.PositiveIntegerField()),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='canales.animalmodel')),
            ],
        ),
    ]
