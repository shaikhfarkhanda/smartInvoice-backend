from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Invoice, InvoiceItem, Client
from .serializers import InvoiceSerializer, InvoiceItemSerializer, ClientSerializer
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.mail import EmailMessage
import tempfile


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    
class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        items_data = data.pop('items', [])
        client_data = data.pop('client', None)

        if isinstance(client_data, dict):
            client, _ = Client.objects.get_or_create(
                name=client_data.get('name'),
                email=client_data.get('email')
            )
        else:
            client = Client.objects.get(id=client_data)

        invoice = Invoice.objects.create(client=client, **data)
        print("Items data received:", items_data)

        for item in items_data:
            try:
                created_item = InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item.get('description', ''),
                    quantity=int(item.get('quantity', 1)),
                    rate=float(item.get('rate', 0))
                )
                print("Item saved:", created_item)
            except Exception as e:
                print("Error saving item:", item, str(e))

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer

class InvoiceListCreatwView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

def download_invoice_pdf(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    client = invoice.client
    items = invoice.items.all()

    html_string = render_to_string('invoices/pdf_template.html', {
        'invoice' : invoice,
        'client' : client,
        'items' : items,
    })

    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{invoice_id}.pdf'
    return response

@api_view(['POST']) 
def send_invoice_email(request, pk):
    import os
    import uuid

    try:
        invoice = Invoice.objects.get(pk=pk)
        html_string = render_to_string('invoices/pdf_template.html', {
            'invoice': invoice,
            'client': invoice.client,
            'items': invoice.items.all(),
        })

        # Generate file path
        file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.pdf")
        pdf_bytes = HTML(string=html_string).write_pdf()

        # Write PDF to file temporarily (optional, for debugging)
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)

        # Attach PDF directly from memory
        email = EmailMessage(
            subject=f"Invoice #{invoice.invoice_number}",
            body="Please find attached the invoice.",
            from_email="shaikhfarkhanda14@gmail.com",
            to=[invoice.client.email],
        )
        email.attach(
            filename=f"Invoice_{invoice.invoice_number}.pdf",
            content=pdf_bytes,
            mimetype="application/pdf"
        )
        email.send()

        # Delete file if needed
        if os.path.exists(file_path):
            os.remove(file_path)

        return Response({"message": "Invoice sent successfully!"})

    except Exception as e:
        print("❌ EMAIL ERROR:", e)
        return Response({"error": f"Failed to send invoice. {str(e)}"}, status=500)
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def login_status(request):
    return Response({"logged_in": True})

