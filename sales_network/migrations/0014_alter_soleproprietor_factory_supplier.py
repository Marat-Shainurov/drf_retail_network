# Generated by Django 4.2.5 on 2023-10-07 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales_network', '0013_alter_contactinfo_email_alter_contactinfo_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soleproprietor',
            name='factory_supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='factory_supplier_for_proprietor', to='sales_network.factory', verbose_name='factory_supplier_for_proprietor'),
        ),
    ]
