# Generated by Django 3.1 on 2022-03-04 08:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0003_auto_20220304_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tags',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Tags_company', to='company.company'),
        ),
    ]
