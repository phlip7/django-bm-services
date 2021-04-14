# Generated by Django 3.1.5 on 2021-04-13 02:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20210409_0120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='area',
            name='city',
        ),
        migrations.RemoveField(
            model_name='subarea',
            name='city',
        ),
        migrations.AddField(
            model_name='area',
            name='locality',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.locality'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subarea',
            name='area',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.area'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='area',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
