# Generated by Django 3.1.4 on 2021-07-03 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20210703_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='content_property_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AlterField(
            model_name='site',
            name='content_property_value',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
        migrations.AlterField(
            model_name='site',
            name='content_tag_name',
            field=models.CharField(blank=True, default='', max_length=120),
        ),
    ]
