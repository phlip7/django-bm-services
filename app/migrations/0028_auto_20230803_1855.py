# Generated by Django 3.1.5 on 2023-08-03 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0027_auto_20230803_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='lat',
            field=models.DecimalField(decimal_places=20, max_digits=25),
        ),
        migrations.AlterField(
            model_name='address',
            name='lng',
            field=models.DecimalField(decimal_places=20, max_digits=25),
        ),
    ]
