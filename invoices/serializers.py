from rest_framework import serializers
from .models import Invoice, InvoiceItem, Client

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name','email']

class InvoiceItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'rate']

class InvoiceSerializer(serializers.ModelSerializer):
    client = ClientSerializer()
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'client', 'invoice_number', 'issue_date', 'due_date', 'status', 'notes', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        return invoice