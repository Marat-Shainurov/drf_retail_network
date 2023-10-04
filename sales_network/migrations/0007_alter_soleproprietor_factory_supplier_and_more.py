# Generated by Django 4.2.5 on 2023-10-03 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales_network', '0006_alter_factory_products'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soleproprietor',
            name='factory_supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proprietor_factory_supplier', to='sales_network.factory', verbose_name='proprietor_factory_supplier'),
        ),
        migrations.AlterField(
            model_name='soleproprietor',
            name='retail_network_supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proprietor_network_supplier', to='sales_network.retailnetwork', verbose_name='proprietor_network_supplier'),
        ),
    ]