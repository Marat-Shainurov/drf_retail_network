from django.db import transaction, IntegrityError
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from products.models import Product
from products.serializers import ProductCreateSerializer, ProductBaseSerializer
from sales_network.models import RetailNetwork, ContactInfo
from sales_network.serializers import ContactInfoBaseSerializer, MainNetworkBaseSerializer, \
    FactorySupplierSerializer


class RetailNetSerializer(serializers.ModelSerializer):
    """
    Base RetailNetwork model serializer, with a broader info of the related objects
    (main_network, contact_info, factory_supplier, products).
    """
    main_network = MainNetworkBaseSerializer(read_only=True)
    contact_info = ContactInfoBaseSerializer(read_only=True)
    factory_supplier = FactorySupplierSerializer(read_only=True)
    products = ProductBaseSerializer(many=True, read_only=True)

    class Meta:
        model = RetailNetwork
        fields = ('id', 'main_network', 'name', 'contact_info', 'products', 'factory_supplier', 'debt_to_supplier',
                  'created_at', 'is_active')


class RetailNetSupplierSerializer(serializers.ModelSerializer):
    """
    A serializers for broader short supplier representation (id + name) used in related models' serializers.
    """
    class Meta:
        model = RetailNetwork
        fields = ('id', 'name',)


class RetailNetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the RetailNetwork model objects creation.
    transaction.atomic() context is used in order to prevent any effects to the database,
    unless all the actions in the overridden create() method are successful.
    """
    contact_info = ContactInfoBaseSerializer(many=False, required=True)
    new_products = ProductCreateSerializer(many=True, required=False)
    product_ids_to_add = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    class Meta:
        model = RetailNetwork
        fields = (
            'id', 'main_network', 'name', 'contact_info', 'new_products', 'product_ids_to_add', 'factory_supplier',)

    def create(self, validated_data):
        with transaction.atomic():
            contact_info_data = validated_data.pop('contact_info')
            new_products_data = validated_data.pop('new_products', [])
            product_ids_to_add_data = validated_data.pop('product_ids_to_add', [])
            contacts = ContactInfo(**contact_info_data)
            contacts.save()
            retail_network = RetailNetwork.objects.create(**validated_data, contact_info=contacts)

            for product in new_products_data:
                retail_network.products.create(**product)

            for product_id in product_ids_to_add_data:
                try:
                    product = get_object_or_404(Product, pk=product_id)
                    retail_network.products.add(product)
                except Http404:
                    raise serializers.ValidationError(f'Product with "{product_id}" id not found')

            return retail_network


class RetailNetUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for the RetailNetwork model objects update.
    transaction.atomic() context is used in order to prevent any effects to the database,
    unless all the actions in the overridden updated() method are successful.
    """
    name = serializers.CharField(required=False)
    contact_info_id = serializers.IntegerField(required=False)
    product_ids_to_add = serializers.ListField(child=serializers.IntegerField(), required=False)
    product_ids_to_remove = serializers.ListSerializer(child=serializers.IntegerField(), required=False)

    class Meta:
        model = RetailNetwork
        fields = ('id', 'name', 'contact_info_id', 'product_ids_to_add', 'product_ids_to_remove', 'factory_supplier',
                  'is_active',)

    def update(self, retail_network, validated_data):
        with transaction.atomic():
            contact_info_data = validated_data.pop('contact_info_id', None)
            if contact_info_data:
                try:
                    new_contacts = get_object_or_404(ContactInfo, pk=contact_info_data)
                    retail_network.contact_info = new_contacts
                except Http404:
                    raise serializers.ValidationError(f'ContactInfo with "{contact_info_data}" id not found')

            prod_ids_to_add_data = validated_data.pop('product_ids_to_add', [])
            for product_id in prod_ids_to_add_data:
                try:
                    prod_to_add = get_object_or_404(Product, pk=product_id)
                    retail_network.products.add(prod_to_add)
                except Http404:
                    raise serializers.ValidationError(f'Product with "{product_id}" id not found')

            prod_ids_to_remove_data = validated_data.pop('product_ids_to_remove', [])
            for product_id in prod_ids_to_remove_data:
                try:
                    prod_to_remove = get_object_or_404(Product, pk=product_id)
                    if prod_to_remove not in retail_network.products.all():
                        raise serializers.ValidationError(
                            f"The {product_id} product is not related to {retail_network}")
                    retail_network.products.remove(prod_to_remove)
                except Http404:
                    raise serializers.ValidationError(f'Product with "{product_id}" id not found')

            for attr, val in validated_data.items():
                setattr(retail_network, attr, val)

            try:
                retail_network.save()
            except IntegrityError:
                raise serializers.ValidationError(
                    f'ContactInfo with "{contact_info_data}" id is already related to another entity.')
            return retail_network
