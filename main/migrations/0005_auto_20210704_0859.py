# Generated by Django 3.1.4 on 2021-07-04 05:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_site_content_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='site',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='main.site'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='HrefContentPage',
        ),
    ]